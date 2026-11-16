# Security

## Supported versions

Only the latest released version is supported. A fix is published as a new version of the plugins;
update with `claude plugin marketplace update ai-agent`, then `claude plugin update <plugin>@ai-agent`.

## Reporting a vulnerability

Report it privately: the **Report a vulnerability** button under the repository's **Security** tab
(GitHub private vulnerability reporting), or write to mail@0ics.it. Please do not open a public issue
for it.

Say which plugin and version, what an attacker has to control (a file of the project, a web page the
agent reads, an argument of a command), and what happens. You will get an answer as soon as the
maintainer can; there is no guaranteed time. A report that is confirmed is credited in the release
that fixes it, unless you ask otherwise.

## What counts

These plugins are instructions an agent follows, plus one local Python tool. A vulnerability here is,
for example:

- a page that makes the agent do something harmful or something the user did not ask for: delete or
  overwrite outside the project, send data out, weaken a permission, hide what it did;
- a hidden or obfuscated instruction in any file;
- a command or a script of the plugins that runs content it should treat as data — a file name, a
  line of the audited code, the text of a web page;
- a lint or audit configuration that executes code from the project being checked in a way its own
  tools do not already do.

A linter rule that is too strict or too loose, or an agent that plans badly, is a bug: open an issue.

## What the plugins do on your machine

So that you can judge them before installing:

- **They run under Claude Code's permissions.** Every shell command and every file written goes
  through the agent, which asks you as your permission mode says. The plugins ship no hook, no
  background process and no MCP server of their own.
- **They write in the project you run them in**: settings (`j-settings.md`), the linter's
  configuration, the ast-grep rules under `.ast-grep/`, the Memory Bank, the task folders, the plans,
  the audit's files under `audit/`.
- **One permission rule, asked first.** `/j-setup` asks before adding to the project's
  `.claude/settings.json` the rule `Read(~/.claude/plugins/cache/ai-agent/**)`, which lets the agent
  read the plugins' own pages without a prompt at each one. It is a read rule on the plugins' folder
  and nothing else; declined, everything works with a prompt per read.
- **They install tools only when a command says so and you run it**: the linters of your project's
  languages, `ast-grep`, the audit's Python packages in a virtual environment under `audit/.tools/`,
  and the MCP servers you choose in `/j-mcp-setup`.
- **They do not reach the network on their own.** There is no telemetry and no call home. Network
  access happens only through the tools above and through what you ask the agent to do — the `biz`
  and `info` commands search the web, because that is their job.
