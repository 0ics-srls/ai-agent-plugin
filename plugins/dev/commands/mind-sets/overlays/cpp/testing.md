# C++ — Tests

How `testing-principles.md` is written in a C++ project: CTest runs the tests, written with the
framework chosen in LISTEN — GoogleTest with GoogleMock, or Catch2 with trompeloeil.

---

## 1. The runner

CTest, through the test presets of the pack's `CMakePresets.json`. One test program per test file,
named after it; each test carries its level as a label and a time limit (testing principles 7.3).

- `ctest --preset unit` — the default, fast run (testing principles 6.2).
- `ctest --preset all` — unit and integration.
- `ctest --preset asan` — everything, under the sanitizers.

The presets run the tests in parallel, print a failed test's output, and fail when no test is
selected. The build comes first: `cmake --build --preset debug`.

## 2. The levels

- `tests/unit/` — the logic, on doubles of the Core contracts, in memory.
- `tests/integration/` — the adapters on the real thing (a real file, a real engine), each test in a
  place of its own so the tests run side by side (testing principles 7.1).
- A test's name says the behaviour.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour.
- **A call across the boundary that is itself the behaviour** is a mock of the contract: with
  GoogleMock a `StrictMock` (so an unexpected call fails), with Catch2 trompeloeil's `mock_interface`
  and a `REQUIRE_CALL`.
- The test keeps the double it hands in through a `std::shared_ptr` (`language.md` §1).
