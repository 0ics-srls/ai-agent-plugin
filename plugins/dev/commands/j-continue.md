---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Continue existing work (junior workflow). Resumes a feature or a bug from where it stopped — reads the Memory Bank's state, checks it against the branch and the task folder, re-reads what the phase needs, picks up the thread. Use when the user says continue, riprendi, pokracuj, or starts a new session on existing work.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
  `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md` — the phases, and what each one leaves.

## Steps

### 1. Current branch
```bash
git branch --show-current
```
Not on a `feature/*` or `bugfix/*` branch → ask with AskUserQuestion which work to continue.

### 2. State from the Memory Bank
From `activeContext.md`:
- `@state` — the phase: LISTEN, ANALYZE, INVENTORY, PROPOSE, PLAN, DIAGNOSE, DEVELOP, CLOSE, DEPLOY, or
  IDLE — no work in progress: say so, and name `/dev:j-new-feature`, `/dev:j-bug`, `/dev:j-poc`; STOP;
- `@feature` or `@bug` — the task, whichever exists;
- `@branch`.

### 3. Check it against reality
`@state` empty or not a phase:
- **Reality first**: is there a feature or bugfix branch? a task folder with notes? recent commits?
- Reality shows work in progress → propose updating the Memory Bank to match it.
- Nothing exists:
  ```
  Invalid state in Memory Bank.
  Use /dev:j-status to see what's there, or /dev:j-new-feature to start fresh.
  ```
  STOP.

The task folder missing from `{@tasks}/`:
- **Check the branch name** — the folder may have another name.
- Truly missing:
  ```
  Task folder not found: the Memory Bank names a task that is not in {@tasks}/.
  ```
  STOP.

### 4. The task folder
`{@tasks}/{@feature}/` or `{@tasks}/{@bug}/`: `notes.md` (or `bug-notes.md`), `plan.md` when it
exists, the other files.

### 5. Status
```
Here's where we were:

Task: [name]
Branch: [current branch]
Phase: [state]

DONE:
[from the Memory Bank and the task's notes]

NEXT:
[what comes now — for ANALYZE, INVENTORY or PROPOSE: the design documents are re-read first, and the
sections the earlier phases leave are checked in notes.md, so the user sees it coming]

Want to continue from here or do you have updates?
```

### 6. Resume
Updates from the user → listen. Confirmed → resume the phase, as the command that owns it says
(`/dev:j-new-project` for `01-scaffold`, `/dev:j-new-feature` for a feature, `/dev:j-bug` for a bug; CLOSE is
`/dev:j-close`'s, DEPLOY `/dev:j-deploy`'s). A task whose `notes.md` says `Flow: j-step` is a feature in steps:
`/dev:j-step` resumes it — the step left half way, or the next one. A task whose `notes.md` has `## BB scope` is a black-box work: its
phases are resumed as the command of its `Flow:` line says (`/dev:bbc-core`, `/dev:bbc-plan`, `/dev:bbc-refactor`,
`/dev:bbc-integrate`, `/dev:bbc-e2e`; `/dev:bbc-plan` when the line is missing), with the BB's scope (`bbc.md` §3); a bug whose `bug-notes.md`
says `Flow: bbc-debug` keeps its ISOLATE on the map (`/dev:bbc-debug` step 6). Resuming is entering the phase: whatever was in context when the work
stopped is gone.

**LISTEN** — show what `## Requirements` (or `## Problem`) already holds, and go on listening until the
user says "done".

**A feature in ANALYZE, INVENTORY or PROPOSE** — apply the contract of every phase up to the one
being resumed, in order, and check the product of each one already passed: a missing section is
produced now, because the phases after it execute what it says.

```
ANALYZE_CONTRACT (what the phase requires, and what it leaves):

ENTERING the phase, re-read these NOW — even if they were already read this session:
  - the mindsets the code is designed and written against (paths relative to mind-sets/):
      principles.md, code-principles.md, testing-principles.md
      the branches named in j-settings.md @mindsets-branches
      the overlay files named in j-settings.md @mindsets-overlay
    (one set per component when j-settings.md has `-<component>` keys)
  - mind-sets/code-navigation.md                  (follow it for every symbol/code lookup)
WHY re-read: LISTEN can run for days. Whatever was loaded when the session opened is out of
context or already compacted by the time the analysis arrives — and these are the documents
the work is understood against, which happens now.

LEAVING the phase, notes.md carries `## Analysis`: what the work touches, and the mindsets that apply
to it.
```
```
INVENTORY_CONTRACT (what the phase looks for, and what it leaves):

WHAT IT LOOKS FOR — capabilities, not names. A capability is what a piece of code DOES:
validate an account number, retry with backoff, convert a currency, refresh a token. A
different name is not a different capability, and a search by name is exactly how an existing
implementation stays hidden. The rule is mind-sets/principles.md 2.1-2.3, and the search
discipline is mind-sets/code-navigation.md:
the tool comes from j-settings.md (@code-nav-local for own code, @code-nav-external for
third-party APIs), and where a semantic tool is available its use is required, not optional.

WHERE IT LOOKS: in the order of mind-sets/principles.md 2.3 — the project's own code first (the
usable piece: a function, a class, a module, a package), the web last.

LEAVING the phase, notes.md carries a `## Inventory — capabilities and where they already live` section,
one line per capability the task needs, each line ANSWERED:
  1. the capability, described by WHAT IT DOES — not by the name it has or would get
  2. in the project: path + symbol of the existing implementation, found with the tool — or the
     search that was run and came back empty, quoted, because "it does not exist" is a claim and
     not an impression
  3. outside the project: the library already depended on, or the package available, that covers
     it — name + version — and the reference found, if the answer came from the web
  4. the decision: reuse it (from where), extend it (what), or write it (why nothing covers it)
WHY here: this is the last point where changing the decision costs one sentence. Once the plan
exists it costs a block, and once the code exists there are two implementations and nobody
repairs them. The worst copy is the one written during a clean-up of duplicates.

PROPOSE presents this section together with `## Code Organization` and asks, in so many words:
is this what we reuse? The plan then executes it without re-deciding it, and /dev:j-review-plan
refuses a plan whose block rewrites a capability this section had already located.
```
```
PROPOSE_CONTRACT (what the phase decides, and what it leaves):

The structure is decided on what INVENTORY found: what exists is reused, and only what nothing
covers gets written.

LEAVING the phase, notes.md carries a `## Code Organization` section, five entries, each one
ANSWERED and not left open:
  1. what of this feature is shared — with what exists already, or with what is coming
  2. which package/module/project owns each shared part, by name and path
  3. for each shared part: the contract the consumers see, and who injects the implementation
     — chosen against `mind-sets/code-principles.md` §1 (SOLID)
  4. what this feature does NOT own, named with the package that owns it instead
  5. the mechanism chosen to govern the behaviour, and why (catalogue in
     `mind-sets/code-principles.md` §2)
WHY here: here it costs one sentence to change the decision. Once the plan exists it costs a
block, and once the code exists nobody repairs it.

The user approves it before any plan is written.
```
A task with `bug-notes.md` is a bug: it has no inventory and no organization of its own
(`development-workflow.md`), and the contracts above do not apply to it.

**PLAN** — re-read the rules the plan's code is written against: `mind-sets/principles.md`,
`code-principles.md`, `testing-principles.md`, the branches of `@mindsets-branches`, the overlay files
of `@mindsets-overlay` (one set per component when `j-settings.md` has `-<component>` keys); then the
planner of the plan's type, in full (`tddab-planner.md` with the language's `tddab.md`, or
`step-planner.md`).

**DIAGNOSE** — re-read `mind-sets/debug-protocol.md` and continue Protocol D from the last step written
in `bug-notes.md`.

**DEVELOP** — `/dev:j-cvm-exec-plan`: it resumes the execution from the blocks already completed.

**CLOSE** — `/dev:j-close`, from its step 1: it checks again what is done. **DEPLOY** — `/dev:j-deploy`.

## Rules
- Always read `j-settings.md` and the Memory Bank before anything.
- Never assume — if unclear, ask with AskUserQuestion.
- Remind the user to save (`/dev:j-save`) before leaving.
