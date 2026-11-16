---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Setup/validate Junior workflow settings for this project. On an existing project it wires ai-agent in — detects language, stack, commands, ports, the mindsets profile and the lint gate, and writes j-settings.md. On a project not created yet it writes the base j-settings.md and leaves the rest to /dev:j-new-project. MUST run first before any other j-* command.
---

## Purpose
Create or update `j-settings.md` in the project root: the settings every Junior workflow command
reads. **It detects what the project shows, asks only what it cannot see, and leaves out what is not
known yet.**

A key that is not known yet is left out of the file. `none` and `n/a` mean "decided: there is none",
never "not known".

## Steps

### 0. Secrets and MCP servers: asked here, run from here
/dev:j-setup is the entry point: it asks about the two commands that come with it — fundamental, neither
required — and runs the ones the user wants. Called by `/dev:j-new-project` or `/dev:bbc-core` with a profile, this step is
skipped: the questions were asked when its base settings were written.
```bash
[ -e .git/git-crypt ] && echo "SECRETS_READY"
cat .mcp.json opencode.jsonc 2>/dev/null   # the project's servers, for either host: /dev:j-mcp-setup's PROJECT_CFG
python3 -c "
import json, os
for path, key in (('~/.claude.json', 'mcpServers'), ('~/.config/opencode/opencode.json', 'mcp')):
    try: print(path, sorted(json.load(open(os.path.expanduser(path))).get(key, {})))
    except (OSError, ValueError): pass
"   # the user-wide ones, by name: /dev:j-mcp-setup's PROFILE_CFG
for tool in npx uvx bunx ast-grep; do command -v "$tool" >/dev/null 2>&1 && echo "$tool: ok" || echo "$tool: missing"; done
```
These are the minimum development tools: the MCP servers start through the runners (`npx` for
cvm, chrome-devtools and the framework servers, `uvx` for ui-ticket-mcp, `bunx` for claude-chat), and
the lint gate runs `ast-grep` (step 7 installs it).
Ask with AskUserQuestion, one question each, only for what is missing:
- **Secrets** (no git-crypt yet): set up `.00-secrets/`, encrypted in git? Yes → run
  `/dev:j-init-secrets` now, to its end, then come back here.
- **MCP servers** (no CVM, or no code-navigation server, or a runner missing): configure them, with
  the missing runners? Yes → `/dev:j-mcp-setup` installs the runners and the servers; it runs
  after step 3, once the language is known, so its catalog offers the servers of that language; on a
  project to create it runs during step 15, before code navigation is detected, with the language the
  user gives.

- **CI/CD** (no `@production-branch` yet, a remote `origin`): a `production` branch, a pull request to it that runs the
  final gate, a deploy when it is merged? Yes → `/dev:j-ci-setup` runs after step 12, once `@gate-final` exists; on a project to
  create it runs after the first plan, and step 17 names it.

What the user declines is named in the report.

### 0b. What the plugin needs in the project
The set is a plugin: its pages are in the plugin's folder, outside the project, and no script has
prepared the project. Each of these is checked on every run, and written when it is not so:
- `.claude/settings.json` has `Read(~/.claude/plugins/cache/ai-agent/**)` in `permissions.allow`:
  without it the agent is asked before each read of a page of the plugin, and refused where
  nobody can answer. It is a permission of the user's, so it is asked first: say the rule, word
  for word, and what it is for, and ask with AskUserQuestion — add it, or leave it out. Added on
  a yes, the file's other keys kept; left out, nothing is written and the rest goes on.
- The project's base files, from `${CLAUDE_PLUGIN_ROOT}/project/`, each one only when the project does not have it:
  `CLAUDE.md`, `.mcp.json`, `memory-bank/history.md`, `memory-bank/archive/.gitkeep`.
- `memory-bank/README.md` is a copy of `${CLAUDE_PLUGIN_ROOT}/project/memory-bank/README.md`: it is the set's page,
  not the project's, so a copy that differs is replaced.
- The root `.gitignore` has the lines `.cvm/`, `.lsai/` and `problem-chrome-dt/`.

What was written is committed with what this command produces.

### 0c. A project that has the set as a git submodule
The signs: `.gitmodules` has a submodule whose url ends in `ai-agent`, `ai-agent-lite` or
`ai-agent-oc` (its path is `.ai-agent`, here `<submodule>`), or `.claude/commands` is a symbolic
link, or `.claude` itself is one. None of them → step 1.

With the submodule and the plugin together every command is there twice. Say what the move does —
the list below — and ask with AskUserQuestion: move the project to the plugin now, or leave it on
the submodule. Left on the submodule → say that the plugin is to be disabled in this project
(`claude plugin disable dev@ai-agent --scope project`) and STOP. To move:
1. `git status --porcelain` is empty and no plan is being executed (`.cvm/` has no execution of
   this project in progress): otherwise STOP, the work in progress is closed or committed first —
   a plan under way names the set's files where the submodule has them.
2. The links into the submodule are removed, each only when it is a symbolic link: under
   `.claude/`, `commands`, `lint-rules`, `audit`, `support` and any other link that resolves
   inside `<submodule>/`, with their lines in `.claude/.gitignore`. When `.claude` itself is a
   link (an earlier setup), the files of the project in it — `settings.json`,
   `settings.local.json` — are kept aside, the link is removed, `.claude/` is made a folder and
   they are put back.
3. `memory-bank/README.md`, a link into the submodule, is removed: step 0b writes the copy.
4. The submodule: `git submodule deinit -f <submodule>`, `git rm -f <submodule>`,
   `rm -rf .git/modules/<submodule>`; `.gitmodules` is removed when it is left empty.
5. `.git/hooks/pre-commit` is removed when it has the line `# ai-agent-submodule-guard`.
6. What still names the submodule's places, in the tracked files outside `{@tasks}/` and
   `memory-bank/archive/`: `git grep -nE '\.claude/(commands|lint-rules|audit|support)|\.ai-agent'`.
   - `sgconfig.yml` → written again from its template, the rules copied to `.ast-grep/` (step 7).
   - `CLAUDE.md`, the line that sends to `code-navigation.md` in `.claude/` → the mindset
     `code-navigation` of the plugin `dev` (`/dev:mind-sets:code-navigation`).
   - `j-settings.md`, a value with such a path → found again by the step that writes the key.
   - A pipeline that initialises the submodule, a script, any other file → shown to the user,
     changed on their word.
   - The submodule had the `biz-*` and `info-*` commands too, and `dev` does not: say that they
     are the plugins `biz` and `info` of the same catalogue, installed when wanted.
7. Step 0b again, then `git add -A . && git commit -m "chore: the set as a plugin, not a submodule"`.

Then step 1: `j-settings.md` is there, so the settings are validated (step 20), which brings the
lint configuration files to the plugin's pack.

### 1. Existing settings
```bash
ls -la j-settings.md 2>/dev/null
```
**Called by `/dev:j-new-project` or `/dev:bbc-core` with a profile → PROFILE GIVEN (step 18).** Otherwise, **j-settings.md
exists → VALIDATE MODE (step 20)**; neither → continue.

### 2. Existing project or project to create
```bash
ls -la
ls ${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/overlays/
```
Each overlay's `language.md` §7 says, under **Recognized by**, the files that mark its language. Look
for them in the repository, to a depth of 3, outside `externals/` and the vendored folders the same
§7 names.
- **Files of an overlay found → EXISTING PROJECT**: steps 3-13.
- **None found**, and the repository holds source files besides the ai-agent wiring (`.ai-agent`,
  `.claude/`, `memory-bank/`, `j-settings.md`) → ask with AskUserQuestion: a project in a language
  without an overlay (its name → EXISTING PROJECT, `@mindsets-overlay: none`), or a project to create.
- **Nothing** → **PROJECT TO CREATE**: steps 15-17.

---

## EXISTING PROJECT — Phase 1: SCAN

### 3. Language and stack
Each component's language is the overlay whose §7 recognized its files, or the one the user named in
step 2. Read the build files as that §7 says: their frameworks and libraries say the branches of step 5.

A monorepo has one language per component — the backend, each frontend — and each component has its
own keys (`@lint-<component>`, `@test-focused-<component>`, `@test-block-<component>`).

### 3b. MCP servers, when the user asked for them in step 0
Run `/dev:j-mcp-setup` with the language from step 3. Its configuration is read again in step 9.

### 4. Folders
```bash
ls -d src/ backend/ src/backend/ server/ api/ frontend/ src/frontend/ client/ web/ app/ 2>/dev/null
ls -d tests/ test/ spec/ tasks/ docs/ tools/ scripts/ deploy/ externals/ 2>/dev/null
```

### 5. Mindsets profile
The mindsets live in `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/`. The table of its `README.md` §2 assigns the
branches to what a project has; for each component, the scan decides from what it shows — the
frameworks and libraries of step 3.

`security` applies to a system exposed to callers it does not control; the scan cannot see that, so
it is asked (step 10). When no branch applies, `@mindsets-branches: none`: decided, there is none.

The overlay is the language's folder under `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/overlays/` and the files of it the branches
call for (its `language.md` §7 lists them with their branches). Each is written as its path under
`mind-sets/`, because the commands load it from there: `overlays/python/language.md`. A language with no
overlay folder gets `@mindsets-overlay: none`, and the report says so.

### 6. Base library
```bash
cat .gitmodules 2>/dev/null
ls externals/ 2>/dev/null
```
A submodule or a referenced shared library that provides the base — entity, repository, unit of
work, generic endpoints — is the project's base library: `@base-library: <repository url> (<path>)`.
When none is visible, it is asked (step 10).

### 7. Lint gate
The gate checks the project's own sources. A folder that is not — the code of a base library or of
another submodule under `externals/`, generated code, build output — is excluded with each tool's own
mechanism, as the pack and the language's overlay write it.

For each component → language, read `${CLAUDE_PLUGIN_ROOT}/lint-rules/manifest.yaml[language]` →
`{ native_lint, ast_grep, config_files }`. A language the manifest does not declare has no pack yet:
no `@lint-<component>`, no configuration files, no `sgconfig.yml` line; the report says so.
1. `@lint-<component>: <native_lint>`, with the placeholders the language's §7 names replaced by the
   project's own.
2. `ast_grep: true` → the component's language gets a line in `sgconfig.yml`; `false` → native
   linter only.
3. Each `config_files` template from `${CLAUDE_PLUGIN_ROOT}/lint-rules/<language>/native/` goes into the project at
   the same relative path, where the language's §7 says. A file that
   already exists is merged, asking first, and kept otherwise. The templates under `externals/` go in
   when the project keeps code that is not its own there: `externals/` exists, or `@base-library` is a
   submodule.
4. A component's gate is the one its language's overlay names (`language.md` §7),
   written as the overlay says, asking first when it changes a file of the project.
5. When a component has `ast_grep: true`, `ast-grep` must answer `ast-grep --version`; when it does
   not, install it with `npm i -g @ast-grep/cli` and check it again; without `npm`, Node.js is installed
   first, as `/dev:j-mcp-setup` installs its runners. The gate `@lint-astgrep` runs it by name, without `externals/`:
   `ast-grep scan --globs '!externals/**'`.

6. The project's own scripts, tracked `*.sh` or `*.ps1` files (`git ls-files`), are a component of their own, with no
   overlay: the manifest's `shell` entry gives `@lint-scripts: <native_lint>`, its configuration files go to the
   repository root, and `sgconfig.yml` has its line.

`sgconfig.yml` is a copy of `${CLAUDE_PLUGIN_ROOT}/lint-rules/sgconfig.template.yml` at the project root: the
`_shared` line stays when a component has `ast_grep: true`, and the `${LANG}` line is expanded once
per such language that has a folder `${CLAUDE_PLUGIN_ROOT}/lint-rules/<language>/ast-grep/` (dropped for a language
whose rules are all in `_shared`, and the file is not written when no component has `ast_grep: true`).

The rules those lines name are copied into the project, because the plugin's folder is not in it
and its pipeline does not have the plugin: `${CLAUDE_PLUGIN_ROOT}/lint-rules/_shared/ast-grep/` → `.ast-grep/_shared/`,
each such language's `${CLAUDE_PLUGIN_ROOT}/lint-rules/<language>/ast-grep/` → `.ast-grep/<language>/`, and
`${CLAUDE_PLUGIN_ROOT}/VERSION` → `.ast-grep/VERSION`, the version of the set the rules were copied from.

### 8. Test levels
The keys of `## Tests — by level` in step 11, in the forms the language's overlay gives
(`overlays/<language>/tddab.md` §1) on the solution or the package the scan found (`language.md` §7). `@test-e2e` is the end-to-end run where the project has one — it starts by itself what it needs,
the backend and its storage, so `/dev:j-close`, `/dev:j-deploy` and the pipeline run it as it is — `@bench` the run of
a benchmarks project where there is one; otherwise `none`. `@gate-final` writes out, in order, each
component's lint, `@lint-astgrep`, `@test-slow`, each frontend's build, `@test-e2e` and `@bench`,
leaving out the ones that are `none`.

The command that starts each component, `@start-<component>` in `## Run`, in the form the language's
overlay gives (`language.md` §7): `/dev:j-debug` starts the services with it. A component nothing starts, a
library, has `@start-<component>: none`: decided, there is none.

What a test level's command needs in the project, when the language's §7 names it under **The test
levels**, goes in as step 7 puts a configuration file: created when missing, merged into an existing file
asking first, and nothing else of that file touched.

### 9. Git, deploy, tools
```bash
git branch -a 2>/dev/null | head -10
git remote show origin 2>/dev/null | grep "HEAD branch"
git branch -a 2>/dev/null | grep -E "(^|/)develop$"
ls -la tools/deploy* scripts/deploy* deploy* Dockerfile compose.yaml docker-compose* 2>/dev/null
ls -la .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null
ls -la tools/backup* scripts/backup* tools/restore* scripts/restore* 2>/dev/null
```
Code navigation — the one rule for `@code-nav-local` and `@code-nav-external` (`/dev:j-mcp-setup` applies
the same): from the servers configured in the project and for the user — step 0 lists them, from
`/dev:j-mcp-setup`'s PROJECT_CFG and PROFILE_CFG of the host in use — lsai → `lsai`, else vs-mcp → `vs-mcp`, else `grep`; xmp4 → `xmp4`, else
`none`. The search scope for `code-navigation.md`: `@own-code-roots` = the project's source and test
folders plus the base library's path when it is a submodule (its capabilities are searched before
writing; a package is searched with `@code-nav-external`), and
`@vendored-globs` = the folders each component's overlay names as vendored (§7) — for a language
without an overlay, the build output and package folders the scan shows.

---

## EXISTING PROJECT — Phase 2: PROPOSE

### 10. Findings, then only the unknowns
Show what was detected — language and stack per component, the main branch, deploy, the mindsets
profile (branches and overlay files), the base library, the lint keys, the test levels — and ask
with AskUserQuestion only what the scan could not establish:
- **Exposure**: is the system reached by callers it does not control (internet, other
  organizations)? yes → `security` joins the branches.
- **Base library**, when none is visible: is there a library this project builds on? its repository
  and how it is referenced (submodule path or package).
- **Kind of plans**: TDDAB (building functionality, the default) or Step (removing, migrating,
  reconfiguring).
- **Merge strategy**: how a finished branch reaches the main line → `@merge-strategy` — `direct` (merged
  locally into `@main-branch` and pushed, the default), `pr` (a pull request to `@main-branch`),
  `gitflow` (a pull request to `@dev-branch`), `gitflow-simple` (merged locally into `@dev-branch`).
  With a `develop` branch in the scan, the gitflow ones come first; `@dev-branch` is that branch, `none`
  otherwise.
- **Deploy, backup, restore scripts, domain, local limitations**, when not found.
- **What the language's overlay asks on an existing project**: the questions its `language.md` §7 lists
  under that name, when it has them — a choice about what the project already has that only the owner
  can make.
- A branch the scan suggests but cannot confirm (a dependency present but unused) is confirmed here.

---

## EXISTING PROJECT — Phase 3: CREATE

### 11. Confirm, then write `j-settings.md`
Show the final values; on confirmation write the file with the sections below, each key filled from
the scan or the answers, the unknown ones left out.

```markdown
# Junior Workflow Settings
# Generated by /dev:j-setup on YYYY-MM-DD — run /dev:j-setup again to update

## Project
@language: {the overlay folder's name, or the language the user named}   # one key per component in a monorepo: @language-backend, @language-frontend

## Mindsets
@mindsets-branches: {service-layers, data, api, resilience, operations, security, frontend, game — the ones that apply | none}
@mindsets-overlay: {overlays/<language>/language.md, … — the overlay files that go with those branches, each by its path | none}
@base-library: {<repository url> (<path in the project>) | none}
# A monorepo has one @mindsets-branches-<component> and @mindsets-overlay-<component> per component.

## Git
@main-branch: {main|master}
@merge-strategy: {direct|pr|gitflow|gitflow-simple}
@dev-branch: {develop|none}

## Folders
@tasks: tasks/

## Methodology
@backend-method: {tddab|step}

## Linting
@lint-astgrep: ast-grep scan --globs '!externals/**'
@lint-backend: {command}
@lint-frontend: {command}
@lint-scripts: {command, when the project has scripts}

## Tests — by level
# Templates: a plan copies them into a block, the placeholders filled with the block's own names
@test-focused-backend: {command with {project} and {test}}
@test-focused-frontend: {command with {file} and {test}}
@test-block-backend: {command with {project}}
@test-block-frontend: {command}
# Global: run as they are
@test-fast: {the unit tests of every component, in seconds}
@test-slow: {everything, integration included}
@test-e2e: {the command, which starts what the run needs | none}
@bench: {command | none}
@gate-final: {the final gate's commands, in order}

## Run
@start-backend: {the command that starts it | none}
@start-frontend: {the command that starts it | none}

## Deploy
@deploy-script: {path|none}
@domain: {url|none}
@backup-script: {path|none}
@restore-script: {path|none}

## CI/CD
@production-branch: {production | none} # /dev:j-ci-setup writes this section
@ci-merge: {auto|manual}
@ci-platform: {github|gitlab}

## Code Navigation
@code-nav-local: {lsai|vs-mcp|grep}
@code-nav-external: {xmp4|none}
@own-code-roots: {src/, tests/, the base library's path when it is a submodule}
@vendored-globs: {the vendored folders of each component's overlay (language.md §7)}

## Local Limitations
@limitations: {services that do not run locally|none}
```

### 12. Commit what this command produced
Only the files this command wrote, by path:
```bash
git add j-settings.md .claude/settings.json <what step 0b wrote> <sgconfig.yml and .ast-grep/, when step 7 wrote them> <each file steps 7 and 8 created or changed, package.json included>
git commit -m "chore(j-setup): project settings and lint configuration"
```
Other pending changes stay as they are, and the report names them.

### 13. Report
What was detected, what the user provided, the mindsets profile with the files it loads, the base
library, the lint gate, what was left out and why, and what the user declined in step 0 — secrets
(`/dev:j-init-secrets`), MCP servers and ChromeDevTools (`/dev:j-mcp-setup`). After `/dev:j-mcp-setup` the agent
is restarted to load the new servers. Then: the next command of the work (`junior.md`).

---

## PROJECT TO CREATE

### 15. Base settings
Only what holds before any code exists:
- git: the main branch, and the merge strategy (asked as in step 10; `direct` by default) with its
  `@dev-branch`;
- folders: `@tasks: tasks/`;
- methodology: `@backend-method` (asked: TDDAB by default);
- base library: asked — is there a library the new project will build on? → `@base-library`;
- code navigation, detected as in step 9 — after `/dev:j-mcp-setup`, when the user asked for it in step 0
  (it asks the language the project will have).

Language, mindsets branches and overlay, lint, test levels, deploy are left out:
`/dev:j-new-project` decides them while it designs the project and writes them into this file, lint gate
included.

### 16. Write and commit
`j-settings.md` with the sections above that have values, and the header line
`# Base settings — j-new-project completes them`. Commit it alone:
`git add j-settings.md .claude/settings.json <what step 0b wrote> && git commit -m "chore(j-setup): base settings"`.

### 17. Report
The base settings, the keys left for `/dev:j-new-project`, what the user declined in step 0, and the next
command: `/dev:j-new-project` — or `/dev:bbc-analyze`, for a project designed as black boxes; with the CI/CD asked for in step 0, `/dev:j-ci-setup` after its first plan.

---

## PROFILE GIVEN (called by /dev:j-new-project or /dev:bbc-core)

### 18. Complete the settings from the profile
`/dev:j-new-project` — or `/dev:bbc-core`, for a project designed as black boxes — hands over what it decided with the user: the project's name, language, kind, the
mindsets branches and overlay files, the base library, the exposure. Nothing is scanned and nothing is asked again:
1. Write the keys of step 11 from the profile into `j-settings.md` — the test levels in the forms of
   the language's overlay (step 8) — keeping the base settings already there; the header line
   `# Base settings — j-new-project completes them` goes.
2. Wire the lint gate with step 7 for each component's language — the native configuration files go
   where its §7 says, in the repository of the project to come, except for a component its §7 says gets them
   after its scaffold: there the keys are written now, and the files come with its first block — and
   `ast-grep` is installed when missing.
3. Report what was written. The command that called — `/dev:j-new-project` or `/dev:bbc-core` — commits it with its plan.

---

## VALIDATE MODE (j-settings.md exists)

### 20. Read and repair
```bash
cat j-settings.md
```
Repairs, made silently:
- A name in `@mindsets-branches` or `@mindsets-overlay` that has no file under `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/` → reported and
  set from the profile detection of step 5.
- Keys of the old mindsets (`@senior-mindset`, `@foundations-mindset`, `@tddab-lang-overlay`,
  `@engine-overlay`, `@bdd-overlay`, `@csharp-mindset`) → replaced by the `## Mindsets` section, built
  from step 5, shown to the user before writing.
- Keys that no file of the set reads (`@tddab-file`, `@frontend-method`, `@chromedevtools`,
  `@mindsets-dir`, the ports, the database keys…) → listed, and removed on confirmation.
- `@start-<component>` missing → from step 8.
- `@code-nav-local` / `@code-nav-external` / `@own-code-roots` / `@vendored-globs` missing →
  detected as in step 9.
- Settings written as base settings (header from step 16) on a project that now has build files →
  completed as an EXISTING PROJECT: steps 3-9, the questions of step 10, the confirmation of step 11
  and the commit of step 12, the base settings already there kept.
- `## Linting` missing or partial → the missing keys only, from step 7.
- Any other key of step 11 that the project's components call for, missing (a frontend key only when
  there is a frontend) → found with the step that writes it (3-9); what the scan cannot establish is
  asked as in step 10.
- Lint configuration files that differ from the pack (`${CLAUDE_PLUGIN_ROOT}/lint-rules/<language>/native/`, and
  `sgconfig.yml` from its template, the rules under `.ast-grep/` when `.ast-grep/VERSION` is not
  `${CLAUDE_PLUGIN_ROOT}/VERSION`) → show the diff and, on confirmation, bring them to the pack's
  version; a line the project added on purpose is kept, asking. A template the language's §7 merges into
  another file is compared there, in that file: it is not a file of the project.
- The tools of step 0 and `ast-grep` → checked again; a missing `ast-grep` is installed as in step 7.
- `## CI/CD` missing → what step 9 lists: a pipeline (`.github/workflows/`, `.gitlab-ci.yml`) or a
  branch on the remote other than the main and the dev branch. Either one → asked: which branch is the
  production branch, whether the merge to it is automatic or by hand, the platform → `@production-branch`,
  `@ci-merge`, `@ci-platform`, and nothing of the pipeline is changed. Neither → `@production-branch: none`.

Every key already present and its order are kept: a second run adds what is missing and changes
nothing that is already right.

### 21. Show and choose
Show the settings by section; then: keep them, change a setting, re-scan the project, or start from
scratch (delete `j-settings.md` and go to step 2). Kept → what the repairs changed is committed as step
12 says.

---

## Rules of this command
- **Scan first**: detect everything the project shows.
- **Ask only the unknowns**, with AskUserQuestion.
- **Leave out what is not known**: a missing key is filled by the command that learns it.
- **Propose, then confirm** before writing.
- **Keep the user's edits** in validate mode.
- It writes `j-settings.md`, `sgconfig.yml`, the lint configuration files and what the test levels need
  (step 8), and commits exactly those — in PROFILE GIVEN the command that called (`/dev:j-new-project`, `/dev:bbc-core`) commits them with its plan.
