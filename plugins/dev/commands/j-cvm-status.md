---
description: "Turn the status line of Claude Code on or off — the git branch, the model, and the CVM's progress bar while a plan runs — for this project or for the user. Use when the user says /dev:j-cvm-status on, off, status line, riga di stato, barra CVM, accendi o spegni la barra."
---

# CVM status line

While `/dev:j-cvm-exec-plan` executes a plan, the status line at the bottom of the terminal shows where it
is: `⎇ feature/27-image-viewer  Fable 5.2  ██████░░░░░░░░ 3/7 03-image-cache [GREEN]`. With no plan
running it shows the branch and the model. The line is drawn by
`${CLAUDE_PLUGIN_ROOT}/support/statusline/statusline.py`; this command switches it with
`${CLAUDE_PLUGIN_ROOT}/support/statusline/install.py`, which is the only thing that writes the settings.

## Steps

### 1. The action and the scope
From what the user wrote after the command:
- the action: `on`, `off`, or `status` when nothing is said;
- the scope, when the user names one: `project` — this project on this machine, written in
  `.claude/settings.local.json`, which is not committed — or `user` — every repository of this user,
  written in `~/.claude/settings.json`, with a copy of the script in `~/.claude/`. Not named → it is
  left out, and the installer chooses: the project when the set is in the project, the user otherwise.

### 2. Run the installer
In the project's root folder, with `python3`, or `python` where `python3` does not answer:
`python3 ${CLAUDE_PLUGIN_ROOT}/support/statusline/install.py <action> [<scope>]`

### 3. Report
Its answer, as it is: one line that starts with `status line:` (`status` gives one per level, and the
level Claude Code uses). When it did nothing, the line says why — another status line is already set
in that file, and it is the user's: it is not replaced; the settings file is not valid JSON; in this
project the set is a plugin, and the scope is `user`. Nothing is edited by hand to get around it: the
user decides.

## What to know
- It is on by default: the set's setup turns it on for the project — where the set is a plugin,
  `/dev:j-setup` does, for the user — unless the user already has a status line, or switched it off here:
  `off` leaves `.claude/statusline.off`, and the setup respects it.
- The line changes as soon as the settings are saved; no restart.
- `project` writes the path of the project on this machine: the same folder opened from another
  system (Windows and WSL) needs `on` there too, or `user`.
- Requirements: `python3` (or `python`) and `git` on the PATH; `.cvm/` in the project's root.
