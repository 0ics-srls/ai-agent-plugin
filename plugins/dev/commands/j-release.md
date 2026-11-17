---
description: Release what is on the main branch (junior workflow). Opens the pull request from the main branch to the production branch; its CI runs the final gate, and once merged — by itself or by hand, as /dev:j-ci-setup decided — the CD deploys. Use when the user says release, rilascia, manda in produzione, nasad, on a project with CI/CD.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root: `@production-branch`, `@ci-merge`, `@ci-platform`. Missing → this project has no CI/CD: `/dev:j-ci-setup` sets
  it up, `/dev:j-deploy` deploys without it. STOP.

## Steps

### 1. What goes out
```bash
git fetch origin
git log origin/{@production-branch}..origin/{@main-branch} --oneline
git diff origin/{@production-branch}..origin/{@main-branch} --stat
```
Nothing → "Nothing to release." STOP. A task still open in the Memory Bank (`@feature` or `@bug`) is named: its work goes out only once `/dev:j-close` has merged it.

### 2. Confirm
Show the commits, what they change and, with `@ci-merge: auto`, that the deploy starts by itself as soon as the gate is green. Ask with AskUserQuestion: **release this?**

### 3. The pull request
A pull request between these two branches that is already open is the one to use. Otherwise:
```bash
# GitHub
gh pr create --base {@production-branch} --head {@main-branch} --title "release: <what goes out>" --body "<the commits of step 1>"
# GitLab
glab mr create --target-branch {@production-branch} --source-branch {@main-branch} --title "release: <what goes out>" --description "<the commits of step 1>"
```
With `@ci-merge: auto`:
```bash
gh pr merge --auto --merge        # GitHub
glab mr merge --auto-merge        # GitLab
```
A merge commit always, never a squash (`/dev:j-ci-setup`, Rules). The branches stay: `{@main-branch}` is not deleted.

### 4. Report
The link; what happens next. `auto`: it merges itself on a green gate, and the deploy starts. `manual`: the gate runs, and the merge is the user's.

A red gate: nothing is merged and nothing is deployed. What it found is `/dev:j-bug`'s: the fix closes on `{@main-branch}`, and the pull request runs again.
A failed deploy: its log on the platform; `@restore-script` by hand, with the dialog of `/dev:j-deploy`, step 5.

### 5. Update MB
`progress.md`: what was sent to production, and the link.

## Rules
- **Never pushed to `@production-branch` directly**: only through the pull request, whose gate is the barrier.
- **It waits for nothing**: the pipeline runs on the platform.
