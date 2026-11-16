---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: BBC — integrate black boxes after one of them changed its contract or they were built apart. Every call between them is checked on both sides of the contract, and a TDDAB plan proves them wired together, real BB with real BB; the map's integration points are updated. Use when the roadmap says built BBs meet, after /dev:bbc-plan changed a contract, or when the user says bbc integrate, integra i BB, test tra i BB.
---

## Prerequisites
- `${CLAUDE_PLUGIN_ROOT}/commands/bbc-plan.md`, read in full — this command follows its steps by number — and,
  through it, `j-new-feature.md`.
- As `/dev:bbc-plan`: the Memory Bank, `j-settings.md`, `junior.md`, `development-workflow.md`, `bbc.md`;
  the map.
- `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`, followed for every lookup: print its CODE-NAV
  PREFLIGHT block before the first one.
- The BBs to integrate: the ones the user names, the ones the roadmap of `BBC-MAP.md` says meet now, or
  those `/dev:bbc-plan`'s STOP named after a contract changed. Each of them is built (its status in the
  map); a BB still to build is planned first, with `/dev:bbc-plan`.
- **The main folder**, not a worktree: the integration composes BBs developed apart, so it runs where
  they are all merged — the base, with the works of those BBs closed (`bbc.md` §3.5).

## Steps

### 1. The task
`/dev:bbc-plan` steps 1-4, the name `bb-integrate-<BBs>`, the line `Flow: /dev:bbc-integrate`; `## BB scope`
lists every BB named, with its files and contract.

### 2. The integration points — ANALYZE
**Update MB:** `@state::ANALYZE`, `@feature::NN-<name>`, `@branch::feature/NN-<name>` — this command
has no LISTEN, where `/dev:j-new-feature` writes the last two. From the map and the code, with code
navigation: every call from one of the BBs to another — caller (file:line), callee, the contract
between them; and where the composition root registers each BB, or that it does not yet. For each
call, on both sides:
- the arguments the caller passes are the ones the contract declares;
- the result is taken and used as declared, the asynchronous call awaited;
- every error the callee declares is handled where the caller can react;
- the calls come in the order the flow needs (`BBC-MAP.md`, the flows).
Write each point under `## Analysis`: matches, or what does not, with both lines quoted.

### 3. INVENTORY, PROPOSE
`/dev:bbc-plan` steps 7-8: the integration fixtures that already exist (the composition the tests start,
the database fixture), and the fix of every point that does not match — on the caller's side, or a
contract change asked as `/dev:bbc-plan` step 8 asks it.

### 4. PLAN — TDDAB
`/dev:bbc-plan` step 9, the scope being the BBs named and the composition root. The blocks:
- a BB not yet registered in the composition root is registered at the GREEN of the first
  integration test that needs it, that test being its RED (`bbc.md` §4.2);
- the integration tests of every point, real BB with real BB, wired as the composition root wires them,
  doubles only at the system's boundary (`bbc.md` §4.2), asserting what the integration produces — the
  state, the answer, the error that crosses — never that a call was made; a test of a point that
  already works is green at its first run (`bbc.md` §4);
- the fix of every point that does not match, its test first, on the caller's side or as the contract
  change PROPOSE decided — the code is written at GREEN;
- the last block writes the integration points in `BBC-MAP.md`, each with its test.

### 5. Commit, STOP
`/dev:bbc-plan` steps 10-11. Next: `/dev:j-cvm-exec-plan`, then `/dev:bbc-e2e` when a flow crosses these BBs and
has no end-to-end test.

## Rules
- **Both sides of every contract are read.**
- **Real BBs together**: a double of one of the BBs under integration is not an integration test.
- **Nothing assumed about a call**: each point is matched with the lines quoted.
