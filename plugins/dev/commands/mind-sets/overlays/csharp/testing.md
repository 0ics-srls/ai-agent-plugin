# C# / .NET 10 — Tests

How `testing-principles.md` is written with xUnit v3 on .NET 10.

---

## 1. Tests

- **A project that already has its tests keeps its libraries.** What follows is how a new project is
  written. An existing project keeps its mock library — Moq, NSubstitute — and its test framework: new
  tests are written with them, as the tests beside them are, and no plan, review or audit proposes to
  replace them. `testing-principles.md` holds with any of them: a double fits what the test proves
  (4.2), whoever makes it. A project on xUnit v2 whose owner chose to stay there (`language.md` §7)
  writes its output through the `ITestOutputHelper` its test class receives
  (`using Xunit.Abstractions;`), and the v3 forms of this section — `TestContext.Current`,
  `Assert.SkipWhen`, Microsoft.Testing.Platform — do not apply to it.
- xUnit v3 on Microsoft.Testing.Platform. Assertions come from AwesomeAssertions (Apache 2.0, namespace
  `AwesomeAssertions`), the open continuation of FluentAssertions v7: FluentAssertions is commercial
  from v8, and its older free versions are the same package one upgrade away (principles 6.4).
- A test that awaits is `async Task`; every async call takes `TestContext.Current.CancellationToken`; output goes
  through `TestContext.Current.TestOutputHelper`; a conditional skip uses `Assert.SkipWhen` /
  `Assert.SkipUnless`.
- A test that waits for asynchronous work awaits the `Task` or signal the code exposes, with a
  deadline: `await work.WaitAsync(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken)`.
  Time-dependent logic runs on `FakeTimeProvider`, moved forward with `Advance(...)`.
- Names: `Method_Scenario_ExpectedBehavior` (`Create_EmailTaken_ReturnsConflict`).
- Each test is Arrange, Act, Assert, with one Act. Several inputs of the same behaviour are one
  `[Theory]` with `[InlineData]` or typed `TheoryData<...>`; the test body is straight-line code.
- Tests go through the public surface of the unit.
- The doubles (testing principles 4.2): the state a contract keeps — the repository, the unit of
  work — is a fake written by hand in `App.Testing` (`FakeStore`), and the clock is
  `FakeTimeProvider`; a call across the boundary that is itself the behaviour — a message sent, a
  notification, an external service — is a fake made by FakeItEasy (MIT), with its analyzer
  `FakeItEasy.Analyzer.CSharp`, which stops a call specification left without its assertion:
  `var notifier = A.Fake<INotifier>();` …
  `A.CallTo(() => notifier.OrderPlacedAsync(OrderId, A<CancellationToken>._)).MustHaveHappenedOnceExactly();`.
  Doubles are named for what they are (`FakeRepository<T>`), and the shared arrangement comes from
  builders and helper methods.
- `App.Core.Tests` — unit: what the Core holds with behaviour of its own — the query and page
  records, the error codes.
- `App.Domain.Tests` — unit: the services with in-memory implementations of `IRepository<T>` and
  `IUnitOfWork`, `FakeTimeProvider`, builders for the data.
- `App.Db.Tests` — integration on the real database engine started with Testcontainers: migrations,
  mapping, constraints, concurrency, queries.
- `App.Api.Tests` — `WebApplicationFactory<Program>` on the same Testcontainers database: status codes,
  ProblemDetails, serialization, the framework's own failures, and authorization where the security
  branch applies. The serialization tests
  read the raw JSON and check that a property name and an enum value arrive exactly as declared. The
  load is proved in each of its shapes — rows, `Select`, `Group` — and in its refusals. The contract
  test keeps `openapi/<Api project>.json` equal to the served document (`aspnetcore.md` §3), and every
  failure — the framework's ones too — is sent for real and its answer checked against what the
  document declares: status, `application/problem+json`, `Code`.
- `App.Db.Tests` reads an enum column back as text and checks it holds the declared name.
- The unit run (`@test-fast`) is the unit projects, through a solution filter
  (`App.Unit.slnf`) that each block creating a unit test project extends; the full run
  (`@test-slow`), at the end of a plan and before every merge, is the whole solution.
