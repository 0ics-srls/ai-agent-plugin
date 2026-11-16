---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Parse and execute a plan — TDDAB or Step — with the CVM planexecutor, block by block, in the phases the planexecutor runs. Resumes after an interruption. Use when the user says execute plan, esegui piano, run plan CVM.
---

# CVM Execute Plan

The planexecutor is a program that runs inside the CVM: it holds the plan, the state and the order
of the phases, and every task it hands out says what to do and what to answer. This command starts it
and drives it: it takes a task, does it, reports the outcome.

## Prerequisites

- The CVM MCP server answers (`mcp__cvm__parsePlan` is available). When it is not: run
  `/dev:j-mcp-setup`, choose CVM, come back. STOP.

## Steps

### 1. The plan
- The path the user gave; otherwise the plan path in the Memory Bank's `activeContext.md`; otherwise
  ask with AskUserQuestion and wait.
- **The plan file is not read here, and no plan file is searched for.** Each task points at the part
  of the plan its phase needs; reading the whole plan beside it invites working ahead of it.
- `mcp__cvm__parsePlan` with `filePath`, the path. Invalid → show the errors and STOP.
- **A block whose id is in `.cvm/uplan-progress.json` is skipped, silently.** That is how an interrupted plan resumes;
  a new plan with an id an earlier plan completed loses that block. Before a new plan starts, its ids are compared with that
  list: one that is there is renamed in the plan, and the review runs again.
- To start over instead of resuming, on the user's word only: delete `.cvm/uplan-progress.json`.

### 2. Start the planexecutor
```
mcp__cvm__loadFile → programId: "planexecutor", filePath: "@planexecutor"
mcp__cvm__start    → programId: "planexecutor", executionId: "run-<timestamp>"
```

### 3. The loop — one CVM call per turn
`mcp__cvm__getTask`, do the task, `mcp__cvm__submitTask` with the answer the task asks for, wait for
its reply, then the next `getTask` — until it answers "Execution completed". What each task does is
in the task and in the plan. Every CVM call is made by the main conversation, one per turn: two in the
same turn put the phases out of step.

### 4. When a fix cannot be found
The planexecutor repeats FIX and RE-VERIFY until the block passes; it has no limit. When the evidence
gives no fix, stop and tell the user: the plan may need to change.

### 5. The plan does not change during the execution
The planexecutor loads the plan when it starts and hands out every block from that copy. Editing the
plan file, or running `parsePlan` again, changes nothing it hands out: the execution and the file
stop agreeing. A FIX fixes the code. When the plan itself is wrong — a command that cannot run, a name
the gate refuses, a step that cannot be done as written — stop and tell the user what and why. The
plan is corrected and reviewed (`/dev:j-review-plan`), then this command runs again: `parsePlan`, start,
and the blocks already completed are skipped.
