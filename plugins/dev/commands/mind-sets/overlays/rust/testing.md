# Rust — Tests

How `testing-principles.md` is written with `cargo test`.

---

## 1. The runner

- `cargo test`. **The default run is the fast one** (testing principles 6.2): a test that needs something real is behind the
  crate's `integration` feature, so `cargo test --workspace` leaves it out; the full run is `cargo test --workspace --all-features`.
  The logic lives in a library, `main.rs` only starts it, so a command-line tool is tested the same way.
- A run that finds no test is green for cargo: a block proves its test ran by its name in the output.
- Asynchronous tests are `#[tokio::test]`. libtest has no time limit: a test that can hang awaits inside
  `tokio::time::timeout`, so it fails with its name (testing principles 7.3).
- Several inputs of one behaviour are one `rstest` with its `#[case]`s (testing principles 1.4).
- A test's name says the behaviour: `<method>_<scenario>_<expected>`. Both paths of a `Result` are proved.

## 2. The levels

- Unit: a `#[cfg(test)] mod tests` in the file of the module, the logic on doubles of the contracts, in memory.
- Integration: the crate's `tests/` folder, `#![cfg(feature = "integration")]`, through its public surface, the code that talks to the outside on
  the real thing (testing principles 7.2): a real database through the `testcontainers` crate, started once for
  the run; each test owns its data.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour, in a `test-support` crate that
  the other crates take as a dev-dependency: `#[cfg(test)]` code is not visible across crates.
- **A call across the boundary that is itself the behaviour** is a mock of the contract: `mockall`'s `automock`,
  and the test states the call it expects.
- Plain data and pure functions are used as they are.
