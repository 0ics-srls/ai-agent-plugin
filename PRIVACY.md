# Privacy policy

This policy covers the plugins of this repository — `dev`, `biz`, `info` and `ai-agent` — published by
0ics srl.

## What the plugins collect

Nothing. The plugins are text pages an agent reads, configuration templates, and one Python tool
that runs on your machine. They have no telemetry, no analytics, no account, no server of their own,
and they send no data to the author or to anyone else.

## Where your data stays

Everything the plugins produce is written in the project you run them in — settings, plans, the
Memory Bank, the task folders, the audit's files — or in Claude Code's own folders on your machine.
It stays there until you delete it, and it is shared only if you commit and push it yourself.

## Who else is involved

The plugins work inside other software, each under its own terms, not under this policy:

- **Claude Code and the model behind it.** Your conversation, the pages of the plugins and the files
  the agent reads are processed by the provider of your agent, under your agreement with them.
- **Tools the commands install or run at your request**: the linters and compilers of your project's
  languages, `ast-grep`, and the Python packages of the audit tool. Installing them downloads them
  from their public registries (npm, PyPI and the like).
- **The App Store Compliance Playbook, when you run `/store:store-setup`.** The command clones it from
  its author's repository on GitHub into `~/repositories/app-store-compliance`, after asking you, and
  `/store:store-audit` runs its scripts on your machine against your app's project. It is the work of
  Mirza Iqbal under the OpenRoots Agent License 2.3: its terms, not this policy, govern it.
- **MCP servers you choose in `/j-mcp-setup`.** Each one is optional and is configured only when you
  pick it. Some are services on the network — for example a web search server, or the `claude-chat`
  relay at `cc-chat.0ics.ai`, which is operated by 0ics srl and carries the
  messages agents exchange through it, only when you configure it with a key. What a server receives
  is governed by that server's own terms.
- **The web.** The `biz` and `info` commands have the agent search and read web pages, through the
  search and fetch tools of your agent.

## Children

The plugins are tools for software development and are not directed at children.

## Changes

A change to this policy is a change to this file, visible in the repository's history and published
with a new version of the plugins.

## Contact

0ics srl — mail@0ics.it. A question that can be public may also be an issue in this repository.
