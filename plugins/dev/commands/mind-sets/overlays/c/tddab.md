# C — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in a C project. How a test is
written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a C project; a plan copies them into
its blocks (`tddab-planner.md`, "The commands, by level"). `BUILD` is `cmake --build --preset debug`;
`{file}` is a test file's name without its extension, which is its program's name.

| Key | C |
|---|---|
| `@test-focused-<component>` | `BUILD && CMOCKA_TEST_FILTER='{test}' ctest --preset all --stop-on-failure -R '^{file}$' -V` |
| `@test-block-<component>` | `BUILD && ctest --preset all --stop-on-failure -R '^{file}$'`, once for each test file the block touches |
| `@test-fast` | `BUILD && ctest --preset unit --stop-on-failure` |
| `@test-slow` | `BUILD && ctest --preset all --stop-on-failure` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `BUILD && ctest --preset all --stop-on-failure`, the `asan` build and run, the audit (`language.md` §5) |

`--stop-on-failure` stops `ctest` after the first test that fails (`testing-principles.md` 6.3).

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `tests/unit/` on doubles; an
adapter in `tests/integration/` on the real thing (`testing.md` §2).

## 3. The RED of a block

The block's test file, including the header of what the block builds: without it the build stops;
then, with a wrong behaviour, the report names the failing test and the check.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a C block

- The names, the include guards, the contracts and the memory of `language.md` §1; a function that can
  fail returns the domain's error code, `[[nodiscard]]` (§3).
- A new library is a target with its type, linked only to the layers below it, and calls `lint_gate`;
  a new dependency goes to `cmake/dependencies.cmake` with its version.
- The state of a contract on a fake; a call across the boundary on a cmocka mock (`testing.md` §3).
- No console write: the logger (`language.md` §4).

## 6. The skeleton's blocks

The form in C of each block of the skeleton `/dev:j-new-project` plans for a library or a command-line tool
(a library drops block 3):

| Block | C |
|---|---|
| 1 | the project: `CMakeLists.txt`, the pack's files as /dev:j-setup copied them, `cmake/dependencies.cmake`; Core — the data, the contracts, the error codes; the first entity's service. RED: the service's unit tests on its doubles |
| 2 | the adapter of the first entity, its serialization as is (`language.md` §6). RED: on the real file or engine |
| 3 | the application — the settings read and checked at startup, the logger, the version logged at startup, `main` the composition root. RED: the program started without its settings stops and names the missing one |
