#!/usr/bin/env python3
"""Type name → the file that declares it: the one way the audit resolves a name.

A name declared once in its family resolves to that file. A name declared in several files
resolves by directory first; then, for the languages that write their scope down (jvm, dotnet,
php, rust), by the namespace or the import the referencing file writes; what is still several
files is NOT resolved, and counted as ambiguous. Production code never resolves into test code.

deps.py builds its graph with it (`TypeIndex.resolve`, on its per-file records); oo_build.py
resolves the names of the object-oriented facts with it (`TypeIndex.from_facts`, `resolve_type`).
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

_ARGS = re.compile(r"[\[<](.*)[\]>]", re.S)  # the arguments of a generic, outermost brackets


def _split_top(text: str, sep: str) -> list[str]:
    """`text` split at `sep` outside any bracket: `str, list[A, B]` → [`str`, `list[A, B]`]."""
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch in "[<(":
            depth += 1
        elif ch in "]>)":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


class TypeIndex:
    def __init__(self, decls: dict[tuple[str, str], list[str]], records: dict[str, dict],
                 tests: set[str]):
        """decls: (family, declared name) → the files declaring it; records: file → its record
        (`family`, `lang`, `ns`, `imports`); tests: the files that are test code."""
        self.decls = decls
        self.records = records
        self.tests = tests
        self.ambiguous: collections.Counter[str] = collections.Counter()
        self.global_imports = {i[len("global:"):] for r in records.values()
                               for i in (r.get("imports") or ())
                               if isinstance(i, str) and i.startswith("global:")}
        self.types: dict[tuple[str, str], list[str]] = {}  # (file, simple name) → full names

    def in_scope(self, rec: dict, fam: str, c: str, name: str) -> bool:
        """Does the file SEE the declaration in `c`? The languages with namespaces say so in
        writing: same namespace (or an enclosing one), or an import of it, of the name, or of
        a wildcard over it. Without that a unique name is still not an edge: `Field` in a file
        that imports java.lang.reflect.Field is not the class Field a test declares."""
        ns = rec.get("ns")
        imps = {i.removeprefix("global:") for i in (rec.get("imports") or ())} | self.global_imports
        cns = self.records[c].get("ns")
        if fam == "rust":
            p = Path(c)
            stem = p.parent.name if p.stem in ("mod", "lib") else p.stem
            return any(re.search(rf"\b{re.escape(name)}\b", i) or i.endswith("::*")
                       and stem in i for i in imps)
        if not cns:
            return not ns  # both in the default package / global namespace
        sep = "\\" if fam == "php" else "."
        return (cns == ns or (ns or "").startswith(cns + sep) or cns in imps
                or f"{cns}{sep}{name}" in imps or f"{cns}{sep}*" in imps)

    def resolve(self, rel: str, rec: dict, name: str) -> list[str]:
        fam = rec.get("family") or rec.get("lang")
        cands = [c for c in self.decls.get((fam, name), ()) if c != rel]
        # Production code does not depend on test code: a name a test also declares (a nested
        # helper called `Field`, a fake called `Clock`) is never resolved into the test.
        if rel not in self.tests:
            cands = [c for c in cands if c not in self.tests]
        if not cands:
            return []
        here = Path(rel).parent
        same_dir = [c for c in cands if Path(c).parent == here]
        if same_dir:
            cands = same_dir
        elif fam in ("jvm", "dotnet", "php", "rust"):
            cands = [c for c in cands if self.in_scope(rec, fam, c, name)]
            if not cands:
                return []
        if len(cands) == 1:
            return cands
        if fam == "dotnet" and len({self.records[c].get("ns") for c in cands}) == 1:
            return cands  # a partial class: one type written across several files
        self.ambiguous[rec.get("lang", "?")] += 1
        return []

    # --- over the object-oriented facts ---------------------------------------------------------

    @classmethod
    def from_facts(cls, files, tests: set[str] = frozenset()) -> "TypeIndex":
        """The index of the types the FileFacts declare, by their simple name."""
        import deps  # deps imports this module: the import is the caller's, at call time
        family = {a.lang: a.family for a in deps.ADAPTERS}
        decls: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
        records, types = {}, collections.defaultdict(list)
        for ff in files:
            records[ff.file] = {"lang": ff.lang, "family": family.get(ff.lang, ff.lang),
                                "ns": ff.package, "imports": list(ff.imports)}
            for t in ff.types:
                simple = t.full_name.rsplit(".", 1)[-1]
                if ff.file not in decls[(records[ff.file]["family"], simple)]:
                    decls[(records[ff.file]["family"], simple)].append(ff.file)
                types[(ff.file, simple)].append(t.full_name)
        for v in decls.values():
            v.sort()
        index = cls(dict(decls), records, set(tests))
        index.types = {k: sorted(set(v)) for k, v in types.items()}
        return index

    def resolve_all(self, rel: str, name: str) -> tuple[str, ...]:
        """Every project type a declared type names, in order: the name itself; when it is
        dotted and not a type, its owner (`PropModel.Kind` → `PropModel`: an enum or a member
        of the class); then the arguments of a generic (`Array[X]`, `Dictionary[K, V]`,
        `List<X>`, `Optional[X]`) and the members of a union (`X | None`), recursively."""
        out: list[str] = []

        def add(n: str) -> None:
            n = n.strip().strip("'\"").rstrip("?").strip()
            if not n:
                return
            alts = _split_top(n, "|")
            if len(alts) > 1:
                for a in alts:
                    add(a)
                return
            base = n.split("<", 1)[0].split("[", 1)[0].strip()
            hit = self.resolve_type(rel, base)
            if hit is None and "." in base:
                hit = self.resolve_type(rel, base.rsplit(".", 1)[0])
            if hit and hit not in out:
                out.append(hit)
            m = _ARGS.search(n)
            if m:
                for arg in _split_top(m.group(1), ","):
                    add(arg)

        add(name)
        return tuple(out)

    def resolve_type(self, rel: str, name: str) -> str | None:
        """The full name of the project type `name` written in file `rel` means, or None — the
        name itself, without looking inside a generic (that is resolve_all)."""
        name = name.split("<", 1)[0].split("[", 1)[0].strip().strip("'\"").rstrip("?")
        if not name or rel not in self.records:
            return None
        simple = name.rsplit(".", 1)[-1]
        hits = {full for f in self.resolve(rel, self.records[rel], simple)
                for full in self.types.get((f, simple), ())}
        if not hits:  # declared in the referencing file itself
            hits = set(self.types.get((rel, simple), ()))
        if "." in name:
            hits = {h for h in hits if h == name or h.endswith("." + name)} or hits
        return hits.pop() if len(hits) == 1 else None
