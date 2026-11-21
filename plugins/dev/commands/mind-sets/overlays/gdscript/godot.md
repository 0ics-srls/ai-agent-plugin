# GDScript (Godot 4.7) — The engine and the game

How `branches/game.md` is written in a Godot 4.7 project: the main scene, the nodes and their
dependencies, signals, autoloads, input, time, data and saves.

---

## 1. The main scene is the composition root

`main.tscn` with `main.gd` is the entry point (game branch 1): it reads the configuration, creates the
logger and the services, and hands each node what it needs. Under it, `World` (a `Node2D` or `Node3D`)
holds the current level and `UI` (a `CanvasLayer`) the interface; a level changes by freeing the child
of `World` and adding the next one, so the transition is the root's.

```gdscript
# res://src/main.gd
extends Node
## The composition root: reads the configuration, builds the services once, hands each node what it
## needs.

const CONFIG_PATH: String = "res://game.cfg"

@export var player: Player
@export var hud: Hud


func _ready() -> void:
	var config: GameConfig = GameConfig.load_from(CONFIG_PATH)
	if config.error() != "":
		# The project logger does not exist yet: the engine log is the only sink at this point.
		push_error("startup aborted: %s" % config.error())
		get_tree().quit(1)
		return
	var app_log: AppLog = AppLog.new(config.log_level())
	var version: String = ProjectSettings.get_setting("application/config/version", "dev")
	app_log.info("game_started", {"version": version})
	var health: Health = Health.new(config.player_health())
	player.setup(health, app_log)
	hud.setup(health)
```

`player` and `hud` are set in `main.tscn` (`player = NodePath("World/Player")`): the root does not look
nodes up by path.

## 2. A node is built by the scene — its dependencies are handed in

- **The engine creates a node with no arguments.** A node whose `_init` requires an argument compiles;
  when the scene loads, the node stays in the tree without its script — none of its code runs — while
  the game goes on. So a node has no required `_init` argument.
- Its dependencies arrive from the parent that owns it, as Godot's scene organization lists them: a
  `setup(...)` method the composition root calls; an `@export` reference the scene file sets; a
  `Callable` the parent assigns: a test hands it a double the same way.
- **The engine calls `_ready` on the children before the parent**: the root's `_ready` calls `setup`,
  so a node uses its dependencies from `setup` on, never in its own `_ready`.
- An object that is not a node (`Health`, `AppLog`, `SaveFile`) takes its dependencies in `_init`.

```gdscript
# res://src/world/player.gd
class_name Player
extends CharacterBody2D
## The player on screen: it presents a Health and forwards the input; the rules are in Health.

signal died

const SPEED: float = 200.0

var _health: Health
var _app_log: AppLog


func setup(health: Health, app_log: AppLog) -> void:
	_health = health
	_app_log = app_log
	var connected: int = _health.depleted.connect(_on_health_depleted)
	if connected != OK:
		_app_log.error("player_not_connected", {"error": error_string(connected)})


func _physics_process(_delta: float) -> void:
	var direction: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * SPEED
	if move_and_slide():
		_app_log.info("player_collided", {"collisions": get_slide_collision_count()})


func _on_health_depleted() -> void:
	_app_log.info("player_died")
	died.emit()
```

## 3. Signals up, calls down

A child emits a signal in the past tense (`died`, `item_collected`); its parent, or the composition
root, connects it and decides (game branch 3). The result of `connect` is checked (`language.md` §3).
A signal a node must declare for its contract is typed (`language.md` §2).

```gdscript
# res://src/ui/hud.gd
class_name Hud
extends CanvasLayer
## The interface over the world: it shows what the rules report, through their signals.

@export var status: Label

var _health: Health


func setup(health: Health) -> void:
	_health = health
	var connected: int = _health.depleted.connect(_on_health_depleted)
	if connected != OK:
		push_error("hud not connected: %s" % error_string(connected))


func _on_health_depleted() -> void:
	status.text = "Game over"
```


## 4. Autoloads

An autoload is only for a system that keeps its own data, is reached from every scene and changes no
other system's data (game branch 4) — a music player, a scene-transition fader. Services, the logger and
the game's state are built by the composition root and handed in.

## 5. Input and time

- Every input is an action of the Input Map (`project.godot` `[input]`): `Input.get_vector(...)`,
  `Input.is_action_just_pressed("jump")`, `_unhandled_input(event)` with `event.is_action_pressed(...)`.
  No key code in the game's logic (game branch 6).
- Physics and movement in `_physics_process(delta)`, the rest in `_process(delta)`; a delay is a
  `Timer` or `get_tree().create_timer(seconds).timeout` awaited (game branch 7).

## 6. Data and resources

- The game's tuned values are data (game branch 8): a custom `Resource` (`class_name EnemyStats extends
  Resource` with `@export` fields), edited in the inspector and shipped with the game as `.tres` in
  `res://` — or a JSON/`ConfigFile` read and validated at load.
- `preload` for what a scene always needs (loaded with the script, off the frame's path); `load` or
  `ResourceLoader.load_threaded_request` for what is chosen at run time, ahead of the frame that uses
  it. A missing resource is a `null`, checked.
- A node's properties are set before `add_child` (game branch 9).

## 7. Saves

A save is JSON in `user://` (game branch 10), with a `version` field, written by `SaveFile`
(`language.md` §3) and read back into typed objects, every field checked; a version the loader does
not know is refused with a message. A `Resource` is never loaded from `user://`: it can carry a script.
`ConfigFile` holds the player's settings, not the game's state.

## 8. The project's folders

```
project.godot, game.cfg, gdlintrc
src/
├── main.gd, main.tscn      # the composition root (§1)
├── core/                   # the logger, the configuration, the contracts and error codes
├── <mechanic>/             # the rules of the game, one folder per mechanic: plain objects (game branch 2)
├── world/                  # the scenes of the world: levels, characters — they present the rules
├── ui/                     # the scenes of the interface
└── save/                   # the save format and its file
test/
├── unit/                   # the rules, without the scene tree; mirrors src/
├── integration/            # scenes loaded headless, files, the main scene
├── doubles/                # the doubles of the contracts (testing.md)
└── test_data.gd            # the objects every suite shares
addons/                     # third-party code at fixed releases, outside the gate
```

The assets live beside the scenes that use them (`world/player/player.png`).
