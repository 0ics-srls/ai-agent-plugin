---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC — change a black box of the map — its responsibility, its contract, a split or a merge, a decision — and then the code that follows it: the phases of a feature up to a reviewed plan, the map changed and approved first. Use when the user says bbc refactor, cambia il BB, sposta la responsabilità, dividi o unisci i BB, or bbc-audit sent a finding of the map here."
---

## Prerequisites
- `${CLAUDE_PLUGIN_ROOT}/commands/bbc-plan.md`, read in full — this command follows its steps by number — and,
  through it, `j-new-feature.md`.
- As `/bbc-plan`: the Memory Bank, `j-settings.md`, `junior.md`, `development-workflow.md`, `bbc.md`;
  the map and the BBs the user names.

## Purpose
The map is the design the code follows (`bbc.md`). A change of design is made in the map first, with the
user — a BB's responsibility, its contract, a split or a merge, a decision of `## Decisions` — and then
the code is brought to it. It runs `/bbc-plan`'s phases. **It writes no code: `j-cvm-exec-plan`
executes the plan.**

## Steps

### 1. Clean state, base branch
`/bbc-plan` steps 1-2. In a worktree opened by `/bbc-work` they are skipped, as `/bbc-plan` says.

### 2. The task
`/bbc-plan` steps 3-4, the name `bb<N>-refactor-<what>`, the line `Flow: bbc-refactor`.

### 3. LISTEN
**Update MB** as `/j-new-feature` step 5 says: `@state::LISTEN`, `@feature::NN-<name>`,
`@branch::feature/NN-<name>`. `## Requirements` is the change, in the user's words, and the BBs it
touches — or the finding of `/bbc-audit` the user sent here.

### 4. ANALYZE
`/bbc-plan` step 6: the map's BBs the change touches and the BBs that use their contracts; their code as
`/bbc-plan` step 6 reads it.

### 5. The map changed — before INVENTORY
The new text of the BBs' definitions and of `BBC-MAP.md` — the graph, the contracts, `## Decisions` —
shown and approved with AskUserQuestion; each contract or decision changed is named with the BBs that use
it (`bbc.md` §3.3). Once approved, it is written in the map's files (`{@tasks}/bbc/`) and in
`## Code Organization`: the map is the design, and the code follows it.

### 6. INVENTORY, PROPOSE
`/bbc-plan` steps 7-8, on the map approved in step 5.

### 7. PLAN
`/bbc-plan` step 9: the plan brings the code to the changed map — a TDDAB plan when a behaviour or a
contract changes, a Step plan (`step-planner.md`) when the code only moves; one or the other, never both
(`step-planner.md` §5). Every block ends with the tests of the BBs it touches.

### 8. Commit, STOP
`/bbc-plan` steps 10-11, with `{@tasks}/bbc/` among the files committed. With a contract changed, the
STOP also names `/bbc-integrate` with the BBs that use it, after the plan is executed.

## Rules
- **The map changes first, approved; then the code.**
- **A contract or a decision changes only by the user's decision**, named with the BBs that use it.
- **No figure judges the result** (`principles.md` 7.3): the tests and the gate do.
