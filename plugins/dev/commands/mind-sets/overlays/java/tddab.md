# Java — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Java. How a test is written is
`testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Java project; a plan copies them into its blocks
(`tddab-planner.md`, "The commands, by level").

| Key | Java |
|---|---|
| `@test-focused-<component>` | `./mvnw -q test -Dtest={class}#{test} -DexcludedGroups=` |
| `@test-block-<component>` | `./mvnw -q test -Dsurefire.skipAfterFailureCount=1 -Dtest={class} -DexcludedGroups=`, once for each test class the block touches |
| `@test-fast` | `./mvnw -q test -Dsurefire.skipAfterFailureCount=1` |
| `@test-slow` | `./mvnw -q test -Dsurefire.skipAfterFailureCount=1 -DexcludedGroups=` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `./mvnw -q test -Dsurefire.skipAfterFailureCount=1 -DexcludedGroups=`, the audit (`language.md` §5) |

`-Dsurefire.skipAfterFailureCount=1` makes Surefire skip the remaining tests after the first failure or error (`testing-principles.md` 6.3).

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in a plain test on the doubles; the code that talks to
the outside in a `@Tag("slow")` test on the real thing (`testing.md` §2).

## 3. The RED of a block

The test calls the class the block will build as its contract says, with the class and the method declared and their
bodies returning a wrong value: it compiles, runs and fails on the behaviour it names.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Java block

- A closed set an `enum`; a value a `record` (`language.md` §1).
- A contract is an `interface`; constructor injection only.
- The state of a contract on the fakes; a call across the boundary on Mockito (`testing.md` §3).
- AssertJ only; `assertThatThrownBy` for an exception.
- No console write: SLF4J (`language.md` §4).

## 6. The skeleton's blocks

The form in Java of each block of the skeleton `/dev:j-new-project` plans; the frameworks are the project's, chosen in LISTEN.

| Block | Java |
|---|---|
| 1 | the `pom.xml`, `./mvnw`; the pack's files as `language.md` §5 says; the contracts and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the code that talks to the outside, for the first entity, written once; its tests on the real thing |
| 3 | the logic of the first entity on the contracts; the fakes and the tests on them |
| 4 | the transport the project has, on the logic: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup |
