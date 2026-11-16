---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Set up a project's CI/CD (junior workflow). A production branch; a pull request from the main branch to it runs the final gate; merged, it deploys. On GitHub or GitLab, read from the remote; the merge automatic or by hand, as the user decides. Optional, one project at a time. Use when the user says CI, CD, CI/CD, pipeline, branch production, or /dev:j-setup asks and the answer is yes.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root, with `@gate-final` (missing → run `/dev:j-setup` first; a project still to be
  built runs this command after its first plan: until then there is no gate to run).
- A remote `origin`, and its command line authenticated: `gh auth status` or `glab auth status`.

## Purpose
`{@main-branch}` is what is finished, the branch `@production-branch` is what runs. A pull request from one to the
other runs `@gate-final`; when it is merged, the pipeline runs `@backup-script` and `@deploy-script`. Nothing is defined
twice: the gate and the deploy stay the keys of `j-settings.md`. `/dev:j-release` opens that pull request.

## Steps

### 1. The platform
```bash
git remote get-url origin
```
`github.com` → GitHub Actions; `gitlab` in the host → GitLab CI; anything else → ask with AskUserQuestion. A project that
already has a pipeline (`.github/workflows/`, `.gitlab-ci.yml`) shows it, and asks whether to add these beside it, or stop.

### 2. Ask with AskUserQuestion
- **The merge, with the gate green**: `auto` — the pull request merges itself and the deploy starts, with nobody reading it; `manual` — the
  green gate allows the merge, someone presses it, and the deploy starts then. → `@ci-merge`.
- **The production branch's name**, `production` by default. → `@production-branch`.
- **`@deploy-script` is `none` or missing**: which script deploys? With none, this sets up the CI alone, and the report says so.

### 3. The branch
Created from `{@main-branch}` when missing, and pushed:
```bash
git fetch origin
git rev-parse --verify origin/{@production-branch} 2>/dev/null || git push origin origin/{@main-branch}:refs/heads/{@production-branch}
```

### 4. The pipeline
The templates in `${CLAUDE_PLUGIN_ROOT}/support/ci/`, filled and written into the project:

| Platform | Template | Written as |
|---|---|---|
| GitHub | `github/ci.yml`, `github/cd.yml` | `.github/workflows/ci.yml`, `.github/workflows/cd.yml` |
| GitLab | `gitlab/gitlab-ci.yml` | `.gitlab-ci.yml` |

- `__PRODUCTION_BRANCH__`, `__GATE_FINAL__`, `__DEPLOY_SCRIPT__`, `__BACKUP_SCRIPT__`: the values of `j-settings.md`, as they are. No `@deploy-script`: no CD.
  `@backup-script: none`: its step comes out.
- `__TOOLCHAIN_STEPS__` (GitHub), `__IMAGE__` (GitLab): what the gate needs for each component, read from its `language.md`
  §5 and the project's build files: the platform's official setup step for each toolchain, at the minimum version the project declares. What the
  gate's tests start, such as Docker, is there on GitHub's hosted runners; on GitLab it is asked of the runner.
- What `@limitations` says does not run locally, and a gate step that needs a machine the platform does not give (an iOS build on a Mac), is named to the
  user with AskUserQuestion: its runner, or that step left out and named in the report.
- A submodule `@base-library` is checked out with the code; `.ai-agent` is not needed by the gate.
- No `.00-secrets/`: the step that unlocks it comes out.

### 5. The secrets of the pipeline
The values never appear in the conversation, the log or a file.
- `.00-secrets/` exists: the key of git-crypt, encoded, goes to the platform's secrets:
  `git-crypt export-key - | base64 -w0 | gh secret set GIT_CRYPT_KEY` (GitLab: `glab variable set GIT_CRYPT_KEY --masked`, reading from stdin).
- What `@deploy-script` reads from the environment is named by the user and set the same way.

### 6. The rule on the platform
The merge needs the gate green, and with `@ci-merge: auto` it happens by itself.
- GitHub: `gh api -X PUT repos/{owner}/{repo}/branches/{@production-branch}/protection` with the required status check `gate`;
  `auto` also `gh repo edit --enable-auto-merge`.
- GitLab: `glab api` on `protected_branches` for the branch, and `only_allow_merge_if_pipeline_succeeds` on the project.

A plan of the platform that refuses this (a private repository on a free plan) is reported as it is, with what it leaves unprotected: the gate
still runs, and the merge has to be held by whoever presses it.

### 7. The settings
In `j-settings.md`, section `## CI/CD`: `@production-branch`, `@ci-merge`, `@ci-platform`.

### 8. Commit what this command produced
Only these files, by path, on `{@main-branch}`:
```bash
git add j-settings.md .github/workflows/ci.yml .github/workflows/cd.yml   # GitLab: .gitlab-ci.yml
git commit -m "chore(j-ci-setup): CI on the pull requests to {@production-branch}, CD on what reaches it"
git push origin {@main-branch}
```

### 9. Report
The platform, the branch, the gate and the deploy they run, the merge, the secrets set by name, what the platform refused, what was left out. Next: `/dev:j-release`, which
is also the first proof that it works.

## Rules
- **Optional, and per project**: a project without `@production-branch` keeps `/dev:j-close` and `/dev:j-deploy` as they are.
- **Nothing defined twice**: the pipeline runs the keys of `j-settings.md`.
- **Merge commits only**: squash would leave `@production-branch` out of `{@main-branch}`'s history.
- **Ask with AskUserQuestion** whatever is not decided.
