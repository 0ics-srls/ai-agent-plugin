#!/usr/bin/env python3
"""F5c — REPEATED code: the same sequence of statements written in many places.

The defect this exists for: the same few lines live in forty files, one gets fixed, thirty-nine
keep the bug. A clone detector that compares whole functions or long token runs misses it — two
lines repeated inside forty different functions are below any function-level threshold. So the
unit here is the STATEMENT, and the question is "where else is this exact code written?".

How — algorithmic, the method of the clone-class detectors (CCFinder and its family):

  1. every block of every function (if/for/while bodies included) is cut into its statements by
     the file's tree-sitter grammar — the same grammars as the dependency graph;
  2. each statement is normalized: a local name or a literal becomes a placeholder, but a name
     after a dot (`.own(`, `.State`) and a name that is called (`foo(`) stay as written — that is
     what makes two snippets the same code rather than the same shape;
  3. every run of consecutive statements is hashed, and the runs written in at least
     `--min-places` places are kept; a run is reported only at its MAXIMAL length (if all its
     places extend by one more identical statement, the longer run is the one reported);
  4. families are ranked by duplicated mass: tokens × (places − 1).

What comes out is a FACT, not a suspect: the code IS written in all those places, and the report
lists every one of them. Whether to unify it is the project's decision, recorded once.

Writes `repeats.json` (every family with all its places) and returns a summary. Incremental like
the graph: each file's statements are cached under the sha1 of its content.
"""

from __future__ import annotations

import collections
import hashlib
import json
import zlib
from pathlib import Path

import deps
import similar

CACHE_VERSION = 4
_CACHE_KEY = f"{CACHE_VERSION}:{hashlib.sha1(Path(__file__).read_bytes()).hexdigest()}"

BLOCKS = {"block", "body", "compound_statement", "statement_block", "function_body",
          "declaration_list", "class_body", "statements", "suite", "switch_block",
          "switch_body", "match_body", "case_block", "else_clause_body"}
MAX_RUN = 12  # statements in one run; longer repeats are reported at this length


def _norm_tokens(src: bytes, node) -> list[str]:
    """The statement's tokens: names after a dot and called names kept, other names and
    literals abstracted, comments dropped."""
    leaves = []
    stack = [node]
    while stack:
        n = stack.pop()
        if "comment" in n.type:
            continue
        if n.child_count == 0:
            leaves.append(n)
            continue
        stack.extend(reversed(n.children))
    out = []
    for i, n in enumerate(leaves):
        k = similar._kind(n)
        if k is None:
            continue
        if k == "I":
            prev = deps._txt(src, leaves[i - 1]) if i > 0 else ""
            nxt = deps._txt(src, leaves[i + 1]) if i + 1 < len(leaves) else ""
            if prev in (".", "->", "::", "?.") or nxt == "(":
                k = deps._txt(src, n)
        out.append(k)
    return out


def _kept(tokens: list[str]) -> set[str]:
    """The names kept as written (called, or after a dot): the content of a statement. A run
    with fewer than two of them — `var a = points[i-1]`, `x = p_x` — is an idiom of the language,
    not code someone copied."""
    return {t for t in tokens if t not in ("I", "L") and (t[:1].isalpha() or t[:1] == "_")
            and not _KEYWORD(t)}


def _KEYWORD(t: str) -> bool:
    return t in KEYWORDS


KEYWORDS = {"var", "let", "const", "val", "func", "fn", "def", "function", "return", "if", "else",
            "elif", "for", "while", "in", "and", "or", "not", "is", "as", "new", "null", "nil",
            "None", "true", "false", "True", "False", "self", "this", "super", "static", "await",
            "pass", "break", "continue", "match", "case", "switch", "default", "do", "try",
            "catch", "finally", "throw", "raise", "yield", "lambda", "void", "public", "private",
            "protected", "class", "struct", "enum", "import", "from", "export", "package", "use",
            "mut", "ref", "out", "where", "when", "then", "end", "begin", "local", "global",
            "auto", "int", "float", "bool", "string", "double", "char", "long", "short"}


def _blocks(fn_node):
    """Every statement list inside a function: its body and every nested block."""
    for n in deps._walk(fn_node):
        if n.type in BLOCKS:
            stmts = [c for c in n.named_children if "comment" not in c.type]
            if stmts:
                yield stmts


def statements_of(adapter, src: bytes) -> list[dict]:
    tree = adapter.parser.parse(src)
    kinds = similar.FUNCS.get(adapter.lang, ())
    out = []
    seen_blocks = set()
    for fn in deps._walk(tree.root_node):
        if fn.type not in kinds:
            continue
        name = similar._name(src, fn)
        inline_test = adapter.lang == "rust" and similar._inline_test(src, fn)
        for stmts in _blocks(fn):
            # a nested function walks the same block again, and some grammars wrap one statement
            # list in two nodes (`function_body` > `statements`): one block per first statement
            key = stmts[0].start_byte
            if key in seen_blocks:
                continue
            seen_blocks.add(key)
            out.append({"fn": name, "test": inline_test, "s": [
                [zlib.crc32(" ".join(t).encode()), len(t), s.start_point[0] + 1, s.end_point[0] + 1,
                 sorted(_kept(t)), any(x in similar.CONTROL for x in t)]
                for s in stmts for t in [_norm_tokens(src, s)] if t]})
    return out


def collect_repeats(repo: Path, out: Path, cache_dir: Path, src_roots: list[str],
                    min_tokens: int = 20, min_places: int = 3, min_mass: int = 120,
                    min_content: int = 2,
                    module_of=None, roots=None,
                    depth: int = 2, test_names=deps.TEST_DIRS) -> dict:
    files = deps.source_files(repo, src_roots)
    by_ext, missing, _ = deps.adapter_table(files)
    cache_path = cache_dir / "repeats-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("version") != _CACHE_KEY:
            cache = {}
    except (OSError, ValueError):
        cache = {}
    old, new = cache.get("files", {}), {}
    for f in files:
        a = by_ext.get(f.suffix.lower())
        if a is None or not similar.FUNCS.get(a.lang):
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
            new[rel] = {"sha": sha, "blocks": statements_of(a, data)}
        except Exception:  # noqa: BLE001 - one unparsable file must not sink the run
            new[rel] = {"sha": sha, "blocks": []}
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": _CACHE_KEY, "files": new}), encoding="utf-8")
    tmp.replace(cache_path)

    # --- every run of consecutive statements, hashed; a place is (file, block, start index)
    runs: dict[tuple[int, int], list[tuple[str, int, int]]] = collections.defaultdict(list)
    tokens_of: dict[tuple[int, int], int] = {}
    at: dict[tuple[str, int, int, int], tuple[int, int]] = {}
    blocks = []
    for rel in sorted(new):
        for b in new[rel]["blocks"]:
            bid = len(blocks)
            blocks.append((rel, b))
            s = b["s"]
            for i in range(len(s)):
                h, tok = 0, 0
                for k in range(1, min(MAX_RUN, len(s) - i) + 1):
                    h = zlib.crc32(str(s[i + k - 1][0]).encode(), h)
                    tok += s[i + k - 1][1]
                    key = (h, k)
                    at[(rel, bid, i, k)] = key
                    if tok >= min_tokens:
                        runs[key].append((rel, bid, i))
                        tokens_of[key] = tok

    families = []
    for key, all_places in runs.items():
        # ONE place per block: the same line written ten times in a row inside one function is a
        # list, not a copy — what matters is how many DIFFERENT places hold the code
        first: dict[int, tuple[str, int, int]] = {}
        for p in all_places:
            if p[1] not in first or p[2] < first[p[1]][2]:
                first[p[1]] = p
        places = sorted(first.values())
        files_of = {p[0] for p in places}
        r0, b0, i0 = places[0]
        run = blocks[b0][1]["s"][i0:i0 + key[1]]
        logic = any(len(st) > 5 and st[5] for st in run)
        # three places — or two, when what is copied is a long piece of LOGIC (a decision or a
        # loop): a copy in one other file is exactly the one a fix never reaches
        enough = len(places) >= min_places or (len(places) == 2 and logic
                                                and tokens_of[key] >= 2 * min_tokens + 20)
        if not enough or len(files_of) < 2 or tokens_of[key] * len(places) < min_mass:
            continue  # a short line passes only when it is written in many places
        content = {n for st in run for n in (st[4] if len(st) > 4 else ())}
        if len(content) < min_content:
            continue  # an idiom of the language, not code somebody copied
        h, k = key
        # maximal only: if every place extends by one identical statement, the longer run wins
        if k < MAX_RUN:
            right = {at.get((r, b, i, k + 1)) for r, b, i in places}
            left = {at.get((r, b, i - 1, k + 1)) for r, b, i in places}
            if (len(right) == 1 and None not in right and
                    len({q[1] for q in runs.get(next(iter(right)), ())}) >= len(places)) or \
                    (len(left) == 1 and None not in left and
                     len({q[1] for q in runs.get(next(iter(left)), ())}) >= len(places)):
                continue
        locs = []
        for r, b, i in places:
            st = blocks[b][1]["s"]
            locs.append({"file": r, "start": st[i][2], "end": st[i + k - 1][3],
                         "fn": blocks[b][1]["fn"],
                         "test": deps.is_test_path(r, test_names) or blocks[b][1].get("test", False)})
        mods = sorted({module_of(l["file"], roots, depth) or "?" for l in locs}) if module_of \
            else []
        families.append({"key": f"{h:08x}:{k}", "places": len(locs), "files": len(files_of),
                         "statements": k, "logic": logic,
                         "tokens": tokens_of[key], "mass": tokens_of[key] * (len(locs) - 1),
                         "modules": mods, "locations": sorted(locs, key=lambda l: (l["file"],
                                                                                    l["start"]))})
    # one place can sit in several maximal families of different length: keep a family only if
    # it is not entirely inside a bigger-mass family's places
    families.sort(key=lambda f: (-f["places"], -f["mass"]))
    kept, covered = [], set()
    for f in families:
        spots = {(l["file"], l["start"], l["end"]) for l in f["locations"]}
        inside = all(any(c[0] == s[0] and c[1] <= s[1] and s[2] <= c[2] for c in covered)
                     for s in spots)
        if inside:
            continue
        # a longer run that starts where most places of a bigger family start is a VARIANT of
        # it (the same line, plus what some places do next), reported with it
        starts = {(l["file"], l["start"]) for l in f["locations"]}
        host = next((g for g in kept if len(starts & {(l["file"], l["start"])
                                                      for l in g["locations"]}) * 5
                     >= 4 * len(starts)), None)
        if host is not None:
            host.setdefault("variants", []).append(
                {"places": f["places"], "statements": f["statements"], "tokens": f["tokens"]})
            covered |= spots
            continue
        kept.append(f)
        covered |= spots
    kept.sort(key=lambda f: (-f["mass"], -f["places"]))
    out.mkdir(parents=True, exist_ok=True)
    (out / "repeats.json").write_text(json.dumps(
        {"min_tokens": min_tokens, "min_places": min_places, "families": kept}, indent=1) + "\n",
        encoding="utf-8")
    prod = [f for f in kept if sum(not l["test"] for l in f["locations"]) >= min_places]
    return {"files": len(new), "families": len(kept), "prod_families": len(prod),
            "missing_grammars": missing, "top": prod[:10]}
