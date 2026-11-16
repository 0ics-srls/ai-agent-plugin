---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC — design the black boxes of a new project, or of a new part of one, from the requirements, with the user, before any code ({@tasks}/bbc/): the black boxes by responsibility, their contracts, dependencies and flows, the decisions of the architecture. No code is read. The diagram is approved before the details; then /dev:bbc-review, and back here with its findings until the user approves the map. Use when a project, or a part of it, too large for one context window is to be built as black boxes, or the user says bbc analyze, mappa BBC, black box map, scomponi in BB, progetta a black box."
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md` — the method, and the map's structure
  (§2).
- The last `{@tasks}/bbc/BBC-REVIEW-YYYY-MM-DD.md`, when it exists: the findings it sent here are what
  this run corrects.

## Steps

### 1. The project
From the Memory Bank (`productContext.md`) and the user: what the project — or the new part — must do,
and its components. No code is read: the map is designed from the requirements (`bbc.md` §2). The
layers are not asked here: they are named with the language, which `/dev:bbc-core` asks.

What the user says the project, or the new part, must do is written in `{@tasks}/bbc/BBC-MAP.md`
`## Requirements` (`bbc.md` §2), as the user says it, one requirement per line — now, before step 2
splits it: `/dev:bbc-review` runs in another session and reads the requirements there.

A new part of an existing project: the existing code it uses is described by the user — what it does,
and its contract as it is today — and goes on the map as an external system.

A map that already exists in `{@tasks}/bbc/` → read it first, and keep what is still true. With a
review's findings, this run corrects them: each finding's answer is written beside it in the review.

### 2. The responsibilities
The requirements split by responsibility — five to ten sentences without an "and" — each one a BB
candidate, then the wrappers (`bbc.md` §1.4). Each candidate is named with the user, with
AskUserQuestion: its responsibility and the BBs it depends on. Every BB has the status `to build`
(`bbc.md` §2); its contract is designed in step 4, once the boundaries are approved.

### 3. The diagram first
Show the dependency graph (Mermaid, the colours of `bbc.md` §2) and, under it, one line per BB: id,
name, responsibility, status. Ask with AskUserQuestion: **are these the boundaries?** — split, merge, a
responsibility missing. Change and show again until the user approves it.

### 3b. The decisions
The style of the architecture (layers, hexagonal…) and the mechanisms the BBs need
(`code-principles.md` §2 — a state machine, a strategy behind one contract, a named pipeline…), each
with its reason and the BBs it governs. Asked with AskUserQuestion, one at a time, and approved; written
in `## Decisions` (`bbc.md` §2).

### 4. The details
For each BB, designed with the user, with AskUserQuestion, one BB at a time: its contract — the members,
their inputs, their results, their errors — shaped by the BBs that will use it (`code-principles.md` 1.7)
and approved; its dependencies and dependents; its files `none — to build`; its tests `none`. An external
system has the contract the user described in step 1.

Then the layer-to-BB matrix, the 2-3 flows that cross most BBs (sequence diagrams), the integration
points — caller, callee, the contract between them — and the **dependency graph** in the order of the
integration: the BBs that depend on nothing first, then each BB after those it uses. The order is the
integration's: with the Core of the contracts in place every BB can be developed at the same time
(`bbc.md`, the steps of the method).

### 5. Write the map
`{@tasks}/bbc/BBC-MAP.md` (with `## Requirements`, written in step 1, and `## Decisions`),
`{@tasks}/bbc/bb/BB<N>-<name>.md`,
`{@tasks}/bbc/diagrams/*.mmd`, as `bbc.md` §2 lists them. Each boundary carries its reason in one line.
A review's findings corrected here: their answers written in the review.

### 6. Commit
```bash
git add {@tasks}/bbc/
git commit -m "docs(bbc): black-box map"
```
Only these files; other pending changes stay as they are, and the report names them. The commit lands
on the branch this ran on: `/dev:bbc-work` opens its worktrees from the base, so the map reaches the base
before any BB is delegated — the report says so when this branch is not the base.

### 7. Report
The BBs with their responsibilities, the graph, the decisions, the flows. Next: `/dev:bbc-review` to review
the analysis; its findings come back here, until the review has none the user wants corrected.

## Rules
- **Responsibilities, not files**: a BB is what the system must do.
- **No code is read**: the map comes from the requirements and the user's approvals.
- **The requirements are in the map**, `## Requirements`, written as the user said them: the review
  reads them there.
- **The diagram is approved before the details are written**, and **the decisions are approved before
  the details**.
- **A BB is designed one at a time**, with the user.
