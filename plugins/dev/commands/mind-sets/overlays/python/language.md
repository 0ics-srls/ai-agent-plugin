# Python — Language

How the principles and the code principles are written in Python.

---

## 1. Language and conventions

- PEP 8's names: modules, functions, variables `snake_case`; classes `PascalCase`; constants
  `UPPER_CASE`; a private member or module starts with `_`.
- **Every function is typed** — parameters and return, `-> None` included; collections are typed;
  generics use the current syntax (`class Page[T]`). mypy runs strict.
- The type checker is not silenced (code principles 3.3): no `typing.cast` — ruff's banned API refuses
  it outside the tests — and a `# type: ignore` names its code (mypy) and is the owner's decision; a
  value is narrowed with a check (`isinstance`, `is None`), validated into its type, or the program
  raises where its absence is known.
- **A closed set is a `StrEnum` whose values are its names** (`ACTIVE = "ACTIVE"`), so the value that
  leaves the program is the declared name (code principles 3.3, 3.5).
- **A contract is a `Protocol`**: the implementation does not inherit from it; the type checker checks
  it where it is passed. A behaviour shared by several types is written once, as a generic.
- **Values are frozen** (code principles 3.1): `@dataclass(frozen=True, slots=True)`, their collections
  tuples.
- No `print`, no `breakpoint()`, no `eval`/`exec`, no `pickle` or unsafe `yaml.load` on what comes from
  outside: ruff refuses each — `print` aside, in a command-line tool (§7).

## 2. Async

- Where the program is asynchronous, the call chain is `async` from the I/O up to its entry point (code
  principles 4.6); a blocking call inside an `async` function is refused by ruff (`ASYNC`).
- Concurrent work is an `asyncio.TaskGroup`; a deadline is `asyncio.timeout(...)`; a wait is an `await`
  on what signals it (code principles 4.7) — never `time.sleep` or a polling loop.
- A resource with a lifetime is a context manager (`with` / `async with`).

## 3. Errors

An outcome the caller handles is a domain error carrying a code from an enum (code principles 3.4); the
boundary maps each code once. An `except` names the exception it handles; a re-raise keeps the cause
(`raise … from error`).

## 4. Logging

`logging` with a module logger (`logging.getLogger(__name__)`), configured once by the entry point. The
message is a constant; the values travel in `extra` (ruff `G004` refuses an f-string in a log call).

## 5. Project and build

- **uv** manages the interpreter, the dependencies and the lock: `pyproject.toml` declares them,
  `uv.lock` pins every version and is committed (principles 6.2); the development tools are the `dev`
  group. A package is added with `uv add`.
- The `src` layout.
- Every dependency's license is admitted by principles 6.4.
- The pack's files at the folder of `pyproject.toml` (`${CLAUDE_PLUGIN_ROOT}/lint-rules/python/native/`): `ruff.toml`
  — the rules that find a defect, family by family, each with what it finds; no style, naming or
  documentation rule; `mypy.ini` — strict;
  `pytest.ini` (`testing.md`).
- The gate is the manifest's `native_lint`: `uv run ruff check . && uv run mypy .`. It checks no
  formatting: a format finds no defect, and on code that exists it only makes it be rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `uv export --no-emit-project
  --format requirements.txt | uvx pip-audit -r /dev/stdin --disable-pip`.
- The version is `[project] version`; the program reads it with `importlib.metadata.version` and logs
  it at startup (operations 2).

## 6. Serialization

Data is serialized as it is: field names as declared, no alias; a `StrEnum` as its value, which is its
name (§1). Data that comes from outside is validated once, at the boundary, and refuses unknown fields.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON, TOML, YAML and CSV: `json.loads`, `tomllib`, `yaml.safe_load` and `csv.DictReader` give
  dictionaries and lists, which go straight into the validated model and no further — not
  `data["x"]` (a `KeyError` at run time) or `data.get("x")` (a `None` that breaks far away), nor a
  dictionary passed on;
- XML: `ElementTree` mapped into the model in one reader — not `find("x").text` where it is used,
  which fails on a `None` when the element is missing;
- the configuration: one settings model read and validated at start — not `os.environ["X"]` or
  `os.getenv` in the code;
- a request: the framework's typed models for the body, the query and the headers — not the raw
  request read by key;
- the database: rows mapped into the model in one place (the ORM, or one mapper per model) — not
  `row["column"]` or `row[2]` where the data is used.

## 7. What /dev:j-setup and /dev:j-new-project read in a Python project

- **Recognized by**: `pyproject.toml`; its `dependencies` say the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Python project |
  | `testing.md` | every Python project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`/dev:j-new-project`): what the program is — a library, a command-line tool, a
  service — and what it talks to.
- **What /dev:j-setup asks on an existing project**: the project already has tests — a `test_*.py` or a
  `*_test.py` file — or its own pytest configuration (`[tool.pytest.ini_options]` in `pyproject.toml`,
  a `pytest.ini`, a pytest section in `tox.ini` or `setup.cfg`) → ask with AskUserQuestion, once: keep
  the tests where they are and as they run, or adopt the layout of this overlay? It is the owner's
  decision, and keeping is a full answer. *Keep*: the pack's `pytest.ini` is not copied, no test is
  moved and no dependency is added; the test levels are the commands the project already runs, on its
  own folder — `@test-fast` and `@test-slow` name it, `uv run pytest -x <the folder of its tests>` —
  and `testing.md` §1 says where a new test goes. *Adopt*: nothing changes here — moving the tests
  into `tests/unit` and `tests/integration`, with `pytest-timeout`, `pytest-asyncio` and the pack's
  `pytest.ini`, is a work of its own, `/dev:j-new-feature`, and until it closes the project is set up as
  *Keep*.
- **The lint gate**: the manifest's `native_lint`; the pack's `ruff.toml` and `mypy.ini` go to the
  folder of `pyproject.toml`. `pytest.ini` goes there too in a project the set creates: it is the
  test runner's configuration — where the tests are, their time limit, the async mode — not a check,
  and it is kept out of an existing project (above).
- **A command-line tool**: its gate is `uv run ruff check --ignore T20 . && uv run mypy .` — `print` is
  its output; `T10`, the check on a `breakpoint()` left behind, stays.
- **Vendored** (`@vendored-globs`): `.venv/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `uv run <the entry point>`, as `[project.scripts]` declares it.
- **Where its errors show** (`/dev:j-debug`): the traceback in the terminal that started it; the log.
