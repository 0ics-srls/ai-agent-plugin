#!/usr/bin/env python3
"""The per-file facts → one resolved fact base (spec §2).

Merges the facts of every file — a C# partial class written across several files is one type —
and resolves the names they record as written: each base of a type to the project type it names,
split into extends (a class, struct, record base) and implements (an interface, protocol base);
each typed reference to its type; each call to the type of its receiver — `self`, a typed
parameter or local of the method, a typed field of the owner, or a type name — when that type, or
one of its ancestors, declares the callee. Python and GDScript do not write `override`: a method
overrides when an ancestor of the project declares one of the same name, and only then does its
body kind become an OverrideBodyFact. What names no project type is counted, never guessed.
"""

from __future__ import annotations

import collections
from dataclasses import replace

from oo_model import FactBase, FileFacts, OverrideBodyFact, TypeFact
from resolve import TypeIndex

INHERITS = {"class": "extends", "struct": "extends", "record": "extends",
            "interface": "implements", "protocol": "implements", "enum": "extends"}
UNDECLARED_OVERRIDE = ("python", "gdscript")  # override is not written: decided here


def build_fact_base(files: list[FileFacts], tests: set[str] = frozenset()) -> FactBase:
    files = sorted(files, key=lambda f: f.file)
    index = TypeIndex.from_facts(files, tests)
    unresolved: collections.Counter[str] = collections.Counter()
    types = _merge_partials([t for f in files for t in f.types])
    by_name = {t.full_name: t for t in types}
    file_of = {t.full_name: t.file for t in types}
    lang_of = {f.file: f.lang for f in files}

    extends: dict[str, list[str]] = {}
    implements: dict[str, list[str]] = {}
    main_of = {}  # file → the first type it declares: what `extends "res://x.gd"` names
    for t in sorted(types, key=lambda t: (t.file, t.line)):
        main_of.setdefault(t.file, t.full_name)
    for t in types:
        for b in t.bases:
            full = (main_of.get(b[len("res://"):]) if b.startswith("res://")
                    else index.resolve_type(t.file, b))
            if full is None or full == t.full_name:
                unresolved["bases"] += 1
                continue
            rel = extends if INHERITS[by_name[full].kind] == "extends" else implements
            if full not in rel.setdefault(t.full_name, []):
                rel[t.full_name].append(full)

    methods = sorted({m.id: m for f in files for m in f.methods}.values(), key=lambda m: m.id)
    declared = collections.defaultdict(set)  # type → method names it declares
    for m in methods:
        declared[m.owner].add(m.name)

    def ancestors(t: str) -> list[str]:
        out, todo, seen = [], list(extends.get(t, []) + implements.get(t, [])), {t}
        while todo:
            a = todo.pop(0)
            if a in seen:
                continue
            seen.add(a)
            out.append(a)
            todo += extends.get(a, []) + implements.get(a, [])
        return out

    bodies = {mid: kind for f in files for mid, kind in f.bodies.items()}
    obodies = {b.method: b for f in files for b in f.obodies}
    resolved_methods = []
    for m in methods:
        if lang_of.get(file_of.get(m.owner, "")) in UNDECLARED_OVERRIDE and not m.is_ctor and \
                any(m.name in declared[a] for a in ancestors(m.owner)):
            m = replace(m, is_override=True)
            if m.id in bodies:
                obodies[m.id] = OverrideBodyFact(m.id, bodies[m.id])
        resolved_methods.append(m)
    method_owner = {m.id: m.owner for m in resolved_methods}

    trefs = []
    for f in files:
        for r in f.trefs:
            hits = index.resolve_all(f.file, r.declared_type)
            if not hits:
                unresolved["trefs"] += 1
            trefs.append(replace(r, resolved=hits[0] if hits else "", also=hits[1:]))
    typed = collections.defaultdict(dict)  # holder (method id or type id) → name → type
    for r in trefs:
        if r.resolved:
            typed[r.holder][r.name] = r.resolved

    def owns(t: str, callee: str) -> bool:
        return callee in declared[t] or any(callee in declared[a] for a in ancestors(t))

    calls, constructions = [], {}
    for f in files:
        for c in f.calls:
            owner = method_owner.get(c.method, "")
            recv = c.receiver
            built = _constructed(index, f, c, declared[owner])
            if built:
                constructions[c.id] = built
                calls.append(replace(c, callee_type=built))
                continue
            if recv in ("self", "this", ""):
                target = owner
            else:
                target = (typed[c.method].get(recv) or typed[f"type:{owner}"].get(recv)
                          or index.resolve_type(f.file, recv) or "")
            if target and owns(target, c.callee):
                calls.append(replace(c, callee_type=target))
            else:
                if recv not in ("", "self", "this") or not target:
                    unresolved["calls"] += 1
                calls.append(c)

    ttests = []
    for f in files:
        for t in f.ttests:
            if t.kind == "type":
                t = replace(t, resolved=tuple(index.resolve_type(f.file, n) or "" for n in t.tested))
                subject = t.subject.removeprefix("this.").removeprefix("self.")
                owner = method_owner.get(t.method, "")
                if t.subject not in typed[t.method] and subject not in typed[f"type:{owner}"]:
                    unresolved["ttests"] += 1  # the tested value has no declared type
            ttests.append(t)

    def merged(name):
        return sorted({x.id: x for f in files for x in getattr(f, name)}.values(),
                      key=lambda x: x.id)

    return FactBase(types=types, methods=resolved_methods, fields=merged("fields"),
                    accesses=merged("accesses"), calls=sorted(calls, key=lambda c: c.id),
                    trefs=sorted(trefs, key=lambda r: r.id),
                    ttests=sorted({t.id: t for t in ttests}.values(), key=lambda t: t.id),
                    obodies=sorted(obodies.values(), key=lambda b: b.id),
                    catches=sorted({c.id: c for f in files for c in f.catches}.values(), key=lambda c: c.id),
                    extends=extends, implements=implements, unresolved=dict(unresolved),
                    langs=lang_of, bodies=bodies,
                    method_file={m.id: f.file for f in files for m in f.methods},
                    constructions=constructions)


def _constructed(index: TypeIndex, f: FileFacts, c, owner_methods: set[str]) -> str | None:
    """The project type a call constructs, or None: C# `new T()` (receiver "new"), GDScript
    `T.new()`, Python `T()` — a bare call to a name that is a project type, not a method."""
    if c.receiver == "new":
        return index.resolve_type(f.file, c.callee)
    if f.lang == "gdscript" and c.callee == "new" and c.receiver:
        return index.resolve_type(f.file, c.receiver)
    if f.lang == "python" and c.receiver == "" and c.callee not in owner_methods:
        return index.resolve_type(f.file, c.callee)
    return None


def _merge_partials(types: list[TypeFact]) -> list[TypeFact]:
    """One TypeFact per full name: a partial class written in several files is one type, declared
    at its first place (by file, then line), with the bases of every part."""
    by: dict[str, list[TypeFact]] = collections.defaultdict(list)
    for t in types:
        by[t.full_name].append(t)
    out = []
    for full, parts in sorted(by.items()):
        parts.sort(key=lambda t: (t.file, t.line))
        bases = tuple(dict.fromkeys(b for p in parts for b in p.bases))
        out.append(replace(parts[0], bases=bases, abstract=any(p.abstract for p in parts)))
    return out
