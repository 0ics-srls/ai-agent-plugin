#!/usr/bin/env bash
# Install what the audit's fact collection needs, and report what is available.
#
# Run from the PROJECT ROOT (the repository being audited), not from inside .claude:
#   bash .claude/audit/install.sh
#
# SEPARATION — the rule this script obeys and must keep obeying:
#
#   The audit system owns exactly ONE directory in the project: `audit/`.
#   It reads anywhere; it WRITES NOWHERE ELSE.
#
# No edit to the project's .gitignore, its settings, its config or its sources. The transient
# environment goes in `audit/.tools/`, and it is excluded by `audit/.gitignore` — a file inside the
# audit system's own root, which is the audit's business and nobody else's. Editing the project's
# root .gitignore would also collide with setup-base.sh, which maintains that file with its own
# idempotent list.
#
# Inside `audit/` the split is: `facts/`, `findings/`, `modules.md`, `plan.md` are the PRODUCT and
# belong in the project's history; `.tools/` is machinery and does not.
#
# Idempotent. Nothing already present is installed again, and the script never fails because a
# tool is unavailable: it prints what is missing, and a missing tool means the audit reports that
# dimension `Non esaminato`. That is the honest outcome and it is the point — a missing fact is
# declared, never replaced by reading the files by hand.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
AUDIT_ROOT="$PROJECT_ROOT/audit"
TOOLS="$AUDIT_ROOT/.tools"
VENV="$TOOLS/venv"
REQ="$SCRIPT_DIR/requirements.txt"

echo "=== audit tooling, for $PROJECT_ROOT ==="
echo "    the audit system writes only under audit/ — nothing else is touched"
echo ""

# --- Python dependencies: lizard (KISS) and the tree-sitter grammars (DRY, encapsulation) ----
# One check for the whole requirements file. Checking only lizard would skip the grammars on a
# machine that already has lizard, and F3 would then come out MISSING for no visible reason.
PYMODS="import lizard, tree_sitter, tree_sitter_gdscript, tree_sitter_python, tree_sitter_javascript, tree_sitter_typescript, tree_sitter_c_sharp, tree_sitter_java, tree_sitter_kotlin, tree_sitter_swift, tree_sitter_php, tree_sitter_rust, tree_sitter_c, tree_sitter_cpp, tree_sitter_go, tree_sitter_dart, tree_sitter_perl"
VENV_PY=""
if python3 -c "$PYMODS" >/dev/null 2>&1; then
    echo "[HAVE] python deps   lizard + tree-sitter grammars, importable by python3"
elif [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "$PYMODS" >/dev/null 2>&1; then
    VENV_PY="$VENV/bin/python"
    echo "[HAVE] python deps   in audit/.tools/venv"
else
    echo "[INSTALL] python deps (lizard, tree-sitter grammars)"
    if pip3 install --quiet --user -r "$REQ" >/dev/null 2>&1 && \
       python3 -c "$PYMODS" >/dev/null 2>&1; then
        echo "         installed with pip --user"
    else
        # Debian and friends refuse a user install into a managed environment (PEP 668).
        # A local venv is the documented way out, so take it rather than suggesting
        # --break-system-packages, which breaks something that is not ours.
        echo "         pip --user refused (likely PEP 668) — using audit/.tools/venv instead"
        mkdir -p "$TOOLS"
        if { [ -x "$VENV/bin/python" ] || python3 -m venv "$VENV" >/dev/null 2>&1; } && \
           "$VENV/bin/pip" install --quiet -r "$REQ" >/dev/null 2>&1 && \
           "$VENV/bin/python" -c "$PYMODS" >/dev/null 2>&1; then
            VENV_PY="$VENV/bin/python"
            echo "         installed in audit/.tools/venv"
        else
            echo "[MISS] python deps   could not be installed → the whole code audit will be Non esaminato"
        fi
    fi
fi

# --- the audit system excludes its OWN machinery, inside its OWN root ------------------------
# One owner for that rule: audit.py prepare. Re-implementing it here would be two copies of one capability.
python3 "$SCRIPT_DIR/audit.py" prepare >/dev/null && \
    echo "[IGNORE] audit/.tools/ excluded by audit/.gitignore (the project's own .gitignore is untouched)"

echo ""
echo "Run the audit (it writes audit/REPORT.md) with:"
echo "  python3 .claude/audit/audit.py map"
[ -n "$VENV_PY" ] && echo "  (it runs itself with audit/.tools/venv, where the dependencies are)"
echo ""
echo "Whatever is MISSING above is reported Non esaminato by the audit. It is not worked around."
