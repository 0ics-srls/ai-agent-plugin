#!/usr/bin/env python3
"""Which METHODS each commit modified (spec §5.2), for the method co-change signal.

One `git log -p -U0` over the source roots gives, per commit, the files it touched and the line
ranges of every hunk in the file the commit PRODUCED. Each range is mapped to the methods whose
lines contain it in that very version — the blob is parsed with oo_extract.extract_file, never with
a parser of this module — so a method later renamed or moved is counted under the name and lines it
had then. The methods of each blob are cached under its sha in audit/.tools/history-cache.json, so
a second run parses nothing it has parsed before. A commit touching more than
`srp.max_commit_files` files (a reformat, a move) is not a change of design, and is skipped.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import deps
import oo_extract
from oo_model import MethodChangeFact

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_HERE = Path(__file__).resolve().parent
_CACHE_KEY = hashlib.sha1(b"".join((_HERE / n).read_bytes()
                                   for n in ("history.py", "oo_extract.py"))).hexdigest()


def _git(repo: Path, *args: str, stdin: bytes | None = None) -> bytes | None:
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=repo, input=stdin,
                           capture_output=True, check=False)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def _commits(log: str):
    """(commit, number of files it touched, {path: [(first, last) post-image line ranges]})."""
    commit, files, ranges, path = None, 0, {}, None
    for line in log.splitlines():
        if line.startswith("@") and not line.startswith("@@"):
            if commit:
                yield commit, files, ranges
            commit, files, ranges, path = line[1:].strip(), 0, {}, None
        elif line.startswith(":"):
            files += 1
        elif line.startswith("+++ "):
            p = line[4:]
            path = p[2:] if p.startswith("b/") else None  # `+++ /dev/null`: a deletion
        elif path and (m := HUNK.match(line)):
            start, count = int(m.group(1)), int(m.group(2) or "1")
            # a pure deletion (+c,0) sits after line c of the new file
            ranges.setdefault(path, []).append((start, start + max(count, 1) - 1))
    if commit:
        yield commit, files, ranges


def _blobs(repo: Path, wanted: list[str]) -> dict[str, bytes]:
    out = _git(repo, "cat-file", "--batch", stdin="".join(f"{w}\n" for w in wanted).encode())
    blobs, i = {}, 0
    for w in wanted:
        if out is None:
            break
        nl = out.index(b"\n", i)
        header = out[i:nl].split()
        i = nl + 1
        if len(header) < 3 or header[1] != b"blob":
            continue
        size = int(header[2])
        blobs[w] = out[i:i + size]
        i += size + 1
    return blobs


def method_changes(repo: Path, src_roots: list[str], cache_dir: Path,
                   cfg: dict) -> list[MethodChangeFact] | None:
    repo = Path(repo)
    if _git(repo, "rev-parse", "--is-inside-work-tree") is None:
        return None
    log = _git(repo, "log", "-p", "-U0", "--raw", "--no-merges", "-M", "--relative",
               "--format=@%H", "--", *src_roots)
    if log is None:
        return None
    by_ext, _, _ = deps.adapter_table(deps.source_files(repo, src_roots))
    limit = cfg["srp"]["max_commit_files"]
    todo = []  # (commit, path, ranges)
    for commit, nfiles, ranges in _commits(log.decode("utf-8", "replace")):
        if nfiles > limit:
            continue
        for path, rs in ranges.items():
            a = by_ext.get(Path(path).suffix.lower())
            if a is not None and a.lang in oo_extract.EXTRACTORS and (repo / path).is_file() \
                    and not deps.is_excluded(Path(path).parts):
                todo.append((commit, path, rs, a))

    cache_dir = Path(cache_dir)
    cache_path = cache_dir / "history-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("version") != _CACHE_KEY:
            cache = {}
    except (OSError, ValueError):
        cache = {}
    methods: dict[str, list] = cache.get("blobs", {})
    keys = {(c, p): f"{c}:{p}" for c, p, _, _ in todo}
    missing = sorted({k for k in keys.values() if k not in methods})
    if missing:
        data = _blobs(repo, missing)
        for c, p, _, a in todo:
            k = keys[(c, p)]
            if k in methods:
                continue
            ff = oo_extract.extract_file(a, data.get(k, b""), p, roots=tuple(src_roots))
            methods[k] = [[m.id, m.line, m.end_line] for m in ff.methods]
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps({"version": _CACHE_KEY, "blobs": methods},
                                         sort_keys=True), encoding="utf-8")
    out = set()
    for c, p, rs, _ in todo:
        for mid, line, end in methods.get(keys[(c, p)], ()):
            if any(lo <= end and hi >= line for lo, hi in rs):
                out.add(MethodChangeFact(c, mid))
    return sorted(out, key=lambda f: f.id)
