---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Review a plan — TDDAB or Step — against its methodology, the project's mindsets and the real code, before the user sees it and before it runs (junior workflow). Use when the user says review plan, controlla il piano, skontroluj plan, or before executing a plan.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`, followed for every lookup of step 5: print its
  CODE-NAV PREFLIGHT block before the cross-check, and give no "does not exist" verdict without a
  quoted result of a ready tool (or a declared text-search fallback, flagged as lower confidence).
  The tools are `@code-nav-local` and `@code-nav-external` of `j-settings.md`.

## Steps

### 1. The plan
The path the user gave; otherwise `{@tasks}/NN-*/plan.md` or `index.md` of the current task;
otherwise ask with AskUserQuestion.

### 2. Its type — read from the plan itself
- lines `- test:` in `<red>` → **TDDAB plan**;
- lines `- action:` → **Step plan**;
- a `<files>` tag → a plan in several files: read `index.md` and every file, then type it the same way;
- both kinds of lines → a mixed plan: the first Structural Issue (the parser accepts it and reads it as
  TDDAB; the planners forbid it).

`@backend-method` is the project's default for writing a plan; the plan under review may be of the
other type, and its blocks decide.

### 3. What it is judged against — read in full
- **The methodology of its type**: TDDAB → `mind-sets/tddab-planner.md` and the language's
  `mind-sets/overlays/<language>/tddab.md`; Step → `mind-sets/step-planner.md`.
- **The rules of its code**: `mind-sets/principles.md`, `mind-sets/code-principles.md`,
  `mind-sets/testing-principles.md`, the branches named in `@mindsets-branches`, the overlay files
  named in `@mindsets-overlay` (one set per component when `j-settings.md` has `-<component>` keys).
- **The decisions it executes**, in the task's `notes.md`: `## Code Organization` and
  `## Inventory — capabilities and where they already live` (`development-workflow.md`, PROPOSE and
  INVENTORY).

These files are the only source of truth: no rule from memory, none stricter or looser than they
are.

### 4. The plan in itself
- **Structure**: every tag the planner requires, block ids unique in the plan and numbered from `01`, the mission with its
  `## Shared Capabilities` (every capability more than one block uses, with its owner and its
  consumers), `## Design principles` and `## Code rules` (each rule with its source), each block's
  Protocol D line, as the planner states them.
- **Order**: no block uses a type, a function or a file a later block creates; the execution order at
  the end of the plan names every block with its dependencies, in the order the blocks are written,
  and the mission says nothing about the plan.
- **Self-sufficiency**: each block executes with the mission and its own lines alone — the mission at
  its RED or EXECUTE, its lines at GREEN and FIX, its success at VERIFY; full paths; no "as discussed".
- **Completeness**, as the planner defines it: no TODO, no open decision, no "A or B"; a `...` that
  skips boilerplate is allowed, one that skips a decision is not.
- **Commands**, as the planner of its type asks them, each command written out and consistent with the
  `## Linting` and `## Tests — by level` keys of `j-settings.md`: the mission has `## Commands`; in a TDDAB plan each
  block's intro has its `Focused run:` and its success ends with the Gate, Block tests and Regression
  lines; in a Step plan a block that touches code ends with those three lines, and a block that does
  not proves its work as `step-planner.md` Tag Rule 5 says. No block asks for a commit, a Memory Bank update
  or the whole suite.
- **Conformity**: the code the blocks show obeys the rules read in step 3, each overlay section the
  block names included — the mechanism the platform provides used, not rewritten (principles 1.1).
  Every name and shape a block fixes in a contract is one the language's analyzers accept, as the
  overlay lists them: a refused one fails the gate of the block that writes it and is renamed in all
  the blocks after it.

### 5. The plan against the real code
Print the CODE-NAV PREFLIGHT block first, then, with `@code-nav-local`:

- **A. Existence** — every type, function or method the plan uses, calls, extends or injects and does
  not create: found, with the signature the plan expects (parameters, return type, namespace). Not
  found → **dependency error**, with the block id and the symbol. A base library that is a submodule
  is searched in its path (`@base-library`, part of `@own-code-roots`): `/dev:j-new-project` brings it in
  before the plan; one that is a package, with `@code-nav-external` — and when that is `none`, against
  the base library's README and sample application, read now, the review saying so.
- **B. Paths** — every file the plan edits or extends exists at that path. Missing → reported: the
  plan's layout does not match the project.
- **C. Reuse — a rewritten capability is BLOCKING** (principles 2.1): a capability is what the code
  does, not its name. For every capability a block delivers:
  1. the inventory of step 3 says it already lives somewhere (or, for a new project, that the base
     library or the platform provides it) and the block writes it anyway → **blocking**: the plan
     contradicts the decision it executes;
  2. it exists in the code — searched by what it does, not only by the name the plan gives it — and
     the block rewrites it → **blocking**, and the inventory is wrong too: say both.

  The fix is the planner's: the block names the existing symbol with its path, the RED uses that
  symbol and pins the result to its own (in a Step plan: the action names it, and the success proves
  the consumer uses it), and nothing new is written. A capability with no
  implementation anywhere passes: the point is to stop the second copy, never the first.
  A task with no inventory section → that is the first
  issue reported: back to the phase that writes it, not a patch of the plan.
- **C-bis. The approved organization** — reading `## Code Organization` and the plan:
  - every shared part has its block, in the project or library that owns it, at the named path, and
    that block comes before its consumers;
  - no block rewrites locally what the organization gave to a library — the base library's parts
    included (principles 3.2): the block names the package it takes it from;
  - the mechanism the organization chose (code principles §2) is the one the plan builds — the state
    machine with its states and transitions, the strategy behind one contract, the named pipeline —
    not a set of conditionals in its place;
  - nothing shared appears in the plan without being in the organization: if it must, the
    organization changes first, with the user.

  A feature or a new project without `## Code Organization` → the first issue reported, above
  everything else: back to PROPOSE.
- **D. Third-party APIs**, when `@code-nav-external` is set: every external call the plan makes, with
  that version's signature. A mismatch or a missing symbol → reported. `none` → skipped.

When `@code-nav-local` resolves to a text search, the cross-check is a best effort and the report
says so.

**A bugfix** (`bug-notes.md`, Protocol D) has no inventory and no `## Code Organization`, and is not
asked for them. What is checked instead: a fix that touches behaviour which already has an
implementation, or a part the organization gave to a library, points at it by name and path and does
not add a second path beside it.

### 6. The parser
`mcp__cvm__parsePlan` on the plan, when the tool is available: its errors are Structural Issues;
valid → "CVM parsePlan: valid". The parser refuses a line it cannot read with its line number.
The parser rewrites `.cvm/uplan.json`. While an execution of the plan is in progress
(`mcp__cvm__list_executions`), it is not run, and the report says so: the execution keeps the plan it
loaded, and a new file beneath it no longer matches what it executes.

### 7. Report
```
PLAN REVIEW — ISSUES FOUND

[Dependency / Ordering Errors]
- block id + what it uses from a later block

[Code Cross-Check Errors]
- block id + the symbol or path that does not exist, with the query that looked for it

[Rewritten Capabilities — BLOCKING]
- block id + the capability + where it already lives (path + symbol) + whether the inventory had it

[Organization Not Executed]
- the shared part, the mechanism or the library the plan does not follow

[Structural Issues]
[Completeness Issues]
[Rule Violations]
- block id + the rule (file, section) + what the block does instead

SUGGESTED FIXES:
1. …

Fix these before executing the plan with /dev:j-cvm-exec-plan.
```

```
PLAN REVIEW — APPROVED ✅
✓ Structure — ✓ Order — ✓ Self-sufficiency — ✓ Completeness
✓ Code cross-check: the symbols and paths it uses exist
✓ Reuse: no block rewrites a capability that already exists
✓ Organization: shared parts, owners and mechanism as approved
✓ Rules: the mindsets of j-settings.md
✓ CVM parsePlan: valid

Ready: /dev:j-cvm-exec-plan
```

### 8. Fixing the plan
Run by the one who wrote the plan, before showing it (the planners' "Who reads the plan"): fix the
plan and review it again, until the report is APPROVED; the user then sees the plan with the verdict.
Run on a plan the user already has: fix it on the user's word, then review it again.

## Rules
- **The files of step 3 are the only source of truth.**
- **Review the content, not only the form**: a plan that parses, carries every tag and orders its
  blocks right is still defective if a block rewrites a capability that exists, or writes code
  against a rule.
- **Strict on order and self-sufficiency**: the blocks execute one at a time on a clean context.
- **Against the real code, with the tools**: a symbol or a path exists or it does not, and the
  configured tool answers it. A check invented on the source — a grep of one's own, a count — has no
  place here; the questions of step 5 are put to the navigation tool, and C-bis is a reading of two
  documents.
- **Every issue says why, and the fix is specific.** A good plan is approved quickly.
