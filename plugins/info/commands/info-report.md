---
description: Generate final verified intelligence report with traffic-light confidence levels
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/intelligence-analyst.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Should have run `/info:info-search` + `/info:info-audit` (ideally also `/info:info-cross`)

## What This Command Does

Synthesizes all research, cross-references, and audit results into a clean, readable intelligence report. Uses a traffic-light system for confidence. Designed to be shared with others.

## Steps

### 1. Load All Research Data

If several topics exist in `research/`, ask the user which one. Read ALL files in `research/{topic-slug}/`:
- `sources.md`, `claims.md`, `cross-ref.md`, `audit.md`

If `audit.md` doesn't exist:
```
No audit data found. The report will have limited confidence assessment.
Strongly recommend running /info:info-audit first.
Generate report anyway? (y/n)
```

### 2. Generate Intelligence Report

Create `research/{topic-slug}/report.md`:

```markdown
# Intelligence Report: {topic}

**Date**: {today}
**Research depth**: {search only / cross-referenced / fully audited}
**Sources analyzed**: {n}
**Claims evaluated**: {n}
**Overall confidence**: {HIGH / MODERATE / LOW}

---

## Executive Summary

{3-5 sentences summarizing the key findings. Lead with the answer to the original question. Include the biggest caveat.}

---

## Key Findings

### 🟢 HIGH CONFIDENCE (verified by multiple independent sources)

**{Finding 1 title}**
{Clear statement of the finding}
- Based on: {source summary}
- Confidence: {score}/5
- Key evidence: {most compelling data point}

**{Finding 2 title}**
...

### 🟡 MODERATE CONFIDENCE (some verification, minor gaps)

**{Finding title}**
{Statement with appropriate hedging}
- Based on: {source summary}
- Confidence: {score}/5
- Caveat: {what could change this}

### 🔴 LOW CONFIDENCE (unverified, contested, or single-source)

**{Finding title}**
{Statement with clear uncertainty markers}
- Based on: {source summary}
- Confidence: {score}/5
- Risk: {why this might be wrong}

---

## What We Don't Know

{List of important questions that the research could NOT answer, with explanation of why}

1. **{question}** - {why we couldn't answer it}
2. ...

---

## Source Quality Assessment

| Quality | Count | Examples |
|---------|-------|---------|
| Tier 1 (primary/official) | {n} | {examples} |
| Tier 2 (major outlets) | {n} | {examples} |
| Tier 3 (specialized) | {n} | {examples} |
| Tier 4-5 (weak) | {n} | {examples} |

**Source diversity**: {good / limited / poor}
**Geographic coverage**: {global / regional / single-country}
**Temporal range**: {date range of sources}

---

## Contradictions & Debates

{Any claims where credible sources disagree, presented fairly}

| Claim | Position A | Position B |
|-------|-----------|-----------|
| {claim} | {view + sources} | {view + sources} |

---

## Bias & Methodology Notes

{Any systematic biases detected in the available information}
{Limitations of this research (e.g., language barrier, paywalled sources)}

---

## Recommendations

### If you need to make a decision based on this:
- **Trust**: {what you can rely on}
- **Verify further**: {what needs more research before acting}
- **Be skeptical of**: {what to take with a grain of salt}

### For deeper research:
- {suggestion for additional research angle}
- {specific expert/source to consult}

---

## Appendix: Research Trail

| Step | Date | Command | Result |
|------|------|---------|--------|
| Initial search | {date} | /info:info-search | {n} sources, {n} claims |
| Cross-reference | {date} | /info:info-cross | {n} verified, {n} contested |
| Audit | {date} | /info:info-audit | Overall: {confidence} |
| Report | {today} | /info:info-report | This document |

**Full research data**: `research/{topic-slug}/`
```

### 3. Ask About Format

```
Report generated at: research/{topic-slug}/report.md

Would you like me to:
1. Simplify it (shorter, less technical)
2. Expand specific sections
3. Export key findings as bullet points (for sharing)
4. It's good as is
```

### 4. Update Memory Bank

Update activeContext.md with report generation.

## Rules
- The report must be READABLE by someone who hasn't seen the raw research
- Use traffic lights (🟢🟡🔴) consistently - they're the visual anchor
- NEVER present low-confidence findings without flagging them
- "We don't know" is a valid and important finding - include it prominently
- The executive summary should be understandable in 30 seconds
- Keep the report factual. Save opinions for the Recommendations section
- Source the key findings - the reader should be able to verify
- Update MB with report activity
