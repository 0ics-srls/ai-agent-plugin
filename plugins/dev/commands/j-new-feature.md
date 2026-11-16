---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Start a new feature (junior workflow). Creates the feature branch and task folder and goes through the phases of development-workflow.md up to PLAN — what the user needs, the code and the mindsets that apply, what already exists, the structure — writes the plan, reviews it, then STOPS. The user triggers j-cvm-exec-plan to execute it. Use when the user wants to add something new, implement a feature, aggiungere funzionalita, or pridat novu feature.
---

## Prerequisites
These open the session. The documents needed to DESIGN are re-read on entering ANALYZE instead —
LISTEN can run for days, and what was loaded at the opening is out of context, or compacted away, by
the time the analysis arrives.

1. Read the Memory Bank (skip the subdirectories) if not already done this session.
2. `j-settings.md` at the repository root (missing → run `/j-setup` first).
3. If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
   `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md` — the phases this command goes through, with
   what each one leaves in `notes.md`.

## Purpose
A feature goes LISTEN → ANALYZE → INVENTORY → PROPOSE → PLAN → DEVELOP → CLOSE
(`development-workflow.md`). This command runs the phases up to PLAN on the feature's own branch and
task folder. **It writes no code: `j-cvm-exec-plan` executes the plan.** The task's file is
`{@tasks}/NN-<feature>/notes.md`.

## Steps

### 1. Clean State
- `git status` — check for uncommitted changes.
- If changes exist:
  - **Review what will be committed** — no sensitive files (.env, credentials)?
  - If something unexpected → ask the user before committing.
  - On `{@main-branch}` or `{@dev-branch}`: no WIP commit on a shared branch. They stay uncommitted through
    step 2, and step 3 commits them on the new branch.
  - On any other branch: `git add . && git commit -m "WIP: save before new feature"`, then `git push`.

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
- Ask with AskUserQuestion: "What do you want to call this feature? (short, like: login-social,
  dark-mode)", then confirm:
  ```
  I'll create:
  - Branch: feature/NN-{name}
  - Folder: {@tasks}/NN-{name}/
  ```
- On confirmation:
  ```bash
  git checkout -b feature/NN-feature-name
  mkdir -p {@tasks}/NN-feature-name
  git push -u origin feature/NN-feature-name
  ```
  What step 1 left uncommitted on a shared branch is committed here, reviewed as step 1 says:
  `git add . && git commit -m "WIP: save before new feature"`.
  **IMPORTANT:** push the branch immediately, so the user can see it on the remote.

### 4. Notes
Create `{@tasks}/NN-feature-name/notes.md`:
```markdown
# Feature: NN-feature-name

## Requirements
<!-- LISTEN: what the user says -->

## Analysis
<!-- ANALYZE -->

## Inventory — capabilities and where they already live
<!-- INVENTORY -->

## Code Organization
<!-- PROPOSE -->

## Status
- [ ] Requirements gathered
- [ ] Code analyzed
- [ ] Inventory done
- [ ] Organization approved
- [ ] Plan reviewed
- [ ] Development done (j-cvm-exec-plan)
- [ ] Closed (j-close)
```

### 5. LISTEN
**Update MB** in `activeContext.md`:
```
@state::LISTEN
@feature::NN-feature-name
@branch::feature/NN-feature-name
```
Say:
```
Ready!
Branch: feature/NN-feature-name
Folder: {@tasks}/NN-feature-name/

Now TELL ME what you need. I will listen and do nothing until you say "done".
You can tell me:
- What this feature should do
- How it should work
- What you see in your mind

Go!
```
Write what the user says under `## Requirements`, as they speak. No code is read and nothing is
proposed.

### 6. ANALYZE — when the user says "done"
**Update MB:** `@state::ANALYZE` · **notes.md:** "Requirements gathered" done.

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
**A project with a black-box map.** `{@tasks}/bbc/BBC-MAP.md` exists → the project is designed as
black boxes (`${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md`): read its `## Decisions` and the definition
(`{@tasks}/bbc/bb/BB<N>-<name>.md`) of every BB the work touches, and write them under `## Analysis`.
The code of this feature goes in its BB's namespace and reaches another BB through the Core's contract,
never its implementation. A change of a contract, of a boundary or of a decision is not made here:
STOP, `/bbc-refactor`.

Then:
1. **Context**: the Memory Bank's activeContext and progress; `git log --oneline -10` (the patterns
   established recently); the architecture documents when they exist (CLAUDE.md, architecture.md); the
   versions of the libraries the feature uses; the notes of the previous task when this continues it.
2. The code the feature touches, with code navigation; the running application through ChromeDevTools
   when the feature is in the frontend.
3. `## Analysis` in `notes.md`.

### 7. INVENTORY
**Update MB:** `@state::INVENTORY` · **notes.md:** "Code analyzed" done.

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
is this what we reuse? The plan then executes it without re-deciding it, and j-review-plan
refuses a plan whose block rewrites a capability this section had already located.
```
A capability the framework or a library already provides is a capability the project already depends
on: it is read there before anything gets written.

### 8. PROPOSE
**Update MB:** `@state::PROPOSE` · **notes.md:** "Inventory done" done.

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
With a black-box map (step 6), `## Code Organization` names the BB that owns each part and the
contracts used, as the map writes them.

Present the solution with both sections of `notes.md`, and ask with AskUserQuestion:
- `## Inventory — capabilities and where they already live` — for each capability, what already does
  it and where, what gets written because nothing covers it, with the search that came back empty:
  **is this what we reuse?**
- `## Code Organization` — what is shared and which library owns it, the contracts the consumers
  depend on, what this feature does not own, the mechanism with its reason: **is this organization
  right?**

The plan executes both decisions without re-deciding them: this is the last point where changing
either is free.

### 9. PLAN — when the user approves
**Update MB:** `@state::PLAN` · **notes.md:** "Organization approved" done.

**Re-read the rules the plan's code is written against**, even if ANALYZE read them:
`mind-sets/principles.md`, `code-principles.md`, `testing-principles.md`, the branches of
`@mindsets-branches` and the overlay files of `@mindsets-overlay` (one set per component when
`j-settings.md` has `-<component>` keys). The plan designs the code, and the planner needs them in
context while it does.

The type: `@backend-method` is the project's default; the user's explicit request in this session
wins.

**TDDAB — the methodology read is a HARD GATE, in this order:**
- **a. Read in full** `mind-sets/tddab-planner.md` and the language's `overlays/<language>/tddab.md`.
  TDDAB v2 is not generic TDD — bottom-up decomposition, RED as the contract, reference code
  intentionally not compilable, no fixed test count: the rules live in those files.
- **b. Prove it**: under `## TDDAB Rules Applied` in `notes.md`, the 3-5 key rules this plan follows,
  in your own words — decomposition direction, what RED contains, what makes a block self-sufficient.
  If they cannot be written from what was just read, go back to a.
- **c. Only now** write `{@tasks}/NN-feature-name/plan.md` in the structure `tddab-planner.md` defines,
  and its path in the Memory Bank: `@plan::{@tasks}/NN-feature-name/plan.md`.

**Step — the same hard gate, on the other methodology:**
- **a. Read in full** `mind-sets/step-planner.md`: one concern per block, concrete actions, criteria
  that prove the work, preconditions in the intro.
- **b. Prove it**: 3-5 key rules in your own words, in `notes.md`.
- **c. Only now** write `{@tasks}/NN-feature-name/plan.md` in the structure that file defines, and its
  path in the Memory Bank: `@plan::{@tasks}/NN-feature-name/plan.md`.

Then `/j-review-plan`, as the planner requires: the plan is shown only once the review approves it.

### 10. Commit the phase's product
**notes.md:** "Plan reviewed" done — before the commit, so the commit carries it.
```bash
git add {@tasks}/NN-feature-name/notes.md {@tasks}/NN-feature-name/plan.md <any plan sub-files> memory-bank/activeContext.md
git commit -m "docs(NN-feature-name): plan (<tddab|step>, N blocks)"
git push origin feature/NN-feature-name
```
Only these files; other pending changes stay as they are, and the report names them.

### 11. STOP
```
✅ Plan created and reviewed: {@tasks}/NN-feature-name/plan.md ({N} blocks)

Next: /j-cvm-exec-plan {@tasks}/NN-feature-name/plan.md, then /j-close to merge.
```
**Start no code. The user triggers `j-cvm-exec-plan`.**

## Rules
- **LISTEN → ANALYZE → INVENTORY → PROPOSE → PLAN → STOP**, in this order.
- Do NOT read code during LISTEN; do NOT propose solutions during LISTEN.
- **Write what the user says to `notes.md`** as they speak.
- **Update the Memory Bank at every phase change.**
- **Ask with AskUserQuestion** whatever is not decided.
