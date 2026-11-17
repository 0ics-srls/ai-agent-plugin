---
description: Capture a new startup idea, problem, or insight into the idea registry. Use when user says ho un'idea, nuova idea, capture this idea, mam napad, or describes a business problem/insight worth tracking.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Captures a raw idea, problem observation, or business insight and adds it to the persistent idea registry. Nothing gets lost between sessions.

## Steps

### 1. Ensure Registry Exists
```bash
mkdir -p ideas/evaluations ideas/research ideas/validations ideas/mvp-specs
```
If `ideas/registry.md` doesn't exist, create it from the template below.

### 2. Listen Mode
Say:
```
Tell me your idea, problem, or insight. I'll capture it structured.
You can be messy - I'll organize it.

What's on your mind?
```

Wait for user input. Do NOT evaluate yet - just capture.

### 3. Structure the Idea

Extract and organize:
- **One-liner**: What is it in one sentence?
- **Problem**: What problem does it solve?
- **Who**: Who has this problem?
- **Current alternatives**: How do people solve it today?
- **Your angle**: Why would yours be better/different?

Ask clarifying questions if any of these are unclear. Use AskUserQuestion.

### 4. Assign ID and Add to Registry

- Read `ideas/registry.md`
- Find the highest existing ID number
- Assign next ID: `IDEA-{NN}`
- Create slug from the one-liner (e.g., `ai-recipe-planner`)

Add entry to registry:
```markdown
### IDEA-{NN}: {one-liner}
- **Status**: captured
- **Date**: {today}
- **Problem**: {problem statement}
- **Who**: {target audience}
- **Current alternatives**: {how they solve it now}
- **Your angle**: {differentiation}
- **Score**: -/60 (not evaluated)
- **Files**: -
```

### 5. Check for Related Ideas

Scan the registry for similar or related ideas. If found:
```
Note: This relates to IDEA-{XX} ({title}). You might want to
evaluate them together or merge them.
```

### 6. Confirm

```
Captured as IDEA-{NN}: {one-liner}
Status: captured

Next steps:
- Run `/biz:biz-evaluate` to score this idea (quick, 5 min)
- Run `/biz:biz-capture` again if you have more ideas
- You have {N} total ideas, {M} not yet evaluated
```

## Registry Template

If `ideas/registry.md` doesn't exist, create:
```markdown
# Idea Registry

Master list of all startup ideas, problems, and insights.
Nothing gets deleted - files stay forever; the Status field marks where each idea stands.

## Status Enum (single source of truth - every biz command uses these)
Pipeline: `captured` → `evaluated` → `researched` → `validated` → `mvp-specced` → `building`
Terminal:  `parked` (low score / deprioritized - set by /biz:biz-evaluate or /biz:biz-validate)
           `killed` (dead end with documented reasons - set by /biz:biz-close)
           `pivoted` (forked into a new idea - set by /biz:biz-pivot)
Who sets what: /biz:biz-capture→captured, /biz:biz-evaluate→evaluated|parked, /biz:biz-research→researched,
/biz:biz-validate→validated|parked, /biz:biz-mvp-spec→mvp-specced (then building when dev starts), /biz:biz-close→killed, /biz:biz-pivot→pivoted

## Active Ideas
<!-- Ideas currently being explored -->

## Parked Ideas
<!-- Ideas scored too low or deprioritized, kept for reference -->

---
<!-- New ideas go above this line -->
```

## Rules
- NEVER evaluate during capture. Just record faithfully
- NEVER skip adding to registry. Every idea gets an entry
- Ask clarifying questions, but don't challenge the idea yet
- If user dumps multiple ideas, capture each as separate entry
- Update MB activeContext with latest capture activity
