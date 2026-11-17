---
description: "BBC — plan the end-to-end tests of the map's flows: every flow that crosses the black boxes, through the real transport and the real storage, at the level the project has (the API, the user interface). A TDDAB plan, reviewed and ready for /dev:j-cvm-exec-plan. Use when the user says bbc e2e, test dei flussi, or /dev:bbc-integrate pointed here."
---

## Prerequisites
- `${CLAUDE_PLUGIN_ROOT}/commands/bbc-plan.md`, read in full — this command follows its steps by number — and,
  through it, `j-new-feature.md`.
- As `/dev:bbc-plan`: the Memory Bank, `j-settings.md`, `junior.md`, `development-workflow.md`, `bbc.md`;
  the map with its flows.
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/testing-principles.md`.
- The BBs' own tests green (their commands in their definitions): a flow is tested on BBs that work
  alone. Red → `/dev:bbc-debug` first.
- **The main folder**, not a worktree: a flow crosses BBs developed apart, so it is tested where they
  are all merged and wired in the composition root — the base (`bbc.md` §3.5).

## Steps

### 1. The task
`/dev:bbc-plan` steps 1-4, the name `/dev:bbc-e2e`, the line `Flow: bbc-e2e`; `## BB scope` lists the flows and
the BBs they cross.

### 2. The level — ANALYZE
**Update MB:** `@state::ANALYZE`, `@feature::NN-<name>`, `@branch::feature/NN-<name>` — this command
has no LISTEN, where `/dev:j-new-feature` writes the last two. The level of the end-to-end tests is the outermost the project has
(`testing-principles.md` 3.3): through the user interface where `@test-e2e` runs one; through the
API's real transport otherwise; through the entry point of a project with neither. Under
`## Analysis`, one row per flow of `BBC-MAP.md`:

```
| Flow | BBs crossed | Normal path | Error paths | Tested by |
|---|---|---|---|---|
| Open edit | BB4 → BB2 → BB1, BB3 | yes | snapshot missing; chat refused | none |
```

### 3. INVENTORY, PROPOSE
`/dev:bbc-plan` steps 7-8: the host, the fixtures, the seed and the test data the end-to-end tests already
share; where the new ones go.

### 4. PLAN — TDDAB
`/dev:bbc-plan` step 9, tests on code that exists, as `bbc.md` §4 says. One block per flow: its normal path and its error paths, each test asserting the
state of every BB the flow crosses and what the user or the caller receives — not only the return
value. The storage and the transport are real; doubles only for a system outside the project.
`@test-e2e` runs them; without one, `@test-slow`, the level of the API.

### 5. Commit, STOP
`/dev:bbc-plan` steps 10-11.

## Rules
- **The flows of the map**: each one tested on its normal path and its error paths.
- **No double of a BB of the project** at this level.
- **The BBs work alone first.**
