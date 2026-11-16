---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Score and evaluate a captured idea against startup criteria (6 dimensions, /60). Use when user says evaluate the idea, valuta l'idea, quanto vale, score it, ohodnot napad.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- `ideas/registry.md` must exist. If it doesn't:
  ```
  No idea registry found. Run `biz-capture` to start capturing ideas.
  ```
  STOP.

## What This Command Does

Takes a captured idea and scores it against 6 dimensions to decide: research further, park, or kill.

## Steps

### 1. Select Idea

Read `ideas/registry.md`. List ideas with status `captured` or ask user which to evaluate:
```
Which idea do you want to evaluate?

Unevaluated ideas:
- IDEA-01: {title}
- IDEA-03: {title}

Or type an ID directly.
```

### 2. Review the Idea

Read the registry entry. Summarize back to user:
```
IDEA-{NN}: {one-liner}
Problem: {problem}
Who: {target}
```

### 3. Score Together

Go through each dimension with the user. For each, discuss briefly then agree on a score:

| # | Dimension | Question | Score |
|---|-----------|----------|-------|
| 1 | **Problem Severity** | How painful is this? (1=meh, 10=desperate) | ?/10 |
| 2 | **Market Size** | How many people/businesses have this? | ?/10 |
| 3 | **Willingness to Pay** | Would they pay? How much? | ?/10 |
| 4 | **Competition** | How crowded? (1=saturated, 10=wide open) | ?/10 |
| 5 | **Your Advantage** | Unique insight, skill, or access? | ?/10 |
| 6 | **Feasibility** | MVP in weeks, not months? | ?/10 |

For each dimension, provide your honest assessment first, then ask user if they agree or want to adjust.

### 4. Calculate and Recommend

```
Total: {sum}/60

Recommendation (>= 25 is research-eligible — consistent with biz-help):
- Below 25: Park it. Not worth the time right now. (status → `parked`)
- 25-35: Borderline. Research-eligible (`biz-techscape` then `biz-research`) ONLY if you're passionate — otherwise park it.
- 35-45: Worth researching. Run `biz-techscape` then `biz-research` next.
- 45+: Strong candidate. Definitely research this.
```

### 5. Create Evaluation File

Create `ideas/evaluations/{idea-slug}.md`:
```markdown
# Evaluation: IDEA-{NN} - {title}

**Date**: {today}
**Score**: {total}/60

## Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Problem Severity | {n}/10 | {brief note} |
| Market Size | {n}/10 | {brief note} |
| Willingness to Pay | {n}/10 | {brief note} |
| Competition | {n}/10 | {brief note} |
| Your Advantage | {n}/10 | {brief note} |
| Feasibility | {n}/10 | {brief note} |

## Key Strengths
- {strength 1}
- {strength 2}

## Key Risks
- {risk 1}
- {risk 2}

## Recommendation
{park/research/strong candidate} - {reasoning}
```

### 6. Update Registry

Update the idea's entry in `ideas/registry.md`:
- Set **Score** to `{total}/60`
- Set **Status** to `evaluated`
- Add **Files**: `evaluations/{idea-slug}.md`
- If score < 25 (or 25-35 without passion): set **Status** to `parked` AND move to "Parked Ideas" section

### 7. Summary

```
IDEA-{NN} scored {total}/60 → {recommendation}

{If research recommended}:
Run `biz-techscape` (what exists, the cheap scan), then `biz-research` for the deep market analysis.

{If parked}:
Parked - it's still in the registry if you want to revisit.

You have {N} ideas ready for research.
```

## Rules
- Be HONEST. Don't inflate scores to be nice
- Challenge the user's assumptions constructively
- If user can't answer "who would pay for this?" - that's a signal
- Compare to other evaluated ideas when relevant: "IDEA-03 scored higher on feasibility"
- Update MB with evaluation activity
