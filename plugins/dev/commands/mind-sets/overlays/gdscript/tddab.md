# GDScript (Godot 4.7) — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in a Godot project: the
tests by level and the reference code of a block. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Godot project (the component is
the game); a plan copies them into its blocks (`tddab-planner.md`, "The commands, by level"). `RUN` is
`addons/gdUnit4/runtest.sh --godot_binary "$(command -v godot)" --headless --ignoreHeadlessMode`.

| Key | GDScript |
|---|---|
| `@test-focused-<component>` | `godot --headless --import --quit && RUN -a res://{suite}` — the block's suite: a single test cannot run alone |
| `@test-block-<component>` | `RUN -a res://{suite}`, once for each suite the block touches |
| `@test-fast` | `RUN -a res://test/unit` |
| `@test-slow` | `RUN -a res://test` — unit and integration |
| `@test-e2e` | `godot --headless --path . --quit-after 120` — the main scene started headless; exit 0 and its `game_started` line |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `RUN -a res://test`, the main scene started headless |

`--import` comes first when the block adds a `class_name`: it writes the cache of the global classes.
Before the tests, the component's gate (`language.md` §5). The run's `Overall Summary: N test cases`
is read: a path with no test exits 0.

## 2. Each block at its level

The RED of a block runs at the level of what it builds (game branch 11): a rule of the game as a unit
suite in `test/unit/`, on plain objects and doubles of its contracts; a scene as an integration suite in
`test/integration/`, loaded with `scene_runner`; the whole game as the main scene started headless.

## 3. Reference RED — a rule of the game

```gdscript
# res://test/unit/combat/health_test.gd
extends GdUnitTestSuite
## The suite of src/combat/health.gd.

# gdUnit4 assertions are fluent (each returns the assertion): the value is meant to be dropped.
@warning_ignore_start("return_value_discarded")

const MAXIMUM: int = 10


func test_should_lose_the_damage_when_hit() -> void:
	var health: Health = Health.new(MAXIMUM)

	health.take_damage(3)

	assert_int(health.current()).is_equal(7)


func test_should_stop_at_zero_when_the_damage_is_larger() -> void:
	var health: Health = Health.new(MAXIMUM)

	health.take_damage(MAXIMUM + 5)

	assert_int(health.current()).is_equal(0)


func test_should_signal_depleted_when_reaching_zero() -> void:
	var health: Health = Health.new(MAXIMUM)

	health.take_damage.call_deferred(MAXIMUM)

	await await_signal_on(health, "depleted", [])
```

Without `Health`, the suite does not compile: exit 105. With a wrong expected value: exit 100.

## 4. Reference GREEN

```gdscript
# res://src/combat/health.gd
class_name Health
extends RefCounted
## The hit points of a character: they never go below zero, and their end is signalled.

signal depleted

var _current: int


func _init(maximum: int) -> void:
	_current = maximum


func current() -> int:
	return _current


func take_damage(amount: int) -> void:
	_current = maxi(_current - amount, 0)
	if _current == 0:
		depleted.emit()
```

## 5. Rules of a GDScript block

- Every declaration typed — written, or `:=` where the type is evident (`language.md` §1).
- The contract a block's consumers use is an `@abstract` class, part of the RED.
- Doubles subclass the contract, in `test/doubles/`; test objects from `TestData` (`testing.md`).
- A node gets its dependencies through `setup` (`godot.md` §2); a rule of the game is a plain object.
- No `print`, no `assert` in a test; every `Error` checked or returned.
- A block that adds a `class_name` runs `--import` before its focused run.

## 6. The skeleton's blocks

The form in Godot 4.7 of each block of the skeleton `/dev:j-new-project` plans for a game:

| Block | Godot 4.7 |
|---|---|
| G1 | the project: `project.godot` with the pack's `[debug]` section (as /dev:j-setup copied it), `config/features` `4.7`, the Input Map's first actions, `application/config/version`; `gdlintrc`; `.gitignore` with `.godot/`; gdUnit4 at its release in `addons/gdUnit4/`; `src/core/app_log.gd` (`language.md` §4) and the configuration read and validated at startup (`game.cfg`, `language.md` §5); `main.tscn` with `World` and `UI` and `main.gd`, the composition root (`godot.md` §1). RED: the main scene started headless logs `game_started` with the version and exits 0; with an invalid `game.cfg` it exits 1 with `startup aborted` |
| G2 | the first mechanic's rules, chosen in LISTEN, as plain objects in `src/<mechanic>/`, with their state machine when the mechanic has states (game branch 5) — `testing.md`, unit suites |
| G3 | the first scene that presents them, in `src/world/`: the node, its `setup`, its actions of the Input Map, its signals up (`godot.md` §2-5); its integration suite with `scene_runner`; the root wires it |
| G4 | the interface: the HUD in `src/ui/`, connected by the root to the rules' signals; its integration suite |
| G5 | the save: the format with its `version`, written to `user://` by `SaveFile` and read back into typed objects, a version it does not know refused (`godot.md` §7); unit suites for the format, an integration suite for the file |
