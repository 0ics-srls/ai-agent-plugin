# PHP — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in PHP. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a PHP project; a plan copies them into its blocks
(`tddab-planner.md`, "The commands, by level").

| Key | PHP |
|---|---|
| `@test-focused-<component>` | `vendor/bin/phpunit --filter {test} {file}` |
| `@test-block-<component>` | `vendor/bin/phpunit {file}`, once for each test file the block touches |
| `@test-fast` | `vendor/bin/phpunit` |
| `@test-slow` | `vendor/bin/phpunit --testsuite=Unit,Feature` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `vendor/bin/phpunit --testsuite=Unit,Feature`, the audit (`language.md` §5) |

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `tests/Unit/` on the doubles; the code that talks to the
outside in `tests/Feature/` on the real thing (`testing.md` §2).

## 3. The RED of a block

The test calls the class the block will build as its contract says: it fails first because the class does not exist, then because
its behaviour is wrong — the failing test names it.

## 4. The GREEN

The smallest code that makes the RED pass, typed, through the gate (`language.md` §5).

## 5. Rules of a PHP block

- `declare(strict_types=1);` first; everything typed; `final` by default (`language.md` §1).
- A value a `final readonly class`, never an array; a closed set a backed `enum`.
- The state of a contract on the fakes; a call across the boundary on `createMock` (`testing.md` §3).
- No debug output: the logger (`language.md` §4).

## 6. The skeleton's blocks

The form in PHP of each block of the skeleton `/dev:j-new-project` plans; the frameworks are the project's, chosen in LISTEN.

| Block | PHP |
|---|---|
| 1 | `composer init`; the pack's files as /dev:j-setup placed them; the contracts and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the code that talks to the outside, for the first entity, written once; its tests on the real thing |
| 3 | the logic of the first entity on the contracts; the fakes and the tests on them |
| 4 | the transport the project has, on the logic: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup |
