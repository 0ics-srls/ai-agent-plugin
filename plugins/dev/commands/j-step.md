---
description: A feature built in small steps the user drives (junior workflow). Each run is one step — the user says one piece, the piece goes through the phases of a feature at its own size, ONE TDDAB block is written, approved and executed with the planexecutor, then it STOPS and the user checks. The first run opens the branch and the task folder; the next ones add a step to the same feature; /dev:j-close closes it. Use when the user wants to build step by step, a piece at a time, un pezzo alla volta, passo passo, po kroku, or does not know the whole feature yet.
---

## Prerequisites
1. Read the Memory Bank (skip the subdirectories) if not already done this session.
2. `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
3. If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
   `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md`.
4. `${CLAUDE_PLUGIN_ROOT}/commands/j-new-feature.md`, read in full: a step goes through its phases, by number, at
   the size of one piece — its contracts of ANALYZE, INVENTORY and PROPOSE are the ones a step obeys.
5. `${CLAUDE_PLUGIN_ROOT}/commands/j-cvm-exec-plan.md`: a step executes its block as that command says.

## Purpose
A feature whose whole is not known when it starts: the user says one piece, sees it built, and from
what they see says the next one. Each run of this command is one step:

```
the user says a piece → what it touches, what already does it → ONE TDDAB block → the user approves it
                      → the planexecutor executes it → STOP: the user checks → the next run
```

The first run opens the feature — its branch, its task folder. Every later run adds a step to it.
`/dev:j-close` closes it, when the user says the feature is done. The task's file is
`{@tasks}/NN-<feature>/notes.md`; the plan is `{@tasks}/NN-<feature>/plan.md`, one block longer at
every step.

A step is small on purpose, and that is its risk: nobody decides the structure of the whole. So every
step looks for what already exists before it writes, `## Shared` in `notes.md` says what the steps
have in common, and a piece that changes something shared stops and asks (step 4).

## Steps

### 1. The first step, or the next one
Read `@feature`, `@branch` and `@state` in `activeContext.md`, and the first lines of that task's
`notes.md`.
- **No work in progress** (`@state::IDLE`, no `@feature`) → the first step: step 2.
- **`notes.md` says `Flow: j-step`** → the next step of that feature. The current branch is `@branch`
  (otherwise `git checkout` it) and `git status --porcelain` is empty; changes that are there are
  shown to the user, and committed or left on their word. Then, by the last entry of `## Steps`:
  - its block was executed (`@state::LISTEN`) → a new step: step 3;
  - it has no `Block:` yet → that step was left before its block was approved: say where it stands
    and go on from step 4;
  - it has its `Block:` and `@state::DEVELOP` → the execution was interrupted: step 6 resumes it.
- **Another work is in progress** — a feature, a bug, a black-box work → say which one and STOP: it
  is resumed with `/dev:j-continue` and closed with `/dev:j-close`; a step is not added to it.

### 2. The first step: the feature is opened
`/dev:j-new-feature` steps 1-3: the uncommitted changes reviewed and committed, the base branch of
`@merge-strategy` pulled, the next `NN`, the name asked and confirmed, `feature/NN-<name>` created
and pushed, `{@tasks}/NN-<name>/`.

`{@tasks}/NN-<name>/notes.md`:
```markdown
# Feature: NN-feature-name
Flow: j-step

## Requirements
<!-- what the feature is for, in the user's words; completed as the steps say more -->

## Shared — what the steps have in common
<!-- one line per capability more than one step uses: what it does, its owner (path, symbol), the contract the others see -->

## Steps
<!-- one entry per step, appended; an entry is not rewritten once its block is executed -->

## Status
- [ ] Closed (/dev:j-close)
```
**Update MB** in `activeContext.md`: `@feature::NN-feature-name`, `@branch::feature/NN-feature-name`.

### 3. LISTEN — one piece
**Update MB:** `@state::LISTEN`.

The piece is what the user wrote with the command; with nothing written, ask:
```
Step {N} of {NN-feature-name}.
Tell me the next piece — one thing I can build and you can check — or what to correct in the last one.
```
- The step before has `Checked by the user: pending` → it is asked first, in the same question, and
  written in that entry: `ok`, or what was wrong.
- **What was wrong is a piece like any other**: this step corrects it, and its block's tests say what
  the correct behaviour is. The executed block of the step before is not changed.
- A piece that is not clear enough to write its tests → ask, with AskUserQuestion, what is missing.
  No code is read and nothing is proposed until the piece is clear.

Append the step's entry under `## Steps`, and what the piece says about the whole under
`## Requirements`:
```markdown
### Step N — <title>
- Asked: <the user's words>
- Touches:
- Inventory:
- Organization:
- Block:
- Checked by the user: pending
```

### 4. ANALYZE, INVENTORY, PROPOSE — at the size of the piece
**Update MB:** `@state::ANALYZE`.

`/dev:j-new-feature` steps 6, 7 and 8, on this piece and on nothing else. Their three contracts hold as
they are written there; what a step does differently:

- **The mindsets of the ANALYZE contract** are re-read on the first step of a session, and again
  after the context was compacted. Between two steps of the same session they are in context.
- **`Touches`**: the code this piece touches, read with code navigation (`code-navigation.md`). With
  a black-box map, as `/dev:j-new-feature` step 6 says: a change of a contract, of a boundary or of a
  decision → STOP, `/dev:bbc-refactor`.
- **`Inventory`**: one line per capability the piece needs, answered as the INVENTORY contract
  requires — where it already lives, or the search that came back empty, and the decision: reuse,
  extend, write. `## Shared` is read first: what an earlier step wrote is the first place a
  capability already lives.
- **`Organization`**: what of this piece is shared, and who owns it.
  - Nothing of it is shared and nothing shared changes → the line says so, and the step goes on
    without a question.
  - **The piece adds something more than one step will use, or changes something shared — an owner,
    a contract, the mechanism of a behaviour** → STOP and ask with AskUserQuestion, presenting that
    part with the five entries of the PROPOSE contract. On the user's approval `## Shared` is
    updated, and the step goes on.
- **A piece too large for one block** (`tddab-planner.md`: a block is atomic) → say so, propose how it
  splits into pieces, and ask which one this step builds. The others are the next steps, when the
  user says them.
- **A piece that is not built test-first** — a removal, a migration, a reconfiguration — is not a
  step: say so, and that it is a feature of its own (`/dev:j-new-feature`, a Step plan).

### 5. The block
**Update MB:** `@state::PLAN`.

On the first step of a session, the methodology is read in full, as `/dev:j-new-feature` step 9 a-b says:
`mind-sets/tddab-planner.md` and the language's `overlays/<language>/tddab.md`, and the 3-5 key rules
this feature's blocks follow written under `## TDDAB Rules Applied` in `notes.md`, once.

`{@tasks}/NN-feature-name/plan.md`, in the structure `tddab-planner.md` defines:
- **The first step** writes it: the `<mission>` — from `## Requirements` and `## Shared`, complete
  enough to execute a block with no other context — and the block `01-<slug>`.
- **A later step** appends ONE block, the next number, and brings the `<mission>` up to date with
  what `## Shared` and `## Requirements` now say. **The blocks already executed are not touched.**
- The block's tests are this piece's behaviour, every case of it; for a correction, the behaviour the
  user expected.

The block is reviewed as `/dev:j-review-plan` says, on the `<mission>` and on the new block: the blocks
already executed are not reviewed again. What the review finds is corrected before the user sees the
block.

Then show the block — its tests, in plain words; the files it writes or changes; what it reuses — and
ask with AskUserQuestion: execute it, or change it. Changed on the user's word, and asked again.

On the approval: `Block: NN-<slug>` in the step's entry, `@plan::{@tasks}/NN-feature-name/plan.md` in
the Memory Bank, and
```bash
git add {@tasks}/NN-feature-name/notes.md {@tasks}/NN-feature-name/plan.md memory-bank/activeContext.md
git commit -m "docs(NN-feature-name): step N — <title>"
```

### 6. DEVELOP — the block is executed
**Update MB:** `@state::DEVELOP`.

As `j-cvm-exec-plan.md` steps 1-5 say, on `{@tasks}/NN-feature-name/plan.md`: the plan is parsed,
the blocks of the earlier steps are in the planexecutor's list and are skipped, and the one new block
goes through its phases — RED, GREEN, VERIFY, the commit. Every rule of that command holds: one CVM
call per turn, no code outside the task the planexecutor hands out, the plan not edited while it runs.

**No step runs the final gate.** A step ends with its block's own commands — the gate of what it
touches, its tests, the fast regression — and the FINAL REVIEW of the execution runs the same fast
commands (`j-cvm-exec-plan.md` step 3). `@gate-final` is `/dev:j-close`'s, once, when the feature is done:
a step that ran it would make a one-line piece cost minutes.

A block that cannot be made to pass → stop and tell the user what and why, as that command's step 4
says. The piece is then said again, smaller or differently: a new step.

### 7. STOP — the user checks
**Update MB:** `@state::LISTEN`. `git push origin feature/NN-feature-name`.

```
✅ Step {N} done: {title} — block {NN-slug}, commit {hash}

Check it: {how to see this piece working — the command to run, the page to open, the test that shows it}

Next: /dev:j-step with the next piece, or with what to correct. /dev:j-close when the feature is done.
```
**Nothing more is built.** The next piece is the user's to say.

## Rules
- **One piece, one block, one execution, then STOP.** A step does not go on to the next piece.
- **The final gate is `/dev:j-close`'s**: no step runs `@gate-final`.
- **No code outside the planexecutor**: the block is the only way code gets written.
- **Every step looks for what exists before it writes**, `## Shared` first.
- **A block already executed is never changed**: a correction is a new step.
- **Something shared that is added or changed is asked**, before the block is written.
- **Update the Memory Bank at every phase change.**
- **`/dev:j-close` closes the feature**: it reads the whole change against the mindsets and runs the gate.
