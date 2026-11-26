# Java — Language

How the principles and the code principles are written in Java.

---

## 1. Language and conventions

- The current LTS; `camelCase` methods and fields, `PascalCase` types, `UPPER_SNAKE_CASE` constants.
- **A closed set is an `enum`** (code principles 3.3); a `switch` on it is an expression, exhaustive, with no
  `default`, so a new constant stops the build.
- **A state machine is a `sealed` interface whose records are the states**, or an `enum` with its transitions
  (code principles 2.1).
- **A value is a `record`** (code principles 3.1), its collections `List.copyOf`; a record with a rule of its
  own checks it in the compact constructor (code principles 2.4). A mutable collection is never handed out.
- **A contract is an `interface`**, shaped by its consumer; the implementation is package-private.
- **Private by default** (code principles 4.4): package-private classes, `public` only for what a consumer needs.
- **Constructor injection**: the fields `final`, the dependencies in the signature.
- No `System.out`, no `System.err`: the gate refuses each — a command-line tool's own output aside (§7).
- `Optional` as a return value, never as a field or a parameter.
- A warning is silenced with `@SuppressWarnings` on the smallest scope, with a comment saying why.
- **A class stays open** (code principles 1.9): no `final` on a class — the pack's rule
  `no-final-class` refuses it. Closed on the owner's yes only: the reason in a comment above the
  class, then `// ast-grep-ignore: no-final-class`. A `sealed` interface for a closed set of states is
  another thing.

## 2. Async

- Blocking work runs on virtual threads; concurrent work is a `StructuredTaskScope` or a chain of
  `CompletableFuture` (`thenCompose`, `thenApply`), which is never blocked on with `.get()`: the gate refuses it.
- A deadline is a timeout on the operation; a wait is on what signals it (code principles 4.7), never
  `Thread.sleep` in a loop.

## 3. Errors

An outcome the caller handles is a domain exception carrying a code from an enum (code principles 3.4); the
boundary maps each code once. A `catch` names the exception it handles, never `Exception`, and keeps the cause.

## 4. Logging

SLF4J only: a constant message with `{}` placeholders, the values as its arguments (code principles 4.9). The
backend's configuration is not touched from the code.

## 5. Project and build

- **Maven, through its wrapper**: `./mvnw` is committed, so every machine has a Maven that SpotBugs' plugin accepts (3.8.9 or newer). A multi-module build declares every version once, in the parent's `dependencyManagement` or a BOM;
  the modules declare none (principles 6.2). A Gradle project takes the same tools with its own plugins.
- Every dependency's license is admitted by principles 6.4.
- The pack's files (`${CLAUDE_PLUGIN_ROOT}/lint-rules/java/native/`): `checkstyle.xml`, `spotbugs-exclude.xml` beside the root
  `pom.xml`; `.mvn/jvm.config` in that folder; `pom-plugins.xml` is not a file of the project: its plugins are
  merged into `<build><plugins>`, and `error-prone.version` into `<properties>`.
- The gate is the manifest's `native_lint`: `./mvnw -q -DskipTests verify`: in the compiler, the lint
  categories that find a defect at error (`-Werror`) and Error Prone's bug patterns; on `verify`, three
  Checkstyle checks and SpotBugs' bug categories. Each is there because it finds a defect — an
  unchecked cast, an error swallowed, an equals without hashCode, a null dereferenced; no check of
  style, of imports or of naming, which find none and on code that exists only make it be rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `./mvnw org.owasp:dependency-check-maven:check`.
- The version is `<version>` in the `pom.xml`; the program reads it from its build information and logs it at
  startup (operations 2).

## 6. Serialization

Jackson with the declared names: no `@JsonProperty` that renames, no naming strategy; an `enum` as its name, which
is Jackson's default, and by its name in the storage. Data that comes from outside is
deserialized once, at the boundary, and refuses unknown properties.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: Jackson's `readValue`/`writeValue` on records whose constructor validates — not `readTree`
  walked with `get` or `path` (`path("count").asInt()` is `0` when the field is missing, in silence;
  `get("x").asText()` throws on a missing one), nor an `ObjectNode` built by hand;
- XML: Jackson XML or JAXB on classes — not DOM, SAX or XPath walked by name;
- YAML and CSV: Jackson's YAML and CSV (with its schema) on records — not a node tree, not `split` and
  indexes;
- the configuration: one typed record read and validated at start — not `System.getProperty`,
  `System.getenv` or `Properties.getProperty` in the code;
- a request: the framework's binding of the request on records — not parameters and headers read by
  name;
- the database: rows mapped onto records in one place (the ORM, or one `RowMapper` per record) — not
  `rs.getString("column")` where the data is used;
- performance, only on the user's request: Jackson's streaming `JsonParser` by hand, in one reader.

## 7. What /dev:j-setup and /dev:j-new-project read in a Java project

- **Recognized by**: `pom.xml`; its `<dependencies>` say the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Java project |
  | `testing.md` | every Java project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`/dev:j-new-project`): what is built — a library, a command-line tool, a service — and what it
  talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of the root `pom.xml`; §5 says where the
  pack's files go.
- **A command-line tool**: `@lint-astgrep` carries `--off=no-system-out-println` —
  `ast-grep scan --globs '!externals/**' --off=no-system-out-println`.
- **Closed classes allowed** (`@closed-classes`): `@lint-astgrep` carries `--off=no-final-class`.
- **Vendored** (`@vendored-globs`): `target/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `java -jar target/<artifact>.jar`.
- **Where its errors show** (`/dev:j-debug`): the build's output; the failed test's output; the log.
