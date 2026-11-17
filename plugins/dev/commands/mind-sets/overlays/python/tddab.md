# Python — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Python. How a test is
written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Python project; a plan copies them
into its blocks (`tddab-planner.md`, "The commands, by level").

| Key | Python |
|---|---|
| `@test-focused-<component>` | `uv run pytest {file}::{test}` — one test by its node id |
| `@test-block-<component>` | `uv run pytest {file}`, once for each test file the block touches |
| `@test-fast` | `uv run pytest` — `tests/unit`, the default of `pytest.ini` |
| `@test-slow` | `uv run pytest tests` — unit and integration |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `uv run pytest tests`, the audit (`language.md` §5) |

In an existing project that kept its tests (`language.md` §7), `@test-fast` and `@test-slow` are the
commands `j-settings.md` has, on the project's own test folder.

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `tests/unit/` on the doubles of
`tests/unit/doubles.py`; the code that talks to the outside in `tests/integration/` on the real thing
(`testing.md` §2). In a project that kept its tests, a block's tests go beside the ones that are
there (`testing.md` §1).

## 3. The RED of a block

The block's test file, importing the class the block will build and calling it as its contract says:
it fails first because the class does not exist, then because its behaviour is wrong — the failing test
names it.

## 4. The GREEN

The smallest code that makes the RED pass, typed, through the gate (`language.md` §5).

## 5. Rules of a Python block

- Every function typed; a closed set a `StrEnum` whose values are its names (`language.md` §1).
- A contract is a `Protocol`; the RED types its subject with the class it builds.
- The state of a contract on the fakes; a call across the boundary on `create_autospec` (`testing.md`
  §3).
- No `print`; a log message is constant, its values in `extra`.

## 6. The skeleton's blocks

The form in Python of each block of the skeleton `/dev:j-new-project` plans; the frameworks are the
project's, chosen in LISTEN.

| Block | Python |
|---|---|
| 1 | `uv init --package`; the pack's `ruff.toml`, `mypy.ini`, `pytest.ini` as /dev:j-setup copied them; the contracts (`Protocol`s) and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the storage: the first entity, the implementation of its contract written once, its tests in `tests/integration/` on the real store |
| 3 | the domain: the first entity's service on the contracts; `tests/unit/doubles.py` and the service's tests |
| 4 | the transport the project has, on the domain: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the settings validated at startup |
