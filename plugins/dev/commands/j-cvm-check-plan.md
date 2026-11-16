---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Validate a plan — TDDAB or Step — with the CVM parser. Shows the plan's type, its blocks and the validation errors with their lines. Use when the user says check plan, validate plan, controlla piano CVM.
---

# CVM Check Plan

Validate a plan file with the CVM `parsePlan` tool, the same parser the planexecutor reads.

## Prerequisites

The CVM MCP server answers: the tool `mcp__cvm__parsePlan` is available. When it is not, the CVM
server is not configured: run `/j-mcp-setup` and choose CVM, then come back. STOP.

## Steps

1. **The plan file**: the path the user gave; otherwise `index.md` (a plan in several files) or
   `plan.md` in the current task folder, `index.md` first; otherwise ask with AskUserQuestion.
2. **Parse it**: `mcp__cvm__parsePlan` with `filePath`, the path — not while an execution of the plan is in
   progress (`mcp__cvm__list_executions`): the parser rewrites `.cvm/uplan.json`, which the execution
   loaded, and the report says so. The parser decides the type from the blocks — `- test:` lines make a
   TDDAB plan, only `- action:` lines a Step plan (a mixed plan is read as TDDAB: `j-review-plan`
   refuses it) — and refuses a line it cannot read with its line number.
3. **Report**:
   - valid → the type, the number of blocks, their ids, and the `.cvm/uplan.json` written;
   - invalid → every error with its line;
   - when `.cvm/uplan-progress.json` exists, the blocks already completed.

```
Plan OK ✓ — TDDAB, 3 blocks
  01-greet
  02-farewell
  03-summary
Saved: .cvm/uplan.json
Progress: 1/3 completed (01-greet)
```

```
Plan INVALID ✗
  line 0: Missing <mission> tag
  line 17: Block "01-probe" has unparseable line in red: "- test @local-only: …"
```

## Notes
- `parsePlan` writes `.cvm/uplan.json` on every valid parse (the previous one is kept as `.bak`); the
  progress file is not touched.
- The structure of a plan — tags, line prefixes, phase names — is the planners' (`tddab-planner.md`,
  `step-planner.md`); this command checks it, `/j-review-plan` checks its content.
