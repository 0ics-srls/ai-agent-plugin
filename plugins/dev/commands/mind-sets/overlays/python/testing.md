# Python — Tests

How `testing-principles.md` is written with pytest.

---

## 1. The runner

- **A project that already has its tests keeps them where they are and as they run.** What follows is
  how a new project is written. In an existing project whose owner kept its tests (`language.md` §7),
  a new test goes beside the ones that are there — their folder, their naming — and runs with the
  project's own configuration; no plan, review or audit proposes to move the tests, to add the
  runner's plugins or to change its options. `testing-principles.md` holds all the same.
- pytest, with the pack's `pytest.ini`: a warning is an error, markers and configuration strict.
- **The default run is the fast one** (testing principles 6.2): `uv run pytest` runs `tests/unit`;
  the full run names the folder, `uv run pytest tests`.
- A run that collects no test is red (pytest exits 5), not green.
- Asynchronous tests run with pytest-asyncio; a test has a time limit, so a test that hangs fails with
  its name.

## 2. The levels

- `tests/unit/` — the logic, on doubles of the contracts, in memory.
- `tests/integration/` — the code that talks to the outside on the real thing it talks to (testing
  principles 7.2): a real database, a real transport; each test leaves nothing behind.
- The test files are packages (`__init__.py`), named `test_<module>.py`; a test's name says the
  behaviour: `test_<method>_<scenario>_<expected>`.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, in `tests/unit/doubles.py`, with the real
  behaviour.
- **A call across the boundary that is itself the behaviour** is a mock bound to the contract:
  `create_autospec(Contract, instance=True)`, and the test asserts the call
  (`assert_awaited_once_with` / `assert_called_once_with`).
- Plain data and pure functions are used as they are.
