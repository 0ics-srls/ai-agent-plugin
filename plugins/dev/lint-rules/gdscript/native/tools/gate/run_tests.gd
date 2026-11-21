extends SceneTree
## The test run: gdUnit4's command-line runner started in a process of its own, with the arguments
## this script received (-a <folder or suite>), and judged from outside. It ends with gdUnit4's exit
## code when that is not 0, and with 1 in the two cases gdUnit4 calls green: no test ran, or objects
## were still alive when the engine closed — Godot reports them after gdUnit4 has set its exit code.
## It is a script of the engine, so it runs the same on every system:
## godot --headless --path . -s res://tools/gate/run_tests.gd -a res://test/unit

const RUNNER: String = "res://addons/gdUnit4/bin/GdUnitCmdTool.gd"
const LOG_COPIER: String = "res://addons/gdUnit4/bin/GdUnitCopyLog.gd"
const LEAK_LINES: Array[String] = ["instances were leaked at exit", "resources still in use at exit"]
## The other tool of the gate. The engine exits 0 on macOS when the script it is given is missing or
## does not compile, so each tool checks that the other is there and compiles.
const PARSE_STEP: String = "res://tools/gate/parse_scripts.gd"


func _init() -> void:
	var parse_step := load(PARSE_STEP) as Script
	if parse_step == null or not parse_step.can_instantiate():
		print("run_tests: the gate's parse step is missing or does not compile: ", PARSE_STEP)
		quit(1)
		return
	var given: PackedStringArray = _arguments_after_this_script()
	# --remote-debug on a port nobody listens on keeps the engine out of its interactive debugger.
	var run: PackedStringArray = [
		"--headless", "--path", ".", "-s", "-d", "--remote-debug", "tcp://127.0.0.1:0", RUNNER, "--ignoreHeadlessMode",
	]
	run.append_array(given)
	var lines: Array[String] = []
	var status: int = OS.execute(OS.get_executable_path(), run, lines, true)
	var output: String = "\n".join(lines)
	print(output)

	var copy: PackedStringArray = ["--headless", "--path", ".", "--quiet", "-s", LOG_COPIER]
	copy.append_array(given)
	var copied: int = OS.execute(OS.get_executable_path(), copy)
	if copied != 0:
		print("run_tests: gdUnit4's log was not copied (exit %d)" % copied)

	quit(_verdict(status, output))


func _arguments_after_this_script() -> PackedStringArray:
	var all: PackedStringArray = OS.get_cmdline_args()
	for index: int in all.size():
		if all[index].ends_with("run_tests.gd"):
			return all.slice(index + 1)
	return PackedStringArray()


func _verdict(status: int, output: String) -> int:
	if status != 0:
		print("run_tests: gdUnit4 ended with %d" % status)
		return status
	var summary := RegEx.create_from_string("Overall Summary:.*\\s(\\d+) test cases")
	var found: RegExMatch = summary.search(output)
	if found == null or found.get_string(1).to_int() == 0:
		print("run_tests: no test ran")
		return 1
	for leak: String in LEAK_LINES:
		if output.contains(leak):
			print("run_tests: objects were still alive when the engine closed")
			return 1
	print("run_tests: %s test cases, nothing left alive" % found.get_string(1))
	return 0
