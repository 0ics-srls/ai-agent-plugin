# ai-agent — a development workflow for Claude Code

**v2.31.52** · by 0ics srl · [how it works](FLOW.md)

`dev` is a Claude Code plugin that makes the agent work the way a careful developer does: it listens
before it reads, looks for what already exists before it writes, has you approve the structure and
then the plan, builds test-first one small block at a time, and closes only when the project's gate
is green. Every step leaves something written in the project, so the work survives the end of a
session.

```
you: what you need  →  the agent: what exists, the structure  →  you approve
                    →  a test-first plan, reviewed             →  you approve
                    →  built block by block, a commit each     →  gate green, merged
```

It comes with the rules it follows — how code is organized, in 14 languages and their frameworks —
with a lint gate per language that keeps only the rules that find a defect, with a method for
projects too large for one context window, and with an audit of an existing codebase.

## Install

1. Register the catalogue — once per machine:

```
claude plugin marketplace add 0ics-srls/ai-agent-plugin
```

2. Install the plugin. For one project, from the project's folder — it is written in the project's
   `.claude/settings.json`, which is committed, and everybody who works on the project still runs
   this command once:

```
claude plugin install dev@ai-agent --scope project
```

   Or for every project on this machine:

```
claude plugin install dev@ai-agent
```

   The same from inside a session: `/plugin marketplace add 0ics-srls/ai-agent-plugin`, then
   `/plugin install dev@ai-agent`.

3. Start Claude Code again in the project.

Git on your machine must be able to clone the repository without asking for anything: Claude Code
does not show git's prompts. Check with `git ls-remote https://github.com/0ics-srls/ai-agent-plugin.git`.

## Start

Every command is typed with the plugin's name in front.

| | |
|---|---|
| `/dev:j-setup` | First, once per project: it finds the language, the stack and the commands, asks only what it cannot see, writes `j-settings.md` and wires the lint gate |
| `/dev:j-new-project` | A new project, from what it must be to the plan of its skeleton — or an existing one, described and given its Memory Bank |
| `/dev:j-new-feature` | A feature: you say what you need, and it goes up to a reviewed plan |
| `/dev:j-step` | A feature a piece at a time: you say a piece, it is built as one test-first block, you check, and say the next |
| `/dev:j-bug` | A bug: the cause proved first, then the plan of the fix |
| `/dev:j-cvm-exec-plan` | Executes the plan, block by block |
| `/dev:j-close` | Runs the gate, merges, optionally deploys |
| `/dev:j-save` · `/dev:j-continue` · `/dev:j-status` | Leave, resume, see where the work stands |
| `/dev:j-help` | All the commands |

**[FLOW.md](FLOW.md)** has the whole picture: the phases and what each one leaves, the diagrams of
which command comes when, the method for large projects (`/dev:bbc-*`), the audit of the code
(`/dev:x-audit-code`), and the rules the agent reads.

The plan is executed by the CVM plan executor, an MCP server: `/dev:j-mcp-setup` installs it, with
the code-navigation servers the workflow can use.

## What `/dev:j-setup` leaves in the project

- `j-settings.md`: the project's settings, its lint gate and its test commands;
- the linter's configuration files of the project's languages;
- `.ast-grep/`: the set's ast-grep rules, copied, with `.ast-grep/VERSION` — the version of the set
  they come from — and `sgconfig.yml` that names them. They are in the project so that its gate runs
  in a pipeline too, where the plugin is not installed;
- `.claude/settings.json`: one rule, `Read(~/.claude/plugins/cache/ai-agent/**)`, that lets the
  agent read the plugin's own pages without a prompt at each one. `/dev:j-setup` asks before adding it;
- when the project does not have them: `CLAUDE.md`, `.mcp.json`, `memory-bank/` with its README;
- in `CLAUDE.md` — or in your own `CLAUDE.local.md` — who works with the agent: `/dev:j-setup` asks whether
  you are a programmer, a junior or someone who does not program, and in which language to talk to you.
  For the last two the agent explains in plain words and, when you say what you want, proposes the
  command that does it.

## Update

```
claude plugin marketplace update ai-agent
claude plugin update dev@ai-agent          # add --scope project when it was installed so
```

Then start Claude Code again. Updates are not automatic for this catalogue; they can be turned on in
`/plugin` → Marketplaces. After an update, `/dev:j-setup` in a project compares the lint files and
`.ast-grep/` with the new version and proposes to bring them to it.

## One project only, or not this one

A plugin installed for the machine can be switched off in one project, and on again:

```
claude plugin disable dev@ai-agent --scope project
claude plugin enable dev@ai-agent --scope project
```

To remove it: `claude plugin uninstall dev@ai-agent`, and `claude plugin marketplace remove ai-agent`
for the catalogue.

## A project that has the set as a git submodule

With the submodule (`.ai-agent/`) and the plugin together every command is there twice: a project
uses one or the other. To move a project to the plugin: close or commit the work in progress,
install `dev` for the project, start Claude Code again and run `/dev:j-setup`. It finds the
submodule and asks; on a yes it removes the links in `.claude` and the submodule, replaces the
linked `memory-bank/README.md` with a copy, writes `sgconfig.yml` and `.ast-grep/` again, shows
what else still names the submodule (a pipeline, a script) and commits.

## Issues, contributions, security, privacy

- [SUPPORT.md](SUPPORT.md) — what an issue needs and what to expect.
- [CONTRIBUTING.md](CONTRIBUTING.md) — this repository is generated from the set's source at each
  release, so its files are not edited here: how a change gets in, what a good one looks like, what
  is declined.
- [SECURITY.md](SECURITY.md) — how to report a vulnerability, and what the plugin does on your machine.
- [PRIVACY.md](PRIVACY.md) — the plugins collect nothing.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## The other plugins of this catalogue

The catalogue has two more plugins, for work that is not software development. They stand on their
own: neither needs `dev`, and `dev` needs neither.

| Plugin | What it does | Start |
|---|---|---|
| `biz` | A funnel for startup ideas: an idea is captured, scored, checked against the software that already exists, researched on its market, validated on its assumptions, and turned into the specification of an MVP — which `dev` can then build | `/biz:biz-help` |
| `info` | Research that is verified: facts gathered with their sources, cross-referenced against independent ones, audited for reliability and bias, reported with a confidence level each | `/info:info-help` |
| `ai-agent` | Nothing of its own: it installs `dev`, `biz` and `info` together | — |

```
claude plugin install biz@ai-agent
claude plugin install info@ai-agent
claude plugin install ai-agent@ai-agent     # all three
```

Each one is installed, updated, enabled and disabled by itself, like `dev`.

## License

Copyright (c) 2026 0ics srl. [Mozilla Public License 2.0](LICENSE).

In short: use it for anything, commercial work included, and distribute it; when you distribute a
file of this repository that you changed, that file stays under the MPL 2.0 and its source is made
available. Your own project is not touched by this: the code and the documents the agent writes
with these skills are yours.

Additional permission: the files `/dev:j-setup` copies into your project — the linter's configuration,
the ast-grep rules under `.ast-grep/`, `sgconfig.yml`, the starter `CLAUDE.md`, `.mcp.json` and
`memory-bank/README.md` — may be used, changed and distributed there without any condition.
