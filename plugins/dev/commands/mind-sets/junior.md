---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "Junior workflow mindset - which command enters which phase of development-workflow.md, where the phase is tracked, how the agent works, and the golden rules. Base mindset for the j-* family; the phases are development-workflow.md's, what a command does in them is in the command."
---

# Junior Workflow Mindset

The commands of the junior workflow on the phases of `development-workflow.md`, and the rules that
hold in every phase. What a phase does and leaves is `development-workflow.md`; what a command does
inside a phase is in the command; the project's settings are in `j-settings.md`.

---

## The commands on the phases

```mermaid
flowchart TD
    IDLE([IDLE])
    IDLE -->|j-new-project, j-new-feature| LISTEN([LISTEN])
    LISTEN --> ANALYZE([ANALYZE])
    ANALYZE --> INVENTORY([INVENTORY])
    INVENTORY --> PROPOSE([PROPOSE])
    PROPOSE -->|user approves| PLAN([PLAN])
    IDLE -->|j-bug| BUG_LISTEN([LISTEN])
    BUG_LISTEN --> DIAGNOSE([DIAGNOSE])
    DIAGNOSE --> PLAN
    PLAN -->|user approves the reviewed plan<br>j-cvm-exec-plan| DEVELOP([DEVELOP])
    DEVELOP -->|j-close| CLOSE([CLOSE])
    CLOSE -->|j-deploy, or j-release with CI/CD| DEPLOY([DEPLOY])
    CLOSE --> IDLE
    DEPLOY --> IDLE
    IDLE -->|j-poc| POC([POC<br>no state tracking])
    POC --> IDLE
```

| Command | Phases |
|---|---|
| `j-new-project` | a project not designed as black boxes: LISTEN, ANALYZE, INVENTORY, PROPOSE, then its settings, then PLAN, then the Memory Bank; it stops before DEVELOP. On an existing project: LISTEN, its settings, ANALYZE, the Memory Bank, then IDLE |
| `j-new-feature` | LISTEN, ANALYZE, INVENTORY, PROPOSE, PLAN; on a project with a black-box map, it reads the map |
| `j-bug` | LISTEN, DIAGNOSE, PLAN; on a project with a black-box map, it reads the map |
| `j-review-plan`, `j-cvm-check-plan` | PLAN: the plan reviewed against the mindsets and the code; its structure checked |
| `j-cvm-exec-plan` | DEVELOP |
| `j-close` | CLOSE |
| `j-deploy`, `j-release` | DEPLOY: by hand, or through the CI/CD (`j-ci-setup`) |
| `bbc-analyze`, `bbc-review` | the analysis: the black boxes designed from the requirements, no code read, reviewed in a loop until approved, and the roadmap (`bbc.md`) |
| `bbc-core` | starts a black-box project — the profile, the skeleton — and plans the Core of the contracts, as `j-new-feature` (`bbc.md`) |
| `bbc-plan`, `bbc-refactor`, `bbc-integrate`, `bbc-e2e` | as `j-new-feature`, on the black boxes of the map (`bbc.md`) |
| `bbc-work` | a black box delegated to its own worktree and session, where `bbc-plan` develops it |
| `bbc-audit` | the code checked against the analysis: a report, and a feature that fixes it |
| `bbc-debug` | as `j-bug`, with ISOLATE on the map |

### State tracking
The phase is saved in `activeContext.md`:
```
@state::IDLE|LISTEN|ANALYZE|INVENTORY|PROPOSE|PLAN|DIAGNOSE|DEVELOP|CLOSE|DEPLOY
@feature::NN-feature-name          (a bug: @bug::NN-bug-description)
@branch::feature/NN-feature-name   (a bug: bugfix/NN-bug-description)
@plan::{@tasks}/NN-name/plan.md    (from PLAN on)
```
IDLE is no work in progress. A debugging session (`j-debug`) leaves its outcome:
```
@lastDebug::{description}
@debugResult::{found|needsMore|wasBug|wasFeature}
```

### Commands from any state
| Command | Action |
|---------|--------|
| `j-save` | Save state to MB, commit, push, leave |
| `j-status` | Read MB, show current state |
| `j-help` | Show available commands |
| `j-continue` | Read MB, resume from saved state |
| `j-setup` | Configure/update project settings |
| `j-ci-setup` | CI/CD for the project, when the user wants it |
| `j-debug`, `j-debug-mb` | Protocol D on a problem, without a branch or a task (`debug-protocol.md`) |
| `j-browse` | The running application in the browser, guided by the user |
| `j-e2e-generate`, `j-e2e` | The manual end-to-end checklist: written from the use cases, run in the browser |
| `bbc-analyze`, `bbc-review` | The black boxes of a new project, or a new part of one, designed from the requirements before its code, no code read; reviewed until the user approves; and the roadmap of their development (`bbc.md`) |
| `bbc-audit` | The code of the black boxes checked against the analysis: a report, and a feature that fixes it |

---

## How the agent works

- **Model**: every agent runs on the session's model. A skill names no model, and an agent
  declares none.
- **Search and review** go through code navigation (`mind-sets/code-navigation.md`, the tools of
  `@code-nav-local` and `@code-nav-external`), in the main conversation, never delegated. A text
  search is the declared fallback when the navigation tool is absent or not ready.
- **Planned work** is a TDDAB or Step plan executed by the CVM planexecutor.
- **Long sessions**: the documents a phase needs are re-read on entering the phase (each command says
  which), and the state lives in the Memory Bank.

---

## Golden Rules

1. **NEVER act without being asked**
2. **ALWAYS read j-settings.md + MB at session start**
3. **ALWAYS ask before modifying code**
4. **Each feature = one branch**
5. **Migrations: ADD, never recreate** (`branches/data.md` 12)
6. **Update MB at every state change and checkpoint** — during a plan the planexecutor updates it
   for each block
7. **NEVER delete branches** - push them, user needs control
8. **ALWAYS push branch before merge** - so user can review on remote
9. **ALWAYS use AskUserQuestion tool** - when you need more specs or clarification, use the tool instead of plain text questions
10. **REALITY WINS OVER MB** - if MB state doesn't match what you see (code, branches, folders), investigate and ask user before blindly following MB
11. **A file touched is left with zero warnings** — its existing warnings are fixed too (`principles.md` 6.1)
