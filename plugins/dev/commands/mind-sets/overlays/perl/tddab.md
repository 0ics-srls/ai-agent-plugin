# Perl — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in Perl. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Perl project; a plan copies them into its blocks (`tddab-planner.md`, "The commands, by
level").

| Key | Perl |
|---|---|
| `@test-focused-<component>` | `carton exec prove -lv {file}` — the test file; its subtests name the failing behaviour |
| `@test-block-<component>` | `carton exec prove -l {file}`, once for each test file the block touches |
| `@test-fast` | `carton exec prove -lr t/unit` |
| `@test-slow` | `carton exec prove -lr t` |
| `@test-e2e` | the project's end-to-end tests, when it has them; otherwise `none` |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `carton exec prove -lr t`, the audit (`language.md` §5) |

`prove` has no option to stop at the first failing test (`testing-principles.md` 6.3): a run goes
to its end, file by file. The first failure it reports is the one that gets fixed.

Before the tests, the component's gate (`language.md` §5).

## 2. Each block at its level

The RED of a block runs at the level of what it builds: the logic in `t/unit/` on the doubles; the code that talks to the outside in `t/integration/` on the real thing
(`testing.md` §2).

## 3. The RED of a block

The test file uses the class the block will build and calls it as its contract says: it fails first because the class does not exist, then because its behaviour is
wrong — the failing subtest names it.

## 4. The GREEN

The smallest code that makes the RED pass, through the gate (`language.md` §5).

## 5. Rules of a Perl block

- `use v5.36;` first; Moo with typed attributes, `is => 'ro'` (`language.md` §1).
- A contract is a `Moo::Role`.
- The state of a contract on the fakes; a call across the boundary on `Test2::Mock` (`testing.md` §3).
- No `print` or `warn`: `Log::Any` (`language.md` §4).

## 6. The skeleton's blocks

The form in Perl of each block of the skeleton `/dev:j-new-project` plans; the frameworks are the project's, chosen in LISTEN.

| Block | Perl |
|---|---|
| 1 | the `cpanfile`, with Carton; the pack's files as /dev:j-setup placed them; the contracts and the errors (`language.md` §1, §3). RED: the first contract's test |
| 2 | the code that talks to the outside, for the first entity, written once; its tests on the real thing |
| 3 | the logic of the first entity on the contracts; the fakes and the tests on them |
| 4 | the transport the project has, on the logic: validation at the boundary, the errors mapped once, serialization as is (`language.md` §6) |
| 5 | operations: the version logged at startup, the logging configured once, the configuration validated at startup |
