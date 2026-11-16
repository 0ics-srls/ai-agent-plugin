---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Quick dashboard of all ideas and their funnel status. Use when user says biz status, stato delle idee, come vanno le idee, idea dashboard, ako su na tom napady.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Shows a quick dashboard of all ideas in the registry with their current status in the funnel.

## Steps

### 1. Read Registry

Read `ideas/registry.md`. If it doesn't exist:
```
No idea registry found. Run `biz-capture` to start capturing ideas.
```

### 2. Display Dashboard

```
IDEA FUNNEL STATUS
==================

Pipeline:
  Captured → Evaluated → Researched → Validated → MVP Specced → Building

  captured:    {n} ideas
  evaluated:   {n} ideas
  researched:  {n} ideas
  validated:   {n} ideas
  mvp-specced: {n} ideas
  building:    {n} ideas

Closed:
  parked:  {n}   killed: {n}   pivoted: {n}

Top Candidates (score >= 35):
  IDEA-{NN}: {title} [{status}] Score: {n}/60
  IDEA-{NN}: {title} [{status}] Score: {n}/60

Needs Attention:
  {n} ideas captured but not evaluated
  {n} ideas evaluated but not researched

Quick Actions:
  biz-capture   - Add a new idea
  biz-evaluate  - Score an unevaluated idea
  biz-research  - Research a promising idea
  biz-validate  - Validate before building
  biz-mvp-spec  - Create technical spec
  biz-review    - Check dev alignment with biz goals
```

## Rules
- Keep it brief - this is a dashboard, not a report
- Highlight what needs action (unevaluated ideas, stalled research)
- If an idea has been in the same status for a long time, mention it
