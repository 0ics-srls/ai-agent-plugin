# Principles

What a good software system has, whatever it is and whatever language it is written in. Each
principle states a **goal**; the shape that reaches it comes from the platform.

---

## 1. How the principles are applied

1.1 **The goal is ours, the mechanism is the platform's.** Each goal is reached with what the
platform already provides — the framework, the ORM, the dependency-injection container, the built-in
validation, the standard error format. Code is written by hand only for what the platform does not
provide, and "it does not provide it" holds only by citing where it was looked for.

## 2. Before writing: search

2.1 **A capability is implemented once.** A capability is what the code DOES — validate an account,
retry with backoff, convert a currency — not the name it was given. A different name is not a
different capability. If it exists, use it or extend it. A second implementation is a defect, and the
worst one is the copy written while removing duplicates.

2.2 **Search by what it does, not by what it is called**, at every granularity: a function, a class, a
module, a package. "It does not exist" is a claim, and it holds only by citing the search and its
result.

2.3 **Search in this order:** the project's own code; the base library it builds on; the libraries it
already depends on; the platform, its documentation and its official templates; the package
registries; proven projects; and the web last. A proven approach that covers 80% of the need beats new
code.

## 3. Structure: decided before the code

3.1 **The structure is decided before writing**: what is shared, who owns it, the contract the
consumers see, and the mechanism that governs the behaviour. Before the code, changing it costs one
sentence; after, nobody repairs it.

3.2 **The base is generic; a feature adds only what is its own.** What every feature repeats is
written once, generically, in the part that owns it, behind a contract. A new feature then costs one
declaration where the base needs it, and the only new code is its own rules. The contracts of the base
are ours; their implementation delegates to the platform's own mechanism (1.1). A skeleton is this
base — what can be built on it is what it is judged by, not what it does on its first day.

3.3 **Every part is reached through a contract, and dependencies point one way.** A consumer depends
on an interface, never on an implementation, and no dependency points back up. What crosses a
boundary is an interface (behaviour) or data. Behaviour lives in services behind interfaces; data
carries no logic.

3.4 **Black boxes.** The system is split into self-contained parts: a clear boundary, hidden
internals, isolated dependencies. One part cannot break another. A boundary, once others depend on it,
changes only on purpose.

3.5 **Organize by domain, not by type.** A shared library is welcome when it has one responsibility, a
name that says it (`money`, `auth/tokens`), an owner and a contract. The dumping ground is not:
`utils/`, `helpers/`, `common/`, `misc/`.

3.6 **Dependencies are injected, and the composition is readable.** Each module owns the registration
of its own parts, and the composition root reads in ten seconds: from it you can see what exists and
who provides it.

## 4. Errors and input

4.1 **Errors belong to the domain and are translated at the boundary.** The domain reports its
failures with codes — "invalid", "conflict"; the boundary maps them to its own terms once, in one
place, and a code without a mapping turns a test red. A lookup that finds nothing is a result, not a
failure: the caller receives the absence.

4.2 **No error is swallowed silently.** The user gets a clear, actionable message; the error is
recorded once, where it is handled.

4.3 **Input is validated at the boundary, once.** Every rule about incoming data — required, length,
format, range — is stated in one place and checked where the data enters; failures name each field.
Code past the boundary trusts the data it receives and does not re-check it.

## 5. Configuration

5.1 **Configuration is centralized and validated at startup.** No hidden defaults in code: if a
required value is missing, the program does not start and says which one.

5.2 **Secrets live in `.00-secrets/`, encrypted in git with git-crypt**: plaintext in the working tree,
encrypted in the repository. Every secret of the project is there; outside it are only the files of a
single developer, the git-crypt key, which lives in a password manager, and the API keys the project
owner chose to keep in the MCP configuration (`.mcp.json`, `opencode.jsonc` or `opencode.json`). Configuration and code
read a secret from there and never carry its value, those MCP keys aside. The git-crypt key never passes through
an agent: what a command shows it reaches the model and stays in the transcript.

## 6. Build and dependencies

6.1 **Zero warnings.** A warning is an error: the build is green (0 warnings, 0 errors) or red. Every
warning is fixed in the code that raises it; a rule is relaxed only by the project owner's decision,
one rule at a time, with its reason written beside it.

6.2 **Dependency versions are defined in one place**, and every module uses the same version of every
dependency.

6.3 **Build output goes to a fixed, predictable location**, and a clean build is reproducible on any
machine with the required toolchain — the toolchain version is a minimum, not an exact pin.

6.4 **Free dependencies only** (MIT, Apache 2.0, BSD, MPL, PSF-2.0, BSL-1.0) — not even a free version of a package that
has gone commercial. The exceptions are the licensed UI libraries: DevExtreme, and the Prime family
(PrimeNG, PrimeReact, PrimeVue) under the PrimeUI license.

6.5 **Dependencies stay on supported, patched versions**, and the build audits them.

## 7. How code is judged

7.1 **By reading it, and with the project's deterministic tools**: compiler, type checker, linters,
analyzers, tests. Their exit code outweighs the reader's impression.

7.2 **No improvised checks.** A grep or a regex over the source, presented as a finding, redoes worse
the work of tools that have type information, and it arrives when the structure is already decided.

7.3 **No number measures quality.** Lines, parameters, nesting depth and files touched do not say
whether an algorithm is good, whether responsibilities are in the right place, or whether the next
change will be cheap. Those are the questions.
