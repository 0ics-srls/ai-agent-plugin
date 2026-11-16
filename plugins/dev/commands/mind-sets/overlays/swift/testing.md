# Swift — Tests

How `testing-principles.md` is written in Swift: Swift Testing (`import Testing`), the doubles written
by hand.

---

## 1. The runner

- `@Test` functions grouped in a `struct` suite; `#expect` checks, `#require` stops the test.
- `swift test` runs the package's tests; an app's UI tests run with `xcodebuild test`.
- The levels are separate test targets: `<Target>Tests` for the unit level, `<Target>IntegrationTests`
  for the integration level, so the fast run skips the slow one (testing principles 6.2).

## 2. The levels

- **Unit** — the logic on doubles of the contracts, in memory.
- **The code that talks to the outside** — on the real thing (testing principles 7.2): the generated
  client through a transport that answers as the backend does; SwiftData on a store in memory, or on a
  file when the test reads what was stored.
- **The screens** — XCUITest (`app.md` §5).
- A test's name says the behaviour.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake, an `actor` in a `TestSupport` target, with the real
  behaviour.
- **A call across the boundary that is itself the behaviour** is a spy written by hand: an `actor` that
  records the calls; the test checks them with `#expect`. No mocking library.
- Plain data and pure functions are used as they are.
