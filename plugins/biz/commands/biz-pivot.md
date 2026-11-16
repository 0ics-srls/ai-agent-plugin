---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Pivot an existing idea - fork into a new direction while preserving history. Use when user says pivot, cambiamo direzione, fork the idea, nuova variante dell'idea.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Pivots an existing idea by forking it into a new variant. The original idea is marked as `pivoted` and a new idea is created with a link to its parent, preserving the full decision history.

## Steps

### 1. Select Idea to Pivot

Read `ideas/registry.md`. Show ideas that are candidates for pivot (status: evaluated, researched, validated, mvp-specced, or building).

Ask the user which idea to pivot. If they already specified one, confirm it.

### 2. Understand the Pivot

Read all existing files for this idea (evaluation, research, validation, techscape, mvp-spec - whatever exists).

Ask:
```
What's changing in this pivot? Help me understand:

1. Is the PROBLEM different, or the same problem with a different SOLUTION?
2. Is the TARGET AUDIENCE different?
3. What triggered this pivot? (research findings, user feedback, market change, gut feeling)
```

### 3. Classify the Pivot Type

Based on the conversation, classify:

| Pivot Type | What Changes | What Stays |
|---|---|---|
| **Customer pivot** | Target audience | Core problem/solution |
| **Problem pivot** | Problem focus | Target audience |
| **Solution pivot** | How we solve it | Problem + audience |
| **Channel pivot** | Distribution/delivery | Product concept |
| **Revenue pivot** | Monetization model | Product + audience |
| **Technology pivot** | Tech stack/approach | Business model |

Tell the user the pivot type and confirm.

### 4. Create the Fork

Assign next available ID. Use format: `IDEA-{NN}` (normal sequential ID).

In the new registry entry, add a `Pivoted from:` field linking to the parent idea.

Structure the new idea:
- **One-liner**: Updated for the pivot direction
- **Problem**: What problem are we solving now?
- **Who**: Who has this problem?
- **Current alternatives**: How do they solve it today?
- **Your angle**: What's different about our approach?
- **Pivot from**: `IDEA-{parent}` - {pivot type} pivot
- **What we're keeping**: List what carries over (research, validation, tech, contacts)

### 5. Carry Forward Relevant Work

Determine what from the original idea still applies:

- **Evaluation**: Re-score only changed dimensions. Copy unchanged scores.
- **Research**: If market/competitors still relevant, reference original research file. Note what's different.
- **Validation**: Mark which validations still hold and which need re-testing.
- **Techscape**: If tech decisions still apply, reference original. Note changes.

If enough carries over to skip a stage, suggest it:
```
The market research from IDEA-{parent} still applies to this pivot.
I suggest we start from `biz-validate` instead of `biz-research`.
```

### 6. Update Registry

**Original idea:**
- Change status to `pivoted`
- Add note: `Pivoted to IDEA-{new} ({pivot type} pivot) - {date}`

**New idea:**
- Add entry with status `captured` (or higher if work carries over)
- Score: carry over adjusted score, or `-/60` if major changes
- Add `Pivoted from: IDEA-{parent}`

### 7. Create Pivot Record

Create file `ideas/evaluations/{new-slug}.md` with a pivot section:

```markdown
# {New Idea Title}

## Pivot History
- **Pivoted from**: IDEA-{parent} ({original title})
- **Pivot type**: {customer|problem|solution|channel|revenue|technology}
- **Trigger**: {what caused the pivot}
- **What carries over**: {list}
- **What's new**: {list}

## Evaluation
{carried over or new scores}
```

### 8. Summary

```
PIVOT COMPLETE

Original: IDEA-{parent} "{title}" -> status: pivoted
New:      IDEA-{new} "{title}" -> status: {status}
Type:     {pivot type} pivot

Carried over:
  {list of what was preserved}

Needs fresh work:
  {list of what needs to be redone}

Next step: `biz-{next-command}` to {what needs doing}
```

### 9. Update Memory Bank

Update activeContext.md with pivot activity. Update productContext.md if this changes the current product direction.

## Rules
- NEVER delete the original idea's files - they're history
- Be honest about what carries over and what doesn't. A customer pivot invalidates most market research. A solution pivot might keep it all.
- If the pivot is so radical that nothing carries over, say so - it might be better to just `biz-capture` a new idea
- Don't let the user pivot to avoid killing a bad idea. If the core problem is weak, pivoting the solution won't fix it.
- Update Memory Bank with pivot activity
