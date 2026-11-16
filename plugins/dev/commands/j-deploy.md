---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Deploy to production (junior workflow). The DEPLOY phase of development-workflow.md — runs the final gate, the backup, the deploy script, and verifies. Use when the user says deploy, metti in produzione, nasad, or push to production.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first): its `## Deploy` section.
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## When to Use
- **Standalone:** Deploy anytime you're on the right branch and code is ready (e.g., after manual merge, hotfix, or CI)
- **From /dev:j-close:** /dev:j-close step 8 delegates here (follows steps 3-6 of this file) — this file is the single source of truth for deploy logic
- **With `@production-branch` set:** the deploy is the CD's, through `/dev:j-release`. Running it here is an exception, on the user's explicit word, and it is said first; step 5's restore holds for a failed CD too

## Pre-check
- No uncommitted changes
- The final gate must be green

## Steps

### 1. Verify Before Deploy
```bash
git branch --show-current
git status
```
- Show current branch (so user knows what will be deployed)
- If uncommitted changes → "Commit first"
- `@deploy-script` is "none" → "No deploy script configured. Nothing to deploy. (To configure: /dev:j-setup
  → edit @deploy-script)" — STOP. Nothing runs before this check.
- **Update MB:** `@state::DEPLOY`

### 2. Run the final gate
```bash
{@gate-final}
```
- Red → FIX before deploying, DO NOT proceed. What `@limitations` says does not run locally is named
  in the report, not skipped in silence.

### 3. Backup (Pre-Deploy)
Check `@backup-script` in j-settings.md.

**If @backup-script is NOT "none":**
```
Running backup before deploy...
```
```bash
{@backup-script}
```
- Show output to user
- If backup FAILS → STOP, do not deploy
```
Backup failed. Deploy cancelled.
Error: [show error]

Fix the backup issue before retrying.
```

**If @backup-script is "none":**
```
No backup script configured. Proceeding with deploy.
   (To configure: /dev:j-setup → edit @backup-script)
```

### 4. Execute Deploy
```bash
{@deploy-script}
```

### 5. Verify Deploy / Handle Failure
- Check script output

**If deploy SUCCESS → go to step 6**

**If deploy FAILS:**

Check if `@restore-script` exists and is not "none":

**WITH restore available:**
```
Deploy failed. Error: [show error]

You have a backup ready. What do you want to do?

1. RESTORE
   → Run @restore-script to roll back to before the deploy

2. LET'S DEBUG
   → Debug the error together
```

**WITHOUT restore (no script configured):**
```
Deploy failed. Error: [show error]

No restore script configured.

What do you want to do?

1. STOP
   → Nothing else runs: the error above is what has to be read

2. LET'S DEBUG
   → Debug the error together
```

**If user chooses RESTORE (option 1 with restore):**
```bash
{@restore-script}
```
- Show output
- If restore succeeds:
```
Restore completed. Environment rolled back to before the deploy.

The code is still in the branch, you can retry anytime.
Use /dev:j-deploy to retry after fixing the issue.
```
- If restore fails:
```
Restore also failed. Error: [show error]

ACTION REQUIRED: production may be down.
1. Nothing else runs
2. BOTH errors above (deploy + restore) are what has to be read
```
STOP.

**If user chooses DEBUG (option 2):**
Continue debugging with user, with Protocol D (`${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol.md`).

### 6. Confirm Success
```
Deploy completed!

Verify at: {@domain} (from j-settings.md) — `/dev:j-e2e {@domain}` runs the end-to-end checklist there

If something doesn't work online, check:
- Application logs
- Service status
```

### 7. Update MB
If a feature/bug is active in MB (`@feature` or `@bug`), update:
- `activeContext.md` → note deploy completed
- `progress.md` → mark feature/bug as deployed

Then `@state` goes back to IDLE when no feature or bug is open, and to the task's phase otherwise
(from /dev:j-close: its step 9 sets it).

This ensures standalone deploys don't leave stale state in MB.

## Rules
- NEVER deploy if the final gate is red
- ALWAYS run backup if @backup-script is configured
- If backup fails → STOP, do not deploy
- Always verify the site works after deploy
- If deploy fails and restore available → offer restore first
