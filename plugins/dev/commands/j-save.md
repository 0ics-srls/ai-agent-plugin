---
description: Save and leave (junior workflow). Commits WIP, updates Memory Bank, pushes to remote. Use when the user says save, pause, stop, leave, I'm done for now, or wants to preserve progress before ending the session.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## Steps

### 1. Update Memory Bank
First, so that the commit carries it. Update `memory-bank/activeContext.md` with:
- Current state (the phase: LISTEN, ANALYZE, INVENTORY, PROPOSE, PLAN, DIAGNOSE, DEVELOP, CLOSE, DEPLOY,
  or IDLE)
- What we were doing
- What's left to do
- Any open issues

### 2. Commit Work
```bash
git status
git branch --show-current
```

**If nothing but the Memory Bank changed** → commit `memory-bank/` alone, go to step 3.

**If on `{@main-branch}` (or `{@dev-branch}`) with uncommitted changes** → do NOT commit WIP directly on a shared branch. Ask user:
```
You have uncommitted changes on {branch}. WIP commits should not go on shared branches.
1. Create a branch for them (wip/save-{date}) and commit there
2. Stash them, untracked files included (`git stash push -u -- . ':!memory-bank'`) — they stay local; the
   Memory Bank is committed alone, as above
3. Commit anyway (only if you are sure)
```

**Review what will be committed:**
- No sensitive files (.env, credentials, API keys)?
- No large binary files accidentally staged?
- Changes make sense for current work?

If something unexpected → ask user before proceeding.

```bash
git add .
git commit -m "WIP: [brief description of where we are]"
```

### 3. Push
```bash
git push origin [current-branch]
```

### 4. Confirm
```
Everything saved!

Branch: [name]
Commit: [message]
Pushed: yes

WHERE WE WERE:
[brief summary]

NEXT TIME:
Use /dev:j-continue to resume from here.

Bye!
```

## Rules
- Always push (so it's saved on remote too)
- Always update MB (so the agent remembers)
- Give clear summary
