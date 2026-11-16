---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Run the manual E2E checklist in the browser with ChromeDevTools (junior workflow). Executes the test cases of tests/e2e-manual/template.md against the running app — on any web project, with or without automated end-to-end tests. Use when the user says run e2e, testa il frontend, spusti e2e testy, or wants to verify UI behavior end-to-end.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## Steps

### 0. Check ChromeDevTools MCP
If the ChromeDevTools MCP server does not answer (`mcp__chrome-devtools__*` tools):
```
ChromeDevTools MCP is not configured.
It is required to run the checklist in the browser.

Run /dev:j-mcp-setup to install ChromeDevTools MCP, then retry.
```
STOP.

### 1. The checklist
`tests/e2e-manual/template.md`; missing or outdated →
```
No checklist found for this project.
Run `/dev:j-e2e-generate` to create one from the use cases.
```
STOP. Its header gives the frontend URL, the backend's health check, the login and the accounts.
`$ARGUMENTS` may carry a URL — `/dev:j-deploy` passes `@domain` after a deploy: the run goes there instead of
the header's frontend URL, and the backend's health check is the one that application answers.

### 2. Check Services Running
```bash
curl -s <frontend URL from the header> > /dev/null && echo "FE OK" || echo "FE NOT RUNNING"
curl -s <backend health from the header> > /dev/null && echo "BE OK" || echo "BE NOT RUNNING"
```
Not running → start them with `@start-<component>` of `j-settings.md`, then check again; still not →
ask the user.

### 3. Create Test Run File
```bash
mkdir -p tests/e2e-manual/results
cp tests/e2e-manual/template.md tests/e2e-manual/results/$(date +%Y-%m-%d).md
```

### 4. Login Process (if authentication required)
The header's **Login** says the method; the accounts are in `.00-secrets/test-accounts.md`.

**General login flow:**
1. Navigate to login page (URL from app)
2. Take snapshot to see login UI elements
3. Authenticate using project-specific method:
   - a provider (OAuth/OIDC) → click its button, sign in with the account
   - `credentials` → fill the username/password form with the account
   - `none` → skip login
4. Verify redirect to authenticated area

**If login fails:**
- Take screenshot of error
- Ask user: "Login failed. Can you complete it manually? Say 'done' when ready."

### 5. Execute Tests
Use ChromeDevTools MCP to:
- `mcp__chrome-devtools__navigate_page` to go to URLs
- `mcp__chrome-devtools__take_snapshot` to verify UI elements
- `mcp__chrome-devtools__click` to test interactions
- `mcp__chrome-devtools__fill` to test forms
- `mcp__chrome-devtools__list_console_messages` to check for errors

For each test case:
1. Execute the action
2. Take snapshot to verify result
3. Mark result: `[x]` pass, `[!]` fail, `[-]` skip

### 6. Document Results
Update the test file with:
- Results for each test case
- Console errors found
- Screenshots of failures (saved to `problem-chrome-dt/`)
- Summary table

Full report saved to: `tests/e2e-manual/results/YYYY-MM-DD.md`

### 7. Report to User
```
E2E Test Run Complete!

Date: YYYY-MM-DD
Environment: <frontend URL from the header>

RESULTS:
- Passed: NN
- Failed: NN
- Skipped: NN

ISSUES FOUND:
- [describe any bugs]

Full report: tests/e2e-manual/results/YYYY-MM-DD.md

A failed case is a bug: /dev:j-bug, with what this run found.
```

## Test Execution Order
Follow the order in template:
1. Prerequisites (services running)
2. Public pages (login screen, about)
3. Auth flow (the header's Login)
4. Dashboard
5. Each feature section
6. Edge cases

## Rules
- The login is the header's; the accounts come from `.00-secrets/test-accounts.md`, never from the checklist
- Take snapshot BEFORE and AFTER each major action
- Check console for errors after each page load
- If test fails, document WHY before moving on
- Save screenshots of failed tests to `problem-chrome-dt/e2e-{testname}.webp`; an agent reads them, never the main conversation
- A failed case is fixed with `/dev:j-bug`, not here
