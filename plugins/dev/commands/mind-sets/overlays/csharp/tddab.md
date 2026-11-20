# C# / .NET 10 — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in C#: the tests by
level and the reference code of a block. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in C#; a plan copies them into its
blocks (`tddab-planner.md`, "The commands, by level").

| Key | C# |
|---|---|
| `@test-focused-backend` | `dotnet test --project {project} --filter-method "*{test}*"` |
| `@test-block-backend` | `dotnet test --project {project} --stop-on-fail on`, once for each test project the block touches |
| `@test-fast` | `dotnet test --solution App.Unit.slnf --stop-on-fail on` — the unit projects |
| `@test-slow` | `dotnet test --solution App.slnx --stop-on-fail on` — every project, integration included |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `dotnet run -c Release --project benchmarks/App.Benchmarks` on BenchmarkDotNet (MIT), where the project has benchmarks; otherwise `none` |
| `@gate-final` | the lint gate, `dotnet test --solution App.slnx --stop-on-fail on`, the frontend's part, `@test-e2e`, `@bench` where they are not `none` |

`--stop-on-fail on` stops a test project at its first failing test (`testing-principles.md` 6.3). The
projects of a solution run side by side, so another project may already have started when one fails:
the run is red at the first failure all the same. A project that stayed on xUnit v2 (`language.md`
§7) ends its test commands with `-- xUnit.StopOnFail=true`, the same option on VSTest.

Before the tests, the component's gate: `dotnet build App.slnx` (`language.md` §5).

xUnit v3 on Microsoft.Testing.Platform filters with `--filter-method`, `--filter-class`,
`--filter-namespace` and `--filter-trait`, each taking a name with `*` wildcards. A test project with
no test fails the run (exit code 8, "Zero tests ran"): a test project is created by the block that
writes its first test.

## 2. Each layer's block, at its level

The RED of a block runs at the level of its layer, in the test project `testing.md` assigns to it:
a Domain service on in-memory fakes, Db on the real database engine, Api through
`WebApplicationFactory<Program>`.

## 3. Reference RED — a Domain service block

```csharp
// tests/App.Domain.Tests/Customers/CustomerServiceTests.cs
using AwesomeAssertions;

namespace App.Domain.Tests.Customers;

public sealed class CustomerServiceTests
{
    private const string NewName = "Grace Hopper";
    private const int UnknownId = 404;

    // xUnit builds the class once per test: each test gets its own store and service.
    private readonly FakeStore _store = new();
    private readonly CustomerService _service;

    public CustomerServiceTests() => _service = new CustomerService(_store.Repository<Customer>(), _store.UnitOfWork);

    [Fact]
    public async Task RenameAsync_ExistingCustomer_StoresTheNewName()
    {
        var customer = _store.Add(CustomerBuilder.Default());

        var renamed = await _service.RenameAsync(customer.Id, NewName, TestContext.Current.CancellationToken);

        renamed.Should().BeTrue();
        _store.Get<Customer>(customer.Id).Name.Should().Be(NewName);
        _store.Commits.Should().Be(1);
    }

    [Fact]
    public async Task RenameAsync_UnknownId_ReturnsFalseAndCommitsNothing()
    {
        var renamed = await _service.RenameAsync(UnknownId, NewName, TestContext.Current.CancellationToken);

        renamed.Should().BeFalse();
        _store.Commits.Should().Be(0);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public async Task RenameAsync_BlankName_Throws(string name)
    {
        var customer = _store.Add(CustomerBuilder.Default());

        var act = () => _service.RenameAsync(customer.Id, name, TestContext.Current.CancellationToken);

        await act.Should().ThrowAsync<ArgumentException>();
    }
}
```

`FakeStore` and `CustomerBuilder` live in the shared test project (`tests/App.Testing`): the in-memory
implementation of the base contracts and the builders every test uses (testing principles 4.2, 5.1).

## 4. Reference GREEN

```csharp
// src/App.Core/Customers/ICustomerService.cs — a Core contract names no entity
namespace App.Core.Customers;

public interface ICustomerService
{
    Task<bool> RenameAsync(int id, string name, CancellationToken cancellationToken);
}
```

```csharp
// src/App.Domain/Customers/CustomerService.cs
using App.Core;
using App.Core.Customers;
using App.Db.Customers;

namespace App.Domain.Customers;

internal sealed class CustomerService(IRepository<Customer> customers, IUnitOfWork unitOfWork) : ICustomerService
{
    public async Task<bool> RenameAsync(int id, string name, CancellationToken cancellationToken)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);

        var customer = await customers.GetByIdAsync(id, cancellationToken);
        if (customer is null)
        {
            return false;
        }

        customer.Name = name;
        await unitOfWork.CommitAsync(cancellationToken);
        return true;
    }
}
```

The test project reaches the `internal` service through `InternalsVisibleTo`: each project names its
test projects in its `.csproj` (`<InternalsVisibleTo Include="App.Domain.Tests" />`).

## 5. Rules of a C# block

- A test that awaits is `async Task`; every async call takes `TestContext.Current.CancellationToken`.
- The reference code obeys the gate (`language.md` §5): no null test of a parameter that is not
  nullable, no `!`, no `Console`, no `[LoggerMessage]`.
- Code produced by source generators (DI registrations, serializers) is navigable only after a build;
  until then a code-navigation search that finds nothing is not proof of absence
  (`mind-sets/code-navigation.md`).

## 6. The skeleton's blocks

The form in C# / .NET 10 of each block of the skeleton `/dev:j-new-project` plans:

| Block | C# / .NET 10 |
|---|---|
| 1 | `dotnet new sln --format slnx`, `dotnet new globaljson`; `Directory.Build.props` and `.editorconfig` as /dev:j-setup copied them from the pack; `Directory.Packages.props` with Central Package Management; the base library, when there is one, already under `externals/` (/dev:j-new-project brought it in before the plan) with its projects added to the solution and the pack's `externals/` files beside it (`language.md` §5); the development files — `.gitignore` (`dotnet new gitignore`), `compose.yaml` for the local database, the README with the commands — `language.md` §5; `App.Core` — `aspnetcore.md` §1; `App.Core.Tests` and `App.Unit.slnf` listing it — `testing.md` §1. RED: the first test of the Core's page record |
| 2 | `App.Db`, EF Core, `dotnet ef migrations add Initial`, enums as names, migrations as generated code — `efcore.md`; `App.Db.Tests` on the real engine with Testcontainers, the database fixture in `App.Testing` — `testing.md` §1 |
| 3 | `App.Domain` — `aspnetcore.md` §1-2; `App.Domain.Tests` with the fakes of the Core contracts and the builders in `App.Testing`, added to `App.Unit.slnf` — `testing.md` §1 |
| 4 | `App.Api`, `AddValidation`, ProblemDetails, JSON options with naming policy null, the one load endpoint of every entity on the DevExtreme load options, OpenAPI (`AddOpenApi`) with the base's transformers — operation names, `LoadResultOf<Entity>`, every answer, the schemas of our converters — the Scalar UI (`Scalar.AspNetCore`, `MapScalarApiReference()`) — `aspnetcore.md` §3, `language.md` §6; `App.Api.Tests` on `WebApplicationFactory<Program>` and the database fixture, with the test that keeps `openapi/<Api project>.json` equal to the served document — `testing.md` §1 |
| 5 | `GET /version`, `/health/live` and `/health/ready`, Serilog from configuration, Options with `ValidateOnStart`, `appsettings.Development.json`, `launchSettings.json` — `aspnetcore.md` §6, the version `language.md` §5 |

With the security branch, the block between 4 and 5 is `aspnetcore.md` §7: the authentication and the
fallback policy.

A desktop client on Avalonia, as the frontend blocks of `/dev:j-new-project`:

| Block | Avalonia |
|---|---|
| F1 | `dotnet new avalonia.mvvm -n App.Desktop -o frontend`, added to the solution under the same gate, the first test — `avalonia.md` |
| F2 | the generated client — `avalonia.md` §1 |
| F3 | the calls as results: each answer the entity or the domain's error — `avalonia.md` §1 |
| F4 | the first entity's screen: its view model and its view — `avalonia.md` §2-3 |
| F5 | end to end: the headless application against the real backend — `avalonia.md` §5 |
