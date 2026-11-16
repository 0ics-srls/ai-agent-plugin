# Issues and support

## Before opening an issue

- Update to the latest version: `claude plugin marketplace update ai-agent`, then
  `claude plugin update <plugin>@ai-agent`, and start Claude Code again.
- Search the open and closed issues: the same thing may be there already.
- A security problem does not go in an issue: see `SECURITY.md`.

## What an issue is for

| Kind | What it needs |
|---|---|
| **Bug** — a command does not do what its page says, a path is wrong, a gate fails on correct code or passes a defect | The plugin and its version, the version of Claude Code, the system, the model; the command you ran; what happened and what you expected; the part of the transcript that shows it |
| **Proposal** — a change to a skill, a mindset, a lint gate | The problem first: what the agent did, on what kind of project, and why it is wrong. Then, if you have one, the change |
| **Question** — how something is meant to be used | What you are trying to do and what you tried |

Remove from what you paste anything private: code that is not yours to publish, names, keys.

One issue, one subject. Two problems are two issues.

## What to expect

- This project is maintained by a very small team, in the time there is. There is no guaranteed answer
  time and no paid support.
- A bug that can be reproduced is fixed in the source and comes back with the next release; the
  issue is closed with the version that carries the fix.
- A proposal gets a yes, a no with its reason, or a question. `CONTRIBUTING.md` says what is
  declined as a rule, so that nobody spends time on it.
- An issue waiting for an answer from its author for 30 days is closed. It can be reopened with the
  answer.
- An issue about Claude Code itself, about a model's behaviour in general, or about a linter's own
  bug belongs to those projects, and is closed with a pointer to them.

## Labels

`bug`, `proposal`, `question`; then `dev`, `biz`, `info` for the plugin; `needs-info` while waiting
for the author; `accepted` and `declined` for a proposal's outcome.
