---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC (Black Box Codebase) — the method of designing a project, or a new part of one, too large for one context window as black boxes, on abstractions, before its code: the map, the work on one box at a time through the others' contracts, the change of a contract, the order of the tests, the diagnosis from the leaves. The principles it stands on are principles.md 3.3, 3.4, 3.6 and code-principles.md 1.4, 1.7, 1.8; this file adds only the method. Read by the bbc-* commands."
---

# BBC — Black Box Codebase

The principles are already written: every part is reached through a contract and dependencies point
one way (`principles.md` 3.3); the system is split into black boxes with a clear boundary, hidden
internals and isolated dependencies, and a boundary others depend on changes only on purpose (3.4);
dependencies are injected (3.6); a part has one reason to change (`code-principles.md` 1.4); its
contract is shaped by its clients (1.7) and the code that decides depends on contracts (1.8).

BBC is the **method** that applies them to a new project, or a new part of an existing one, too large
to be held in one context window, before its code is written: it names the black boxes, draws them on a
map, and works on one at a time. It designs first because an agent that starts from code derives
concrete views from it — the calls, the files, the runtime — not abstractions: the abstractions are
designed first, with the user, and the code follows them.

The steps of the method, each with the command that takes it. Before them, `j-setup` writes
`j-settings.md`, the settings every command reads: a project designed as black boxes starts with
`j-setup`, then these steps in order.
1. **The analysis**: the BBs by responsibility, their contracts, their dependencies, the flows and the
   decisions of the architecture, from the requirements, with the user; no code is read —
   `bbc-analyze`.
2. **The review of the analysis**, against the requirements and the method; no code is read. Its
   findings go back to step 1, until the user approves the map; then the roadmap — `bbc-review`.
3. **The Core**: every contract of the map written in the Core (§1.6) — the interfaces, the
   abstractions, the types they exchange — each with its fake and its contract tests — `bbc-core`. On a
   project with no code yet, `bbc-core` is the project's start: it takes the map's decisions, asks the
   language and what the code needs, and plans the skeleton and then the Core. `j-new-project` is for a
   project that is not designed as black boxes.
4. **Every BB developed alone**: it depends only on the other BBs' contracts, so with the Core in place
   every BB can be built at the same time as the others, in parallel when the user wants — `bbc-plan`,
   one at a time, or `bbc-work`, one worktree per BB.
5. **Composed**: real BB with real BB, in the order of the dependency graph — `bbc-integrate`.
6. **The flows**, end to end through the real transport and storage — `bbc-e2e`.
7. **The code checked against the analysis**: a report, and a feature that fixes what it found —
   `bbc-audit`.
8. **A change of the map, then of the code**: a BB's responsibility, its contract, a split or a merge, a
   decision — changed in the map with the user, and the code brought to it — `bbc-refactor`.
9. **A failure isolated** BB by BB, leaves first — `bbc-debug`.

---

## 1. What a black box is

1. **A responsibility, cut vertically.** A black box (BB) is the set of files that carry one
   responsibility — "snapshot management", "edit session" — across the layers it needs (Core, Db,
   Domain, Api, or the layers the overlay names). Layers are horizontal; a BB cuts through them. A BB
   is not a layer, and a description with an "and" is two BBs.
2. **It fits in one context window.** Its files can be loaded and worked on in one sitting. That is
   an operational limit, not a quality score: a BB is split when it has a second responsibility or no
   longer loads, along its responsibilities — the file count is neither the reason nor the cut.
3. **It has a contract and declared dependencies.** The contract is what it exposes (its interfaces,
   its endpoints, its events); the dependencies are the other BBs it uses, through their contracts.
   The dependencies form a graph with no cycle.
4. **A wrapper is a BB too** — `BB-W<N>`: a protocol adapter (HTTP, gRPC, CLI, MCP, a hub) that only
   delegates to the BB it wraps and translates the protocol. It decides nothing; if it decides
   anything, it is a full BB.
5. **A namespace.** A BB is a namespace named after its responsibility — its folder in each layer it
   cuts. Its implementation lives there; its contract lives in the Core.
6. **The Core** holds the abstract concepts of the whole system: the contract of every BB — its
   interfaces, the types they exchange, its errors, its events — each under its BB's namespace, and
   nothing that implements them. Whoever uses a BB references the Core, never the BB; dependency
   injection gives the implementation. The Core is the project's own (the skeleton's first block,
   `overlays/<language>/tddab.md` §6); `bbc-core` writes the map's contracts in it, each with its fake
   and its contract tests.

## 2. The map

The map lives in `{@tasks}/bbc/` and is committed with the code:

| File | Holds |
|---|---|
| `BBC-MAP.md` | `## Requirements` — what the project, or the new part, must do, as the user said it, written by `bbc-analyze` and read by `bbc-review`; the project in one page; the BB index (id, name, responsibility, status); the dependency graph (Mermaid); the layer-to-BB matrix; the flows (sequence diagrams of the 2-3 scenarios that cross most BBs); the integration points (caller, callee, contract, the test that proves it); the change history |
| `bb/BB<N>-<name>.md` | one BB: its responsibility, and what it is NOT responsible for; its files; its contract, written out; its dependencies; its tests and the command that runs them |
| `diagrams/*.mmd` | the dependency graph and the flows, as Mermaid sources |
| `BBC-REVIEW-YYYY-MM-DD.md` | the review of the analysis: each finding, and the answer written beside it |
| `BBC-AUDIT-YYYY-MM-DD.md` | the code against the analysis: each finding, BB by BB |

**The decisions**, `## Decisions` in `BBC-MAP.md`: the style of the architecture (layers, hexagonal…)
and the mechanisms chosen (`code-principles.md` §2), each with its reason and the BBs it governs,
approved by the user. Every `bbc-*` command reads them, and none re-decides them: a decision changes
only as a contract does (§3.3) — named first, with the BBs it governs, and decided by the user.

Diagram colours: a leaf `fill:#90EE90,color:#000`, a hub `fill:#FFD700,color:#000`, a wrapper
`fill:#E8E8E8,stroke-dasharray:3 3,color:#000`, an external system `fill:#ADD8E6,color:#000`, a BB to
build `fill:#FFFFFF,stroke-dasharray:5 5,color:#000`; `-->` depends on, `-.->` wraps.

**The status of a BB**, in the index: `built` — its code exists — or `to build` — its contract is
designed with the user and it has no files yet. A BB to build becomes `built` when the plan that
develops it writes its files in its definition.

**The roadmap**, `## Roadmap` in `BBC-MAP.md`: its steps in order — the Core of the contracts, the BBs,
the integrations, the flows, and last the audit of the code against the map — each with the BBs (or the
flows) it covers, each of them with its own status. `bbc-review` proposes it and the user approves it.
Who marks a step done: `j-close` marks the Core, a BB, an integration, a flow, by the `Flow:` line of
the work it closes — a step whose BBs go in parallel closes BB by BB, and is done when all of its are;
`bbc-audit` marks the audit step, when its report has no finding.

The map is written from the requirements and the user's approvals, never from code. A BB's files are
written in its definition by the plan that builds it. The existing code a new part uses is an external
system on the map, its contract described by the user as it is today. The map is drawn in passes — the
BBs that can already be seen, then the rest — and shown as a diagram before the details are written.

## 3. Working on one BB

1. **The scope is the BB.** The work reads and changes the BB's files. Of every other BB it uses the
   contract the map states — the map's, not what its implementation does: what an implementation
   happens to do today is not what it promised, and a dependency written on it breaks at its next
   change.
2. **The search is not scoped.** Looking for what already does a capability is still done across the
   whole project, by what it does (`principles.md` 2.1-2.3): a capability found in another BB is used
   through that BB's contract, or moved to the BB that owns it — never copied into this one.
3. **A contract changes only on purpose** (`principles.md` 3.4). A change of a BB's contract — a
   signature, a result, an error, a removed member — is named before it is made, with the BBs that use
   it, and decided by the user. After it, those BBs are integrated again (`/bbc-integrate`).
4. **The definition follows the code.** A change of a BB's files, contract or tests is written in its
   `bb/BB<N>-<name>.md` and, when the contract or the dependencies change, in `BBC-MAP.md`.
5. **In parallel.** Each BB worked on at the same time as others has its own git worktree, its own
   branch and its own agent session, opened in that folder: the MCP servers keep their state in the
   folder of the session (the plan of the CVM, the index of the navigation tool), so two works in one
   session would overwrite each other's. A work may stay open there for days. The base branch is
   brought into a worktree when the user decides. A contract an open work uses changes only as point 3
   says, named together with that work. What composes the BBs is not delegated: the integration and
   the flows (`bbc-integrate`, `bbc-e2e`) run in the main folder, once the BBs they compose are merged
   into the base.

## 4. The tests, in three steps

1. **The BB alone.** Its logic, with doubles of the other BBs' contracts — the fakes of the Core — and
   of the outside (`testing-principles.md` 4.1-4.2); its data access against the real storage (3.2);
   its contract tests, written with the Core, run against it. A green BB proves its own logic and
   that it keeps its contract as its fake does.
2. **The BBs together.** Two or more real BBs wired as the composition root wires them; doubles only
   at the boundary of the system. The composition root is shared by every BB, so the development of
   a BB does not touch it: `bbc-integrate` registers there the BBs it composes. A test here asserts what the integration produces — the state, the
   answer, the error that crosses the boundary — not that a call was made.
3. **The flows.** The scenarios of the map, end to end through the real transport and the real
   storage (`testing-principles.md` 3.3), at the level the project has: the API, the user interface.

Each step has its tests run by the project's commands (`j-settings.md` `## Tests — by level`).

Tests planned on code that exists prove it: a test that passes when it is first run is the expected outcome, and no
production code is written to make it pass. A plan that builds a BB, or the part of it that is missing, writes that
code at its GREEN. A test of code that exists that fails is a finding, and its cause is found with Protocol D. The
block's intro says so, because the RED phase of the planexecutor speaks of failing tests.

## 5. Finding what is broken

Protocol D (`debug-protocol.md`) is the method; BBC gives its ISOLATE an order:

1. The BBs the failure crosses, read from the map's flows.
2. Their tests, **leaves first**, in the order of the dependency graph: a leaf that fails is the
   cause; a hub tested before its leaves can fail because of them.
3. Every BB green and the failure still there → the cause is at an integration point: the call
   between two BBs (the arguments, the awaiting, the error not handled, the order of the calls), read
   on both sides of the contract.
4. A wrapper failing over a green BB → the cause is in the protocol (serialization, authentication,
   routing), not in the logic.

## 6. When BBC is used

For a new project, or a new part of an existing one, with several layers and more code than one
context window will hold, designed before its code. Not for code that exists — an agent cannot recover
its abstractions from it; not for a prototype, a project with a single boundary, or one without
automated tests — there the phases of `development-workflow.md` alone are enough.
