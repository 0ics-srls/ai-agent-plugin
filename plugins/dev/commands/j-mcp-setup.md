---
description: Install and configure MCP servers for the project. Universal — works with both Claude Code (.mcp.json / mcpServers) and opencode (opencode.jsonc / mcp). Interactive — asks which MCPs to add, auto-installs everything, merges into the right config. Use when user says mcp setup, add mcp, configura mcp, or wants to enable AI tooling.
---

## Prerequisites
- The project's language, which decides the framework servers the catalog offers: from `/dev:j-setup`
  when it runs this command, otherwise from `@language` in `j-settings.md` (in a monorepo, each
  `@language-<component>`), otherwise asked with AskUserQuestion.

## Step 0: Detect host & resolve config targets

Detect which agent runtime this project targets:
- **opencode** if any present: `opencode.json` / `opencode.jsonc` in root, a `.opencode/` directory, or `AGENTS.md` (and no `.claude/`).
- **Claude Code** if any present: `.claude/` directory, `CLAUDE.md`, or `.mcp.json`.
- If BOTH (or neither is clear) → ask with AskUserQuestion which runtime to configure.

Resolve these targets from the detected host and use them everywhere below:

| Target | Claude Code | opencode |
|---|---|---|
| **PROFILE_CFG** (user-wide) | `~/.claude.json` — only its `mcpServers` is read and written: the file holds the rest of Claude Code's state | `~/.config/opencode/opencode.json` |
| **PROJECT_CFG** | `.mcp.json` | `opencode.jsonc` |
| **ROOT_KEY** | `mcpServers` | `mcp` |
| **GUIDE_FILE** | `CLAUDE.md` | `AGENTS.md` |
| **Empty skeleton** | `{"mcpServers":{}}` | `{"mcp":{}}` |

## Config format mapping (canonical → host)

Every config block below is written in **canonical (Claude) form**. Emit it under ROOT_KEY:
- **Claude Code** → use the snippet **as-is** under `mcpServers`.
- **opencode** → under `mcp`, transform each entry:
  - **stdio** (`command` + `args` [+ `env`]) → `{ "type":"local", "command":[<command>, <...args>], "enabled":true, "environment":{<env>} }`
    (merge `command`+`args` into ONE array; rename `env`→`environment`; omit `environment` if there is no env).
  - **http / remote** (`type:"http"`|`"stdio"` with a `url`) → `{ "type":"remote", "url":<url>, "enabled":true }`
    (add `headers` only if the canonical block carries auth).

Example — canonical `cvm` → **opencode**:
```json
"cvm": {
  "type": "local",
  "command": ["npx", "-y", "cvm-server@latest"],
  "enabled": true,
  "environment": { "CVM_STORAGE_TYPE": "file", "CVM_DATA_DIR": ".cvm", "CVM_LOG_LEVEL": "info", "CVM_SANDBOX_PATHS": "." }
}
```

## Step 1: Detect what's ALREADY installed (BOTH locations!)

Check the two config files for the host — user-wide AND project-level:
```bash
echo "=== User-wide ===" && python3 -c "import json,os,sys;print(sorted(json.load(open(os.path.expanduser(sys.argv[1]))).get(sys.argv[2],{})))" PROFILE_CFG ROOT_KEY 2>/dev/null || echo "[]"   # the names only: the file holds secrets
echo "=== Project ===" && cat PROJECT_CFG 2>/dev/null || echo "{}"
```

Parse ROOT_KEY keys from BOTH files. An MCP installed at user level works in ALL projects — don't offer to install it again.

Show: "Already installed (user): [list]" and "Already installed (project): [list]"

## Step 2: Show FULL catalog, ask which to install

Show ALL available MCPs in ONE table, marking installed ones and WHERE they're installed.

```
=== MCP SERVER CATALOG ===

CODE INTELLIGENCE
  [ ] lsai            — Compiler-grade code navigation (10 languages, 14 tools)
  [ ] xmp4            — Code intelligence via SCIP for third-party libraries
  [ ] vs-mcp          — Visual Studio semantic analysis               [csharp]

FRAMEWORK-SPECIFIC
  [ ] primeng         — PrimeNG component docs, props, theming (Angular) [typescript]
  [ ] angular-cli     — Angular CLI integration                        [typescript]
  [ ] nx-mcp          — Nx workspace architecture, generators (Nx monorepos) [typescript]
  [ ] laravel-boost   — Laravel tools — DB, artisan, tinker, docs        [php]

DEVELOPMENT TOOLS
  [ ] chrome-devtools — Browser automation — click, type, screenshot
  [ ] cvm             — Claude Virtual Machine — autonomous task execution
  [ ] ui-ticket-mcp   — UI ticket review with browser overlay
  [ ] brave-search    — Web search via Brave API
  [ ] claude-chat     — Chat between Claude Code sessions (rooms, direct messages)

Legend: [u]=user-wide  [p]=project  [ ]=not installed
```

A server tagged `[language]` is offered only when that language is one of the project's (the
Prerequisites); a server without a tag is offered to every project. `laravel-boost` is offered only when
`composer.json` has `laravel/framework`.

Use AskUserQuestion with multiSelect. Show only MCPs NOT already installed (in either location).
Ask in rounds by category (max 4 options per question).
Skip rounds where all MCPs in that group are already installed.

## Step 3: Ask config questions for selected MCPs

After ALL selections, ask ONLY for MCPs that need user input:
- **ui-ticket-mcp** → ASK: port (default 3200)
- **cvm** → ASK: data dir (default .cvm)
- **brave-search** → ASK: BRAVE_API_KEY
- **xmp4** → ASK: install user-wide or project-only?
- **claude-chat** → ASK: the agent's name in the chat (default: the project's folder name) and the API
  key

## Step 3b: The runners the selected servers need

Each server starts through a runner; a missing runner is installed here, before Step 4.

| Runner | Servers | Install (Linux / macOS / WSL) | Install (Windows) |
|---|---|---|---|
| `npx` (Node.js LTS) | primeng, angular-cli, nx-mcp, chrome-devtools, cvm, brave-search | the system package manager (`apt-get install -y nodejs npm`, `brew install node`) | `winget install OpenJS.NodeJS.LTS` |
| `uvx` (uv) | ui-ticket-mcp | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| `bunx` (Bun) | claude-chat | `curl -fsSL https://bun.sh/install \| bash` | `powershell -c "irm bun.sh/install.ps1 \| iex"` |

```bash
command -v npx uvx bunx
```
After an install, the runner is checked again with `<runner> --version`.

## Step 4: AUTO-INSTALL everything

For each selected MCP, run the installation AND write the config (translated per Step 0 mapping). The user should do NOTHING.

### lsai — AUTO-INSTALL
**Detect OS and install automatically:**

**Windows (native or detected via `USERPROFILE` env var):**
```powershell
iwr https://github.com/0ics-srls/Zerox.Lsai.Public/releases/latest/download/install.ps1 -OutFile $env:TEMP\lsai-install.ps1; & $env:TEMP\lsai-install.ps1
```
Skip if `%USERPROFILE%\.lsai\run.cmd` already exists.

**Linux / macOS / WSL:**
```bash
curl -fsSL https://github.com/0ics-srls/Zerox.Lsai.Public/releases/latest/download/install.sh | bash
```
Skip if `~/.lsai/run` already exists.

Config (write to **PROJECT_CFG** — per-project, LSAI needs project context):

**Windows:**
```json
"lsai": {
  "command": "C:\\Users\\{USERNAME}\\.lsai\\run.cmd",
  "args": ["--stdio"]
}
```
Use absolute path with `run.cmd` — MCP configs don't expand `~`.

**Linux / macOS / WSL:**
```json
"lsai": {
  "command": "/home/{USERNAME}/.lsai/run",
  "args": ["--stdio"]
}
```
Use the absolute path (resolve `$HOME` and substitute) — MCP configs don't expand `~` on Linux either.

### xmp4 — CONFIG ONLY (no install needed)
If user chose user-wide → write to **PROFILE_CFG**
If user chose project → write to **PROJECT_CFG**
```json
"xmp4": {
  "type": "http",
  "url": "https://mcp.example4.ai/mcp"
}
```
(`mcp.example4.ai` is the REAL production endpoint — not a placeholder, do not "fix" it.)

### vs-mcp — CONFIG ONLY (no install needed, VS provides it)
Write to **PROJECT_CFG** (port is project-specific):
```json
"vs-mcp": {
  "type": "http",
  "url": "http://localhost:3001/sdk/"
}
```

### primeng — CONFIG ONLY (npx auto-downloads on first use)
Write to **PROJECT_CFG**:
```json
"primeng": {
  "command": "npx",
  "args": ["-y", "@primeng/mcp"]
}
```

### angular-cli — CONFIG ONLY (npx auto-downloads)
Write to **PROJECT_CFG**:
```json
"angular-cli": {
  "command": "npx",
  "args": ["-y", "@angular/cli", "mcp"]
}
```

### nx-mcp — CONFIG ONLY (npx auto-downloads)
Write to **PROJECT_CFG**:
```json
"nx-mcp": {
  "type": "stdio",
  "command": "npx",
  "args": ["nx-mcp@latest"]
}
```

### laravel-boost — AUTO-INSTALL
```bash
composer require laravel/boost --dev
php artisan boost:install
```
Skip if `composer.json` already has `laravel/boost`.

Write to **PROJECT_CFG**:
```json
"laravel-boost": {
  "command": "php",
  "args": ["artisan", "boost:mcp"]
}
```

### chrome-devtools — CONFIG ONLY (npx auto-downloads)
Write to **PROJECT_CFG**:
```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest", "--no-sandbox", "--disable-setuid-sandbox"]
}
```

### cvm — CONFIG ONLY (npx auto-downloads)
Write to **PROJECT_CFG**:
```json
"cvm": {
  "command": "npx",
  "args": ["-y", "cvm-server@latest"],
  "env": {
    "CVM_STORAGE_TYPE": "file",
    "CVM_DATA_DIR": ".cvm",
    "CVM_LOG_LEVEL": "info",
    "CVM_SANDBOX_PATHS": "."
  }
}
```

### ui-ticket-mcp — AUTO-INSTALL (backend + frontend)

**Step A: Install backend (MCP server)** — `uvx` comes from Step 3b.

Write to **PROJECT_CFG**:
```json
"ui-ticket-mcp": {
  "command": "uvx",
  "args": ["ui-ticket-mcp"],
  "env": {
    "PROJECT_ROOT": ".",
    "REVIEW_PORT": "{PORT}"
  }
}
```

**Step B: Install frontend panel**
```bash
npm install ui-ticket-panel
```

**Step C: Add component to the app automatically**
Find the root component of the project:
- Angular → look for `src/index.html`
- React → look for `public/index.html` or `src/index.html`
- Vue → look for `index.html` or `public/index.html`
- Plain HTML → look for `index.html`
- If j-settings exists, its frontend component (`@lint-frontend`, `@start-frontend`) names the folder

Once found, add BEFORE `</body>`:
```html
<script type="module" src="https://unpkg.com/ui-ticket-panel/dist/bundle.js"></script>
<review-panel api-url="http://localhost:{PORT}/api"></review-panel>
```

If using a bundler (detected from package.json having angular/react/vue):
- Also add to the main entry file (main.ts, main.tsx, main.js):
```typescript
import { defineReviewPanel } from 'ui-ticket-panel';
defineReviewPanel();
```

The `api-url` port MUST match the `REVIEW_PORT` in PROJECT_CFG.

### brave-search — CONFIG ONLY (npx auto-downloads)
Write to **PROFILE_CFG** (user-wide — generic tool):
```json
"brave-search": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "{KEY}"
  }
}
```

### claude-chat — CONFIG ONLY (bunx auto-downloads)
Write to **PROJECT_CFG**, with the name and the key asked in Step 3:
```json
"claude-chat": {
  "command": "bunx",
  "args": ["cc-chat-mcp"],
  "env": {
    "CLAUDE_CHAT_NAME": "{AGENT_NAME}",
    "CLAUDE_CHAT_URL": "wss://cc-chat.0ics.ai",
    "CLAUDE_CHAT_API_KEY": "{API_KEY}"
  }
}
```
The key lives in PROJECT_CFG by the project owner's choice.

## Step 5: Write configs (merge, never overwrite)

For each target file (**PROJECT_CFG** and/or **PROFILE_CFG**):
1. Read existing content (or start with the host's **Empty skeleton**)
2. Translate each selected MCP to the host format (Step 0 mapping) and add it under **ROOT_KEY** — do NOT remove existing ones
3. Write merged result — every other key of the file kept as it was (PROFILE_CFG of Claude Code holds
   the whole user state)
4. Validate JSON: `python3 -m json.tool <file>`
   (opencode `opencode.jsonc` accepts plain JSON; if the existing file has comments, preserve them or write `opencode.json` instead.)

## Step 5-bis: The working directories stay out of the repository

An MCP server that writes inside the project leaves a working directory there — machine-specific
data that changes every session. Committed by accident, it is noise in every diff and a conflict
in every merge.

**The list of base entries is owned by the setup script that wired ai-agent into the project
(`setup-base.sh`, and its Windows twin `setup.ps1`)**, which guarantees them in the root `.gitignore`
idempotently on every setup and every re-run:
`.cvm`, `.lsai/`, `problem-chrome-dt/`. **Do NOT re-implement that logic here**, and do not tell the user
to add those entries — they are already there, and saying otherwise is stale advice.

What this command owns is knowing WHICH directory each MCP creates:

| MCP | What it writes in the project |
|---|---|
| cvm | `.cvm/` (file storage, `CVM_DATA_DIR`) — in the base list |
| lsai | `.lsai/` (index) — in the base list |
| chrome-devtools | `problem-chrome-dt/` (the screenshots `/dev:j-browse` and `/dev:j-e2e` save) — in the base list |
| every other one | if it writes inside the project, its directory is ignored the same way |

So: for each MCP you configured, check that its working directory is ignored. If it is in the
base list, it already is — say nothing. If it is not (a server the base list does not know), add
that one entry to the root `.gitignore` in the same shape the scripts use — one line, never
duplicated — and report it under what you DID, not under advice.

## Step 6: Update j-settings.md — Code Navigation

If `j-settings.md` exists, update `@code-nav-local` and `@code-nav-external` in its
`## Code Navigation` with the rule of `/dev:j-setup` step 9 (the one owner of that rule), reading both
config files of the host.

## Step 7: Update GUIDE_FILE — Code Navigation section

Read project's **GUIDE_FILE** (`CLAUDE.md` or `AGENTS.md`). Find or create `## Code Navigation` section
and write, for the servers configured:
- own code → the `@code-nav-local` server (lsai or vs-mcp), with its symbol, outline and usage tools;
- third-party library APIs → xmp4, when configured;
- the rule for every lookup: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md` (preflight, readiness,
  scope, a negative verdict only with the quoted result); text search only as its declared fallback.
Only modify `## Code Navigation` — do NOT touch other sections.

## Step 7-bis: Commit what this command produced

The configuration is this command's product. Commit **only its own files**, by path:

```bash
git add .mcp.json <or opencode.jsonc> .gitignore CLAUDE.md <or AGENTS.md> j-settings.md
# .gitignore only if Step 5-bis touched it, j-settings.md only if Step 6 changed it
git commit -m "chore(mcp): configure <the servers you added>"
```

Never the whole tree: a commit that carries what the command did not produce is not a point to
return to, it is noise. If the working tree has other pending changes, leave them alone and say
so in the summary. A user-wide config (PROFILE_CFG) lives outside the project and is not
committed.

## Step 8: Summary

```
✅ MCP servers installed and configured:
  + lsai (installed + configured in PROJECT_CFG)
  + chrome-devtools (configured in PROJECT_CFG)
  + ui-ticket-mcp (backend configured + frontend panel added to src/index.html)
  • xmp4 (already installed in PROFILE_CFG)

Restart the agent (Claude Code / opencode) to activate new MCP servers.
```

Only show "⚠️ Action required" for things that genuinely need user action (like replacing a placeholder API key).

## Rules
- NEVER tell user to install something manually — DO IT
- NEVER tell the user to add an entry to `.gitignore` — the base list is guaranteed by the setup
  script, and anything beyond it you add yourself (Step 5-bis)
- NEVER remove existing MCP entries — only add/update
- Resolve the host (Step 0) FIRST — every path/format/key below derives from it
- Check BOTH PROFILE_CFG AND PROJECT_CFG before offering MCPs
- User-wide MCPs (xmp4, brave-search) → PROFILE_CFG
- Project MCPs (lsai, vs-mcp, cvm, chrome-devtools, ui-ticket, primeng, angular-cli, nx-mcp, laravel-boost, claude-chat) → PROJECT_CFG
- A selected server whose runner is missing gets the runner installed first (Step 3b)
- xmp4 defaults to user-wide (explores external libraries, not project-specific)
- Translate every block to the host format (canonical → host) before writing
- Detect OS for platform-specific installers (LSAI: bash vs PowerShell)
- For ui-ticket-mcp: install BOTH backend AND frontend, modify HTML automatically
- Validate JSON before writing
- Ask ALL selection questions FIRST, config questions AFTER, install LAST
