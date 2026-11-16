# C — Tests

How `testing-principles.md` is written in a C project: CTest runs the test programs, written with
cmocka — its assertions, and its mocks for a call across the boundary.

---

## 1. The runner

CTest, through the test presets of the pack's `CMakePresets.json`: `ctest --preset unit` (the default,
fast run), `ctest --preset all` (unit and integration), `ctest --preset asan` (everything under the
sanitizers). One test program per test file, named after it, with its level as a label and a time
limit; the presets fail when no test is selected. One test of a program runs through cmocka's filter,
`CMOCKA_TEST_FILTER`.

## 2. The levels

- `tests/unit/` — the logic, on doubles of the Core contracts.
- `tests/integration/` — the adapters on the real thing, each test in a place of its own.
- A test's name says the behaviour.

## 3. The doubles (testing principles 4.2)

A contract is a struct of function pointers (`language.md` §1), so a double is a set of functions that
fill it: the state a contract keeps on a fake with the real behaviour; the call across the boundary
that is itself the behaviour on a cmocka mock — the function checks its arguments and the test states
the call it expects.
