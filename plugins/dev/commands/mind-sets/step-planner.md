---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "Step Plan methodology - action-based sequential plans (removals, migrations, refactors) for work that is not test-first. The alternative to tddab-planner; /dev:j-review-plan validates both."
---

# Step Planner Mindset

## What is a Step Plan?
A **Step Plan** is for sequential operations that don't follow test-first methodology:
- **Removal**: retiring legacy code, deleting unused features
- **Migration**: moving data, changing schemas, switching providers
- **Cleanup**: refactoring config, removing dead dependencies
- **Infrastructure**: environment changes, deploy procedures

### Difference from TDDAB
```
TDDAB: Write tests FIRST → implement → verify tests pass
Step:  Execute actions → verify they did their work
```

Use TDDAB when building new functionality. Use Step Plan when the work is removing, moving, or reconfiguring — work no new test describes.

---

## Step Plan Format

### Required Tags

| Tag | Where | Purpose |
|-----|-------|---------|
| `<mission>` | Once, top of plan | Full project context (type auto-detected from blocks) |
| `<block id="NN-name">` | Wraps each step | Step boundary with unique id |
| `<intro>` | Inside block | Context: what, why, dependencies, preconditions |
| `<actions>` | Inside block | List of actions to execute (replaces `<red>` from TDDAB) |
| `<success>` | Inside block | Checklist that PROVES the block's work was done — all items must pass |

### Plan Template

```markdown
# Step Plan: [Feature Name]
**Date:** YYYY-MM-DD

<mission>
[Full project context — architecture, tech stack, what is being removed/migrated,
what must remain working.
Must contain enough information that ANY block can be executed on clean context.
Plan type (tddab or step) is auto-detected from blocks: all "- action:" → step.]

## Design principles — KISS, DRY and SOLID, one line each, transcribed from code-principles.md §1 and principles.md 2.1, 3.2

## Code rules — the rules this plan's code must obey, each with its source (file, section), transcribed from the mindsets j-settings.md names in @mindsets-branches and @mindsets-overlay, and from principles.md, code-principles.md, testing-principles.md

## Commands — the commands the blocks and the FINAL REVIEW run, written out
</mission>

<block id="01-short-name">
## Step 1: [Block Title]

<intro>
[What this step does. Preconditions (which steps must complete first).
Why this order matters. Files/dirs affected.]
</intro>

<actions>
- action: [first action to perform]
- action: [second action]
- action: [third action]
</actions>

If an action or a criterion fails, the cause is found with Protocol D — `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md`, read in full — before any change.

<success>
- [ ] [verifiable outcome — e.g., no references remain]
- [ ] [a block that touches code: the Gate, Block tests and Regression lines]
</success>
</block>

## Execution Order
01-short-name   → no dependencies
```

### Tag Rules
1. `<mission>` — EXACTLY once, plain tag (no attributes). Plan type is auto-detected: all `- action:` blocks → step
2. `<block id="">` — id format: `NN-kebab-case`, NN from `01` in every plan, in the order of the blocks, and unique across
   ALL the files of the plan. A plan does not go on from the numbers of the one before it
3. `<intro>` — MUST include preconditions if the step depends on prior steps
4. `<actions>` — each line starts with `- action:`, describes ONE concrete action. Can be file removal, config edit, command execution, etc.
5. `<success>` — checklist that **proves the work of THIS block was done**, in `- [ ]` format,
   all items must pass. Proof means the mechanism that fits the work: if the block analyses
   hundreds of files, the criterion shows they were analysed; if it produces an artifact, the
   criterion is the artifact; if it rewrites a rule, the criterion quotes the new text. A step
   plan has no universal gate like a TDDAB block's Gate and test lines, and that is deliberate —
   its work is the one no new test describes. The proof is chosen block by block; a block that
   touches code ends its success with the Gate, Block tests and Regression lines of
   `tddab-planner.md` ("The commands, by level"), the commands written out.
6. `<files>` — ONLY in index.md for multi-file plans (same as TDDAB)
7. The Protocol D line — after the actions of every block, outside the tags, as in the template:
   EXECUTE and FIX read the block from the plan file (their task points at its lines); in the success
   it would be checked as a criterion
8. `## Execution Order` — once, at the end of the plan file (in a multi-file plan, of `index.md`),
   one line per block with what it depends on, as in `tddab-planner.md` ("Execution Order Section");
   the mission does not carry it
9. Tags can span multiple lines
10. No nesting tags inside other tags (except all tags are inside `<block>`)
11. Standard markdown between tags is preserved for human reading
12. **A tag named in the text is written in backticks or without angle brackets**, anywhere in the plan file, as in `tddab-planner.md` (Tag Rule 10).

---

## Step Planning Rules

### 1. Information Self-Sufficiency
Same as TDDAB — each block must be understandable with ZERO context:
- Show FULL file paths
- Include exact commands to run
- Never reference "previous discussion"
- `<mission>` must contain the test/verification command

### 2. Action Clarity
Each `- action:` line must be a concrete, executable instruction:

```
CORRECT:
- action: Remove directory legacy_store/ entirely
- action: Delete the packages vectorstore and graphlib from the project's dependency file
- action: Run the package manager's restore to rebuild the lock file

WRONG:
- action: Clean up old stuff
- action: Fix the config
- action: Remove things that aren't needed
```

### 3. Verification Strategy
Every block needs at least one verification. Common patterns:

```
For code removal:
- [ ] the Block tests and Regression lines pass, with the same tests as before
- [ ] the project builds / type-checks clean (if a reference to the removed code were left
      anywhere, this fails — and it is complete in a way a text search is not: it sees
      re-exports, aliases and dynamic imports that no grep pattern catches)

For config changes:
- [ ] application starts without errors
- [ ] no references to old config values remain

For dependency removal:
- [ ] the package manager's restore completes without errors
- [ ] the removed packages are not in the lock file

For a schema change (branches/data.md 12-13):
- [ ] the migration is versioned, and runs on the version already in production
- [ ] the change follows expand → migrate → switch → contract, the contract step in a later release
```

### 4. Atomic Steps
Each step must be:
- **Complete** — the system works after this step
- **Rollback-able** — can revert with `git revert HEAD`
- **Ordered** — preconditions stated in `<intro>`
- **Verified** — has success criteria that prove it worked

### 5. No Mixing
A plan is EITHER tddab (`- test:`) OR step (`- action:`), never both. The parser does not refuse a
mixed plan — it reads it as TDDAB and gives its action blocks a RED — so `/dev:j-review-plan` does.

### 6. The Approved Organization Applies Here Too
An action plan executes the organization already approved — where the task has one, a feature
has it in the `## Code Organization` section of `notes.md` — just as a TDDAB plan does. A
removal, a migration or a refactor is exactly where local copies get left behind, and that part
holds even for a bugfix, which has no such section and is not asked for one.

- When an action moves or rewrites something the organization assigned to a shared library, the
  action points AT that library, by name and path, and leaves no local copy behind. Two copies
  of a thing that was supposed to be shared is the state this plan is meant to leave, not reach.
- Moving the shared part into the library that owns it comes BEFORE the actions that consume it.
  The consumers are then edited to take it from there, in a later step.

```
CORRECT:
- action: Move the retry policy from import/retry to core/retry
- action: Replace the local retry helpers in import/ and export/ with the one
          from core/retry, deleting both local copies

WRONG:
- action: Clean up the duplicated retry logic
  (which copy survives, and where does it live?)
```

**And the approved INVENTORY applies here too.** The phase between ANALYZE and PROPOSE left a
`## Inventory — capabilities and where they already live` section on `notes.md`: one line per capability,
with where it already lives or the search that came back empty. An action that writes a capability
that section had already located is an error, not a detail — and in a clean-up plan it is the
worst one, because the pass that was supposed to remove duplicates adds one. The planner does not
search: the search happened in INVENTORY and the user approved it. The planner transcribes it, by
naming the symbol and its path in the action, and by making the success criterion prove that the
consumer uses THAT one.

```
CORRECT:
- action: Point export/ at with_retry from core/retry — take it from there
          and delete the local backoff helper export/retry_utils
  success: - [ ] export/ uses with_retry from core/retry, and
                 export/retry_utils no longer exists

WRONG:
- action: Give export/ a retry mechanism
  (it already exists one directory away, and this action will write a second one)
```

---

## Shared Capability Registry — in the mission

**The mission is the only text EVERY block receives** (at its EXECUTE). A block does not read another block's
intro, so a capability declared only there gets rewritten by the next action that needs it. The
same registry a TDDAB plan carries (see `mind-sets/tddab-planner.md`) belongs in a step plan's
mission, one line per capability that more than one block touches:

```markdown
## Shared Capabilities
| Capability (what it does) | Owner (path + symbol) | Consumed by |
|---|---|---|
| Retry with exponential backoff | core/retry: with_retry — EXISTS (inventory) | import/, export/ |
```

For actions instead of tests, the consequence is the one rule 6 already states: the action
**names the symbol and its path** and the success criterion **proves the consumer uses that
one**. An action that writes a second implementation of a row contradicts the mission, not
another block.

It is bounded by the plan — the capabilities this plan moves, shares or consumes, not an
inventory of the repository — so it stays a few rows whatever the size of the codebase. The rows
that point outside the plan come from the approved `## Inventory — capabilities and where they already live`
of `notes.md`: the planner transcribes, it does not search again.

---

## Design principles — in the mission

Every mission carries a `## Design principles` section: KISS, DRY and the five SOLID principles
(SRP, OCP, LSP, ISP, DIP), one line each, transcribed from `code-principles.md` §1 (and principles 2.1
and 3.2 for capabilities and the base) and adapted to what this plan does. In a step plan they apply to the code the actions write
or move: a migration that moves a type keeps one owner for it (DRY, SRP), a removal does not leave
a caller testing the subtypes of what it receives (LSP). The mission is the only shared text the
executor of a block reads, so the principles are the ones written there. A principle the plan has no use
for says so in its line; it is not dropped.

## Code rules — in the mission

The same section a TDDAB mission carries (see `mind-sets/tddab-planner.md`, "Code rules — in the
mission"), applied to the code the actions write or move. The planner writes those actions against
the mindsets — `principles.md`, `code-principles.md`, `testing-principles.md`, and the branches and
overlay files `j-settings.md` names in `@mindsets-branches` and `@mindsets-overlay` — and transcribes
into the mission, each with its source, the rules that code must obey:

```markdown
## Code rules
- A closed set of values is an enum, never strings or loose constants — code-principles.md 3.3
- No error is swallowed; the domain reports codes, the boundary translates them — principles.md 4.1, 4.2
- Logs go through the structured logger; the console is one of its sinks — code-principles.md 4.9
- The schema changes by expand, migrate, switch, contract — branches/data.md 13
```

A migration that moves a type carries the rules of what it moves; a removal that writes no code
says so in one line. The mission is the only shared text the executor of a block reads, so the rules are
the ones written there.

---

## Step Size Guidelines

### Ideal Step Size:
- **One concern per block**: the actions that succeed or fail together, and whose failure is
  diagnosable — if the block fails, it is clear which action did it
- **Scope**: single concern (one package, one config file, one dependency group)
- **Verification**: the criteria prove this block's work, and a block that touches code ends with
  the Gate, Block tests and Regression lines

### Too Large (Split It):
- Removes unrelated things in one step
- If step fails, unclear which action caused it
- Cannot rollback cleanly

### Too Small (Merge It):
- Single file deletion with no verification needed
- Config line removal that has no impact alone

---

## Who reads the plan

The CVM planexecutor executes a step plan one block at a time: EXECUTE, VERIFY, FIX until VERIFY
passes, the Memory Bank update, the commit with the message `chore: <the block's title>`, and after the last
block a FINAL REVIEW. The EXECUTE task carries the mission and the block's actions and points at the block's lines in the
plan file; FIX points at them too; VERIFY carries the success criteria — all in the same conversation. A plan never asks for a commit, a Memory Bank update or the whole suite, and the
block title is the commit message. Whoever executes a block has not seen the others: that is where the
format's demands come from — self-sufficient blocks, preconditions stated in the intro, no dependency
on a later block, the mission as the only briefing.

Before the user sees the plan, it goes through `/dev:j-review-plan`: the issues the review reports are
fixed in the plan and the plan is reviewed again, until the review approves it. Only then is it shown,
with the review's verdict.

---

## GOLDEN RULES OF STEP PLANS

1. **If actions are vague** → STOP, make them concrete
2. **If the criteria do not prove the work was done** → STOP, write criteria that do — «done» and «verified» prove nothing
3. **If an action writes a capability the approved inventory already located** → STOP, point the
   action at the existing symbol and its path, and let the success criterion prove the consumer
   uses that one
4. **If mixing test-first with actions** → STOP, split into two plans
5. **If step depends on another** → state it in `<intro>` as precondition
6. **If not atomic** → STOP, split the step
