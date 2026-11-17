---
description: Close a feature or a bug and deploy (junior workflow). The CLOSE phase of development-workflow.md — verifies completion, reads the change against the mindsets, runs the final gate, merges as @merge-strategy says, optionally deploys, rotates the Memory Bank. Use when work is done, user says close, merge, chiudi, hotovo, or feature is ready for production.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md` and
  `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/development-workflow.md` (CLOSE).
- For step 3, re-read now: `mind-sets/principles.md`, `code-principles.md`, `testing-principles.md`,
  the branches of `@mindsets-branches` and the overlay files of `@mindsets-overlay` (one set per component
  when `j-settings.md` has `-<component>` keys) — the change is read against them.

## Steps

### 1. Verify Completion (use intelligence!)
**Update MB:** `@state::CLOSE`. The branch to close is the current one, `{branch}`
(`git branch --show-current`, the Memory Bank's `@branch`): `feature/NN-…` or `bugfix/NN-…`.

`git status`: uncommitted changes are committed now, on `{branch}`, with the Memory Bank —
reviewed first (no `.env`, credentials, API keys or large binaries; nothing unexpected, or ask) — so
that step 3 reads them.
The prefix follows the branch: `bugfix/` → `fix`, `feature/` → `feat`:
```bash
git add <the files of the work, by path> memory-bank/
git commit -m "<feat|fix>(NN-name): <what is left>"
```

Read MB, task folder (notes.md, plan.md, bug-notes.md), the execution's progress
(`.cvm/uplan-progress.json`: the blocks the planexecutor completed), and recent commits.

**Check if work is actually complete:**
- Are all planned items done?
- Were tests run? (check notes or recent output)
- Does the code look finished?

**If something seems incomplete or unclear:**
```
Before closing, I want to make sure everything is ready.

I noticed that: [what doesn't add up - e.g.: "the plan has 3 items but only 2 are marked done"]

Do you want to close anyway or complete the remaining items first?
```

**If everything looks good → proceed.**

NOTE: Don't rely only on `@state` in MB - it could be wrong. Use your intelligence to assess the actual situation.

### 2. Review Changes Summary
The base branch follows `@merge-strategy`: `gitflow` or `gitflow-simple` → `{@dev-branch}`; otherwise
`{@main-branch}`. Show user what will be closed and deployed:
```bash
git log {base-branch}..HEAD --oneline
git diff {base-branch}..HEAD --stat
```

```
Changes summary for this branch:

Commits: [number] commit(s)
Files changed: [list from diff --stat]

All of this will be merged into {base-branch} as @merge-strategy says.
```

This gives the junior a clear picture before proceeding.

### 3. The change, read against the mindsets
```bash
git diff {base-branch}..HEAD
```
Read the change against the files the prerequisites re-read — by reading it and with the project's
deterministic tools (`principles.md` §7), never with a grep or a count of your own. Before the merge,
the change is checked in particular against:
- `principles.md` 5.2 — no secret outside `.00-secrets/`, no secret value in configuration or code (the
  MCP keys 5.2 names aside);
- `principles.md` 4.3 — incoming data validated at the boundary, once;
- `branches/data.md`, `branches/api.md`, `branches/security.md` — when they are in `@mindsets-branches`.

Each issue is reported with the rule it breaks (file and section) and where. A violation → FIX before
proceeding (`/dev:j-bug` when it needs a diagnosis).

### 3b. Definition of Done Verification
Before proceeding to tests, verify the FULL feature DoD:
- [ ] **ALL plan blocks** completed by the planexecutor (`.cvm/uplan-progress.json`), each with its commit
- [ ] **Tests exist** for every new piece of functionality
- [ ] **No block skipped** — every block of the plan was executed, or descoped with the user's approval written in the task's notes

**If ANY gate fails → STOP. Tell user what's missing. Do NOT proceed.**

### 4. The final gate
Run `{@gate-final}` from `j-settings.md` — every component's lint, `@lint-astgrep`, `@test-slow`, each
frontend's build, `@test-e2e`, `@bench`, with no filter: this is the pre-merge barrier, where
regressions at a distance surface. What `@limitations` says does not run locally is named in the
report, not skipped in silence.
- Red → FIX before proceeding; the merge waits until it is green.

### 5. Nothing left uncommitted
`git status` is clean: step 1 committed the work. A change written after step 1 — a fix of step 3 or 4
— is committed as step 1 says, then goes back to step 3, so that it is read and gated before the
merge.

### 6. Push the Branch
**IMPORTANT:** Always push the branch BEFORE merging so user can review it on remote.
```bash
git push -u origin {branch}
```

### 7. Merge or Create PR

**Read `@merge-strategy` from j-settings.md:**

**In a worktree** — `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, as a
`/dev:bbc-work` opens it — the base branch is open in the main folder and `git checkout` of it is refused
there. With `direct` or `gitflow-simple` (`<base>` is `{@main-branch}` or `{@dev-branch}`), the merge is
done from the worktree instead of the steps below:
1. `git fetch origin` and `git merge origin/<base>` into `{branch}`, here; a conflict is shown and asked
   as below — whoever closes decides;
2. `{@gate-final}` again when the merge brought anything in;
3. step 9's rotation, committed on `{branch}`;
4. `git push origin HEAD:<base>` — a fast-forward of the base, since `{branch}` now contains it.
Then step 8 for `direct`; step 10 for `gitflow-simple`. With `pr` or `gitflow` the steps below hold
as they are. With every strategy, the worktree is removed once step 9 is pushed (step 9, point 7).

#### If `@merge-strategy: direct` — Merge locally and push main
```bash
git checkout {@main-branch}
git pull origin {@main-branch}
git merge {branch}
```

**If merge shows CONFLICT:** show the files in conflict (`git diff --name-only --diff-filter=U`) and ask with
AskUserQuestion: resolve them here, each file read on both sides, or leave them to the user. Resolved here → the merge
is committed and `{@gate-final}` runs again before the push. Left to the user → `git merge --abort`, and the work
stays on `{branch}`. STOP until it is decided.

**Push main:**
```bash
git push origin {@main-branch}
```

→ Continue to step 8 (Deploy).

#### If `@merge-strategy: pr` — Create Pull Request
```bash
gh pr create --base {@main-branch} --head {branch} \
  --title "<feat|fix>(NN-name): description" \
  --body "$(cat <<'EOF'
## Changes
- [list from notes.md]

## Testing
- [test results]
EOF
)"
```

If `gh` CLI is not available, show the URL:
```
Pull Request ready to create:

https://github.com/{owner}/{repo}/compare/{@main-branch}...{branch}

Title: <feat|fix>(NN-name): description
```

```
PR created! Link: [PR URL]

A reviewer will merge it. After merge:
- Deploy will happen via CI/CD (if configured)
- Or run /dev:j-deploy manually after merge

Branch: {branch} (kept for review)
```

→ Skip step 8 (Deploy). Go directly to step 9.

#### If `@merge-strategy: gitflow` — PR to develop
Features always target `@dev-branch` (develop), never main directly.
```bash
gh pr create --base {@dev-branch} --head {branch} \
  --title "<feat|fix>(NN-name): description" \
  --body "$(cat <<'EOF'
## Changes
- [list from notes.md]

## Testing
- [test results]
EOF
)"
```

If `gh` CLI is not available, show the URL:
```
Pull Request ready to create:

https://github.com/{owner}/{repo}/compare/{@dev-branch}...{branch}
```

```
PR created to {@dev-branch}! Link: [PR URL]

A reviewer will merge it into develop.
Release to main will happen through a release branch (managed by team lead).

Branch: {branch} (kept for review)
```

→ Skip step 8 (Deploy). Go directly to step 9.

#### If `@merge-strategy: gitflow-simple` — Direct merge to develop
Features merge directly to `@dev-branch` (develop).
```bash
git checkout {@dev-branch}
git pull origin {@dev-branch}
git merge {branch}
```

**If merge shows CONFLICT:** show the files in conflict (`git diff --name-only --diff-filter=U`) and ask with
AskUserQuestion: resolve them here, each file read on both sides, or leave them to the user. Resolved here → the merge
is committed and `{@gate-final}` runs again before the push. Left to the user → `git merge --abort`, and the work
stays on `{branch}`. STOP until it is decided.

```bash
git push origin {@dev-branch}
```

```
Feature merged into {@dev-branch}!

Deploy to production happens when develop is merged to main (managed by team lead).

Branch: {branch} (kept for review)
```

→ Skip step 8 (Deploy). Go directly to step 9.

### 8. Deploy (if not already done, only for @merge-strategy: direct)

#### 8a. Check if Already Deployed
Check if user already deployed manually with /dev:j-deploy:
- Check `progress.md` for the deploy already recorded (/dev:j-deploy step 7)
- Or ask user: "Have you already deployed with /dev:j-deploy?"

**If already deployed → skip to step 9**

If not deployed yet → continue:

**Update MB:** `@state::DEPLOY`

#### 8b. Run the deploy (delegate to /dev:j-deploy)

`@deploy-script` is "none" → nothing to deploy: continue to step 9, and nothing of /dev:j-deploy runs.

`@production-branch` set → nothing is deployed here: `/dev:j-release` sends it out through the CI/CD. Continue to step 9.

Read `${CLAUDE_PLUGIN_ROOT}/commands/j-deploy.md` and follow its **steps 3-6** EXACTLY (backup, execute deploy, verify/failure dialog with restore option, confirm success).

Notes for the /dev:j-close context:
- SKIP /dev:j-deploy steps 1-2 (branch check and final gate) — /dev:j-close already verified them in steps 1-4
- On SUCCESS → continue to step 9
- On FAILURE → follow /dev:j-deploy's failure dialog; keep `@state::DEPLOY` until resolved, do NOT continue to step 9

### 9. Update MB → IDLE + ROTATE closed work out (NO branch deletion)
**IMPORTANT:** Do NOT delete branches! User needs to see all branches on remote for control.

- **Update notes.md (or bug-notes.md):** mark "Closed (/dev:j-close)".
- **A black-box work** (`## BB scope` in its `notes.md`): its lines of `## Roadmap` in
  `{@tasks}/bbc/BBC-MAP.md` marked done, by the `Flow:` line of `notes.md` — the Core of a `/dev:bbc-core`, the BB of a `/dev:bbc-plan`,
  the BBs integrated by a `/dev:bbc-integrate`, the flows of a `/dev:bbc-e2e`; a `/dev:bbc-refactor` has none. A step
  is done when all of its lines are (`bbc.md` §2). The audit's line is `/dev:bbc-audit`'s to mark, not this
  command's.
- Update MB:
  - In `progress.md` → the closed task's lines move to `history.md` (the rotation below)
  - In `activeContext.md` → clear `@feature` or `@bug`, `@branch` and `@plan`; set `@state::IDLE`

**Then ROTATE. This is the step that keeps the Memory Bank from growing without bound.**
`memory-bank/README.md` already mandates `activeContext::Completed→history` and
`progress::ClearsOnNewTask`. Those are rules nothing executes unless you execute them HERE —
closing a feature is the moment "completed" becomes true. Skipped repeatedly, `activeContext.md`
and `progress.md` turn into an append-only log that is auto-loaded into every future session.

ROTATION RULE (obey verbatim):
1. **Move, never delete.** Every line you remove from `activeContext.md` / `progress.md` is
   APPENDED VERBATIM to `memory-bank/history.md` under a dated `## YYYY-MM-DD — <feature>`
   heading. `history.md` is write-only: it is never read at session start, so size there is free.
2. **What leaves:** the just-closed feature's blocks, its release notes, superseded "Prior"
   sections — anything whose work is finished.
3. **What stays:** the currently open feature, unresolved decisions, open blockers, live
   constraints (rules marked "NON toccare"/"BY DESIGN"), and the deferred backlog. When unsure
   whether a constraint is still live, it STAYS.
4. **Verify, do not assume.** After moving, check that each removed line exists in `history.md`:
   ```bash
   while IFS= read -r l; do [ -z "$l" ] && continue; \
     grep -qxF -- "$l" memory-bank/history.md || echo "LOST: $l"; \
   done < <(git diff -U0 memory-bank/activeContext.md memory-bank/progress.md \
            | grep '^-' | grep -v '^---' | sed 's/^-//')
   ```
   (`--` because a line that begins with `-`, as a checklist item of `progress.md` does, is otherwise
   read as an option.) Any `LOST:` line means you rewrote instead of moving — put it in `history.md` before continuing.
   **A hand-rewritten section is NOT covered by a check you ran on a scripted move.**
5. At the end of the day (`memory-bank/README.md`: `EndOfDay→archive/YYYY-MM-DD.md`), archive the
   day's dated sections of `history.md` into `memory-bank/archive/YYYY-MM-DD.md` — same
   move-never-delete rule.
6. Commit and push what this step wrote, on the branch you are on now (`{@main-branch}` or
   `{@dev-branch}` after a local merge, `{branch}` with a pull request). In a worktree this step runs
   before the push of step 7, on `{branch}`, so that the base receives the rotation with the work:
   ```bash
   git add memory-bank/ {@tasks}/NN-name/ <{@tasks}/bbc/BBC-MAP.md, for a black-box work>
   git commit -m "chore(NN-name): close"
   git push origin <the current branch>
   ```
7. **In a worktree**, with every strategy, once this is pushed: `git status --porcelain` is empty —
   anything there is shown and asked, nothing is lost — then, the main folder being the first line of
   `git worktree list`:
   ```bash
   git -C <main folder> worktree remove --force <worktree folder>
   ```
   `--force` because git refuses to remove a worktree that holds a submodule, as a project with the
   set has; with the status empty, what it removes are the ignored files — the links of `.claude/`,
   the folders of the MCP servers. The branch is kept, and the user closes this session.

### 10. Confirm

**If `@merge-strategy: direct`:**
```
Feature [name] completed and deployed!

Verify at: {@domain} (from j-settings.md)

Next time you want to work, use /dev:j-new-feature
```
With `@deploy-script: none`, nothing was deployed: it says "completed and merged", with no line to verify. With
`@production-branch` set, it says "completed and merged", and names `/dev:j-release`.

**If `@merge-strategy: pr`:**
```
Feature [name] — PR created!

PR: [link]
Branch: {branch} (kept for review)

After the PR is merged and deployed, use /dev:j-new-feature for the next task.
```

**If `@merge-strategy: gitflow` or `gitflow-simple`:**
```
Feature [name] — merged/PR'd to {@dev-branch}!

Deploy to production happens when develop is released to main (managed by team lead).

Next time you want to work, use /dev:j-new-feature
```

## Rules
- NEVER merge if the final gate is red
- NEVER deploy without testing
- NEVER delete branches (user needs them for review/control)
- ALWAYS push feature branch before merging
- Always update MB at the end
- ALWAYS rotate closed work into `history.md` (step 9) — move it, never delete it, then verify
