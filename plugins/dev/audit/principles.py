#!/usr/bin/env python3
"""F9 — ENCAPSULATION, as a fact read off the syntax tree.

PRIVATE ACCESS: `other._field` / `other._method()` — a member the language marks private by
convention, used from outside its object. That is the violation itself, not a suspect: the line
says it. Only for the languages where the private is a convention (GDScript, Python,
JavaScript/TypeScript); where the compiler enforces it there is nothing to find.

Computed over every file, in one run, with the same tree-sitter grammars as the rest. Writes
`principles.json`.
"""

from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

import deps

CACHE_VERSION = 5
_CACHE_KEY = f"{CACHE_VERSION}:{hashlib.sha1(Path(__file__).read_bytes()).hexdigest()}"

CONVENTION_PRIVATE = {"gdscript", "python", "javascript", "typescript", "tsx"}
OWN = {"self", "this", "super", "cls"}


# Members the language's own libraries name with an underscore and mean as public.
PUBLIC_UNDERSCORE = {"_replace", "_asdict", "_fields", "_make", "_field_defaults"}
DECLS = ("variable_statement", "const_statement", "function_definition", "signal_statement",
         "enum_definition", "class_definition", "method_definition", "public_field_definition",
         "field_definition", "property_signature", "method_signature")


def private_access(adapter, src: bytes) -> tuple[list[dict], list[str]]:
    """Every `obj._member` where the member is NOT declared in this file.

    A class reaching into another instance of ITSELF (`var c := Ejection.new(); c._seat = …`
    inside Ejection) is allowed in every language with real privacy; the violation is reaching
    into a member some other class declares."""
    tree = adapter.parser.parse(src)
    own, declared = set(), set()
    for n in deps._walk(tree.root_node):
        if n.type in ("class_name_statement", "class_definition", "class_declaration"):
            f = n.child_by_field_name("name")
            if f is not None:
                own.add(deps._txt(src, f))
        if n.type in DECLS:
            f = n.child_by_field_name("name") or n.child_by_field_name("property")
            if f is not None:
                declared.add(deps._txt(src, f))
        if n.type in ("attribute", "member_expression"):  # `self._x = …` declares _x (Python, JS)
            o = n.child_by_field_name("object")
            m = n.child_by_field_name("attribute") or n.child_by_field_name("property")
            if o is not None and m is not None and deps._txt(src, o) in OWN:
                declared.add(deps._txt(src, m))
    out = []
    for n in deps._walk(tree.root_node):
        if n.type not in ("attribute", "member_expression"):
            continue
        obj = n.child_by_field_name("object") or (n.children[0] if n.children else None)
        mem = n.child_by_field_name("attribute") or n.child_by_field_name("property")
        if mem is None:  # GDScript: `obj` `.` `member` or `obj` `.` `member(...)`
            rest = [c for c in n.children[1:] if c.type != "."]
            mem = rest[0] if rest else None
            if mem is not None and mem.type in ("attribute_call", "attribute_subscript",
                                                "subscript") and mem.children:
                mem = mem.children[0]  # `obj._m(…)`, `obj._m[i]`: the member is the first child
        if obj is None or mem is None:
            continue
        o, m = deps._txt(src, obj), deps._txt(src, mem)
        if m.startswith("_") and not (m.startswith("__") and m.endswith("__")) and \
                o not in OWN and o not in own and m not in declared and m not in PUBLIC_UNDERSCORE:
            out.append({"line": n.start_point[0] + 1, "object": o[:60], "member": m})
    return out, sorted(declared)


def collect_principles(repo: Path, out: Path, cache_dir: Path, src_roots: list[str],
                       test_names=deps.TEST_DIRS) -> dict:
    files = deps.source_files(repo, src_roots)
    by_ext, missing, _ = deps.adapter_table(files)
    cache_path = cache_dir / "principles-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("version") != _CACHE_KEY:
            cache = {}
    except (OSError, ValueError):
        cache = {}
    old, new = cache.get("files", {}), {}
    langs = collections.Counter()
    for f in files:
        a = by_ext.get(f.suffix.lower())
        if a is None or a.lang not in CONVENTION_PRIVATE:
            continue
        rel = f.relative_to(repo).as_posix()
        try:
            data = f.read_bytes()
        except OSError:
            continue
        langs[a.lang] += 1
        sha = hashlib.sha1(data).hexdigest()
        hit = old.get(rel)
        if hit and hit.get("sha") == sha:
            new[rel] = hit
            continue
        try:
            sites, declared = private_access(a, data)
            new[rel] = {"sha": sha, "private": sites, "declared": declared}
        except Exception:  # noqa: BLE001 - one unparsable file must not sink the run
            new[rel] = {"sha": sha, "private": [], "declared": []}
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": _CACHE_KEY, "files": new}), encoding="utf-8")
    tmp.replace(cache_path)

    # A member an ANCESTOR declares is the family's own (`g._assign_id` where Actor declares it and
    # the file is an Actor): only a member no class of the file's own lineage declares is someone
    # else's. The lineage comes from the `extends` edges of the graph, when it is there.
    parents: dict[str, set[str]] = collections.defaultdict(set)
    deps_csv = out / "deps.csv"
    if deps_csv.is_file():
        for line in deps_csv.read_text(encoding="utf-8").splitlines()[1:]:
            a, _, rest = line.partition(",")
            b, _, kind = rest.rpartition(",")
            if kind == "extends":
                parents[a].add(b)

    def lineage(f: str) -> set[str]:
        seen, todo = set(), [f]
        while todo:
            x = todo.pop()
            for y in parents.get(x, ()):
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
        return seen

    priv = []
    for f, r in sorted(new.items()):
        inherited = {m for anc in lineage(f) for m in new.get(anc, {}).get("declared", ())}
        sites = [p for p in r["private"] if p["member"] not in inherited]
        if sites:
            priv.append({"file": f, "test": deps.is_test_path(f, test_names), "uses": len(sites),
                         "members": sorted({p["member"] for p in sites}), "sites": sites[:30]})
    priv.sort(key=lambda x: (-x["uses"], x["file"]))
    out.mkdir(parents=True, exist_ok=True)
    (out / "principles.json").write_text(json.dumps({"private_access": priv}, indent=1) + "\n",
                                         encoding="utf-8")
    prod = [x for x in priv if not x["test"]]
    return {"files": len(new), "langs": dict(langs), "private_files": len(prod),
            "private_uses": sum(x["uses"] for x in prod), "top": prod[:10],
            "missing_grammars": missing}
