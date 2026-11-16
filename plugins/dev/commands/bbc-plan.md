---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: BBC — plan the development of one black box as a feature. From the BB's definition in the map — its responsibility, its contract, its dependencies — the phases of /dev:j-new-feature scoped to the BB write a TDDAB plan, the cases of the contract as the tests and the implementation behind it, the other BBs as the fakes of the Core, the Core's contract tests run against the real implementation; the plan is reviewed, then it STOPS and the user triggers /dev:j-cvm-exec-plan. Use when the user says bbc plan, sviluppa il BB, pianifica il BB, or names a black box of the roadmap to build.
---

## Prerequisites
1. Read the Memory Bank (skip the subdirectories) if not already done this session.
2. `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
3. If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`,
   `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md`, `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md` and
   `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/testing-principles.md`.
4. `${CLAUDE_PLUGIN_ROOT}/commands/j-new-feature.md`, read in full: this command follows its steps by number.
5. The map: `{@tasks}/bbc/BBC-MAP.md` (missing → `/dev:bbc-analyze` first) and the BB the user names —
   `{@tasks}/bbc/bb/BB<N>-<name>.md`. A BB not on the map → `/dev:bbc-analyze` updates the map first. The
   Core of the contracts is `/dev:bbc-core`'s.

## Purpose
`/dev:j-new-feature`'s phases, with the scope of one BB (`bbc.md` §3): the work reads and changes the BB's
files and uses every other BB through its contract. What it plans is the development of that BB,
against the Core (`bbc.md` §1.6). **It writes no code:
`/dev:j-cvm-exec-plan` executes the plan.** The task's file is `{@tasks}/NN-<name>/notes.md`.
`/dev:bbc-core`, `/dev:bbc-refactor`, `/dev:bbc-e2e`, `/dev:bbc-integrate` and `/dev:bbc-debug` follow these steps by number.

## Steps

### 1-3. Clean state, base branch, branch and folder
As `/dev:j-new-feature` steps 1-3: the uncommitted changes reviewed and committed, the base branch of
`@merge-strategy` pulled, the next `NN`, the name asked and confirmed — `bb<N>-<name>` —
`feature/NN-<name>` created and pushed, `{@tasks}/NN-<name>/`. In a worktree opened by
`/dev:bbc-work`, the branch and the folder already exist: these steps are skipped.

### 4. Notes
`{@tasks}/NN-<name>/notes.md` as `/dev:j-new-feature` step 4, with one more line under its title —
`Flow: /dev:bbc-plan`, or the name of the command that follows these steps (`/dev:bbc-core`, `/dev:bbc-refactor`,
`/dev:bbc-integrate`, `/dev:bbc-e2e`) — so that `/dev:j-continue` resumes the work with that command, and one more
section before `## Requirements`:
```markdown
## BB scope
- BB: BB<N>-<name> — {@tasks}/bbc/bb/BB<N>-<name>.md
- Status: built | to build
- Files: <the BB's files, from its definition — "none, to build" for a BB to build>
- Contract: <what it exposes, as the map writes it>
- Uses (through their contracts): <BB, contract>…
```
In a worktree opened by `/dev:bbc-work`, `notes.md` already holds
`## BB scope`: it is completed — the `Flow:` line added — not written again.

### 5. LISTEN
As `/dev:j-new-feature` step 5: **Update MB** `@state::LISTEN`, `@feature::NN-<name>`,
`@branch::feature/NN-<name>`. This command writes `## Requirements` itself, from the map, and shows it — "Develop BB<N>-<name>
behind its contract": its responsibility; every member of its contract with the cases it promises —
the normal path, the edge cases, the errors, the boundaries (`testing-principles.md` 2.2); the
contracts it uses. Then it asks what to add — a case the user knows is fragile, a member to leave out — and the user's
words are added. No code is read and nothing is proposed.

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

The BB's scope: the code read is the BB's files; of every BB it uses, the contract on the map, checked
against the code's declaration with code navigation — not its implementation (`bbc.md` §3.1).
`## Analysis` says what the work touches inside the BB, and which contracts it uses. For a BB already
built that this plan completes — a member added by `/dev:bbc-refactor`, a case left out — it also writes the
**coverage matrix**: one row per member of the contract, the cases it
promises, and the tests that already prove each — or "none":

```
| Member | Cases | Proved by |
|---|---|---|
| CreateAsync | created; duplicate → conflict; blank name → invalid | CreateAsync_New_…; none; none |
```

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
is this what we reuse? The plan then executes it without re-deciding it, and /dev:j-review-plan
refuses a plan whose block rewrites a capability this section had already located.
```

The search is NOT scoped to the BB (`bbc.md` §3.2): a capability found in another BB is reused through
that BB's contract, or moved to the BB that owns it — never copied into this one. The builders,
doubles and fixtures the tests already share are found here too (`testing-principles.md` 5.1, 4.2).

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

Besides the two sections, the proposal names **every change of a contract** — this BB's or another's —
with the BBs that use it (`bbc.md` §3.3), and asks with AskUserQuestion, change by change: **change
this contract?** A file outside the BB's scope that the work needs is asked the same way: enlarge the
BB, or the work belongs to another BB. The answers are written in `## Code Organization`.

### 9. PLAN — when the user approves
**Update MB:** `@state::PLAN` · **notes.md:** "Organization approved" done.

As `/dev:j-new-feature` step 9: the rules re-read, the planner's hard gate, `plan.md`, its path in the
Memory Bank, `/dev:j-review-plan` until approved. The plan of this command is TDDAB:
- blocks bottom-up, each one a member or a group of members of the contract; each RED names the cases
  of `## Requirements` it proves; the GREEN is the implementation, in the BB's namespace, behind the
  contract the Core declares; every other BB is the fake of its contract the Core provides. Its logic
  is tested with those fakes, its data access against the real storage (`bbc.md` §4.1). For a BB already
  built that this plan completes, every "none" of the coverage matrix becomes a test, a test green at its first run is the
  expected outcome, and what is missing is written at GREEN (`bbc.md` §4);
- the BB's contract tests, written by `/dev:bbc-core`, run against the real implementation, in the block of
  the members they prove: the fake and the BB keep the same contract;
- every block changes only the BB's files and those the user added in PROPOSE; the composition root
  is not one of them — `/dev:bbc-integrate` registers the BB there (`bbc.md` §4.2);
- the last block writes the BB's definition (`bb/BB<N>-<name>.md`: its files, its tests and the command
  that runs them, the status `built`) and, when a contract, a dependency or the status changed,
  `BBC-MAP.md` (`bbc.md` §3.4).

### 10-11. Commit, STOP
As `/dev:j-new-feature` steps 10-11. With a contract changed, the STOP also names `/dev:bbc-integrate` with
the BBs that use it, after the plan is executed.

## Rules
- **The BB's scope**: its files are read and changed; the other BBs through their contracts.
- **The search is never scoped**: a capability is implemented once, wherever it lives.
- **The contract is the requirement**: the cases it promises are the tests, case by case.
- **A contract changes only by the user's decision**, named with the BBs that use it.
- **Update the Memory Bank at every phase change.**
- **Ask with AskUserQuestion** whatever is not decided.
