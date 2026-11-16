---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC — check whether the code reflects the analysis: each black box's code in its namespace, its contract in the Core as the map writes it, the dependencies only through the Core and only those on the map, the decisions of the map kept. It writes a report, and the findings are fixed by one feature. Use when the roadmap reaches the audit, after BBs were built or changed, or the user says bbc audit, il codice rispecchia la mappa, controlla il codice contro la BBC."
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first); its own code roots
  (`@own-code-roots`).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md` — the method, the map (§2).
- `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`, followed for every lookup: print its CODE-NAV
  PREFLIGHT block before the first one. `@code-nav-local` answers: one outline or info query on a file of
  the project, its result quoted — otherwise STOP and propose `/dev:j-mcp-setup`, as `x-audit-code.md`
  Prerequisites say: the audit confirms every claim through the navigation tool.
- The map: `{@tasks}/bbc/BBC-MAP.md` and `{@tasks}/bbc/bb/` (missing → `/dev:bbc-analyze` first).
- When step 4 writes a plan: the CVM answers (`mcp__cvm__parsePlan` is available); otherwise propose
  `/dev:j-mcp-setup`, CVM. STOP. And `${CLAUDE_PLUGIN_ROOT}/commands/j-cvm-exec-plan.md`, read in full: its steps 1-5 are
  how that plan is executed here.

## Purpose
The map is the design the code follows (`bbc.md`): it was approved before the code existed. This command
reads the code and says where it does not follow the map — nothing else. The rules of the set on how
code is written are `/dev:x-audit-code`'s; this one checks only what the map promises. **It fixes nothing:**
its findings make a report, and one feature fixes them.

## Steps

### 1. Read the map
`BBC-MAP.md` — with its `## Decisions` and its dependency graph — and every `bb/BB<N>-<name>.md`. The BBs
with the status `built` are checked; a BB `to build` has no code yet, and the report names it as such.

### 2. The code's graph — the tool, deterministic
As `x-audit-code.md` step 1 runs it:
- the first time (no `audit/.tools/`): `bash ${CLAUDE_PLUGIN_ROOT}/audit/install.sh`;
- the scope, `audit/scope.md`, as that step says it — asked to the user once, the folders that hold the
  BBs' code; the tool refuses the map without it;
- `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py map` → `audit/map/modules.md`, `audit/map/graph.md`. The tool refuses,
  and leaves the map as it is, when its parser is missing; a map with no module is not one either: show
  the output, STOP.

A BB is a namespace — its folder in each layer it cuts (`bbc.md` §1.5): its modules in `modules.md` are
those folders.

### 3. The checks — per BB
Each finding with the map's line, the code's `file:line`, and the query or the line of `graph.md` that
shows it:
- **Its files in its namespace**: the files its definition lists are in its folders, and its folders
  hold nothing of another BB's responsibility.
- **Its contract in the Core as the map writes it**: every member, its inputs, its results, its errors —
  read with the navigation tool on the Core's declaration.
- **Its implementation behind that contract**: the code that does the BB's work implements the Core's
  interfaces; nothing it exposes outside them is used by another BB.
- **Its dependencies**: every edge of `graph.md` that leaves its modules goes to the Core, or to a BB its
  definition depends on, through that BB's contract; none goes to another BB's implementation, and none
  is missing from the map.
- **The decisions**: every decision of `## Decisions` that governs it — the style, the mechanism — is the
  one its code follows (`code-principles.md` §2 for the mechanisms).

### 4. Here, or a plan of its own
When the BBs to check do not fit one session, the checks become a Step plan
(`${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/step-planner.md`, read in full): `{@tasks}/bbc/audit-plan.md`, one block per
BB, each block running step 3 on its BB and writing its findings into the report of step 5. Its block
ids are new to the project, as `step-planner.md` Tag Rule 2 says. The plan is validated with
`mcp__cvm__parsePlan` (invalid → corrected and parsed again): it has no task folder, and the review of
a plan is made against one. Then it is executed here, as `${CLAUDE_PLUGIN_ROOT}/commands/j-cvm-exec-plan.md` steps
1-5 say, and on to step 5: this command writes only its report, so no stop protects anything.

### 5. The report
`{@tasks}/bbc/BBC-AUDIT-YYYY-MM-DD.md`: for each BB, each finding — the check, where (the map and the
code, `file:line`), the evidence, what the map says instead; the BBs with no finding, named; the BBs
`to build`, named.

The roadmap: when the report has no finding, the audit's line of `## Roadmap` in
`{@tasks}/bbc/BBC-MAP.md` is marked done (`bbc.md` §2). With findings it stays open: the run of this
command after the fix closes it.

### 6. Commit
```bash
git add {@tasks}/bbc/BBC-AUDIT-YYYY-MM-DD.md   # and {@tasks}/bbc/BBC-MAP.md, when step 5 marked the roadmap
git commit -m "docs(bbc): audit of the code against the map YYYY-MM-DD"
```
Only these files; other pending changes stay as they are, and the report names them.

### 7. STOP
The findings are fixed by one feature: `/dev:j-new-feature`, its requirements the report; it reads the map in
its ANALYZE (`j-new-feature.md` step 6). A finding the user
decides belongs to the map — the design must change, not the code — goes to `/dev:bbc-refactor` instead.

## Rules
- **Only what the map promises**: the set's rules on code are `/dev:x-audit-code`'s.
- **By reading the code, and with deterministic tools** (`principles.md` 7.1-7.3): the navigation tool and
  the graph of `audit.py`; no grep presented as a finding, no number.
- **A finding without its evidence is not a finding.**
- **Nothing is fixed here.**
