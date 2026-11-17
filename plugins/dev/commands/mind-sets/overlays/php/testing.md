# PHP — Tests

How `testing-principles.md` is written with PHPUnit.

---

## 1. The runner

- **A project that already has its tests keeps them where they are and as they run.** What follows is
  how a new project is written. In an existing project whose owner kept its tests (`language.md` §7),
  a new test goes beside the ones that are there — their folder, their naming, their suite — and runs
  with the project's own configuration; no plan, review or audit proposes to move the tests or to
  change the runner's options. `testing-principles.md` holds all the same.
- PHPUnit, with the pack's `phpunit.xml`: a warning, a deprecation or a test with no assertion is a failure.
- **The default run is the fast one** (testing principles 6.2), by the pack's `defaultTestSuite`: `vendor/bin/phpunit`; the full run
  names both suites, `vendor/bin/phpunit --testsuite=Unit,Feature`.
- PHPUnit fails a run with no test only with `failOnEmptyTestSuite`, which the pack sets.
- Several inputs of one behaviour are one `#[DataProvider]` (testing principles 1.4).
- A test's name says the behaviour: `test_should_<behaviour>_when_<condition>`. One test class for one production class.

## 2. The levels

- `tests/Unit/`: the logic, on doubles of the contracts, no framework boot.
- `tests/Feature/`: the code that talks to the outside on the real thing (testing principles 7.2); each test leaves nothing behind.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour, in `tests/Doubles/`.
- **A call across the boundary that is itself the behaviour** is PHPUnit's `createMock` of the interface, and the test states the
  call with `expects`.
- Plain data and pure functions are used as they are. Test objects come from shared builders (testing principles 5.1).
