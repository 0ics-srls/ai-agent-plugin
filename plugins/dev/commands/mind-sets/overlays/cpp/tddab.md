# C++ — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in a C++ project. How a test
is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a C++ project; a plan copies them
into its blocks (`tddab-planner.md`, "The commands, by level"). `BUILD` is `cmake --build --preset
debug`; `{file}` is a test file's name without its extension, which is its program's name.

| Key | C++ |
|---|---|
| `@test-focused-<component>` | `BUILD && ctest --preset all -R '^{file}\..*{test}$'` |
| `@test-block-<component>` | `BUILD && ctest --preset all -R '^{file}\.'`, once for each test file the block touches |
| `@test-fast` | `BUILD && ctest --preset unit` |
| `@test-slow` | `BUILD && ctest --preset all` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `BUILD && ctest --preset all`, the `asan` build and run, the audit (`language.md` §5) |

Before the tests, the component's gate (`language.md` §5): the build runs the warnings and clang-tidy.

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `tests/unit/` on doubles; an
adapter in `tests/integration/` on the real thing (`testing.md` §2).

## 3. The RED of a block

The block's test file, including the header of what the block builds: without it the build stops;
then, with a wrong behaviour, the failing test names it.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a C++ block

- The names, the contracts and the ownership of `language.md` §1; a result that can fail is an
  `std::expected` with the domain's error (§3).
- A new library is a target with its type, linked only to the layers below it, and calls `lint_gate`;
  a new dependency goes to `cmake/dependencies.cmake` with its version.
- The state of a contract on fakes; a call across the boundary on a mock (`testing.md` §3).
- No console write: the logger (`language.md` §4).

## 6. The skeleton's blocks

The form in C++ of each block of the skeleton `j-new-project` plans for a library or a command-line
tool (a library drops block 4):

| Block | C++ |
|---|---|
| 1 | the project: `CMakeLists.txt`, the pack's files as j-setup copied them, `cmake/dependencies.cmake` with the framework chosen in LISTEN; Core — the contracts, the first entity, the errors. RED: the first test program builds under the gate and runs |
| 2 | the adapter of the first entity, its serialization as is (`language.md` §6). RED: on the real file or engine |
| 3 | Domain — the first entity's service on the contracts. RED: its unit tests on the doubles |
| 4 | the application — the settings read and checked at startup, the logger, the version logged at startup, the composition root (`language.md` §4-5). RED: the program started without its settings stops and names the missing one |
