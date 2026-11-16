# ai-agent — Claude Code plugins

**v2.31.43** — the ai-agent skill set by 0ics srl, as a catalogue of Claude Code plugins. This
repository is generated from the set's source at each release: its files are not edited here (see
[CONTRIBUTING.md](CONTRIBUTING.md)).

| Plugin | What it is |
|---|---|
| `dev` | Software development: the junior workflow (`j-*`), the black-box method (`bbc-*`), the code audit, the mindsets and the lint gates |
| `biz` | The funnel of the startup ideas (`biz-*`) |
| `info` | Research verified (`info-*`) |
| `ai-agent` | All three: it has nothing of its own, it installs `dev`, `biz` and `info` |

Each one is installed, enabled and disabled by itself.

## Before you install

Git on your machine must be able to clone the repository without asking for anything: Claude Code
does not show git's prompts. Check:

```
git ls-remote https://github.com/0ics-srls/ai-agent-plugin.git
```

## Install

1. Register the catalogue — once per machine:

```
claude plugin marketplace add 0ics-srls/ai-agent-plugin
```

2. Install the plugins you want. For one project, from the project's folder — it is written in the
   project's `.claude/settings.json`, which is committed, and everybody who works on the project
   still runs this command once:

```
claude plugin install dev@ai-agent --scope project
```

   Or for every project on this machine:

```
claude plugin install dev@ai-agent
```

   `biz@ai-agent` and `info@ai-agent` the same way; `ai-agent@ai-agent` installs the three.
   The same from inside a session: `/plugin marketplace add 0ics-srls/ai-agent-plugin`, then
   `/plugin install dev@ai-agent`.

3. Start Claude Code again in the project, then `/j-setup` (or `/dev:j-setup`), then `/j-help`.
   `biz` and `info` need no setup: `/biz-help`, `/info-help`.

## Choose per project

A plugin installed for the machine can be switched off in one project, and on again:

```
claude plugin disable biz@ai-agent --scope project
claude plugin enable biz@ai-agent --scope project
```

## What `/j-setup` leaves in the project

- `j-settings.md`: the project's settings, its lint gate and its test commands;
- the linter's configuration files of the project's languages;
- `.ast-grep/`: the set's ast-grep rules, copied, with `.ast-grep/VERSION` — the version of the set
  they come from — and `sgconfig.yml` that names them. They are in the project so that its gate runs
  in a pipeline too, where the plugin is not installed;
- `.claude/settings.json`: one rule, `Read(~/.claude/plugins/cache/ai-agent/**)`, that lets the
  agent read the plugins' own pages without a prompt at each one. `/j-setup` asks before adding it;
- when the project does not have them: `CLAUDE.md`, `.mcp.json`, `memory-bank/` with its README.

## Update

```
claude plugin marketplace update ai-agent
claude plugin update dev@ai-agent          # each plugin installed; add --scope project when it was installed so
```

Then start Claude Code again. Updates are not automatic for this catalogue; they can be turned on in
`/plugin` → Marketplaces. After an update, `/j-setup` in a project compares the lint files and
`.ast-grep/` with the new version and proposes to bring them to it.

## Remove

```
claude plugin uninstall dev@ai-agent
claude plugin marketplace remove ai-agent
```

## A project that has the set as a git submodule

With the submodule (`.ai-agent/`) and the plugin together every command is there twice: a project
uses one or the other. To move a project to the plugin: close or commit the work in progress,
install `dev` for the project, start Claude Code again and run `/dev:j-setup`. It finds the
submodule and asks; on a yes it removes the links in `.claude` and the submodule, replaces the
linked `memory-bank/README.md` with a copy, writes `sgconfig.yml` and `.ast-grep/` again, shows
what else still names the submodule (a pipeline, a script) and commits.

## Issues, contributions, security, privacy

- [SUPPORT.md](SUPPORT.md) — what an issue needs and what to expect.
- [CONTRIBUTING.md](CONTRIBUTING.md) — this repository is generated: how a change gets in, what a
  good one looks like, what is declined.
- [SECURITY.md](SECURITY.md) — how to report a vulnerability, and what the plugins do on your machine.
- [PRIVACY.md](PRIVACY.md) — the plugins collect nothing.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

Copyright (c) 2026 0ics srl. [Mozilla Public License 2.0](LICENSE).

In short: use it for anything, commercial work included, and distribute it; when you distribute a
file of this repository that you changed, that file stays under the MPL 2.0 and its source is made
available. Your own project is not touched by this: the code and the documents the agent writes
with these skills are yours.

Additional permission: the files `/j-setup` copies into your project — the linter's configuration,
the ast-grep rules under `.ast-grep/`, `sgconfig.yml`, the starter `CLAUDE.md`, `.mcp.json` and
`memory-bank/README.md` — may be used, changed and distributed there without any condition.
