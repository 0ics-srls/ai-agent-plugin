# C++ — Language

How the principles and the code principles are written in C++23.

---

## 1. Language and conventions

- **C++23**, with the standard library: `std::expected`, `std::format`, ranges.
- **The names**: types `Leading_upper_snake_case`; an interface
  the same after an `I`; functions, variables, parameters and enumerators `snake_case`; private and
  protected members `m_`.
- **A type with behaviour is a `class`; a `struct` is plain data** — an entity, a value, the settings.
  An entity is data with an identity that travels as it is (code principles 3.1, 3.2).
- **A contract is an abstract class** in Core: special members deleted, a virtual destructor.
- **A dependency is injected by the constructor, and its ownership is always in the type**: a
  `std::shared_ptr` when it is shared, a `std::unique_ptr` moved in when the consumer is its only
  owner — decided case by case. Never a borrow: no reference member, no `std::reference_wrapper`, no
  raw pointer kept. The constructor refuses a null one (code principles 4.5).
- **Ownership is in the type** (RAII); no raw `new` or `delete`.
- **A function whose result says whether it worked is `[[nodiscard]]`.**
- **A value with a meaning is a named constant.**
- **No unchecked access**: `.at()`, `std::span`; no pointer arithmetic.
- **The console is never written directly** — `std::cout`, `printf`, `puts`, `std::print`: the pack's
  ast-grep rule `cpp-no-console-output` refuses them; output goes through the logger (§4) —
  a command-line tool's own output aside (§7).
- **A class stays open** (code principles 1.9): no `final` on a class or a struct — the pack's rule
  `cpp-no-final-class` refuses it. Closed on the owner's yes only: the reason in a comment above the
  class, then `// ast-grep-ignore: cpp-no-final-class`.

## 2. Concurrency and waiting

A thread is a `std::jthread`, stopped through its `std::stop_token`; a wait is on the signal of
whoever does the work — a future, a condition variable with the stop token — with a deadline, never a
`sleep_for` in a loop (code principles 4.7). A value shared between threads is immutable, or behind one
mutex held with `std::scoped_lock`.

## 3. Errors

An outcome the caller handles is a value: `std::expected<T, Error>`, the error a code from a closed set
with its detail (code principles 3.4); a lookup that finds nothing is an `std::optional`. An exception
of a library the project calls is caught in the adapter that calls it and returned as the domain's
error.

## 4. Logging

One logger, configured once by the entry point, with its sinks (the console, a file). The message is a
constant template, its values the arguments.

## 5. Project and build

- **CMake with Ninja**, and the pack's `CMakePresets.json`: `debug` and `asan` (Address and
  UndefinedBehavior sanitizers) to build; `unit`, `all` and `asan` to test (`testing.md` §1). The build
  goes to `build/<preset>/` (principles 6.3).
- **One library per layer**, each with its folder and its public headers: Core (the contracts, the
  entities, the errors), Domain, the adapters to the outside, the application with the composition
  root. **The layers are enforced by the build**: a library sees only the headers of what it links.
  Every `add_library` names its type.
- **Every dependency, with its version, in one file** (`cmake/dependencies.cmake`, principles 6.2),
  `SYSTEM`, so the gate checks only the project's own code; its license admitted by principles 6.4.
- **The gate is the build.** The pack's `cmake/lint-gate.cmake` gives `lint_gate(<target>)`: the
  warnings that find a defect at error, and clang-tidy run on each source with the checks that find one
  — the static analyzer, the bugprone family, a chosen list; every target of the project calls it. The
  manifest's `native_lint` builds. No check of names, of style or of formatting: they find no defect,
  and on code that exists they only make it be rewritten.
- **The version** is `project(… VERSION)`; the program logs it at startup (operations 2).
- **The audit of the dependencies** (principles 6.5), in `@gate-final`: osv-scanner on the fetched
  sources — `osv-scanner scan source -r --include-git-root --no-ignore --x-no-default-plugins
  --x-plugins vcs/gitrepo build/debug/_deps`.

## 6. Serialization

A struct is serialized by its declared names and an enumeration by its declared names (code principles
3.5). The serialization code sits in the adapter that reads or writes, not in the entity.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: nlohmann's `from_json`/`to_json` for each struct (`NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE`), read
  with `j.get<T>()` in the adapter — not `j["x"]` in the code: on a non-const object it inserts a
  `null`, in silence, and on a const one it is undefined behaviour; nor a `json` built by hand;
- every other form: one adapter per format that maps into the structs, and its parsed tree stays in
  it.

## 7. What /dev:j-setup and /dev:j-new-project read in a C++ project

- **Recognized by**: `CMakeLists.txt` whose `project()` names `CXX`, with `*.cpp`/`*.hpp` sources;
  `cmake/dependencies.cmake` says the test framework. A Godot extension (`godot-cpp`) has its game in
  a Godot project of its own, a GDScript component.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every C++ project |
  | `testing.md` | every C++ project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`/dev:j-new-project`): what is built — a library, a command-line tool, an
  extension; the test framework — GoogleTest with GoogleMock, or Catch2 with trompeloeil.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `CMakeLists.txt`; the pack's
  `.clang-tidy`, `CMakePresets.json` and `cmake/lint-gate.cmake` go to that folder.
- **A command-line tool**: `@lint-astgrep` carries `--off=cpp-no-console-output` —
  `ast-grep scan --globs '!externals/**' --off=cpp-no-console-output`.
- **Closed classes allowed** (`@closed-classes`): `@lint-astgrep` carries `--off=cpp-no-final-class`.
- **Vendored** (`@vendored-globs`): `build/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `cmake --build --preset debug` and the program from `build/debug/`; a library
  has none.
- **Where its errors show** (`/dev:j-debug`): the build's output (compiler and clang-tidy); the failed
  test's output; the sanitizers' report of the `asan` run; the program's log.
