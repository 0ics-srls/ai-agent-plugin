---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "Development workflow — the phases a piece of work goes through, from the request to the deploy, in any project and any language: what each phase does and what it leaves. The one place the process is written; junior.md maps the commands onto it."
---

# Development Workflow

The phases of a piece of work, in order, in any project and any language. Every command goes through
them — `junior.md` says which command enters which phase — and adds only what is its own. `notes.md`
is the task's file, in `{@tasks}/NN-<name>/`.

---

## The phases

| Phase | What it does | What it leaves |
|---|---|---|
| LISTEN | the user says what is needed; no code is read and nothing is proposed | `notes.md` `## Requirements` |
| ANALYZE | the code the work touches and the mindsets that apply are read and understood; nothing is decided yet | `## Analysis` |
| INVENTORY | what already does each part of the job is searched, in the order of `principles.md` 2.3, by what it does and not by its name (`code-navigation.md`) | `## Inventory — capabilities and where they already live`: one line per capability, with where it lives or the search that came back empty, and the decision — reuse, extend, write |
| PROPOSE | the structure is decided on what the inventory found — what is shared and who owns it, the contracts, the mechanism of the behaviour (`code-principles.md` §2) — and the user approves it | `## Code Organization` |
| PLAN | the plan that executes the organization — TDDAB to build (`tddab-planner.md`), Step to remove, migrate or reconfigure (`step-planner.md`) — reviewed with `/j-review-plan` until approved, then shown to the user | `plan.md` |
| DEVELOP | `/j-cvm-exec-plan` executes the plan, block by block | a commit per block |
| CLOSE | the change is read against the mindsets and judged with the project's tools (`principles.md` §7); `j-settings.md @gate-final` is green (`@limitations` says what does not run locally); the branch is pushed and merged as `@merge-strategy` says | the merge |
| DEPLOY | the scripts and the domain of `j-settings.md` `## Deploy`; with `@production-branch`, the same scripts on the platform, once the pull request whose gate is `@gate-final` is merged (`j-ci-setup`, `j-release`) | — |

A bug goes LISTEN → DIAGNOSE → PLAN → DEVELOP → CLOSE. Its LISTEN leaves `bug-notes.md` `## Problem`;
DIAGNOSE finds the cause with Protocol D (`debug-protocol.md`) and leaves it in `bug-notes.md`. It designs nothing, so a bug has no inventory and no organization of its
own; a fix that touches something shared points at it, by name and path.

## Across the phases

- A phase re-reads, on entering it, the documents it needs: it can come days after the one before.
- A commit holds one logical change, with a conventional message (`feat:`, `fix:`, `refactor:`,
  `test:`, `docs:`, `chore:`); in DEVELOP the planexecutor commits each block with its title.
