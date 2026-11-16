---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Start a project with the junior workflow (junior workflow). A project to create goes through the phases of development-workflow.md up to PLAN — what the project is, the mindsets that apply, what already exists, the structure — has j-setup record the profile and wire the lint gate, writes the TDDAB plan of the skeleton and the Memory Bank, then STOPS; the user triggers j-cvm-exec-plan. A project that already has code is wired, described and given its Memory Bank, without a plan. Use when starting a brand new project from scratch, or bringing an existing one into the workflow — nuovo progetto, novy projekt.
---

## Prerequisites
- If not read this session: read `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
  `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md` — the phases this command goes through, with
  what each one leaves in `notes.md`.
- Read the Memory Bank (skip the subdirectories) if not already done.
- `j-settings.md` at the repository root: the base settings `j-setup` writes for a project to create,
  the full settings for an existing one. Missing → run `/j-setup` first, then come back.

## Purpose
The project is born in the root of the current repository — the one already wired to ai-agent
(`.ai-agent` submodule, `.claude/`). This command decides what the skeleton is, and writes the plan
that builds it with every foundation in place from day one. **It writes no project code:
`j-cvm-exec-plan` executes the plan.** The task's file is `{@tasks}/01-scaffold/notes.md`, on the
branch `feature/01-scaffold`, which `j-close` merges like any feature.

**A project designed as black boxes** — `{@tasks}/bbc/BBC-MAP.md` exists — is not started here:
`/bbc-core` starts it, from the map's decisions (`bbc.md`, the steps of the method). STOP and say so.

**A repository that already has a project's code** — the build files `j-setup` step 2 looks for — is
not scaffolded: it goes to **EXISTING PROJECT** below. Everything else follows the steps here.

## Steps

### 0. Branch and folder
`{@tasks}/bbc/BBC-MAP.md` exists → STOP: the project is designed as black boxes, and `/bbc-core` starts
it.

The base branch follows `@merge-strategy` (`gitflow` or `gitflow-simple` → `{@dev-branch}`; otherwise
`{@main-branch}`):
```bash
git checkout {base-branch}
git checkout -b feature/01-scaffold
mkdir -p {@tasks}/01-scaffold
git push -u origin feature/01-scaffold
```

### 1. LISTEN — what the project is
**Update MB:** `@state::LISTEN`, `@feature::01-scaffold`, `@branch::feature/01-scaffold`

Ask with AskUserQuestion, and wait for every answer:
1. **Name** and **one sentence** of what it does.
2. **Kind**: Web API (backend), full stack (frontend + backend), worker / background service,
   library / package, console / CLI, game, desktop or mobile application.
3. **Language** of each component: the languages that have an overlay (`ls
   ${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/overlays/`), or another one, named by the user — then the project has no
   overlay yet, and the proposal says so. For each language with an overlay, the questions its
   `language.md` §7 lists under **What LISTEN asks** (the framework, the UI library…).
4. **Storage**: a database? which one.
5. **Calls outside the process**: other services, queues, external APIs?
6. **Exposure**: is it reached by callers you do not control (internet, other organizations)?
7. **Base projects to bring in**: is there a library the project builds on — the base of entities,
   repositories, unit of work, generic endpoints? Its repository and how it comes in (git submodule
   path, or package). When `@base-library` is already in `j-settings.md`, confirm it instead of asking.

Write the answers under `## Requirements`.

### 2. ANALYZE — the mindsets of this project
**Update MB:** `@state::ANALYZE`

1. Read `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/README.md` and, from it, every file that applies: the three of
   every project, the branches its table assigns to what the answers describe, and the language's
   overlay files that go with them. A language with no overlay folder: the plan is written from the
   principles and the branches, and the proposal says that no overlay exists for it yet.
2. **The base library**, when there is one: read its README and its sample application, and write
   which parts of the base it provides (contracts, implementation, endpoints, errors, serialization)
   and how a project builds on it. What it provides is used, not rewritten (principles 2.1, 3.2).
3. **TDDAB**: `mind-sets/tddab-planner.md` in full and `mind-sets/overlays/<language>/tddab.md` when it
   exists — the bottom-up decomposition the organization of step 4 is written for.
4. Write `## Analysis`: the branches, the overlay files, the base library's part.

### 3. INVENTORY — what already exists for this project
**Update MB:** `@state::INVENTORY`

For each part of the skeleton — the solution layout, the base contracts, the data access, the list
queries, the errors, the logging, the tests — find what already does it, in the order of
`principles.md` 2.3. Write `## Inventory — capabilities and where they already live`, one line per
part: what covers it (name, version, link) or the search that came back empty, and the decision —
reuse, extend, write.

### 4. PROPOSE — the structure, approved before anything is written
**Update MB:** `@state::PROPOSE`

Show the inventory, and write under `## Code Organization`:
- **the projects / modules and their references** — for a service, the four layers of
  `branches/service-layers.md` with the names the overlay gives them;
- **the base**: the contracts every entity shares and who provides them — the base library (which
  package) or the project itself (which layer);
- **the first entity** that proves the base end to end, and its own rules;
- **the mechanisms** the behaviour needs, if any (code principles §2);
- **the rules in force**: the branches and overlay files, and the lint gate the overlay defines;
- **the commands**: build, the test levels, migrations.

Ask: **is this organization right?** Wait for the answer; change and show again until it is.

### 5. SETTINGS — j-setup records the profile and wires the lint gate
**The base library**, when the project uses one as a git submodule, comes in now, before the plan:
`git submodule add <its repository> externals/<name>`. Its code is then in the repository: the plan's
blocks use its types, and `/j-review-plan` finds them there. A base library that is a package is
added by block 1, which creates the project it goes in; the review checks its types with
`@code-nav-external`.

Run `/j-setup` with the profile decided in steps 1-4 (its PROFILE GIVEN mode): the project's name,
language, kind, the mindsets branches and overlay files, the base library, the exposure. j-setup
completes `j-settings.md` and copies the lint pack into the repository root — with the pack's
`externals/` files when the base library is a submodule — so the first block of the plan already builds
under the gate. A frontend's pack comes with its block F1, after the scaffold (its overlay's `language.md` §7). A language whose pack is not in `${CLAUDE_PLUGIN_ROOT}/lint-rules/manifest.yaml` has none yet: the
proposal says so, as for a missing overlay.

### 6. PLAN — the TDDAB plan of the skeleton
**Update MB:** `@state::PLAN`

**TDDAB — hard gate, read even if you think you know it**: `mind-sets/tddab-planner.md` in full and
`mind-sets/overlays/<language>/tddab.md` when it exists, again — TDDAB v2 is not generic TDD (bottom-up
decomposition, RED = the contract, reference code intentionally non-compilable, no fixed test-count
limits). Under `## TDDAB Rules Applied` in `notes.md`, write the 3-5 rules you will apply, in your own
words; if you cannot, read it again.

Write `{@tasks}/01-scaffold/plan.md` in the format of `tddab-planner.md`, and its path in the Memory
Bank: `@plan::{@tasks}/01-scaffold/plan.md`. The mission carries the
`## Design principles`, `## Code rules` and `## Commands` the planner asks for.

The blocks follow the organization approved in step 4, bottom-up — what a block uses exists in an
earlier block. For a service, the usual order:

| Block | What it builds |
|---|---|
| 1 | the solution, its build and Core: the base contracts the project writes itself and the first entity's contracts |
| 2 | Db: the base implementation written once, the context, the first entity and its mapping, the first migration |
| 3 | Domain: the first entity's service on the base contracts |
| 4 | Api: composition, validation, error mapping, serialization as is, the endpoints every entity gets and the first entity's own |
| 5 | operations: version, health, logging, configuration validated at startup, secrets from `.00-secrets/` when the project has it |

Each block's form in the project's language — the commands, the packages, the test project it
creates, the overlay section it applies — is `overlays/<language>/tddab.md` §6, "The skeleton's
blocks"; every block names that section, so the executor builds it with the language's own mechanisms.

Whether the project has `.00-secrets/` is read before the plan (`.git/git-crypt`). Without it, because the user
declined `/j-init-secrets`, no block creates that folder and none writes a secret's value anywhere: a secret the
skeleton needs is asked with AskUserQuestion — `/j-init-secrets` now, or the part that needs it left out — and a
skeleton with no secret reads no such source.

With the security branch, a block between 4 and 5 sets the authentication and the authorization
policy. What the base library provides is not a block: as a submodule step 5 brought it in, as a package
block 1 adds it, and the blocks that use it name its types. Without a base library, blocks 1-4 write the base in the project, each part where
the overlay places it. A library, a CLI or a worker drops the blocks it has no part for.

A game follows the game branch (`branches/game.md`) instead of the service's blocks: its blocks, G1 to
G5 — the project and its composition root, the first mechanic's rules, the scene that presents them,
the interface, the save — are those of its overlay's `tddab.md` §6.

A full stack adds the frontend blocks after block 5; block 4 writes the API's contract document at the
repository root — the file the client is generated from. One set per application, in `frontend/` (in
`frontend/<app>/` when there are several), each block's form in the frontend's language in its
overlay's `tddab.md` §6:

| Block | What it builds |
|---|---|
| F1 | the application, its gate and its first test |
| F2 | the generated client |
| F3 | the typed load and the errors |
| F4 | the first entity's pages |
| F5 | end to end |

Every block carries its commands as `tddab-planner.md` ("The commands, by level") states them, from the
`## Tests — by level` keys j-setup wrote in step 5.

Then `/j-review-plan`, as the planner requires: the plan is shown only once the review approves it.

### 7. MEMORY BANK — the project's memory
Read `memory-bank/README.md` (the setup created the folder and linked it) and write, in MBEL, the
core files from what the phases established — nothing that no phase established:
- `productContext.md` — why the project exists: the vision, the problems it solves, its users, the
  success criteria (LISTEN);
- `systemPatterns.md` — how it is built: the components and their layers, the shared parts and who
  owns them, the mechanisms, the data flows (PROPOSE's `## Code Organization`);
- `techContext.md` — what it is built with: the stack and its versions, the base library, the
  development setup, the commands (`j-settings.md`);
- `activeContext.md` — the current task: `@state`, `@feature`, `@branch`, `@plan`, the decisions taken;
- `progress.md` — the progress of that task;
- `history.md` — empty: it is written only, never read at the start.
A file that already exists is completed, not overwritten.

### 8. Commit the phase's product
```bash
git add j-settings.md .claude/settings.json <sgconfig.yml and .ast-grep/, when j-setup wrote them> <the lint files j-setup created> .gitmodules externals/ {@tasks}/01-scaffold/notes.md {@tasks}/01-scaffold/plan.md <any plan sub-files> memory-bank/
git commit -m "docs(01-scaffold): project settings, scaffolding plan (TDDAB, N blocks) and Memory Bank"
git push origin feature/01-scaffold
```
`.gitmodules` and `externals/` only when step 5 brought a base library in as a submodule.
Only these files; other pending changes stay as they are, and the report names them.

### 9. STOP
```
✅ Scaffolding plan created and reviewed: {@tasks}/01-scaffold/plan.md ({N} TDDAB blocks)

Next: /j-cvm-exec-plan {@tasks}/01-scaffold/plan.md, then /j-close to merge.
```
**Start no code. The user triggers `j-cvm-exec-plan`.**

---

## EXISTING PROJECT

The repository already holds the project. Nothing is scaffolded and no plan is written: the project is
wired, described as it is, and given its Memory Bank. The description says how the project is made; it
does not judge it.

### E1. LISTEN — what the project is for
**Update MB:** `@state::LISTEN`

Ask with AskUserQuestion, and wait for every answer: the project's **name** and **one sentence** of
what it does; **who uses it**; **what success is** for it; **what comes next** — the work the team
expects to do with it.

### E2. SETTINGS — the project wired
`j-settings.md` missing → run `/j-setup`: its EXISTING PROJECT mode scans the project, asks what it
cannot establish, writes the settings and wires the lint gate. `j-settings.md` with only the base
settings (header `# Base settings — j-new-project completes them`) → run `/j-setup`: its VALIDATE MODE
completes it as an EXISTING PROJECT (step 20). Full settings with a key missing → `/j-setup` VALIDATE
adds the missing keys, as its step 20 says.

### E3. ANALYZE — what exists, described
**Update MB:** `@state::ANALYZE`

With code navigation (`mind-sets/code-navigation.md`, the tools of `@code-nav-local` and
`@code-nav-external`), read the project and establish, each with the files it is read from:
- the components and their layers: the projects or packages, what each one holds, which depends on
  which;
- the base library, when there is one, and what it gives the project;
- the main entities and the mechanisms that govern them (a state machine, a pipeline, a strategy);
- the surface it exposes: the API, the user interface, the messages;
- the tests: the levels there are, where they live, how they run;
- configuration, logging, secrets, the build and the deploy;
- the conventions the code follows: naming, folder layout, error handling.

### E4. MEMORY BANK
As step 7, from E1 and E3: `productContext.md` from E1, `systemPatterns.md` and `techContext.md` from
E3 and `j-settings.md`; `activeContext.md` with `@state::IDLE` and no task; `progress.md` with no task;
`history.md` empty.

### E5. Commit
```bash
git add memory-bank/ j-settings.md .claude/settings.json <sgconfig.yml and .ast-grep/, when j-setup wrote them> <the lint files j-setup created>
git commit -m "docs: Memory Bank of the existing project"
```
Only these files; other pending changes stay as they are, and the report names them.

### E6. STOP
```
✅ Project wired and described: memory-bank/ (productContext, systemPatterns, techContext)

Next: /j-new-feature to build something, /j-bug to fix something.
```

## Rules
- **LISTEN → ANALYZE → INVENTORY → PROPOSE → SETTINGS → PLAN → MEMORY BANK → STOP**, in this order;
  an existing project: **LISTEN → SETTINGS → ANALYZE → MEMORY BANK → STOP**.
- **The project is born in the root of the current repository.**
- **The mindsets decide the code**: the plan is written against the files step 2 read, and names them.
- **A base library is used, not rewritten.**
- **j-setup owns `j-settings.md` and the lint wiring**; this command hands it the profile.
- **Ask with AskUserQuestion** whatever is not decided.
