#!/usr/bin/env bash
# The test run, from the folder of project.godot: gdUnit4's runtest.sh with the arguments given
# (-a <folder or suite>, -c). It fails on gdUnit4's own exit code, on a run in which no test ran
# (gdUnit4 exits 0 on a path with no test), and on objects still alive when the engine closes:
# gdUnit4 sets its exit code before Godot reports them.
set -u

log="$(mktemp)"
trap 'rm -f "$log"' EXIT

addons/gdUnit4/runtest.sh --godot_binary "$(command -v godot)" --headless --ignoreHeadlessMode "$@" 2>&1 | tee "$log"
status=${PIPESTATUS[0]}

if [ "$status" -ne 0 ]; then
  exit "$status"
fi
if ! grep -Eq 'Overall Summary:.*[^0-9][1-9][0-9]* test cases' "$log"; then
  echo "run_tests: no test ran" >&2
  exit 1
fi
if grep -Eq 'instances were leaked at exit|resources still in use at exit' "$log"; then
  echo "run_tests: objects were still alive when the engine closed" >&2
  exit 1
fi
