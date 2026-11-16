# Swift — Language

How the principles and the code principles are written in Swift 6, for the Apple platforms: an app
(iOS, macOS) with SwiftUI, a library or a command-line tool with the Swift Package Manager. The app is
`app.md`.

---

## 1. Language and conventions

- Apple's API Design Guidelines: types `PascalCase`; functions, properties, enumeration cases
  `camelCase`; no prefixes, no underscores.
- **A value is a `struct` with `let` properties** (code principles 3.1); a `class` only for identity,
  `final`. Data that crosses a concurrency boundary is `Sendable`.
- **A closed set is an `enum`**; one that leaves the program has a `String` raw value equal to its
  declared name (code principles 3.3, 3.5).
- **A contract is a `protocol`** in Core, small, `Sendable`; the implementation conforms to it, the
  consumer holds `any Contract` (code principles 1.8).
- **A dependency is injected by the initializer**; the composition root builds them once.
- **No force unwrap, no `try!`, no implicitly unwrapped optional**: `guard let`, `if let`, `??`.
  The ast-grep rules `swift-no-force-unwrap`, `swift-no-force-try` and
  `swift-no-implicitly-unwrapped-optional` refuse them outside the tests.
- **Access is the smallest that works**: `private` by default, `public` only for a module's API.
- **The console is never written directly** — `print`, `debugPrint`, `dump`, `NSLog`: the pack's
  ast-grep rule `swift-no-console-output` refuses them; a command-line tool writes its output to
  `FileHandle.standardOutput`, everything else goes through the logger (§4).

## 2. Concurrency and waiting

- Swift 6 language mode: complete concurrency checking.
- Shared mutable state lives in an `actor`; the user interface on `@MainActor`.
- Concurrent work is structured: `async let`, a task group; a wait is an `await` on what signals it
  (code principles 4.7) — never `Task.sleep` in a loop, never a `DispatchQueue` for shared state.
- A long task checks its cancellation.

## 3. Errors

An outcome the caller handles is thrown typed — `throws(AppError)` — the error a code from a closed set
with its detail and the field involved (code principles 3.4); the boundary maps each answer to its code
once. An error is never swallowed: a `catch` handles it or passes it on.

## 4. Logging

`os.Logger`, one subsystem, a category per area. Every interpolated value carries its privacy
(`privacy: .public` for what is safe to read, `.private` for personal data).

## 5. Project and build

- **The Swift Package Manager**: `Package.swift` declares every dependency with its exact version and
  `Package.resolved` is committed (principles 6.2); every dependency's license is admitted by
  principles 6.4. Apple's frameworks before third-party ones.
- **One target per layer** — Core (the contracts, the entities, the errors), the data and the client,
  Domain, the features, the shell — and a test target per target: SwiftPM refuses an import a target
  does not declare, so the layers are enforced by the build.
- **Every warning is an error**: `.treatAllWarnings(as: .error)` in every target's `swiftSettings`; an
  app target sets `SWIFT_TREAT_WARNINGS_AS_ERRORS = YES`.
- The gate is the manifest's `native_lint`: `swift build`; an app adds its `xcodebuild build`. It
  checks no format and no style: they find no defect, and on code that exists they only make it be
  rewritten.
- The audit of the dependencies (principles 6.5), in `@gate-final`: the versions pinned in
  `Package.resolved` against the published advisories.
- The version is the app's `CFBundleShortVersionString` (a tool's, a constant), logged at startup
  (operations 2).

## 6. Serialization

`Codable` with the declared names: no key strategy, no `CodingKeys` that rename; an enumeration as its
raw value, which is its name (§1). Data that comes from outside is decoded once, at the boundary.

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON and property lists: `JSONDecoder`/`PropertyListDecoder` on `Decodable` types, a non-optional
  property that is missing throwing `DecodingError`, and the encoders on `Encodable` ones — not
  `JSONSerialization` with `as? [String: Any]`, where every cast that does not match is `nil`, in
  silence;
- XML, which Foundation does not decode into types: one `XMLParser` delegate that maps into the
  types, and the parsed elements stay in it;
- the settings: one typed wrapper over `UserDefaults` — not `UserDefaults.standard.string(forKey:)`
  where the value is used;
- the database: SwiftData's models — not rows or dictionaries read by key.

## 7. What /dev:j-setup and /dev:j-new-project read in a Swift project

- **Recognized by**: `Package.swift`; an app by its `.xcodeproj` (or a project generator's file) with a
  SwiftUI `App`.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Swift project |
  | `testing.md` | every Swift project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `app.md` | `branches/frontend.md`, `branches/data.md`, `branches/security.md`: an app |

- **What LISTEN asks** (`/dev:j-new-project`): what is built — an iOS app, a macOS app, a library, a
  command-line tool; for an app, the backend whose OpenAPI document the client is generated from, and
  whether it keeps data on the device.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `Package.swift`; the pack
  has no configuration file to copy.
- **Vendored** (`@vendored-globs`): `.build/`, `DerivedData/`, `*.xcodeproj/xcuserdata/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: a tool `swift run <product>`; an app from Xcode, or `xcodebuild` and the
  simulator.
- **Where its errors show** (`/dev:j-debug`): the build's output; the failed test's output; the unified log
  (`log stream --predicate 'subsystem == "<subsystem>"'`, Console.app); for an app, Xcode's console.
