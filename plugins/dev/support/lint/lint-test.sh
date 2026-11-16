#!/usr/bin/env bash
# lint-test.sh — self-test every ast-grep lint pack under .claude/lint-rules/.
# Contract (the RED→GREEN of layers 1-2): for each pack with an `ast-grep/` dir,
# every `tests/invalid/**` fixture MUST be flagged (>=1 finding) and every
# `tests/valid/**` fixture MUST be clean (0 findings). Uses the pack's rules + `_shared`.
# Dot-entries are pruned: a fixture dir can pick up gitignored build artifacts (a build
# tool's cache folder), and a `.lock`/`.bin` no rule could ever flag would turn the suite RED.
# Exit 0 = all packs green; 1 = at least one fixture wrong.
# If ast-grep is not installed → skip-with-warning (exit 0), per the offline-safe policy.
# If python3 is not installed → skip-with-warning (exit 0), same policy: scan_count() needs it
# to parse ast-grep's JSON output, and without it every fixture would be misreported as
# "NOT flagged" (a false RED blaming the packs, not the missing tool).
set -uo pipefail

# The packs sit beside support/: .claude/lint-rules in a project, the same layout in a workbench copy.
LR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/lint-rules"
SHARED="$LR/_shared/ast-grep"

if ! command -v ast-grep >/dev/null 2>&1; then
  echo "[lint-test] ast-grep not installed — skipping rule tests (exit 0, offline-safe)."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[lint-test] python3 not installed — skipping rule tests (exit 0, offline-safe)."
  exit 0
fi

# count findings for one file under a temp config (findings JSON array length)
scan_count() { # scan_count <config> <file> -> finding count.
  # ast-grep exits non-zero when it finds error-severity matches; with `pipefail` that would
  # mark the pipe failed. Capture stdout FIRST (its exit code is irrelevant), then parse.
  local out
  out="$(ast-grep scan -c "$1" "$2" --json=compact 2>/dev/null)"
  printf '%s' "$out" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0
}

fail=0
packs=0
for dir in "$LR"/*/; do
  pack="${dir%/}"
  name="$(basename "$pack")"
  [ -d "$pack/ast-grep" ] || continue     # native-only packs (dart/perl) have no ast-grep layer
  [ -d "$pack/tests" ]    || continue
  packs=$((packs+1))

  cfg="$(mktemp)"
  printf 'ruleDirs:\n  - %s\n' "$SHARED" > "$cfg"
  [ "$name" != "_shared" ] && printf '  - %s\n' "$pack/ast-grep" >> "$cfg"

  if [ -d "$pack/tests/invalid" ]; then
    while IFS= read -r f; do
      n="$(scan_count "$cfg" "$f")"
      if [ "${n:-0}" -ge 1 ] 2>/dev/null; then
        echo "[ok]   $name invalid/$(basename "$f"): $n finding(s)"
      else
        echo "[FAIL] $name invalid/$(basename "$f") NOT flagged"; fail=1
      fi
    done < <(find "$pack/tests/invalid" -name '.*' -prune -o -type f -print 2>/dev/null)
  fi

  if [ -d "$pack/tests/valid" ]; then
    while IFS= read -r f; do
      n="$(scan_count "$cfg" "$f")"
      if [ "${n:-0}" -eq 0 ] 2>/dev/null; then
        echo "[ok]   $name valid/$(basename "$f") clean"
      else
        echo "[FAIL] $name valid/$(basename "$f") has $n finding(s)"; fail=1
      fi
    done < <(find "$pack/tests/valid" -name '.*' -prune -o -type f -print 2>/dev/null)
  fi

  rm -f "$cfg"
done

echo "---"
echo "[lint-test] $packs ast-grep pack(s) tested; result: $([ "$fail" -eq 0 ] && echo GREEN || echo RED)"
exit "$fail"
