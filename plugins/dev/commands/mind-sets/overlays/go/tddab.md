# Go — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Go. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Go project; a plan copies them into its blocks
(`tddab-planner.md`, "The commands, by level").

| Key | Go |
|---|---|
| `@test-focused-<component>` | `go test -race -tags=integration -v -run '^{test}$' {package}` |
| `@test-block-<component>` | `go test -race -tags=integration -v {package}`, once for each package the block touches |
| `@test-fast` | `go test -race ./...` |
| `@test-slow` | `go test -race -tags=integration ./...` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `go test -run '^$' -bench . ./...`, when the project has benchmarks; otherwise `none` |
| `@gate-final` | the lint gate, `go test -race -tags=integration ./...`, the audit (`language.md` §5) |

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `<file>_test.go` on the doubles; the code that talks to
the outside in a test with the build tag, on the real thing (`testing.md` §2).

## 3. The RED of a block

The test calls the function the block will build as its contract says, with the function declared and its body returning a
wrong value: it compiles, runs and fails on the behaviour it names. Both paths of an error are proved.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Go block

- A closed set a defined type with its constants (`language.md` §1).
- A contract is an `interface` at its consumer; the constructor accepts it.
- The state of a contract on the fakes; a call across the boundary on `testify/mock` (`testing.md` §3).
- Every error handled and wrapped (`language.md` §3).
- No console write: `slog` (`language.md` §4).

## 6. The skeleton's blocks

The form in Go of each block of the skeleton `/dev:j-new-project` plans; the frameworks are the project's, chosen in LISTEN.

| Block | Go |
|---|---|
| 1 | `go mod init`; the pack's files as `language.md` §5 says; the contracts and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the code that talks to the outside, for the first entity, written once; its tests on the real thing |
| 3 | the logic of the first entity on the contracts; the fakes and the tests on them |
| 4 | the transport the project has, on the logic: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup |
