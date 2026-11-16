---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Help (junior workflow). Shows all available junior commands with descriptions. Use when the user asks what commands exist, how junior workflow works, or says help/aiuto/pomoc.
---

## Prerequisites
- If not read this session: Read `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`
- MB: not required for help

## Show
```
=== JUNIOR WORKFLOW HELP ===

FIRST TIME SETUP:
  j-setup        → Configure project settings (REQUIRED before other commands)
  j-init-secrets → Encrypt the project's secrets in git (.00-secrets/, git-crypt)
  j-mcp-setup    → Install/configure MCP servers (CVM, code navigation, ChromeDevTools)
  j-ci-setup     → Set up CI/CD: a production branch, the gate on its pull requests, the deploy on merge
  j-new-project  → Create a brand new project with all foundations, or bring an existing one in

START WORK:
  j-new-feature  → Start a new feature
  j-bug          → Fix a bug
  j-poc          → Experiment with something new (proof of concept)
  j-continue     → Resume where you left off

DURING WORK:
  j-cvm-exec-plan  → Execute the plan, block by block
  j-review-plan    → Review a plan against its methodology, the mindsets and the code
  j-cvm-check-plan → Check a plan's structure with the CVM parser
  j-debug          → Debug any problem (Protocol D)
  j-debug-mb       → Same as j-debug but uses less memory (for long sessions)
  j-status         → See current status
  j-save           → Save everything and leave

TESTING & BROWSING:
  j-browse       → Browse/interact with any web page (you guide, I click)
  j-e2e-generate → Generate the manual E2E checklist from the use cases
  j-e2e          → Run the manual E2E checklist in the browser

LARGE PROJECTS — BLACK BOXES (BBC):
  bbc-analyze    → Design the black boxes from the requirements, no code: structure, decisions, diagram
  bbc-review     → Review the analysis (back to bbc-analyze until approved), then the roadmap
  bbc-core       → Start a black-box project (profile, skeleton) and plan the Core: every contract, with its fake and its contract tests
  bbc-plan       → Plan the development of one black box from its contract
  bbc-work       → Delegate one black box to its own worktree and session, in parallel
  bbc-refactor   → Change a black box of the map, then the code
  bbc-integrate  → Test black boxes together, real with real, and fix what does not match
  bbc-e2e        → Plan the end-to-end tests of the map's flows
  bbc-audit      → Check the code against the analysis: a report, and a feature that fixes it
  bbc-debug      → Fix a bug that crosses several black boxes

AUDIT:
  x-audit-code   → Audit the code, one command, to the report: the map, the description, the cards confirmed by reading

FINISH:
  j-close        → Close the feature or the bug, merge, and deploy
  j-release      → Send the main branch to production, through the CI/CD
  j-deploy       → Deploy only (works standalone on the right branch)

=== FIRST TIME? ===

Run j-setup first! It will:
1. Find what your project shows, and ask only what it cannot see
2. Create j-settings.md with all configurations
3. Make all other j-* commands work properly

=== HOW IT WORKS ===

1. Run j-setup (only once per project), and j-new-project to start one or bring one in
2. Use j-new-feature or j-bug
3. Tell me what you need (I listen)
4. When you say "done", I analyze the code and look for what already exists
5. I propose the structure, you approve it
6. I write the plan and review it, then you review it
7. You say "j-cvm-exec-plan" and I build it one block at a time
8. When done, use j-close to merge and deploy

=== IF YOU'RE STUCK ===

- Don't know what to do? → j-status to see where we are
- Need to leave? → j-save to save everything
- Something not working? → Tell me the problem
- Have doubts? → Ask! Better to ask than make mistakes
- Settings wrong? → j-setup to change them

=== IMPORTANT RULES ===

- I do NOTHING until you ask me
- Before modifying code, I ask confirmation
- If you need to leave, always use j-save
- Don't be afraid of mistakes, we can always go back

=== IF SOMETHING GOES VERY WRONG ===

1. Use j-save
2. j-status shows where it stands, and j-continue picks it up
```
