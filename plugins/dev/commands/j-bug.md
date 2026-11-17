---
description: Fix a bug (junior workflow). Goes through the bug path of development-workflow.md — LISTEN, DIAGNOSE with Protocol D, PLAN — on its own branch and task folder, then STOPS; the user triggers /dev:j-cvm-exec-plan to execute the fix. Use when the user reports a bug, something is broken, non funziona, nefunguje, or needs to fix an error.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
  `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md` — the bug path, and what each phase leaves.
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md` (Protocol D — systematic
  debugging).
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`, followed for tracing the bug and every symbol
  lookup (the tools of `@code-nav-local` and `@code-nav-external`; a text search is the declared
  fallback when the tool is absent or not ready).

## Purpose
A bug goes LISTEN → DIAGNOSE → PLAN → DEVELOP → CLOSE (`development-workflow.md`). This command runs
the first three on the bug's own branch and task folder: it finds the cause with Protocol D and writes
the plan that fixes it. **It writes no fix: `/dev:j-cvm-exec-plan` executes the plan.** The task's files are
`{@tasks}/NN-<bug>/bug-notes.md` (the diagnosis) and `plan.md` (the fix).

## Steps

### 1. Clean State
- `git status` — check for uncommitted changes.
- If changes exist:
  - **Review what will be committed** — no sensitive files (.env, credentials)?
  - If something unexpected → ask the user before committing.
  - On `{@main-branch}` or `{@dev-branch}`: no WIP commit on a shared branch. They stay uncommitted through
    step 2, and step 3 commits them on the new branch.
  - On any other branch: `git add . && git commit -m "WIP: save before bugfix"`, then `git push`.

### 2. Sync with the base branch
The base branch follows `@merge-strategy`: `gitflow` or `gitflow-simple` → `{@dev-branch}`; otherwise
`{@main-branch}`.
```bash
git checkout {base-branch}
git pull origin {base-branch}
```
**IMPORTANT:** always start from the latest base branch, to avoid conflicts later.

### 3. Branch and folder
- The next number: the highest `NN-*` **folder** in `{@tasks}/`, plus one
  (`ls -d {@tasks}/[0-9][0-9]-*/ 2>/dev/null | sort | tail -1`); 01 when there is none.
- Ask the bug's short name with AskUserQuestion, then confirm:
  ```
  I'll create:
  - Branch: bugfix/NN-{bug-description}
  - Folder: {@tasks}/NN-{bug-description}/
  ```
- On confirmation:
  ```bash
  git checkout -b bugfix/NN-bug-description
  mkdir -p {@tasks}/NN-bug-description
  git push -u origin bugfix/NN-bug-description
  ```
  What step 1 left uncommitted on a shared branch is committed here, reviewed as step 1 says:
  `git add . && git commit -m "WIP: save before bugfix"`.
  **IMPORTANT:** push the branch immediately, so the user can see it on the remote.

### 4. Bug notes
Create `{@tasks}/NN-bug-description/bug-notes.md`:
```markdown
# Bug: NN-bug-description

## Problem
**Expected:** [what should happen]
**Actual:** [what happens instead]
**Where:** [page/function]

## Diagnosis
<!-- Protocol D: READ, ISOLATE, DOCS, HYPOTHESIZE -->

## Verification
- [ ] Bug reproduced
- [ ] Cause found, hypothesis approved
- [ ] Fix plan reviewed (plan.md)
- [ ] Fixed (/dev:j-cvm-exec-plan)
- [ ] Closed (/dev:j-close)
```

### 5. LISTEN
**Update MB** in `activeContext.md`:
```
@state::LISTEN
@bug::NN-bug-description
@branch::bugfix/NN-bug-description
```
Say:
```
Tell me about the bug:
- What SHOULD happen?
- What happens INSTEAD?
- Where do you see it? (which page/function)

If you have screenshots, share them!
When done explaining, say "done".
```
Write what the user says under `## Problem`.

### 6. DIAGNOSE — Protocol D, up to the hypothesis
**Update MB:** `@state::DIAGNOSE`

A `/dev:j-debug` session that found this problem (`@lastDebug`, `@debugResult::wasBug`) is where the
diagnosis starts: its steps are checked against the code and written under `## Diagnosis`, not
redone from nothing.

**A project with a black-box map.** `{@tasks}/bbc/BBC-MAP.md` exists → ISOLATE follows the map, as
`${CLAUDE_PLUGIN_ROOT}/commands/bbc-debug.md` step 6 orders it (the BBs the failure crosses, their tests leaves
first, then the integration points), and `bug-notes.md` carries the line
`Flow: bbc-debug, ISOLATE on {@tasks}/bbc/BBC-MAP.md` under its title. The fix stays in the BB that
owns the cause; a fix that changes a contract → STOP, `/dev:bbc-refactor`.

Apply Protocol D (`debug-protocol.md`), writing each step under `## Diagnosis`:
1. **READ** — the exact error or behaviour, quoted.
2. **ISOLATE** — the precise location (file:line), where it appears and where it originates.
3. **DOCS** — the framework's documentation, when the error is the framework's.
4. **HYPOTHESIZE** — the cause, the reasoning, the prediction of what the fix changes.

Tools: the browser through ChromeDevTools (`/dev:j-browse`) when the bug shows in the UI, or the user's screenshots;
code navigation for the code; the logs where the logger's configuration writes them
(`branches/operations.md` 1); the services started with `@start-<component>`. The bug is reproduced on
command before the hypothesis: a fix that cannot be shown to work is not a fix.

DIAGNOSE designs nothing: a fix that touches something shared points at it, by name and path
(`development-workflow.md`). Then ask, and wait:
```
I found the problem: [simple explanation]

**Hypothesis:** [what causes it]
**Reasoning:** [why]
**Prediction:** [what will happen after the fix]

To fix it I need to: [what the plan will do]

Proceed?
```

### 7. PLAN — the fix, always as a plan
**Update MB:** `@state::PLAN`

Write `{@tasks}/NN-bug-description/plan.md`, of the type the fix is, and its path in the Memory Bank
(`@plan::{@tasks}/NN-bug-description/plan.md`):
- **TDDAB** (`tddab-planner.md` with the language's `tddab.md`) when a test can show the bug: the RED is
  the test that fails because of it, the GREEN the fix;
- **Step** (`step-planner.md`) when the fix is a removal, a migration or a configuration change.

The mission can be brief for a bugfix. The prediction of HYPOTHESIZE is a criterion of the success:
it is what Protocol D's VERIFY checks. Every block carries the Protocol D line and its commands, as the
planner states them.

Then `/dev:j-review-plan`, as the planner requires: the plan is shown only once the review approves it.

### 8. Commit the phase's product
```bash
git add {@tasks}/NN-bug-description/bug-notes.md {@tasks}/NN-bug-description/plan.md <any plan sub-files> memory-bank/activeContext.md
git commit -m "docs(NN-bug-description): diagnosis and fix plan"
git push origin bugfix/NN-bug-description
```
Only these files; other pending changes stay as they are, and the report names them.

### 9. STOP
```
✅ Bug diagnosed and fix plan reviewed: {@tasks}/NN-bug-description/plan.md ({N} blocks)

Next: /dev:j-cvm-exec-plan {@tasks}/NN-bug-description/plan.md, then /dev:j-close to merge.
```
**Start no fix. The user triggers `/dev:j-cvm-exec-plan`.** `@bug` and `@branch` stay in the Memory Bank
until /dev:j-close.

## Rules
- **Protocol D always** — READ the exact error, ISOLATE precisely, HYPOTHESIZE before fixing, VERIFY
  one change at a time.
- **LISTEN → DIAGNOSE → PLAN → STOP**, in this order; the fix is a plan, executed by the CVM.
- **ONE change at a time** — never change multiple things without verifying.
- **ZERO warnings** — the gate of every block is green.
- NEVER delete branches (the user needs them for review and control).
- ALWAYS push the branch.
- If the "bug" is actually a feature → `/dev:j-new-feature`.
- **Ask with AskUserQuestion** whatever is not decided.
