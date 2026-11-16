#!/usr/bin/env python3
"""The thresholds of the SOLID facts and signals (spec §7): the defaults, overridden by
`audit/solid.json` of the analysed project, every key optional. A threshold is configuration,
never a constant in the code that applies it."""

from __future__ import annotations

import copy
import json
from pathlib import Path

DEFAULTS = {"srp": {"lcom4_max": 1, "cochange_k": 3, "max_commit_files": 20},
            "ocp": {"dispatch_min_branches": 3, "repeat_min_sites": 2,
                    "kind_enum_names": ["Kind", "Type", "Mode"]}}


def load_config(repo: Path) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    p = Path(repo) / "audit" / "solid.json"
    if p.is_file():
        for section, values in json.loads(p.read_text(encoding="utf-8")).items():
            cfg.setdefault(section, {}).update(values)
    return cfg
