# Go — Tests

How `testing-principles.md` is written with `go test`.

---

## 1. The runner

- `go test -race`. **The default run is the fast one** (testing principles 6.2): `go test -race ./...`; a test that needs
  something real carries `//go:build integration`, and the full run is `go test -race -tags=integration ./...`.
- A package with no test passes: a block proves its test ran by its name in the output, with `-v`.
- `go test` stops a test that hangs at its `-timeout` and prints where it was (testing principles 7.3).
- Several inputs of one behaviour are one table with `t.Run` for each row (testing principles 1.4); tests call `t.Parallel()`
  (testing principles 7.1); a helper calls `t.Helper()`.
- The assertions are testify's: `require` when the rest of the test depends on it, `assert` otherwise.
- A test's name says the behaviour: `Test<Method>_<Scenario>`, its rows named in words.

## 2. The levels

- Unit: `<file>_test.go` next to the file, the logic on doubles of the contracts, in memory.
- Integration: with the build tag, the code that talks to the outside on the real thing (testing principles 7.2): a real
  database through testcontainers-go, started once in `TestMain`; each test owns its data.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour, in `internal/testsupport`.
- **A call across the boundary that is itself the behaviour** is a `testify/mock` of the contract, and the test asserts the call.
- Plain data and pure functions are used as they are.
