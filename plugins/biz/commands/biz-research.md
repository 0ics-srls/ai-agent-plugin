---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Deep MARKET research for a promising idea - competitors, TAM/SAM/SOM, monetization. Use when user says market research, ricerca di mercato, chi sono i competitor, quanto vale il mercato. NOT for fact verification (/info:info-search); for the tech landscape use /biz:biz-techscape.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Idea should be evaluated first (run `/biz:biz-evaluate`)

## What This Command Does

Deep research on a specific idea: competitors, market size, existing solutions, monetization models, and differentiation opportunities.

## Steps

### 1. Select Idea

Read `ideas/registry.md`. Show ideas with status `evaluated` and score >= 25:
```
Which idea do you want to research?

Ready for research:
- IDEA-02: {title} (Score: 42/60)
- IDEA-05: {title} (Score: 38/60)
```

Read the evaluation file for context.

### 2. Research Plan

Tell user:
```
I'll research IDEA-{NN}: {title}

I'll cover:
1. Existing solutions & competitors
2. Market size (TAM/SAM/SOM)
3. How competitors monetize
4. Gaps and opportunities
5. Key risks

This will involve web searches. Let's start.
```

### 3. Competitor & Solution Research

Use WebSearch to find:
- Direct competitors (same problem, similar solution)
- Indirect competitors (same problem, different approach)
- Adjacent solutions (related problem space)
- Open source alternatives
- DIY/manual workarounds people use

For each competitor found, note:
- Name and URL
- What they do (one line)
- Pricing model
- Apparent strengths/weaknesses
- Estimated size (funding, team, users if findable)

### 4. Market Size Analysis

Research and estimate:
- **TAM** (Total Addressable Market) - Everyone who could theoretically use this
- **SAM** (Serviceable Addressable Market) - The segment you can actually reach
- **SOM** (Serviceable Obtainable Market) - Realistic first-year target

Be honest about assumptions. Use bottom-up when possible:
```
{N} potential users × ${X} annual price = ${Y} SOM
```

### 5. Monetization Analysis

Research how similar products make money:
- SaaS subscription
- Freemium + premium
- Marketplace/transaction fees
- Usage-based pricing
- One-time purchase
- Advertising
- Data/API licensing

Recommend the most viable model for this specific idea with reasoning.

### 6. Differentiation & Gaps

Based on competitor research, identify:
- What's missing from existing solutions?
- What do users complain about? (check reviews, forums, Reddit)
- Where is the market heading?
- What could you do differently?

### 7. Risk Assessment

Identify top risks:
- **Market risk** - Is the market real? Growing or shrinking?
- **Competition risk** - Could a big player crush you?
- **Technical risk** - Is this technically hard to build?
- **Regulatory risk** - Any legal/compliance concerns?
- **Timing risk** - Too early? Too late?

### 8. Create Research Report

Create `ideas/research/{idea-slug}.md`:
```markdown
# Market Research: IDEA-{NN} - {title}

**Date**: {today}
**Researcher**: the agent + {user}

## Executive Summary
{2-3 sentences: is this market worth pursuing?}

## Existing Solutions & Competitors

### Direct Competitors
| Name | What They Do | Pricing | Strengths | Weaknesses |
|------|-------------|---------|-----------|------------|
| {name} | {desc} | {pricing} | {str} | {weak} |

### Indirect Competitors / Alternatives
| Name | Approach | Why People Use It |
|------|----------|-------------------|
| {name} | {approach} | {reason} |

## Market Size

| Metric | Estimate | Reasoning |
|--------|----------|-----------|
| TAM | ${X} | {how calculated} |
| SAM | ${X} | {how calculated} |
| SOM (Year 1) | ${X} | {how calculated} |

## Monetization

**Recommended model**: {model}
**Reasoning**: {why this model fits}
**Comparable pricing**: {what competitors charge}

## Opportunities & Gaps
1. {gap 1 - what's missing in the market}
2. {gap 2}
3. {gap 3}

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| {risk} | High/Med/Low | {what to do about it} |

## Verdict
{GO / NEEDS MORE VALIDATION / NO-GO}
{Reasoning for verdict}

## Next Steps
{If GO}: Run `/biz:biz-validate` to test key assumptions
{If NO-GO}: Specific reasons why not. Move to parked.
```

### 9. Update Registry

Update `ideas/registry.md`:
- Set **Status** to `researched`
- Add research file to **Files**
- Add brief research verdict

### 10. Present Findings

Give user a concise summary:
```
Research complete for IDEA-{NN}: {title}

Key findings:
- {N} direct competitors found, biggest is {name}
- Market size: ~${SOM} addressable in year 1
- Best monetization: {model} at ~${price}/mo
- Main opportunity: {gap}
- Main risk: {risk}

Verdict: {GO/VALIDATE/NO-GO}

{If GO}: Run `/biz:biz-validate` to test assumptions before building.
```

## Rules
- Use WebSearch extensively - don't guess about competitors
- Be conservative on market size. Fantasy TAMs help nobody
- If you can't find competitors, that's a WARNING not a positive (maybe no market)
- Always check if competitors have raised funding (signals market validation)
- Update MB with research findings
