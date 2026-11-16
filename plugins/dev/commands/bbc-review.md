---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BBC — review the analysis: the black-box map against the requirements and the method — the boundaries, the contracts, the connections, the logic of the flows, the requirements and the decisions — with no code read; write what is wrong with where and why, and send it back to /dev:bbc-analyze, until the user approves the map; then propose the roadmap of the development — the Core of the contracts, the BBs (in parallel when the user wants), the integrations, the flows, the audit of the code — approved by the user and written in the map. Use after /dev:bbc-analyze, before working on the BBs, or when the user says bbc review, controlla la mappa, roadmap dei BB."
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session; its
  `productContext.md` says what the project around the map is.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md`.
- The map: `{@tasks}/bbc/BBC-MAP.md` and `{@tasks}/bbc/bb/` (missing → `/dev:bbc-analyze` first). Its
  `## Requirements` holds the requirements the map is reviewed against, written by `/dev:bbc-analyze`.

## Steps

### 1. Read the map
First the requirements: `## Requirements` of `BBC-MAP.md` (`bbc.md` §2), and `productContext.md` for
the project around them. A map without `## Requirements` → the first finding, critical: the analysis is
reviewed against requirements, and there are none written; `/dev:bbc-analyze` writes them.

Then `BBC-MAP.md` with its `## Decisions`, every `bb/BB<N>-<name>.md`, every `diagrams/*.mmd`. No code
is read: the analysis is reviewed as an analysis (`bbc.md`, the steps of the method).

### 2. Check it — each finding with its evidence: the map's line, and the requirement's

**A. Boundaries** (`bbc.md` §1)
- A.1 one responsibility per BB: a description with an "and" is two; a BB with no responsibility of its
  own belongs in its neighbour.
- A.2 no cycle in the dependency graph.
- A.3 every dependency a flow uses is on the map, and every one on the map is used by a flow.
- A.4 a BB nobody depends on is an entry point, or it is unreachable.

**B. Contracts**
- B.1 every flow uses a contract as the map declares it — members, parameters, results, errors; two
  callers of one contract use it the same way (its result taken, its errors handled).
- B.2 every BB's contract serves the BBs that use it — every member a flow needs is there, with the
  results and the errors the flow handles — and every BB it depends on is on the map, with the contract
  it uses.

**C. Connections**
- C.1 every BB is reachable from an entry point.
- C.2 every flow reaches its result, with no missing step.
- C.3 every event a BB raises has its handler, in the BB that owns the reaction.

**D. Logic of the flows**
- D.1 the steps of a flow come in an order whose preconditions hold.
- D.2 the states of an entity: every needed transition exists, none leads to an illegal state
  (`code-principles.md` 2.1).
- D.3 every error a step can raise is handled on a path the flow shows.
- D.4 an invariant a flow relies on holds even when a step fails half-way.

**E. Requirements and decisions**
- E.1 every requirement — each line of `## Requirements`, cited by its line — is carried by a BB, and a
  flow shows it.
- E.2 every BB, dependency and mechanism serves a requirement, a line of `## Requirements`: what serves
  none is complexity nobody asked for.
- E.3 every decision of `## Decisions` is applied in the BBs and the contracts it governs, and none
  contradicts another.

Severity: **critical** — the system would not work or could not be worked on (a cycle, a contract a flow
cannot use, an unhandled error path, a reachable illegal state, a requirement no BB carries);
**warning** — it may fail or mislead (a responsibility too broad, a mechanism nobody needs); **info** — a
suggestion.

### 3. Write the review
`{@tasks}/bbc/BBC-REVIEW-YYYY-MM-DD.md`: the counts by category and severity, then each finding — the
check, where (the map's line, the requirement), the evidence, what corrects it.

### 4. Each finding goes back to the analysis
Nothing stays open. Ask with AskUserQuestion, one finding at a time, critical first: corrected by
`/dev:bbc-analyze` (the default), or kept as it is, with the user's reason. The answer is written beside the
finding. When findings go to `/dev:bbc-analyze`, the report says so and STOPS after the commit: the map is
corrected there, and this review runs again on it.

### 5. The roadmap — once the user approves the map
When no finding is left to correct, propose the order of the development (`bbc.md`, the steps of the
method):
1. the Core of the contracts — every contract of the map in the Core, with its fake and its contract
   tests — `/dev:bbc-core`;
2. every BB to build or to complete: with the Core in place each depends only on contracts, so all of
   them can go at the same time — `/dev:bbc-work` per BB, each in its own worktree, or `/dev:bbc-plan` one at a
   time;
3. the integrations, in the order of the dependency graph — `/dev:bbc-integrate` with the BBs that meet;
4. the flows — `/dev:bbc-e2e`;
5. the code against the analysis — `/dev:bbc-audit`.
Show it with AskUserQuestion: approved, or what to change. The approved roadmap goes in `BBC-MAP.md`,
`## Roadmap`, each step with the BBs (or the flows) it covers, each with its own status (`bbc.md` §2). A map that already has
one: the steps already done stay, the rest is proposed again.

### 6. Commit
```bash
git add {@tasks}/bbc/
git commit -m "docs(bbc): review and roadmap YYYY-MM-DD"
```
Only these files; other pending changes stay as they are, and the report names them. As for
`/dev:bbc-analyze`, the map reaches the base before `/dev:bbc-work` delegates a BB from it.

## Rules
- **Against the requirements and the method**: no code is read; a finding cites the map's line and the
  requirement.
- **Critical only for what breaks the system** or stops the work.
- **Every finding has where it goes**, decided by the user: back to the analysis, or kept with a reason.
- **The roadmap is the user's**: proposed once the map is approved, approved before it is written.
