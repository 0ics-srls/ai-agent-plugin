#!/usr/bin/env python3
"""The SOLID FACTS of report section 4 (spec §4), computed from the FactBase alone.

Each one is true by construction — the code IS what the entry says — and lists every place:
  4.O   the same type switch in several places: adding a type means editing every one of them;
  4.L1  an override whose body is empty or only-throw while the base method is not abstract;
  4.L2  an implementation of an interface method whose body is empty or only-throw;
  4.L3  a method holding a value typed as a base type B, and type-testing it against subtypes of B;
The 4.L entries are structural: the behavioural contract is not analysed. A fact's id is built
from its places, so the same code gives the same ids in any run.
"""

from __future__ import annotations

import collections
import hashlib
from dataclasses import dataclass

from oo_model import FactBase

REFUSED = ("empty", "throw")


@dataclass(frozen=True)
class SolidFact:
    kind: str                  # "4.O" | "4.L1" | "4.L2" | "4.L3" | "4.D"
    places: tuple[str, ...]    # "file:line", sorted
    detail: dict
    evidence: tuple[str, ...]  # the ids of the facts it is made of

    @property
    def id(self) -> str:
        return f"solid:{self.kind}:" + hashlib.sha1("|".join(self.places).encode()).hexdigest()[:10]


@dataclass(frozen=True)
class Chain:
    """One dispatch: the type tests of one chain id."""
    method: str
    subject: str
    tested: frozenset[str]
    branches: int
    kind: str                  # "type" | "enum"
    place: str
    evidence: tuple[str, ...]


def _place(fb: FactBase, method_id: str, line: int) -> str:
    return f"{fb.method_file.get(method_id, '?')}:{line}"


def _ancestors(fb: FactBase, t: str, via=("extends", "implements")) -> list[str]:
    out, todo, seen = [], [t], {t}
    while todo:
        cur = todo.pop(0)
        for rel in via:
            for a in getattr(fb, rel).get(cur, []):
                if a not in seen:
                    seen.add(a)
                    out.append(a)
                    todo.append(a)
    return out


def _methods_of(fb: FactBase) -> dict[str, list]:
    by = collections.defaultdict(list)
    for m in fb.methods:
        by[m.owner].append(m)
    return by


def _sorted(facts) -> list[SolidFact]:
    return sorted(facts, key=lambda f: f.id)


def dispatch_chains(fb: FactBase) -> list[Chain]:
    by_chain = collections.defaultdict(list)
    for t in fb.ttests:
        by_chain[t.chain].append(t)
    out = []
    for chain_id, ts in sorted(by_chain.items()):
        ts.sort(key=lambda t: t.line)
        first = ts[0]
        out.append(Chain(first.method, first.subject, frozenset(n for t in ts for n in t.tested),
                         max(t.branches for t in ts), first.kind,
                         _place(fb, first.method, first.line), tuple(t.id for t in ts)))
    return out


def _kind_enum(c: Chain, names) -> bool:
    """An enum chain counts when its members are of an enum named as a kind (configured)."""
    return all(m.rsplit(".", 1)[0].rsplit(".", 1)[-1].endswith(tuple(names)) for m in c.tested)


def dispatch_groups(fb: FactBase, cfg: dict) -> dict[tuple[str, frozenset], list[Chain]]:
    """The dispatches of `ocp.dispatch_min_branches`+ branches, grouped by what they test: a group
    of `ocp.repeat_min_sites`+ is the fact 4.O, a group of one the signal of a single switch."""
    ocp = cfg["ocp"]
    groups = collections.defaultdict(list)
    for c in dispatch_chains(fb):
        if c.branches >= ocp["dispatch_min_branches"] and (
                c.kind == "type" or _kind_enum(c, ocp["kind_enum_names"])):
            groups[(c.kind, c.tested)].append(c)
    return dict(groups)


def repeated_dispatch(fb: FactBase, cfg: dict) -> list[SolidFact]:
    return _sorted(SolidFact("4.O", tuple(sorted(c.place for c in cs)),
                             {"tested": sorted(t), "kind": k,
                              "methods": sorted(c.method for c in cs)},
                             tuple(sorted(e for c in cs for e in c.evidence)))
                   for (k, t), cs in dispatch_groups(fb, cfg).items()
                   if len(cs) >= cfg["ocp"]["repeat_min_sites"])


def refused_bequest(fb: FactBase) -> list[SolidFact]:
    by_id = {m.id: m for m in fb.methods}
    methods = _methods_of(fb)
    out = []
    for ob in fb.obodies:
        m = by_id.get(ob.method)
        if m is None or ob.body not in REFUSED:
            continue
        base = None
        for a in _ancestors(fb, m.owner, via=("extends",)):
            same = [b for b in methods.get(a, []) if b.name == m.name]
            if same:
                base = next((b for b in same if b.arity == m.arity), same[0])
                break
        if base is None or base.is_abstract:
            continue
        out.append(SolidFact("4.L1", tuple(sorted((_place(fb, m.id, m.line),
                                                    _place(fb, base.id, base.line)))),
                             {"method": m.id, "base": base.id, "body": ob.body},
                             (ob.id, m.id, base.id)))
    return _sorted(out)


def stubbed_interface(fb: FactBase) -> list[SolidFact]:
    kind = {t.full_name: t.kind for t in fb.types}
    methods = _methods_of(fb)
    out = []
    for t in fb.types:
        if t.kind in ("interface", "protocol"):
            continue
        ifaces = [a for a in _ancestors(fb, t.full_name) if kind.get(a) in ("interface", "protocol")]
        declared = {}
        for i in ifaces:
            for im in methods.get(i, []):
                declared.setdefault(im.name, im)
        for m in methods.get(t.full_name, []):
            im = declared.get(m.name)
            body = fb.bodies.get(m.id)
            if im is None or body not in REFUSED:
                continue
            out.append(SolidFact("4.L2", tuple(sorted((_place(fb, m.id, m.line),
                                                        _place(fb, im.id, im.line)))),
                                 {"method": m.id, "interface_method": im.id, "body": body},
                                 (m.id, im.id)))
    return _sorted(out)


def subtype_tests(fb: FactBase) -> list[SolidFact]:
    owner = {m.id: m.owner for m in fb.methods}
    typed = collections.defaultdict(dict)  # holder → name → (type, tref id)
    for r in fb.trefs:
        if r.resolved and r.role in ("param", "field"):
            typed[r.holder][r.name] = (r.resolved, r.id)
    groups = collections.defaultdict(list)  # (method, subject, base) → [(ttest, subtypes)]
    for t in fb.ttests:
        if t.kind != "type":
            continue
        name = t.subject.removeprefix("this.").removeprefix("self.")
        held = typed[t.method].get(t.subject) or typed[f"type:{owner.get(t.method, '')}"].get(name)
        if held is None:
            continue
        base, tref = held
        subs = [r for r in t.resolved if r and r != base and base in _ancestors(fb, r)]
        if subs:
            groups[(t.method, t.subject, base, tref)].append((t, subs))
    return _sorted(SolidFact("4.L3", tuple(sorted(_place(fb, m, t.line) for t, _ in hits)),
                             {"method": m, "subject": s, "base": b,
                              "tested": sorted({x for _, subs in hits for x in subs})},
                             tuple(sorted({t.id for t, _ in hits} | {tref})))
                   for (m, s, b, tref), hits in groups.items())
