# Dart — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Dart. How a test is written is `testing.md`. In a Flutter
project each `dart test` below is `flutter test`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Dart project; a plan copies them into its blocks (`tddab-planner.md`,
"The commands, by level").

| Key | Dart |
|---|---|
| `@test-focused-<component>` | `dart test {file} --name "{test}"` |
| `@test-block-<component>` | `dart test {file}`, once for each test file the block touches |
| `@test-fast` | `dart test test/unit` |
| `@test-slow` | `dart test` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `dart test`, the audit (`language.md` §5) |

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `test/unit/` on the doubles; the code that talks to the outside in
`test/integration/` on the real thing (`testing.md` §2).

## 3. The RED of a block

The test calls the class the block will build as its contract says, with the class declared and its method returning a wrong value: it
fails on the behaviour it names. The gate refuses an unresolved name.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Dart block

- `final` and `const` by default; a closed set an `enum` or a `sealed` class (`language.md` §1).
- A contract is an `abstract interface class`.
- The state of a contract on the fakes; a call across the boundary on `mocktail` (`testing.md` §3).
- No `print`, no `!` on what can be null (`language.md` §1, §4).

## 6. The skeleton's blocks

The form in Dart of each block of the skeleton `j-new-project` plans; the frameworks are the project's, chosen in LISTEN.

| Block | Dart |
|---|---|
| 1 | `dart create --force .`, because the folder holds the pack's file, which then goes back over the template's; the pack's files as `language.md` §5 says; the contracts and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the code that talks to the outside, for the first entity, written once; its tests on the real thing |
| 3 | the logic of the first entity on the contracts; the fakes and the tests on them |
| 4 | the transport the project has, on the logic: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup |
