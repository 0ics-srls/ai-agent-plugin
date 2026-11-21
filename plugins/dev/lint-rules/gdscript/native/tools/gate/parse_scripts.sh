#!/usr/bin/env bash
# The gate's parse step, run from the folder of project.godot: every script of the project is loaded
# by tools/gate/parse_scripts.gd, in one Godot process. It fails on a script that does not compile,
# and on a run that does not end with its verdict line: Godot exits 0 when the script it was given is
# missing or does not parse.
set -u

output="$(godot --headless --path . --quit-after 600 -s res://tools/gate/parse_scripts.gd 2>&1)"
status=$?
printf '%s\n' "$output"

if [ "$status" -eq 0 ] && printf '%s\n' "$output" | grep -Eq '^parse_scripts: [1-9][0-9]* scripts, 0 do not compile$'; then
  exit 0
fi
if ! printf '%s\n' "$output" | grep -Eq '^parse_scripts: [0-9]+ scripts, [0-9]+ do not compile$'; then
  echo "parse_scripts: no verdict line — the step did not run to its end" >&2
fi
exit 1
