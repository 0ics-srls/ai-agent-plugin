---
description: Generate the manual E2E checklist from the use cases (junior workflow). Writes tests/e2e-manual/template.md — the scenarios /dev:j-e2e runs by hand in the browser through ChromeDevTools — from the tasks' requirements and the Memory Bank's productContext. Works on any web project, with or without automated end-to-end tests. Use before /dev:j-e2e, or when user says generate tests, crea test, vygeneruj testy.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/dev:j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`

## Purpose
Generate or update `tests/e2e-manual/template.md`: the checklist of what a person — or the agent in the
browser — checks end to end in the running application. It is not the project's automated end-to-end
suite (`@test-e2e`, written by the plans' blocks): it checks the application as a user sees it, and
works on a project that has no automated end-to-end tests at all. Its sources:
- the use cases: `## Requirements` of each task's `notes.md` in `{@tasks}/`, and any use-case document
  there;
- the product's features: `memory-bank/productContext.md`.

## Steps

### 1. Read Sources
- `{@tasks}/*/notes.md` (`## Requirements`) and any use-case document in `{@tasks}/`
- `memory-bank/productContext.md` (features list)

### 2. How the application is reached
The checklist's header carries what `/dev:j-e2e` needs to reach the application, so no setting holds it:
- **URLs** — the frontend's and the backend's health check, read from the project (the start
  scripts, the launch settings, the dev-server configuration) or asked with AskUserQuestion;
- **login** — none, a credentials form, or a provider (OAuth/OIDC), asked with AskUserQuestion when
  the code does not show it;
- **accounts** — `.00-secrets/test-accounts.md`, the section of this application (the project's
  secrets, encrypted in git — `principles.md` 5.2).

### 3. Extract Test Sections
From the use cases and productContext, sections:
- **0. Prerequisites** — services running, database ready
- **1. Authentication** — the login flow of step 2
- **2. Main features** — from productContext.md
- **N. Additional features** — one section per major feature

Section names come from YOUR project's features, not from this template.

### 4. Generate Template
Create `tests/e2e-manual/template.md`:

```markdown
# Manual E2E Checklist - [project name, from productContext.md]

## Test Run Info
- **Date:** YYYY-MM-DD
- **Tester:** the agent (autonomous)
- **Frontend URL:** [from step 2]
- **Backend health:** [from step 2]
- **Login:** [none | credentials | provider name]
- **Accounts:** `.00-secrets/test-accounts.md`, section [application]

## Legend
- [x] = PASS
- [!] = FAIL (with notes)
- [-] = SKIP (with reason)

---

## 0. PREREQUISITES

### 0.1 Backend
- [ ] Backend running (started with `@start-backend`)
- [ ] Health check OK

### 0.2 Frontend
- [ ] Frontend running (started with `@start-frontend`)
- [ ] No console errors on load

### 0.3 Database (if applicable)
- [ ] Database running
- [ ] Migrations applied

---

## 1. AUTHENTICATION

### 1.1 Login Screen
- [ ] Page loads without errors
- [ ] Login UI elements visible

### 1.2 Login Flow
- [ ] Authentication works
- [ ] Redirects to authenticated area after login
- [ ] Session persists

---

## 2. [FEATURE FROM productContext.md]
<!-- Repeat for each feature -->

### 2.1 [Sub-feature]
- [ ] [Test case from use cases]
- [ ] [Test case from use cases]

---

[Continue with each feature from productContext.md...]
```

### 5. Save and commit
```bash
mkdir -p tests/e2e-manual/results
git add tests/e2e-manual/template.md
git commit -m "test(e2e-manual): checklist from the use cases"
```

### 6. Report
```
Manual E2E checklist generated!

Source: productContext.md + {@tasks}/ use cases
Output: tests/e2e-manual/template.md

Sections:
- 0. Prerequisites (N tests)
- 1. Authentication (N tests)
- 2. [Feature name] (N tests)
...

Total: NN test cases

Run `/dev:j-e2e` to execute them.
```

## Rules
- Each feature in productContext.md = at least one test section
- Each use case = at least one test case
- Group related tests in subsections
- Include both happy path and error cases
- Add "console error check" after each page load
- URLs, login and accounts in the header, from the project or asked — never invented
- Keep tests atomic - one check per line
