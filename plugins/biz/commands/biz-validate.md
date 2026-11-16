---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Validate key assumptions with evidence before committing to MVP development. Use when user says validate, valida le ipotesi, test assumptions, overit predpoklady - the gate before biz-mvp-spec.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Idea should be researched first (run `biz-research`)

## What This Command Does

Identifies and tests the riskiest assumptions about an idea before committing to building an MVP. Creates a validation plan and tracks evidence.

## Steps

### 1. Select Idea

Read `ideas/registry.md`. Show ideas with status `researched`:
```
Which idea do you want to validate?

Researched ideas:
- IDEA-02: {title} (Research verdict: GO)
```

Read both the evaluation and research files.

### 2. Identify Key Assumptions

Every startup idea is built on assumptions. Extract the top assumptions that MUST be true:

```
IDEA-{NN}: {title}

Your idea assumes:
1. {assumption about the problem} - e.g., "Developers waste >2hrs/week on X"
2. {assumption about willingness to pay} - e.g., "Teams would pay $50/mo for this"
3. {assumption about solution} - e.g., "An AI can do this better than manual"
4. {assumption about market} - e.g., "Enough small teams exist that need this"
5. {assumption about differentiation} - e.g., "Competitors don't serve {segment}"

Which of these keeps you up at night? Which feels most uncertain?
```

### 3. Rank by Risk

With user, rank assumptions by:
- **Impact if wrong**: Would the whole idea collapse?
- **Certainty**: How confident are we this is true?

Focus on: HIGH impact + LOW certainty assumptions first.

### 4. Design Validation Tests

For each critical assumption, propose a lightweight test:

| Assumption | Test | Evidence Needed | Effort |
|-----------|------|-----------------|--------|
| "People have this problem" | Find forum posts, Reddit threads, support tickets | 10+ independent mentions | 1 hour web search |
| "They'd pay $X/mo" | Find competitor pricing, survey if possible | Comparable pricing exists | 30 min research |
| "AI can solve this" | Quick prototype or existing proof | Technical feasibility demo | 1-2 days |
| "Market is big enough" | Bottom-up calculation from research | Credible numbers | Already done |

Prioritize tests that are:
- **Fast** (hours, not weeks)
- **Cheap** (free or near-free)
- **Informative** (clearly proves or disproves)

### 5. Execute Together

Work through the validation tests with the user:
- Use WebSearch to find evidence
- Search Reddit, HackerNews, ProductHunt, forums
- Look for existing demand signals (people asking for this)
- Check Google Trends for related terms
- Find relevant surveys or reports

### 6. Score Each Assumption

After testing, rate each:
- **Validated** - Strong evidence supports it
- **Plausible** - Some evidence, not conclusive
- **Questionable** - Weak evidence or mixed signals
- **Invalidated** - Evidence against it

### 7. Create Validation Report

Create `ideas/validations/{idea-slug}.md`:
```markdown
# Validation: IDEA-{NN} - {title}

**Date**: {today}

## Assumptions Tested

### 1. {Assumption}
- **Status**: Validated / Plausible / Questionable / Invalidated
- **Test**: {what we did}
- **Evidence**: {what we found}
- **Sources**: {links}

### 2. {Assumption}
...

## Validation Checklist

- [x/] Talked to potential users (or found proxy evidence)
- [x/] Identified competitors and differentiation
- [x/] Clear monetization model exists
- [x/] MVP scope is definable
- [x/] Can describe product in one sentence
- [x/] Know who first 10 users would be

## Overall Assessment

**Confidence Level**: {High / Medium / Low}
**Critical Blockers**: {any invalidated assumptions?}

## Decision

{PROCEED TO MVP / PIVOT / PARK}

**If PROCEED**: Key constraint for MVP is {X}. Run `biz-mvp-spec`.
**If PIVOT**: The problem is real but solution needs rethinking. Specifically: {what to change}. Run `biz-pivot`.
**If PARK**: {why and what would need to change to revisit}
```

### 8. Update Registry

Update `ideas/registry.md`:
- Set **Status** to `validated` or `parked`
- Add validation file to **Files**
- Note the decision

### 9. Summary

```
Validation complete for IDEA-{NN}: {title}

Assumptions tested: {N}
- Validated: {n}
- Plausible: {n}
- Questionable: {n}
- Invalidated: {n}

Decision: {PROCEED / PIVOT / PARK}

{If PROCEED}: Run `biz-mvp-spec` to create the technical specification.
```

## Rules
- Don't skip validation because the idea "feels right"
- One invalidated critical assumption = serious red flag
- "I couldn't find evidence" is itself evidence (maybe nobody cares)
- Be the user's skeptical co-founder, not their cheerleader
- Update MB with validation results
