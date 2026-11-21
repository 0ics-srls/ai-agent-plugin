extends SceneTree
## The gate's parse step: loads every script of the project in one process and reports the ones that
## do not compile. `--check-only` is not used: on macOS it exits 0 on a script that does not parse.

## Folders whose scripts are not the project's own.
const SKIPPED: Array[String] = ["res://addons", "res://.godot"]


func _init() -> void:
	var scripts: Array[String] = []
	_collect("res://", scripts)
	var broken: Array[String] = []
	for path: String in scripts:
		var script := load(path) as Script
		if script == null or not script.can_instantiate():
			broken.append(path)
	for path: String in broken:
		printerr("parse_scripts: does not compile: ", path)
	print("parse_scripts: %d scripts, %d do not compile" % [scripts.size(), broken.size()])
	quit(0 if broken.is_empty() and not scripts.is_empty() else 1)


func _collect(folder: String, scripts: Array[String]) -> void:
	for file: String in DirAccess.get_files_at(folder):
		if file.get_extension() == "gd":
			scripts.append(folder.path_join(file))
	for child_name: String in DirAccess.get_directories_at(folder):
		var child: String = folder.path_join(child_name)
		if child in SKIPPED or FileAccess.file_exists(child.path_join(".gdignore")):
			continue
		_collect(child, scripts)
