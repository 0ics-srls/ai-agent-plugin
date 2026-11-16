#!/usr/bin/env python3
"""The map of the project, computed in seconds on the whole of it: where to look, never a verdict.

A named pipeline (STEPS): each step reads the context the previous ones filled and adds to it. It
writes `audit/map/` and nothing outside `audit/`:
- `modules.md`: every folder of the project's own code that holds code files directly, with its
  language and its number of files. A folder, not a build project: two maps of one game are one
  Godot project and two folders, and the folders are what a subsystem rewritten per unit shows up
  in;
- `shape/<module>.md`: the types and the method signatures of each file, no bodies;
- `graph.md`: which module refers to which, and the cycles;
- `siblings.md`: the modules of one parent folder that declare the same type or method names, and
  the modules they all depend on;
- `facts/<CARD>.json`: the places each card with a computable fact points at (`CARD_FACTS`);
- `coverage.md`: what was computed, for which languages, and what was not, with why.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import deps
import history
import oo_build
import oo_extract
import principles
import similar
import solid
import solid_config
from oo_model import FactBase, FileFacts

STEPS = ("modules", "shape", "graph", "siblings", "facts", "coverage")
ROOT_MODULE = "."
SIMILARITY, LEXICAL, MIN_TOKENS = 0.70, 0.50, 50  # similar.py's: which units are compared at all
READ_FIRST = 10  # C1: how many functions of a module are named to be read first
STATE_TYPES = frozenset({"bool", "boolean", "Bool", "string", "String", "str", "&str"})


@dataclass
class Module:
    path: str                       # the folder, relative to the project root; "." for the root
    files: list[str] = field(default_factory=list)
    langs: list[str] = field(default_factory=list)  # most files first

    @property
    def key(self) -> str:
        """The name of its shape file."""
        return "_root" if self.path == ROOT_MODULE else self.path.replace("/", "-")


@dataclass
class Context:
    repo: Path
    out: Path
    roots: list[str]
    lang_of: dict[str, str] = field(default_factory=dict)      # code file → its language
    uncovered: dict[str, int] = field(default_factory=dict)    # extension → files not examined
    uninstalled: dict[str, int] = field(default_factory=dict)  # extension → files, grammar missing
    missing_grammars: list[str] = field(default_factory=list)
    modules: dict[str, Module] = field(default_factory=dict)
    facts: dict[str, FileFacts] = field(default_factory=dict)  # file → its object facts
    base: FactBase | None = None
    edges: dict[tuple[str, str], int] = field(default_factory=dict)
    cycles: list[list[str]] = field(default_factory=list)
    deps_of: dict[str, set[str]] = field(default_factory=dict)
    siblings: list[tuple[str, list[str], list[str], list[str]]] = field(default_factory=list)
    changes: list | None = None  # history.method_changes, None outside git
    not_computed: dict[str, str] = field(default_factory=dict)  # card → why

    @property
    def tools(self) -> Path:
        return self.repo / "audit" / ".tools"


class NotComputed(Exception):
    """A card's fact could not be computed here: the reason goes to coverage.md."""


def own_roots(repo: Path) -> list[str]:
    """`@own-code-roots` of `j-settings.md`, or the whole project without it: what `scope` shows the user
    to choose from."""
    try:
        text = (repo / "j-settings.md").read_text(encoding="utf-8")
    except OSError:
        return ["."]
    m = re.search(r"^@own-code-roots:\s*(.+)$", text, re.MULTILINE)
    roots = [r.strip().strip("/") or "." for r in m.group(1).split(",")] if m else []
    roots = [r for r in roots if r and not r.startswith(("{", "none")) and (repo / r).is_dir()]
    return roots or ["."]


# What the audit examines is said once, by the user, in `audit/scope.md`: one line `- <folder>` per
# folder. It is not `@own-code-roots`: that key says where the navigation searches — proofs of concept,
# the base library, tools — and a folder searched is not a folder judged.
def scope_file(repo: Path) -> Path:
    return repo / "audit" / "scope.md"


def scope(repo: Path) -> list[str] | None:
    """The folders the audit examines, or None when nobody said them yet."""
    try:
        text = scope_file(repo).read_text(encoding="utf-8")
    except OSError:
        return None
    return [line[2:].strip() for line in text.splitlines() if line.startswith("- ")] or None


def write_scope(repo: Path, folders: list[str]) -> list[str]:
    """Write the scope, or say which of the folders the project does not have."""
    roots = [f.strip().rstrip("/") or "." for f in folders]
    problems = [f"{r}: not a folder of the project" for r in roots if not (repo / r).is_dir()]
    if problems:
        return problems
    lines = ["# What this audit examines", "", *[f"- {r}" for r in roots], ""]
    _write(scope_file(repo), "\n".join(lines))
    return []


STALE_WITH_THE_MAP = ("map", "plan-describe.md", "plan-verify.md", "candidates.md")


def mapped_roots(repo: Path) -> list[str] | None:
    """The folders the map in `audit/map/` was made of (`coverage.md`), or None without a map."""
    try:
        text = (repo / "audit" / "map" / "coverage.md").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"^Roots: (.+)$", text, re.MULTILINE)
    return [r.strip() for r in m.group(1).split(",")] if m else None


def drop_stale(repo: Path) -> list[str]:
    """Remove the map made of other folders than the scope, and what was made from it — the plans, the
    candidates; the descriptions stay, each valid for its module's files. What was removed, as paths."""
    made_of = mapped_roots(repo)
    if made_of is None or sorted(made_of) == sorted(scope(repo) or []):
        return []
    removed = []
    for name in STALE_WITH_THE_MAP:
        path = repo / "audit" / name
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(f"audit/{name}/")
        elif path.is_file():
            path.unlink()
            removed.append(f"audit/{name}")
    return removed


def run(repo: Path) -> Context:
    ctx = Context(repo=repo, out=repo / "audit" / "map", roots=scope(repo) or ["."])
    for step in STEPS:
        globals()[f"step_{step}"](ctx)
    return ctx


def _module_path(rel: str) -> str:
    parent = str(PurePosixPath(rel).parent)
    return ROOT_MODULE if parent in ("", ".") else parent


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_name(t) -> str:
    """The name a reader knows a type by: a GDScript without class_name is named by its file, the
    PascalCase of the file's stem as Godot's style guide writes it; elsewhere the last segment."""
    name = t.full_name
    if "/" in name:
        return "".join(w.capitalize() for w in PurePosixPath(name).name.split("_"))
    return re.split(r"\.|::", name)[-1]


# ---- the steps ---------------------------------------------------------------------------------

def step_modules(ctx: Context) -> None:
    files = deps.source_files(ctx.repo, ctx.roots)
    by_ext, ctx.missing_grammars, missing_exts = deps.adapter_table(files)
    uncovered: collections.Counter[str] = collections.Counter()
    uninstalled: collections.Counter[str] = collections.Counter()
    for f in files:
        rel = f.relative_to(ctx.repo).as_posix()
        ext = f.suffix.lower()
        if ext in by_ext:
            ctx.lang_of[rel] = by_ext[ext].lang
        elif ext in missing_exts:
            uninstalled[ext] += 1
        elif ext in deps.KNOWN_UNCOVERED:
            uncovered[ext] += 1
    ctx.uncovered = dict(sorted(uncovered.items()))
    ctx.uninstalled = dict(sorted(uninstalled.items()))
    for rel in sorted(ctx.lang_of):
        ctx.modules.setdefault(_module_path(rel), Module(_module_path(rel))).files.append(rel)
    for m in ctx.modules.values():
        count = collections.Counter(ctx.lang_of[f] for f in m.files)
        m.langs = [lang for lang, _ in sorted(count.items(), key=lambda kv: (-kv[1], kv[0]))]
    rows = [f"| {m.key} | {m.path} | {', '.join(m.langs)} | {len(m.files)} |"
            for m in sorted(ctx.modules.values(), key=lambda m: m.path)]
    _write(ctx.out / "modules.md", "# Modules\n\nEvery folder of the project's own code that holds "
           "code files directly.\n\n| Module | Path | Language | Files |\n|---|---|---|---|\n"
           + "\n".join(rows) + "\n")


def step_shape(ctx: Context) -> None:
    by_ext, _, _ = deps.adapter_table([ctx.repo / f for f in ctx.lang_of])
    for rel, lang in ctx.lang_of.items():
        if lang not in oo_extract.EXTRACTORS:
            continue
        adapter = by_ext[PurePosixPath(rel).suffix.lower()]
        ctx.facts[rel] = oo_extract.extract_file(adapter, (ctx.repo / rel).read_bytes(), rel,
                                                 tuple(ctx.roots))
    tests = {rel for rel in ctx.facts if deps.is_test_path(rel)}
    ctx.base = oo_build.build_fact_base(list(ctx.facts.values()), tests)
    shape_dir = ctx.out / "shape"
    for old in shape_dir.glob("*.md") if shape_dir.is_dir() else ():
        old.unlink()
    for m in ctx.modules.values():
        lines = [f"# {m.path}", ""]
        for rel in m.files:
            lines.append(f"## {rel}")
            ff = ctx.facts.get(rel)
            if ff is None:
                lines += [f"- not extracted: {ctx.lang_of[rel]}", ""]
                continue
            for t in sorted(ff.types, key=lambda t: (t.line, t.full_name)):
                bases = f" : {', '.join(t.bases)}" if t.bases else ""
                lines.append(f"- {t.kind} {display_name(t)}{bases}")
                lines += [f"  - {x.name}({x.arity})" for x in sorted(
                    (x for x in ff.methods if x.owner == t.full_name), key=lambda x: (x.line, x.name))]
            free = sorted((x for x in ff.methods if x.owner not in {t.full_name for t in ff.types}),
                          key=lambda x: (x.line, x.name))
            lines += [f"- function {x.name}({x.arity})" for x in free]
            lines.append("")
        _write(shape_dir / f"{m.key}.md", "\n".join(lines))


def step_graph(ctx: Context) -> None:
    tools = ctx.repo / "audit" / ".tools"
    work = tools / "graph"
    deps.collect_deps(ctx.repo, work, tools, ctx.roots,
                      lambda rel, _roots, _depth: _module_path(rel), set(), 0)
    edges: collections.Counter[tuple[str, str]] = collections.Counter()
    with (work / "deps.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            a, b = _module_path(row["from"]), _module_path(row["to"])
            if a != b and a in ctx.modules and b in ctx.modules:
                edges[(a, b)] += 1
    ctx.edges = dict(sorted(edges.items()))
    for (a, b) in ctx.edges:
        ctx.deps_of.setdefault(a, set()).add(b)
    nodes = {n for e in ctx.edges for n in e}
    ctx.cycles = deps.tarjan(nodes, ctx.deps_of)
    rows = [f"| {a} | {b} | {n} |" for (a, b), n in ctx.edges.items()]
    cycles = [" <-> ".join(c) for c in ctx.cycles] or ["none"]
    _write(ctx.out / "graph.md", "# Graph\n\nWhich module refers to which, with the number of file "
           "references.\n\n| From | To | Edges |\n|---|---|---|\n" + "\n".join(rows)
           + ("\n" if rows else "") + "\n## Cycles\n\n" + "\n".join(cycles) + "\n")


def _names_of(ctx: Context, m: Module) -> set[str]:
    out = set()
    for rel in m.files:
        ff = ctx.facts.get(rel)
        if ff is not None:
            out |= {display_name(t) for t in ff.types}
            out |= {x.name for x in ff.methods if not x.is_ctor and not x.name.startswith("_")}
    return out


def step_siblings(ctx: Context) -> None:
    by_parent: dict[str, list[Module]] = collections.defaultdict(list)
    for m in ctx.modules.values():
        if m.path != ROOT_MODULE:
            by_parent[_module_path(m.path)].append(m)
    names = {m.path: _names_of(ctx, m) for m in ctx.modules.values()}
    for parent in sorted(by_parent):
        mods = sorted(by_parent[parent], key=lambda m: m.path)
        count = collections.Counter(n for m in mods for n in names[m.path])
        shared = sorted(n for n, c in count.items() if c >= 2)
        if len(mods) < 2 or not shared:
            continue
        members = [m.path for m in mods if names[m.path] & set(shared)]
        common = set.intersection(*(ctx.deps_of.get(p, set()) for p in members))
        ctx.siblings.append((parent, members, shared, sorted(common)))
    parts = ["# Siblings\n\nModules of one parent folder that declare the same type or method "
             "names, and the modules they all depend on.\n"]
    for parent, members, shared, common in ctx.siblings:
        parts.append(f"## {parent}\n\n- Modules: {', '.join(members)}\n"
                     f"- Shared names: {', '.join(shared)}\n"
                     f"- Common dependencies: {', '.join(common) or 'none'}\n")
    if not ctx.siblings:
        parts.append("none\n")
    _write(ctx.out / "siblings.md", "\n".join(parts))


def step_facts(ctx: Context) -> None:
    facts_dir = ctx.out / "facts"
    for old in facts_dir.glob("*.json") if facts_dir.is_dir() else ():
        old.unlink()
    for card, compute in CARD_FACTS.items():
        try:
            items = compute(ctx)
        except NotComputed as e:
            ctx.not_computed[card] = str(e)
            continue
        unique = {i["id"]: i for i in reversed(items)}
        doc = {"card": card, "items": sorted(unique.values(), key=lambda i: i["id"])}
        _write(facts_dir / f"{card}.json", json.dumps(doc, indent=1, sort_keys=True) + "\n")


# ---- the facts of the cards: each says where to read, never how much ---------------------------

def _clean(x):
    """A fact carries no measure: every number is dropped from its detail."""
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items() if not _is_number(v)}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x if not _is_number(v)]
    return x


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def item(card: str, places, detail: dict) -> dict:
    places = sorted(set(places))
    key = f"{detail.get('kind', '')}|" + "|".join(places)
    return {"id": f"{card}-{hashlib.sha1(key.encode()).hexdigest()[:10]}", "places": places,
            "detail": _clean(detail)}


def _name_of(mid: str) -> str:
    return mid.split("#", 1)[1].rsplit("/", 1)[0]


def _owner_name(ctx: Context, owner: str) -> str:
    t = next((t for t in ctx.base.types if t.full_name == owner), None)
    return display_name(t) if t is not None else PurePosixPath(owner).name


def _place(ctx: Context, mid: str, line: int) -> str:
    return f"{ctx.base.method_file.get(mid, '?')}:{line}"


def _is_test(ctx: Context, mid: str) -> bool:
    return deps.is_test_path(ctx.base.method_file.get(mid, ""))


def _changes(ctx: Context) -> list:
    """The methods each commit changed, without the files a commit adds: a file created, or a
    module copied in, is not a change made to something that was there."""
    if ctx.changes is None:
        found = history.method_changes(ctx.repo, ctx.roots, ctx.tools,
                                       solid_config.load_config(ctx.repo)) or []
        added = _added_files(ctx.repo, ctx.roots)
        ctx.changes = [c for c in found
                       if ctx.base.method_file.get(c.method) not in added.get(c.commit, ())]
    return ctx.changes


def _added_files(repo: Path, roots: list[str]) -> dict[str, set[str]]:
    log = history._git(repo, "log", "--no-merges", "--diff-filter=A", "--name-only", "--relative",
                       "--format=@%H", "--", *roots)
    out: dict[str, set[str]] = {}
    commit = ""
    for line in (log or b"").decode("utf-8", "replace").splitlines():
        if line.startswith("@"):
            commit = line[1:].strip()
        elif line.strip():
            out.setdefault(commit, set()).add(line.strip())
    return out


def a1_families(ctx: Context) -> list[dict]:
    """The same capability in several modules: sibling modules with the same names, similar
    functions across modules, the same method of sibling modules changed together in one commit.
    A method changed in one module and not in another of the same name is not a fact: the same name
    is not the same capability, and on a real project it is mostly noise (`clear`, `of`, `update`).
    The families of capabilities are the agent's, from the description."""
    out = []
    methods_in: dict[str, dict[str, list]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for m in ctx.base.methods:
        f = ctx.base.method_file.get(m.id)
        if f:
            methods_in[_module_path(f)][m.name].append(m)
    for parent, members, shared, common in ctx.siblings:
        places = [_place(ctx, m.id, m.line) for mod in members for n in shared
                  for m in methods_in[mod].get(n, [])]
        places += [f"{t.file}:{t.line}" for t in ctx.base.types
                   if _module_path(t.file) in members and display_name(t) in shared]
        out.append(item("A1", places, {"kind": "siblings", "parent": parent, "modules": members,
                                       "names": shared, "common": common or ["none"]}))
    tools = ctx.tools / "similar"
    similar.collect_similar(ctx.repo, tools, ctx.tools, ctx.roots, SIMILARITY, MIN_TOKENS, LEXICAL)
    pairs = json.loads((tools / "similar.json").read_text(encoding="utf-8"))["pairs"]
    for p in pairs:
        ma, mb = _module_path(p["a"]), _module_path(p["b"])
        if ma != mb and not (p["a_test"] or p["b_test"]):
            out.append(item("A1", [f"{p['a']}:{p['a_start']}", f"{p['b']}:{p['b_start']}"],
                            {"kind": "similar", "units": [p["a_name"], p["b_name"]],
                             "modules": sorted({ma, mb})}))
    by_commit: dict[str, set[str]] = collections.defaultdict(set)
    for c in _changes(ctx):
        by_commit[c.commit].add(c.method)
    found: dict[tuple, set[str]] = collections.defaultdict(set)  # (name, changed) → commits
    for _, members, shared, _ in ctx.siblings:
        for name in shared:
            having = [mod for mod in members if name in methods_in[mod]]
            if len(having) < 2:
                continue
            for commit, mids in by_commit.items():
                changed = [mod for mod in having
                           if any(m.id in mids for m in methods_in[mod][name])]
                if len(changed) >= 2:
                    found[(name, tuple(changed))].add(commit)
    for (name, changed), commits in sorted(found.items()):
        places = [_place(ctx, m.id, m.line) for mod in changed for m in methods_in[mod][name]]
        out.append(item("A1", places, {"kind": "together", "method": name, "modules": list(changed),
                                       "commits": sorted(c[:12] for c in commits)}))
    return out


def b3_private_uses(ctx: Context) -> list[dict]:
    """A member private to another type, used from outside it."""
    work = ctx.tools / "graph"
    principles.collect_principles(ctx.repo, work, ctx.tools, ctx.roots)
    data = json.loads((work / "principles.json").read_text(encoding="utf-8"))
    return [item("B3", [f"{x['file']}:{s['line']}" for s in x["sites"]],
                 {"kind": "private-use", "members": x["members"]})
            for x in data["private_access"] if not x["test"]]


def c1_read_first(ctx: Context) -> list[dict]:
    """Per module, its functions in the order to read them: the complex ones the history changed
    most come first. The order is the fact; the measure behind it is not written."""
    try:
        import lizard  # noqa: PLC0415 - optional: without it the card is read by hand
    except ImportError as e:
        raise NotComputed("lizard is not installed") from e
    commits = collections.Counter(c.method for c in _changes(ctx))
    by_file = collections.defaultdict(list)
    for m in ctx.base.methods:
        by_file[ctx.base.method_file.get(m.id, "")].append(m)
    out = []
    for mod in sorted(ctx.modules.values(), key=lambda m: m.path):
        ranked = []
        for rel in mod.files:
            if deps.is_test_path(rel):
                continue
            info = lizard.analyze_file(str(ctx.repo / rel))
            for fn in info.function_list:
                owner = next((m for m in by_file.get(rel, [])
                              if m.line <= fn.start_line <= m.end_line), None)
                weight = fn.cyclomatic_complexity * (1 + (commits[owner.id] if owner else 0))
                ranked.append((-weight, f"{rel}:{fn.start_line}", fn.name))
        ranked = sorted(ranked)[:READ_FIRST]
        if ranked:
            out.append(item("C1", [p for _, p, _ in ranked],
                            {"kind": "read-first", "module": mod.path,
                             "order": [f"{name} — {p}" for _, p, name in ranked]}))
    return out


def _solid_items(card: str, facts) -> list[dict]:
    return [item(card, f.places, {"kind": f.kind, **f.detail}) for f in facts]


def c3_switches(ctx: Context) -> list[dict]:
    return _solid_items("C3", solid.repeated_dispatch(ctx.base, solid_config.load_config(ctx.repo)))


def c4_refusals(ctx: Context) -> list[dict]:
    return _solid_items("C4", solid.refused_bequest(ctx.base) + solid.subtype_tests(ctx.base))


def c5_stubs(ctx: Context) -> list[dict]:
    return _solid_items("C5", solid.stubbed_interface(ctx.base))


def d1_state_fields(ctx: Context) -> list[dict]:
    """A field of state — a bool, a string, an enum — written by two or more methods."""
    enums = {t.full_name for t in ctx.base.types if t.kind == "enum"}
    enum_names = {display_name(t) for t in ctx.base.types if t.kind == "enum"}
    file_of = {t.full_name: t.file for t in ctx.base.types}
    writers = collections.defaultdict(list)
    for a in ctx.base.accesses:
        if a.mode == "w" and not _is_test(ctx, a.method):
            writers[a.field].append(a)
    out = []
    for f in ctx.base.fields:
        typ = f.declared_type.strip()
        if typ not in STATE_TYPES and typ not in enums and typ not in enum_names:
            continue
        ws = writers.get(f.id, [])
        if len({a.method for a in ws}) < 2:
            continue
        places = [f"{file_of.get(f.owner, '?')}:{f.line}"] + [_place(ctx, a.method, a.line) for a in ws]
        out.append(item("D1", places, {"kind": "state-field",
                                       "field": f"{_owner_name(ctx, f.owner)}.{f.name}",
                                       "writers": sorted({_name_of(a.method) for a in ws})}))
    return out


def e2_mirrors(ctx: Context) -> list[dict]:
    """Two types whose fields share their names, and a method that builds one from the other."""
    fields_of = collections.defaultdict(set)
    for f in ctx.base.fields:
        fields_of[f.owner].add(f.name)
    by_short = {display_name(t): t for t in ctx.base.types}
    params = collections.defaultdict(set)
    for r in ctx.base.trefs:
        if r.role == "param" and r.resolved:
            params[r.holder].add(r.resolved)
    out = []
    for c in ctx.base.calls:
        if c.receiver != "new":
            continue
        built = by_short.get(c.callee)
        if built is None:
            continue
        for src in sorted(params.get(c.method, ())):
            shared = fields_of[built.full_name] & fields_of[src]
            if src != built.full_name and len(shared) >= 2:
                s = next(t for t in ctx.base.types if t.full_name == src)
                out.append(item("E2", [f"{built.file}:{built.line}", f"{s.file}:{s.line}",
                                       _place(ctx, c.method, c.line)],
                                {"kind": "mirror", "types": sorted([display_name(built),
                                                                     display_name(s)]),
                                 "fields": sorted(shared)}))
    return out


def f2_swallowed(ctx: Context) -> list[dict]:
    """A catch that does nothing, or only logs."""
    return [item("F2", [_place(ctx, c.method, c.line)],
                 {"kind": "catch", "body": c.body, "method": _name_of(c.method)})
            for c in ctx.base.catches
            if c.body in ("empty", "log-only") and not _is_test(ctx, c.method)]


def h1_uncalled(ctx: Context) -> list[dict]:
    """A method whose name no call of the project uses: not a constructor, an override, an
    abstract or interface method, an engine callback (`_ready`) or a special method (`__str__`)."""
    called = {c.callee for c in ctx.base.calls}
    interfaces = {t.full_name for t in ctx.base.types if t.kind in ("interface", "protocol")}
    out = []
    for m in ctx.base.methods:
        if (m.name in called or m.is_ctor or m.is_dtor or m.is_override or m.is_abstract
                or m.owner in interfaces or m.name.startswith("_") or m.name == "main"
                or m.name.startswith(("get_", "set_")) or _is_test(ctx, m.id)):
            continue
        out.append(item("H1", [_place(ctx, m.id, m.line)],
                        {"kind": "uncalled", "method": f"{_owner_name(ctx, m.owner)}.{m.name}"}))
    return out


CARD_FACTS = {"A1": a1_families, "B3": b3_private_uses, "C1": c1_read_first, "C3": c3_switches,
              "C4": c4_refusals, "C5": c5_stubs, "D1": d1_state_fields, "E2": e2_mirrors,
              "F2": f2_swallowed, "H1": h1_uncalled}


def step_coverage(ctx: Context) -> None:
    langs = collections.Counter(ctx.lang_of.values())
    lines = ["# Coverage", "", f"Roots: {', '.join(ctx.roots)}", "", "## Examined", ""]
    for lang, n in sorted(langs.items()):
        facts = "the object facts and the graph" if lang in oo_extract.EXTRACTORS \
            else "the graph only: no object facts for this language, its cards are read by hand"
        lines.append(f"- {lang}: {n} files — {facts}")
    if not langs:
        lines.append("none")
    lines += ["", "## Not examined", ""]
    gaps = [f"- {ext}: {n} files — not examined: no grammar for this language"
            for ext, n in ctx.uncovered.items()]
    gaps += [f"- {ext}: {n} files — not examined: its grammar is not installed "
             "(`bash .claude/audit/install.sh`)" for ext, n in ctx.uninstalled.items()]
    lines += gaps or ["none"]
    lines += ["", "## Card facts", ""]
    lines += [f"- {card}: not computed: {ctx.not_computed[card]}" if card in ctx.not_computed
              else f"- {card}: computed" for card in sorted(CARD_FACTS)]
    _write(ctx.out / "coverage.md", "\n".join(lines) + "\n")
