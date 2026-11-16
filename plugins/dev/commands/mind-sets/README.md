# Mind-sets

Three levels. The first holds for every project; the branches hold for the projects that have that
part; the overlay says how both are written in the language.

## 1. Every project

1. `principles.md` — the principles of a good software system: search, structure, errors, configuration, build.
2. `code-principles.md` — how the code is written and designed: data and types, writing, KISS/DRY/SOLID, mechanisms.
3. `testing-principles.md` — what a test proves, and a suite that stays fast as it grows.

## 2. The branches — by what the project has

| The project has | Branch |
|---|---|
| a service that keeps data and exposes it | `branches/service-layers.md` |
| a storage | `branches/data.md` |
| a contract exposed over the network | `branches/api.md` |
| calls outside its own process | `branches/resilience.md` |
| a process others depend on | `branches/operations.md` |
| exposure to callers it does not control | `branches/security.md` |
| a user interface on the project's API | `branches/frontend.md` |
| a real-time loop: a game, a simulation | `branches/game.md` |

## 3. The overlay — by language

The overlay of a language is its folder, `overlays/<language>/`: how both levels above are written in
that language. Its `language.md` §7 says how the language is recognized, which of its files go with
which branch, and what `/dev:j-setup` and `/dev:j-new-project` read from it. A language with no folder under
`overlays/` has no overlay yet: its projects follow levels 1 and 2 alone.

## 4. The process and the plans

- `development-workflow.md` — the phases of a piece of work, what each one does and leaves.
- `junior.md` — the commands of the junior workflow on those phases.
- `tddab-planner.md`, `step-planner.md` — how a plan is written, with the language's `tddab.md`.
- `code-navigation.md` — every lookup in the code.
- `debug-protocol.md` — Protocol D, the debugging method; `debug-protocol-mb.md` the same in MBEL,
  `debug-protocol-e2e.md` its extension across the layers.
- `bdd-overlay.md` — on request only, with the language's `bdd.md`.
- `bbc.md` — the method of the black boxes, for a project too large for one context window; read by
  the `bbc-*` commands.
- `audit.md` — the cards of the code audit: what is verified by reading the code, and how it is
  decided; read by `/dev:x-audit-code`.
