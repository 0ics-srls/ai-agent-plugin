# C# / .NET 10 — Language

How the principles and the code principles are written in C# 14 on .NET 10.

---

## 1. Language and conventions — C# 14

- Nullable reference types are enabled. A required string starts as `string.Empty`; an optional
  value is declared nullable (`string?`); every non-nullable member gets its value at its
  declaration or in the constructor.
- The nullable analysis is not silenced (code principles 3.3): no `!` in production code —
  `x!.Name`, `return y!`, `default!` — and a value a library declares nullable but the program knows
  is there fails where that is known: `found ?? throw new InvalidOperationException("…why…")`. No
  `#nullable disable`, no `#pragma warning disable`. The pack's ast-grep rules `no-null-forgiving`,
  `no-null-forgiving-initializer`, `no-nullable-disable` and `no-pragma-warning-disable` refuse them;
  the tests are out of the first two, generated code out of the last two. The one exception is EF
  Core's navigation properties (`efcore.md` §1).
- Records built with initializers declare their mandatory members `required`.
- Injected dependencies arrive through a primary constructor.
- Where a property transforms what it stores, it uses the `field` keyword:
  `public string Name { get => field; set => field = value.Trim(); }`. Inside an accessor, locals take
  a name other than `field`, which is a keyword there (CS9273).
- Where a type gets extension members, they are declared in an `extension(...)` block.
- Collections are built with collection expressions and spread: `int[] all = [..first, ..second];`.
- A variadic method on a hot path takes `params ReadOnlySpan<T>`.
- Values are `record` / `readonly record struct` with `init` properties. Entities are classes that
  implement `IEntity`, with public `get; set;` properties; the rules that govern their changes live
  in the Domain service, except the state machine of a state the entity holds, which the entity
  hosts with that state read-only outside (code principles 2.1, 3.1).
- Closed sets are `enum`s.
- Names follow the .NET conventions: PascalCase for types and members, camelCase for locals and
  parameters, `I` prefix for interfaces, `Async` suffix for asynchronous methods.
- `var` is used where the type is evident from the right side (`new`, a cast, a literal); elsewhere the
  type is written.
- Short strings are composed with interpolation, long text in loops with `StringBuilder`, multi-line
  text with raw string literals (`"""`).
- Callbacks use `Func<>` and `Action<>`.
- Conditions use the short-circuit operators `&&` and `||`.
- Disposable locals use the `using` declaration (`using var stream = ...;`).
- The public members of a library shared by several applications carry XML documentation comments.

## 2. Async

- The whole call chain is asynchronous, from the I/O call up to the endpoint: a method that calls an
  async API is itself `async` and awaits it. Waiting for a task always goes through `await`.
- A method that does work is `async` and awaits; a method that only forwards to one overload returns
  that task directly.
- Every asynchronous method returns `Task`, `Task<T>`, `ValueTask` or `ValueTask<T>`. Event and timer
  work is a `Task`-returning method; periodic work is a `PeriodicTimer` loop in a hosted service.
- `Task` and `Task<T>` are the default. `ValueTask<T>` is for a hot path that usually completes
  synchronously, and each `ValueTask` is awaited once, directly.
- A value already known is returned with `Task.FromResult` (or as a completed `ValueTask<T>`).
- I/O, data access and request/response bodies use their async APIs (`ReadToEndAsync`,
  `ReadFormAsync`, `ToListAsync`, `SaveChangesAsync`). `Task.Run` is for CPU-bound work outside the
  request; long-running work lives in a hosted service.
- Cancellation: every method that does I/O takes a `CancellationToken` as its last parameter and passes
  it to every call that accepts one; a loop checks it with `ThrowIfCancellationRequested()`. A
  `CancellationTokenSource` created for a timeout lives in a `using`.
- A `TaskCompletionSource` is created with `TaskCreationOptions.RunContinuationsAsynchronously`.
- Streams and writers are closed with `await using`.
- An object that needs asynchronous initialization is built by a static `async` factory method.
- Background work receives copies of the request data it needs and opens its own scope with
  `IServiceScopeFactory.CreateAsyncScope()`.
- State travels as parameters.
- Asynchronous sequences use the async LINQ built into .NET 10 (`System.Linq.AsyncEnumerable`).
- The application's own code awaits plainly; a general-purpose library shared by several
  applications awaits with `ConfigureAwait(false)`.

## 3. Waiting and concurrency

- Every wait is awaitable and waits for a signal: `await` on the task that does the work, a
  `Channel<T>` reader (`ReadAsync`, `ReadAllAsync`), `SemaphoreSlim.WaitAsync`, a
  `TaskCompletionSource` completed by the producer, `PeriodicTimer.WaitForNextTickAsync` for a
  schedule. The code that starts asynchronous work hands its caller the `Task` that completes with it.
- A deadline on a wait: `await task.WaitAsync(timeout, timeProvider, cancellationToken)`, or a
  `CancellationTokenSource` with `CancelAfter` linked to the caller's token.
- `Task.Delay(delay, timeProvider, cancellationToken)` is for a backoff or a schedule.
- Mutual exclusion in async code is a `SemaphoreSlim(1, 1)` with `WaitAsync`; around synchronous code
  it is a `System.Threading.Lock` field with `lock`.
- Producer/consumer work goes through a bounded `Channel<T>` (`Channel.CreateBounded<T>`), so a slow
  consumer slows the producer.

## 4. Exceptions

- An exception is for the unexpected. An outcome that is part of normal use is a return value: a
  lookup that finds nothing returns `null` (`Task<T?>`), and the endpoint answers `404`.
- A parameter's type says whether it may be absent, and the compiler checks every caller: a parameter
  that is not nullable is not tested for null again — no `ArgumentNullException.ThrowIfNull` on it.
  What the type cannot say — a name that must not be empty, a count that must not be negative — a
  public member of a contract refuses with the throw helpers
  (`ArgumentException.ThrowIfNullOrWhiteSpace`, `ArgumentOutOfRangeException.ThrowIfNegative` and
  their siblings), at the top of the method, before its first `await`. Business validation of incoming
  data happens once, at the boundary.
- The predefined types come first: `ArgumentException` for a bad argument,
  `InvalidOperationException` for a call the object's state does not allow. A custom exception
  exists when a caller catches it by type; its name ends in `Exception` and it has the three standard
  constructors.
- A `catch` names the specific type it handles, optionally with a `when` filter, and handles it there;
  the others travel up to the global handler.
- A rethrow inside `catch` is the bare `throw;`, which keeps the stack trace; a wrapping exception
  carries the original as `innerException`.
- Cancellation is caught as `OperationCanceledException`.
- A method that fails leaves the state as it found it.
- `using` releases resources; `finally` is for cleanup of what is not `IDisposable`.
- Messages are full sentences ending with a period.

## 5. Solution and build

- Solution file `.slnx`, created with `dotnet new sln --format slnx`.
- `Directory.Build.props` at the folder of the solution is the pack's,
  `${CLAUDE_PLUGIN_ROOT}/lint-rules/csharp/native/Directory.Build.props`, which /dev:j-setup copies: `net10.0`, the latest
  language, nullable references and implicit usings, every warning an error, the
  artifacts output, the NuGet audit of every transitive package.
- Central Package Management: `Directory.Packages.props` at the folder of the solution, with
  `ManagePackageVersionsCentrally` `true` and `CentralPackageTransitivePinningEnabled` `true`, holds
  every version as a `PackageVersion`; each `.csproj` lists its `PackageReference`s by name, without
  `Version`. A package is added with `dotnet add package <name>`, which writes the version there.
- The gate is one command, `dotnet build App.slnx`, and every warning is an error
  (`TreatWarningsAsErrors`): the compiler's, the nullable analysis included, and the analyzer's. The
  analyzer runs the SDK's standard level plus the rules the pack's `.editorconfig` lists one by one —
  each because it finds a defect: a resource not released, a call that blocks, an error of logic, a
  security hole. Naming, style, library design guidelines and micro-optimization are not in the gate,
  and the gate checks no formatting: they find no defect, and on code that exists they only make it
  be rewritten. It names the solution: the unit filter `App.Unit.slnf` sits beside it.
- The gate checks the project's own sources. The code under `externals/` — the base library, another
  submodule — builds in the solution with its own settings: the pack's `externals/Directory.Build.props`,
  `externals/Directory.Packages.props` and `externals/.editorconfig`, which /dev:j-setup copies, stop the
  project's build settings, its central package management and its style there (a submodule's own
  files, nearer, win); the build takes no `-warnaserror`, which would turn the submodule's warnings into
  errors.
- Every warning is fixed in the code that raises it. A rule joins or leaves the pack's list only by
  the project owner's decision, one rule at a time, with its reason.
- `.editorconfig` at the folder of the solution is the pack's, `${CLAUDE_PLUGIN_ROOT}/lint-rules/csharp/native/.editorconfig`,
  which /dev:j-setup copies: the rules of the gate, each with what it finds, the migrations as generated
  code, and the two rules about releasing resources off in the test projects.
- A library shared by several applications, UI applications included, turns CA2007 on in its own
  `.editorconfig` (`dotnet_diagnostic.CA2007.severity = warning`): there every `await` carries
  `ConfigureAwait(false)`.
- `global.json`: minimum SDK `10.0.100`, `rollForward` `latestFeature`, test runner
  `Microsoft.Testing.Platform`.
- The development files, written by the first block: `.gitignore` (`dotnet new gitignore`); `compose.yaml` with the
  local database where there is one — the project's engine, a development-only password, a healthcheck; the README
  with the commands of `j-settings.md`.
- Version: `VersionPrefix` in `Directory.Build.props` plus the CI build number; the application reads
  `AssemblyInformationalVersionAttribute`, answers it on `GET /version` and logs it at startup.
- Native AOT is enabled only for a CLI or serverless tool, on explicit request.

## 6. Serialization and logging

- JSON is as is, with one set of `JsonSerializerOptions` built in one place and used by every
  serializer of the application — HTTP, messages, files, outgoing clients: `PropertyNamingPolicy =
  null`, `DictionaryKeyPolicy = null`, `new JsonStringEnumConverter()` with no naming policy, and
  `NumberHandling = JsonNumberHandling.Strict`: a number travels as a number, so the OpenAPI document
  types it `integer` or `number` and not `integer | string`.
- Every serialized form is read into the application's types and written from them (code principles
  3.7) — the mapper of each form, and the hand practice it replaces:
  - JSON: `JsonSerializer` with the options above, `required` members and `UnmappedMemberHandling.Disallow`
    — not a `JsonDocument` or `JsonNode` walked by property (`GetProperty` throws when the property is
    missing, `TryGetProperty` falls back in silence, `GetValue<int>` on a string throws), nor a
    `JsonObject` built by hand;
  - XML: `XmlSerializer` or `DataContractSerializer` — not `XDocument`, `XmlDocument` or XPath walked by
    name (`Element("a")!.Value` throws when the element is missing);
  - YAML: YamlDotNet's `Deserialize<T>` — not the nodes of a `YamlStream`;
  - CSV: CsvHelper's `GetRecords<T>` with its `ClassMap` — not `Split(',')` and indexes, where a column
    moved is read in silence;
  - the configuration: Options bound and validated at start (`AddOptions<T>().BindConfiguration(…)
    .ValidateDataAnnotations().ValidateOnStart()`) — not `configuration["Section:Key"]` or
    `GetValue<T>("Key")` in the code, where a missing key is `null` or `0`;
  - a request: model binding on typed parameters (`[FromBody]`, `[FromQuery]`, `[FromRoute]`,
    `[FromHeader]`) — not `Request.Query["x"]`, `Request.Form["x"]` or `Request.Headers["x"]`;
  - the database: EF Core's entities, or Dapper's `Query<T>` where the SQL is written — not
    `reader["column"]` or the rows of a `DataTable`;
  - performance, only on the user's request: `Utf8JsonReader`/`Utf8JsonWriter` by hand, in one reader.
- Logging is code the author writes: `ILogger<T>` and its `Log...` methods, with a constant message
  template whose placeholders are named —
  `logger.LogInformation("Customer {CustomerId} created", customer.Id)`. The template stays constant
  (CA2254).
- The console is a sink of the structured logger — Serilog's console sink, configured with the other
  sinks; the code writes through `ILogger<T>`, and `Console.WriteLine` appears nowhere in it.
- Polling a third-party system without signals lives in one class: a `PeriodicTimer` loop with its
  interval and deadline from Options, which completes a `TaskCompletionSource` or writes to a
  `Channel<T>` that the rest of the code awaits.

## 7. What /dev:j-setup and /dev:j-new-project read in a C# project

- **Recognized by**: `*.slnx`, `*.sln`, `*.csproj`; the stack from `TargetFramework` and the
  `PackageReference`s (ASP.NET Core, EF Core and its provider, HttpClient, messaging), which say the
  branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every C# project |
  | `testing.md` | every C# project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `efcore.md` | `branches/data.md` |
  | `aspnetcore.md` | `branches/service-layers.md`, `branches/api.md`, `branches/resilience.md`, `branches/operations.md`, `branches/security.md` (§7) |
  | `avalonia.md` | `branches/frontend.md`: a desktop client, `Avalonia` among the `PackageReference`s |
  | `bdd.md` | `bdd-overlay.md`, on request only |

  A backend service with a database reads all of them; a command-line tool reads `language.md` and
  `testing.md`, plus the branches it has.
- **What LISTEN asks** (`/dev:j-new-project`): for a service, the database engine (EF Core's provider);
  ASP.NET Core is the transport, not a question. A desktop client: the backend whose OpenAPI document its client is generated from.
- **What /dev:j-setup asks on an existing project**: tests on xUnit v2 — `xunit` among the
  `PackageReference`s, not `xunit.v3` — → ask with AskUserQuestion, once: migrate the tests to xUnit v3,
  or stay on v2? It is the owner's decision, and staying is a full answer. *Stay*: the gate turns the
  v3 rule off — `@lint-astgrep: ast-grep scan --globs '!externals/**' --off=no-xunit-abstractions` —
  the test levels are the commands the project already runs, on VSTest, and `global.json` gets no
  `test` key; `testing.md` §1 says how its tests are written. *Migrate*: nothing changes here — the
  migration is a work of its own, `/dev:j-new-feature`, and until it closes the project is on v2, set up as
  *Stay*. Nothing is asked about the mock library: the project keeps the one it has — Moq,
  NSubstitute — (`testing.md` §1).
- **The lint gate**: the manifest's `native_lint`, `App` the solution's name; its configuration files go
  to the folder of the solution, the pack's `externals/` files to `externals/` (§5).
- **Vendored** (`@vendored-globs`): `bin/`, `obj/`, `artifacts/`.
- **The test levels**: the keys of `tddab.md` §1 — `@test-fast` on the solution filter of the unit
  projects (`*.Unit.slnf`), `@test-slow` on the solution. Their commands need the test runner in
  `global.json` (§5), in the folder of the solution: `"test": { "runner": "Microsoft.Testing.Platform" }`.
  Only that key is added: the SDK of an existing `global.json` stays.
- **The start command**: `dotnet run --project src/App.Api`, the project that hosts the API
  (`aspnetcore.md` §1).
- **Where its errors show** (`/dev:j-debug`): the Serilog files and console of the running service
  (`aspnetcore.md` §6), the `ProblemDetails` the API answers with its `Code`, the build's and the tests'
  output.
- `App` in the overlays stands for the project's name.
