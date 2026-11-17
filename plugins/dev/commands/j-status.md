---
description: Show current status (junior workflow). Shows branch, state, progress, and pending work. Use when the user asks where are we, what's the status, cosa manca, co sme robili, or wants a summary of current work.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## Steps

### 1. Gather Info
```bash
git branch --show-current
git status
git worktree list
```

### 2. Read from MB
- `activeContext.md` - current state, feature, branch
- `progress.md` - what's done

### 3. Read the project
- Its name and what it is: `productContext.md` of the Memory Bank
- Key settings from `j-settings.md`: the language, `@main-branch`, `@merge-strategy`

### 3b. Verify MB matches reality
Quick sanity check:
- Does current branch match `@branch` in MB?
- Does task folder exist if MB says feature in progress?

If mismatch → note it in output with ⚠️

### 4. Show Output
```
=== CURRENT STATUS ===

Project: [name] ([what it is])
Branch: [branch name]
Uncommitted changes: [yes/no]

CURRENT TASK:
[feature (@feature) or bug (@bug) name, or "none"]

[When `git worktree list` has more than one line:]
OPEN WORKTREES:
- [folder] — [branch]   (each one has its own session; this one is marked "here")

STATE:
[LISTEN/ANALYZE/INVENTORY/PROPOSE/PLAN/DIAGNOSE/DEVELOP/CLOSE/DEPLOY or IDLE]

[If mismatch found:]
⚠️ MB says branch X but you're on Y - run /dev:j-continue to sync

DONE:
- [list of completed items]

TODO:
- [list of remaining items]

LAST MB UPDATE:
[when was MB last updated]

=== AVAILABLE COMMANDS ===
/dev:j-continue  → continue working
/dev:j-save      → save and leave
/dev:j-close     → close the feature or the bug, and deploy
/dev:j-setup     → change project settings
/dev:j-help      → show all commands
```

## Rules
- This command is read-only, does not modify anything
- If MB is empty/outdated, suggest updating it
- If j-settings.md is missing, suggest running /dev:j-setup
