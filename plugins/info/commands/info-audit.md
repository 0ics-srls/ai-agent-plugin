---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Deep truth audit - evaluate reliability, bias, contradictions, confidence scoring
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/intelligence-analyst.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Should have run `info-search` and ideally `info-cross` first

## What This Command Does

The "brain" of the verification system. This step reads ALL collected data (sources, claims, cross-references) and performs deep analysis: source reliability assessment, bias detection, logical consistency checks, and confidence scoring. Can spawn targeted agents to investigate specific doubts.

## Steps

### 1. Load All Research Data

If several topics exist in `research/`, ask the user which one. Read ALL files in `research/{topic-slug}/`:
- `sources.md` - raw sources
- `claims.md` - extracted claims
- `cross-ref.md` - cross-reference matrix (if exists)

If cross-ref doesn't exist, warn:
```
No cross-reference data found. Running audit on uncross-referenced claims
reduces confidence. Consider running info-cross first.
Proceed anyway? (y/n)
```

### 2. Source Reliability Assessment

For each source used across all claims, evaluate:

| Factor | Question | Weight |
|--------|----------|--------|
| **Authority** | Is the source an expert/institution in this field? | High |
| **Independence** | Is the source financially/politically independent on this topic? | High |
| **Track Record** | Has this source been accurate historically? | Medium |
| **Transparency** | Does the source show methodology/data? | Medium |
| **Recency** | How current is the information? | Context-dependent |
| **Primary vs Secondary** | Is this original reporting or repackaged? | Medium |

Create reliability tier for each source:
- **Tier 1**: Court documents, government statistics, SEC filings, academic peer-reviewed journals, official specifications, raw data
- **Tier 2**: Major newspapers (NYT, Reuters, BBC), established industry analysts (Gartner, IDC), books by domain experts
- **Tier 3**: Trade publications, named industry practitioners, established tech blogs (with editorial process), conference proceedings
- **Tier 4**: Reddit (with upvotes/discussion), Stack Overflow, Medium articles, named personal blogs, podcasts
- **Tier 5**: Anonymous posts, undated content, SEO-farm articles, press releases (promotional), social media posts, AI-generated content

### 3. Bias Detection

For each claim, check for:

- **Confirmation bias**: Are all sources from the same "side"?
- **Selection bias**: Are inconvenient data points being ignored?
- **Survivorship bias**: Are we only hearing success stories?
- **Authority bias**: Are we trusting a source because of WHO said it, not WHAT they said?
- **Recency bias**: Are we over-weighting recent events?
- **Financial bias**: Does the source profit from this claim being believed?
- **Geographic/cultural bias**: Are all sources from the same region/perspective?

### 4. Logical Consistency Analysis

Check claims against each other:

- Do any claims **logically contradict** each other?
- Do the numbers **add up**? (e.g., if market share claims from different sources total >100%)
- Is the **timeline** consistent? (cause before effect, dates align)
- Are there **logical leaps**? (correlation presented as causation)
- Does the **overall narrative** make sense when all claims are combined?

### 5. Deep Investigation (Spawn Agents if Needed)

If the audit reveals specific doubts, spawn **targeted agents** to investigate:

```
INVESTIGATION AGENT - Doubt: {specific doubt}

During truth audit of "{topic}", I found:
{description of the doubt or inconsistency}

Your job: Search specifically for evidence that resolves this doubt.
Focus on:
- {specific search instructions}

Return: What you found, with sources.
```

This is the key differentiator - the audit can recursively trigger more research.

Typical triggers for investigation:
- A high-impact claim with only Tier 3-4 sources
- Two Tier 1 sources that contradict each other
- A claim that seems "too good to be true"
- Missing context that would change interpretation
- A statistic without methodology

### 6. Confidence Scoring

Score each claim on a 5-level scale:

| Level | Label | Criteria |
|-------|-------|----------|
| **5** | VERIFIED | 3+ independent Tier 1-2 sources confirm. No contradictions. Logically consistent. Consistent over time. |
| **4** | LIKELY TRUE | 2+ independent sources confirm. Minor caveats. No strong contradictions. |
| **3** | PLAUSIBLE | Some confirmation, some gaps. Could go either way. No contradictions but limited independent verification. |
| **2** | DOUBTFUL | Single source, weak sources, possible bias, or unresolved contradictions. |
| **1** | UNRELIABLE | No independent confirmation. Known biased sources. Logical problems. Or actively contradicted. |

### 7. Self-Assessment & Auto-Investigation

After scoring all claims, perform a **self-assessment** on each verdict:

For each claim, ask yourself: "How confident am I in MY OWN assessment?" Express as percentage (0-100%).

This is NOT the claim's confidence score. This is your confidence in your ability to judge the claim correctly, given the data available.

Factors that lower self-assessment:
- Topic outside your training data strength
- All sources are from the same ecosystem/bubble
- You had to rely heavily on inference rather than data
- The claim involves very recent events (post training data)
- Technical domain where you lack depth
- Ambiguous or conflicting signals that could go either way

**CRITICAL: If self-assessment < 80% on any claim:**

1. Identify WHY your assessment is uncertain
2. Formulate what specific information would raise your confidence
3. Spawn a **targeted agent** to search for exactly that information:

```
SELF-DOUBT INVESTIGATION - Claim: {claim text}

My assessment of this claim has {X}% self-confidence.
I'm uncertain because: {reason}

Search specifically for:
- {what would confirm or deny the assessment}
- {what data point is missing}
- {what expert opinion would help}

Return: findings that help me be MORE or LESS confident in my verdict.
```

4. After the agent returns, re-evaluate the claim and update the self-assessment
5. If still < 80%, flag it prominently in the report as "AUDITOR UNCERTAINTY"

### 8. Generate Audit Report

Create `research/{topic-slug}/audit.md`:

```markdown
# Truth Audit: {topic}

**Date**: {today}
**Data analyzed**: {n} sources, {n} claims, {n} cross-references

## Executive Summary

**Overall confidence**: {HIGH / MODERATE / LOW / MIXED}
**Key finding**: {1-2 sentence summary}
**Biggest risk**: {what's most likely to be wrong and why}

## Claim-by-Claim Audit

### CLAIM-01: {claim text}
- **Confidence**: {1-5} - {VERIFIED / LIKELY TRUE / PLAUSIBLE / DOUBTFUL / UNRELIABLE}
- **Source quality**: {Tier breakdown}
- **Cross-ref status**: {confirmed/contested/unverified/contradicted}
- **Bias check**: {clean / flags found}
- **Logic check**: {consistent / issues found}
- **Reasoning**: {2-3 sentences explaining the assessment}
- **Caveats**: {what could change this assessment}
- **Self-assessment**: {0-100}% — {why this percentage}

### CLAIM-02: ...

## Source Reliability Map

| Source | Tier | Bias Flags | Claims Supported | Reliability |
|--------|------|------------|-----------------|-------------|
| {source} | {1-5} | {flags} | {claim list} | {high/med/low} |

## Bias Analysis
{overall bias patterns detected across the research}

## Logical Consistency
{narrative coherence assessment}

## Investigation Results
{findings from any deep-investigation agents spawned}

## Information Quality Score

| Metric | Score |
|--------|-------|
| Source diversity | {1-5} |
| Source quality | {1-5} |
| Cross-referencing depth | {1-5} |
| Temporal coverage | {1-5} |
| Perspective balance | {1-5} |
| **Overall quality** | {average}/5 |

## Self-Assessment

| Claim | Verdict | Self-Assessment | Action Taken |
|-------|---------|----------------|-------------|
| CLAIM-01 | {verdict} | {X}% | {none / investigated: {finding}} |
| CLAIM-02 | {verdict} | {X}% | {none / investigated: {finding}} |

**Auditor uncertainty flags**: {list claims still < 80% after investigation, if any}

## Recommendations
- {what the user should trust}
- {what needs more research}
- {what to be skeptical about}
```

### 9. Ask User

After presenting the audit, ask:
```
Do you want me to:
1. Investigate specific doubts further (I'll send targeted agents)
2. Generate the final report (info-report)
3. Something else?
```

If the user wants more investigation, go back to Step 5.

### 10. Update Memory Bank

Update activeContext.md with audit findings and confidence levels.

## Rules
- This is the JUDGMENT step. Be ruthlessly analytical, not diplomatic
- A single Tier 1 source outweighs five Tier 4 sources
- "Widely reported" ≠ true. Check if it's circular sourcing (one source copied by many)
- When in doubt, score lower. False confidence is worse than acknowledged uncertainty
- The recursive investigation (Step 5) is powerful but expensive. Use it for HIGH-IMPACT doubts only
- Always explain your reasoning. "Confidence: 2" without explanation is useless
- If the overall picture is "we don't really know", say so clearly
- Update MB with audit results
