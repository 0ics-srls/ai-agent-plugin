# Rust — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Rust. How a test is written is
`testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Rust project; a plan copies them into its
blocks (`tddab-planner.md`, "The commands, by level").

| Key | Rust |
|---|---|
| `@test-focused-<component>` | `cargo test -p {crate} --all-features {test}` — the tests whose path contains the name |
| `@test-block-<component>` | `cargo test -p {crate} --all-features` |
| `@test-fast` | `cargo test --workspace` |
| `@test-slow` | `cargo test --workspace --all-features` — unit, integration and documentation tests |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `cargo bench`, when the project has a `benches/` folder; otherwise `none` |
| `@gate-final` | the lint gate, `cargo test --workspace --all-features`, the audit (`language.md` §5) |

`cargo test` stops at the first test binary that fails — `--no-fail-fast` is never passed
(`testing-principles.md` 6.3). Inside one binary the harness runs its tests to the end: that is as
far as it stops.

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in the module's `#[cfg(test)] mod tests` on the
doubles; the code that talks to the outside in the crate's `tests/` on the real thing (`testing.md` §2).

## 3. The RED of a block

The test calls the type the block will build as its contract says, with the type and the method declared and
their bodies not yet written: it compiles, runs and fails on the behaviour it names. A body not yet written returns
a wrong value of its type: `todo!` is refused by the gate.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Rust block

- A closed set an `enum`; a value with a rule a newtype (`language.md` §1).
- A contract is a `trait`; the service generic over it.
- The state of a contract on the fakes; a call across the boundary on `mockall` (`testing.md` §3).
- A `Result` proved on both paths; in a test `unwrap` and `expect` are allowed.
- No console write: `tracing` (`language.md` §4).

## 6. The skeleton's blocks

The form in Rust of each block of the skeleton `/dev:j-new-project` plans. A library or a command-line tool is one
package, and stops at the blocks it has; a service is the workspace of `service.md` §1.

| Block | Rust |
|---|---|
| 1 | `cargo init` or the workspace; the pack's files as /dev:j-setup placed them; the contracts (`trait`s) and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the storage, when there is one: the first entity, the implementation of its contract written once, its tests in `tests/` on the real store (`service.md` §3) |
| 3 | the logic of the first entity on the contracts; the `test-support` crate and the tests on its fakes |
| 4 | the transport: a tool's command and its arguments, or a service's routes (`service.md` §2); validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup (`service.md` §4) |
