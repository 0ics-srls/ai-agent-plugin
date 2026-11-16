# PHP — Language

How the principles and the code principles are written in PHP.

---

## 1. Language and conventions

- The current supported PHP 8; `declare(strict_types=1);` first in every file.
- **Everything is typed**: parameters, returns, properties; an array's shape in its PHPDoc. PHPStan runs at `max`, with the
  strict rules that find a defect.
- **A closed set is a backed `enum` whose values are its names** (`case Active = 'Active';`), so the value that leaves the
  program is the declared name (code principles 3.3, 3.5); a `match` on it has no `default`.
- **A state machine is an `enum` with its transitions as methods**, or a class per state behind one interface (code
  principles 2.1).
- **A value is a `final readonly class`** (code principles 3.1), never an associative array; one with a rule of its own checks
  it in the constructor (code principles 2.4).
- **A contract is an `interface`**, shaped by its consumer.
- **`final` and `private` by default** (code principles 4.4): composition, not inheritance.
- **Constructor injection**: `app()` and `resolve()` in business code hide a dependency from the signature.
- No `var_dump`, `dd`, `dump`, `print_r`, `ray`: the gate refuses each.
- A PHPStan finding is silenced with its ignore comment, on the line, naming the identifier and saying why.

## 2. Async

PHP runs one request at a time: a slow task goes to a queued job. A job is idempotent, and a wait is on what signals it (code
principles 4.7), never `sleep` in a loop.

## 3. Errors

An outcome the caller handles is a domain exception carrying a code from an enum (code principles 3.4); the boundary maps each
code once. A `catch` names the exception it handles, and a re-throw keeps the previous one.

## 4. Logging

Monolog, through the PSR-3 `LoggerInterface`: a constant message, the values in the context array (code
principles 4.9).

## 5. Project and build

- **Composer**: `composer.json` declares the dependencies, `composer.lock` is committed, for a library too (principles 6.2).
  The tools are `require-dev`: `phpstan/phpstan`, `phpstan/phpstan-strict-rules`, `phpunit/phpunit`.
- Every dependency's license is admitted by principles 6.4.
- The pack's files beside `composer.json` (`${CLAUDE_PLUGIN_ROOT}/lint-rules/php/native/`): `phpstan.neon` (its `paths`
  are the project's own), `phpunit.xml` (`testing.md`).
- The gate is the manifest's `native_lint`: `vendor/bin/phpstan analyse`. It checks no formatting and no style: they
  find no defect, and on code that exists they only make it be rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `composer audit`.
- The version comes from the configuration, logged at startup (operations 2).

## 6. Serialization

`json_encode` on the declared names, with `JSON_THROW_ON_ERROR`: no key that renames; a backed `enum` as its value, which is its
name (§1). Data that comes from outside is validated once, at the boundary, and read into its typed class.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: `json_decode` with `JSON_THROW_ON_ERROR` gives an array, read in one reader into the readonly
  class through its constructor — not `$data['x']` elsewhere, a warning and a `null`;
- XML: SimpleXML or DOM read in one reader into the class;
- a request: one typed object built from it — not `$_GET['x']`, `$_POST['x']` or the headers where they
  are used;
- the configuration: one typed object read at start — not `getenv` in the code;
- the database: rows fetched into classes in one place — not `$row['column']` where the data is used.

## 7. What j-setup and j-new-project read in a PHP project

- **Recognized by**: `composer.json`; its `require` says the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every PHP project |
  | `testing.md` | every PHP project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`j-new-project`): what is built, and what it talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `composer.json`; §5 says where the pack's files go.
- **Vendored** (`@vendored-globs`): `vendor/`, `.phpunit.cache/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: the project's script in `bin/`.
- **Where its errors show** (`j-debug`): PHPStan's output; the failed test's output; the log.
