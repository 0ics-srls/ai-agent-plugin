---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: BBC — delegate the work on one black box to its own git worktree and agent session. It opens the worktree and its branch, writes there the BB's scope and the Memory Bank, and STOPS with the command that opens a session in that folder; there the BB is developed with /dev:bbc-plan, and closed with /dev:j-close. Several BBs can be delegated at the same time. Use when the user says bbc work, lavora sul BB, delega il BB, or a step of the roadmap sends BBs in parallel.
---

## Prerequisites
1. Read the Memory Bank (skip the subdirectories) if not already done this session.
2. `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
3. If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/bbc.md` — §3 point 5, the work in parallel.
4. The map: `{@tasks}/bbc/BBC-MAP.md` (missing → `/dev:bbc-analyze` first) and the BB the user names —
   `{@tasks}/bbc/bb/BB<N>-<name>.md`. A BB not on the map → `/dev:bbc-analyze` updates the map first.

## Purpose
One BB, one git worktree, one branch, one agent session opened in that folder (`bbc.md` §3.5): the
MCP servers keep their state in the folder of the session, so two works in one session would overwrite
each other's. This command opens the worktree and hands the BB over; it develops nothing itself.

## Steps

### 1. The BB, the base and the name
The BB from the map, with its status and its contract. The base branch of `@merge-strategy`
(`@dev-branch` for `gitflow` and `gitflow-simple`, `@main-branch` otherwise), fetched:
`git fetch origin <base>`. The worktree starts from it, so what the BB is developed against must
already be there:
- the map — `git show origin/<base>:{@tasks}/bbc/BBC-MAP.md`; missing → STOP: `/dev:bbc-analyze` and
  `/dev:bbc-review` commit on the branch they ran on, and that commit reaches the base first;
- the Core of the contracts, when the roadmap has its step: that step done. A BB delegated before has
  no contract on the base to develop against → STOP, the Core first.

The next `NN` (the highest number in `{@tasks}` plus one); the name `NN-bb<N>-<name>` asked and
confirmed with AskUserQuestion.

### 2. The worktree
From the main folder:
```bash
git worktree add ../<project folder>-NN-bb<N>-<name> -b feature/NN-bb<N>-<name> origin/<base>
git -C ../<project folder>-NN-bb<N>-<name> submodule update --init   # when the project has submodules
for l in .claude/*; do [ -L "$l" ] && cp -P "$l" ../<project folder>-NN-bb<N>-<name>/.claude/; done
git -C ../<project folder>-NN-bb<N>-<name> push -u origin feature/NN-bb<N>-<name>
```
The folder sits beside the project's; `git worktree list` shows it. The links of `.claude/` to the set
are ignored by git, so a new worktree does not have them, and a session opened there would have no
command: they are copied from the main folder's `.claude/` as links, and in the worktree they reach
the set of its own submodule.

### 3. The scope, in the worktree
In the worktree's folder:
- `{@tasks}/NN-bb<N>-<name>/notes.md`, with `## BB scope` as `/dev:bbc-plan` step 4 writes it — the BB, its
  status, its files, its contract, the contracts it uses — and nothing else yet;
- the Memory Bank's `activeContext.md`: `@state::IDLE`, `@feature::NN-bb<N>-<name>`,
  `@branch::feature/NN-bb<N>-<name>`;
- committed and pushed there:
  ```bash
  git -C <worktree> add {@tasks}/NN-bb<N>-<name>/ memory-bank/
  git -C <worktree> commit -m "docs(NN-bb<N>-<name>): the scope of BB<N>-<name>"
  git -C <worktree> push
  ```

### 4. STOP
```
BB<N>-<name> delegated to <worktree folder>, branch feature/NN-bb<N>-<name>.

Open a session there:   cd <worktree folder> && claude
In that session:
  /dev:bbc-plan BB<N>-<name>      the development of the BB
  /dev:j-cvm-exec-plan            its plan
  /dev:j-close                    when the BB is done, from the worktree
```
A change of the map — `/dev:bbc-refactor` — is made in the main folder, not in a BB's worktree: it changes
the map and the contracts other BBs use.

Every work in the worktree stays on its branch and within the BB's scope: the steps of a command that
would open another branch are skipped there, as `/dev:bbc-plan` steps 1-3 are. Other BBs can be delegated
now, each with this command. The integration and the flows are not delegated: `/dev:bbc-integrate` and
`/dev:bbc-e2e` run in the main folder, once the BBs they compose are merged into the base (`bbc.md` §3.5).

## Rules
- **One worktree, one session**: a BB's work runs only in the session opened in its folder.
- **A contract that open works use** changes only as `bbc.md` §3.3 says: the change names the open
  worktrees whose BB uses it (`git worktree list`, the `## BB scope` of each one's `notes.md`).
- **The base is brought into a worktree only on the user's decision.**
- **Ask with AskUserQuestion** whatever is not decided.
