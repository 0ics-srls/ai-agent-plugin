# C — Language

How the principles and the code principles are written in C23.

---

## 1. Language and conventions

- **C23**: `nullptr`, `bool` as a keyword, `[[nodiscard]]`, an enumeration with its underlying type. A
  POSIX program defines `_POSIX_C_SOURCE` for the whole build.
- **The names**: functions, variables, types and members
  `snake_case`; enumerators and macros `UPPER_CASE`; a public function starts with its module's name.
  No `_t` suffix: POSIX reserves it.
- **A header has an include guard**; **a file includes what it uses**; **a function used only in its
  file is `static`**.
- **A contract is a struct of function pointers with the implementation's `void *context`**, in Core;
  the implementation is a function that returns it filled, and the consumer keeps it by value (code
  principles 1.8). A double is another function that returns the same struct (`testing.md` §3).
- **No implicit truth**: a `bool` is set or returned as `true`/`false`; an integer is compared
  explicitly.
- **Memory**: every allocation is freed on every path, by the function that owns it.
- **A buffer has a size from a named constant**, and text is copied bounded by that size.
- **The console is never written directly** — `printf`, `puts`, `perror`, `fprintf(stderr, …)`: the
  pack's ast-grep rule `c-no-console-output` refuses them; output goes through the logger (§4).

## 2. Concurrency and waiting

A thread is joined by its owner; a wait is on the signal of whoever does the work — a condition
variable with a deadline — never a `sleep` in a loop (code principles 4.7). Data shared between threads
is behind one mutex, or written before the threads start and only read after.

## 3. Errors

Every function that can fail returns an error code from the domain's closed set, `[[nodiscard]]`; its
results go out through pointer parameters, and a lookup that finds nothing says so (principles 4.1).
Each code has its declared name, for the logs.

## 4. Logging

One logger, configured once by `main`, with its sinks (the console, a file). A constant format, the
values its arguments.

## 5. Project and build

- **CMake with Ninja**, and the pack's `CMakePresets.json` (`debug`, `asan`; the test presets `unit`,
  `all`, `asan`); the build goes to `build/<preset>/`.
- **One library per layer**: Core (the data and the contracts), Domain, the adapters, the application
  with `main`, the composition root. A library sees only the headers of what it links: the build
  enforces the layers. Every `add_library` names its type.
- **Every dependency, with its version, in one file** (`cmake/dependencies.cmake`, principles 6.2); its
  license admitted by principles 6.4.
- **The gate is the build.** The pack's `cmake/lint-gate.cmake` gives `lint_gate(<target>)`: the
  warnings that find a defect at error, and clang-tidy on each source with the checks that find one —
  the static analyzer, the bugprone and cert families, a chosen list; every target calls it. The
  manifest's `native_lint` builds. No check of names, of style or of formatting: they find no defect,
  and on code that exists they only make it be rewritten.
- **The version** is `project(… VERSION)`, logged at startup (operations 2).
- **The audit of the dependencies** (principles 6.5), in `@gate-final`: osv-scanner on the fetched
  sources, as in C++ (`overlays/cpp/language.md` §5).

## 6. Serialization

Each field is written under its declared name and an enumeration as its declared name, from one table
that also reads it back (code principles 3.5). The serialization code sits in the adapter.

C has no mapper of its own, so the adapter is the mapper (code principles 3.7): one function per
struct reads its fields from the parsed tree (`cJSON_GetObjectItemCaseSensitive` with `cJSON_IsNumber`,
`cJSON_IsString`…), fails on a field missing or of another type, and frees the tree; nothing else
sees a `cJSON *`.

## 7. What j-setup and j-new-project read in a C project

- **Recognized by**: `CMakeLists.txt` whose `project()` names `C` (not `CXX`), with `*.c`/`*.h`
  sources. A project that names both `C` and `CXX` reads both overlays, each on its own sources.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every C project |
  | `testing.md` | every C project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`j-new-project`): what is built — a library or a command-line tool; whether it
  is a POSIX program.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `CMakeLists.txt`; the pack's
  `.clang-tidy`, `CMakePresets.json` and `cmake/lint-gate.cmake` go to that folder.
- **Vendored** (`@vendored-globs`): `build/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `cmake --build --preset debug` and the program from `build/debug/`; a library
  has none.
- **Where its errors show** (`j-debug`): the build's output (compiler, clang-tidy, analyzer); the
  failed test's report; the sanitizers' report of the `asan` run; the program's log.
