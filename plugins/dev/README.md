# dev — a plugin of the ai-agent catalogue

**v2.31.55** — Software development with an agent that writes well-organized code: the junior workflow (j-*), the black-box method (bbc-*), the code audit, the mindsets and the lint gates.

Start in a project with `/dev:j-setup`, which records the project's settings and wires its lint gate, then `/dev:j-help` lists the commands: a feature or a bug goes from what the user needs to a reviewed test-first plan, executed block by block, and is closed with the gate green. `/dev:j-setup` writes in the project: `j-settings.md`, the linter's configuration, the ast-grep rules under `.ast-grep/`, a rule in `.claude/settings.json` that lets the agent read this plugin's pages, and, when missing, `CLAUDE.md`, `.mcp.json` and `memory-bank/`.

Install: `claude plugin marketplace add 0ics-srls/ai-agent-plugin`, then `claude plugin install dev@ai-agent`. How it
works, with the diagrams of which command comes when: https://github.com/0ics-srls/ai-agent-plugin/blob/master/FLOW.md —
how to update, what the plugin writes in a project and the other plugins of the catalogue are in the
repository's README: https://github.com/0ics-srls/ai-agent-plugin

Copyright (c) 2026 0ics srl. Mozilla Public License 2.0, see LICENSE.
