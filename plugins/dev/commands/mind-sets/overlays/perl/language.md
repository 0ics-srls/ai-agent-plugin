# Perl — Language

How the principles and the code principles are written in modern Perl.

---

## 1. Language and conventions

- `use v5.36;` first in every file, tests too: strict, warnings, `say`, signatures; `use autodie;` for I/O, `use utf8;` for the source.
- `snake_case` subroutines, `PascalCase` packages; a module named by its responsibility, never a `Util` dumping ground; `@EXPORT_OK`,
  never `@EXPORT`.
- **Every class is Moo with `Types::Standard`**: each attribute typed.
- **A closed set is a `Type::Tiny` `Enum` whose values are its names** (code principles 3.3, 3.5).
- **A value is `is => 'ro'`** (code principles 3.1), its constraints checked at construction (code principles 2.4); a change is a new object.
- **A state machine is a class holding its state and its transitions**, refusing the illegal ones (code principles 2.1).
- **A contract is a `Moo::Role` with `requires`**; a service takes `ConsumerOf[...]`.
- **Private by default** (code principles 4.4): `_` on a private method or attribute, `init_arg => undef` for an internal one.
- **Constructor injection**: a bootstrap function is the composition root, with no global registry.
- Three-argument `open`, or `Path::Tiny`. A process runs in list form, never through a shell string.
- No `print` or `warn` for debugging, no `Data::Dumper` left behind. A web script runs under taint mode.
- A Perl::Critic finding is silenced with `## no critic (<Policy>) -- <why>`, on the line.

## 2. Concurrency

One declared strategy per program: `Mojo::IOLoop`, MCE or `Parallel::ForkManager`, never a hand-rolled `fork`. A wait is on what signals it
(code principles 4.7), never a `sleep` in a loop.

## 3. Errors

An outcome the caller handles is an error object of a Moo class, thrown with `die`, carrying a code from a closed set (code principles 3.4);
caught with `try`/`catch` from `Feature::Compat::Try`. The boundary maps each code once. A library never dies with a bare string.

## 4. Logging

`Log::Any`: a library uses `$log`, the entry point configures the adapter once. A constant message, the values in its context hash (code
principles 4.9).

## 5. Project and build

- **Carton**: `cpanfile` declares the dependencies, `cpanfile.snapshot` is committed (principles 6.2); everything runs under `carton exec`.
- Every dependency's license is admitted by principles 6.4.
- The pack's files beside `cpanfile` (`${CLAUDE_PLUGIN_ROOT}/lint-rules/perl/native/`): `.perlcriticrc`.
- The gate is the manifest's `native_lint`: Perl::Critic on `lib` and `t`, with its most severe policies and the ones the pack raises because they find a defect — a system call nobody checks, an eval nobody reads. It checks no formatting and no style: they find no defect, and on code that exists they only make it be rewritten. ast-grep has no
  Perl grammar: these two are the gate.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `carton exec cpan-audit deps .`.
- The version is `our $VERSION` in the main module, logged at startup (operations 2).

## 6. Serialization

`Cpanel::JSON::XS` on the declared names: no key that renames; a value of a closed set as its name. Data that comes from outside is decoded once,
at the boundary, and read into its typed class, which refuses an unknown key.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: the decoded hash goes into the Moo class (`isa`, `required`) in one reader — not
  `$data->{x}` elsewhere, where a mistyped key is `undef` and autovivification creates keys in silence;
- the database and the configuration: rows and settings read into classes in one place — not
  `$row->{column}` or `$ENV{X}` where they are used.

## 7. What /dev:j-setup and /dev:j-new-project read in a Perl project

- **Recognized by**: `cpanfile`; its `requires` say the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Perl project |
  | `testing.md` | every Perl project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`/dev:j-new-project`): what is built — a library, a command-line tool, a service — and what it talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `cpanfile`; the pack's files go to that folder.
- **Vendored** (`@vendored-globs`): `local/`, `cover_db/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `carton exec perl script/<the program>`.
- **Where its errors show** (`/dev:j-debug`): Perl::Critic's output; `perl -c` on the file; the failed test's output with `prove -lv`; the log.
