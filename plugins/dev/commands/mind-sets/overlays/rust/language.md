# Rust — Language

How the principles and the code principles are written in Rust.

---

## 1. Language and conventions

- Edition 2024; `snake_case` functions and modules, `PascalCase` types.
- **A closed set is an `enum`** (code principles 3.3); a `match` on it names every variant, so a new one
  stops the build where it matters.
- **A state machine is an `enum` whose variants carry the data of that state**, and a transition takes
  `self` and returns the next state (code principles 2.1): an illegal state cannot be written.
- **A value with a rule of its own is a newtype**, its field private, built only by a constructor that
  returns a `Result` (code principles 2.4); data from outside is parsed into it at the boundary.
- **A contract is a `trait`**, shaped by its consumer. A service is generic over it; a trait object
  (`dyn`) where the implementation is chosen at run time. An async method is native, with `+ Send` on its
  future; `async_trait` only for a trait object.
- **Values are immutable** (code principles 3.1): no `mut` binding without a reason, no setters, no
  `&mut` to an inner collection handed out.
- **Borrow by default**: a parameter that is only read is `&str` or `&[T]`; a constructor that keeps it
  takes `impl Into<String>`. A `clone` answers a need of ownership, never a complaint of the borrow checker
  not yet understood.
- **Private by default** (code principles 4.4): `pub(crate)` inside a crate; what `lib.rs` re-exports is the
  crate's public surface.
- No `unwrap`, `expect`, `println!`, `eprintln!`, `dbg!`, `todo!`, `unimplemented!` outside the tests:
  Clippy refuses each. A command-line tool writes its output with `writeln!` on the handle of stdout.
- **`unsafe` is forbidden by the pack.** A project that needs it, for a foreign function, lifts it by the
  owner's decision, in the crate that needs it, with a `// SAFETY:` comment on each block.
- A lint is silenced as `#[expect(clippy::<lint>, reason = "...")]`, on the smallest scope: Clippy refuses
  one without its reason.

## 2. Async

- Where the program is asynchronous, the call chain is `async` from the I/O up to its entry point (code
  principles 4.6), on one tokio runtime started by `main`.
- Blocking work never runs on the runtime: tokio's own I/O, and `spawn_blocking` for what has no async form.
- Concurrent work is `tokio::join!` or a `JoinSet`; a deadline is `tokio::time::timeout`; a wait is an
  `.await` on what signals it (code principles 4.7), never a sleep in a loop.

## 3. Errors

An outcome the caller handles is a `Result` with a domain error: an `enum` deriving `thiserror::Error`,
each variant a code with its context (code principles 3.4); the boundary maps each variant once. `?`
propagates it. `anyhow`, with its `.context(...)`, only in an entry point, where nobody matches on the error.
An error is never dropped with `let _ =` or `.ok()` unless the comment says why it does not matter.

## 4. Logging

`tracing`, configured once by the entry point with its `EnvFilter`: a constant message, the values as named
fields (`info!(user_id, "user retrieved")`); `#[instrument]` on the operations worth a span, skipping what is
private or heavy.

## 5. Project and build

- **Cargo.** `cargo add` adds a dependency; `Cargo.lock` is committed, for a library too (principles 6.2). A
  workspace declares every version in `[workspace.dependencies]`, and its crates inherit them. `rust-version` gives the minimum
  toolchain (principles 6.3).
- Every dependency's license is admitted by principles 6.4.
- The pack's files at the folder of the root `Cargo.toml` (`${CLAUDE_PLUGIN_ROOT}/lint-rules/rust/native/`): `clippy.toml`.
  `Cargo.lints.toml` is not a file of the project: its tables are merged into `Cargo.toml`,
  as `[lints.*]` in a single package, as `[workspace.lints.*]` in a workspace with `[lints] workspace = true`
  in each crate.
- The gate is the manifest's `native_lint`: `cargo clippy --workspace --all-targets -- -D warnings`. The
  lints that find a defect are errors — Clippy's correctness and suspicious groups, and the ones the
  pack lists one by one; its style, complexity, pedantic and nursery groups are off, and the gate checks
  no formatting: they find no defect, and on code that exists they only make it be rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: `cargo audit`.
- The version is `[package] version`; the program reads it with `env!("CARGO_PKG_VERSION")` and logs it at
  startup (operations 2).

## 6. Serialization

`serde` with the declared names: no `rename`, no `rename_all`. A unit variant of an `enum` as its name, which
is serde's default. Data that comes from outside is parsed once, at the boundary, with
`deny_unknown_fields`.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- every format serde reads — JSON, TOML, YAML, CSV (`csv` with `deserialize`), XML (quick-xml with
  serde): `from_str::<T>` on `Deserialize` types, `to_string` from `Serialize` ones — not a
  `serde_json::Value` indexed by key (`v["x"]` never fails: a missing key is `Null`, `as_str()` is
  `None`), not a CSV `StringRecord` read by index, not an XML event loop by hand;
- the configuration: one `Deserialize` struct read and validated at start — not `std::env::var` in
  the code;
- a request with axum: the extractors `Json<T>`, `Query<T>`, `Path<T>` and the typed headers — not the
  `HeaderMap` or the query string read by key;
- the database: sqlx's `query_as!` and `FromRow` — not `row.get("column")`;
- performance, only on the user's request: a borrowed `Value` or a streaming reader by hand, in one
  reader.

## 7. What j-setup and j-new-project read in a Rust project

- **Recognized by**: `Cargo.toml`; its `[dependencies]` say the frameworks and the branches.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Rust project |
  | `testing.md` | every Rust project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `service.md` | `branches/service-layers.md`, `branches/api.md`, `branches/data.md`, `branches/resilience.md`, `branches/operations.md`, `branches/security.md`: a service |

- **What LISTEN asks** (`j-new-project`): what is built — a library, a command-line tool, a service — and what
  it talks to.
- **The lint gate**: the manifest's `native_lint`, run from the folder of the root `Cargo.toml`; §5 says where
  the pack's files go.
- **Vendored** (`@vendored-globs`): `target/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `cargo run -p <the binary's package>`.
- **Where its errors show** (`j-debug`): the compiler's and Clippy's output; a panic's backtrace with
  `RUST_BACKTRACE=1`; the log, its level set by `RUST_LOG`.
- **Code navigation**: what a `derive` or a procedural macro generates may be missing from the index: confirm it
  in the source or with `cargo expand` before calling it absent (`code-navigation.md`).
