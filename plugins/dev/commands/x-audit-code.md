---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "Audit the code of a project against the cards of mind-sets/audit.md, in one command, to the report — the folders to audit said by the user once (the product, not the proofs of concept or the base library), the map and the algorithmic facts computed on them, the description of every module, then the agent reads the map against the cards, writes the candidates, confirms or withdraws each one by reading only its places, and writes the report of the confirmed problems. On a project too large for one session it writes its own Step plans and executes them itself; run again after an interruption, it resumes. Works on a project not made with the set too, after /dev:j-setup. Use when the user says audit the code, controlla il codice, audit del design, code audit."
---

## Rules — obeyed at every step
- **One command, to the report.** This command executes its own plans here, as `j-cvm-exec-plan.md`
  drives the planexecutor, and goes on to the next step by itself; it stops only when a tool does not
  answer (the navigation tool, the CVM, the map's parser) or at the report. Run again after an
  interruption, it resumes: step 0 says where.
- **Nothing from memory.** Every claim is confirmed from code read in the session: the project's code
  with `@code-nav-local`, a dependency's code in the version the project references with
  `@code-nav-external` or in its source. What is known about a framework without reading it is not
  evidence.
- **Only what is confirmed enters the report.** A fact of the map says where to read, never a verdict;
  what reading withdraws goes in `audit/checked/`, with the case of the card it is.
- **The code is read where something points, and once.** The map and the facts are read whole; the
  code only at the places a candidate names, and the places of one module are opened in one pass for
  every candidate and every card they concern. A module is never read whole to see whether a card
  applies to it, and never read again for the next card.
- **The project's gate is not run here**: the user runs it.
- Nothing is written outside `audit/`. A secret found is cited by its file and line, never by its value;
  `.00-secrets/` is not opened.

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first: a project not made with the
  set is wired by it the same way).
- `@code-nav-local` is `lsai` or `vs-mcp`, and it answers: one outline or info query on a file of the
  project, its result quoted. Anything else — `grep`, absent, not ready — STOP: the audit confirms every
  claim through the navigation tool; propose `/dev:j-mcp-setup`.
- The CVM answers (`mcp__cvm__parsePlan` is available) — it runs the plans of a large project;
  otherwise propose `/dev:j-mcp-setup`, CVM. STOP.
- `${CLAUDE_PLUGIN_ROOT}/commands/j-cvm-exec-plan.md`, read in full: its steps 1-5 are how a plan of this command is
  executed, here, by this command.
- Read in full, if not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/audit.md` (the cards) and
  `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`.

## Steps

### 0. Where the audit stands
**`audit/scope.md` is missing → the scope first**: the second point of step 1, the question to the user
included, then back here. A map and a plan made before the user said the scope may be of folders that
are not audited; the tool removes them when the scope names other folders.

Then the first case that holds, in this order:
1. **A plan of the audit is under way** — the `sourceFile` of `.cvm/uplan.json` is
   `audit/plan-describe.md` or `audit/plan-verify.md`, that file exists, and that plan has block ids
   that are not in `.cvm/uplan-progress.json` → execute it to its end, as `j-cvm-exec-plan.md` steps 1-5 say (its
   completed blocks are skipped); then the step after that plan: the `facts` line of step 2 after the
   description, step 5 after the verification.
2. **The verification is under way** — `audit/candidates.md` has a candidate with `Status: to verify`,
   and `audit/map/` did not change since it was committed → step 4.
3. **The report is due** — `audit/candidates.md` has no candidate to verify, and there is no
   `audit/REPORT.md` newer than it → step 5.
4. Otherwise: step 1.

### 1. The scope and the map — the tool, deterministic
- The first time (no `audit/.tools/`): `bash ${CLAUDE_PLUGIN_ROOT}/audit/install.sh`.
- **What the audit examines is the user's to say, once**: `audit/scope.md`. When it is missing:
  `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py scope` lists the project's own roots (`@own-code-roots`) with the
  source files of each; ask with AskUserQuestion which folders are the product to audit, and wait —
  that key says where the navigation searches, so it also holds proofs of concept, the base library
  and tools, and a folder searched is not a folder judged: they are audited only when the user names
  them. Then `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py scope <folder>…` → `OK audit/scope.md: …`. When it
  exists: say its folders in one line and go on; the user changes them with the same command. The
  tool refuses the map without a scope, and leaves out what git ignores. When the scope names other
  folders than the map in `audit/map/` was made of, the command removes that map and what was made
  from it — the plans, the candidates — and says so: they are made again from here; the descriptions
  stay.
- `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py map` → `audit/map/`: the modules, their shape, the graph, the sibling
  modules, the algorithmic facts of the cards, the coverage. The tool runs itself with
  `audit/.tools/venv` when install.sh made it. It refuses, and leaves the map as it is, when its
  parser is missing; a map with no module is not one either: show the output, STOP.
- Read `coverage.md` in `audit/map/` and tell the user, in one line each, what was not examined and why.

### 2. The description — once, the only step that reads all the code
- `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py plan-describe` → `audit/plan-describe.md`: one block per group of
  modules, each group sized to be read in one sitting, then the architecture. Each module has its own
  file, `audit/describe/<module key>.md`; a module whose file carries the fingerprint of its files now
  — written by `audit.py mark-described` when its description was written or confirmed — is left out.
  A description folder of the earlier layout, one file per group, is split into those files once.
- When the plan holds only its architecture block and `architecture.md` exists in `audit/describe/`, the
  project is described: go on.
- When it holds a single describe block: its blocks are done here, in order, as its mission says.
- Otherwise: `mcp__cvm__parsePlan` with `audit/plan-describe.md` (invalid → show the errors, STOP);
  commit `audit/scope.md`, `audit/map/` and `audit/plan-describe.md`, by path; say the number of blocks and of modules;
  execute the plan here, as `j-cvm-exec-plan.md` steps 1-5 say. When it completes, go on.
- Described: `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py facts` — B1, the module edges against the layers the
  description found, and `capabilities.md` in `audit/map/`, every capability of every module. It runs
  `check-describe` first, and refuses while a module has no section, two, one in another file, or a
  fingerprint that is not current: `plan-describe` again.

### 3. The candidates — the agent reads the map
Read whole, in this order:
1. `architecture.md` in `audit/describe/`: the layers the project gave itself, and where its documents and
   the graph differ.
2. `modules.md`, `graph.md` (with its cycles) and `siblings.md`, in `audit/map/`.
3. `capabilities.md` in `audit/map/`: the same capability said with different words in two modules is one
   family (A1) — it is the reasoning this step does, the table does not.
4. `audit/map/facts/*.json`, the algorithmic facts: the duplicate checker's similar code, the symbols
   without callers, the fields of state written by several methods, the edges against the layers, the
   rest the cards name. A fact says where to look, never a verdict; a fact spread over hundreds of
   places points at no place — it is a hint for a family the map shows, or nothing.
5. What was withdrawn before: `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py checked` lists the withdrawn items of
   `audit/checked/`. A `valid` one, at the same places and for the same card, is not a candidate
   again; a `stale` one is judged again like anything else.

Then the cards, family by family — A to H, the branches I to N only when `@mindsets-branches` has
them, O the tests. For each card, its **At scale** line says how it is found on the whole project: the
searches are made on the whole project, targeted, with the map and the navigation tool — the calls to
the waiting APIs for H4, the classes two sibling modules both declare, the edge that goes against the
layers, the method one member of a family has and another lacks. What the map already shows is not
searched again.

Write `audit/candidates.md`, one section per candidate:
```
## <CARD>-<short-kebab-name> — <what is suspected, in one line>
- Cards: <the cards it concerns, the first one in its id>
- Places: <path:line>, <path:line>
- From: <what on the map or which fact points here; the query and its result>
- Status: to verify
```
and at its end, `## Nothing on the map`: one line per family of cards with no candidate, and why. A
candidate is what the map supports: a card with nothing pointing at it has none. Commit
`audit/candidates.md`, `audit/scope.md` and `audit/map/`, by path; show the candidates, grouped by family.

### 4. The verification — here, or a plan of its own
Group the candidates by the module of their places. What the verification opens is those places, with
what around them the cards' questions need.

**When it fits in this session**, with room to write what it finds: verify here, one group after the
other.

**When it does not**: write `audit/plan-verify.md`, a Step plan, after reading
`${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/step-planner.md` in full:
- one block per group of modules, listing its candidates by their id in `audit/candidates.md`; the
  groups as large as one sitting reads;
- the mission says what this step says — the rules above, the verification of a group below, the
  forms — and that each card is read in `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/audit.md` by its id: a block names
  its cards, it does not copy them;
- the block ids `NN-kebab-case`: NN two digits from `01` (after `99`, `01` again), and the slug carries
  this run's label, `r<yymmddhhmm>`, so that an id is not repeated inside the plan;
- no block writes the report: it is step 5's, written by this command.
Then `mcp__cvm__parsePlan` with it (invalid → correct it and parse again); commit it and
`audit/candidates.md`, by path; execute it here, as `j-cvm-exec-plan.md` steps 1-5 say. When it
completes: step 5.

**The verification of a group** — the same here and in a block:
1. The CODE-NAV PREFLIGHT block of `code-navigation.md`, filled, before the first lookup.
2. Each place opened once, with the navigation tool; for every candidate there, the questions of each
   of its cards, one at a time, with the code in hand, and the card's **Not a violation**.
3. Confirmed → `audit/findings/<group>.md`:
   ```
   ### <CARD> — <the problem, in one line>
   - Rule: <file and section of the rule, as the card quotes it>
   - Where: <path:line>, <path:line>
   - Evidence: <what was read, with the query and its result>
   - Gravity: grave | da correggere
   ```
   Withdrawn → `audit/checked/<group>.md`:
   ```
   ### <candidate id> — not a violation: <the case of the card it is>
   - Places: <path:line>, <path:line>
   ```
   the places read: `audit.py check` requires the line, and `audit.py checked` says from them whether
   the record still holds. A file with nothing to say holds the single line `none`.
4. Something a card describes, seen while reading and not a candidate (H2 is only found this way) →
   written like any other finding.
4b. A module's description found wrong while reading — it names a file, a symbol or a capability the
   code does not have → `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py unmark-described <module>`, and the report's
   `## Not examined` names the module: the next run describes it again.
5. `python3 ${CLAUDE_PLUGIN_ROOT}/audit/audit.py check <file>` on each file written → `OK <file>`.
6. Each candidate's `Status:` in `audit/candidates.md` → `confirmed (<findings file>)` or `withdrawn
   (<checked file>)`; committed with the two files, by path. The status is where the work resumes.

The gravity is the card's: `grave` when it already breaks a behaviour, or will at the next change of
the code around it; `da correggere` otherwise.

### 5. The report
Written here, by this command, when no candidate is `to verify`: `audit/REPORT.md`, from `audit/describe/`, `audit/findings/` and
`coverage.md` in `audit/map/`:
- `## The project`: the components and the architecture the project gave itself, the capabilities,
  the mechanisms;
- `## Problems`: every finding, the grave ones first, per family or module, each with its rule, where,
  the evidence and the command that takes it — `/dev:j-bug` for a grave one, `/dev:j-new-feature` otherwise;
- `## Not examined`: what `coverage.md` lists as not examined or not computed, with why, and the
  modules whose description was taken back (step 4, point 4b).

Commit `audit/`, by path, and show the report. The next run of this command starts from step 1: the
map is computed again, only what changed is described again, and the candidates are written again
from the new map, the withdrawn ones `audit.py checked` gives as `valid` left out.
