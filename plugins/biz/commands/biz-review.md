---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: BUSINESS alignment review of development progress - are we building the right thing? (bridge dev to biz). Use when user says biz review, siamo allineati col business, business check, ma to zmysel. NOT a code review.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Reads the current state of development and provides business-oriented feedback. This is the **bridge from dev back to biz** - it answers: "Are we still building the right thing?"

## Steps

### 1. Gather Context

**Locate ideas files** (ideas repo may be standalone or a submodule of this dev project):
- Check `ideas/registry.md` (standalone or submodule already at root)
- If not found, check if there's a git submodule containing `registry.md`
- If still not found, ask the user where the ideas repo is

Read in order:
1. `ideas/registry.md` - find the active idea being built
2. The idea's MVP spec from `ideas/mvp-specs/`
3. Memory Bank files (productContext, activeContext, progress)
4. Current codebase state: `git log --oneline -20` + project structure

### 2. Assess Alignment

Compare what's being built against the MVP spec:

```
MVP Spec says:                    Actual state:
─────────────────────────────────────────────────
Must-have features:
☐/☑ {feature 1}                   {built / in progress / not started}
☐/☑ {feature 2}                   {built / in progress / not started}
☐/☑ {feature 3}                   {built / in progress / not started}

User journey coverage:
Step 1: {status}
Step 2: {status}
...
Value moment: {status}
```

### 3. Check for Scope Creep

Look for signs of scope creep:
- Features being built that aren't in the MVP spec
- Over-engineering (complex architecture for simple needs)
- Premature optimization
- "Nice to have" work before "must have" is done

If found:
```
SCOPE CREEP ALERT:
- {what's being built} is not in the MVP spec
- Recommendation: {defer it / cut it / if actually needed, add to spec}
```

### 4. Business Health Check

Answer these questions:
- **Are we solving the original problem?** Compare current direction to the problem statement
- **Would a user get value from what exists today?** Could you demo it?
- **What's the fastest path to first user?** What's actually blocking launch?
- **Has anything changed?** New competitors? Market shift? User feedback?

### 5. Risk Update

Flag any new risks since last review:
- Technical risks discovered during development
- Market changes found
- Assumption that turned out wrong during building
- Timeline concerns

### 6. Generate Review Report

Present to user:

```markdown
# Business Review: IDEA-{NN} - {title}
**Date**: {today}

## Alignment Score: {Good / Drifting / Off-track}

## MVP Progress
- Must-have features: {N}/{total} complete
- User journey: {can/cannot} complete core flow
- Estimated completion: {close / needs more work / significant gap}

## Scope Creep Check
- {Clean - staying focused / Warning - see items below}
{list any scope creep items}

## Business Health
- Problem-Solution fit: {still strong / needs adjustment / concern}
- Path to first user: {clear / blocked by X}
- Competitive landscape: {unchanged / new development: X}

## Recommendations
1. {Most important action}
2. {Second priority}
3. {Third priority}

## Next Review
Suggest reviewing again after: {milestone or timeframe}
```

### 7. Update Registry and MB

- Add review date and summary to registry
- Update MB activeContext with business review findings

## When to Use This

- After completing a major feature
- When feeling lost about priorities
- Before deciding what to work on next
- When considering adding a new feature (is it MVP or scope creep?)
- Before "launching" to first users

## Rules
- Be honest. If the project is drifting, say so clearly
- Reference the original MVP spec. That's the contract
- Don't get into technical details. This is a BUSINESS review
- If the original idea assumptions are invalidated by what you learned during dev, flag it strongly
- Suggest pivots when evidence supports them
