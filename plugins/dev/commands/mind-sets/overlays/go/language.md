# Go — Language

How the principles and the code principles are written in Go.

---

## 1. Language and conventions

- The current stable release. Short lowercase package names, named by their responsibility,
  never `utils`.
- **A closed set is a defined `string` type whose constants hold their own names** (`const StatusActive Status =
  "StatusActive"`), so the value that leaves the program is the declared name (code principles 3.3, 3.5); the `exhaustive`
  linter refuses a `switch` that misses one.
- **A state machine is a type with its transitions as methods**, returning the next state or an error (code principles
  2.1).
- **A value with a rule of its own is a defined type built by a constructor** that returns it or an error (code
  principles 2.4).
- **A contract is a small `interface`, defined where it is used**; a constructor accepts interfaces and returns structs.
- **Values are passed by value**, a slice or a map copied when it leaves the owner (code principles 3.1).
- **Private by default** (code principles 4.4): `internal/` for the application, unexported until a consumer needs it.
- **Constructor injection, no framework**: `main` is the composition root.
- No `fmt.Print*`, no `panic` for what can be returned, no ignored error, `_ = err` included: the gate refuses each.
- A linter is silenced with `//nolint:<linter> // <why>` on the line: `nolintlint` refuses one without its reason.

## 2. Concurrency

- `context.Context` is the first parameter of what does I/O, and it flows through every call (code principles 4.6).
- Concurrent work is an `errgroup`; a goroutine has a known end. The sender closes a channel, and a `select` also waits on
  `ctx.Done()`.
- A wait is on what signals it (code principles 4.7), never `time.Sleep` in a loop. An `http.Client` has its `Timeout`:
  `http.Get` and `http.DefaultClient` have none, and the gate refuses them.

## 3. Errors

An outcome the caller handles is a typed error carrying a code (code principles 3.4), or a sentinel; `errors.Is` and
`errors.As` read it, and the boundary maps each code once. An error passed on is wrapped with what failed:
`fmt.Errorf("find user %d: %w", id, err)`.

## 4. Logging

`log/slog`, configured once by `main`: a constant message, the values as attributes (code principles 4.9).

## 5. Project and build

- **Go modules**: `go.mod` and `go.sum` committed, `go mod tidy` before a commit (principles 6.2); its `go` line is the minimum
  version (principles 6.3).
- Every dependency's license is admitted by principles 6.4.
- `${CLAUDE_PLUGIN_ROOT}/lint-rules/go/native/.golangci.yml` goes beside `go.mod`.
- The gate is the manifest's `native_lint`: `golangci-lint run ./...`, with the linters the pack lists one by
  one — each because it finds a defect: an error nobody checks, a resource nobody closes, the context
  misused, a security hole. The linters of style, naming, whitespace and counts are off, and the gate
  checks no formatting: they find no defect, and on code that exists they only make it be rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `govulncheck ./...`.
- The version is set at build time with `-ldflags "-X main.version=..."`, and logged at startup (operations 2).
- Output in `bin/`, built with `-trimpath` (principles 6.3).

## 6. Serialization

`encoding/json` with the declared names: no tag that renames, a `json` tag only for `omitempty`. Data that comes from outside
is decoded once, at the boundary, with `DisallowUnknownFields`.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON and XML: `encoding/json` and `encoding/xml` into structs, and from them. Decoding fills a
  missing field with its zero value, in silence: a required field is a pointer, or checked right after
  the decoding, in the reader — not a `map[string]any` with type assertions (a number is a `float64`,
  a wrong assertion panics), nor an XML token loop by hand;
- CSV: `encoding/csv` gives `[]string`: one reader maps each record into its struct by the header's
  names, and checks it — not indexes where the record is used;
- the configuration: one struct filled and validated at start — not `os.Getenv` in the code;
- a request: the body decoded into its struct, the query and the headers read by one function into a
  typed value — not `r.URL.Query().Get("x")` or `r.Header.Get("x")` where they are used;
- the database: rows scanned into structs in one place per type (generated, or one `scan` function) —
  not `rows.Scan` by position where the data is used;
- performance, only on the user's request: a streaming `json.Decoder` walked by tokens, in one reader.

## 7. What j-setup and j-new-project read in a Go project

- **Recognized by**: `go.mod`; its `require` says the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Go project |
  | `testing.md` | every Go project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |

- **What LISTEN asks** (`j-new-project`): what is built — a library, a command-line tool, a service — and what it talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `go.mod`; the pack's `.golangci.yml` goes to that folder.
- **Vendored** (`@vendored-globs`): `vendor/`, `bin/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `go run ./cmd/<the binary>`.
- **Where its errors show** (`j-debug`): the compiler's and the linters' output; the race detector's report; a panic's
  goroutine trace; the log.
- **Code navigation**: what `go:generate` produces exists only after `go generate`: run it before calling a symbol absent
  (`code-navigation.md`).
