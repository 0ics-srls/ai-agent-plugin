# Swift — The app (SwiftUI)

How `branches/frontend.md` is written in a SwiftUI app for iOS and macOS. The language is
`language.md`.

---

## 1. The client, generated at every build

- The client and its types come from the backend's OpenAPI document through Apple's
  swift-openapi-generator, the build plugin: the document and its configuration sit in the target, the
  code is generated at every build and nobody edits it (frontend 1). The generated types are the
  entities the app uses, as they are (frontend 2).
- A nullable field written as `anyOf` with `{"type": "null"}` is dropped by the generator: the API's
  document writes a nullable value as a type list, `["integer", "null"]`.
- Every answer that is not a success becomes the domain's error once, in one client middleware;
  every call is the entity or the typed error (`language.md` §3).
- Every list runs on the server (frontend 3).

## 2. A screen's logic

- One view model per screen: `@MainActor @Observable class`, holding what the screen shows — the
  data with its loading state and its error (frontend 4) — and changing it only in answer to an intent.
- It speaks only to the contracts; where the user goes next is the shell's, asked through a closure.

## 3. The screen

- A view is `(State) → UI`: it reads the state and sends the user's intents; it holds no data from the
  API.
- Every failure reaches the user (frontend 5).
- Every element a test touches has an `accessibilityIdentifier`.

## 4. Composition, navigation, settings, storage, security

- The `App` is the composition root: it builds the services once and hands them in.
- One `NavigationStack` owned by the shell; the features never navigate on their own.
- The settings — the backend's address — come from outside the code (the build configuration, the
  `Info.plist`) and are validated at start (frontend 8).
- Data kept on the device: SwiftData, an enumeration stored as its name (its `String` raw value).
- Secrets in the Keychain, never in the binary or in `UserDefaults`; App Transport Security stays on.

## 5. Testing the screens

- XCUITest runs the app on the iOS simulator and on macOS, finds the elements by their accessibility
  identifier, acts on them and checks what they show.
- A live device is driven through WebDriverAgent (Appium's), the XCUITest server that exposes the app
  to WebDriver: taps, the element tree, screenshots — the way to check the app on real hardware.
