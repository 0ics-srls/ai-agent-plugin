#!/usr/bin/env python3
"""One source file → its object-oriented facts (spec §2), per language, from the syntax tree.

Names are recorded as written — a base type, a declared type, a tested type, a receiver — and
resolving them to types of the project is oo_build.py's job. A fact the language does not write
down is not guessed: a `var` local has a type only when its initialiser is `new T(...)` (spec §3).
The parser is the one `deps.adapter_table` gives for the file; this module has none of its own.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath

import deps
import similar
import solid_config
from oo_model import (CatchFact, AccessFact, CallFact, FieldFact, FileFacts, MethodFact, OverrideBodyFact,
                      TypedRefFact, TypeFact, TypeTestFact)

THROW_TYPES = ("NotImplemented", "NotSupported")  # prefix match on the thrown type name
# an enum named as a kind: the default names of the configuration (spec §7); the configured ones
# narrow them in solid.py, which is where the threshold is applied
KIND_WORDS = tuple(solid_config.DEFAULTS["ocp"]["kind_enum_names"])


def extract_file(adapter, src: bytes, rel: str, roots: tuple[str, ...] = ()) -> FileFacts:
    """The facts of one file; `roots` are the source roots, which a module path starts below."""
    try:
        tree = adapter.parser.parse(src)
        return EXTRACTORS[adapter.lang](src, tree.root_node, rel, roots)
    except Exception:  # noqa: BLE001 - one unparsable file must not sink the run
        return FileFacts(file=rel, lang=adapter.lang)


def _line(n) -> int:
    return n.start_point[0] + 1


def _strip_generics(name: str) -> str:
    return name.split("<", 1)[0].strip()


# --- C# -----------------------------------------------------------------------------------------

CS_TYPES = {"class_declaration": "class", "interface_declaration": "interface",
            "struct_declaration": "struct", "record_declaration": "record",
            "record_struct_declaration": "record", "enum_declaration": "enum"}
CS_NAMESPACES = ("namespace_declaration", "file_scoped_namespace_declaration")
# The members that are methods: the function nodes of similar.py that sit directly in a type's
# body (a local function belongs to the method around it, an accessor to its property), plus the
# destructor, which similar.py does not compare.
CS_METHODS = (set(similar.FUNCS["csharp"]) - {"local_function_statement", "accessor_declaration"}
              | {"destructor_declaration"})
CS_PATTERNS = ("constant_pattern", "declaration_pattern", "recursive_pattern", "type_pattern")
CS_TYPE_NAMES = ("identifier", "qualified_name", "generic_name", "predefined_type")


def _csharp(src, root, rel, roots=()) -> FileFacts:
    ff = FileFacts(file=rel, lang="csharp")
    namespaces = [n for n in deps._walk(root) if n.type in CS_NAMESPACES]
    namespaces.sort(key=lambda n: n.start_byte)
    file_ns = next((deps._field(src, n, "name") for n in namespaces
                    if n.type == "file_scoped_namespace_declaration"), "")
    ff.package = deps._field(src, namespaces[0], "name") if namespaces else ""
    ff.imports = [deps._txt(src, n.named_children[-1]) for n in deps._walk(root)
                  if n.type == "using_directive" and n.named_children]
    for t in sorted((n for n in deps._walk(root) if n.type in CS_TYPES), key=lambda n: n.start_byte):
        ns = ".".join(deps._field(src, a, "name") for a in _ancestors(t)
                      if a.type == "namespace_declaration") or file_ns
        enclosing = [deps._field(src, a, "name") for a in _ancestors(t) if a.type in CS_TYPES]
        full = ".".join(filter(None, [ns, *enclosing, deps._field(src, t, "name")]))
        mods = _modifiers(src, t)
        kind = CS_TYPES[t.type]
        ff.types.append(TypeFact(full, kind, "abstract" in mods or kind == "interface", rel,
                                 _line(t), ns, tuple(_cs_bases(src, t))))
        members = _cs_members(t)
        fields = _cs_fields(src, members, full)
        ff.fields += fields
        ff.trefs += [TypedRefFact(f"type:{full}", f.name, f.declared_type, "field", f.line)
                     for f in fields if f.declared_type]
        field_names = {f.name for f in fields}
        for m, name, arity, implicit in _cs_methods(src, members):
            mf = _cs_method(src, m, full, kind, name, arity)
            ff.methods.append(mf)
            params, locals_ = _cs_declared(src, m)
            ff.accesses += _cs_accesses(src, m, mf.id, full, field_names,
                                        params | locals_ | implicit)
            ff.calls += _cs_calls(src, m, mf.id)
            ff.trefs += _cs_trefs(src, m, mf.id)
            ff.ttests += _cs_type_tests(src, m, mf.id)
            ff.catches += _catches(src, m, mf.id, "catch_clause", _cs_catch_statements)
            if m.child_by_field_name("body") is not None:
                ff.bodies[mf.id] = _cs_body_kind(src, m)
            if mf.is_override:
                ff.obodies.append(OverrideBodyFact(mf.id, _cs_body_kind(src, m)))
    return ff


# ---- catches: one judgement of a catch's body, for every language ------------------------------

LOGGERS = frozenset({"log", "logger", "_logger", "Log", "console", "tracing", "slog"})
THROWS = frozenset({"throw_statement", "throw_expression", "raise_statement",
                    "throw_keyword"})  # Swift: `throw e` is a control transfer whose keyword is named


def _call_head(src, stmt) -> str:
    """The receiver, or the name, of the call a statement is — "" when the statement is not a call."""
    call = next((n for n in deps._walk(stmt) if n.type in ("invocation_expression", "call",
                                                         "call_expression")), None)
    if call is None:
        return ""
    fn = (call.child_by_field_name("function") or call.child_by_field_name("expression")
          or (call.named_children[0] if call.named_children else None))
    if fn is None:
        return ""
    return deps._txt(src, fn).split("(")[0]


def catch_body(src, statements: list) -> str:
    if not statements:
        return "empty"
    if all(s.type in THROWS or any(c.type in THROWS for c in s.named_children) for s in statements):
        return "rethrow"
    if all(_call_head(src, s).split(".")[0].split("?")[0] in LOGGERS for s in statements):
        return "log-only"
    return "other"


def _catches(src, scope, method_id: str, clause: str, statements_of) -> list[CatchFact]:
    if scope is None:
        return []
    return [CatchFact(method_id, _line(c), catch_body(src, statements_of(c)))
            for c in deps._walk(scope) if c.type == clause]


def _cs_catch_statements(clause) -> list:
    block = clause.child_by_field_name("body") or next(
        (c for c in clause.named_children if c.type == "block"), None)
    return [s for s in block.named_children if s.type != "comment"] if block is not None else []


def _py_catch_statements(clause) -> list:
    block = next((c for c in clause.named_children if c.type == "block"), None)
    return [s for s in block.named_children
            if s.type not in ("comment", "pass_statement")] if block is not None else []


def _ancestors(n):
    p = n.parent
    while p is not None:
        yield p
        p = p.parent


def _modifiers(src, n) -> set[str]:
    return {deps._txt(src, c) for c in n.named_children if c.type == "modifier"}


def _cs_bases(src, t) -> list[str]:
    out = []
    for bl in (c for c in t.named_children if c.type == "base_list"):
        for b in bl.named_children:
            if b.type == "primary_constructor_base_type":
                b = b.child_by_field_name("type") or b
            if b.type in CS_TYPE_NAMES:
                out.append(_strip_generics(deps._txt(src, b)))
    return out


def _cs_members(t) -> list:
    body = t.child_by_field_name("body")
    return list(body.named_children) if body is not None else []


def _cs_has_bodies(prop) -> bool:
    if prop.child_by_field_name("value") is not None:  # `int P => x;`
        return True
    acc = prop.child_by_field_name("accessors")
    return acc is not None and any(a.child_by_field_name("body") is not None
                                   for a in acc.named_children)


def _cs_fields(src, members, owner) -> list[FieldFact]:
    out = []
    for m in members:
        if m.type == "field_declaration":
            decl = next((c for c in m.named_children if c.type == "variable_declaration"), None)
            if decl is None:
                continue
            typ = deps._field(src, decl, "type") or ""
            for v in decl.named_children:
                if v.type == "variable_declarator":
                    out.append(FieldFact(owner, deps._field(src, v, "name"), _line(v), typ))
        elif m.type == "property_declaration" and not _cs_has_bodies(m):
            out.append(FieldFact(owner, deps._field(src, m, "name"), _line(m),
                                 deps._field(src, m, "type") or ""))
    return out


def _cs_methods(src, members):
    """(node, name, arity, implicit parameters) for every method of the type, the accessors of a
    property with bodies included as get_P / set_P."""
    for m in members:
        if m.type in CS_METHODS:
            name = similar._name(src, m)
            if m.type == "destructor_declaration":
                name = "~" + name
            elif m.type == "operator_declaration":
                op = m.child_by_field_name("operator")
                name = "operator" + (deps._txt(src, op) if op is not None else "")
            params = m.child_by_field_name("parameters")
            arity = sum(1 for p in params.named_children if p.type == "parameter") if params else 0
            yield m, name, arity, set()
        elif m.type == "property_declaration" and _cs_has_bodies(m):
            prop = deps._field(src, m, "name")
            if m.child_by_field_name("value") is not None:
                yield m, f"get_{prop}", 0, set()
                continue
            for a in m.child_by_field_name("accessors").named_children:
                if a.child_by_field_name("body") is None:
                    continue
                word = next((deps._txt(src, c) for c in a.children
                             if deps._txt(src, c) in ("get", "set", "init")), "get")
                if word == "get":
                    yield a, f"get_{prop}", 0, set()
                else:
                    yield a, f"{word}_{prop}", 1, {"value"}


def _cs_method(src, m, owner, kind, name, arity) -> MethodFact:
    mods = _modifiers(src, m)
    has_body = m.child_by_field_name("body") is not None
    return MethodFact(owner=owner, name=name, arity=arity, line=_line(m),
                      end_line=m.end_point[0] + 1,
                      is_ctor=m.type == "constructor_declaration",
                      is_dtor=m.type == "destructor_declaration",
                      is_static="static" in mods,
                      is_abstract="abstract" in mods or (kind == "interface" and not has_body),
                      is_virtual="virtual" in mods, is_override="override" in mods)


def _cs_scope(m):
    """The nodes of a method that hold its code: the body, the constructor initializer."""
    return [c for c in m.named_children
            if c.type in ("block", "arrow_expression_clause", "constructor_initializer")]


def _cs_declared(src, m) -> tuple[set[str], set[str]]:
    params = set()
    p = m.child_by_field_name("parameters")
    if p is not None:
        params = {deps._field(src, x, "name") for x in p.named_children if x.type == "parameter"}
    locals_ = set()
    for s in _cs_scope(m):
        for n in deps._walk(s):
            if n.type in ("variable_declarator", "declaration_pattern", "catch_declaration",
                          "parameter", "local_function_statement"):
                nm = deps._field(src, n, "name")
            elif n.type == "foreach_statement":
                nm = deps._field(src, n, "left")
            elif n.type == "declaration_expression":
                nm = deps._field(src, n, "name")
            elif n.type == "lambda_expression":
                lp = n.child_by_field_name("parameters")
                nm = deps._txt(src, lp) if lp is not None and lp.type == "identifier" else None
            else:
                continue
            if nm:
                locals_.add(nm)
    return params, locals_


def _is_write(n) -> bool:
    p = n.parent
    if p is None:
        return False
    if p.type == "assignment_expression":
        return p.child_by_field_name("left") == n
    return p.type in ("postfix_unary_expression", "prefix_unary_expression") and any(
        c.type in ("++", "--") for c in p.children)


def _cs_accesses(src, m, mid, owner, field_names, shadowed) -> list[AccessFact]:
    out = []
    for s in _cs_scope(m):
        for n in deps._walk(s):
            if n.type == "member_access_expression":
                e = n.child_by_field_name("expression")
                name = deps._field(src, n, "name")
                if e is not None and e.type == "this" and name in field_names:
                    out.append(AccessFact(mid, f"field:{owner}.{name}",
                                          "w" if _is_write(n) else "r", _line(n)))
            elif n.type == "identifier" and deps._txt(src, n) in field_names:
                name = deps._txt(src, n)
                p = n.parent
                field = p.field_name_for_child(_index(p, n)) if p is not None else None
                # a declaration, a type, a called name or `a.x` are not this type's field x
                if name in shadowed or field in ("name", "type", "function") or (
                        p is not None and p.type in ("qualified_name", "generic_name",
                                                     "name_colon")):
                    continue
                out.append(AccessFact(mid, f"field:{owner}.{name}",
                                      "w" if _is_write(n) else "r", _line(n)))
    return out


def _index(parent, child) -> int:
    for i, c in enumerate(parent.children):
        if c == child:
            return i
    return -1


def _cs_calls(src, m, mid) -> list[CallFact]:
    """The calls of a method; a construction `new T(...)` is a call with the receiver "new"."""
    out = []
    for s in _cs_scope(m):
        for n in deps._walk(s):
            if n.type == "object_creation_expression":
                t = deps._field(src, n, "type")
                if t:
                    out.append(CallFact(mid, _strip_generics(t).rsplit(".", 1)[-1], "new",
                                        _line(n)))
                continue
            if n.type != "invocation_expression":
                continue
            f = n.child_by_field_name("function")
            if f is None:
                continue
            if f.type == "member_access_expression":
                e = f.child_by_field_name("expression")
                recv = deps._txt(src, e) if e is not None else ""
                callee = _strip_generics(deps._field(src, f, "name") or "")
                out.append(CallFact(mid, callee, "self" if recv == "this" else recv, _line(n)))
            elif f.type in ("identifier", "generic_name"):
                out.append(CallFact(mid, _strip_generics(deps._txt(src, f)), "", _line(n)))
            elif f.type == "member_binding_expression":  # a?.B()
                cond = n.parent.named_children[0] if n.parent is not None else None
                recv = deps._txt(src, cond) if cond is not None and cond != n else ""
                out.append(CallFact(mid, _strip_generics(deps._field(src, f, "name") or ""),
                                    recv, _line(n)))
    return out


def _cs_trefs(src, m, mid) -> list[TypedRefFact]:
    out = []
    p = m.child_by_field_name("parameters")
    for x in (p.named_children if p is not None else []):
        if x.type == "parameter" and x.child_by_field_name("type") is not None:
            out.append(TypedRefFact(mid, deps._field(src, x, "name"), deps._field(src, x, "type"),
                                    "param", _line(x)))
    for s in _cs_scope(m):
        for n in deps._walk(s):
            if n.type != "variable_declaration":
                continue
            t = n.child_by_field_name("type")
            for v in n.named_children:
                if v.type != "variable_declarator":
                    continue
                typ = deps._txt(src, t) if t is not None else ""
                if t is not None and t.type == "implicit_type":
                    init = next((c for c in v.named_children
                                 if c.type == "object_creation_expression"), None)
                    typ = deps._field(src, init, "type") if init is not None else ""
                if typ:
                    out.append(TypedRefFact(mid, deps._field(src, v, "name"), typ, "local",
                                            _line(v)))
    return out


def _cs_pattern(src, pat) -> tuple[str, str] | None:
    """(tested name, "type" | "enum") of a pattern, or None when it tests no type."""
    if pat.type in ("declaration_pattern", "recursive_pattern", "type_pattern"):
        t = pat.child_by_field_name("type")
        return (deps._txt(src, t), "type") if t is not None else None
    if pat.type == "constant_pattern" and pat.named_children:
        c = pat.named_children[0]
        if c.type in CS_TYPE_NAMES:
            return deps._txt(src, c), "type"
        if c.type == "member_access_expression":
            return _kind_member(src, c)
    return None


def _kind_member(src, n) -> tuple[str, str] | None:
    e = n.child_by_field_name("expression")
    left = deps._txt(src, e).rsplit(".", 1)[-1] if e is not None else ""
    return (deps._txt(src, n), "enum") if left.endswith(KIND_WORDS) else None


def _cs_condition(src, c) -> tuple[str, str, str] | None:
    """(subject, tested, kind) of an if condition that tests a type or a kind enum."""
    if c.type == "is_pattern_expression":
        e, pat = c.child_by_field_name("expression"), c.child_by_field_name("pattern")
        got = _cs_pattern(src, pat) if pat is not None else None
        return (deps._txt(src, e), *got) if got and e is not None else None
    if c.type == "is_expression":
        e, t = c.child_by_field_name("left"), c.child_by_field_name("right")
        return (deps._txt(src, e), deps._txt(src, t), "type") if e and t else None
    if c.type == "binary_expression" and any(x.type == "==" for x in c.children):
        left, right = c.child_by_field_name("left"), c.child_by_field_name("right")
        if left is not None and right is not None and right.type == "member_access_expression":
            got = _kind_member(src, right)
            return (deps._txt(src, left), *got) if got else None
    return None


def _chain_facts(mid, links) -> list[TypeTestFact]:
    """links: (line, subject, tested, kind) in order; the ones on the first subject and kind form
    the chain, the others are lone tests."""
    if not links:
        return []
    _, subject, _, kind = links[0]
    on = [x for x in links if x[1] == subject and x[3] == kind]
    tested = tuple(x[2] for x in on)
    chain = f"{mid}@{links[0][0]}"
    out = [TypeTestFact(mid, subject, tested, len(on), chain, line, kind) for line, _, _, _ in on]
    for line, s, t, k in links:
        if (s, k) != (subject, kind):
            out.append(TypeTestFact(mid, s, (t,), 1, f"{mid}@{line}", line, k))
    return out


def _cs_type_tests(src, m, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    for s in _cs_scope(m):
        for n in deps._walk(s):
            if n.type == "if_statement" and not (n.parent is not None
                                                 and n.parent.type == "if_statement"
                                                 and n.parent.child_by_field_name("alternative") == n):
                links, link = [], n
                while link is not None and link.type == "if_statement":
                    c = link.child_by_field_name("condition")
                    got = _cs_condition(src, c) if c is not None else None
                    if got:
                        in_chain.add(c.id)
                        links.append((_line(c), *got))
                    link = link.child_by_field_name("alternative")
                out += _chain_facts(mid, links)
            elif n.type in ("switch_statement", "switch_expression"):
                subj = (n.child_by_field_name("value") if n.type == "switch_statement"
                        else n.named_children[0] if n.named_children else None)
                if subj is None:
                    continue
                pats = []
                for sec in deps._walk(n):
                    if sec.type in ("switch_section", "switch_expression_arm") and _owner_switch(sec) == n:
                        pats += [p for p in sec.named_children if p.type in CS_PATTERNS]
                pats.sort(key=lambda p: p.start_byte)  # deps._walk does not keep source order
                links = [(_line(p), deps._txt(src, subj), *got)
                         for p in pats if (got := _cs_pattern(src, p))]
                out += _chain_facts(mid, links)
            elif n.type == "as_expression":
                left, right = n.child_by_field_name("left"), n.child_by_field_name("right")
                if left is not None and right is not None:
                    out.append(TypeTestFact(mid, deps._txt(src, left), (deps._txt(src, right),),
                                            1, f"{mid}@{_line(n)}", _line(n), "type"))
            elif n.type in ("is_pattern_expression", "is_expression") and n.id not in in_chain:
                got = _cs_condition(src, n)
                if got:
                    out.append(TypeTestFact(mid, got[0], (got[1],), 1, f"{mid}@{_line(n)}",
                                            _line(n), got[2]))
    return out


def _owner_switch(n):
    return next((a for a in _ancestors(n) if a.type in ("switch_statement", "switch_expression")),
                None)


def _cs_body_kind(src, m) -> str:
    body = m.child_by_field_name("body")
    if body is None:
        return "empty"
    if body.type == "arrow_expression_clause":
        stmts = [c for c in body.named_children if c.type != "comment"]
        thrown = stmts[0] if stmts and stmts[0].type == "throw_expression" else None
    else:
        stmts = [c for c in body.named_children if c.type != "comment"]
        if not stmts:
            return "empty"
        thrown = stmts[0] if len(stmts) == 1 and stmts[0].type == "throw_statement" else None
    if thrown is not None:
        new = next((c for c in thrown.named_children if c.type == "object_creation_expression"),
                   None)
        name = deps._field(src, new, "type") if new is not None else ""
        if name and _strip_generics(name).rsplit(".", 1)[-1].startswith(THROW_TYPES):
            return "throw"
    return "other"



# --- Python -------------------------------------------------------------------------------------

PY_PARAMS = ("identifier", "typed_parameter", "default_parameter", "typed_default_parameter",
             "list_splat_pattern", "dictionary_splat_pattern")
PY_TARGETS = ("pattern_list", "tuple_pattern", "list_pattern")  # `self.a, self.b = ...`


def _module_of(rel: str, roots, ext: str, index: str) -> str:
    """`src/billing/x.py` → `billing.x` when `src` is a source root; else the path with dots. The
    file `index` of a folder (`__init__`, `index`) is the folder's module."""
    path = rel
    for r in sorted((r.strip("/") for r in roots if r.strip("/.")), key=len, reverse=True):
        if path.startswith(r + "/"):
            path = path[len(r) + 1:]
            break
    parts = path[:-len(ext)].split("/") if path.endswith(ext) else path.split("/")
    if parts and parts[-1] == index:
        parts = parts[:-1]
    return ".".join(parts)


def _py_module(rel: str, roots) -> str:
    return _module_of(rel, roots, ".py", "__init__")


def _python(src, root, rel, roots=()) -> FileFacts:
    ff = FileFacts(file=rel, lang="python", package=_py_module(rel, roots))
    if root.has_error:  # a syntax error: the tree around it is not the code that was meant
        return ff
    for n in deps._walk(root):
        if n.type == "import_statement":
            ff.imports += [deps._txt(src, c.child_by_field_name("name") or c)
                           for c in n.named_children]
        elif n.type == "import_from_statement":
            mod = deps._field(src, n, "module_name") or ""
            ff.imports += [f"{mod}.{deps._txt(src, c.child_by_field_name('name') or c)}"
                           for c in n.children_by_field_name("name")]
    for c in sorted((n for n in deps._walk(root) if n.type == "class_definition"),
                    key=lambda n: n.start_byte):
        enclosing = [deps._field(src, a, "name") for a in _ancestors(c)
                     if a.type == "class_definition"]
        full = ".".join(filter(None, [ff.package, *enclosing, deps._field(src, c, "name")]))
        bases = tuple(_py_bases(src, c))
        kind = "protocol" if "Protocol" in bases else "class"
        methods = list(_py_methods(src, c))
        flags = [(m, _py_method(src, m, decos, full, kind)) for m, decos in methods]
        abstract = (kind == "protocol" or bool({"ABC", "ABCMeta"} & set(bases))
                    or any(mf.is_abstract for _, mf in flags))
        ff.types.append(TypeFact(full, kind, abstract, rel, _line(c), ff.package, bases))
        fields = _py_fields(src, c, full, [m for m, _ in methods])
        ff.fields += fields
        ff.trefs += [TypedRefFact(f"type:{full}", f.name, f.declared_type, "field", f.line)
                     for f in fields if f.declared_type]
        field_names = {f.name for f in fields}
        for m, mf in flags:
            ff.methods.append(mf)
            me = _py_self(src, m, mf)
            body = m.child_by_field_name("body")
            ff.accesses += _py_accesses(src, body, mf.id, full, field_names, me)
            ff.calls += _py_calls(src, body, mf.id, me)
            ff.trefs += _py_trefs(src, m, body, mf.id)
            ff.ttests += _py_type_tests(src, body, mf.id)
            ff.catches += _catches(src, body, mf.id, "except_clause", _py_catch_statements)
            ff.bodies[mf.id] = _py_body_kind(src, body)
    # A function of the module belongs to no type: its owner is the module, which declares no
    # TypeFact, so the per-type metrics never see it — but its type switches are switches.
    for m, decos in _py_methods(src, root, body=root):
        name = deps._field(src, m, "name")
        mf = MethodFact(owner=ff.package, name=name, arity=len(_py_params(m)), line=_line(m),
                        end_line=m.end_point[0] + 1, is_static=True)
        ff.methods.append(mf)
        body = m.child_by_field_name("body")
        ff.calls += _py_calls(src, body, mf.id, "")
        ff.trefs += _py_trefs(src, m, body, mf.id)
        ff.ttests += _py_type_tests(src, body, mf.id)
        ff.catches += _catches(src, body, mf.id, "except_clause", _py_catch_statements)
        ff.bodies[mf.id] = _py_body_kind(src, body)
    return ff


def _py_bases(src, c) -> list[str]:
    sup = c.child_by_field_name("superclasses")
    if sup is None:
        return []
    out = []
    for b in sup.named_children:
        if b.type == "keyword_argument":  # metaclass=ABCMeta
            v = b.child_by_field_name("value")
            if v is not None:
                out.append(deps._txt(src, v).rsplit(".", 1)[-1])
        elif b.type in ("identifier", "attribute"):
            out.append(deps._txt(src, b).rsplit(".", 1)[-1])
        elif b.type == "subscript":  # Generic[T], Protocol[T]
            v = b.child_by_field_name("value")
            if v is not None:
                out.append(deps._txt(src, v).rsplit(".", 1)[-1])
    return out


def _py_methods(src, c, body=None):
    """(function_definition, decorator names) for the methods written in the class body — or,
    given `body`, for the functions written directly in it."""
    body = c.child_by_field_name("body") if body is None else body
    for n in (body.named_children if body is not None else []):
        decos = []
        if n.type == "decorated_definition":
            decos = [deps._txt(src, d).lstrip("@").split("(", 1)[0].rsplit(".", 1)[-1].strip()
                     for d in n.named_children if d.type == "decorator"]
            n = n.child_by_field_name("definition")
        if n is not None and n.type == "function_definition":
            yield n, decos


def _py_params(m) -> list:
    p = m.child_by_field_name("parameters")
    return [x for x in (p.named_children if p is not None else []) if x.type in PY_PARAMS]


def _py_param_name(src, x) -> str:
    if x.type == "identifier":
        return deps._txt(src, x)
    nm = x.child_by_field_name("name")
    if nm is None:
        nm = next((c for c in x.named_children if c.type == "identifier"), None)
    return deps._txt(src, nm) if nm is not None else ""


def _py_method(src, m, decos, owner, kind) -> MethodFact:
    name = deps._field(src, m, "name")
    static = "staticmethod" in decos
    arity = len(_py_params(m)) - (0 if static else 1)
    return MethodFact(owner=owner, name=name, arity=max(arity, 0), line=_line(m),
                      end_line=m.end_point[0] + 1, is_ctor=name == "__init__",
                      is_dtor=name == "__del__", is_static=static,
                      is_abstract="abstractmethod" in decos or kind == "protocol",
                      is_virtual=True)


def _py_self(src, m, mf) -> str:
    """The name the method calls its instance by — the first parameter — or "" if static."""
    ps = _py_params(m)
    return "" if mf.is_static or not ps else _py_param_name(src, ps[0])


def _py_self_attr(src, n, me) -> str | None:
    """`self.f` → "f"."""
    if n.type != "attribute" or not me:
        return None
    o = n.child_by_field_name("object")
    if o is None or o.type != "identifier" or deps._txt(src, o) != me:
        return None
    return deps._field(src, n, "attribute")


def _py_is_write(n) -> bool:
    p = n
    while p.parent is not None and p.parent.type in PY_TARGETS:
        p = p.parent
    a = p.parent
    return (a is not None and a.type in ("assignment", "augmented_assignment")
            and a.child_by_field_name("left") == p)


def _py_fields(src, c, owner, methods) -> list[FieldFact]:
    """Class-level names, and every `self.f = ...` of its methods; the first place declares it."""
    seen: dict[str, FieldFact] = {}
    body = c.child_by_field_name("body")
    for st in (body.named_children if body is not None else []):
        a = st.named_children[0] if st.type == "expression_statement" and st.named_children else None
        if a is not None and a.type == "assignment":
            left = a.child_by_field_name("left")
            if left is not None and left.type == "identifier":
                nm = deps._txt(src, left)
                seen.setdefault(nm, FieldFact(owner, nm, _line(a),
                                              _py_type(src, a.child_by_field_name("type"))))
    for m in methods:
        ps = _py_params(m)
        me = _py_param_name(src, ps[0]) if ps else ""
        for n in sorted(deps._walk(m), key=lambda n: n.start_byte):
            nm = _py_self_attr(src, n, me)
            if nm and _py_is_write(n):
                a = n.parent
                typ = _py_type(src, a.child_by_field_name("type")) if a.type == "assignment" else ""
                seen.setdefault(nm, FieldFact(owner, nm, _line(n), typ))
    return sorted(seen.values(), key=lambda f: f.line)


def _py_type(src, t) -> str:
    """A type annotation as written, a string annotation without its quotes."""
    if t is None:
        return ""
    return deps._txt(src, t).strip().strip("'\"")


def _py_accesses(src, body, mid, owner, field_names, me) -> list[AccessFact]:
    out = []
    for n in (deps._walk(body) if body is not None else []):
        nm = _py_self_attr(src, n, me)
        if nm in field_names:
            p = n.parent
            if p is not None and p.type == "call" and p.child_by_field_name("function") == n:
                continue
            out.append(AccessFact(mid, f"field:{owner}.{nm}", "w" if _py_is_write(n) else "r",
                                  _line(n)))
    return out


def _py_calls(src, body, mid, me) -> list[CallFact]:
    out = []
    for n in (deps._walk(body) if body is not None else []):
        if n.type != "call":
            continue
        f = n.child_by_field_name("function")
        if f is None:
            continue
        if f.type == "identifier":
            out.append(CallFact(mid, deps._txt(src, f), "", _line(n)))
        elif f.type == "attribute":
            o = f.child_by_field_name("object")
            recv = deps._txt(src, o) if o is not None else ""
            out.append(CallFact(mid, deps._field(src, f, "attribute") or "",
                                "self" if me and recv == me else recv, _line(n)))
    return out


def _py_trefs(src, m, body, mid) -> list[TypedRefFact]:
    out = []
    for x in _py_params(m):
        t = x.child_by_field_name("type") if x.type != "identifier" else None
        if t is not None:
            out.append(TypedRefFact(mid, _py_param_name(src, x), _py_type(src, t), "param",
                                    _line(x)))
    for n in (deps._walk(body) if body is not None else []):
        if n.type == "assignment" and n.child_by_field_name("type") is not None:
            left = n.child_by_field_name("left")
            if left is not None and left.type == "identifier":
                out.append(TypedRefFact(mid, deps._txt(src, left),
                                        _py_type(src, n.child_by_field_name("type")), "local",
                                        _line(n)))
    return out


def _py_kind_member(src, n) -> tuple[str, str] | None:
    """`ShapeKind.A` → ("ShapeKind.A", "enum") when the enum is named as a kind."""
    text = deps._txt(src, n)
    left = text.rsplit(".", 1)[0] if "." in text else ""
    return (text, "enum") if left and left.rsplit(".", 1)[-1].endswith(KIND_WORDS) else None


def _py_condition(src, c) -> tuple[str, str, str] | None:
    """(subject, tested, kind) of `isinstance(x, T)`, `type(x) is T` / `== T`, `x == Kind.A`."""
    if c.type == "call" and deps._field(src, c, "function") == "isinstance":
        args = c.child_by_field_name("arguments")
        a = [x for x in (args.named_children if args is not None else []) if x.type != "comment"]
        return (deps._txt(src, a[0]), deps._txt(src, a[1]), "type") if len(a) == 2 else None
    if c.type == "comparison_operator" and any(x.type in ("is", "==") for x in c.children):
        ops = [x for x in c.named_children]
        if len(ops) != 2:
            return None
        left, right = ops
        if left.type == "call" and deps._field(src, left, "function") == "type":
            args = left.child_by_field_name("arguments")
            a = args.named_children if args is not None else []
            return (deps._txt(src, a[0]), deps._txt(src, right), "type") if len(a) == 1 else None
        if right.type == "attribute":
            got = _py_kind_member(src, right)
            return (deps._txt(src, left), *got) if got else None
    return None


def _py_pattern(src, case) -> tuple[str, str] | None:
    pat = next((c for c in case.named_children if c.type == "case_pattern"), None)
    inner = pat.named_children[0] if pat is not None and pat.named_children else None
    if inner is None:
        return None
    if inner.type == "class_pattern":
        name = next((c for c in inner.named_children if c.type == "dotted_name"), None)
        return (deps._txt(src, name), "type") if name is not None else None
    if inner.type == "dotted_name" and len(inner.named_children) > 1:
        return _py_kind_member(src, inner)
    return None


def _py_type_tests(src, body, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    for n in (deps._walk(body) if body is not None else []):
        if n.type == "if_statement":
            links = []
            conds = [n.child_by_field_name("condition")] + [
                e.child_by_field_name("condition") for e in n.named_children
                if e.type == "elif_clause"]
            for c in conds:
                got = _py_condition(src, c) if c is not None else None
                if got:
                    in_chain.add(c.id)
                    links.append((_line(c), *got))
            out += _chain_facts(mid, links)
        elif n.type == "match_statement":
            subj = n.child_by_field_name("subject")
            mbody = n.child_by_field_name("body")
            cases = [c for c in (mbody.named_children if mbody is not None else [])
                     if c.type == "case_clause"]
            links = [(_line(c), deps._txt(src, subj), *got)
                     for c in cases if subj is not None and (got := _py_pattern(src, c))]
            out += _chain_facts(mid, links)
        elif n.type in ("call", "comparison_operator") and n.id not in in_chain:
            got = _py_condition(src, n)
            if got:
                out.append(TypeTestFact(mid, got[0], (got[1],), 1, f"{mid}@{_line(n)}",
                                        _line(n), got[2]))
    return out


def _py_body_kind(src, body) -> str:
    stmts = [s for s in (body.named_children if body is not None else []) if s.type != "comment"]
    if stmts and stmts[0].type == "expression_statement" and stmts[0].named_children and \
            stmts[0].named_children[0].type == "string":
        stmts = stmts[1:]  # the docstring
    if all(s.type == "pass_statement" or (s.type == "expression_statement" and s.named_children
                                          and s.named_children[0].type == "ellipsis")
           for s in stmts):
        return "empty"
    if len(stmts) == 1 and stmts[0].type == "raise_statement" and stmts[0].named_children:
        e = stmts[0].named_children[0]
        name = deps._field(src, e, "function") if e.type == "call" else deps._txt(src, e)
        if (name or "").rsplit(".", 1)[-1].startswith(THROW_TYPES):
            return "throw"
    return "other"


# --- GDScript -----------------------------------------------------------------------------------
# A file is one type; GDScript has no interfaces and no exceptions: an override that only calls
# `push_error(...)` or `assert(false...)` refuses its parent ("throw"), one that is only `pass` is
# "empty" — the convention the spec declares (§3).

GD_METHODS = ("function_definition", "constructor_definition")
GD_PARAMS = ("identifier", "typed_parameter", "default_parameter", "typed_default_parameter")


def _gdscript(src, root, rel, roots=()) -> FileFacts:
    parent = str(PurePosixPath(rel).parent)
    ff = FileFacts(file=rel, lang="gdscript", package="" if parent == "." else parent)
    cn = next((c for c in root.named_children if c.type == "class_name_statement"), None)
    main = (deps._field(src, cn, "name") if cn is not None else None) or str(
        PurePosixPath(rel).with_suffix(""))
    ext = (cn.child_by_field_name("extends") if cn is not None else None) or next(
        (c for c in root.named_children if c.type == "extends_statement"), None)
    abstract = any(_gd_is_abstract(src, c) for c in root.named_children if c.type == "annotation")
    _gd_type(src, ff, root, main, rel, ext, abstract, _line(cn) if cn is not None else 1)
    for c in sorted((n for n in deps._walk(root) if n.type == "class_definition"),
                    key=lambda n: n.start_byte):
        names = [deps._field(src, a, "name") for a in [c, *_ancestors(c)]
                 if a.type == "class_definition"]
        _gd_type(src, ff, c.child_by_field_name("body"), ".".join([main, *reversed(names)]), rel,
                 c.child_by_field_name("extends"), _gd_annotated(src, c), _line(c))
    return ff


def _gd_is_abstract(src, ann) -> bool:
    return any(deps._txt(src, c) == "abstract" for c in ann.named_children if c.type == "identifier")


def _gd_annotated(src, n) -> bool:
    """`@abstract` on a declaration: in its own annotations, or the standalone line before it."""
    own = next((c for c in n.named_children if c.type == "annotations"), None)
    if own is not None and any(_gd_is_abstract(src, a) for a in own.named_children):
        return True
    p = n.prev_named_sibling
    while p is not None and p.type == "annotation":
        if _gd_is_abstract(src, p):
            return True
        p = p.prev_named_sibling
    return False


def _gd_type(src, ff, body, full, rel, ext, abstract, line) -> None:
    members = list(body.named_children) if body is not None else []
    bases = ()
    if ext is not None:
        b = next((c for c in ext.named_children), None)
        if b is not None:
            bases = (deps._txt(src, b).strip("'\""),)
    methods = [m for m in members if m.type in GD_METHODS]
    mfs = [_gd_method(src, m, full) for m in methods]
    ff.types.append(TypeFact(full, "class", abstract or any(m.is_abstract for m in mfs), rel,
                             line, ff.package, bases))
    fields = [FieldFact(full, deps._field(src, v, "name"), _line(v), _gd_type_of(src, v))
              for v in members if v.type == "variable_statement"]
    ff.fields += fields
    ff.trefs += [TypedRefFact(f"type:{full}", f.name, f.declared_type, "field", f.line)
                 for f in fields if f.declared_type]
    field_names = {f.name for f in fields}
    for m, mf in zip(methods, mfs):
        ff.methods.append(mf)
        body_ = m.child_by_field_name("body")
        if body_ is not None:
            shadowed = {_py_param_name(src, x) for x in _gd_params(m)} | _gd_locals(src, body_)
            ff.accesses += _gd_accesses(src, body_, mf.id, full, field_names, shadowed)
            ff.calls += _gd_calls(src, body_, mf.id)
            ff.ttests += _gd_type_tests(src, body_, mf.id)
            ff.bodies[mf.id] = _gd_body_kind(src, body_)
        ff.trefs += _gd_trefs(src, m, body_, mf.id)


def _gd_params(m) -> list:
    p = m.child_by_field_name("parameters")
    return [x for x in (p.named_children if p is not None else []) if x.type in GD_PARAMS]


def _gd_locals(src, body) -> set[str]:
    """The names a method declares: `var x`, a `for x in`, a `var x` pattern of a match."""
    out = set()
    for n in deps._walk(body):
        if n.type == "variable_statement":
            out.add(deps._field(src, n, "name"))
        elif n.type == "for_statement" and n.child_by_field_name("left") is not None:
            out.add(deps._txt(src, n.child_by_field_name("left")))
        elif n.type == "pattern_binding":
            out |= {deps._txt(src, c) for c in n.named_children if c.type == "identifier"}
    return out


def _gd_method(src, m, owner) -> MethodFact:
    ctor = m.type == "constructor_definition"
    name = "_init" if ctor else deps._field(src, m, "name")
    static = any(c.type == "static_keyword" for c in m.children)
    return MethodFact(owner=owner, name=name, arity=len(_gd_params(m)), line=_line(m),
                      end_line=m.end_point[0] + 1, is_ctor=ctor, is_static=static,
                      is_abstract=_gd_annotated(src, m), is_virtual=True,
                      is_builder=static and _gd_is_builder(src, m))


def _gd_is_builder(src, m) -> bool:
    """`var r := T.new()`, then only `r.field = <parameter or literal>`, then `return r`: the way a
    GDScript record is built when its constructor cannot take the arguments — the form of a
    language idiom, not of a rule (spec of feature 15, the forensics review G1)."""
    body = m.child_by_field_name("body")
    stmts = [c for c in (body.named_children if body is not None else []) if c.type != "comment"]
    if len(stmts) < 3 or stmts[0].type != "variable_statement" or stmts[-1].type != "return_statement":
        return False
    var = deps._field(src, stmts[0], "name")
    value = stmts[0].child_by_field_name("value")
    parts = value.named_children if value is not None and value.type == "attribute" else []
    if not (len(parts) == 2 and parts[1].type == "attribute_call" and parts[1].named_children
            and deps._txt(src, parts[1].named_children[0]) == "new"):
        return False
    params = {_py_param_name(src, x) for x in _gd_params(m)}
    for st in stmts[1:-1]:
        a = st.named_children[0] if st.type == "expression_statement" and st.named_children else None
        if a is None or a.type != "assignment":
            return False
        left, right = a.child_by_field_name("left"), a.child_by_field_name("right")
        lp = left.named_children if left is not None and left.type == "attribute" else []
        if not (len(lp) == 2 and deps._txt(src, lp[0]) == var and lp[1].type == "identifier"):
            return False
        if right is None or not (right.type in ("integer", "float", "string", "true", "false", "null")
                                 or (right.type == "identifier" and deps._txt(src, right) in params)):
            return False
    ret = stmts[-1].named_children
    return len(ret) == 1 and deps._txt(src, ret[0]) == var


def _gd_type_of(src, n) -> str:
    """The declared type of a `var` / parameter; `:= T.new()` is T, any other `:=` none."""
    t = n.child_by_field_name("type")
    if t is not None and t.type == "type":
        return deps._txt(src, t)
    v = n.child_by_field_name("value")
    if t is not None and t.type == "inferred_type" and v is not None and v.type == "attribute":
        parts = v.named_children
        if len(parts) == 2 and parts[1].type == "attribute_call" and parts[1].named_children \
                and deps._txt(src, parts[1].named_children[0]) == "new":
            return deps._txt(src, parts[0])
    return ""


def _gd_accesses(src, body, mid, owner, field_names, shadowed) -> list[AccessFact]:
    out = []
    for n in deps._walk(body):
        name = None
        if n.type == "attribute":
            parts = n.named_children
            if len(parts) >= 2 and deps._txt(src, parts[0]) == "self" and \
                    parts[1].type == "identifier":
                name = deps._txt(src, parts[1])
        elif n.type == "identifier" and n.parent is not None:
            p = n.parent
            first = bool(p.named_children) and p.named_children[0] == n
            member = p.type == "attribute" and not first           # `obj.x`: x is obj's
            called = p.type in ("call", "attribute_call") and first  # `x()`: a call, not a field
            if member or called or p.type == "type" or deps._txt(src, n) in shadowed:
                continue
            name = deps._txt(src, n)
        if name in field_names:
            p = n.parent
            write = p is not None and p.type in ("assignment", "augmented_assignment") and \
                p.child_by_field_name("left") == n
            out.append(AccessFact(mid, f"field:{owner}.{name}", "w" if write else "r", _line(n)))
    return out


def _gd_calls(src, body, mid) -> list[CallFact]:
    out = []
    for n in deps._walk(body):
        if n.type == "call" and n.named_children and n.named_children[0].type == "identifier":
            out.append(CallFact(mid, deps._txt(src, n.named_children[0]), "", _line(n)))
        elif n.type == "attribute_call" and n.parent is not None and n.parent.type == "attribute":
            callee = deps._txt(src, n.named_children[0]) if n.named_children else ""
            recv = src[n.parent.start_byte:n.start_byte].decode("utf-8", "replace").rstrip(". \t")
            out.append(CallFact(mid, callee, recv, _line(n)))
    return out


def _gd_trefs(src, m, body, mid) -> list[TypedRefFact]:
    out = []
    for x in _gd_params(m):
        t = _gd_type_of(src, x) if x.type != "identifier" else ""
        if t:
            out.append(TypedRefFact(mid, _py_param_name(src, x), t, "param", _line(x)))
    for n in (deps._walk(body) if body is not None else []):
        if n.type == "variable_statement":
            t = _gd_type_of(src, n)
            if t:
                out.append(TypedRefFact(mid, deps._field(src, n, "name"), t, "local", _line(n)))
    return out


def _gd_condition(src, c) -> tuple[str, str, str] | None:
    if c.type == "binary_operator" and deps._field(src, c, "op") == "is":
        left, right = c.child_by_field_name("left"), c.child_by_field_name("right")
        return (deps._txt(src, left), deps._txt(src, right), "type") if left and right else None
    return None


def _gd_type_tests(src, body, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    for n in deps._walk(body):
        if n.type == "if_statement":
            conds = [n.child_by_field_name("condition")] + [
                e.child_by_field_name("condition") for e in n.named_children
                if e.type == "elif_clause"]
            links = []
            for c in conds:
                got = _gd_condition(src, c) if c is not None else None
                if got:
                    in_chain.add(c.id)
                    links.append((_line(c), *got))
            out += _chain_facts(mid, links)
        elif n.type == "match_statement":
            subj = n.child_by_field_name("value")
            mbody = n.child_by_field_name("body")
            links = []
            for sec in (mbody.named_children if mbody is not None else []):
                if sec.type != "pattern_section":
                    continue
                for p in sec.named_children:
                    if p.type == "attribute" and subj is not None:
                        got = _py_kind_member(src, p)
                        if got:
                            links.append((_line(p), deps._txt(src, subj), *got))
            out += _chain_facts(mid, links)
        elif n.type == "binary_operator" and n.id not in in_chain:
            got = _gd_condition(src, n)
            if got:
                out.append(TypeTestFact(mid, got[0], (got[1],), 1, f"{mid}@{_line(n)}",
                                        _line(n), got[2]))
    return out


def _gd_body_kind(src, body) -> str:
    stmts = [s for s in body.named_children if s.type != "comment"]
    if all(s.type == "pass_statement" for s in stmts):
        return "empty"
    if len(stmts) == 1 and stmts[0].type == "expression_statement" and stmts[0].named_children:
        call = stmts[0].named_children[0]
        if call.type == "call" and call.named_children:
            name = deps._txt(src, call.named_children[0])
            args = call.child_by_field_name("arguments")
            first = args.named_children[0] if args is not None and args.named_children else None
            if name == "push_error" or (name == "assert" and first is not None
                                        and deps._txt(src, first) == "false"):
                return "throw"
    return "other"


# --- TypeScript ---------------------------------------------------------------------------------

TS_TYPES = {"class_declaration": "class", "abstract_class_declaration": "class",
            "interface_declaration": "interface", "enum_declaration": "enum"}
TS_METHODS = ("method_definition", "method_signature", "abstract_method_signature")
TS_PARAMS = ("required_parameter", "optional_parameter")
TS_WRITES = ("assignment_expression", "augmented_assignment_expression")


def _ts_module(rel: str, roots) -> str:
    ext = next((e for e in (".tsx", ".mts", ".cts", ".ts") if rel.endswith(e)), "")
    return _module_of(rel, roots, ext or ".ts", "index")


def _typescript(src, root, rel, roots=()) -> FileFacts:
    ff = FileFacts(file=rel, lang="typescript", package=_ts_module(rel, roots))
    ff.imports = [deps._field(src, n, "source").strip("\"'`") for n in deps._walk(root)
                  if n.type == "import_statement" and n.child_by_field_name("source") is not None]
    for t in sorted((n for n in deps._walk(root) if n.type in TS_TYPES), key=lambda n: n.start_byte):
        name = deps._field(src, t, "name")
        kind = TS_TYPES[t.type]
        ff.types.append(TypeFact(name, kind, t.type == "abstract_class_declaration" or kind == "interface",
                                 rel, _line(t), ff.package, tuple(_ts_bases(src, t))))
        members = _ts_members(t)
        fields = _ts_fields(src, members, name)
        ff.fields += fields
        ff.trefs += [TypedRefFact(f"type:{name}", f.name, f.declared_type, "field", f.line)
                     for f in fields if f.declared_type]
        field_names = {f.name for f in fields}
        for m in (x for x in members if x.type in TS_METHODS):
            mf = _ts_method(src, m, name, kind)
            ff.methods.append(mf)
            body = m.child_by_field_name("body")
            ff.trefs += _ts_trefs(src, m, mf.id)
            if body is None:
                continue
            ff.accesses += _ts_accesses(src, body, mf.id, name, field_names)
            ff.calls += _ts_calls(src, body, mf.id)
            ff.ttests += _ts_type_tests(src, body, mf.id)
            ff.catches += _catches(src, body, mf.id, "catch_clause", _cs_catch_statements)
            ff.bodies[mf.id] = _lone_throw_kind(body)
            if mf.is_override:
                ff.obodies.append(OverrideBodyFact(mf.id, _lone_throw_kind(body)))
    return ff


def _ts_bases(src, t) -> list[str]:
    out = []
    for h in t.named_children:
        clauses = h.named_children if h.type == "class_heritage" else (
            [h] if h.type == "extends_type_clause" else [])  # an interface extends with its own clause
        for c in clauses:
            for b in c.named_children:
                if b.type in ("identifier", "type_identifier", "nested_type_identifier",
                              "generic_type", "member_expression"):
                    out.append(_strip_generics(deps._txt(src, b)))
    return out


def _ts_members(t) -> list:
    body = t.child_by_field_name("body")
    return list(body.named_children) if body is not None else []


def _ts_type(src, n) -> str:
    """The type an annotation names, without its colon."""
    a = n.child_by_field_name("type")
    return deps._txt(src, a).lstrip(":").strip() if a is not None else ""


def _ts_fields(src, members, owner) -> list[FieldFact]:
    out = [FieldFact(owner, deps._field(src, m, "name"), _line(m), _ts_type(src, m))
           for m in members if m.type == "public_field_definition"]
    for m in members:  # constructor(private readonly repo: Repo): a parameter that is a field
        if m.type == "method_definition" and deps._field(src, m, "name") == "constructor":
            ps = m.child_by_field_name("parameters")
            for x in (ps.named_children if ps is not None else []):
                if x.type in TS_PARAMS and any(c.type in ("accessibility_modifier", "readonly")
                                               for c in x.children):
                    out.append(FieldFact(owner, deps._field(src, x, "pattern"), _line(x),
                                         _ts_type(src, x)))
    return out


def _ts_method(src, m, owner, kind) -> MethodFact:
    name = deps._field(src, m, "name")
    ps = m.child_by_field_name("parameters")
    arity = len([x for x in (ps.named_children if ps is not None else []) if x.type != "comment"])
    words = {c.type for c in m.children}
    return MethodFact(owner=owner, name=name, arity=arity, line=_line(m), end_line=m.end_point[0] + 1,
                      is_ctor=name == "constructor", is_static="static" in words,
                      is_abstract=m.type == "abstract_method_signature" or (
                          kind == "interface" and m.type == "method_signature"),
                      is_override="override_modifier" in words)


def _ts_trefs(src, m, mid) -> list[TypedRefFact]:
    out = []
    ps = m.child_by_field_name("parameters")
    for x in (ps.named_children if ps is not None else []):
        typ = _ts_type(src, x) if x.type in TS_PARAMS else ""
        if typ:
            out.append(TypedRefFact(mid, deps._field(src, x, "pattern"), typ, "param", _line(x)))
    body = m.child_by_field_name("body")
    for v in (n for n in deps._walk(body) if n.type == "variable_declarator") if body else ():
        typ = _ts_type(src, v)
        init = v.child_by_field_name("value")
        if not typ and init is not None and init.type == "new_expression":
            typ = deps._field(src, init, "constructor")
        if typ:
            out.append(TypedRefFact(mid, deps._field(src, v, "name"), typ, "local", _line(v)))
    return out


def _ts_is_write(n) -> bool:
    p = n.parent
    if p is None:
        return False
    if p.type in TS_WRITES:
        return p.child_by_field_name("left") == n
    return p.type == "update_expression"


def _ts_accesses(src, body, mid, owner, field_names) -> list[AccessFact]:
    out = []
    for n in deps._walk(body):
        if n.type != "member_expression":
            continue
        o, name = n.child_by_field_name("object"), deps._field(src, n, "property")
        if o is not None and o.type == "this" and name in field_names:
            out.append(AccessFact(mid, f"field:{owner}.{name}", "w" if _ts_is_write(n) else "r",
                                  _line(n)))
    return out


def _ts_calls(src, body, mid) -> list[CallFact]:
    """The calls of a method; a construction `new T(...)` is a call with the receiver "new"."""
    out = []
    for n in deps._walk(body):
        if n.type == "new_expression":
            c = deps._field(src, n, "constructor")
            if c:
                out.append(CallFact(mid, _strip_generics(c).rsplit(".", 1)[-1], "new", _line(n)))
        elif n.type == "call_expression":
            f = n.child_by_field_name("function")
            if f is None:
                continue
            if f.type == "member_expression":
                o = f.child_by_field_name("object")
                recv = deps._txt(src, o) if o is not None else ""
                out.append(CallFact(mid, deps._field(src, f, "property"),
                                    "self" if recv == "this" else recv, _line(n)))
            elif f.type == "identifier":
                out.append(CallFact(mid, deps._txt(src, f), "", _line(n)))
    return out


def _ts_unwrap(n):
    while n is not None and n.type == "parenthesized_expression" and n.named_children:
        n = n.named_children[0]
    return n


def _ts_condition(src, c) -> tuple[str, str, str] | None:
    """(subject, tested, kind) of an if condition: `x instanceof T`, or `x.kind === Kind.A`."""
    c = _ts_unwrap(c)
    if c is None or c.type != "binary_expression":
        return None
    left, right = c.child_by_field_name("left"), c.child_by_field_name("right")
    op = deps._txt(src, c.child_by_field_name("operator")) if c.child_by_field_name("operator") else ""
    if left is None or right is None:
        return None
    if op == "instanceof":
        return deps._txt(src, left), deps._txt(src, right), "type"
    if op in ("==", "===") and right.type == "member_expression":
        o = right.child_by_field_name("object")
        if o is not None and deps._txt(src, o).rsplit(".", 1)[-1].endswith(KIND_WORDS):
            return deps._txt(src, left), deps._txt(src, right), "enum"
    return None


def _ts_type_tests(src, body, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    nodes = list(deps._walk(body))  # the chains first: a test in a chain is not a lone one
    nodes.sort(key=lambda n: n.type != "if_statement")
    for n in nodes:
        if n.type == "if_statement" and not (n.parent is not None and n.parent.type == "else_clause"):
            links, link = [], n
            while link is not None and link.type == "if_statement":
                c = link.child_by_field_name("condition")
                got = _ts_condition(src, c) if c is not None else None
                if got:
                    in_chain.add(_ts_unwrap(c).id)
                    links.append((_line(c), *got))
                alt = link.child_by_field_name("alternative")
                link = next((x for x in alt.named_children if x.type == "if_statement"),
                            None) if alt is not None else None
            out += _chain_facts(mid, links)
        elif n.type == "switch_statement":
            subj = _ts_unwrap(n.child_by_field_name("value"))
            cases = sorted((x for x in deps._walk(n) if x.type == "switch_case"
                            and _owner_switch(x) == n), key=lambda x: x.start_byte)
            values = [v for v in (x.child_by_field_name("value") for x in cases) if v is not None]
            owners = {deps._txt(src, v.child_by_field_name("object")) for v in values
                      if v.type == "member_expression" and v.child_by_field_name("object")}
            if subj is not None and values and len(owners) == 1 and all(
                    v.type == "member_expression" for v in values):  # the members of one enum
                out += _chain_facts(mid, [(_line(v), deps._txt(src, subj), deps._txt(src, v), "enum")
                                          for v in values])
        elif n.type == "binary_expression" and n.id not in in_chain:
            got = _ts_condition(src, n)
            if got and got[2] == "type":
                out.append(TypeTestFact(mid, got[0], (got[1],), 1, f"{mid}@{_line(n)}", _line(n),
                                        "type"))
    return out




# --- C++ ----------------------------------------------------------------------------------------

CPP_TYPES = {"class_specifier": "class", "struct_specifier": "struct", "enum_specifier": "enum"}
CPP_NAMES = ("field_identifier", "identifier", "destructor_name", "operator_name")


def _cpp(src, root, rel, roots=()) -> FileFacts:
    """A type's name carries its namespaces and enclosing types, joined by dots; a method defined
    outside its class (`void Sq::run() {}`) joins the declaration of the same id."""
    ff = FileFacts(file=rel, lang="cpp")
    ff.imports = [deps._field(src, n, "path").strip("<>\"") for n in deps._walk(root)
                  if n.type == "preproc_include" and n.child_by_field_name("path") is not None]
    methods: dict[str, tuple[MethodFact, object]] = {}  # id → (fact, the definition or None)
    fields_of: dict[str, set[str]] = {}
    for t in sorted((n for n in deps._walk(root) if n.type in CPP_TYPES
                     and n.child_by_field_name("body") is not None), key=lambda n: n.start_byte):
        ns = _cpp_namespace(src, t)
        full = ".".join(filter(None, [ns, *_cpp_enclosing(src, t), deps._field(src, t, "name")]))
        if not deps._field(src, t, "name"):
            continue
        kind = CPP_TYPES[t.type]
        own = []
        if kind != "enum":
            for m in _cpp_members(t):
                if m.type == "field_declaration" and _cpp_declarator(m, "function_declarator") is None:
                    for name, line in _cpp_field_names(src, m):
                        ff.fields.append(FieldFact(full, name, line, deps._field(src, m, "type")))
                    continue
                mf = _cpp_method(src, m, full, deps._field(src, t, "name"))
                if mf is not None:
                    own.append(mf)
                    methods[mf.id] = (mf, m if m.type == "function_definition" else None)
        fields_of[full] = {f.name for f in ff.fields if f.owner == full}
        ff.types.append(TypeFact(full, kind, any(m.is_abstract for m in own), rel, _line(t), ns,
                                 tuple(_cpp_bases(src, t))))
    for d in (n for n in deps._walk(root) if n.type == "function_definition"):
        q = _cpp_declarator(d, "qualified_identifier")
        if q is None or _cpp_in_class(d):
            continue
        owner = ".".join(filter(None, [_cpp_namespace(src, d),
                                       *deps._field(src, q, "scope").split("::")]))
        mf = _cpp_method(src, d, owner, owner.rsplit(".", 1)[-1])
        if mf is None:
            continue
        declared = methods.get(mf.id)
        if declared is not None:  # the flags are the declaration's, the code the definition's
            mf = replace(declared[0], line=mf.line, end_line=mf.end_line)
        methods[mf.id] = (mf, d)
    for mid in sorted(methods):
        mf, d = methods[mid]
        ff.methods.append(mf)
        body = d.child_by_field_name("body") if d is not None else None
        ff.trefs += _cpp_trefs(src, d, mid) if d is not None else []
        if body is None:
            continue
        ff.accesses += _cpp_accesses(src, d, body, mid, mf.owner, fields_of.get(mf.owner, set()))
        ff.calls += _cpp_calls(src, body, mid)
        ff.ttests += _cpp_type_tests(src, body, mid)
        ff.catches += _catches(src, body, mid, "catch_clause", _cs_catch_statements)
        ff.bodies[mid] = _lone_throw_kind(body)
        if mf.is_override:
            ff.obodies.append(OverrideBodyFact(mid, _lone_throw_kind(body)))
    return ff


def _cpp_namespace(src, n) -> str:
    return ".".join(reversed([deps._field(src, a, "name") for a in _ancestors(n)
                              if a.type == "namespace_definition" and deps._field(src, a, "name")]))


def _cpp_enclosing(src, n) -> list[str]:
    return list(reversed([deps._field(src, a, "name") for a in _ancestors(n)
                          if a.type in CPP_TYPES and deps._field(src, a, "name")]))


def _cpp_in_class(n) -> bool:
    return any(a.type == "field_declaration_list" for a in _ancestors(n))


def _cpp_members(t) -> list:
    body = t.child_by_field_name("body")
    out = []
    for c in (body.named_children if body is not None else []):
        if c.type == "template_declaration":
            out += [x for x in c.named_children if x.type in ("function_definition",
                                                              "field_declaration", "declaration")]
        elif c.type in ("function_definition", "field_declaration", "declaration"):
            out.append(c)
    return out


def _cpp_declarator(n, kind):
    """The first `kind` node down the declarator chain of a declaration."""
    d = n.child_by_field_name("declarator")
    while d is not None:
        if d.type == kind:
            return d
        d = d.child_by_field_name("declarator")
    return None


def _cpp_field_names(src, m) -> list[tuple[str, int]]:
    out = []
    for d in (c for c in m.children if m.field_name_for_child(_index(m, c)) == "declarator"):
        while d is not None and d.type != "field_identifier":
            d = d.child_by_field_name("declarator")
        if d is not None:
            out.append((deps._txt(src, d), _line(d)))
    return out


def _cpp_method(src, m, owner, simple) -> MethodFact | None:
    fd = _cpp_declarator(m, "function_declarator")
    if fd is None:
        return None
    n = fd.child_by_field_name("declarator")
    if n is not None and n.type == "qualified_identifier":
        n = n.child_by_field_name("name")
    if n is None or n.type not in CPP_NAMES:
        return None
    name = deps._txt(src, n)
    ps = fd.child_by_field_name("parameters")
    arity = len([x for x in (ps.named_children if ps is not None else [])
                 if x.type in ("parameter_declaration", "optional_parameter_declaration",
                               "variadic_parameter_declaration")])
    specs = {deps._txt(src, c) for c in fd.named_children if c.type == "virtual_specifier"}
    words = {c.type for c in m.children}
    storage = {deps._txt(src, c) for c in m.named_children if c.type == "storage_class_specifier"}
    pure = m.type == "field_declaration" and "=" in words  # `virtual f() = 0;`
    return MethodFact(owner=owner, name=name, arity=arity, line=_line(m), end_line=m.end_point[0] + 1,
                      is_ctor=name == simple, is_dtor=n.type == "destructor_name",
                      is_static="static" in storage, is_abstract=pure,
                      is_virtual="virtual" in words, is_override="override" in specs)


def _cpp_bases(src, t) -> list[str]:
    return [_strip_generics(deps._txt(src, b)) for c in t.named_children
            if c.type == "base_class_clause" for b in c.named_children
            if b.type in ("type_identifier", "qualified_identifier", "template_type")]


def _cpp_declared(src, d) -> set[str]:
    """The names a function declares: its parameters and its locals."""
    return {deps._txt(src, n) for n in deps._walk(d) if n.type == "identifier"
            and n.parent is not None
            and n.parent.field_name_for_child(_index(n.parent, n)) == "declarator"
            and n.parent.type != "function_declarator"}


def _cpp_trefs(src, d, mid) -> list[TypedRefFact]:
    out = []
    fd = _cpp_declarator(d, "function_declarator")
    ps = fd.child_by_field_name("parameters") if fd is not None else None
    for x in (ps.named_children if ps is not None else []):
        typ, name = deps._field(src, x, "type"), ""
        n = x.child_by_field_name("declarator")
        while n is not None and n.type != "identifier":
            n = n.child_by_field_name("declarator")
        name = deps._txt(src, n) if n is not None else ""
        if typ and name:
            out.append(TypedRefFact(mid, name, typ, "param", _line(x)))
    return out


def _cpp_is_write(n) -> bool:
    p = n.parent
    if p is None:
        return False
    if p.type == "assignment_expression":
        return p.child_by_field_name("left") == n
    return p.type == "update_expression"


def _cpp_accesses(src, d, body, mid, owner, field_names) -> list[AccessFact]:
    out, shadowed = [], _cpp_declared(src, d)
    for n in deps._walk(body):
        name = ""
        if n.type == "field_expression":
            a = n.child_by_field_name("argument")
            if a is not None and a.type == "this":
                name = deps._field(src, n, "field")
        elif n.type == "identifier" and deps._txt(src, n) not in shadowed:
            p = n.parent
            role = p.field_name_for_child(_index(p, n)) if p is not None else None
            if p is not None and p.type not in ("qualified_identifier", "template_function") and \
                    role not in ("function", "declarator"):
                name = deps._txt(src, n)
        if name in field_names:
            out.append(AccessFact(mid, f"field:{owner}.{name}", "w" if _cpp_is_write(n) else "r",
                                  _line(n)))
    return out


def _cpp_calls(src, body, mid) -> list[CallFact]:
    """The calls of a method; a construction `new T(...)` is a call with the receiver "new"."""
    out = []
    for n in deps._walk(body):
        if n.type == "new_expression":
            typ = deps._field(src, n, "type")
            if typ:
                out.append(CallFact(mid, _strip_generics(typ).rsplit("::", 1)[-1], "new", _line(n)))
            continue
        f = n.child_by_field_name("function") if n.type == "call_expression" else None
        if f is None:
            continue
        if f.type == "field_expression":
            a = f.child_by_field_name("argument")
            recv = deps._txt(src, a) if a is not None else ""
            out.append(CallFact(mid, deps._field(src, f, "field"),
                                "self" if recv == "this" else recv, _line(n)))
        elif f.type == "qualified_identifier":
            out.append(CallFact(mid, deps._field(src, f, "name"), deps._field(src, f, "scope"),
                                _line(n)))
        elif f.type in ("identifier", "template_function"):
            out.append(CallFact(mid, _strip_generics(deps._txt(src, f)), "", _line(n)))
    return out


def _cpp_cast(src, n) -> tuple[str, str, str] | None:
    """(subject, tested, "type") of a `dynamic_cast<T*>(x)` call."""
    f = n.child_by_field_name("function") if n.type == "call_expression" else None
    if f is None or f.type != "template_function" or deps._field(src, f, "name") != "dynamic_cast":
        return None
    td = next((x for x in deps._walk(f) if x.type == "type_descriptor"), None)
    args = n.child_by_field_name("arguments")
    if td is None or args is None or not args.named_children:
        return None
    return deps._txt(src, args.named_children[0]), deps._field(src, td, "type"), "type"


def _cpp_condition(src, c) -> tuple[str, str, str] | None:
    """(subject, tested, kind) of an if condition: a dynamic_cast, or `x == Kind::A`."""
    for n in sorted(deps._walk(c), key=lambda n: n.start_byte):
        got = _cpp_cast(src, n)
        if got:
            return got
        if n.type == "binary_expression" and any(x.type == "==" for x in n.children):
            left, right = n.child_by_field_name("left"), n.child_by_field_name("right")
            if left is not None and right is not None and right.type == "qualified_identifier" \
                    and deps._field(src, right, "scope").rsplit("::", 1)[-1].endswith(KIND_WORDS):
                return deps._txt(src, left), deps._txt(src, right), "enum"
    return None


def _cpp_type_tests(src, body, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    nodes = sorted(deps._walk(body), key=lambda n: (n.type != "if_statement", n.start_byte))
    for n in nodes:
        if n.type == "if_statement" and not (n.parent is not None and n.parent.type == "else_clause"):
            links, link = [], n
            while link is not None and link.type == "if_statement":
                c = link.child_by_field_name("condition")
                got = _cpp_condition(src, c) if c is not None else None
                if got:
                    in_chain.update(x.id for x in deps._walk(c))
                    links.append((_line(c), *got))
                alt = link.child_by_field_name("alternative")
                link = next((x for x in alt.named_children if x.type == "if_statement"),
                            None) if alt is not None else None
            out += _chain_facts(mid, links)
        elif n.type == "switch_statement":
            c = n.child_by_field_name("condition")
            subj = c.child_by_field_name("value") if c is not None else None
            values = [v for v in (x.child_by_field_name("value") for x in sorted(
                (x for x in deps._walk(n) if x.type == "case_statement" and _owner_switch(x) == n),
                key=lambda x: x.start_byte)) if v is not None]
            scopes = {deps._field(src, v, "scope") for v in values if v.type == "qualified_identifier"}
            if subj is not None and values and len(scopes) == 1 and all(
                    v.type == "qualified_identifier" for v in values):  # the members of one enum
                out += _chain_facts(mid, [(_line(v), deps._txt(src, subj), deps._txt(src, v), "enum")
                                          for v in values])
        elif n.id not in in_chain:
            got = _cpp_cast(src, n)
            if got:
                out.append(TypeTestFact(mid, got[0], (got[1],), 1, f"{mid}@{_line(n)}", _line(n),
                                        "type"))
    return out


def _lone_throw_kind(body) -> str:
    """empty, throw (the body only throws: the language has no NotImplemented type to look for),
    or other."""
    stmts = [c for c in body.named_children if c.type != "comment"]
    if not stmts:
        return "empty"
    return "throw" if len(stmts) == 1 and stmts[0].type == "throw_statement" else "other"


# --- C ------------------------------------------------------------------------------------------

def _c(src, root, rel, roots=()) -> FileFacts:
    """C has no classes: a struct is a type, a struct whose every field is a function pointer is a
    contract (an interface), and the functions are methods of the file's module, `rel`."""
    ff = FileFacts(file=rel, lang="c")
    ff.imports = [deps._field(src, n, "path").strip("<>\"") for n in deps._walk(root)
                  if n.type == "preproc_include" and n.child_by_field_name("path") is not None]
    alias: dict[str, str] = {}  # a struct tag or a typedef name → the type's name
    for s in sorted((n for n in deps._walk(root) if n.type == "struct_specifier"
                     and n.child_by_field_name("body") is not None), key=lambda n: n.start_byte):
        tag = deps._field(src, s, "name")
        td = s.parent if s.parent is not None and s.parent.type == "type_definition" else None
        name = deps._field(src, td, "declarator") if td is not None else tag
        if not name:
            continue
        alias[name] = name
        if tag:
            alias[tag] = name
        fields = [(fname, line, deps._field(src, fd, "type"), fn)
                  for fd in s.child_by_field_name("body").named_children
                  if fd.type == "field_declaration"
                  for fname, line, fn in _c_field_names(src, fd)]
        interface = bool(fields) and all(fn for *_, fn in fields)
        ff.types.append(TypeFact(name, "interface" if interface else "struct", False, rel,
                                 _line(td if td is not None else s)))
        ff.fields += [FieldFact(name, fname, line, typ) for fname, line, typ, _ in fields]
    fields_of = {}
    for f in ff.fields:
        fields_of.setdefault(f.owner, set()).add(f.name)
    members = {deps._field(src, e, "name"): deps._field(src, en, "name")
               for en in deps._walk(root) if en.type == "enum_specifier"
               for e in deps._walk(en) if e.type == "enumerator"}
    for fn in sorted((n for n in deps._walk(root) if n.type == "function_definition"),
                     key=lambda n: n.start_byte):
        fd = _cpp_declarator(fn, "function_declarator")
        name = deps._field(src, fd, "declarator") if fd is not None else ""
        if not name:
            continue
        ps = fd.child_by_field_name("parameters")
        params = [x for x in (ps.named_children if ps is not None else [])
                  if x.type == "parameter_declaration" and x.child_by_field_name("declarator")]
        storage = {deps._txt(src, c) for c in fn.named_children if c.type == "storage_class_specifier"}
        mf = MethodFact(owner=rel, name=name, arity=len(params), line=_line(fn),
                        end_line=fn.end_point[0] + 1, is_static="static" in storage)
        ff.methods.append(mf)
        body = fn.child_by_field_name("body")
        if body is None:
            continue
        refs = _c_typed_names(src, fn, alias)
        ff.trefs += [TypedRefFact(mf.id, var, typ, role, line) for var, typ, role, line in refs]
        typed = {var: typ for var, typ, _, _ in refs}
        ff.accesses += _c_field_accesses(src, body, mf.id, typed, fields_of)
        ff.calls += _c_calls(src, body, mf.id)
        ff.ttests += _c_enum_switches(src, body, mf.id, members)
        ff.bodies[mf.id] = _lone_throw_kind(body)
    return ff


def _c_field_names(src, fd) -> list[tuple[str, int, bool]]:
    """(name, line, is a function pointer) of each name a field declaration declares."""
    out = []
    for d in (c for c in fd.children if fd.field_name_for_child(_index(fd, c)) == "declarator"):
        fn_ptr = False
        n = d
        while n is not None and n.type != "field_identifier":
            fn_ptr = fn_ptr or n.type == "function_declarator"
            n = n.child_by_field_name("declarator") or next(
                (c for c in n.named_children if c.type in ("pointer_declarator", "field_identifier")),
                None)
        if n is not None:
            out.append((deps._txt(src, n), _line(n), fn_ptr))
    return out


def _c_typed_names(src, fn, alias) -> list[tuple[str, str, str, int]]:
    """(name, type, "param" | "local", line) of the parameters and locals whose declared type is a
    struct of this file."""
    out = []
    for d in deps._walk(fn):
        if d.type not in ("parameter_declaration", "declaration"):
            continue
        t = d.child_by_field_name("type")
        if t is None:
            continue
        tname = deps._field(src, t, "name") if t.type == "struct_specifier" else deps._txt(src, t)
        if tname not in alias:
            continue
        for decl in (c for c in d.children if d.field_name_for_child(_index(d, c)) == "declarator"):
            n = decl
            while n is not None and n.type != "identifier":
                n = n.child_by_field_name("declarator")
            if n is not None:
                out.append((deps._txt(src, n), alias[tname],
                            "param" if d.type == "parameter_declaration" else "local", _line(n)))
    return out


def _c_field_accesses(src, body, mid, typed, fields_of) -> list[AccessFact]:
    out = []
    for n in deps._walk(body):
        if n.type != "field_expression":
            continue
        a, field = n.child_by_field_name("argument"), deps._field(src, n, "field")
        owner = typed.get(deps._txt(src, a)) if a is not None else None
        if owner and field in fields_of.get(owner, ()):
            out.append(AccessFact(mid, f"field:{owner}.{field}", "w" if _cpp_is_write(n) else "r",
                                  _line(n)))
    return out


def _c_calls(src, body, mid) -> list[CallFact]:
    out = []
    for n in deps._walk(body):
        f = n.child_by_field_name("function") if n.type == "call_expression" else None
        if f is None:
            continue
        if f.type == "field_expression":  # s->area(s): a call through the contract
            a = f.child_by_field_name("argument")
            out.append(CallFact(mid, deps._field(src, f, "field"),
                                deps._txt(src, a) if a is not None else "", _line(n)))
        elif f.type == "identifier":
            out.append(CallFact(mid, deps._txt(src, f), "", _line(n)))
    return out


def _c_enum_switches(src, body, mid, members) -> list[TypeTestFact]:
    """A switch whose cases are the members of one enum of this file."""
    out = []
    for n in sorted((x for x in deps._walk(body) if x.type == "switch_statement"),
                    key=lambda x: x.start_byte):
        subj = _ts_unwrap(n.child_by_field_name("condition"))
        values = [v for v in (x.child_by_field_name("value") for x in sorted(
            (x for x in deps._walk(n) if x.type == "case_statement" and _owner_switch(x) == n),
            key=lambda x: x.start_byte)) if v is not None]
        names = [deps._txt(src, v) for v in values]
        enums = {members.get(x) for x in names}
        if subj is not None and names and all(v.type == "identifier" for v in values) \
                and len(enums) == 1 and None not in enums:
            out += _chain_facts(mid, [(_line(v), deps._txt(src, subj), x, "enum")
                                      for v, x in zip(values, names)])
    return out


# --- Swift --------------------------------------------------------------------------------------

SWIFT_KINDS = {"class": "class", "struct": "struct", "enum": "enum", "actor": "class"}
SWIFT_METHODS = ("function_declaration", "protocol_function_declaration", "init_declaration",
                 "deinit_declaration")
SWIFT_FATAL = frozenset({"fatalError", "preconditionFailure"})


def _swift(src, root, rel, roots=()) -> FileFacts:
    """An extension adds its members to the type it extends: it is not a second type."""
    ff = FileFacts(file=rel, lang="swift")
    ff.imports = [deps._txt(src, n.named_children[0]) for n in deps._walk(root)
                  if n.type == "import_declaration" and n.named_children]
    decls = sorted((n for n in deps._walk(root) if n.type in ("class_declaration",
                                                              "protocol_declaration")),
                   key=lambda n: n.start_byte)
    owners = []  # (type name, kind, declaration)
    for t in decls:
        word = deps._field(src, t, "declaration_kind")
        name = _strip_generics(deps._field(src, t, "name"))
        kind = "protocol" if t.type == "protocol_declaration" else SWIFT_KINDS.get(word, "")
        if word != "extension" and kind:
            ff.types.append(TypeFact(name, kind, kind == "protocol", rel, _line(t), "",
                                     tuple(_swift_bases(src, t))))
        if kind or word == "extension":
            owners.append((name, kind or "extension", t))
    for name, _, t in owners:  # the fields of a type, its extensions included, before any access
        ff.fields += [f for m in _swift_members(t) if m.type == "property_declaration"
                      for f in _swift_fields(src, m, name)]
    for name, kind, t in owners:
        field_names = {f.name for f in ff.fields if f.owner == name}
        for m in (x for x in _swift_members(t) if x.type in SWIFT_METHODS):
            mf = _swift_method(src, m, name, kind)
            ff.methods.append(mf)
            ff.trefs += _swift_trefs(src, m, mf.id)
            body = m.child_by_field_name("body")
            if body is None:
                continue
            ff.accesses += _swift_accesses(src, body, mf.id, name, field_names,
                                           _swift_declared(src, m))
            ff.calls += _swift_calls(src, body, mf.id)
            ff.ttests += _swift_type_tests(src, body, mf.id)
            ff.catches += _catches(src, body, mf.id, "catch_block", _swift_catch_statements)
            ff.bodies[mf.id] = _swift_body_kind(src, body)
            if mf.is_override:
                ff.obodies.append(OverrideBodyFact(mf.id, _swift_body_kind(src, body)))
    return ff


def _swift_members(t) -> list:
    """The members of a type's body; the parser's recovery may wrap some in an ERROR node."""
    body = t.child_by_field_name("body")
    out = []
    for c in (body.named_children if body is not None else []):
        out += c.named_children if c.type == "ERROR" else [c]
    return out


def _swift_bases(src, t) -> list[str]:
    return [_strip_generics(deps._txt(src, c.named_children[0])) for c in t.named_children
            if c.type == "inheritance_specifier" and c.named_children]


def _swift_type(src, n) -> str:
    a = next((c for c in n.named_children if c.type == "type_annotation"), None)
    return deps._txt(src, a).lstrip(":").strip() if a is not None else ""


def _swift_fields(src, m, owner) -> list[FieldFact]:
    return [FieldFact(owner, deps._txt(src, b), _line(b), _swift_type(src, m))
            for p in m.named_children if p.type == "pattern"
            for b in p.named_children if b.type == "simple_identifier"]


def _swift_method(src, m, owner, kind) -> MethodFact:
    name = {"init_declaration": "init", "deinit_declaration": "deinit"}.get(
        m.type, deps._field(src, m, "name"))
    mods = {deps._txt(src, x) for c in m.named_children if c.type == "modifiers"
            for x in c.named_children}
    return MethodFact(owner=owner, name=name, arity=len([c for c in m.named_children
                                                          if c.type == "parameter"]),
                      line=_line(m), end_line=m.end_point[0] + 1,
                      is_ctor=m.type == "init_declaration", is_dtor=m.type == "deinit_declaration",
                      is_static=bool(mods & {"static", "class"}),
                      is_abstract=m.type == "protocol_function_declaration" or kind == "protocol",
                      is_override="override" in mods)


def _swift_trefs(src, m, mid) -> list[TypedRefFact]:
    out = []
    for p in (c for c in m.named_children if c.type == "parameter"):
        typ = next((deps._txt(src, c) for c in p.named_children if c.type == "user_type"), "")
        if typ:
            out.append(TypedRefFact(mid, deps._field(src, p, "name"), typ, "param", _line(p)))
    return out


def _swift_declared(src, m) -> set[str]:
    """The parameters and the locals of a method."""
    out = {deps._field(src, p, "name") for p in m.named_children if p.type == "parameter"}
    body = m.child_by_field_name("body")
    out |= {deps._txt(src, b) for n in (deps._walk(body) if body is not None else ())
            if n.type == "property_declaration" for p in n.named_children if p.type == "pattern"
            for b in p.named_children if b.type == "simple_identifier"}
    return out


def _swift_is_write(n) -> bool:
    for a in _ancestors(n):
        if a.type == "directly_assignable_expression":
            return True
        if a.type not in ("navigation_expression", "navigation_suffix"):
            return False
    return False


def _swift_accesses(src, body, mid, owner, field_names, shadowed) -> list[AccessFact]:
    out = []
    for n in deps._walk(body):
        if n.type != "simple_identifier" or deps._txt(src, n) not in field_names:
            continue
        p = n.parent
        if p.type == "navigation_suffix":  # x.side is this type's field only when x is self
            nav = p.parent
            target = nav.child_by_field_name("target") if nav is not None else None
            if target is None or target.type != "self_expression":
                continue
        elif deps._txt(src, n) in shadowed or p.type in (
                "pattern", "parameter", "prefix_expression", "switch_pattern") or (
                p.type == "call_expression" and p.named_children[0] == n):
            continue
        out.append(AccessFact(mid, f"field:{owner}.{deps._txt(src, n)}",
                              "w" if _swift_is_write(n) else "r", _line(n)))
    return out


def _swift_calls(src, body, mid) -> list[CallFact]:
    out = []
    for n in deps._walk(body):
        if n.type != "call_expression" or not n.named_children:
            continue
        f = n.named_children[0]
        if f.type == "navigation_expression":
            target = f.child_by_field_name("target")
            suffix = f.child_by_field_name("suffix")
            recv = deps._txt(src, target) if target is not None else ""
            callee = deps._txt(src, suffix).lstrip(".") if suffix is not None else ""
            out.append(CallFact(mid, callee, "self" if recv == "self" else recv, _line(n)))
        elif f.type == "simple_identifier":
            out.append(CallFact(mid, deps._txt(src, f), "", _line(n)))
    return out


def _swift_pattern(src, sp) -> tuple[str, str] | None:
    """(tested, kind) of a switch pattern: `.a` an enum member, `is T` or `let x as T` a type."""
    text = deps._txt(src, sp)
    if text.startswith("."):
        return text.split("(")[0], "enum"
    typ = next((deps._txt(src, x) for x in deps._walk(sp) if x.type == "user_type"), "")
    if typ and (text.startswith("is ") or " as " in text):
        return typ, "type"
    return None


def _swift_type_tests(src, body, mid) -> list[TypeTestFact]:
    out, in_chain = [], set()
    nodes = sorted(deps._walk(body), key=lambda n: (n.type != "if_statement", n.start_byte))
    for n in nodes:
        if n.type == "if_statement" and not (n.parent is not None and n.parent.type == "if_statement"):
            links, link = [], n
            while link is not None:
                c = link.child_by_field_name("condition")
                if c is not None and c.type == "check_expression":
                    in_chain.add(c.id)
                    links.append((_line(c), deps._field(src, c, "target"),
                                  deps._field(src, c, "name"), "type"))
                link = next((x for x in link.named_children if x.type == "if_statement"), None)
            out += _chain_facts(mid, links)
        elif n.type == "switch_statement":
            subj = n.child_by_field_name("expr")
            pats = sorted((sp for e in n.named_children if e.type == "switch_entry"
                           for sp in e.named_children if sp.type == "switch_pattern"),
                          key=lambda x: x.start_byte)
            links = [(_line(sp), deps._txt(src, subj), *got) for sp in pats
                     if (got := _swift_pattern(src, sp))]
            if subj is not None and links:
                out += _chain_facts(mid, links)
        elif n.type == "check_expression" and n.id not in in_chain:
            out.append(TypeTestFact(mid, deps._field(src, n, "target"), (deps._field(src, n, "name"),),
                                    1, f"{mid}@{_line(n)}", _line(n), "type"))
        elif n.type == "as_expression" and any(c.type == "as_operator" and deps._txt(src, c) != "as"
                                               for c in n.named_children):
            out.append(TypeTestFact(mid, deps._field(src, n, "expr"), (deps._field(src, n, "name"),),
                                    1, f"{mid}@{_line(n)}", _line(n), "type"))
    return out


def _swift_catch_statements(clause) -> list:
    block = next((c for c in clause.named_children if c.type == "statements"), None)
    return list(block.named_children) if block is not None else []


def _swift_body_kind(src, body) -> str:
    """empty, throw (the body only throws or only calls fatalError), or other."""
    block = next((c for c in body.named_children if c.type == "statements"), None)
    stmts = [c for c in (block.named_children if block is not None else []) if c.type != "comment"]
    if not stmts:
        return "empty"
    if len(stmts) == 1:
        s = stmts[0]
        if any(c.type == "throw_keyword" for c in s.named_children):
            return "throw"
        if s.type == "call_expression" and s.named_children \
                and deps._txt(src, s.named_children[0]) in SWIFT_FATAL:
            return "throw"
    return "other"


# --- Rust ---------------------------------------------------------------------------------------

RUST_TYPES = {"struct_item": "struct", "enum_item": "enum", "trait_item": "interface"}
RUST_PANICS = frozenset({"unimplemented", "todo", "panic", "unreachable"})


def _rust(src, root, rel, roots=()) -> FileFacts:
    """A trait is an interface; `impl Trait for T` gives T its base, and every function of it is an
    override: Rust admits no function there that the trait does not declare. No catch: Rust
    returns `Result`."""
    ff = FileFacts(file=rel, lang="rust")
    ff.imports = [deps._txt(src, n.named_children[0]) for n in deps._walk(root)
                  if n.type == "use_declaration" and n.named_children]
    impls = sorted((n for n in deps._walk(root) if n.type == "impl_item"), key=lambda n: n.start_byte)
    traits_of: dict[str, list[str]] = {}
    for i in impls:
        if i.child_by_field_name("trait") is not None:
            traits_of.setdefault(_rust_name(src, i, "type"), []).append(_rust_name(src, i, "trait"))
    for t in sorted((n for n in deps._walk(root) if n.type in RUST_TYPES), key=lambda n: n.start_byte):
        name = deps._field(src, t, "name")
        kind = RUST_TYPES[t.type]
        supers = [_strip_generics(deps._txt(src, b)) for c in t.named_children
                  if c.type == "trait_bounds" for b in c.named_children]
        ff.types.append(TypeFact(name, kind, kind == "interface", rel, _line(t), "",
                                 tuple(supers + traits_of.get(name, []))))
        body = t.child_by_field_name("body")
        if t.type == "struct_item" and body is not None:
            ff.fields += [FieldFact(name, deps._field(src, f, "name"), _line(f),
                                    deps._field(src, f, "type"))
                          for f in body.named_children if f.type == "field_declaration"]
    fields_of: dict[str, set[str]] = {}
    for f in ff.fields:
        fields_of.setdefault(f.owner, set()).add(f.name)
    owners = [(deps._field(src, t, "name"), t, False) for t in deps._walk(root) if t.type == "trait_item"]
    owners += [(_rust_name(src, i, "type"), i, i.child_by_field_name("trait") is not None)
               for i in impls]
    for owner, decl, in_trait_impl in sorted(owners, key=lambda x: x[1].start_byte):
        body = decl.child_by_field_name("body")
        for m in (c for c in (body.named_children if body is not None else [])
                  if c.type in ("function_item", "function_signature_item")):
            mf = _rust_method(src, m, owner, in_trait_impl)
            ff.methods.append(mf)
            ff.trefs += _rust_trefs(src, m, mf.id)
            block = m.child_by_field_name("body")
            if block is None:
                continue
            ff.accesses += _rust_accesses(src, block, mf.id, owner, fields_of.get(owner, set()))
            ff.calls += _rust_calls(src, block, mf.id)
            ff.ttests += _rust_matches(src, block, mf.id)
            ff.bodies[mf.id] = _rust_body_kind(src, block)
            if mf.is_override:
                ff.obodies.append(OverrideBodyFact(mf.id, _rust_body_kind(src, block)))
    return ff


def _rust_name(src, n, field) -> str:
    """The type an impl names, without its generics or its path: `impl<T> a::Shape for Vec<T>`."""
    return _strip_generics(deps._field(src, n, field)).rsplit("::", 1)[-1]


def _rust_method(src, m, owner, in_trait_impl) -> MethodFact:
    ps = m.child_by_field_name("parameters")
    params = ps.named_children if ps is not None else []
    return MethodFact(owner=owner, name=deps._field(src, m, "name"),
                      arity=len([x for x in params if x.type == "parameter"]), line=_line(m),
                      end_line=m.end_point[0] + 1,
                      is_static=not any(x.type == "self_parameter" for x in params),
                      is_abstract=m.type == "function_signature_item", is_override=in_trait_impl)


def _rust_trefs(src, m, mid) -> list[TypedRefFact]:
    ps = m.child_by_field_name("parameters")
    return [TypedRefFact(mid, deps._field(src, x, "pattern"), deps._field(src, x, "type"), "param",
                         _line(x))
            for x in (ps.named_children if ps is not None else [])
            if x.type == "parameter" and x.child_by_field_name("type") is not None]


def _rust_accesses(src, block, mid, owner, field_names) -> list[AccessFact]:
    out = []
    for n in deps._walk(block):
        if n.type != "field_expression":
            continue
        v, field = n.child_by_field_name("value"), deps._field(src, n, "field")
        if v is not None and v.type == "self" and field in field_names:
            p = n.parent
            write = p is not None and p.type in ("assignment_expression",
                                                 "compound_assignment_expr") \
                and p.child_by_field_name("left") == n
            out.append(AccessFact(mid, f"field:{owner}.{field}", "w" if write else "r", _line(n)))
    return out


def _rust_calls(src, block, mid) -> list[CallFact]:
    out = []
    for n in deps._walk(block):
        f = n.child_by_field_name("function") if n.type == "call_expression" else None
        if f is None:
            continue
        if f.type == "field_expression":  # self.draw(), x.area()
            v = f.child_by_field_name("value")
            recv = deps._txt(src, v) if v is not None else ""
            out.append(CallFact(mid, deps._field(src, f, "field"), recv, _line(n)))
        elif f.type == "scoped_identifier":  # Sq::new(), the receiver is the path
            out.append(CallFact(mid, deps._field(src, f, "name"), deps._field(src, f, "path"),
                                _line(n)))
        elif f.type == "identifier":
            out.append(CallFact(mid, deps._txt(src, f), "", _line(n)))
    return out


def _rust_variant(src, pat) -> str:
    """`Kind::A`, `Kind::A(x)` or `Kind::A { .. }` → `Kind::A`; "" for any other pattern."""
    p = pat.named_children[0] if pat.named_children else None
    if p is None:
        return ""
    if p.type == "scoped_identifier":
        return deps._txt(src, p)
    if p.type in ("tuple_struct_pattern", "struct_pattern"):
        head = p.child_by_field_name("type") or (p.named_children[0] if p.named_children else None)
        return deps._txt(src, head) if head is not None and head.type == "scoped_identifier" else ""
    return ""


def _rust_matches(src, block, mid) -> list[TypeTestFact]:
    """A match whose arms are the variants of one enum (a wildcard arm aside)."""
    out = []
    for n in sorted((x for x in deps._walk(block) if x.type == "match_expression"),
                    key=lambda x: x.start_byte):
        subj, body = n.child_by_field_name("value"), n.child_by_field_name("body")
        pats = [a.child_by_field_name("pattern") for a in (body.named_children if body else [])
                if a.type == "match_arm"]
        pats = [p for p in pats if p is not None and deps._txt(src, p) != "_"]
        variants = [(_line(p), _rust_variant(src, p)) for p in pats]
        enums = {v.rsplit("::", 1)[0] for _, v in variants if v}
        if subj is not None and variants and all(v for _, v in variants) and len(enums) == 1:
            out += _chain_facts(mid, [(line, deps._txt(src, subj), v, "enum")
                                      for line, v in variants])
    return out


def _rust_body_kind(src, block) -> str:
    """empty, throw (the body only calls unimplemented!, todo!, panic! or unreachable!), or other."""
    stmts = [c for c in block.named_children if c.type not in ("line_comment", "block_comment")]
    if not stmts:
        return "empty"
    if len(stmts) == 1:
        s = stmts[0]
        mac = s if s.type == "macro_invocation" else next(
            (c for c in s.named_children if c.type == "macro_invocation"), None)
        if mac is not None and deps._field(src, mac, "macro") in RUST_PANICS:
            return "throw"
    return "other"


EXTRACTORS = {"csharp": _csharp, "python": _python, "gdscript": _gdscript,
              "typescript": _typescript, "tsx": _typescript, "cpp": _cpp,
              "c": _c, "swift": _swift, "rust": _rust}
