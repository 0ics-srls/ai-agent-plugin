# C# / .NET 10 — EF Core

How `branches/data.md` is written with EF Core.

---

## 1. Data — EF Core

- The `DbContext` and its `DbSet`s are `internal` to `App.Db`: the layer exists to hide them.
- `IUnitOfWork` commits through one `SaveChangesAsync` at the end of the operation.
- Reads go through `IRepository<T>.Query()`, untracked (`AsNoTracking`).
- Every list query is bounded: a page size with a maximum, with `Skip`/`Take` for numbered pages and
  keyset pagination (`Where(x => x.Id > lastId).Take(n)`) for next-page navigation over large tables.
- Related data is loaded in the same query: `Include` (with a filtered include where a subset is
  needed), and `AsSplitQuery()` when several collections are included. Lazy-loading proxies stay
  disabled.
- A navigation property is filled only when its query includes it: loaded without the `Include`, it
  is `null` whatever its declaration says. Its declaration in the entity is EF's pattern,
  `public Customer Customer { get; set; } = null!;` — the one place a `null!` is allowed, in the
  entities of the Db project (the pack's rule leaves `*.Db/` out); a scalar is `required`. A query that
  reads a navigation includes it, or projects with `Select` into a type of its own; code that receives
  an entity does not read a navigation its query did not load.
- A large result set is streamed: `AsAsyncEnumerable()` in the query, `IAsyncEnumerable<T>` up to the
  endpoint.
- Indexes back the columns the queries filter and sort on.
- SQL written by hand goes through `FromSql` with interpolated parameters; a dynamic column or table
  name comes from a fixed list.
- Mapping in `IEntityTypeConfiguration<T>`, loaded with `ApplyConfigurationsFromAssembly`.
- Columns carry the property names as declared; the model adds no naming convention.
- Enums are stored as their names: the base sets the conversion once for every enum property of the
  model (`EnumToStringConverter<TEnum>` — the mechanism behind `HasConversion<string>()`), with a
  column length that fits the longest name, so an entity's configuration declares nothing for it.
- Optimistic concurrency: a version column marked `IsConcurrencyToken()` on the entities that need
  it; `DbUpdateConcurrencyException` becomes a conflict error.
- A unique-key violation (`DbUpdateException` from the commit) becomes a conflict error, caught where
  the operation commits.
- Unique values are normalized before they are stored (an e-mail: `Trim()` and
  `ToLowerInvariant()`).
- Migrations live in `App.Db`; the deploy applies them with a migration bundle
  (`dotnet ef migrations bundle`) before the new version starts.
- The database provider retries transient failures with its execution strategy
  (`UseNpgsql(connectionString, o => o.EnableRetryOnFailure())`); a unit of work that opens its own
  transaction runs inside `Database.CreateExecutionStrategy().ExecuteAsync(...)`. The command timeout
  is configuration (`o.CommandTimeout(seconds)`).
