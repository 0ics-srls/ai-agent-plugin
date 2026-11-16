#!/usr/bin/env python3
"""F5b — SIMILAR code: functions that were copied and then changed, across the whole project.

What `jscpd` (F5) finds is the same sequence of tokens twice — code copied and left alone. What it
cannot find is the copy that was then edited: a statement added, one removed, a condition changed,
names replaced. That is the duplication that costs, because the copies now differ and every fix has
to be found and made N times. In the clone literature it is the near-miss, or Type-3, clone.

How it is found — algorithmic, no model, the method of the near-miss detectors (NiCad, SourcererCC):

  1. every function of every file is cut out by its tree-sitter grammar (the same grammars as the
     dependency graph, so the same languages);
  2. its tokens are NORMALIZED: every name becomes `I`, every literal `L`; keywords, operators and
     punctuation stay as they are. Renaming a variable or changing a constant does not hide a copy;
     comments are not tokens at all;
  3. the token sequence is cut into overlapping 3-token shingles, kept as a multiset;
  4. two functions are similar when the shingles they share are at least `--similarity` (default
     0.70, NiCad's usual setting) of the larger of the two. Functions shorter than `--min-tokens`
     are not compared: below that size every getter resembles every other getter.

Candidates come from an inverted index with prefix filtering (each function is indexed only by its
rarest shingles, which two functions above the threshold must share), so the cost grows with the
number of similar pairs, not with the square of the number of functions.

Writes `similar.json`: the pairs, with both locations, the similarity, and whether each side is test
code; and the FAMILIES — sets of functions linked by similarity (one function copied into six
places is one family of six, not fifteen pairs). Incremental, like the graph: each file's units are
cached under the sha1 of its content in `audit/.tools/similar-cache.json`.
"""

from __future__ import annotations

import collections
import hashlib
import json
import math
import zlib
from pathlib import Path

import deps

CACHE_VERSION = 2
_CACHE_KEY = f"{CACHE_VERSION}:{hashlib.sha1(Path(__file__).read_bytes()).hexdigest()}"

# The node types that are a function, per language — what gets compared.
FUNCS = {
    "gdscript": ("function_definition", "constructor_definition"),
    "python": ("function_definition",),
    "javascript": ("function_declaration", "method_definition", "function_expression",
                   "arrow_function", "generator_function_declaration"),
    "csharp": ("method_declaration", "constructor_declaration", "local_function_statement",
               "operator_declaration", "accessor_declaration"),
    "java": ("method_declaration", "constructor_declaration"),
    "kotlin": ("function_declaration", "secondary_constructor", "anonymous_initializer"),
    "swift": ("function_declaration", "init_declaration"),
    "php": ("function_definition", "method_declaration"),
    "rust": ("function_item",),
    "c": ("function_definition",),
    "cpp": ("function_definition",),
    "go": ("function_declaration", "method_declaration", "func_literal"),
    "dart": ("function_body",),
    "perl": ("subroutine_declaration_statement",),
}
FUNCS["typescript"] = FUNCS["tsx"] = FUNCS["javascript"]

SHINGLE = 3
# The tokens of a decision or a loop. A function without any is straight-line — a list of
# constructions or assignments, data written as code — and a copy of it is a copy of data, not of
# logic: fixing one never owes a fix to the other. The report keeps copies of LOGIC.
CONTROL = {"if", "elif", "else", "for", "while", "match", "switch", "case", "when", "loop",
           "?", "&&", "||", "and", "or", "guard", "unless", "until", "foreach", "do"}


def _kind(n) -> str | None:
    """The normalized token of a leaf, or None for what is not a token (a comment)."""
    t = n.type
    if "comment" in t:
        return None
    if not n.is_named:
        return t  # keywords, operators, punctuation: the structure, kept as written
    if any(k in t for k in ("string", "literal", "number", "integer", "float", "char", "escape",
                            "heredoc", "rune", "imaginary", "fragment", "content")):
        return "L"
    if "primitive" in t or "predefined" in t or t in ("void_type", "true", "false", "null",
                                                        "nil", "none", "self", "this"):
        return t
    return "I"


def _tokens(src: bytes, node) -> tuple[list[str], list[str]]:
    """The normalized token sequence, and the LEXEMES: the names and literals as written."""
    out, lex, stack = [], [], [node]
    while stack:
        n = stack.pop()
        if n.child_count == 0:
            k = _kind(n)
            if k is not None:
                out.append(k)
                if k in ("I", "L"):
                    lex.append(deps._txt(src, n))
            continue
        if "comment" in n.type:
            continue
        stack.extend(reversed(n.children))
    return out, lex


def _name(src: bytes, n) -> str:
    f = n.child_by_field_name("name")
    if f is None and n.type == "function_body" and n.prev_sibling is not None:
        f = n.prev_sibling  # Dart: the signature is the sibling before the body
        g = f.child_by_field_name("name")
        if g is None:
            for c in deps._walk(f):
                if c.child_by_field_name("name") is not None:
                    g = c.child_by_field_name("name")
                    break
        f = g
    if f is None and n.type == "function_definition":
        d = n.child_by_field_name("declarator")  # C/C++: the name sits inside the declarator
        while d is not None and d.child_by_field_name("declarator") is not None:
            d = d.child_by_field_name("declarator")
        f = d
    return deps._txt(src, f)[:80] if f is not None else "<anonymous>"


def _inline_test(src: bytes, n) -> bool:
    """A test written inside a production file: Rust `#[test]` / `mod tests` / `#[cfg(test)]`."""
    def attrs(x):
        p = x.prev_named_sibling
        while p is not None and p.type == "attribute_item":
            yield deps._txt(src, p)
            p = p.prev_named_sibling
    if any("test" in a for a in attrs(n)):
        return True
    a = n.parent
    while a is not None:
        if a.type == "mod_item" and (deps._txt(src, a.child_by_field_name("name")) == "tests"
                                     if a.child_by_field_name("name") is not None else False
                                     or any("cfg(test)" in t for t in attrs(a))):
            return True
        a = a.parent
    return False


def units_of(adapter, src: bytes, min_tokens: int) -> list[dict]:
    tree = adapter.parser.parse(src)
    kinds = FUNCS.get(adapter.lang, ())
    found = []
    for n in deps._walk(tree.root_node):
        if n.type in kinds:
            toks, lex = _tokens(src, n)
            if len(toks) < min_tokens:
                continue
            sh = [zlib.crc32(" ".join(toks[i:i + SHINGLE]).encode())
                  for i in range(len(toks) - SHINGLE + 1)]
            found.append({"name": _name(src, n), "start": n.start_point[0] + 1,
                          "end": n.end_point[0] + 1, "b0": n.start_byte, "b1": n.end_byte,
                          "tokens": len(toks), "sh": sh,
                          "logic": any(t in CONTROL for t in toks),
                          "test": adapter.lang == "rust" and _inline_test(src, n),
                          "lx": [zlib.crc32(x.encode()) for x in lex]})
    return found


def _as_set(items) -> frozenset:
    """A multiset made a set: the third occurrence of a shingle is its own element, so the
    overlap of two functions counts a shingle that appears three times in both as three."""
    occ: collections.Counter = collections.Counter()
    out = []
    for h in items:
        occ[h] += 1
        out.append((h, occ[h]))
    return frozenset(out)


def _overlap(a: frozenset, b: frozenset) -> float:
    return len(a & b) / max(len(a), len(b)) if a and b else 0.0


def _candidates(sets: list[frozenset], t: float) -> set[tuple[int, int]]:
    """Pairs that CAN reach overlap t. sim = |A∩B| / max(|A|,|B|) >= t implies |A∩B| >= t·|A|,
    so two such sets share an element among the first |A| - ceil(t·|A|) + 1 of A's rarest:
    each set is indexed by that prefix only (prefix filtering, as in SourcererCC)."""
    freq: collections.Counter = collections.Counter(x for s in sets for x in s)
    index: dict = collections.defaultdict(list)
    for i, s in enumerate(sets):
        if not s:
            continue
        ordered = sorted(s, key=lambda x: (freq[x], x))
        for x in ordered[: len(ordered) - math.ceil(t * len(ordered)) + 1]:
            index[x].append(i)
    cand: set[tuple[int, int]] = set()
    for ids in index.values():
        for k, i in enumerate(ids):
            for j in ids[k + 1:]:
                if min(len(sets[i]), len(sets[j])) >= t * max(len(sets[i]), len(sets[j])):
                    cand.add((i, j) if i < j else (j, i))
    return cand


def collect_similar(repo: Path, out: Path, cache_dir: Path, src_roots: list[str],
                    similarity: float, min_tokens: int, lexical: float = 0.5,
                    test_names=deps.TEST_DIRS) -> dict:
    files = deps.source_files(repo, src_roots)
    by_ext, missing, _ = deps.adapter_table(files)

    cache_path = cache_dir / "similar-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("version") != f"{_CACHE_KEY}:{min_tokens}":
            cache = {}
    except (OSError, ValueError):
        cache = {}
    old, new = cache.get("files", {}), {}
    parsed = errors = 0
    for f in files:
        a = by_ext.get(f.suffix.lower())
        if a is None or not FUNCS.get(a.lang):
            continue
        rel = f.relative_to(repo).as_posix()
        try:
            data = f.read_bytes()
        except OSError:
            continue
        sha = hashlib.sha1(data).hexdigest()
        hit = old.get(rel)
        if hit and hit.get("sha") == sha:
            new[rel] = hit
            continue
        try:
            new[rel] = {"sha": sha, "units": units_of(a, data, min_tokens)}
        except Exception:  # noqa: BLE001 - one unparsable file must not sink the run
            new[rel] = {"sha": sha, "units": [], "error": True}
            errors += 1
        parsed += 1
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": f"{_CACHE_KEY}:{min_tokens}", "files": new}),
                   encoding="utf-8")
    tmp.replace(cache_path)

    units = [(rel, u) for rel in sorted(new) for u in new[rel]["units"]]
    shs = [_as_set(u["sh"]) for _, u in units]
    lxs = [_as_set(u.get("lx", ())) for _, u in units]
    cand = _candidates(lxs, lexical)

    tests = {rel for rel in new if deps.is_test_path(rel, test_names)}
    pairs = []
    for i, j in cand:
        (ra, ua), (rb, ub) = units[i], units[j]
        if ra == rb and (ua["b0"] <= ub["b0"] < ua["b1"] or ub["b0"] <= ua["b0"] < ub["b1"]):
            continue  # one function nested inside the other is not a copy of it
        lex = _overlap(lxs[i], lxs[j])
        if lex < lexical:
            continue
        sim = _overlap(shs[i], shs[j])
        if sim < similarity:
            continue
        pairs.append({"similarity": round(sim, 3), "lexical": round(lex, 3),
                      "tokens": max(ua["tokens"], ub["tokens"]),
                      "a": ra, "a_start": ua["start"], "a_end": ua["end"], "a_name": ua["name"],
                      "b": rb, "b_start": ub["start"], "b_end": ub["end"], "b_name": ub["name"],
                      "a_logic": ua.get("logic", True), "b_logic": ub.get("logic", True),
                      "a_test": ra in tests or ua.get("test", False),
                      "b_test": rb in tests or ub.get("test", False), "_i": i, "_j": j})
    pairs.sort(key=lambda p: (-p["similarity"], -p["tokens"], p["a"], p["a_start"]))

    # --- families: the connected components of the similarity pairs
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for p in pairs:
        parent[find(p["_i"])] = find(p["_j"])
    groups = collections.defaultdict(list)
    for p in pairs:
        for k in ("_i", "_j"):
            groups[find(p[k])].append(p[k])
    families = []
    for members in groups.values():
        ms = sorted(set(members))
        if len(ms) < 3:
            continue
        families.append({"size": len(ms), "members": [
            {"file": units[m][0], "start": units[m][1]["start"], "end": units[m][1]["end"],
             "name": units[m][1]["name"], "logic": units[m][1].get("logic", True),
             "test": units[m][0] in tests or units[m][1].get("test", False)} for m in ms]})
    families.sort(key=lambda f: (-f["size"], f["members"][0]["file"]))
    for p in pairs:
        del p["_i"], p["_j"]

    out.mkdir(parents=True, exist_ok=True)
    (out / "similar.json").write_text(json.dumps(
        {"similarity": similarity, "lexical": lexical, "min_tokens": min_tokens,
         "shingle": SHINGLE,
         "pairs": pairs, "families": families}, indent=1) + "\n", encoding="utf-8")
    prod = [p for p in pairs if not (p["a_test"] or p["b_test"])]
    return {"files": len(new), "parsed": parsed, "errors": errors, "units": len(units),
            "pairs": len(pairs), "prod_pairs": len(prod), "families": len(families),
            "missing_grammars": missing, "top": prod[:8]}
