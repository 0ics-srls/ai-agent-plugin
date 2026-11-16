---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC — plan the Core of the contracts, the first step of the roadmap; on a project with no code yet it is the project's start — the profile, the skeleton, then the Core. Every contract of the map written in the project's Core — the abstract concepts of the whole system, each BB's interfaces and the types they exchange under the BB's namespace — with its fake and its contract tests, so that every BB can then be developed in parallel against it. A TDDAB plan, reviewed, then it STOPS and the user triggers /dev:j-cvm-exec-plan. Use when the roadmap's first step is due, or the user says bbc core, scrivi il core, le interfacce dei BB."
---

## Prerequisites
- `${CLAUDE_PLUGIN_ROOT}/commands/bbc-plan.md`, read in full — this command follows its steps by number — and,
  through it, `j-new-feature.md`.
- As `/dev:bbc-plan`: the Memory Bank, `j-settings.md`, `junior.md`, `development-workflow.md`, `bbc.md`,
  `testing-principles.md`; the map, with its roadmap (missing → `/dev:bbc-review` first).
- The project's Core: what the skeleton's first block made (`overlays/<language>/tddab.md` §6). A
  project with no code yet is started here — step 1b gives it its profile, and this plan's first blocks
  are its skeleton. A new part of a project that has no Core gets its own, as
  `overlays/<language>/tddab.md` §6 says, written by this plan's first block.
- **The main folder**, not a worktree: the Core is what the worktrees are opened on (`bbc.md` §3.5).

## Purpose
The Core holds the abstract concepts of the whole system (`bbc.md` §1.6): the contract of every BB —
its interfaces, the types they exchange, its errors, its events — under the BB's namespace, and nothing
that implements them. Whoever uses a BB references the Core; dependency injection gives the
implementation, which lives in the BB's namespace. With the Core on the base, every BB is developed at
the same time as the others, against the Core alone.

On a project with no code yet this command is the project's start (`bbc.md`, the steps of the method):
the profile (step 1b), the skeleton, then the Core, in one plan. The map's `## Decisions` are taken as
they are; nothing the map decided is decided again.

Beside it, in the support the tests share (`testing-principles.md` 4.2, 5.1), each contract has its
fake — the double the other BBs' tests use, with behaviour — and its **contract tests**: what every
implementation of the contract must do, case by case, written once and run against any implementation.
Here they run against the fake; the BB's `/dev:bbc-plan` runs them against the real one, so the fake and
the BB cannot drift apart. **It writes no code: `/dev:j-cvm-exec-plan` executes the plan.**

## Steps

### 1. The task
`/dev:bbc-plan` steps 1-4, the name `core`, the line `Flow: /dev:bbc-core`. `## BB scope`:
`- BB: Core — the contracts of every BB of the map`, its files the project's Core and the tests'
shared support.

### 1b. A project with no code yet — the profile
No build file in the repository (the ones `j-setup.md` step 2 looks for) → the project starts here.
A project that has code → step 2.
1. From `BBC-MAP.md` `## Decisions`: the style of the architecture, the layers and the mechanisms. They
   are not asked again.
2. Ask with AskUserQuestion only what the map does not say and the code needs: the language of each
   component (the folders of `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/overlays/`); for each language, the questions
   its `language.md` §7 lists under «What LISTEN asks»; the storage; the base library and how it comes
   in — a git submodule or a package.
3. A base library that is a git submodule is added now, as `j-new-project.md` step 5 says it.
4. Run `/dev:j-setup` with that profile (its PROFILE GIVEN mode, `j-setup.md` step 18): it completes
   `j-settings.md` and copies the lint pack. What it wrote is committed with the plan, in step 5.

### 2. LISTEN
**Update MB** as `/dev:j-new-feature` step 5 says: `@state::LISTEN`, `@feature::NN-core`,
`@branch::feature/NN-core`. `## Requirements` is written from the map and shown: for each BB its
contract — every member with its inputs, its results, its errors — its events, the types it exchanges,
and the cases each member promises (`testing-principles.md` 2.2). Then it asks what to add, and the
user's words are added. No code is read and nothing is proposed.

### 3. ANALYZE, INVENTORY, PROPOSE
`/dev:bbc-plan` steps 6-8. ANALYZE reads the Core the project has. PROPOSE names, for each contract of the
map, its place in the Core — the BB's namespace. An external system's contract, described by the user
on the map (`bbc.md` §2), is not the Core's: the BB that uses it depends on it through its own contract.

### 4. PLAN — TDDAB
`/dev:bbc-plan` step 9, the scope being the Core and the tests' shared support.

On a project with no code yet (step 1b), the plan's first blocks are the skeleton's, as
`overlays/<language>/tddab.md` §6 gives them — each layer's project with its test project, the shared
test support, the composition root, the operations block — without a first entity: the BBs are what is
built on it.

Then the blocks of the Core, one per BB, in the order of the dependency graph, leaves first:
- RED: its contract tests, as a suite any implementation can be run against, here run against its
  fake — every case of `## Requirements`;
- GREEN: in the Core, under the BB's namespace, its interfaces, the types they exchange, its errors and
  its events; in the shared support, its fake, with behaviour;
- the Core references no implementation, as the overlay's rule of Core says.

The last block writes in each `bb/BB<N>-<name>.md` the file of its contract in the Core, its fake and
its contract tests with the command that runs them; and in `BBC-MAP.md` a contract that changed in
PROPOSE.

### 5. Commit, STOP
`/dev:bbc-plan` steps 10-11. Next: `/dev:j-cvm-exec-plan`, then `/dev:j-close`; then the BBs — `/dev:bbc-work` for
each BB, each in its own worktree, or `/dev:bbc-plan` one at a time.

## Rules
- **The Core holds contracts only**: no implementation, no helper — a capability shared by several BBs
  has a BB that owns it.
- **One namespace per BB**, in the Core as in its implementation.
- **Every contract has its fake and its contract tests**, and the fake passes them.
- **The Core is on the base before any BB is delegated.**
