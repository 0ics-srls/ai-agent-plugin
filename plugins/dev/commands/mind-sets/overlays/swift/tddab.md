# Swift — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Swift. How a test is
written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Swift project; a plan copies them
into its blocks (`tddab-planner.md`, "The commands, by level").

| Key | Swift |
|---|---|
| `@test-focused-<component>` | `swift test --filter '{Suite}/{test}'` |
| `@test-block-<component>` | `swift test --filter '{Suite}'`, once for each suite the block touches |
| `@test-fast` | `swift test --skip IntegrationTests` |
| `@test-slow` | `swift test` |
| `@test-e2e` | an app's UI tests: `xcodebuild test -scheme {App} -destination '{destination}'`, the command starting the backend first; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `swift test`, an app's `xcodebuild` build and UI tests, the audit (`language.md` §5) |

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic on doubles; the client and the data
on the real thing; a screen with XCUITest (`testing.md` §2).

## 3. The RED of a block

The block's suite, importing the module and calling the type the block will build: without it the
build stops; then, with a wrong behaviour, the failing `#expect` names it.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Swift block

- Values `struct`s, contracts `protocol`s, errors thrown typed (`language.md` §1, §3).
- A new target names its dependencies and the warnings-as-errors setting; a new dependency goes to
  `Package.swift` with its exact version.
- The state of a contract on a fake; a call across the boundary on a spy (`testing.md` §3).
- No console write: the logger (`language.md` §4).

## 6. The skeleton's blocks

A library or a command-line tool:

| Block | Swift |
|---|---|
| 1 | the package: `Package.swift` with its targets; Core — the contracts, the first entity, the errors. RED: the first suite builds under the gate and runs |
| 2 | the code that talks to the outside, for the first entity. RED: on the real thing |
| 3 | the logic of the first entity on the contracts; `TestSupport` with its fakes. RED: on the doubles |
| 4 | a tool: the command, its arguments validated, its output; the composition root. RED: the command run without its arguments says what is missing |

An app, as the frontend blocks of `j-new-project`:

| Block | Swift |
|---|---|
| F1 | the app target and the package, the gate, the first test |
| F2 | the generated client (`app.md` §1) |
| F3 | the calls as results: each answer the entity or the domain's error |
| F4 | the first entity's screen: its view model and its view (`app.md` §2-3) |
| F5 | end to end: the UI test of the screen against the real backend |
