# Dart — Tests

How `testing-principles.md` is written with `package:test`.

---

## 1. The runner

- `dart test`; `flutter test` in a Flutter project. **The default run is the fast one** (testing principles 6.2): `dart test test/unit`; the
  full run is `dart test`.
- A run that finds no test is an error for `dart test`.
- `group` gathers a behaviour, `test` proves one; several inputs are a loop over a list of cases (testing principles 1.4).
- A test's name says the behaviour: `should <behaviour> when <condition>`.
- `Timeout` on a test that can hang, so it fails with its name (testing principles 7.3).

## 2. The levels

- `test/unit/`: the logic, on doubles of the contracts, in memory.
- `test/integration/`: the code that talks to the outside on the real thing (testing principles 7.2); each test owns its data.
- `test/` mirrors `lib/`, one test file for one production class.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour, in `test/helpers/`.
- **A call across the boundary that is itself the behaviour** is a `mocktail` mock of the contract, and the test verifies the call.
- Plain data and pure functions are used as they are. Test objects come from `test/helpers/` (testing principles 5.1).
