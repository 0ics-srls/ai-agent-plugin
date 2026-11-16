#!/usr/bin/env bash
# validate-lint-manifest.sh — assert the lint manifest declares every target language
# with all required keys. Dependency-light (bash + grep/awk), no YAML library.
# Usage: validate-lint-manifest.sh [path-to-manifest.yaml]
# Exit 0 = valid; exit 1 = first violation (message on stderr).
set -uo pipefail

MANIFEST="${1:-.claude/lint-rules/manifest.yaml}"
REQUIRED_KEYS=(native_lint ast_grep config_files)
# The languages are the ones the manifest declares; each must have its pack beside the manifest.
mapfile -t LANGS < <(awk '/^languages:/ { inl=1; next } inl && /^  [a-z]+:$/ { sub(/:$/, ""); sub(/^  /, ""); print }' "${1:-.claude/lint-rules/manifest.yaml}")

err() { echo "[manifest] ERROR: $1" >&2; exit 1; }

[ -f "$MANIFEST" ] || err "manifest not found: $MANIFEST"
grep -qE '^languages:' "$MANIFEST" || err "missing top-level 'languages:' key"

for l in "${LANGS[@]}"; do
  grep -qE "^  ${l}:" "$MANIFEST" || err "missing language entry: $l"
  # Extract this language's block: from '  <lang>:' to the next top-level '  <word>:'.
  block="$(awk -v lang="$l" '
    $0 ~ "^  "lang":" { inb=1; next }
    inb && /^  [a-z]/ { inb=0 }
    inb { print }
  ' "$MANIFEST")"
  for k in "${REQUIRED_KEYS[@]}"; do
    printf '%s\n' "$block" | grep -qE "^    ${k}:" || err "language '$l' missing required key: $k"
  done
  [ -d "$(dirname "$MANIFEST")/$l" ] || err "language '$l' is declared but its pack folder is missing"
  while read -r cfg; do
    [ -f "$(dirname "$MANIFEST")/$cfg" ] || err "language '$l' config file missing: $cfg"
  done < <(printf '%s\n' "$block" | awk '/^      - / { sub(/^      - /, ""); print }')
done

[ "${#LANGS[@]}" -gt 0 ] || err "no language declared"
echo "[manifest] OK: ${#LANGS[@]} language(s) declared, each with its keys and its pack"
exit 0
