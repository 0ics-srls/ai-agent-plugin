# GDScript (Godot 4.7) — Language

How the principles and the code principles are written in GDScript on Godot 4.7. Every form below was
run on Godot 4.7.2 with the pack's warnings (every one at error), gdtoolkit 4.5.0 and gdUnit4 6.2.3.

---

## 1. Language and conventions

- The GDScript style guide's names: files and folders `snake_case`; `class_name` and node names
  `PascalCase`; functions, variables and signals `snake_case`, a signal in the past tense
  (`health_depleted`); constants and enum members `CONSTANT_CASE`; an enum `PascalCase`, singular. A
  file is named after its `class_name` (`health.gd` → `Health`). The names are the author's care: no
  tool of the gate checks them.
- The style guide's order of a script: `@tool`/`@icon`, `class_name`, `extends`, the doc comment,
  signals, enums, constants, static variables, `@export` variables, the other variables, `@onready`
  variables, `_static_init`, static methods, the engine's virtual methods (`_init`, `_enter_tree`,
  `_ready`, `_process`, `_physics_process`, the others), then the rest; public before private.
- **Every declaration has its type** — `var lives: int = 3`, `func hit(amount: int) -> void`, or `:=`
  where the type is evident from the right side (`var health := Health.new(MAXIMUM)`). The pack raises
  the warnings that find a defect to error — `inferred_declaration` is off (the owner's decision) — so a missing type
  (`untyped_declaration`) and `:=` on a `Variant` (`inference_on_variant`) do not compile; a value the
  engine returns as a `Variant`
  (`ConfigFile.get_value`, `get_setting`) gets the declared type of its variable. Collections are typed:
  `Array[Enemy]`, `Dictionary[StringName, int]`, `for enemy: Enemy in enemies`.
- A call or a property the compiler cannot check is an error (`unsafe_method_access`,
  `unsafe_property_access`, `unsafe_call_argument`, `unsafe_cast`): an `Object` is narrowed with `is`
  before its members are used. `as` gives `null` on a wrong type without a word: a cast with `as` is
  followed by the check of that `null`.
- **A closed set is an `enum`** (code principles 3.3). An `int` where the enum is expected does not
  compile (`int_as_enum_without_cast`). A `match` on an enum is not checked for exhaustiveness: it ends
  with `_:`, which names the value it got.
- **Contracts are abstract classes**: `@abstract class_name` with `@abstract func`. Constructing one
  does not compile, and neither does a subclass that misses an abstract method. Consumers type their
  variables with the contract.
- **Data is immutable** (code principles 3.1): a data object takes its values in `_init`, keeps them
  in `_` members and exposes read functions (`stats.speed()`); an assignment to a function does not
  compile. A property with only a getter does not protect — an assignment to it compiles and is lost.
  A change is a new object; a typed array kept inside is a copy made read-only (`make_read_only()`).
- **Private is the `_` prefix.** The engine does not enforce it: the reader does. The engine's
  callbacks keep the engine's names (`_ready`, `_on_<Node>_<signal>`).

## 2. Coroutines and signals

- A function that `await`s is a coroutine; calling it without `await` is an error (`missing_await`).
- A wait is an `await` on a signal (code principles 4.7): `await timer.timeout`,
  `await get_tree().process_frame` only where one frame is the requirement.
- A signal declares its argument types — `signal health_changed(current: int, maximum: int)`. **The
  engine does not check the arguments of `emit`** (an `emit` with wrong types compiles): the emitter's
  test checks them.

## 3. Errors are values

GDScript has no exceptions. An engine call that can fail returns an `Error`, or `null` and a getter of
the error (`FileAccess.open` → `FileAccess.get_open_error()`); a domain operation returns a result
object whose error has a code from an enum (code principles 3.4). Every one is checked:
`return_value_discarded` at error makes a dropped result a compile error — the `Error` of `save()`, of
`ConfigFile.load()`, the result of `connect()`. `Signal.connect` returns an `int`, not an `Error`: its
variable is an `int`, compared with `OK`. A fluent API whose value is meant to be dropped (a `Tween`
chain) carries `@warning_ignore("return_value_discarded")` on its line, with the reason.

```gdscript
# res://src/save/save_file.gd
class_name SaveFile
extends RefCounted
## Writes the save to user://. Every engine call that can fail is checked, and a failure goes back
## to the caller as an Error, with its cause in the log.

var _app_log: AppLog


func _init(app_log: AppLog) -> void:
	_app_log = app_log


func write(path: String, text: String) -> Error:
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return _failed("save_open_failed", path, FileAccess.get_open_error())
	if not file.store_string(text):
		return _failed("save_write_failed", path, file.get_error())
	return OK


func _failed(event: String, path: String, cause: Error) -> Error:
	_app_log.error(event, {"path": path, "error": error_string(cause)})
	return cause
```

`assert` is for an invariant of the programmer only: a failed `assert` stops a headless debug run.

## 4. Logging

One project logger (code principles 4.9), injected like any other dependency: every line is the event
and its context as JSON, written through the engine log — `push_error` for errors, `push_warning` for
warnings, `print` for the rest — so it reaches every sink the engine has: the console,
`user://logs/godot.log` (`debug/file_logging/enable_file_logging.pc`, the last `max_log_files` runs
kept), and any `Logger` registered with `OS.add_logger`. Nothing else prints.

```gdscript
# res://src/core/app_log.gd
class_name AppLog
extends RefCounted
## The one logger of the project. Every line carries the event and its context as JSON and goes
## through the engine log, so it reaches every sink the engine has.

enum Level { DEBUG, INFO, WARNING, ERROR, OFF }

var _min_level: Level


func _init(min_level: Level) -> void:
	_min_level = min_level


func info(event: String, context: Dictionary[String, Variant] = {}) -> void:
	_write(Level.INFO, event, context)


func warning(event: String, context: Dictionary[String, Variant] = {}) -> void:
	_write(Level.WARNING, event, context)


func error(event: String, context: Dictionary[String, Variant] = {}) -> void:
	_write(Level.ERROR, event, context)


func _write(level: Level, event: String, context: Dictionary[String, Variant]) -> void:
	if level < _min_level:
		return
	var line: String = JSON.stringify(
		{"level": Level.find_key(level), "event": event, "context": context}
	)
	match level:
		Level.ERROR:
			push_error(line)
		Level.WARNING:
			push_warning(line)
		_:
			print(line)
```

## 5. Project and build

- `project.godot` is the pack's for its `[debug]` section (`${CLAUDE_PLUGIN_ROOT}/lint-rules/gdscript/native/project.godot`,
  which j-setup copies or merges): the GDScript warnings that find a defect at error, the others off —
  unused names and style find none; `directory_rules` keeps the engine's
  default, which silences `res://addons`. The Godot version is the project's feature tag
  (`config/features=PackedStringArray("4.7")`); every developer and the CI run the same 4.7.x binary.
- Third-party code lives in `addons/<name>/` at one fixed release — gdUnit4 at the version its
  `plugin.cfg` names — and is updated as a change of its own. A folder the engine must not import
  (`docs/`) has an empty `.gdignore`. `.godot/` (the engine's cache) is not committed.
- The version is `application/config/version`; the composition root logs it at startup (operations 2).
- Configuration (code principles 3.6, principles 5.1): one file read and validated by the composition
  root before anything else starts — `ConfigFile` for settings, never for game state. An invalid value
  stops the startup (`godot.md` §1):

```gdscript
# res://src/core/game_config.gd
class_name GameConfig
extends RefCounted
## The settings, read once at startup from one file and checked there; nothing else reads it.

const SECTION: String = "game"

var _log_level: AppLog.Level = AppLog.Level.INFO
var _player_health: int = 0
var _error: String = ""


static func load_from(path: String) -> GameConfig:
	var config: GameConfig = GameConfig.new()
	var file: ConfigFile = ConfigFile.new()
	var loaded: Error = file.load(path)
	if loaded != OK:
		config._error = "%s: %s" % [path, error_string(loaded)]
		return config
	var level_name: String = file.get_value(SECTION, "log_level", "INFO")
	if not AppLog.Level.has(level_name):
		config._error = "%s: unknown log_level %s" % [path, level_name]
		return config
	config._log_level = AppLog.Level[level_name]
	var health_points: int = file.get_value(SECTION, "player_health", 0)
	if health_points <= 0:
		config._error = "%s: player_health must be positive" % path
		return config
	config._player_health = health_points
	return config


func error() -> String:
	return _error


func log_level() -> AppLog.Level:
	return _log_level


func player_health() -> int:
	return _player_health
```

- The gate is the manifest's `native_lint`: `godot --headless --import --quit` (it writes the cache of
  the global classes, without which `--check-only` does not know a `class_name` of another file), then
  `godot --headless --check-only --script` on every `.gd` outside `addons/` and `.godot/` (exit 1 on a
  warning at error; through `xargs`, 123), then `gdlint .`, which skips `addons/` and `.godot/` and
  keeps its two rules that find a defect — a value compared with itself, an expression with no effect
  (the pack's `gdlintrc`). The gate checks no names, no order and no formatting: they find no defect,
  and on code that exists they only make it be rewritten.

## 6. Serialization

- A save or a data file is JSON or `ConfigFile` data — never a `Resource` read from the player's disk:
  a `.tres` or `.res` can carry a script, and loading it runs it. Names leave and arrive as declared,
  and an enum as its name (`Level.find_key(level)`, read back with `Level[name]` after `Level.has(name)`
  — code principles 3.5).
- `JSON.parse_string` returns a `Variant`: it is checked with `is` and read into typed objects, every
  field validated (game branch 10).
- Godot has no mapper into the script's classes, so the project has one reader that is (code
  principles 3.7): the `Dictionary` of a parse and the values of a `ConfigFile` stay in it, and the rest
  of the code receives typed objects — not `dict["x"]`, `dict.get("x", default)` or
  `config.get_value(section, key, default)` where the value is used, where a key mistyped yields the
  default in silence.

## 7. What j-setup and j-new-project read in a Godot project

- **Recognized by**: `project.godot`. The branches: `game` always; `data`, `api`, `resilience`,
  `security` only if the game has a storage of its own or talks to a service.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Godot project |
  | `testing.md` | every Godot project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `godot.md` | `branches/game.md` |
- **What LISTEN asks** (`j-new-project`): 2D or 3D; the target platforms (desktop, mobile, web); the
  first mechanic — the rule the first playable scene shows.
- **The lint gate**: the manifest's `native_lint`, run from the folder of `project.godot`; the pack's
  `project.godot` (its `[debug]` section merged into the project's, asking first) and `gdlintrc` go
  to that folder.
- **Vendored** (`@vendored-globs`): `addons/`, `.godot/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `godot --path .` (the editor: `godot --path . --editor`); headless, the main
  scene runs with `godot --headless --path .`.
- **Where its errors show** (`j-debug`): the engine's output in the terminal that started it, with the
  GDScript backtrace of a `push_error`; `user://logs/godot.log` (on Linux
  `~/.local/share/godot/app_userdata/<project>/logs/`); the gdUnit4 run's report.
