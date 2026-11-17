---
description: "TDDAB v2 methodology - atomic test-first blocks, bottom-up decomposition, RED as the contract, and the commands each block carries. Single source for every plan executor; load together with the language overlay."
---

# TDDAB Planner Mindset

## What is TDDAB?
**Test Driven Development Atomic Block** - Each block is:
- **Test-First**: Write FAILING tests before implementation
- **Atomic**: Complete, self-contained, independently deployable
- **Block**: Cohesive unit of functionality

### The planexecutor runs the phases; the plan holds what they need

A plan is executed by the CVM planexecutor, one block at a time. It runs every block through its
phases — RED, GREEN, VERIFY, FIX until VERIFY passes, a check that every test the block lists exists,
the Memory Bank update, the commit with the message `feat: <the block's title>` — and after the last block
a FINAL REVIEW. Each phase's task says what to do and how wide to run the tests. The RED task carries
the mission, the block's intro and its tests, and points at the block's lines in the plan file; GREEN
and FIX point at those lines too; VERIFY carries the success criteria, the check of the tests carries
the tests. Every phase runs in the same conversation as the RED, where the mission was read. The plan holds what no phase knows:

- the mission: the project's context, `## Shared Capabilities`, `## Design principles`, `## Code rules`,
  `## Commands`;
- each block: the intro with its focused run, the tests, the reference code closed by the Protocol D
  line, and the success with its outcomes and its commands.

A plan never asks for a commit, a Memory Bank update or the whole suite: they are phases, and a block
that asks for one gets it twice or out of order. The block title is the commit message, so it says
what the block delivers.

### The commands, by level

`j-settings.md` holds the test commands by level (`## Tests — by level`): templates a plan fills with
the block's names, and global commands a plan copies as they are. Their form in each language is in
`overlays/<language>/tddab.md` §1.

| Where in the plan | What it runs | From `j-settings.md` |
|---|---|---|
| a block's intro, `Focused run:` | the tests the block writes — RED, GREEN and FIX run them | `@test-focused-<component>`, filled with the block's test project or file and its tests |
| a block's success | the gate of each component the block touches, the block's test projects, the fast regression | `@lint-<component>`, `@lint-astgrep`, `@test-block-<component>` filled, `@test-fast` |
| the mission's `## Commands` | the same gates and `@test-fast`, once: what the FINAL REVIEW runs | `@lint-*`, `@test-fast` |

**`@gate-final` is not in a plan.** The final gate — the slow tests, the end-to-end run, the builds,
the audit — takes minutes, and it judges a work that is finished: `/dev:j-close` runs it, once. A block,
and the FINAL REVIEW that closes an execution, run the fast commands above and nothing wider; a
feature built in steps (`/dev:j-step`) is executed once per step, and would pay the whole gate at each.

Every block's success ends with these three lines, each command written out in the form the
language's overlay gives (`overlays/<language>/tddab.md` §1):

```
- [ ] Gate: [the lint command of each component the block touches] · [`@lint-astgrep`] → exit 0
- [ ] Block tests: [the block command of each test project the block touches] → all pass
- [ ] Regression: [the fast run] → all pass
```

Every one of these commands stops at the first failure (`testing-principles.md` 6.3): the test
commands carry the runner's own option, as `j-settings.md` writes them, and a line that chains
commands chains them with `&&`. VERIFY stops at the first line that fails: it does not go on to count
what else is red.

A component the block does not touch has no command in them, and a key that is `none` has none. The
Gate commands come from `## Linting`, the other two from `## Tests — by level`. VERIFY's task says to
run the tests of what the block touches; the Regression line is a criterion of the success, and VERIFY
runs it as written.

---

## TDDAB Plan Format

### Required Tags

Plans use lightweight XML tags for machine-parseable structure.
Keep markdown readable — tags mark boundaries, not replace content.

| Tag | Where | Purpose |
|-----|-------|---------|
| `<mission>` | Once, top of plan | Full project context — enough that any block can execute on clean context |
| `<block id="NN-name">` | Wraps each TDDAB | Block boundary with unique id |
| `<intro>` | Inside block | Context: what, why, dependencies, files |
| `<red>` | Inside block | Test definitions (bullet list) |
| `<success>` | Inside block | Checklist of verifiable outcomes that must ALL pass |

### Plan Template

```markdown
# TDDAB Plan: [Feature Name]
**Date:** YYYY-MM-DD

<mission>
[Full project context — architecture, tech stack, patterns, conventions,
file structure, testing approach, build commands. Must contain enough
information that ANY block can be executed on a completely clean context
without prior knowledge. Think of it as the briefing document for a
developer who just walked into the project.]

## Design principles — KISS, DRY and SOLID, one line each, transcribed from code-principles.md §1 and principles.md 2.1, 3.2

## Code rules — the rules this plan's code must obey, each with its source (file, section), transcribed from the mindsets j-settings.md names in @mindsets-branches and @mindsets-overlay, and from principles.md, code-principles.md, testing-principles.md

## Commands — each component's gate and `@test-fast` from j-settings.md, written out; the FINAL REVIEW runs these, not `@gate-final`
</mission>

<block id="01-short-name">
## TDDAB-1: [Block Title]

<intro>
[What this block does. Dependencies on previous blocks.
Files to create/modify. Key decisions already made.
Focused run: [`@test-focused-<component>`, filled with this block's test project or file and tests].]
</intro>

<red>
- test: [first test that must fail then pass]
- test: [second test]
- test: [third test]
</red>

### Implementation
[Code in the target language showing types, signatures, key logic, test assertions.
Must be detailed enough that whoever executes the task can produce compilable code from it.
Does NOT need perfect imports or boilerplate — that is filled in while the task runs.
No TODOs, no unresolved decisions.]

If a test or a criterion fails, the cause is found with Protocol D — `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md`, read in full — before any change.

<success>
- [ ] [verifiable outcome of this block]
- [ ] Gate: [`@lint-<component>` of each component it touches, `@lint-astgrep`] → exit 0
- [ ] Block tests: [`@test-block-<component>`, filled] → all pass
- [ ] Regression: [`@test-fast`] → all pass
</success>
</block>

<block id="02-next-thing">
## TDDAB-2: [Next Block]
...same structure...
</block>

## Execution Order
01-short-name   → no dependencies
02-next-thing   → depends on 01
```

### The Protocol D line

Every block's `### Implementation` ends with the line of the template: «If a test or a criterion fails, the cause is found with Protocol D — `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md`, read in full — before any change.»
GREEN and FIX both read the block from the plan file — their task points at its lines — so this is
where the rule reaches whoever makes the tests pass and whoever repairs them. It is not a line of the
success, which VERIFY checks as a criterion, and not of the mission, which the FIX task does not
carry.

### Tag Rules
1. `<mission>` — EXACTLY once, before first block, must be comprehensive enough for clean-context execution
2. `<block id="">` — id format: `NN-kebab-case`, NN from `01` in every plan, in the order of the blocks, and unique across
   ALL the files of the plan. A plan does not go on from the numbers of the one before it
3. `<intro>` — MUST be self-sufficient (executable with zero prior context)
4. `<red>` — each line starts with `- test:`, describes ONE testable behavior. Must cover ALL cases: happy path, edge cases, error conditions, boundaries. No arbitrary limits on count.
5. `<success>` — checklist of verifiable outcomes (`- [ ]` format), ALL must pass: the block's own
   outcomes, then the Gate, Block tests and Regression lines with their commands written out ("The
   commands, by level"). `/dev:j-review-plan` flags a block whose success leaves them out or names a key
   instead of its command.
6. `<files>` — ONLY in index.md, signals multi-file mode (see Multi-File Plans below)
7. Tags can span multiple lines
8. No nesting tags inside other tags (except all tags are inside `<block>`)
9. Standard markdown between tags is preserved for human reading
10. **A tag named in the text is written in backticks or without angle brackets** ("the mission tag", "the files list"), anywhere in the plan file: a tag written bare is a tag boundary to a parser that matches tags by name, and a reader cannot tell the mention from the tag either.

---

## WHAT A TDDAB PLAN IS NOT

### NEVER Include:
- Options or alternatives ("Should we A or B?")
- Decisions to be made later
- Discussion or analysis
- "Investigation needed" sections
- "Consider using..." phrases
- Multiple approaches

### NEVER Write:
```
// WRONG - This is discussion, not a plan
"Option A: Use library X"
"Option B: Build custom solution"

// WRONG - This is not executable
"Investigate if we need..."
"Consider whether..."
```

---

## TDDAB Planning Rules

### 1. Information Self-Sufficiency (CRITICAL!)
**Each TDDAB must be understandable with ZERO context:**
- Show FULL file paths, not relative references
- Write code in the target language with types, signatures, key logic, and test assertions
- Code is REFERENCE — detailed enough for whoever executes the task to produce compilable code, but does NOT need perfect imports or boilerplate
- Never reference "previous discussion" or "as we decided"
- Never use "..." to skip DECISIONS — but acceptable for standard boilerplate
- `<mission>` must contain enough project context that ANY block works on clean context

**Why:** the RED task of a block carries the mission and the block's part, the phases after it the block's part, and nothing a block says reaches another block's task. The `<mission>` is the only shared briefing — it must cover architecture, stack, patterns, commands. Compiling and verifying happen while the task is being executed, not while the plan is being written.

### 2. Preliminary Work Handling
**Merge non-testable setup into first TDDAB implementation:**
- Package additions → Part of TDDAB-1 implementation
- Configuration changes → Part of implementation phase
- File deletions → Part of implementation phase

**NEVER create separate "setup" or "preparation" blocks**

### 3. Atomic Block Rules
Each TDDAB must be:
- **Deployable alone** — System works after this block
- **Rollback-able** — Can revert with `git revert HEAD`
- **Complete** — No dependencies on future blocks
- **Tested** — Has tests that prove it works

### 4. RED = CONTRACT (CRITICAL!)
The `<red>` tests define the **interface contract** for the block — they specify WHAT the unit must do, not how the full feature works end-to-end.

```
CORRECT: RED tests for a Service block
- test: CreateOrder with valid items → returns Order with status Created
- test: CreateOrder with empty items → fails with the invalid-argument error
- test: CreateOrder stores the order once — the in-memory repository holds it and the unit of work
        committed once

WRONG: RED tests for the Service block that go through the endpoint
- test: POST /api/orders returns 201
- test: POST /api/orders with bad data returns 400
(These test the WHOLE stack, not the service: they are the RED of the endpoint's own block)
```

### 5. Bottom-Up Decomposition (CRITICAL!)

**The plan follows the organization already approved — it does not decide it again.** Where the
task has one — a feature has it in the `## Code Organization` section of `notes.md` — it says
what is shared, which library owns each shared part, the contract the consumers depend on, who
injects the implementation, and what this feature does NOT own. That decision was approved by
the user in PROPOSE; here it gets executed. A bugfix has no such section and is not asked for
one: what still holds for it is the rule just below —
do not reimplement locally what a shared library owns.

**And the plan executes the approved INVENTORY the same way** — the base library's part included,
when there is one: what it names as reused is used, not written. The phase between ANALYZE and
PROPOSE left a `## Inventory — capabilities and where they already live` section on `notes.md`: one line per
capability, with where it already lives or the search that came back empty. A block that creates a
capability that section had already located is an error — the same kind of error as a block that
depends on a later one, and just as fatal, because the result is two implementations that drift.
The planner does not search: the search happened in INVENTORY and the user approved it here. The
planner transcribes it.

**How the contract makes it inevitable.** Saying "use the existing one" in the intro is not
enough, because the tasks that execute a block show the mission (at RED) and that block only. The RED
does the work: it imports the existing symbol from its real path and exercises it through the new
consumer, and it pins the result to the existing implementation's own. A fresh copy then does not
pass the block's own contract.

```
WRONG — the capability exists, and the block writes it again
  <block id="03-import-job">
  <red>
  - test: the import job retries a failed batch with increasing delays
  </red>
  (the executor writes its own retry helper inside the import job; retry logic now
   lives in core/retry AND in import/, and the two will drift)

CORRECT — the inventory said: "retry with backoff → core/retry: with_retry"
  <block id="03-import-job">
  <intro>
  Capability: retry with backoff. Already implemented — with_retry in
  core/retry (inventory approved in PROPOSE). This block does NOT rewrite it:
  it wraps the import batch call with it.
  </intro>
  <red>
  - test: import_batch is wrapped by with_retry from core/retry — the test
          imports THAT symbol and asserts the job calls it
  - test: given the same failing sequence, the import job's delays are exactly those
          with_retry produces — no second backoff policy
  </red>
```

The second test is the one that closes the hole: even a hand-written helper would have to
reproduce the existing behaviour exactly, and at that point rewriting it buys nothing.

So a feature block does not reimplement locally what the organization assigned to a shared
library. It names the package it takes it from:

```
CORRECT:   Block 03 uses MoneyAmount from the core/money library (owner per Code Organization)
WRONG:     Block 03 defines its own MoneyAmount inside the feature folder
           (now there are two, and they will drift)
```

Features MUST be decomposed into blocks **bottom-up by layer**, not as one monolithic block per endpoint/feature.

```
CORRECT decomposition for "Add Order endpoint":
  Block 01: Order model + validation       (unit tests)
  Block 02: OrderService business logic     (unit tests, in-memory fakes of the repository and the unit of work)
  Block 03: Order persistence               (integration tests on the real database engine)
  Block 04: Order endpoint                  (API tests through the real transport, on the real database)

WRONG — one block for entire endpoint:
  Block 01: Complete Order endpoint          (6 API tests)
  (This is NOT atomic, NOT testable in isolation, NOT rollback-safe)
```

**Why bottom-up?**
- Each block tests ONE responsibility in isolation
- If Block 02 fails, you know the problem is in the service, not the model or controller
- Each block is genuinely atomic — revert one without breaking others

**Decomposition strategy:**
0. **Shared libraries first** — the contracts AND their implementation, inside the library that
   owns them per the Code Organization. They come first because nothing can depend on something
   that does not exist yet, and because what gets written here gets written once, for every
   consumer that follows.
1. **Data/Model** — entities, value objects, the shapes of composite data (code-principles.md 3.2), validation rules
2. **Logic/Service** — business rules, orchestration (doubles of the contracts it uses, testing-principles.md 4.2)
3. **Persistence** — mapping, queries, migrations (integration tests on the real storage)
4. **Interface** — endpoint/CLI (tests through the real transport)
5. **Wiring** — DI registration, configuration (final block if needed)

**If two blocks turn out to need the same thing,** while you are still writing the plan, that
thing becomes a shared-library block placed before both of them. It does not become two
implementations to be unified later: later never comes, and by then each one has consumers.

**The plan builds the mechanism the analysis chose.** The Code Organization names it — a state
machine, a strategy behind one contract, a named pipeline, invariants at construction, rules as
data (the catalogue is in `mind-sets/code-principles.md` §2). The blocks build THAT:

```
CORRECT:   Block 01: OrderState closed type + transition(state, event) → state | NotAllowed
                     (the states, events and transitions from the notes.md diagram)
           Block 02: OrderService calls transition, and cannot express an illegal move

WRONG:     Block 01: Order with isPaid, isShipped, wasCancelled booleans
           Block 02: OrderService with the rules spread across ifs
           (behaves similarly today, and is not the mechanism that was approved)
```

The tasks that execute a block show the mission (at RED) and that block only. A mechanism named in the
plan becomes a type; a mechanism left out gets improvised as conditionals.

---

## TDDAB Size Guidelines

### Ideal TDDAB Size:
- **Tests**: ALL necessary — happy path, edge cases, error conditions, boundary values. No fixed number. A simple validator may need 2 tests, a complex service may need 15. Cover ALL edge cases.
- **Scope**: single layer or single responsibility — that is the criterion. How many files a block touches and how many lines it adds are not criteria: a block that renames one symbol across six files is one responsibility, and a block that adds two unrelated behaviours to one file is two

### Too Large (Split It):
- Multiple unrelated features
- Can't deploy independently
- Spans multiple layers (model + service + controller in ONE block)
- Tests at a level other than its layer's (testing-principles.md 3.4)

### Too Small (Merge It):
- Just config changes, with nothing that can fail on its own. The number of tests is not a criterion:
  a block with one test that can fail on its own is a block.

---

## TDDAB Naming Convention

```
<block id="NN-kebab-case-name">
## TDDAB-N: [Verb] [Feature] [Context]
```

Examples:
```
<block id="01-add-auth-config">
## TDDAB-1: Add Authentication Configuration

<block id="02-replace-jwt-oauth">
## TDDAB-2: Replace JWT with OAuth Provider

<block id="03-update-claims-logic">
## TDDAB-3: Update Claims Extraction Logic
```

id matches the block number and a short descriptive slug.

---

## Execution Order Section

The execution order is the review's check that the blocks are in order: it is written once, at the
end of the plan after the last block (in a multi-file plan, at the end of `index.md`), one line per
block with what it depends on, and the order of `<files>` is the same order. The mission does not
carry it: the mission is the objective of the work and what a block needs to do it, nothing about the
plan — its blocks, their order, how it is reviewed.

```markdown
## Execution Order
01-first-thing    → no dependencies
02-second-thing   → depends on 01
03-third-thing    → depends on 01, 02
04-fourth-thing   → depends on 01
```

---

## Shared Capability Registry — in the mission

**The mission is the only text EVERY block receives** (at its RED). A block does not read another block's
intro, so a capability declared only there gets rewritten by the next block that needs it — and
the plan that does it will say it isn't: a block whose intro says «does NOT re-implement any
normalization» writes its own whitespace collapse when the shared normalization is declared only in
another block's intro.

So every capability that **more than one block** uses goes in the mission, one line each:

```markdown
## Shared Capabilities
| Capability (what it does) | Owner (path + symbol) | Consumed by |
|---|---|---|
| Retry with exponential backoff | core/retry: with_retry — EXISTS (inventory) | import/, export/ |
| Normalise a title for comparison | core/text: fold — NEW | titles/, search/ |
```

Three things it is not:

- **Not an inventory of the repository.** It is bounded by the plan: only the capabilities this
  plan creates and passes between its own blocks, plus those it takes from outside. A ten-block
  plan has two to five rows, whatever the size of the codebase — nobody lists a 100k-line
  project, and nobody is asked to.
- **Not a new search.** The rows that point outside the plan come from the approved
  `## Inventory — capabilities and where they already live` of `notes.md`: the planner transcribes what
  PROPOSE approved, it does not look again.
- **Not advice.** A block that writes a second implementation of a row contradicts the mission —
  the text it was handed — and not another block it never read. That is the whole point of
  putting it here.

---

## Design principles — in the mission

Every mission carries a `## Design principles` section: KISS, DRY and the five SOLID principles
(SRP, OCP, LSP, ISP, DIP), one line each, transcribed from `code-principles.md` §1 (and principles 2.1
and 3.2 for capabilities and the base) and adapted to what this plan builds — "OCP: a new language is one more entry in
`EXTRACTORS`; the pipeline is not edited", not the principle's textbook definition. The reason is
the same as the registry's: the mission is the only shared text the executor of a block reads, so the
principles it writes code with are the ones written there. A principle the plan has no use for
says so in its line; it is not dropped.

## Code rules — in the mission

The planner designs the code of every block against the mindsets — `principles.md`,
`code-principles.md`, `testing-principles.md`, and the branches and overlay files `j-settings.md` names
in `@mindsets-branches` and `@mindsets-overlay` — and the reference code in the plan
obeys them: a reference that keeps a status in a string, swallows an error or builds its test
objects inline teaches the executor the defect it is supposed to avoid. The mission then carries a
`## Code rules` section with the rules the blocks of THIS plan must obey, each with its source:

```markdown
## Code rules
- A closed set of values is an enum, never strings or loose constants — code-principles.md 3.3
- No error is swallowed; the domain reports codes, the boundary translates them — principles.md 4.1, 4.2
- Logs go through the structured logger; the console is one of its sinks — code-principles.md 4.9
- Test objects come from the builders and doubles the tests share — testing-principles.md 5.1, 4.2
- Test names follow the convention of the language's overlay — overlays/<language>/testing.md (the one `@mindsets-overlay` names), transcribed
```

The rules are chosen for what the blocks write — a plan with no tests carries no test rules, a
plan that adds an endpoint carries the error and validation rules — and they are transcribed, not
named: the mission is the only shared text the executor of a block reads, and a rule that is only pointed
at is not obeyed.

---

## TDDAB Quality Checklist

For each block, verify:
- [ ] Has unique `<block id="">`
- [ ] Has `<intro>` with full context
- [ ] Has `<red>` with testable behaviors
- [ ] Has `<success>` with its outcomes, then the Gate, Block tests and Regression lines with the commands written out
- [ ] Tests are written first and will fail
- [ ] Test objects come from builders, factories or fixtures the tests share (testing-principles.md 5.1); no arrangement copied from test to test
- [ ] Each layer's tests run at its level: logic with doubles of its contracts, data access on the real storage, the transport through the real transport (testing-principles.md §3)
- [ ] Implementation approach is clear (no TODOs, no unresolved decisions)
- [ ] The Implementation ends with the Protocol D line
- [ ] Block is atomic and deployable
- [ ] No decisions or options included
- [ ] File paths are exact
- [ ] Code shows types, signatures, key logic, assertions (compilability verified while the task runs)
- [ ] Can be rolled back independently
- [ ] No dependencies on future blocks
- [ ] Every capability used by more than one block is in the mission's `## Shared Capabilities`,
      and no block writes a second implementation of one
- [ ] The block states which capability it delivers, and where the approved inventory found it
      already implemented — a retry policy already living in a shared library gets wrapped around
      the second consumer, not written again. If the inventory found nothing, the block says so.
- [ ] The mission has `## Design principles`, transcribed from code-principles.md §1
- [ ] The mission has `## Code rules`: the rules of the project's mindsets that these blocks must obey, each with its source, and the reference code obeys them
- [ ] The mission has `## Commands`: each component's gate and `@test-fast`, written out — and not `@gate-final`, which is `/dev:j-close`'s
- [ ] No block asks for a commit, a Memory Bank update or the whole suite

---

## Multi-File Plans

For large plans, split into an **index.md** + multiple sub-files to avoid mission duplication.

### When to Split
- Plan exceeds ~300 lines or ~10 blocks
- Natural layer boundaries exist (models, services, API, UI)

### index.md Format
```markdown
# TDDAB Plan: [Feature Name]
**Date:** YYYY-MM-DD

<mission>
[Full project context — single source of truth]
</mission>

<files>
- 01-models.md
- 02-services.md
- 03-api.md
</files>

## Execution Order
01-order-entity   → no dependencies
...
```

### Sub-file Format (e.g., 01-models.md)
```markdown
# Models Layer

<block id="01-order-entity">
## TDDAB-1: Create Order Entity

<intro>
[Context for this block]
Focused run: [`@test-focused-<component>`, filled].
</intro>

<red>
- test: [first test]
</red>

### Implementation
[Reference code]

If a test or a criterion fails, the cause is found with Protocol D — `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md`, read in full — before any change.

<success>
- [ ] [verifiable outcome]
- [ ] Gate: [...] → exit 0
- [ ] Block tests: [...] → all pass
- [ ] Regression: [...] → all pass
</success>
</block>
```
Every block of a sub-file has the structure of the block of the Plan Template.

### Multi-File Rules
1. `<mission>` in index.md is **authoritative**. `<mission>` in sub-files is silently ignored.
2. `<files>` tag in index.md signals multi-file mode. One filename per line, prefixed with `- `.
3. Block IDs must be **globally unique** across all files.
4. File order in `<files>` = the execution order at the end of `index.md`.
5. Paths are relative to the directory where index.md lives.
6. No `<files>` tag + `<mission>` present = single-file plan (full backward compatibility).

---

## Who reads the plan

The CVM reads the format: `parsePlan` checks the tags, and the planexecutor hands out one task at a
time, each with what its phase needs. That is where the plan's discipline comes from — the mission
as the only briefing, self-sufficient blocks, no dependency on a later block, every test a block
lists a test that will exist in its test files, the commands written out.

Before the user sees the plan, it goes through `/dev:j-review-plan`: the issues the review reports are
fixed in the plan and the plan is reviewed again, until the review approves it. Only then is it shown,
with the review's verdict.

---

## GOLDEN RULES OF TDDAB

1. **If you write "Option A or B"** → STOP, make the decision first
2. **If you write "TODO"** → STOP, make the decision now
3. **If you use "..." to skip a decision** → STOP, resolve it ("..." for boilerplate is fine)
4. **If you write "investigate"** → STOP, do it now, then plan
5. **If tests aren't first** → STOP, restructure the block
6. **If it's not atomic** → STOP, split or merge blocks
7. **If there's no `<block>` tag** → STOP, add structure
8. **If a block asks for a commit, a Memory Bank update or the whole suite** → STOP, remove it: those are the planexecutor's phases
