#!/usr/bin/env python3
"""The object-oriented facts the SOLID facts and signals are computed from
(tasks/13-solid-signals/spec.md §2).

Each fact has an id built from what it IS — the type, the method, the line — never from when it
was found, so two runs on the same code produce the same ids, a finding can cite them, and two runs
can be diffed. Every entity is a frozen dataclass; the facts of one file are a `FileFacts`, whose
JSON is byte-identical whatever the order the facts were collected in.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields

KINDS = {"class", "interface", "struct", "record", "enum", "protocol"}
BODIES = {"empty", "throw", "other"}
CATCH_BODIES = frozenset({"empty", "rethrow", "log-only", "other"})


@dataclass(frozen=True, order=True)
class TypeFact:
    full_name: str
    kind: str
    abstract: bool
    file: str
    line: int
    package: str = ""
    bases: tuple[str, ...] = ()  # names as written; resolved by oo_build

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"kind {self.kind!r} not in {sorted(KINDS)}")

    @property
    def id(self) -> str:
        return f"type:{self.full_name}"


@dataclass(frozen=True, order=True)
class MethodFact:
    owner: str  # TypeFact.full_name
    name: str
    arity: int
    line: int
    end_line: int
    is_ctor: bool = False
    is_dtor: bool = False
    is_static: bool = False
    is_abstract: bool = False
    is_virtual: bool = False
    is_override: bool = False  # declared (C#); for Python and GDScript set by oo_build
    is_builder: bool = False   # a static record builder: new(), parameters to fields, return it

    @property
    def id(self) -> str:
        return f"method:{self.owner}#{self.name}/{self.arity}"


@dataclass(frozen=True, order=True)
class FieldFact:
    owner: str
    name: str
    line: int = 0
    declared_type: str = ""

    @property
    def id(self) -> str:
        return f"field:{self.owner}.{self.name}"


@dataclass(frozen=True, order=True)
class AccessFact:
    method: str  # MethodFact.id
    field: str   # FieldFact.id
    mode: str    # "r" | "w"
    line: int

    def __post_init__(self) -> None:
        if self.mode not in ("r", "w"):
            raise ValueError(f"mode {self.mode!r} is neither 'r' nor 'w'")

    @property
    def id(self) -> str:
        return f"access:{self.method}>{self.field}:{self.mode}@{self.line}"


@dataclass(frozen=True, order=True)
class CallFact:
    method: str            # the caller, MethodFact.id
    callee: str            # the callee name as written
    receiver: str          # "self" | a reference name | a type name | "" for a bare call
    line: int
    callee_type: str = ""  # the owner the callee resolves to, set by oo_build

    @property
    def id(self) -> str:
        return f"call:{self.method}>{self.callee}@{self.line}"


@dataclass(frozen=True, order=True)
class TypedRefFact:
    holder: str         # MethodFact.id, or TypeFact.id for a field
    name: str
    declared_type: str
    role: str           # "field" | "param" | "local"
    line: int
    resolved: str = ""  # TypeFact.full_name, set by oo_build
    also: tuple[str, ...] = ()  # the other project types the declared type names (Dictionary[K, V])

    @property
    def id(self) -> str:
        return f"tref:{self.holder}>{self.name}:{self.declared_type}@{self.line}"


@dataclass(frozen=True, order=True)
class TypeTestFact:
    method: str
    subject: str             # the tested expression, as written
    tested: tuple[str, ...]  # the type names (or enum members) the chain tests, in order
    branches: int            # branches of the chain this test belongs to (1 for a lone test)
    chain: str               # f"{method}@{first line of the chain}"
    line: int
    kind: str                # "type" | "enum"
    resolved: tuple[str, ...] = ()  # the project type each tested name is ("" if none), oo_build

    @property
    def id(self) -> str:
        return f"ttest:{self.method}@{self.line}"


@dataclass(frozen=True, order=True)
class OverrideBodyFact:
    method: str
    body: str  # "empty" | "throw" | "other"

    def __post_init__(self) -> None:
        if self.body not in BODIES:
            raise ValueError(f"body {self.body!r} not in {sorted(BODIES)}")

    @property
    def id(self) -> str:
        return f"obody:{self.method}"


@dataclass(frozen=True, order=True)
class CatchFact:
    """A catch of a method and what its body does: nothing, only throw again, only log, or more."""
    method: str  # MethodFact.id
    line: int
    body: str

    def __post_init__(self) -> None:
        if self.body not in CATCH_BODIES:
            raise ValueError(f"body {self.body!r} not in {sorted(CATCH_BODIES)}")

    @property
    def id(self) -> str:
        return f"catch:{self.method}@{self.line}"


@dataclass(frozen=True, order=True)
class MethodChangeFact:
    commit: str
    method: str

    @property
    def id(self) -> str:
        return f"mchange:{self.commit}>{self.method}"


# The collections of a FileFacts, and the entity each one holds.
COLLECTIONS = {"types": TypeFact, "methods": MethodFact, "fields": FieldFact,
               "accesses": AccessFact, "calls": CallFact, "trefs": TypedRefFact,
               "ttests": TypeTestFact, "obodies": OverrideBodyFact, "catches": CatchFact}


def _from_dict(cls, d: dict):
    """An entity from its asdict(), with the tuples JSON turned into lists given back."""
    kw = {}
    for f in fields(cls):
        v = d[f.name]
        kw[f.name] = tuple(v) if isinstance(v, list) else v
    return cls(**kw)


@dataclass
class FileFacts:
    file: str
    lang: str
    package: str = ""
    imports: list[str] = field(default_factory=list)
    types: list[TypeFact] = field(default_factory=list)
    methods: list[MethodFact] = field(default_factory=list)
    fields: list[FieldFact] = field(default_factory=list)
    accesses: list[AccessFact] = field(default_factory=list)
    calls: list[CallFact] = field(default_factory=list)
    trefs: list[TypedRefFact] = field(default_factory=list)
    ttests: list[TypeTestFact] = field(default_factory=list)
    obodies: list[OverrideBodyFact] = field(default_factory=list)
    catches: list[CatchFact] = field(default_factory=list)
    # method id -> "empty" | "throw" | "other", for the languages (Python, GDScript) whose override
    # is known only once oo_build has linked the bases; it turns these into OverrideBodyFacts
    bodies: dict[str, str] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FileFacts) and self.to_json() == other.to_json()

    def to_json(self) -> str:
        d: dict = {"file": self.file, "lang": self.lang, "package": self.package,
                   "imports": sorted(self.imports)}
        for name in COLLECTIONS:
            d[name] = [asdict(x) for x in sorted(getattr(self, name), key=lambda x: (x.id, x))]
        d["bodies"] = dict(sorted(self.bodies.items()))
        return json.dumps(d, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def from_json(text: str) -> "FileFacts":
        d = json.loads(text)
        ff = FileFacts(file=d["file"], lang=d["lang"], package=d["package"],
                       imports=list(d["imports"]))
        for name, cls in COLLECTIONS.items():
            setattr(ff, name, [_from_dict(cls, x) for x in d.get(name, [])])
        ff.bodies = dict(d.get("bodies", {}))
        return ff


@dataclass
class FactBase:
    """The facts of every file, merged and resolved (oo_build.py): what the SOLID facts and the
    signals are computed from. `extends` / `implements` map a type to the project types it
    inherits from, by kind of the base; `unresolved` counts, per kind of reference, what named no
    type of the project — the share a metric reports instead of guessing."""
    types: list[TypeFact] = field(default_factory=list)
    methods: list[MethodFact] = field(default_factory=list)
    fields: list[FieldFact] = field(default_factory=list)
    accesses: list[AccessFact] = field(default_factory=list)
    calls: list[CallFact] = field(default_factory=list)
    trefs: list[TypedRefFact] = field(default_factory=list)
    ttests: list[TypeTestFact] = field(default_factory=list)
    obodies: list[OverrideBodyFact] = field(default_factory=list)
    catches: list[CatchFact] = field(default_factory=list)
    extends: dict[str, list[str]] = field(default_factory=dict)
    implements: dict[str, list[str]] = field(default_factory=dict)
    unresolved: dict[str, int] = field(default_factory=dict)
    langs: dict[str, str] = field(default_factory=dict)  # file → language
    bodies: dict[str, str] = field(default_factory=dict)  # method id → empty | throw | other
    method_file: dict[str, str] = field(default_factory=dict)  # method id → the file it is in
    constructions: dict[str, str] = field(default_factory=dict)  # call id → the type it builds

    def to_json(self) -> str:
        d: dict = {name: [asdict(x) for x in sorted(getattr(self, name), key=lambda x: (x.id, x))]
                   for name in COLLECTIONS}
        for name in ("extends", "implements"):
            d[name] = {k: sorted(v) for k, v in sorted(getattr(self, name).items())}
        for name in ("unresolved", "langs", "bodies", "method_file", "constructions"):
            d[name] = dict(sorted(getattr(self, name).items()))
        return json.dumps(d, sort_keys=True, separators=(",", ":"))
