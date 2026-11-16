---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: 'Initialize a project''s secret management with git-crypt (a .00-secrets/ folder transparently encrypted in git). Run in the EARLY phase of a project. Installs git-crypt, configures .gitattributes/.gitignore, generates the key and tells the user to save it in a password manager, writes a runbook + security guide. SAFE/idempotent: if git-crypt is already initialized it does NOT re-init (reuses the key); if a secrets dir already has content it stops and destroys nothing. Use when "init secrets", "setup git-crypt", "secret management", new project.'
---

# /j-init-secrets — secret setup with git-crypt (.00-secrets/)

> ⚠️ ASSUME THE EXECUTOR KNOWS NOTHING ABOUT THE PROJECT. Follow the steps literally.
> Generic command — works for ANY project and ANY developer. Do NOT add project-specific content.
> Goal: ALL project secrets live in **`.00-secrets/`** (the exceptions are rule 2 of `docs/SECURITY.md`), encrypted with **git-crypt** (transparent:
> plaintext locally, encrypted in git). No vault, no custom tool, no symlinks.
>
> 🌐 **LANGUAGE RULE: everything you WRITE (README, docs, comments, file messages) = ENGLISH.**

## 🛑 STEP 0 — SAFETY (check before touching anything)
```bash
git rev-parse --show-toplevel 2>/dev/null || echo "NO_GIT"
[ -e .git/git-crypt ] && echo "GITCRYPT_ALREADY_INIT"
{ [ -d .00-secrets ] && [ -n "$(ls -A .00-secrets 2>/dev/null | grep -vx README.md)" ]; } && echo "SECRETS_DIR_HAS_CONTENT"
ls -d secrets vault private .secrets 2>/dev/null
```
- `NO_GIT` → 🛑 STOP: "not a git repo, run `git init` first." Do NOT proceed.
- `SECRETS_DIR_HAS_CONTENT`, or another secrets dir (`secrets/`,`vault/`,`private/`,`.secrets/`) exists
  → 🛑 STOP: do NOT delete, do NOT overwrite. This is a MIGRATION (inventory + move + rewire paths),
  not this command. Report `ls -la` and ask the user.
- `GITCRYPT_ALREADY_INIT` → ⚠️ NOT a stop: **SKIP STEP 2** (re-init would regenerate the key and
  ORPHAN existing encrypted secrets). Reuse the existing key, continue STEP 3+ creating only what is
  MISSING. (This makes the command safe to re-run to finish a partial setup.)

**ABSOLUTE RULE: NEVER delete/overwrite/empty an existing secrets dir or key. Create only what is missing.**

## STEP 1 — Install git-crypt
```bash
git-crypt --version 2>/dev/null || sudo apt-get install -y git-crypt    # Debian/Ubuntu (macOS: brew install git-crypt)
git-crypt --version
```

## STEP 2 — git-crypt init (SKIP if STEP 0 reported GITCRYPT_ALREADY_INIT)
```bash
git-crypt init
```

## STEP 3 — .gitattributes (create if missing; if it exists APPEND only the missing lines)
```
.00-secrets/** filter=git-crypt diff=git-crypt
.00-secrets/README.md !filter !diff
```

## STEP 4 — .gitignore — CRITICAL override (APPEND at the end if missing)
Patterns like `*.key *.pem *.env credentials*` would also match `.00-secrets/<file>` → git-crypt
could not track them. Add:
```
# .00-secrets/ = git-crypt (tracked, encrypted). Overrides ALL rules above.
!.00-secrets/**
```
VERIFY: `git check-ignore .00-secrets/.key` → **empty** output = git tracks it. ✓

## STEP 5 — Create the folder + README (README in ENGLISH, EXACT text below)
```bash
mkdir -p .00-secrets
```
Write `.00-secrets/README.md` with EXACTLY this content:
```markdown
# .00-secrets/ — project secrets (git-crypt)

This folder holds ALL project secrets, encrypted with git-crypt.
Files are plaintext in your working tree, encrypted in git (commits/remote).

Rules:
- Put EVERY secret here. Nothing secret lives outside this folder.
  Only exceptions: personal/per-developer files, the git-crypt key itself (kept in a password manager),
  and the API keys the project owner chose to keep in the MCP configuration (`.mcp.json`, `opencode.jsonc` or `opencode.json`).
- On a new machine: `git-crypt unlock <key-from-your-password-manager>` before using the repo.
- Full runbook: `docs/git-encryption.md`.
- The git-crypt key is the ONLY backup — if lost, encrypted secrets are unrecoverable.
```

## STEP 6 — 🔑 Generate and HAND OVER the key (CRITICAL)
```bash
(umask 077; git-crypt export-key - | base64 -w0 > git-crypt.key)
# Guarantee the key is NEVER tracked — do NOT rely on a pre-existing *.key rule (a fresh repo has none).
git check-ignore -q git-crypt.key || echo 'git-crypt.key' >> .gitignore
git check-ignore git-crypt.key    # must now PRINT the path = ignored. If still empty → STOP, do not commit anything.
test -s git-crypt.key && echo "the key is in git-crypt.key"
```
<BASE_RULE>
**The key never passes through you.** You do not read `git-crypt.key`: no `cat`, no Read, no `base64`, no `grep`, no export to a
terminal you can see, not even to check it. What a command prints reaches the model and stays in the transcript, and a key that was read
is a key that has leaked. You check only that the file exists and is not empty, and that it is ignored. The user reads it, in a terminal
of their own: not with the `!` prefix, whose output comes into this conversation.
</BASE_RULE>

Then TELL the user, plainly, and show no key:
- "🔑 Your git-crypt key (base64) is in `git-crypt.key`. In a terminal of your own, outside this agent: `cat git-crypt.key`, and **SAVE IT NOW in your password manager.**"
- "⚠️ It is the **ONLY backup**. Without it, encrypted secrets are **UNRECOVERABLE**."
- "After saving it, **delete** `git-crypt.key` from the repo (`shred -u git-crypt.key`)."
- "New machine, in your own terminal: `read -rs K; printf '%s' "$K" | base64 -d > k; unset K; git-crypt unlock k; shred -u k`."
**Do NOT delete `git-crypt.key` yourself** — the user deletes it after saving it.

## STEP 7 — Documentation (ENGLISH, create if missing — do NOT overwrite existing)
Create these files with the EXACT text given (the runbook does NOT exist yet and nobody else has it —
you MUST write it in full, verbatim, not just reference it).

### docs/git-encryption.md — EXACT content (ENGLISH)
```markdown
# git-encryption.md — repo secrets encrypted with git-crypt

Secret system for this repo: **git-crypt**. All secrets live in `.00-secrets/` (the exceptions are rule 2
of `docs/SECURITY.md`), encrypted in git,
plaintext in your working tree.

## New machine / fresh clone (files look like binary / start with GITCRYPT)
    sudo apt-get install -y git-crypt          # Debian/Ubuntu (macOS: brew install git-crypt)
    read -rs K                                 # paste the base64 from the password manager: not echoed, not in the history
    printf '%s' "$K" | base64 -d > /tmp/k; unset K
    git-crypt unlock /tmp/k && (shred -u /tmp/k 2>/dev/null || rm -f /tmp/k)
    git-crypt status | grep 00-secrets         # now decrypted (plaintext)

## Daily use (already unlocked)
- Add/edit secrets in `.00-secrets/` → `git add` + `git commit` = encrypted automatically.
- `git pull` / `git checkout` = decrypted automatically in the working tree.
- Nothing secret goes outside `.00-secrets/`, except personal/per-developer files, the git-crypt key
  itself, and the API keys the project owner chose to keep in the MCP configuration (`.mcp.json`, `opencode.jsonc` or `opencode.json`).

## Key management
- Export (backup / another machine), in your own terminal, never through an agent: `git-crypt export-key - | base64 -w0`
  → save the base64 in your password manager.
- ⚠️ Without the key, encrypted secrets are UNRECOVERABLE. Only backup = password manager.

## Verify
    git check-ignore .00-secrets/.key              # empty = git tracks it (not ignored)
    git-crypt status | grep 00-secrets             # encrypted
    git show HEAD:.00-secrets/<file> | head -c 9 | grep -a GITCRYPT   # match = encrypted in the repo
```

### docs/SECURITY.md — non-violable rules (below).
- `CLAUDE.md`: add a `## Secrets (git-crypt)` section so ANY future agent or developer knows WHERE secrets
  are, HOW to access them, and WHY. If `CLAUDE.md` does not exist, create it. Insert EXACTLY:
```markdown
## Secrets (git-crypt)

Secrets live in `.00-secrets/`, transparently encrypted with git-crypt: plaintext in your working
tree, encrypted in git. Put EVERY secret there — nothing secret goes elsewhere (only exceptions:
personal/per-developer files, the git-crypt key itself, and the API keys the project owner chose to keep in the MCP configuration (`.mcp.json`, `opencode.jsonc` or `opencode.json`)).

- New machine / fresh clone: run `git-crypt unlock <key>` (key from your password manager) BEFORE
  building or running anything — otherwise `.00-secrets/` files are unreadable (still encrypted).
- The git-crypt key is the ONLY backup → keep it in a password manager.
- Runbook: `docs/git-encryption.md` · non-violable rules: `docs/SECURITY.md`.
```

### docs/SECURITY.md — minimal content (ENGLISH)
```markdown
# Security (non-violable rules)

1. Every secret lives ONLY in `.00-secrets/` (git-crypt). Never elsewhere, never plaintext in git.
2. Only exceptions: personal/per-developer files and the git-crypt key (password manager, out-of-band),
   and the API keys the project owner chose to keep in the MCP configuration (`.mcp.json`, `opencode.jsonc` or `opencode.json`), named there.
3. Never commit secret values in config/manifests/scripts → reference the secret instead of inlining it
   (the exception of rule 2 aside).
4. The git-crypt key is the ONLY backup → password manager. Lost = secrets unrecoverable.
5. On a new machine: `git-crypt unlock` BEFORE using/building the project.
```

## STEP 8 — FINAL CHECK (everything must pass, real end-to-end test)
Run this block: it prints `SETUP OK` only if every check passes, otherwise it says what is broken.
```bash
fail=0
git-crypt status >/dev/null 2>&1 || { echo "✗ git-crypt not active"; fail=1; }
[ -z "$(git check-ignore .00-secrets/.key 2>/dev/null)" ] || { echo "✗ .00-secrets/ is gitignored (missing !.00-secrets/** in .gitignore)"; fail=1; }
grep -q '.00-secrets/\*\* filter=git-crypt' .gitattributes 2>/dev/null || { echo "✗ .gitattributes missing git-crypt rule"; fail=1; }
[ -f .00-secrets/README.md ] || { echo "✗ .00-secrets/README.md missing"; fail=1; }
[ -f git-crypt.key ] || { echo "✗ git-crypt.key not generated (key to hand over)"; fail=1; }
printf 'probe: ok\n' > .00-secrets/_probe.yaml
# The blob is encrypted when it enters the index: the probe is staged, checked, and unstaged — no commit.
git add .gitattributes .00-secrets/_probe.yaml
# NOTE: grep -aq (NOT grep -q). Encrypted blobs start with a NUL byte (\0GITCRYPT\0…);
# without -a grep treats input as binary → FALSE NEGATIVE. Do not remove -a.
if git show :.00-secrets/_probe.yaml 2>/dev/null | head -c 9 | grep -aq GITCRYPT; then echo "✓ probe ENCRYPTED in the index"; else echo "✗ probe NOT encrypted → git-crypt not encrypting (recheck STEP 3/4)"; fail=1; fi
git rm -q --cached .00-secrets/_probe.yaml && rm -f .00-secrets/_probe.yaml
[ "$fail" -eq 0 ] && echo "✅ SETUP OK — git-crypt configured, .00-secrets encrypted, key ready" || echo "❌ SETUP INCOMPLETE — fix the ✗ above before adding secrets"
```
Do NOT tell the user "done" until the check prints `✅ SETUP OK`. If `❌`, fix the `✗` items and re-run the check.

## STEP 9 — Commit what this command produced
Only its own files, by path — never `git-crypt.key`, which stays ignored until the user deletes it:
```bash
git add .gitattributes .gitignore .00-secrets/README.md docs/git-encryption.md docs/SECURITY.md CLAUDE.md
git commit -m "chore(secrets): git-crypt for .00-secrets/"
```
A file that already existed and was not touched is not staged; other pending changes stay as they
are, and the report names them.

## NOTES — gotchas (read before debugging git-crypt; do not regress)

**Verifying a blob is encrypted → use `grep -aq GITCRYPT`, never `grep -q`.**
git-crypt blobs start with a NUL byte then the magic: `\0 GITCRYPT \0 …`. Plain `grep -q GITCRYPT`
(and `tr -d '\000' | grep`) gives a FALSE NEGATIVE — the NUL makes grep treat the input as binary
and report no match. `-a` forces text mode. This bit STEP 8 once; the fix is the `-a`. To inspect
raw bytes use `git show HEAD:<file> | head -c 12 | od -c` (expect `\0 G I T C R Y P T \0`).

**`git-crypt status -e` is a WEAK check** — it lists files by their *.gitattributes attribute*, not
by actual blob content. A file can show "encrypted" there while its committed blob is still plaintext.
Trust the raw-blob probe (`git show HEAD:<file> | grep -a GITCRYPT`) for real proof.

**The key is PER-PROJECT, never per-user.** It lives at `<project>/.git/git-crypt/keys/default`
(a random AES key generated by `git-crypt init`, unique to that repo). There is NO global/per-user
git-crypt key (no `~/.config/git-crypt`). `git config filter.git-crypt.*` is only the *command*, not
the key. So N repos = N independent keys. Since `.git/` is local and never pushed/cloned, a fresh
clone / new machine has NO key → `git-crypt unlock <key>` is required before the secrets are readable.

**Key backup = password manager, one entry per repo** (entry name = repo name → base64 of the key).
Re-export anytime, in the user's own terminal and never through the agent: `git-crypt export-key - | base64 -w0`.

**Make bootstrap/build self-explaining (automatic for the next agent).** Any script that sources a
`.00-secrets/` file should first detect the still-locked state and fail with an actionable message,
instead of dying on binary garbage:
```bash
if head -c 9 .00-secrets/<file> | grep -aq GITCRYPT; then
  die ".00-secrets/ is ENCRYPTED — run: git-crypt unlock <key-from-password-manager>"
fi
```
