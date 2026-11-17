---
description: Intelligence verification pipeline STEP 1 - multi-agent fact gathering with sources, feeds /info:info-cross/info-audit/info-report. Use when user says info search, verifica informazioni, intelligence research. For startup market research use /biz:biz-research.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/intelligence-analyst.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Orchestrates parallel research agents to gather information from multiple angles on a given topic. Collects facts, sources, and attributions into a structured research dossier.

## Steps

### 1. Understand the Research Target

Ask the user (if not already specified):
```
What topic or question do you want to research?
Be specific - the more focused, the better the results.
```

### 2. Define Search Angles

Break the topic into 3-5 independent research angles. Each angle will be searched by a separate agent in parallel.

Example for "Is X technology ready for production?":
- Angle 1: Technical maturity (docs, release history, known issues)
- Angle 2: Adoption (who uses it, case studies, Stack Overflow activity)
- Angle 3: Alternatives and comparisons
- Angle 4: Criticism and failure stories
- Angle 5: Expert opinions and forecasts

Present angles to user for approval. Adjust if needed.

### 3. Ensure Research Directory

```bash
mkdir -p research/{topic-slug}
```

### 4. Launch Parallel Search Agents

Launch 3-5 agents in parallel using the Agent tool. Each agent gets:

```
RESEARCH AGENT - Angle: {angle name}

Topic: {topic}
Your search angle: {angle description}

INSTRUCTIONS:
1. Use WebSearch to find information from this angle
2. Vary the keywords and keep searching until new queries stop turning up new sources
3. For each relevant finding, record:
   - FACT: The specific claim or data point
   - SOURCE: Publication/site name
   - URL: Where you found it
   - DATE: Publication date (if available)
   - SOURCE TYPE: news | academic | government | corporate | blog | social | forum | official-docs
   - QUOTE: Key quote if available (verbatim)
4. Prioritize:
   - Primary sources over secondary
   - Recent over old (note dates)
   - Named authors/orgs over anonymous
5. Note any contradictions you find WITHIN your angle
6. Return ALL findings in structured format

DO NOT evaluate truth. Just collect facts and sources accurately.
Return your findings as a structured list.
```

Launch all agents in a single message (parallel).

### 5. Collect and Structure Results

After all agents return, merge findings into `research/{topic-slug}/sources.md`:

```markdown
# Research: {topic}

**Date**: {today}
**Search angles**: {list}
**Agents deployed**: {n}

## Sources Collected

### From Angle: {angle 1}
| # | Fact | Source | Type | Date | URL |
|---|------|--------|------|------|-----|
| 1 | {fact} | {source} | {type} | {date} | {url} |
| 2 | ... | ... | ... | ... | ... |

### From Angle: {angle 2}
...

## Raw Agent Reports
{full agent outputs for reference}
```

### 6. Extract Claims

Analyze all collected facts and extract distinct **claims** - specific, verifiable statements.

Create `research/{topic-slug}/claims.md`:

```markdown
# Claims: {topic}

**Extracted from**: {n} sources across {n} angles
**Date**: {today}

## Claims

### CLAIM-01: {one-sentence claim}
- **Sources citing this**: {list of source #s}
- **Source count**: {n}
- **Source types**: {news, academic, etc.}
- **Date range**: {oldest - newest}
- **Status**: unverified

### CLAIM-02: {one-sentence claim}
...

## Contradictions Detected
{list any claims that directly contradict each other, with sources for each side}

## Information Gaps
{what angles returned little/no results - what's missing?}
```

### 7. Summary

```
RESEARCH COMPLETE: {topic}

Sources collected: {n} from {n} angles
Claims extracted: {n}
Contradictions found: {n}
Information gaps: {list}

Files:
  research/{topic-slug}/sources.md  - All sources with attribution
  research/{topic-slug}/claims.md   - Extracted claims for verification

Next steps:
  /info:info-cross  → Cross-reference claims against independent sources
  /info:info-audit  → Full truth audit with confidence scoring
```

## Rules
- NEVER evaluate truth during search. This command COLLECTS, it doesn't JUDGE
- Always record source URLs and dates - without these, a claim is worthless
- Agents do the search, in parallel. The orchestrator only orchestrates
- If WebSearch returns nothing useful for an angle, note it as an information gap
- Prefer diversity of source types - one claim from 3 different source types is stronger than from 3 blogs
- Record contradictions as-is, don't resolve them
- Update MB activeContext with research activity
