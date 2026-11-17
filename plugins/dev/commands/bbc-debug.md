---
description: BBC — fix a bug that crosses several black boxes. The bug path of /dev:j-bug — LISTEN, DIAGNOSE with Protocol D, PLAN — with ISOLATE done on the map, the BBs' tests run leaves first, then the integration points; then STOPS, the user triggers /dev:j-cvm-exec-plan. Use when a failure spans several BBs and cannot be placed, or the user says bbc debug.
---

## Prerequisites
- `${CLAUDE_PLUGIN_ROOT}/commands/j-bug.md`, read in full: this command follows its steps by number.
- As `/dev:j-bug`: `junior.md`, `development-workflow.md`, `debug-protocol.md` (Protocol D), the Memory
  Bank, `j-settings.md`, `code-navigation.md`.
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md`.
- The map: `{@tasks}/bbc/BBC-MAP.md` (missing → `/dev:j-bug`: the method maps no existing code).

## Purpose
`/dev:j-bug`, with the map giving ISOLATE its order (`bbc.md` §5). Protocol D is the method and is not
changed. **It writes no fix: `/dev:j-cvm-exec-plan` executes the plan.**

## Steps

### 1-5. Up to LISTEN
`/dev:j-bug` steps 1-5: clean state, base branch, `bugfix/NN-<bug>` and its folder, `bug-notes.md`,
LISTEN. `bug-notes.md` carries one more line under its title — `Flow: bbc-debug, ISOLATE on
{@tasks}/bbc/BBC-MAP.md` — so that `/dev:j-continue` resumes it with the map.

### 6. DIAGNOSE — Protocol D, ISOLATE on the map
**Update MB:** `@state::DIAGNOSE`. `/dev:j-bug` step 6, with ISOLATE in this order, each step written
under `## Diagnosis`:
1. **The BBs the failure crosses**, from the map's flows — with the flow and its steps quoted.
2. **Their tests, leaves first**, in the order of the dependency graph, each with the command of its
   definition: the result of each run quoted. The first BB whose tests fail is where the cause is
   looked for — its failing test read as Protocol D's READ.
3. **Every BB green** → the integration points between them (`BBC-MAP.md`): both sides of each call
   read with code navigation — the arguments, the awaiting, the errors handled, the order.
4. **A wrapper failing over a green BB** → its protocol: serialization, authentication, routing.

Then HYPOTHESIZE and the question to the user, as `/dev:j-bug` step 6.

### 7. PLAN
`/dev:j-bug` step 7. The fix stays in the BB that owns the cause (`bbc.md` §3); a fix that changes a
contract is asked as `/dev:bbc-plan` step 8 asks it, and `/dev:bbc-integrate` follows the plan. The BB's
definition is updated by the plan's last block when its files, contract or known issues change.

### 8-9. Commit, STOP
`/dev:j-bug` steps 8-9.

## Rules
- **Protocol D always**; the map orders ISOLATE, it does not replace it.
- **Leaves first**: a hub is tested after the BBs it depends on.
- **All green means an integration point**, read on both sides.
