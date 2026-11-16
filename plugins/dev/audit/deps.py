#!/usr/bin/env python3
"""F3 — the dependency graph of the WHOLE project, in one run, incremental.

Why this exists. A navigation tool answers questions about one symbol. Asking it for the
dependencies of every file means one round trip through the model's context per file — on a
project of thousands of files that spends the whole budget on a single fact, while the
computation itself takes seconds. So the graph is built here, in-process, by a parser, and the
audit reads the result.

How it is built — algorithmic, no model involved. Every source file is parsed with its tree-sitter
grammar; comments and strings are separate node types to the parser, so a name in a comment is
NOT an edge. Three ways a file can depend on another, depending on what the language writes down:

  - BY PATH: the file names the other file. Python, JavaScript/TypeScript and Dart imports, C/C++
    `#include "…"`, GDScript `res://` paths and Godot scenes (.tscn/.tres `ext_resource` lines —
    in Godot a good part of the graph lives there, not in the scripts), Rust `mod x;`.
  - BY DECLARED NAME: the file uses a type another file of the project declares. GDScript
    `class_name` and autoloads; C#, Java, Kotlin, Swift, PHP, Rust, C++ type declarations; Perl
    packages. A name declared in several files is resolved by directory, then by the
    namespace/package the file declares or imports; a name still ambiguous after that is NOT an
    edge, and the count of those is reported.
  - BY PACKAGE: Go. `pkg.Name` resolves through the file's imports and go.mod to the file of the
    project's package that declares Name; an unqualified name to the file of the same package.

Each edge has a kind. `extends` is its own kind — a class that inherits from, implements or embeds
another (base lists, `extends`, `implements`, `with`, Rust `impl Trait for`, Go embedded fields,
Perl `use parent` / `@ISA`) — because the design questions about inheritance need it apart from a
plain use.

Incremental: each file's extraction is cached in `audit/.tools/deps-cache.json` under the sha1 of
its content. A run re-parses only the files whose content changed, then reassembles the graph,
which is cheap. After editing one file, one file is parsed.

Writes, under the output directory: deps.csv (file -> file, with the kind of reference),
deps-modules.csv (module -> module, with how many file edges carry it), cycles.txt (every set of
modules that depend on each other in a circle), decls.csv (what each file declares).

Languages without an adapter here are listed in the coverage report as not covered. They are
never guessed at.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

from resolve import TypeIndex

CACHE_VERSION = 5  # 2: class_name read from its `name` field, annotations are not references
                   # 3: a name the file declares itself (const, enum, var, …) shadows a class,
                   #    and a member after a dot (`A.Shot`) is not a global name
                   # 4: ten more languages, and inheritance recorded as its own kind
                   # 5: constructions recorded as their own kind, `new`
# The cache is also keyed by this file's own content: a change to an extractor re-parses everything
# even when nobody remembered to bump the version above — measured, it happened on the first edit.
_CACHE_KEY = f"{CACHE_VERSION}:{hashlib.sha1(Path(__file__).read_bytes()).hexdigest()}"


# ------------------------------------------------------------------------------------- helpers

def _parser(module_name: str, attr: str = "language"):
    """A tree-sitter parser for one grammar package, or None when it is not installed."""
    try:
        import tree_sitter as ts  # noqa: PLC0415 - optional dependency, checked at run time
        mod = __import__(module_name)
        return ts.Parser(ts.Language(getattr(mod, attr)()))
    except Exception:  # noqa: BLE001 - absent grammar is a declared gap, not an error
        return None


def _txt(src: bytes, n) -> str:
    return src[n.start_byte:n.end_byte].decode("utf-8", "replace")


def _texts(src: bytes, root, types: tuple[str, ...]) -> list[str]:
    return [_txt(src, n) for n in _walk(root) if n.type in types]


def _walk(root):
    stack = [root]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)


def _leaves(src: bytes, root, leaf_types, skip_types=(), skip_fields=None) -> list[str]:
    """The identifier leaves under `root`.

    `skip_types` prunes whole subtrees (type arguments, call arguments, comments, strings).
    `skip_fields` maps a node type to the fields whose child is NOT a global name: in `a.b`, `b`
    is a member of whatever `a` is, so it is never looked up as a class of the project."""
    skip_fields = skip_fields or {}
    out, stack = [], [root]
    while stack:
        n = stack.pop()
        if n.type in skip_types:
            continue
        if n.child_count == 0:
            if n.type in leaf_types:
                out.append(_txt(src, n))
            continue
        drop = skip_fields.get(n.type)
        if drop:
            for i, c in enumerate(n.children):
                if n.field_name_for_child(i) not in drop:
                    stack.append(c)
        else:
            stack.extend(n.children)
    return out


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'`" and s[-1] == s[0]:
        return s[1:-1]
    return s


def _field(src: bytes, n, name: str) -> str | None:
    f = n.child_by_field_name(name)
    return _txt(src, f) if f is not None else None


def _last_name(src: bytes, n) -> str | None:
    """The type a construction names, without its package or its type arguments:
    `com.x.Foo<T>` -> `Foo`, `pkg.Bar` -> `Bar`, `\\App\\Baz` -> `Baz`."""
    if n is None:
        return None
    t = re.sub(r"<.*", "", _txt(src, n)).strip()
    t = re.split(r"[.:\\]+", t)[-1].strip("&* ")
    return t if re.match(r"^[A-Za-z_]\w*$", t) else None


# What each language writes to CONSTRUCT an object, as (node type, field holding the type).
# A construction is its own edge kind, `new`: a parent that constructs its child is a factory,
# and a class constructed directly is concrete — both decide inheritance cases without reading.
NEW_NODES = {
    "java": (("object_creation_expression", "type"),),
    "csharp": (("object_creation_expression", "type"),),
    "cpp": (("new_expression", "type"),),
    "javascript": (("new_expression", "constructor"),),
    "php": (("object_creation_expression", None),),
    "go": (("composite_literal", "type"),),
    "rust": (("struct_expression", "name"),),
}
NEW_NODES["typescript"] = NEW_NODES["tsx"] = NEW_NODES["javascript"]
# Languages that construct by calling the type: `Foo(1)`. The callee is kept; resolution keeps it
# only when it names a class the project declares.
CALL_NEW = {"python": ("call", "function"), "kotlin": ("call_expression", None),
            "swift": ("call_expression", None), "dart": ("constructor_invocation", None)}


def constructed(lang: str, src: bytes, root) -> list[str]:
    out = []
    for n in _walk(root):
        for typ, fld in NEW_NODES.get(lang, ()):
            if n.type == typ:
                t = n.child_by_field_name(fld) if fld else next(
                    (c for c in n.children if c.is_named and c.type not in ("arguments",)), None)
                nm = _last_name(src, t)
                if nm:
                    out.append(nm)
        if lang in CALL_NEW and n.type == CALL_NEW[lang][0]:
            fld = CALL_NEW[lang][1]
            t = n.child_by_field_name(fld) if fld else (n.children[0] if n.children else None)
            if t is not None and t.type in ("identifier", "simple_identifier", "type_identifier"):
                out.append(_txt(src, t))
        if lang == "rust" and n.type == "call_expression":  # `Foo::new(…)`
            f = n.child_by_field_name("function")
            if f is not None and f.type == "scoped_identifier" and \
                    _field(src, f, "name") in ("new", "default"):
                nm = _last_name(src, f.child_by_field_name("path"))
                if nm:
                    out.append(nm)
        if lang == "gdscript" and n.type == "attribute" and len(n.children) >= 2:
            head = n.children[0]
            call = next((c for c in n.children[1:] if c.type != "."), None)  # `Foo` `.` `new()`
            if head.type == "identifier" and call is not None and call.type == "attribute_call" \
                    and call.children and _txt(src, call.children[0]) == "new":
                out.append(_txt(src, head))
    return sorted(set(out))


# ------------------------------------------------------------------------------------- adapters

class GDScript:
    lang, grammar, family = "gdscript", "tree_sitter_gdscript", "godot"
    exts = (".gd",)
    LOCAL_DECLS = ("const_statement", "enum_definition", "variable_statement", "signal_statement",
                   "function_definition", "class_definition")

    def __init__(self) -> None:
        self.parser = _parser(self.grammar)

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        # The declared name is the `name` FIELD of class_name_statement, and only that. Taking every
        # leaf of the statement also took the annotation in `@abstract class_name X` and the parent
        # in `class_name X extends Y` — so `abstract`, or `RefCounted`, became a "class" of the
        # project, and every file naming it got an edge. Measured: that one defect welded the
        # simulation to the game in a single false cycle.
        #
        # A name the file declares for itself shadows a project class or an autoload of the same
        # name, so it is not a reference: `const Seat := &"Seat"` and `enum Shot { … }` were read
        # as edges to the class Seat and the autoload Shot. Measured: two false module edges.
        decls, local, bases = [], set(), []
        for n in _walk(tree.root_node):
            if n.type == "class_name_statement":
                f = n.child_by_field_name("name")
                if f is not None:
                    decls.append(_txt(src, f))
            elif n.type in self.LOCAL_DECLS:
                f = n.child_by_field_name("name")
                if f is not None:
                    local.add(_txt(src, f))
            if n.type == "extends_statement":
                for c in n.children:
                    if c.type == "string":
                        bases.append(_unquote(_txt(src, c)))
                    elif c.type == "type":
                        bases += _leaves(src, c, ("identifier",))[:1]
        paths = sorted({_unquote(s) for s in _texts(src, tree.root_node, ("string",))
                        if "res://" in s})
        names = set(_leaf_names_gd(src, tree.root_node)) - local
        return {"decls": sorted(set(decls)), "names": sorted(names), "paths": paths,
                "news": constructed(self.lang, src, tree.root_node),
                "bases": sorted(set(bases))}


def _leaf_names_gd(src: bytes, root) -> list[str]:
    # An annotation (`@abstract`, `@tool`, `@export`) is not a reference to a class: its subtree is
    # skipped, or `abstract` would be read as a name the file uses.
    # In `A.B.c()` only `A` is looked up globally: `B` and `c` are members of what comes before the
    # dot, so `ReplayCameras.Shot` does not name the autoload `Shot`. The calls' arguments are kept.
    out, stack = [], [root]
    while stack:
        n = stack.pop()
        if n.type in ("annotation", "annotations"):
            continue
        if n.child_count == 0 and n.type in ("identifier", "name", "type"):
            out.append(_txt(src, n))
        if n.type == "attribute" and n.children:
            stack.append(n.children[0])
            for c in n.children[1:]:
                if c.type == "attribute_call":
                    stack.extend(a for a in c.children if a.type == "arguments")
                elif c.type not in ("identifier", "."):
                    stack.append(c)
            continue
        stack.extend(n.children)
    return out


class Python:
    lang, grammar, family = "python", "tree_sitter_python", "python"
    exts = (".py",)

    def __init__(self) -> None:
        self.parser = _parser(self.grammar)

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        imports, named, bases, decls = [], {}, [], []
        stack = [tree.root_node]
        while stack:
            n = stack.pop()
            if n.type == "import_statement":
                for d in n.children:
                    if d.type == "dotted_name":
                        imports.append(_txt(src, d))
                    elif d.type == "aliased_import":
                        nm, al = _field(src, d, "name"), _field(src, d, "alias")
                        if nm:
                            imports.append(nm)
                            if al:
                                named[al] = f"{nm}:"
                continue
            if n.type == "import_from_statement":
                mod = _field(src, n, "module_name")
                if mod is not None:
                    imports.append(mod)
                    for i, c in enumerate(n.children):
                        if n.field_name_for_child(i) != "name":
                            continue
                        if c.type == "aliased_import":
                            nm, al = _field(src, c, "name"), _field(src, c, "alias")
                            if nm:
                                named[al or nm] = f"{mod}:{nm}"
                        else:
                            named[_txt(src, c)] = f"{mod}:{_txt(src, c)}"
                continue
            if n.type == "class_definition":
                nm = _field(src, n, "name")
                if nm:
                    decls.append(nm)
                sup = n.child_by_field_name("superclasses")
                if sup is not None:
                    for c in sup.children:
                        if c.type in ("identifier", "attribute"):
                            bases.append(_txt(src, c))
            stack.extend(n.children)
        return {"imports": sorted(set(imports)), "named": named, "bases": sorted(set(bases)),
                "news": constructed(self.lang, src, tree.root_node),
                "decls": sorted(set(decls))}


class EcmaScript:
    lang, family = "javascript", "ecma"
    exts = (".js", ".jsx", ".mjs", ".cjs")

    def __init__(self, grammar: str = "tree_sitter_javascript", attr: str = "language") -> None:
        self.parser = _parser(grammar, attr)

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        specs, named, bases, decls = [], {}, [], []
        for n in _walk(tree.root_node):
            if n.type in ("import_statement", "export_statement"):
                s = n.child_by_field_name("source")
                if s is not None:
                    spec = _unquote(_txt(src, s))
                    specs.append(spec)
                    for c in _walk(n):
                        if c.type == "import_specifier":
                            nm, al = _field(src, c, "name"), _field(src, c, "alias")
                            if nm:
                                named[al or nm] = spec
                        elif c.type in ("import_clause", "namespace_import"):
                            for d in c.children:
                                if d.type == "identifier":
                                    named[_txt(src, d)] = spec
            elif n.type == "call_expression":
                fn = n.child_by_field_name("function")
                args = n.child_by_field_name("arguments")
                if fn is not None and args is not None and \
                        src[fn.start_byte:fn.end_byte] in (b"require", b"import"):
                    strs = _texts(src, args, ("string",))
                    if strs:
                        specs.append(_unquote(strs[0]))
            elif n.type in ("class_declaration", "class", "abstract_class_declaration",
                            "interface_declaration"):
                nm = _field(src, n, "name")
                if nm:
                    decls.append(nm)
            elif n.type in ("extends_clause", "implements_clause", "extends_type_clause"):
                bases += _leaves(src, n, ("identifier", "type_identifier"),
                                 skip_types=("type_arguments", "arguments"),
                                 skip_fields={"member_expression": {"property"}})
        return {"imports": sorted(set(specs)), "named": named, "bases": sorted(set(bases)),
                "news": constructed(self.lang, src, tree.root_node),
                "decls": sorted(set(decls))}


class TypeScript(EcmaScript):
    lang = "typescript"
    exts = (".ts", ".mts", ".cts")

    def __init__(self) -> None:
        super().__init__("tree_sitter_typescript", "language_typescript")


class TSX(EcmaScript):
    lang = "tsx"
    exts = (".tsx",)

    def __init__(self) -> None:
        super().__init__("tree_sitter_typescript", "language_tsx")


class TypeNames:
    """The languages where a file depends on another by USING A TYPE it declares.

    Configured per language with the node types of its parser: which nodes declare a type, which
    nodes list the bases of a class, which leaves are names, which fields of a member access are
    members (never global names), and where the namespace and the imports are written."""

    grammar = ""
    family = ""
    decl_types: tuple[str, ...] = ()
    base_types: tuple[str, ...] = ()
    leaf_types: tuple[str, ...] = ("identifier", "type_identifier")
    skip_types: tuple[str, ...] = ("comment", "line_comment", "block_comment",
                                   "string", "string_literal", "raw_string_literal")
    skip_fields: dict[str, set[str]] = {}
    base_skip: tuple[str, ...] = ("type_arguments", "type_argument_list", "template_argument_list",
                                  "value_arguments", "argument_list", "arguments")
    ns_types: tuple[str, ...] = ()
    import_types: tuple[str, ...] = ()

    def __init__(self) -> None:
        self.parser = _parser(self.grammar, getattr(self, "attr", "language"))

    def is_decl(self, src: bytes, n) -> bool:
        return True

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        decls, bases, ns, imports = [], [], None, []
        for n in _walk(tree.root_node):
            if n.type in self.decl_types and self.is_decl(src, n):
                nm = n.child_by_field_name("name")
                if nm is not None:
                    decls.append(_txt(src, nm).split("<")[0].strip())
            if n.type in self.base_types:
                bases += self.base_names(src, n)
            if n.type in self.ns_types and ns is None:
                ns = self.namespace(src, n)
            if n.type in self.import_types:
                imports += self.import_names(src, n)
        names = set(_leaves(src, tree.root_node, self.leaf_types, self.skip_types,
                            self.skip_fields))
        return {"decls": sorted(set(decls)), "names": sorted(names - set(decls)),
                "bases": sorted(set(bases)), "ns": ns, "imports": sorted(set(imports)),
                "news": constructed(self.lang, src, tree.root_node),
                **self.more(src, tree.root_node)}

    def base_names(self, src: bytes, n) -> list[str]:
        return _leaves(src, n, self.leaf_types, self.base_skip, self.skip_fields)

    def namespace(self, src: bytes, n) -> str | None:
        f = n.child_by_field_name("name")
        return _txt(src, f).strip() if f is not None else None

    def import_names(self, src: bytes, n) -> list[str]:
        return [re.sub(r"\s+", "", _txt(src, n))]

    def more(self, src: bytes, root) -> dict:
        return {}


class CSharp(TypeNames):
    lang, grammar, family = "csharp", "tree_sitter_c_sharp", "dotnet"
    exts = (".cs",)
    decl_types = ("class_declaration", "interface_declaration", "struct_declaration",
                  "record_declaration", "record_struct_declaration", "enum_declaration",
                  "delegate_declaration")
    base_types = ("base_list",)
    leaf_types = ("identifier",)
    skip_fields = {"member_access_expression": {"name"}}
    ns_types = ("namespace_declaration", "file_scoped_namespace_declaration")
    import_types = ("using_directive",)

    def import_names(self, src: bytes, n) -> list[str]:
        # `global using X;` (C# 10) imports X into every file of the project; it is marked, and
        # the resolution applies it everywhere.
        glob = any(c.type == "global" or _txt(src, c) == "global" for c in n.children)
        for c in n.children:
            if c.type in ("qualified_name", "identifier"):
                return [("global:" if glob else "") + _txt(src, c)]
        return []


class Java(TypeNames):
    lang, grammar, family = "java", "tree_sitter_java", "jvm"
    exts = (".java",)
    decl_types = ("class_declaration", "interface_declaration", "enum_declaration",
                  "record_declaration", "annotation_type_declaration")
    base_types = ("superclass", "super_interfaces", "extends_interfaces")
    skip_fields = {"field_access": {"field"}, "method_invocation": {"name"}}
    ns_types = ("package_declaration",)
    import_types = ("import_declaration",)

    def namespace(self, src: bytes, n) -> str | None:
        for c in n.children:
            if c.type in ("scoped_identifier", "identifier"):
                return _txt(src, c)
        return None

    def import_names(self, src: bytes, n) -> list[str]:
        t = re.sub(r"\s+", " ", _txt(src, n)).replace("import ", "").replace("static ", "")
        return [t.strip().rstrip(";").strip()]


class Kotlin(TypeNames):
    lang, grammar, family = "kotlin", "tree_sitter_kotlin", "jvm"
    exts = (".kt", ".kts")
    decl_types = ("class_declaration", "object_declaration", "type_alias")
    base_types = ("delegation_specifier",)
    leaf_types = ("identifier", "type_identifier", "simple_identifier")
    skip_types = TypeNames.skip_types + ("navigation_suffix",)
    ns_types = ("package_header",)
    import_types = ("import", "import_header")

    def base_names(self, src: bytes, n) -> list[str]:
        for c in _walk(n):
            if c.type == "user_type":
                return _leaves(src, c, self.leaf_types, self.base_skip)
        return []

    def namespace(self, src: bytes, n) -> str | None:
        t = re.sub(r"\s+", " ", _txt(src, n)).replace("package ", "").strip()
        return t or None

    def import_names(self, src: bytes, n) -> list[str]:
        t = re.sub(r"\s+", " ", _txt(src, n)).replace("import ", "").strip()
        return [t.split(" as ")[0].strip()] if t else []


class Swift(TypeNames):
    lang, grammar, family = "swift", "tree_sitter_swift", "swift"
    exts = (".swift",)
    decl_types = ("class_declaration", "protocol_declaration", "typealias_declaration")
    base_types = ("inheritance_specifier",)
    leaf_types = ("type_identifier", "simple_identifier")
    skip_fields = {"navigation_expression": {"suffix"}}

    def is_decl(self, src: bytes, n) -> bool:
        # `extension Circle` is declared with the same node as a class, but it names a type that
        # lives elsewhere: it is a use of Circle, not a declaration of it.
        k = n.child_by_field_name("declaration_kind")
        return not (k is not None and _txt(src, k) == "extension")

    def more(self, src: bytes, root) -> dict:
        ext = []
        for n in _walk(root):
            if n.type == "class_declaration" and not self.is_decl(src, n):
                nm = n.child_by_field_name("name")
                if nm is not None:
                    ext += _leaves(src, nm, self.leaf_types)
        return {"bases_extra": sorted(set(ext))}


class PHP(TypeNames):
    lang, grammar, family, attr = "php", "tree_sitter_php", "php", "language_php"
    exts = (".php",)
    decl_types = ("class_declaration", "interface_declaration", "trait_declaration",
                  "enum_declaration")
    base_types = ("base_clause", "class_interface_clause", "use_declaration")
    leaf_types = ("name",)
    skip_fields = {"member_access_expression": {"name"}, "member_call_expression": {"name"},
                   "scoped_call_expression": {"name"},
                   "class_constant_access_expression": {"name"}}
    skip_types = TypeNames.skip_types + ("encapsed_string", "heredoc", "nowdoc", "variable_name")
    ns_types = ("namespace_definition",)
    import_types = ("namespace_use_clause",)

    def base_names(self, src: bytes, n) -> list[str]:
        out = []
        for c in _walk(n):
            if c.type in ("name", "qualified_name") and c.parent is not None and \
                    c.parent.type != "qualified_name":
                out.append(_txt(src, c).split("\\")[-1])
        return out

    def import_names(self, src: bytes, n) -> list[str]:
        return [_txt(src, n).split(" as ")[0].strip().lstrip("\\")]


class Rust(TypeNames):
    lang, grammar, family = "rust", "tree_sitter_rust", "rust"
    exts = (".rs",)
    decl_types = ("struct_item", "enum_item", "trait_item", "type_item", "union_item")
    skip_fields = {"field_expression": {"field"}}
    import_types = ("use_declaration",)

    def import_names(self, src: bytes, n) -> list[str]:
        t = re.sub(r"\s+", "", _txt(src, n))
        return [t.removeprefix("pub").removeprefix("use").rstrip(";")]

    def more(self, src: bytes, root) -> dict:
        impl, mods = [], []
        for n in _walk(root):
            if n.type == "impl_item":
                t = n.child_by_field_name("trait")
                if t is not None:
                    impl += _leaves(src, t, self.leaf_types, self.base_skip)[-1:]
            elif n.type == "mod_item" and n.child_by_field_name("body") is None:
                nm = _field(src, n, "name")
                if nm:
                    mods.append(nm)
        return {"bases_extra": sorted(set(impl)), "mods": sorted(set(mods))}


class CFamily(TypeNames):
    """C and C++. The graph is the `#include "…"` lines, resolved to files of the project; C++
    base classes are resolved by name to the file that declares the class."""
    leaf_types = ("type_identifier",)

    def more(self, src: bytes, root) -> dict:
        inc = []
        for n in _walk(root):
            if n.type == "preproc_include":
                p = n.child_by_field_name("path")
                if p is not None and p.type == "string_literal":
                    inc.append(_unquote(_txt(src, p)))
        return {"includes": sorted(set(inc))}

    def extract(self, src: bytes) -> dict:
        rec = super().extract(src)
        rec.pop("names", None)  # C/C++ depend through their includes, not through bare names
        return rec


class C(CFamily):
    lang, grammar, family = "c", "tree_sitter_c", "cfam"
    exts = (".c", ".h")


class Cpp(CFamily):
    lang, grammar, family = "cpp", "tree_sitter_cpp", "cfam"
    exts = (".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".ipp", ".inl")
    decl_types = ("class_specifier", "struct_specifier")
    base_types = ("base_class_clause",)

    def is_decl(self, src: bytes, n) -> bool:
        # `class X;` is a forward declaration: the class is defined somewhere else
        return n.child_by_field_name("body") is not None


class Dart(TypeNames):
    """Dart names the file it imports, so the graph is its imports; the bases are resolved among
    the files it imports (a Dart file cannot use what it does not import)."""
    lang, grammar, family = "dart", "tree_sitter_dart", "dart"
    exts = (".dart",)
    decl_types = ("class_definition", "mixin_declaration", "enum_declaration", "type_alias")
    base_types = ("superclass", "interfaces", "mixins")

    def more(self, src: bytes, root) -> dict:
        uris = []
        for n in _walk(root):
            if n.type in ("library_import", "library_export", "part_directive"):
                for s in _walk(n):
                    if s.type in ("string_literal", "uri"):
                        uris.append(_unquote(_txt(src, s)))
                        break
        return {"uris": sorted(set(uris))}

    def extract(self, src: bytes) -> dict:
        rec = super().extract(src)
        rec.pop("names", None)
        return rec


class Go:
    lang, grammar, family = "go", "tree_sitter_go", "go"
    exts = (".go",)

    def __init__(self) -> None:
        self.parser = _parser(self.grammar)

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        root = tree.root_node
        decls, imports, qual, names, bases = [], {}, set(), set(), []
        for n in root.children:
            if n.type in ("function_declaration", "type_declaration", "const_declaration",
                          "var_declaration"):
                for c in _walk(n):
                    if c.type in ("type_spec", "type_alias", "const_spec", "var_spec",
                                  "function_declaration"):
                        nm = c.child_by_field_name("name")
                        if nm is not None:
                            decls.append(_txt(src, nm))
            elif n.type == "import_declaration":
                for s in _walk(n):
                    if s.type == "import_spec":
                        p = _unquote(_field(src, s, "path") or "")
                        alias = _field(src, s, "name")
                        if p:
                            imports[alias or p.rsplit("/", 1)[-1]] = p
        for n in _walk(root):
            if n.type == "selector_expression":
                op, fld = n.child_by_field_name("operand"), n.child_by_field_name("field")
                if op is not None and fld is not None and op.type == "identifier":
                    qual.add(f"{_txt(src, op)}.{_txt(src, fld)}")
            elif n.type == "qualified_type":
                pk, nm = n.child_by_field_name("package"), n.child_by_field_name("name")
                if pk is not None and nm is not None:
                    qual.add(f"{_txt(src, pk)}.{_txt(src, nm)}")
            elif n.type in ("identifier", "type_identifier") and n.child_count == 0:
                names.add(_txt(src, n))
            elif n.type == "field_declaration" and n.child_by_field_name("name") is None:
                t = n.child_by_field_name("type")
                if t is not None:
                    bases.append(_txt(src, t).lstrip("*"))
        return {"decls": sorted(set(decls)), "imports": imports, "qual": sorted(qual),
                "news": constructed(self.lang, src, root),
                "names": sorted(names - set(decls)), "bases": sorted(set(bases))}


class Perl:
    lang, grammar, family = "perl", "tree_sitter_perl", "perl"
    exts = (".pm", ".pl", ".t")
    PRAGMAS = {"strict", "warnings", "utf8", "lib", "constant", "vars", "feature", "integer",
               "overload", "base", "parent", "fields", "open", "POSIX", "Exporter"}

    def __init__(self) -> None:
        self.parser = _parser(self.grammar)

    def extract(self, src: bytes) -> dict:
        tree = self.parser.parse(src)
        decls, uses, bases = [], [], []
        for n in _walk(tree.root_node):
            if n.type == "package_statement":
                for c in n.children:
                    if c.type == "package" and _txt(src, c) != "package":
                        decls.append(_txt(src, c))
            elif n.type == "use_statement":
                pk = [c for c in n.children if c.type == "package"]
                if not pk:
                    continue
                name = _txt(src, pk[0])
                if name in ("parent", "base"):
                    for s in _texts(src, n, ("string_content", "bareword")):
                        bases += [w for w in re.split(r"[\s,]+", s) if w and w != "-norequire"]
                elif name not in self.PRAGMAS:
                    uses.append(name)
        for m in re.finditer(rb"@ISA\s*=\s*(?:qw)?\s*[\(\[]([^)\]]*)[\)\]]", src):
            bases += [_unquote(w) for w in
                      re.split(r"[\s,]+", m.group(1).decode("utf-8", "replace")) if w.strip()]
        return {"decls": sorted(set(decls)), "uses": sorted(set(uses)),
                "bases": sorted(set(b for b in bases if b))}


ADAPTERS = (GDScript, Python, EcmaScript, TypeScript, TSX, CSharp, Java, Kotlin, Swift, PHP, Rust,
            C, Cpp, Dart, Go, Perl)

# A file format, not a language: Godot scenes and resources name what they load on fixed lines.
EXT_RESOURCE = re.compile(r'^\[ext_resource\b[^\]]*\bpath="(res://[^"]+)"')
SCENE_EXTS = (".tscn", ".tres")
# Source extensions no adapter covers: listed as NOT covered in the coverage report, never guessed.
KNOWN_UNCOVERED = (".rb", ".scala", ".mm", ".m", ".lua", ".ex", ".exs", ".clj", ".fs", ".vb",
                   ".erl", ".hs", ".zig", ".jl")
# Directories that are never the project's own code: vendored, generated, build output.
SKIP_DIRS = {"node_modules", ".git", "vendor", "third_party", "_deps", ".cpm_cache", "target",
             "dist", "build", "obj", ".godot", ".import", "__pycache__", ".venv", "venv",
             ".gradle", ".dart_tool", "Pods", "DerivedData", ".build", ".tools"}


# ------------------------------------------------------------------------------------- the graph

def _sha(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def _res_to_rel(p: str) -> str:
    return p.split("res://", 1)[1].split("::", 1)[0] if "res://" in p else p


TEST_DIRS = ("test", "tests", "spec", "specs", "__tests__", "testing", "androidtest",
             "testfixtures", "unittests", "integrationtests")
TEST_NAME = re.compile(r"(^test_.*\.py$|_test\.(py|go|dart|rs|gd|exs?)$|(Tests?|Spec)\.(java|kt|cs|swift|php)$"
                       r"|\.(test|spec)\.[jt]sx?$|^test_.*\.gd$|\.t$)")


def is_test_path(rel: str, test_names=TEST_DIRS) -> bool:
    """A test file, by the directory it lives in or by the naming convention of its language."""
    p = Path(rel)
    names = {t.lower() for t in test_names}
    return any(part.lower() in names for part in p.parts[:-1]) or bool(TEST_NAME.search(p.name))


def is_generated(p: Path) -> bool:
    """A minified or bundled file: `x.min.js`, or a first 64 KiB with a line of thousands of
    characters. Nobody wrote it, so nothing in it is a design decision of the project."""
    if ".min." in p.name or p.name.endswith((".bundle.js", ".pb.go", "_pb2.py", ".g.dart",
                                              ".freezed.dart", ".designer.cs", ".g.cs")):
        return True
    try:
        with p.open("rb") as fh:
            head = fh.read(65536)
    except OSError:
        return False
    return any(len(line) > 2000 for line in head.split(b"\n"))


def is_excluded(rel_parts: tuple[str, ...]) -> bool:
    """Not the project's code: vendored or build directories, hidden directories (`.claude`,
    `.github`, `.venv`), and the audit's OWN root `audit/` — with `--src .` the audit would
    otherwise analyse its own output."""
    dirs = rel_parts[:-1]
    return bool(SKIP_DIRS & set(dirs)) or any(d.startswith(".") for d in dirs) or \
        (len(dirs) > 0 and dirs[0] == "audit")


def git_ignored(repo: Path, src_roots: list[str]) -> tuple[str, ...]:
    """What git ignores under the roots — files, and folders as `<folder>/` — relative to the
    project: a third party's code brought in, build output. Nothing outside a git repository."""
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "--others", "--ignored",
                            "--exclude-standard", "--directory", "--", *src_roots], cwd=repo,
                           capture_output=True, text=True, check=False)
    except OSError:
        return ()
    return tuple(line for line in r.stdout.splitlines() if line) if r.returncode == 0 else ()


def source_files(repo: Path, src_roots: list[str]) -> list[Path]:
    """Every file under the roots, minus what is never the project's own code (`is_excluded`),
    what git ignores, and generated or minified files."""
    ignored = git_ignored(repo, src_roots)
    folders = tuple(i for i in ignored if i.endswith("/"))
    names = frozenset(i for i in ignored if not i.endswith("/"))
    files: list[Path] = []
    for r in src_roots:
        for p in (repo / r).rglob("*"):
            rel = p.relative_to(repo)
            if not p.is_file() or is_excluded(rel.parts):
                continue
            posix = rel.as_posix()
            if posix in names or posix.startswith(folders) or is_generated(p):
                continue
            files.append(p)
    return sorted(set(files))


def tarjan(nodes: set[str], edges: dict[str, set[str]]) -> list[list[str]]:
    """Strongly connected components with more than one node. Iterative: a file graph of
    thousands of nodes overflows a recursive version."""
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = 0
    for root in sorted(nodes):
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on.add(root)
        work = [(root, iter(sorted(edges.get(root, ()))))]
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(sorted(edges.get(w, ())))))
                    advanced = True
                    break
                if w in on:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    out.append(sorted(comp))
    return sorted(out, key=lambda c: (-len(c), c))


def adapter_table(files: list[Path]):
    """extension -> adapter with a parser, the languages whose grammar is missing, and the
    extensions those would have covered. Shared with similar.py, which parses the same files."""
    adapters = [a() for a in ADAPTERS]
    by_ext = {}
    missing_grammars = []
    for a in adapters:
        if a.parser is None:
            missing_grammars.append(a.lang)
            continue
        for e in a.exts:
            by_ext[e] = a
    missing_exts = {e for a in adapters if a.parser is None for e in a.exts}
    # `.h` is C until the project has C++ in it: then its headers are C++, base classes and all.
    cpp = next((a for a in adapters if a.lang == "cpp" and a.parser is not None), None)
    if cpp is not None and any(f.suffix.lower() in cpp.exts for f in files):
        by_ext[".h"] = cpp
    return by_ext, missing_grammars, missing_exts


def collect_deps(repo: Path, out: Path, cache_dir: Path, src_roots: list[str],
                 module_of, roots: set[str], depth: int, test_names=TEST_DIRS) -> dict:
    """Build the graph. Returns a summary and the coverage detail; never raises on a bad file."""
    files = source_files(repo, src_roots)
    by_ext, missing_grammars, missing_exts = adapter_table(files)

    cache_path = cache_dir / "deps-cache.json"
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("version") != _CACHE_KEY:
            cache = {}
    except (OSError, ValueError):
        cache = {}
    old = cache.get("files", {})
    new: dict[str, dict] = {}
    parsed = reused = 0
    uncovered = collections.Counter()

    for f in files:
        rel = f.relative_to(repo).as_posix()
        ext = f.suffix.lower()
        if ext not in by_ext and ext not in SCENE_EXTS:
            if ext in KNOWN_UNCOVERED or ext in missing_exts:
                uncovered[ext] += 1
            continue
        try:
            data = f.read_bytes()
        except OSError:
            continue
        sha = _sha(data)
        hit = old.get(rel)
        if hit and hit.get("sha") == sha:
            new[rel] = hit
            reused += 1
            continue
        if ext in SCENE_EXTS:
            text = data.decode("utf-8", "replace")
            rec = {"lang": "godot-resource",
                   "paths": sorted({m.group(1) for line in text.splitlines()
                                    if (m := EXT_RESOURCE.match(line))})}
        else:
            a = by_ext[ext]
            try:
                rec = {"lang": a.lang, "family": a.family, **a.extract(data)}
            except Exception:  # noqa: BLE001 - one unparsable file must not sink the graph
                rec = {"lang": a.lang, "error": True}
        rec["sha"] = sha
        new[rel] = rec
        parsed += 1

    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": _CACHE_KEY, "files": new}, sort_keys=True),
                   encoding="utf-8")
    tmp.replace(cache_path)

    edges, ambiguous = _resolve(repo, new, src_roots, test_names)

    out.mkdir(parents=True, exist_ok=True)
    with (out / "deps.csv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("from,to,kind\n")
        for a, b, k in sorted(edges):
            fh.write(f"{a},{b},{k}\n")

    # What each file DECLARES — its classes, interfaces, types, packages. The census of what a
    # module does is built from this and from the project's documents, without opening the code.
    with (out / "decls.csv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("module,file,lang,declares\n")
        for rel in sorted(new):
            r = new[rel]
            if r.get("decls"):
                fh.write(f"{module_of(rel, roots, depth) or ''},{rel},{r.get('lang')},"
                         f"{' '.join(r['decls'])}\n")

    mod_edges: collections.Counter[tuple[str, str]] = collections.Counter()
    for a, b, _ in edges:
        ma, mb = module_of(a, roots, depth), module_of(b, roots, depth)
        if ma and mb and ma != mb:
            mod_edges[(ma, mb)] += 1
    with (out / "deps-modules.csv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("from_module,to_module,file_edges\n")
        for (a, b), n in sorted(mod_edges.items(), key=lambda kv: (-kv[1], kv[0])):
            fh.write(f"{a},{b},{n}\n")

    graph: dict[str, set[str]] = collections.defaultdict(set)
    nodes: set[str] = set()
    for (a, b) in mod_edges:
        graph[a].add(b)
        nodes |= {a, b}
    cycles = tarjan(nodes, graph)
    with (out / "cycles.txt").open("w", encoding="utf-8") as fh:
        fh.write("# Sets of modules that depend on each other in a circle "
                 "(strongly connected components of deps-modules.csv)\n")
        for c in cycles:
            fh.write(f"{len(c)} modules: {' <-> '.join(c)}\n")

    return {"files": len(new), "parsed": parsed, "reused": reused,
            "errors": sum(1 for r in new.values() if r.get("error")),
            "edges": len(edges), "module_edges": len(mod_edges), "cycles": cycles,
            "uncovered": dict(uncovered), "missing_grammars": missing_grammars,
            "ambiguous": dict(ambiguous),
            "langs": dict(collections.Counter(r.get("lang") for r in new.values())),
            "kinds": dict(collections.Counter(k for _, _, k in edges)),
            "top": sorted(mod_edges.items(), key=lambda kv: -kv[1])[:8]}


def _normpath(p: Path) -> str:
    parts: list[str] = []
    for s in p.as_posix().split("/"):
        if s in ("", "."):
            continue
        if s == "..":
            if parts:
                parts.pop()
        else:
            parts.append(s)
    return "/".join(parts)


def _resolve(repo: Path, new: dict[str, dict], src_roots: list[str], test_names=TEST_DIRS):
    """Turn every file's extraction into edges. Pure computation on the cached records."""
    present = set(new)
    edges: set[tuple[str, str, str]] = set()

    def add(a: str, b: str | None, kind: str) -> None:
        if b and b != a and b in present:
            edges.add((a, b, kind))

    # --- declared names, per family: a Java class never resolves a Swift reference
    decl_map: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for rel, rec in new.items():
        if rec.get("error"):
            continue
        fam = rec.get("family") or rec.get("lang")
        for d in rec.get("decls", ()):
            decl_map[(fam, d)].append(rel)

    tests = {rel for rel in present if is_test_path(rel, test_names)}

    def visible(rel: str, cands) -> list[str]:
        return [c for c in cands if c != rel and (rel in tests or c not in tests)]

    index = TypeIndex(decl_map, new, tests)
    by_name = index.resolve

    # --- Godot autoloads
    autoload: dict[str, str] = {}
    pg = repo / "project.godot"
    if pg.is_file():
        section = ""
        for line in pg.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("["):
                section = s
            elif section == "[autoload]" and "=" in s:
                name, val = s.split("=", 1)
                target = _res_to_rel(_unquote(val).lstrip("*"))
                if target in present:
                    autoload[name.strip()] = target

    def resolve_py(src_rel: str, mod: str) -> str | None:
        base = Path(src_rel).parent
        if mod.startswith("."):
            dots = len(mod) - len(mod.lstrip("."))
            for _ in range(dots - 1):
                base = base.parent
            parts = [p for p in mod.lstrip(".").split(".") if p]
            cands = [base.joinpath(*parts)] if parts else [base]
        else:
            parts = mod.split(".")
            cands = [Path(*parts)] + [Path(r).joinpath(*parts) for r in src_roots]
        for c in cands:
            for cand in (c.with_suffix(".py"), c / "__init__.py"):
                if cand.as_posix() in present:
                    return cand.as_posix()
        return None

    def resolve_es(src_rel: str, spec: str) -> str | None:
        if not spec.startswith("."):
            return None
        stem = _normpath(Path(src_rel).parent / spec)
        exts = ("", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts")
        for e in exts:
            if stem + e in present:
                return stem + e
        # ESM TypeScript imports `./x.js` and means the source `x.ts`
        bare, dot, ext = stem.rpartition(".")
        if dot and ext in ("js", "jsx", "mjs", "cjs"):
            for e in (".ts", ".tsx", ".mts", ".cts"):
                if bare + e in present:
                    return bare + e
        for e in exts[1:]:
            if f"{stem}/index{e}" in present:
                return f"{stem}/index{e}"
        return None

    # headers by basename, for includes that name a header relative to an include directory
    by_basename: dict[str, list[str]] = collections.defaultdict(list)
    for rel in present:
        by_basename[Path(rel).name].append(rel)

    def resolve_include(src_rel: str, inc: str) -> str | None:
        local = _normpath(Path(src_rel).parent / inc)
        if local in present:
            return local
        for r in src_roots:
            c = _normpath(Path(r) / inc)
            if c in present:
                return c
        cands = [c for c in by_basename.get(Path(inc).name, ())
                 if c.endswith("/" + inc) or c == inc]
        return cands[0] if len(cands) == 1 else None

    def manifests(name: str):
        for m in repo.rglob(name):
            if not (SKIP_DIRS & set(m.relative_to(repo).parts[:-1])):
                yield m, m.read_text(encoding="utf-8", errors="replace")

    # Dart `package:<name>/x.dart` is lib/x.dart of the package whose pubspec says <name>
    dart_pkgs: dict[str, str] = {}
    if any(r.get("lang") == "dart" for r in new.values()):
        for pub, text in manifests("pubspec.yaml"):
            m = re.search(r"^name:\s*(\S+)", text, re.M)
            if m:
                dart_pkgs[m.group(1)] = _normpath(pub.parent.relative_to(repo) / "lib")

    def resolve_dart(src_rel: str, uri: str) -> str | None:
        if uri.startswith("package:"):
            pkg, _, rest = uri[len("package:"):].partition("/")
            base = dart_pkgs.get(pkg)
            return _normpath(Path(base) / rest) if base is not None else None
        if ":" in uri:
            return None
        return _normpath(Path(src_rel).parent / uri)

    # Go: the module path of go.mod maps an import path to a directory of the project
    go_mods: list[tuple[str, str]] = []
    go_dir_decls: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    if any(r.get("lang") == "go" for r in new.values()):
        for gm, text in manifests("go.mod"):
            m = re.search(r"^module\s+(\S+)", text, re.M)
            if m:
                go_mods.append((m.group(1), _normpath(gm.parent.relative_to(repo))))
        for rel, rec in new.items():
            if rec.get("lang") == "go" and not rec.get("error"):
                for d in rec.get("decls", ()):
                    go_dir_decls[(Path(rel).parent.as_posix(), d)].append(rel)

    def go_dir(path: str) -> str | None:
        for mod, root in sorted(go_mods, key=lambda x: -len(x[0])):
            if path == mod or path.startswith(mod + "/"):
                rest = path[len(mod):].lstrip("/")
                return "/".join(p for p in (root, rest) if p) or "."
        return None

    def go_file(rel: str, d: str | None, name: str) -> str | None:
        hit = visible(rel, go_dir_decls.get((d, name), ())) if d else ()
        return hit[0] if hit else None

    # Perl: a package resolves to the file that declares it, else to its path under the roots
    def resolve_perl(rel: str, rec: dict, pkg: str) -> list[str]:
        hit = by_name(rel, rec, pkg)
        if hit:
            return hit
        tail = pkg.replace("::", "/") + ".pm"
        return sorted(c for c in present if c.endswith("/" + tail) or c == tail)[:1]

    for rel, rec in new.items():
        if rec.get("error"):
            continue
        lang = rec.get("lang")
        if lang == "gdscript":
            own = set(rec.get("decls", ()))
            for n in rec.get("names", ()):
                if n in own:
                    continue
                hit = visible(rel, decl_map.get(("godot", n), ()))
                if hit:
                    add(rel, hit[0], "class")
                elif n in autoload:
                    add(rel, autoload[n], "autoload")
            for p in rec.get("paths", ()):
                add(rel, _res_to_rel(p), "path")
            for b in rec.get("bases", ()):
                if "res://" in b:
                    add(rel, _res_to_rel(b), "extends")
                elif b.endswith(".gd"):
                    add(rel, _normpath(Path(rel).parent / b), "extends")
                else:
                    hit = visible(rel, decl_map.get(("godot", b), ()))
                    if hit:
                        add(rel, hit[0], "extends")
        elif lang == "godot-resource":
            for p in rec.get("paths", ()):
                add(rel, _res_to_rel(p), "scene")
        elif lang == "python":
            for m in rec.get("imports", ()):
                add(rel, resolve_py(rel, m), "import")
            named = rec.get("named", {})
            for b in rec.get("bases", ()):
                head, _, tail = b.partition(".")
                src_mod = named.get(head)
                if src_mod is None:
                    continue
                mod, _, nm = src_mod.partition(":")
                t = None
                if nm:  # `from m import Base` — Base is m's, or the submodule m.Base
                    t = resolve_py(rel, mod) or resolve_py(rel, f"{mod}.{nm}")
                else:   # `import m as x` then `x.Base`
                    t = resolve_py(rel, f"{mod}.{tail}") if tail else None
                    t = t or resolve_py(rel, mod)
                add(rel, t, "extends")
        elif lang in ("javascript", "typescript", "tsx"):
            for s in rec.get("imports", ()):
                add(rel, resolve_es(rel, s), "import")
            named = rec.get("named", {})
            for b in rec.get("bases", ()):
                if b in named:
                    add(rel, resolve_es(rel, named[b]), "extends")
        elif lang in ("c", "cpp"):
            for inc in rec.get("includes", ()):
                add(rel, resolve_include(rel, inc), "include")
            for b in rec.get("bases", ()):
                for t in by_name(rel, rec, b):
                    add(rel, t, "extends")
        elif lang == "dart":
            imported = set()
            for u in rec.get("uris", ()):
                t = resolve_dart(rel, u)
                if t in present:
                    imported.add(t)
                    add(rel, t, "import")
            for b in rec.get("bases", ()):
                cands = [c for c in decl_map.get(("dart", b), ())
                         if c in imported or Path(c).parent == Path(rel).parent]
                for t in cands[:1]:
                    add(rel, t, "extends")
        elif lang == "go":
            here = Path(rel).parent.as_posix()
            imports = rec.get("imports", {})
            for q in rec.get("qual", ()):
                alias, _, nm = q.partition(".")
                p = imports.get(alias)
                add(rel, go_file(rel, go_dir(p) if p else None, nm), "import")
            for n in rec.get("names", ()):
                add(rel, go_file(rel, here, n), "class")
            for b in rec.get("bases", ()):
                alias, _, nm = b.rpartition(".")
                if alias:
                    p = imports.get(alias)
                    add(rel, go_file(rel, go_dir(p) if p else None, nm), "extends")
                else:
                    add(rel, go_file(rel, here, b), "extends")
        elif lang == "perl":
            for u in rec.get("uses", ()):
                for t in resolve_perl(rel, rec, u):
                    add(rel, t, "import")
            for b in rec.get("bases", ()):
                for t in resolve_perl(rel, rec, b):
                    add(rel, t, "extends")
        else:  # the TypeNames languages
            bases = set(rec.get("bases", ())) | set(rec.get("bases_extra", ()))
            for n in rec.get("names", ()):
                if n in bases:
                    continue
                for t in by_name(rel, rec, n):
                    add(rel, t, "class")
            for b in bases:
                for t in by_name(rel, rec, b):
                    add(rel, t, "extends")
            for m in rec.get("mods", ()):  # Rust `mod x;`
                d = Path(rel).parent
                if Path(rel).stem not in ("mod", "lib", "main"):
                    d = d / Path(rel).stem
                for c in (d / f"{m}.rs", d / m / "mod.rs"):
                    if c.as_posix() in present:
                        add(rel, c.as_posix(), "mod")
                        break
    # --- constructions: `new` edges, resolved like the names of each language
    for rel, rec in new.items():
        if rec.get("error") or not rec.get("news"):
            continue
        lang = rec.get("lang")
        for nm in rec["news"]:
            if nm in rec.get("decls", ()):
                continue  # a file constructing a class it declares itself
            if lang == "gdscript":
                hit = visible(rel, decl_map.get(("godot", nm), ()))
                add(rel, hit[0] if hit else None, "new")
            elif lang == "python":
                src_mod = rec.get("named", {}).get(nm)
                if src_mod:
                    mod, _, sub = src_mod.partition(":")
                    add(rel, resolve_py(rel, mod) or (resolve_py(rel, f"{mod}.{sub}") if sub
                                                      else None), "new")
            elif lang in ("javascript", "typescript", "tsx"):
                spec = rec.get("named", {}).get(nm)
                add(rel, resolve_es(rel, spec) if spec else None, "new")
            elif lang == "go":
                add(rel, go_file(rel, Path(rel).parent.as_posix(), nm), "new")
                for alias, path in rec.get("imports", {}).items():
                    if f"{alias}.{nm}" in rec.get("qual", ()):
                        add(rel, go_file(rel, go_dir(path), nm), "new")
            else:
                for t in by_name(rel, rec, nm):
                    add(rel, t, "new")
    return edges, index.ambiguous
