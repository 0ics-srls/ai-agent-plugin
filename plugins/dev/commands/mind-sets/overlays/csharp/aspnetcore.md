# C# / .NET 10 — ASP.NET Core service

How `branches/service-layers.md`, `branches/api.md`, `branches/resilience.md` and `branches/operations.md` are written in an ASP.NET Core service.

---

## 1. Projects — the base and the features

| Project | Holds | References |
|---|---|---|
| `App.Core` | the base contracts — `IEntity` (`Id`), `IRepository<T> where T : class, IEntity` (query, get by id, add, delete), `IUnitOfWork`, the query and page records, the error codes — and each feature's interfaces, whose signatures carry ids, values and records (`MergeAsync(int fromId, int intoId, CancellationToken ct)`). Plain .NET types only, no entity class | no project of ours |
| `App.Db` | the entity classes (`Customers/Customer.cs`) next to their `IEntityTypeConfiguration<T>`; `Repository<T> : IRepository<T>` and the unit of work, written once over the `DbContext`; the migrations | `App.Core` |
| `App.Domain` | the services, written against `IRepository<T>` and `IUnitOfWork`; the query and paging every entity shares, written once | `App.Db` |
| `App.Api` | the endpoints every entity gets, written once as a generic mapping (`MapEntityEndpoints<T>()`); each feature's own endpoints; the error mapping; `Program.cs` | `App.Domain` |

A new entity is: the class implementing `IEntity` and its configuration in `App.Db`, and one line of
endpoint mapping in `App.Api`. Its own rules go in its Domain service (code principles 3.1).

## 2. Composition and dependency injection

- Each project has one extension method — `AddDb(configuration)`, `AddDomain()`, `AddApi()` — and
  `Program.cs` calls them in order.
- The generic repository is registered once as an open generic:
  `services.AddScoped(typeof(IRepository<>), typeof(Repository<>))`. Every other service is
  registered explicitly, one line each, with the built-in container.
- Dependencies arrive through the constructor.
- Lifetimes: the `DbContext` and what uses it are scoped; a stateless service is transient or scoped;
  a singleton holds state that is expensive to build or shared by all, and is thread-safe. A service
  depends only on services that live at least as long as it does.
- The container validates the graph at startup:
  `builder.Host.UseDefaultServiceProvider(o => { o.ValidateScopes = true; o.ValidateOnBuild = true; });`.
- The container disposes what it creates; a consumer leaves the disposal of its dependencies to it.
- Factories registered in the container are fast and synchronous; asynchronous initialization runs
  after resolution, in a hosted service or a static async factory.
- Configuration reaches services through the Options pattern.
- The interface is the public part: its consumer receives it by dependency injection and
  does not know the type that implements it. The implementation is `internal`.
- Time comes from `TimeProvider`.

## 3. Api

- Minimal APIs: `MapGroup` and `TypedResults`, with the result union in the signature
  (`Task<Results<Ok<T>, NotFound>>`).
- Validation: `builder.Services.AddValidation()` with DataAnnotations on the request records.
- Every entity has one list endpoint, `POST /<entities>/load`, written once in the generic mapping:
  the DevExtreme load options (`DataSourceLoadOptionsBase`, package `DevExtreme.AspNet.Data`) arrive
  in the JSON body and are answered with
  `await DataSourceLoader.LoadAsync(repository.Query(), options, cancellationToken)`. The options
  decide the shape: whole entities; only the fields `Select` asks, also through navigations; or, with
  `Group`, keys, counts and summaries per group, every level forced not expanded, so a group never
  carries rows. Filter, sort, paging, grouping and summaries run in SQL on the `IQueryable`, and
  DevExtreme's `LoadResult` leaves as it is. Before running, the base forces what the client does not
  decide (`AllowAsyncOverSync = false`, grouping and projection by the provider), refuses with a 400
  and the reason a field that does not exist or is reserved (`[JsonIgnore]`), a `Select` together
  with `Group`, rows asked without `Take` or above the page limit; an error DevExtreme or the database
  raises on the options is a 400 too.
- The OpenAPI document (`AddOpenApi()`; in Development `MapOpenApi()` and the Scalar UI,
  `MapScalarApiReference()`) describes every endpoint and type as they are, names as declared, so the clients generated from it match the server; the base's transformers complete what
  the platform cannot see:
  - every operation has its name, given once in the generic mapping from the entity's name
    (`.WithName("Customers_Load")`, `Customers_GetById`): it is the operation id, and the generated
    client's method is called by it;
  - every answer is declared, so the generated client receives each status with its body typed: the
    success and the expected failures by the result union of the signature
    (`Task<Results<Ok<T>, NotFound>>`), the errors the exception handler writes once on the group
    (`MapGroup(route).ProducesProblem(StatusCodes.Status500InternalServerError)`, and
    `.ProducesProblem(StatusCodes.Status400BadRequest)` on the load, whose options can be refused);
  - the load's response is documented as `LoadResultOf<Entity>` — `data`, `totalCount`, `groupCount`,
    `summary`, with `data` the entity's rows or the groups (`key`, `items`: the inner groups or null,
    `count`, `summary`) — by one `IOpenApiOperationTransformer` of the base, registered with
    `AddOpenApi(o => o.AddOperationTransformer<LoadResults>())`, which finds the entity in the metadata
    the generic mapping attaches to the load (`.WithMetadata(new LoadOf(typeof(T)))`). The generated
    client knows which entity each load lists, and the frontend computes the exact shape of `data` from
    the request (frontend branch); DevExtreme's own `LoadResult`, whose `data` has no type, leaves the
    document;
  - the errors are the one `ProblemDetails` of the document, `application/problem+json`, its schema
    completed with the members the application adds — `Code` and the `errors` of a failed binding —
    so the generated client reads them typed;
  - a type serialized through a converter of ours is given its schema (a `DateOnly` is
    `string`/`date`);
  - the document is a file at the repository's root, `openapi/<Api project>.json`, written by a test: the
    API test host (`WebApplicationFactory<Program>`, Development environment, `testing.md`) reads
    `/openapi/v1.json` and compares it with the file; a difference rewrites the file and fails the
    test. The contract changes with a diff someone reads, and the frontend generates its client from
    that file. The build does not generate the document: it would start the host, and the
    configuration validated at startup stops it.
- Errors: ProblemDetails — `AddProblemDetails()`, `UseExceptionHandler()`, `UseStatusCodePages()` —
  for every failure, the framework's own included: an unreadable body, a failed binding, an unknown
  route. One `IExceptionHandler` maps each error code to its status in a switch expression whose last
  arm throws `UnreachableException`; a unit test runs every `Enum.GetValues<ErrorCode>()` through the
  mapping, so a new code without its status turns the test red. The problem carries the code as a
  member, `Code`, with its name as declared, added in one place
  (`AddProblemDetails(o => o.CustomizeProblemDetails = …)`) so the framework's problems carry it too,
  and the client switches on it.
- Endpoints exchange the entity itself, so the client maps the same shape. A record of its own
  carries composite data — several entities together, a computed summary.
- The HTTP JSON options are the application's JSON settings (language overlay §6), applied in
  `ConfigureHttpJsonOptions`.

## 4. Outgoing calls

- HTTP clients are typed clients from `IHttpClientFactory` (`services.AddHttpClient<TClient>()`) with
  the standard resilience pipeline — rate limiter, total timeout, retry with backoff, circuit breaker,
  attempt timeout — from `.AddStandardResilienceHandler()` (package
  `Microsoft.Extensions.Http.Resilience`).
- A client that lives for the whole application sets `PooledConnectionLifetime` on its
  `SocketsHttpHandler`.
- Other dependencies get a pipeline of their own with `AddResiliencePipeline` (package
  `Microsoft.Extensions.Resilience`): timeout, retry with exponential backoff and jitter, circuit
  breaker.

## 5. Background work

- Background work is a `BackgroundService` whose `ExecuteAsync` loop observes `stoppingToken`;
  `HostOptions.ShutdownTimeout` bounds the orderly stop.

## 6. Configuration, logging, observability

- Options: `AddOptions<T>().BindConfiguration(section).ValidateDataAnnotations().ValidateOnStart()`.
  `appsettings.Development.json` holds the development values, and no `appsettings*.json` holds a
  secret.
- Secrets reach the configuration from `.00-secrets/`, as one more source added after the
  `appsettings` files: `builder.Configuration.AddJsonFile(".00-secrets/appsettings.secrets.json",
  optional: false)`. A clone that is still locked (`git-crypt unlock` not run) stops at startup on that file.
  A project without `.00-secrets/` has no such source: its first secret comes after `/dev:j-init-secrets`.
- `App.Api` configures Serilog with the console and file sinks from the `Serilog` configuration section,
  plus `UseSerilogRequestLogging()`; the console sink is how logs reach a terminal or a container's
  output.
- Health: `MapHealthChecks("/health/live")` for the process and `MapHealthChecks("/health/ready")` with
  the dependency checks (`AddHealthChecks().AddDbContextCheck<TContext>()`, tagged for readiness).
- Traces and metrics with OpenTelemetry (`AddOpenTelemetry().WithTracing(...).WithMetrics(...)`,
  package `OpenTelemetry.Extensions.Hosting`).

## 7. Security — with `branches/security.md`

- A fallback policy requires an authenticated user on every endpoint
  (`AddAuthorizationBuilder().SetFallbackPolicy(...RequireAuthenticatedUser()...)`); a public endpoint
  carries `AllowAnonymous()`.
- An endpoint receives the caller's identity from the authentication service.
- What a caller may do: a named policy on the group (`RequireAuthorization("<policy>")`), and a rule on one record in
  its Domain service, which reports the refusal with its error code.
- The API listens on HTTPS; outside Development it sends HSTS (`UseHsts()`).
- Inbound load: `AddRateLimiter` with a named policy, applied with `RequireRateLimiting` on the groups
  that need it.
