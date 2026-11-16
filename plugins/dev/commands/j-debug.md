---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Debug a problem while looking for it, with Protocol D, explaining each step (junior workflow). It finds and explains the cause and changes no production code — a bug is fixed with j-bug. Full verbose mindset — use when context window is not a concern. For large context sessions use j-debug-mb instead.
---

## Prerequisites
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `j-settings.md` at the repository root (missing → run `/j-setup` first).
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/junior.md`
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/debug-protocol-e2e.md` — the method across the
  layers; it includes `debug-protocol.md`, Protocol D itself, which is read with it and not twice.
- `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/code-navigation.md`, followed for every code lookup of ISOLATE (the
  tools of `@code-nav-local` and `@code-nav-external`; a text search is the declared fallback when the
  tool is absent or not ready).

## Purpose

Debugging while a problem is being looked for: Protocol D applied step by step, and every step
explained as it is taken — what is read and why, what it rules out, why the hypothesis follows from the
evidence — so that the user sees how the problem is debugged. No branch, no folder: it finds and
explains the cause, and changes no production code. A bug is fixed with `j-bug`, which carries the diagnosis into
its plan; a block of a plan under execution is fixed in that plan's FIX.

Use this when:
- Something doesn't work and you don't know why
- You need to investigate before deciding if it's a bug or missing feature
- A plan's FIX or a red gate needs the cause found and explained

## Steps

### 1. The components the problem crosses

The project's components are in `j-settings.md` — `@language-<component>` and `@start-<component>`
(one `@language` and one `@start-<component>` for a project of one component) — with their branches.
For each, where its errors show is its overlay's `language.md` §7 ("Where its errors show"); the logs
of a process are where the logger's configuration writes them (`branches/operations.md` 1). A
component whose language has no overlay: its process output and its logs.

Ask the user with AskUserQuestion — the options are the components by name, plus:
- between two of them (a call from one to the other fails, or answers the wrong thing);
- don't know (let's find out).

### 2. Gather Initial Info

- What should happen, and what happens instead?
- The exact error, where it shows (one of the places of step 1)?
- When did it start? Any recent changes?
- For a component with a user interface: which page or screen, and what the user does.

### 3. Pre-Debug Checklist

Verify before debugging:

```
Components:
- [ ] Every component the problem crosses running? (start: its `@start-<component>` of j-settings.md)
- [ ] The storage reachable, where the project has one?

Evidence ready:
- [ ] Where each component's errors show (step 1) is open: the logs, the console, the output
- [ ] The problem can be reproduced
```

If something not running → start it first, then continue.

### 4. Protocol D - READ

**Find ALL error sources** — one per component the problem crosses, where step 1 says its errors show.

**Output required**, one line per component:
```
**<COMPONENT> ERROR**: [the exact message, quoted, or "none"]
```

### 5. Protocol D - ISOLATE

**Find which component OWNS the problem:**

Trace the flow across the components it crosses, from the input to the result:
```
input → component A did its part? → handed over to B? → B did its part? → … → result?
```

Find where it breaks:
- Last step that worked = ✓
- First step that failed = ✗ ← **This is your target**

**Output required:**
```
**FAILING COMPONENT**: [the component, or the hand-over between two]
**LAST SUCCESS**: [what worked]
**FIRST FAILURE**: [what failed]
**LOCATION**: [file:line if known]
```

### 6. Protocol D - DOCS

If the error involves framework/library:
- Check official docs
- Verify correct version
- Look for known patterns

Skip if it's clearly business logic bug.

### 7. Protocol D - HYPOTHESIZE

**BEFORE touching any code:**

```
**HYPOTHESIS**: [what I think causes the error]
**REASONING**: [why I think this - cause-effect chain]
**PREDICTION**: [what will change after fix]
```

Rules:
- Must be falsifiable (you can test it)
- Must explain ALL symptoms
- No "let's try" - only "I believe X because Y"

Ask user:
```
My hypothesis: [explanation]

Does this match what you're seeing? Should I investigate further or proceed?
```

### 8. Protocol D - VERIFY

**ONE change at a time** — a diagnostic one: a trace log, a probe, a test that reproduces the problem.
The fix itself is not made here, and every diagnostic change is removed once the cause is found —
a test that reproduces the bug too: it is described with the cause, and j-bug's plan writes it as its
RED.

After change:
```
**CHANGE**: [single change made]
**RESULT**: [actual outcome]
**PREDICTION MATCH**: [yes/no]
**CONCLUSION**: [what we learned]
```

If prediction wrong → go back to READ with new information.
If prediction correct → problem understood.

### 9. Decision Point

After Protocol D completes:

```
Problem found: [summary]
Location: [file:line]
Cause: [explanation]

Options:
1. It's a bug → use j-bug: its DIAGNOSE starts from this one
2. It's actually a feature → use j-new-feature
3. It's the block of a plan under execution → back to its FIX, with this cause
4. Need more investigation

What do you want to do?
```

### 10. Update MB

Set in `activeContext.md`:
```
@lastDebug::{description}
@debugResult::{found|needsMore|wasBug|wasFeature}
```

## Rules

- **Protocol D always** - READ, ISOLATE, DOCS, HYPOTHESIZE, VERIFY
- **No guessing** - evidence from logs required
- **One change at a time** - never multiple changes without verifying
- **Quote exact errors** - no paraphrasing
- **Component first** - know WHERE before explaining WHAT
- **No fix here** - the cause is found and explained; the fix is j-bug's, or the running plan's FIX
- **Explain each step** - what was read, what it rules out, why the next step follows
- **Ask if unsure** - use AskUserQuestion to clarify

## Quick Reference

```
RIDHV = Read → Isolate → Docs → Hypothesize → Verify
         ↑                                      ↓
         └────────── if wrong ──────────────────┘

Each component: where its overlay's §7 says its errors show
A process: its logs (branches/operations.md 1)

Always ask: "Which component OWNS this problem?"
```
