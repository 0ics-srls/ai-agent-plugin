#!/usr/bin/env python3
"""The code audit's tool, run from the root of the audited project. It writes only under `audit/`.

    python3 .claude/audit/audit.py prepare        audit/.tools/ and audit/.gitignore
    python3 .claude/audit/audit.py scope [<folder>…]  what the audit examines: audit/scope.md
    python3 .claude/audit/audit.py map            audit/map/, of the folders of the scope
    python3 .claude/audit/audit.py plan-describe  audit/plan-describe.md (the earlier layout migrated)
    python3 .claude/audit/audit.py mark-described <module>…   a description written or confirmed
    python3 .claude/audit/audit.py unmark-described <module>…  a description found wrong: described again
    python3 .claude/audit/audit.py check-describe [<module>…] one current section per module, or why not
    python3 .claude/audit/audit.py facts          the facts that need the description: B1, capabilities.md
    python3 .claude/audit/audit.py check <file>   the form of a findings file, or of a checked file
    python3 .claude/audit/audit.py checked        the withdrawn items, valid or stale

When `audit/.tools/venv` exists (install.sh made it), the tool runs itself with that Python and its
tools on the PATH: a plain `python3` is enough.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import deps  # noqa: E402 - the package's own modules, found through the path above
import map as audit_map  # noqa: E402
import plans  # noqa: E402


def prepare(repo: Path, _args: list[str]) -> int:
    """The audit's own machinery is excluded inside its own root: the project's .gitignore is not
    touched."""
    root = repo / "audit"
    (root / ".tools").mkdir(parents=True, exist_ok=True)
    (root / ".gitignore").write_text(".tools/\n", encoding="utf-8")
    return 0


NO_SCOPE = ("audit/scope.md is missing: the user says what the audit examines — "
            "`audit.py scope <folder>…`; `audit.py scope` alone lists the project's own roots.")


def scope(repo: Path, args: list[str]) -> int:
    """With folders, the scope is written. Without, what there is to choose from: the scope said so
    far, and each of the project's own roots with the source files the map would read there."""
    if args:
        made_of = audit_map.mapped_roots(repo)
        problems = audit_map.write_scope(repo, args)
        for p in problems:
            print(p)
        if problems:
            return 1
        print(f"OK audit/scope.md: {', '.join(audit_map.scope(repo) or [])}")
        removed = audit_map.drop_stale(repo)
        if removed:
            print(f"the map was made of other folders ({', '.join(made_of or [])}): removed "
                  f"{', '.join(removed)} — made again from the new scope")
        return 0
    said = audit_map.scope(repo)
    print(f"scope: {', '.join(said)}" if said else "no scope yet")
    for root in audit_map.own_roots(repo):
        print(f"own root: {root} — {len(deps.source_files(repo, [root]))} source files")
    return 0


def map_(repo: Path, _args: list[str]) -> int:
    if audit_map.scope(repo) is None:
        print(NO_SCOPE)
        return 1
    try:
        import tree_sitter  # noqa: F401, PLC0415 - the parser every language of the map needs
    except ImportError:
        print("tree-sitter is not installed for this Python: run `bash .claude/audit/install.sh`. "
              "The map is not written, and the one in audit/map/ is left as it is.")
        return 1
    prepare(repo, [])
    ctx = audit_map.run(repo)
    print(f"audit/map/: {len(ctx.modules)} modules, {len(ctx.edges)} module edges, "
          f"{len(ctx.siblings)} sibling groups")
    return 0


def plan_describe(repo: Path, _args: list[str]) -> int:
    if not (repo / "audit" / "map" / "modules.md").is_file() and map_(repo, []) != 0:
        return 1
    for note in plans.migrate_describe(repo):
        print(f"migrated: {note}")
    path = plans.write_describe(repo)
    print(f"{path.relative_to(repo).as_posix()}: "
          f"{path.read_text(encoding='utf-8').count('<block id=')} blocks")
    return 0


def _modules(repo: Path, names: list[str]) -> tuple[list, list[str]]:
    """The modules named by path or by key, and the names that are neither."""
    known = plans.read_modules(repo)
    by_name = {m.path: m for m in known} | {m.key: m for m in known}
    return [by_name[n.rstrip("/")] for n in names if n.rstrip("/") in by_name], \
        [n for n in names if n.rstrip("/") not in by_name]


def mark_described(repo: Path, args: list[str]) -> int:
    if not args:
        print("usage: audit.py mark-described <module path or key>…")
        return 2
    modules, unknown = _modules(repo, args)
    problems = [f"{n}: not a module of audit/map/modules.md" for n in unknown]
    problems += plans.mark_described(repo, modules)
    for p in problems:
        print(p)
    if not problems:
        print(f"OK {len(modules)} module(s) marked described")
    return 1 if problems else 0


def unmark_described(repo: Path, args: list[str]) -> int:
    if not args:
        print("usage: audit.py unmark-described <module path or key>…")
        return 2
    modules, unknown = _modules(repo, args)
    problems = [f"{n}: not a module of audit/map/modules.md" for n in unknown]
    problems += plans.unmark_described(repo, modules)
    for p in problems:
        print(p)
    if not problems:
        print(f"OK {len(modules)} module(s) unmarked")
    return 1 if problems else 0


def check_describe(repo: Path, args: list[str]) -> int:
    modules, unknown = _modules(repo, args)
    problems = [f"{n}: not a module of audit/map/modules.md" for n in unknown]
    problems += plans.check_describe(repo, modules if args else None)
    for p in problems:
        print(p)
    if not problems:
        print("OK")
    return 1 if problems else 0


def facts(repo: Path, _args: list[str]) -> int:
    if not (repo / "audit" / "describe" / "architecture.md").is_file():
        print("audit/describe/architecture.md is missing: the description comes first.")
        return 1
    problems = plans.check_describe(repo)
    if problems:
        print("the description is not complete — plan-describe again:")
        for p in problems:
            print(f"  {p}")
        return 1
    counts = plans.write_facts(repo)
    print(f"audit/map/facts/B1.json: {counts['B1']} items; "
          f"audit/map/capabilities.md: {counts['capabilities']} capabilities")
    return 0


def check(repo: Path, args: list[str]) -> int:
    if len(args) != 1:
        print("usage: audit.py check <findings or checked file>")
        return 2
    if not plans.CARDS.is_file():
        print(f"the cards are missing: {plans.CARDS}")
        return 1
    path = Path(args[0]).resolve()
    problems = plans.check(repo, path, set(plans.card_ids(plans.CARDS.read_text(encoding="utf-8"))))
    for p in problems:
        print(p)
    if not problems:
        print(f"OK {args[0]}")
    return 1 if problems else 0


def checked(repo: Path, _args: list[str]) -> int:
    items = plans.checked_items(repo)
    for item in sorted(items, key=lambda item: not item.valid):
        print(f"valid {item.id} — {item.case} — {', '.join(item.places)}" if item.valid
              else f"stale {item.id} — {item.reason}")
    if not items:
        print("no withdrawn item")
    return 0


COMMANDS = {"prepare": prepare, "scope": scope, "map": map_, "plan-describe": plan_describe,
            "mark-described": mark_described, "unmark-described": unmark_described,
            "check-describe": check_describe, "facts": facts, "check": check,
            "checked": checked}


def _audit_venv(repo: Path, argv: list[str]) -> None:
    """Run again with `audit/.tools/venv`'s Python and tools when it exists and is not this one."""
    venv = repo / "audit" / ".tools" / "venv"
    bindir = venv / ("Scripts" if os.name == "nt" else "bin")
    python = bindir / ("python.exe" if os.name == "nt" else "python")
    if not python.is_file() or Path(sys.prefix).resolve() == venv.resolve():
        return
    env = dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")
    os.execve(str(python), [str(python), str(Path(__file__).resolve()), *argv], env)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    _audit_venv(Path.cwd(), argv)
    return COMMANDS[argv[0]](Path.cwd(), argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
