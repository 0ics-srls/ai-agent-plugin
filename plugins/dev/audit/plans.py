#!/usr/bin/env python3
"""What the audit's tool writes for the agent, after the map:
- `audit/plan-describe.md`: the Step plan that describes every module — what it does, its role in the
  architecture the project gave itself, the mechanisms that govern it — and then the architecture;
- the facts that need the description (`write_facts`): B1, the module edges against the layers it
  found, and `audit/map/capabilities.md`, every capability of every module;
- `check`: the form of a findings file, or of a checked file;
- `checked_items`: the withdrawn items of `audit/checked/`, each still valid or stale, and why.

The verification itself is the agent's (`x-audit-code` step 4): it reads the map against the cards.

Every block id is new to the project — the planexecutor skips an id an earlier plan completed
(`.cvm/uplan-progress.json`) — because it carries the label of the run that wrote it.
"""

from __future__ import annotations

import collections
import csv
import datetime
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from map import _module_path, item

SET_ROOT = Path(__file__).resolve().parent.parent  # .claude
NAVIGATION = SET_ROOT / "commands" / "mind-sets" / "code-navigation.md"
PROTOCOL_D = ("If an action or a criterion fails, the cause is found with Protocol D — "
              "`.claude/commands/mind-sets/debug-protocol.md`, read in full — before any change.")
GROUP_LIMIT = 40  # the types of the modules one describe block reads
CARDS = SET_ROOT / "commands" / "mind-sets" / "audit.md"


@dataclass
class Block:
    slug: str
    title: str
    intro: str
    actions: list[str]
    success: list[str]
    depends: str = "no dependencies"


@dataclass
class Module:
    key: str
    path: str
    files: list[str]
    types: int


# ---- shared: the form of a plan ----------------------------------------------------------------

def run_label() -> str:
    """The label of this run, in every block id: an id is new to the project, whatever ran before."""
    return "r" + datetime.datetime.now().strftime("%y%m%d%H%M")


def block_id(index: int, label: str, block_slug: str) -> str:
    """`NN-kebab-case`, as the CVM parser requires: NN is the position in the plan, two digits; the
    label of the run and the slug make the id unique."""
    return f"{index % 99 + 1:02d}-{label}-{block_slug}"


def slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-") or "root"


def write_plan(path: Path, title: str, mission: str, blocks: list[Block], label: str) -> Path:
    ids = [block_id(i, label, b.slug) for i, b in enumerate(blocks)]
    parts = [f"# Step Plan: {title}", "", "<mission>", mission.strip(), "</mission>", ""]
    for n, (bid, b) in enumerate(zip(ids, blocks), 1):
        parts += [f'<block id="{bid}">', f"## Step {n}: {b.title}", "", "<intro>", b.intro.strip(),
                  "</intro>", "", "<actions>", *[f"- action: {a}" for a in b.actions],
                  "</actions>", "", PROTOCOL_D, "", "<success>",
                  *[f"- [ ] {s}" for s in b.success], "</success>", "</block>", ""]
    width = max(len(i) for i in ids)
    parts += ["## Execution Order"]
    parts += [f"{bid.ljust(width)}   → {b.depends}" for bid, b in zip(ids, blocks)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return path


def navigation_rules() -> str:
    """The PREFLIGHT and the discipline of code-navigation.md, as the set writes them."""
    text = NAVIGATION.read_text(encoding="utf-8")
    start = text.index("## GATE")
    end = text.index("## Indexer blind spots")
    return text[start:end].strip()


NOTHING_FROM_MEMORY = (
    "**Nothing from memory.** Every claim is confirmed from code read in this session: the "
    "project's code with the navigation tool, a dependency's code in the version the project "
    "references (`@code-nav-external`, or its source). What is known about a framework without "
    "reading it is not evidence.")


# ---- the describe plan -------------------------------------------------------------------------

def read_modules(repo: Path) -> list[Module]:
    out = []
    table = (repo / "audit" / "map" / "modules.md").read_text(encoding="utf-8")
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in ("Module", "---") or cells[0].startswith("-"):
            continue
        shape = (repo / "audit" / "map" / "shape" / f"{cells[0]}.md").read_text(encoding="utf-8")
        files = [x[3:] for x in shape.splitlines() if x.startswith("## ")]
        types = sum(1 for x in shape.splitlines() if x.startswith("- "))
        out.append(Module(cells[0], cells[1], files, types))
    return out


def _git(repo: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=repo,
                           capture_output=True, text=True, check=False)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def _changed_since(repo: Path, record: Path, files: list[str]) -> str:
    """Why the record no longer holds for the files — `not committed` (no commit, or modified since), or
    `changed: <paths>`, the files changed or new since its last commit; empty when it holds."""
    rel = record.relative_to(repo).as_posix()
    commit = (_git(repo, "log", "-1", "--format=%H", "--", rel) or "").strip()
    if not commit or _git(repo, "status", "--porcelain", "--", rel):
        return "not committed"
    changed = _git(repo, "diff", "--name-only", commit, "--", *files)
    if changed is None:
        return "changed: git does not answer"
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard", "--", *files) or ""
    paths = sorted(set(changed.splitlines() + untracked.splitlines()))
    return f"changed: {', '.join(paths)}" if paths else ""


def _unchanged_since(repo: Path, record: Path, files: list[str]) -> bool:
    """The record is committed and clean, and none of the files changed since its commit."""
    return not _changed_since(repo, record, files)


# One file per module, named by its key: `audit/describe/<key>.md`, one section `## <module path>`,
# its second line the fingerprint of the module's files when its description was last written or
# confirmed — written by `mark-described`, never by hand.
SOURCE = re.compile(r"^Source: ([0-9a-f]{16}) \(\d+ files?\)$", re.M)


def describe_dir(repo: Path) -> Path:
    return repo / "audit" / "describe"


def describe_file(repo: Path, m: Module) -> Path:
    return describe_dir(repo) / f"{m.key}.md"


def fingerprint(repo: Path, m: Module) -> str:
    """The module's files as they are now — the ones its shape lists, their bytes."""
    h = hashlib.sha256()
    for rel in sorted(m.files):
        h.update(rel.encode() + b"\0")
        f = repo / rel
        h.update(f.read_bytes() if f.is_file() else b"<missing>")
        h.update(b"\0")
    return h.hexdigest()[:16]


def _module_sections(text: str) -> list[tuple[str, str]]:
    """`## <heading>` → its text, the heading line included."""
    parts = re.split(r"^(?=## )", text, flags=re.M)
    return [(p.splitlines()[0][3:].strip(), p) for p in parts if p.startswith("## ")]


def described_unchanged(repo: Path, m: Module) -> bool:
    """The module's file holds its section, and the fingerprint written there is the one of its files
    now: the description was written, or confirmed, for this very code."""
    f = describe_file(repo, m)
    if not f.is_file():
        return False
    found = SOURCE.search(f.read_text(encoding="utf-8"))
    return bool(found) and found.group(1) == fingerprint(repo, m)


def mark_described(repo: Path, modules: list[Module]) -> list[str]:
    """Write in each module's file the fingerprint of its files: its description holds for them."""
    problems = []
    for m in modules:
        f = describe_file(repo, m)
        if not f.is_file():
            problems.append(f"{m.path}: no {f.relative_to(repo).as_posix()} — describe it first")
            continue
        text = f.read_text(encoding="utf-8")
        line = f"Source: {fingerprint(repo, m)} ({len(m.files)} file{'s' if len(m.files) != 1 else ''})"
        if SOURCE.search(text):
            text = SOURCE.sub(line, text, count=1)
        else:
            head = f"## {m.path}\n"
            if not text.startswith(head):
                problems.append(f"{m.path}: {f.name} does not open with `## {m.path}`")
                continue
            text = head + line + "\n" + text[len(head):]
        f.write_text(text, encoding="utf-8")
    return problems


def unmark_described(repo: Path, modules: list[Module]) -> list[str]:
    """Remove from each module's file the fingerprint of its files: its description no longer holds,
    and the next describe plan writes it again."""
    problems = []
    for m in modules:
        f = describe_file(repo, m)
        if not f.is_file():
            problems.append(f"{m.path}: no {f.relative_to(repo).as_posix()}")
            continue
        text = f.read_text(encoding="utf-8")
        if not SOURCE.search(text):
            problems.append(f"{m.path}: no fingerprint to remove")
            continue
        lines = [x for x in text.split("\n") if not SOURCE.fullmatch(x)]
        f.write_text("\n".join(lines), encoding="utf-8")
    return problems


def check_describe(repo: Path, only: list[Module] | None = None) -> list[str]:
    """Every module (or the ones named) has exactly one section, `## <path>` in `<key>.md`, with the
    fingerprint of its files now; no description file belongs to something that is not a module."""
    modules = read_modules(repo)
    by_path = {m.path: m for m in modules}
    keys = {m.key for m in modules}
    where: dict[str, list[str]] = collections.defaultdict(list)
    problems = []
    for f in sorted(describe_dir(repo).glob("*.md")):
        if f.name == "architecture.md":
            continue
        if f.stem not in keys:
            problems.append(f"audit/describe/{f.name}: not the file of a module of modules.md")
        for heading, _ in _module_sections(f.read_text(encoding="utf-8")):
            where[heading].append(f.name)
    for m in only if only is not None else modules:
        files = where.get(m.path, [])
        if not files:
            problems.append(f"{m.path}: no section `## {m.path}` in audit/describe/")
        elif len(files) > 1:
            problems.append(f"{m.path}: a section in more than one file: {', '.join(files)}")
        elif files[0] != f"{m.key}.md":
            problems.append(f"{m.path}: its section is in {files[0]}, not in {m.key}.md")
        elif not SOURCE.search((describe_dir(repo) / files[0]).read_text(encoding="utf-8")):
            problems.append(f"{m.path}: no fingerprint — `audit.py mark-described {m.path}` once its "
                            f"description is written or confirmed")
        elif not described_unchanged(repo, m):
            problems.append(f"{m.path}: its files changed since the description was written or "
                            f"confirmed — `audit.py mark-described {m.path}` once it is read again")
    if only is None:
        problems += [f"audit/describe/: `## {h}` is not a module of modules.md"
                     for h in sorted(where) if h not in by_path]
    return problems


def _last_commit_time(repo: Path, f: Path) -> int:
    out = (_git(repo, "log", "-1", "--format=%ct", "--", f.relative_to(repo).as_posix()) or "").strip()
    return int(out) if out else 0


def migrate_describe(repo: Path) -> list[str]:
    """The earlier layout — one file per group of modules — brought to one file per module. First every
    section of every file is collected, then each module is written in its own file once, so no section
    depends on the order the files are read in. A module with two copies keeps the one in its own file,
    else the one of the file committed last. A section with no fingerprint whose old file was committed
    with none of the module's files changed since keeps its validity: its fingerprint is written. A
    section of what is no longer a module is dropped. Run again, it changes nothing."""
    d = describe_dir(repo)
    if not d.is_dir():
        return []
    modules = {m.path: m for m in read_modules(repo)}
    files = [f for f in sorted(d.glob("*.md")) if f.name != "architecture.md"]
    copies: dict[str, list[tuple[Path, str]]] = collections.defaultdict(list)
    for f in files:
        for heading, body in _module_sections(f.read_text(encoding="utf-8")):
            copies[heading].append((f, body.rstrip("\n") + "\n"))
    notes, chosen = [], {}
    for heading, found in sorted(copies.items()):
        m = modules.get(heading)
        if m is None:
            notes.append(f"dropped `## {heading}` ({found[0][0].name}): not a module of modules.md")
            continue
        own = [c for c in found if c[0] == describe_file(repo, m)]
        source, body = (own or sorted(found, key=lambda c: _last_commit_time(repo, c[0]), reverse=True))[0]
        if len(found) > 1:
            notes.append(f"{heading}: {len(found)} copies, the one in {source.name} kept")
        chosen[m.path] = (source, body)
    valid = {path: not SOURCE.search(body) and _unchanged_since(repo, source, modules[path].files)
             for path, (source, body) in chosen.items()}
    targets = {describe_file(repo, modules[path]) for path in chosen}
    for f in files:
        if f not in targets:
            f.unlink()
            notes.append(f"removed {f.name}: its sections are in the files of their modules")
    for path, (source, body) in chosen.items():
        target = describe_file(repo, modules[path])
        if not target.is_file() or target.read_text(encoding="utf-8") != body:
            target.write_text(body, encoding="utf-8")
            notes.append(f"{path}: {source.name} → {target.name}")
        if valid[path]:
            mark_described(repo, [modules[path]])
            notes.append(f"{path}: unchanged since its description was committed, fingerprint written")
    return notes


def pack(modules: list[Module], limit: int) -> list[list[Module]]:
    """A module alone when it has more than `limit` types; else modules together up to it."""
    groups, current, size = [], [], 0
    for m in modules:
        if m.types > limit:
            groups.append([m])
            continue
        if current and size + m.types > limit:
            groups.append(current)
            current, size = [], 0
        current.append(m)
        size += m.types
    if current:
        groups.append(current)
    return groups


def describe_mission(repo: Path) -> str:
    return f"""
## What this plan is for

The code audit of this project (`/x-audit-code`) measures the code against the rules of the set
and against the architecture the project gave itself. This plan writes the description the
verification stands on: what each module does, the role it has in that architecture, the
mechanisms that govern it. It describes; it judges nothing.

The map is in `audit/map/` (`python3 .claude/audit/audit.py map` wrote it): `modules.md`, the shape
of each module in `shape/<module>.md` (types and signatures, no bodies), `graph.md`, `siblings.md`.
The sources of a role: the project's structure, its documents (README, `docs/`), the Memory Bank's
`systemPatterns.md` when there is one.

## What the blocks write

`audit/describe/<module key>.md` — one file per module, named by its key in `audit/map/modules.md`,
holding that module's section only:

```
## <module path>
Source: <written by `audit.py mark-described`, never by hand>
Role: <role> — from <source>
### Capabilities
- <what it does> — <path>:<symbol>
### Mechanisms
- <the mechanism: a state machine, a strategy, a pipeline, a framework's lifecycle> — <path>:<symbol>
```

A capability is said by what it does («computes the lift of a wing»), not by the name of the type.
`Mechanisms` is `none` when the module has none.

A block writes the files of its own modules and no other. A module whose file is there and whose
description is still true of the code read — a change of form, a rename that changes nothing said —
keeps its text as it is: `mark-described` records that it was confirmed, which is what takes it out of
the next plan.

`audit/describe/architecture.md`:

```
## Layers
- <layer>: <module>, <module>
```

from the layer nothing depends on to the outermost, or `none` for a project without layers.

## Rules

- {NOTHING_FROM_MEMORY}
- A symbol cited exists: it was found with the navigation tool in the block that cites it.
- Nothing outside `audit/` is written. The project's gate is not run here: the user runs it.

## The navigation — from `.claude/commands/mind-sets/code-navigation.md`

{navigation_rules()}

## Commands

- The map, when it is missing: `python3 .claude/audit/audit.py map`.
- A module described or confirmed: `python3 .claude/audit/audit.py mark-described <module path>…`.
- The descriptions as they must be: `python3 .claude/audit/audit.py check-describe [<module path>…]`
  → `OK`, or each module that has no section, two, one in another file, or a fingerprint not current.
"""


def describe_block(group: list[Module]) -> Block:
    outs = ", ".join(f"`audit/describe/{m.key}.md`" for m in group)
    shapes = ", ".join(f"`audit/map/shape/{m.key}.md`" for m in group)
    paths = ", ".join(f"`{m.path}`" for m in group)
    plain = " ".join(m.path for m in group)
    return Block(
        slug=f"describe-{slug(group[0].key)}",
        title=f"Describe {', '.join(m.path for m in group)}",
        intro=f"No precondition. Describes the modules {paths}: their shape is in {shapes}, their "
              f"code under those folders. Writes {outs}, one file per module, in the format of the "
              "mission, and no other file of `audit/describe/`.",
        actions=[
            "Print the CODE-NAV PREFLIGHT block of the mission, filled, before the first lookup.",
            f"Read {shapes} and `audit/map/graph.md`; and each module's file in `audit/describe/` "
            "when it is there.",
            "For each module, read with the navigation tool the types whose work the names do "
            "not say, and the project's documents that speak of it (README, `docs/`, "
            "`memory-bank/systemPatterns.md`).",
            f"Write each module's file, {outs}: its section `## <module path>` with `Role:`, "
            "`### Capabilities` and `### Mechanisms` as the mission shows. A file whose description "
            "is still true of the code read is left as it is.",
            f"Run `python3 .claude/audit/audit.py mark-described {plain}`.",
            f"Run `python3 .claude/audit/audit.py check-describe {plain}`.",
        ],
        success=[
            f"`python3 .claude/audit/audit.py check-describe {plain}` prints `OK`",
            "each section has a `Role: … — from …` line, `### Capabilities` and `### Mechanisms`",
            "every capability cites a `<path>:<symbol>` of its module, found with the navigation "
            "tool in this block (the queries are in this block's output)",
        ])


def architecture_block(depends: str) -> Block:
    return Block(
        slug="describe-architecture",
        title="Describe the architecture the project gave itself",
        intro="After the describe blocks. Reads `audit/describe/*.md` and `audit/map/graph.md`, "
              "and the project's documents on its architecture. Writes "
              "`audit/describe/architecture.md`, in the format of the mission.",
        actions=[
            "Read every `audit/describe/*.md` and `audit/map/graph.md`.",
            "Read the project's documents that state its architecture (README, `docs/`, "
            "`memory-bank/systemPatterns.md`), when there are any.",
            "Write `audit/describe/architecture.md`: `## Layers`, one line per layer from the one "
            "nothing depends on, or `none`.",
        ],
        success=[
            "`python3 .claude/audit/audit.py check-describe` prints `OK`: every module of "
            "`audit/map/modules.md` has its one section, current",
            "`audit/describe/architecture.md` has `## Layers` and, under it, every module of "
            "`audit/map/modules.md` in exactly one layer, or the single line `none`",
            "each layer's place in the order is the one the documents state, or, without them, "
            "the one `audit/map/graph.md` shows",
        ],
        depends=depends)


def write_describe(repo: Path, group_limit: int = GROUP_LIMIT, label: str | None = None) -> Path:
    label = label or run_label()
    migrate_describe(repo)
    modules = [m for m in read_modules(repo) if not described_unchanged(repo, m)]
    groups = pack(modules, group_limit)
    blocks = [describe_block(g) for g in groups]
    ids = [block_id(i, label, b.slug) for i, b in enumerate(blocks)]
    blocks.append(architecture_block(f"depends on {', '.join(ids)}" if ids else "no dependencies"))
    return write_plan(repo / "audit" / "plan-describe.md", "describe the project",
                      describe_mission(repo), blocks, label)


# ---- the facts that need the description ------------------------------------------------------

def card_ids(cards: str) -> list[str]:
    ids = re.findall(r"^### ([A-O]\d+)\. ", cards, re.M)
    ids += re.findall(r"^\| ([A-O]\d+) \|", cards, re.M)
    return sorted(set(ids), key=lambda c: (c[0], int(c[1:])))


def b1_against_layers(repo: Path) -> list[dict]:
    """The module edges against the order of the layers the description found, and the cycles."""
    arch = repo / "audit" / "describe" / "architecture.md"
    try:
        text = arch.read_text(encoding="utf-8").split("## Layers", 1)[1]
    except (OSError, IndexError):
        return []
    layer_of = {}
    for i, m in enumerate(re.finditer(r"^- [^:\n]+:\s*(.+)$", text, re.M)):
        for mod in m.group(1).split(","):
            layer_of[mod.strip()] = i
    graph = (repo / "audit" / "map" / "graph.md").read_text(encoding="utf-8")
    table, _, cycles = graph.partition("## Cycles")
    files = collections.defaultdict(set)
    deps_csv = repo / "audit" / ".tools" / "graph" / "deps.csv"
    if deps_csv.is_file():
        with deps_csv.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                files[(_module_path(r["from"]), _module_path(r["to"]))].add(r["from"])
    out = []
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("From", "---"):
            continue
        a, b = cells[0], cells[1]
        if a in layer_of and b in layer_of and layer_of[b] > layer_of[a]:
            out.append(item("B1", sorted(files.get((a, b), {a})),
                            {"kind": "against", "from": a, "to": b}))
    for line in cycles.strip().splitlines():
        if line.strip() and line.strip() != "none":
            mods = [x.strip() for x in line.split("<->")]
            out.append(item("B1", mods, {"kind": "cycle", "modules": mods}))
    return out


def descriptions(repo: Path) -> dict[str, dict]:
    """module → its Role line and its capabilities, from `audit/describe/`."""
    out = {}
    for f in sorted((repo / "audit" / "describe").glob("*.md")):
        if f.name == "architecture.md":
            continue
        for sec in re.split(r"^## ", f.read_text(encoding="utf-8"), flags=re.M)[1:]:
            head, _, body = sec.partition("\n")
            role = re.search(r"^Role:\s*(.+)$", body, re.M)
            caps = body.split("### Capabilities", 1)[1].split("###", 1)[0] if \
                "### Capabilities" in body else ""
            out[head.strip()] = {"role": role.group(1) if role else "",
                                 "capabilities": [x[2:].strip() for x in caps.splitlines()
                                                  if x.startswith("- ")]}
    return out


def write_capabilities(repo: Path, described: dict[str, dict]) -> Path:
    rows = [f"| {mod} | {cap.split(' — ')[0]} | {cap.split(' — ')[1] if ' — ' in cap else ''} |"
            for mod in sorted(described) for cap in described[mod]["capabilities"]]
    path = repo / "audit" / "map" / "capabilities.md"
    path.write_text("# Capabilities\n\nEvery capability of every module, as the description says "
                    "it.\n\n| Module | Capability | Where |\n|---|---|---|\n" + "\n".join(rows)
                    + "\n", encoding="utf-8")
    return path


def write_facts(repo: Path) -> dict[str, int]:
    """B1 against the layers `audit/describe/architecture.md` found, and the capability table."""
    b1 = b1_against_layers(repo)
    facts = repo / "audit" / "map" / "facts"
    facts.mkdir(parents=True, exist_ok=True)
    (facts / "B1.json").write_text(json.dumps({"card": "B1", "items": b1}, indent=1, sort_keys=True)
                                   + "\n", encoding="utf-8")
    described = descriptions(repo)
    write_capabilities(repo, described)
    return {"B1": len(b1), "capabilities": sum(len(d["capabilities"]) for d in described.values())}


# ---- the check of a findings file, or of a checked file ----------------------------------------

FINDING = re.compile(r"^### (?P<card>\S+) — (?P<line>.+)$", re.M)
CHECKED = re.compile(r"^### (?P<id>[A-O]\d+-\S+) — not a violation: (?P<case>\S.*)$")
GRAVITY_NAMES = frozenset({"grave", "da correggere"})
PLACE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.\w+):(\d+)\b")


def _sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^(?=### )", text, flags=re.M)
    return [(p.splitlines()[0], p) for p in parts if p.startswith("### ")]


def missing_lines(repo: Path, text: str) -> list[str]:
    """Every `path:line` the text cites names a file of the project and a line it has."""
    out = []
    for m in PLACE.finditer(text):
        rel, line = m.group(1), int(m.group(2))
        f = repo / rel
        if not f.is_file():
            out.append(f"{rel}:{line}: no such file")
            continue
        with f.open(encoding="utf-8", errors="replace") as fh:
            count = sum(1 for _ in fh)
        if line < 1 or line > count:
            out.append(f"{rel}:{line}: the file has {count} lines")
    return out


def check(repo: Path, path: Path, cards: set[str]) -> list[str]:
    """What is wrong with a findings file, or with a checked file (`audit/checked/`)."""
    text = path.read_text(encoding="utf-8")
    if text.strip() == "none":
        return []
    problems = []
    if path.parent.name == "checked":
        for head, body in _sections(text):
            if not CHECKED.match(head):
                problems.append(f"{head}: not `### <item id> — not a violation: <case>`")
            elif not re.search(r"^- Places:\s*\S", body, re.M):
                problems.append(f"{head}: no `- Places:`")
        return problems + missing_lines(repo, text)
    for head, body in _sections(text):
        m = FINDING.match(head)
        if m is None:
            problems.append(f"{head}: not `### <CARD> — <one line>`")
            continue
        if m["card"] not in cards:
            problems.append(f"{head}: {m['card']} is not a card")
        for name in ("Rule", "Where", "Evidence"):
            if not re.search(rf"^- {name}:\s*\S", body, re.M):
                problems.append(f"{head}: no `- {name}:`")
        g = re.search(r"^- Gravity:\s*(.+?)\s*$", body, re.M)
        if g is None or g.group(1) not in GRAVITY_NAMES:
            problems.append(f"{head}: the gravity is `grave` or `da correggere`")
    if not _sections(text):
        problems.append(f"{path.name}: no section, and not `none`")
    return problems + missing_lines(repo, text)


@dataclass
class CheckedItem:
    id: str
    case: str
    places: list[str]
    reason: str  # why it is stale; empty when it still holds

    @property
    def valid(self) -> bool:
        return not self.reason


def _places(body: str) -> list[str]:
    line = re.search(r"^- Places:\s*(\S.*)$", body, re.M)
    return [f"{p}:{n}" for p, n in PLACE.findall(line.group(1))] if line else []


def checked_items(repo: Path) -> list[CheckedItem]:
    """Every withdrawn item of `audit/checked/`, and whether it still holds: its record committed and
    clean, none of the files of its places changed since."""
    out = []
    for f in sorted((repo / "audit" / "checked").glob("*.md")):
        for head, body in _sections(f.read_text(encoding="utf-8")):
            m = CHECKED.match(head)
            if m is None:
                continue  # `check` reports a heading out of form
            places = _places(body)
            files = sorted({p.rsplit(":", 1)[0] for p in places})
            reason = _changed_since(repo, f, files) if files else "no places"
            out.append(CheckedItem(m["id"], m["case"], places, reason))
    return out
