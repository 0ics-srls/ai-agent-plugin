# Dart — Language

How the principles and the code principles are written in Dart.

---

## 1. Language and conventions

- The current stable Dart 3; files `snake_case`, types `PascalCase`, members `camelCase`.
- **A closed set is an `enum`** (code principles 3.3). **A state machine is a `sealed` class whose subclasses are the states**, a
  `switch` on it exhaustive and with no `default` (code principles 2.1).
- **Values are immutable** (code principles 3.1): `final` locals and fields, `const` where it compiles, `freezed` for a value
  with `copyWith`; a value with a rule of its own checks it in its factory (code principles 2.4).
- **A contract is an `abstract interface class`**, shaped by its consumer.
- **Private by default** (code principles 4.4): `_` on members, `lib/src/` for the implementation, the package's barrel file
  exporting its public surface with `show`.
- **Constructor injection**: a composition root registers (`get_it` where the app uses it).
- `!` is not a way to silence the compiler (code principles 3.3): a null is handled with `?.`, `??` or a pattern, and a
  value known to be there fails where that is known (`?? (throw StateError('…why…'))`). No linter of Dart refuses `!`, so the
  code audit looks for it (card E6). No `print`: the gate refuses it — a command-line
  tool's own output aside (§7).
- A diagnostic is silenced with `// ignore: <name> — <why>`, on the line.
- **A class stays open** (code principles 1.9): no `final class` — no linter of Dart refuses it, so
  the code audit looks for it (card C7); a `sealed` class for a closed set of states is another thing.

## 2. Async

The call chain is `async` from the I/O up (code principles 4.6), every `Future` awaited: the gate refuses one left unawaited.
Heavy work goes to an `Isolate`. A wait is on what signals it, a `Stream` or a `Future` (code principles 4.7), never a
`Future.delayed` in a loop.

## 3. Errors

An outcome the caller handles is a `sealed` result or a domain exception carrying a code from an enum (code principles 3.4); the
boundary maps each code once. An `on` clause names the type it handles.

## 4. Logging

The `logging` package, configured once by the entry point: a constant message, the values in the record's `object` (code principles
4.9).

## 5. Project and build

- **pub**: `pubspec.yaml` declares the dependencies, `pubspec.lock` is committed, for a package too (principles 6.2); `environment` gives
  the minimum SDK (principles 6.3).
- Every dependency's license is admitted by principles 6.4.
- `${CLAUDE_PLUGIN_ROOT}/lint-rules/dart/native/analysis_options.yaml` goes beside `pubspec.yaml`: it includes no
  lint set — it lists its lints one by one, each an error because it finds a defect — so it needs no dev dependency, in a
  Flutter project too.
- The gate is the manifest's `native_lint`: `dart analyze`. It checks no formatting and no style: they find no defect, and on code that exists they only make it be rewritten. ast-grep
  has no Dart grammar: the analyzer is the gate.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `dart pub outdated --no-dev-dependencies`, and the advisories
  `dart pub get` prints.
- The version is `version:` in `pubspec.yaml`, logged at startup (operations 2).

## 6. Serialization

`json_serializable` with the declared names: no `fieldRename`, no `@JsonKey(name:)`; an `enum` as its name, its default. Data that comes
from outside is parsed once, at the boundary, with `disallowUnrecognizedKeys`.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: `jsonDecode` gives a `Map<String, dynamic>`, which goes straight into the generated `fromJson`
  (a required field missing fails there) and no further; `toJson` writes — not `map['x'] as String`,
  a `TypeError` at run time, nor a map passed on;
- the local settings and storage: one typed wrapper — not values read by key where they are used.

## 7. What /dev:j-setup and /dev:j-new-project read in a Dart project

- **Recognized by**: `pubspec.yaml`.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Dart project |
  | `testing.md` | every Dart project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`/dev:j-new-project`): what is built, and what it talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `pubspec.yaml`; §5 says what the pack's file needs.
- **A command-line tool**: the lines of `avoid_print` — its comment, its entry under `errors:` and its entry under
  `rules:` — are taken out of the project's copy of `analysis_options.yaml`.
- **Vendored** (`@vendored-globs`): `.dart_tool/`, `build/`, `*.g.dart`, `*.freezed.dart`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `dart run`; a Flutter app, `flutter run`.
- **Where its errors show** (`/dev:j-debug`): the analyzer's output; the failed test's output; the log.
