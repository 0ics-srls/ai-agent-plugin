# Contributing

Thank you for wanting to make these skills better. Read this page first: this repository works a
little differently from most.

## This repository is generated

The plugins here are built from a source set by a script, and every release overwrites the files of
this repository. So:

- **An issue is always welcome**, and it is the best way to start.
- **A pull request is welcome as a proposal.** It is not merged here: the maintainer applies the
  change to the source, and it comes back with the next release, with you credited as co-author of
  the commit. A pull request that is accepted is closed with a link to the release that carries it.
- Small fixes — a typo, a wrong command, a broken path — need no issue first. For anything larger,
  open an issue and agree on the change before writing it.

## What a good change looks like

The product is the text of the skills: pages an agent reads and follows. A change is judged by what
the agent does after reading it.

- **Say what you saw.** Which command, on which kind of project, with which model, what the agent
  did, and what it should have done. A transcript excerpt is worth more than a description; remove
  what is private.
- **Say how you tried the change.** The same command run again with your text, and what the agent
  did then. A change nobody ran is a guess.
- **One change per pull request**, and the smallest text that does it. A page grows heavier for
  every reader with each sentence added.
- **Write for the weakest reader.** The same page is followed by a large model and by a small one:
  each step says what to do and what tells that it is done.
- **English**, plain and direct. The pages are instructions, not documentation.

## What is declined

So that nobody spends time on it:

- **Style, naming and formatting rules in the lint gates.** A gate keeps only the rules that find a
  defect; the lists are explicit, one rule at a time, and each has its reason. A proposal to add a
  rule says which defect it finds and shows it finding one in real code.
- **Lists of forbidden types or symbols.** A rule of the mindsets names a practice and why it hurts,
  language by language; it is not turned into a ban list.
- **A rule added to fix one case.** If the agent went wrong once, the page that should have
  prevented it is corrected; a new rule is the last resort.
- **Changes that make a skill do something the user did not ask for**, write outside the project,
  or reach the network on their own.

## The licence of your contribution

The plugins are under the Mozilla Public License 2.0 (see `LICENSE`). By proposing a change you
agree that it is published under the same licence, and you confirm that you have the right to
contribute it.

## Conduct

See `CODE_OF_CONDUCT.md`. In short: be precise, be kind, and talk about the text, not the person.
