---
description: Cross-reference claims against independent sources to build verification matrix
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/intelligence-analyst.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Must have run `/info:info-search` first (needs claims.md)

## What This Command Does

Takes extracted claims from /info:info-search and sends parallel agents to independently verify each claim against new sources. Builds a cross-reference matrix showing which claims are confirmed, unconfirmed, or contradicted.

## Steps

### 1. Load Claims

Read `research/{topic-slug}/claims.md`. If multiple topics exist, ask the user which one.

Show summary:
```
Loaded {n} claims for cross-referencing.
Claims will be grouped into batches for parallel verification.
```

### 2. Group Claims for Verification

Group claims into batches of 2-3 related claims. Each batch will be verified by one agent. This is more efficient than one-agent-per-claim.

### 3. Launch Cross-Reference Agents

Launch agents in parallel (one per batch). Each agent gets:

```
VERIFICATION AGENT - Batch {n}

You are verifying these claims about "{topic}":

CLAIM-{NN}: {claim text}
  Original sources: {list}

CLAIM-{NN}: {claim text}
  Original sources: {list}

INSTRUCTIONS:
1. For EACH claim, search for INDEPENDENT sources that either confirm or deny it
2. "Independent" means: NOT the same publication, NOT the same author, NOT citing the same original source
3. Search specifically for:
   - Counter-arguments and opposing views
   - Fact-check articles about this topic
   - Academic or government data that relates
   - Forum discussions where experts weigh in
4. For each new source found, record:
   - Does it CONFIRM, CONTRADICT, or PARTIALLY SUPPORT the claim?
   - SOURCE: name + URL + date + type
   - KEY EVIDENCE: what specific data/argument supports their position
5. Also check:
   - Is the original source known for bias? (check media bias databases)
   - Has the claim been debunked or retracted anywhere?
   - Are there more recent updates that change the picture?

Return structured results per claim.
```

### 4. Build Cross-Reference Matrix

After all agents return, create `research/{topic-slug}/cross-ref.md`:

```markdown
# Cross-Reference: {topic}

**Date**: {today}
**Claims verified**: {n}
**New sources found**: {n}

## Verification Matrix

### CLAIM-01: {claim text}
| Status | Count | Sources |
|--------|-------|---------|
| ✅ Confirming | {n} | {source list} |
| ❌ Contradicting | {n} | {source list} |
| 🟡 Partially supporting | {n} | {source list} |

**Original sources**: {n} | **Independent verification**: {n} new sources
**Cross-ref verdict**: CONFIRMED / PARTIALLY SUPPORTED / CONTESTED / UNVERIFIED / CONTRADICTED

---

### CLAIM-02: {claim text}
...

## Summary Matrix

| Claim | Original Sources | Confirming | Contradicting | Partially Supporting | Verdict |
|-------|-----------------|------------|---------------|---------------------|---------|
| CLAIM-01 | {n} | {n} | {n} | {n} | {verdict} |
| CLAIM-02 | {n} | {n} | {n} | {n} | {verdict} |
| ... | ... | ... | ... | ... | ... |

## Verdict Definitions
- **CONFIRMED**: 2+ independent sources confirm, 0 contradict
- **PARTIALLY SUPPORTED**: 1+ independent sources partially support, 0 contradict
- **CONTESTED**: Has both confirming AND contradicting sources
- **UNVERIFIED**: No independent confirmation found (not necessarily false)
- **CONTRADICTED**: Independent sources contradict, few/no confirmations

## Source Bias Notes
{any bias findings about original or new sources}

## New Contradictions Discovered
{contradictions found during cross-referencing that weren't in the original research}
```

### 5. Update Claims

Update `claims.md` - change status of each claim from `unverified` to the cross-ref verdict.

### 6. Summary

```
CROSS-REFERENCE COMPLETE: {topic}

Results:
  ✅ Confirmed:             {n} claims
  🟡 Partially supported:   {n} claims
  ⚠️ Contested:             {n} claims
  ❓ Unverified:            {n} claims
  ❌ Contradicted:          {n} claims

New sources found: {n}
New contradictions: {n}

Files:
  research/{topic-slug}/cross-ref.md - Full cross-reference matrix

Next step:
  /info:info-audit → Deep truth analysis with confidence scoring
```

## Rules
- INDEPENDENT sources only. Same article republished on 3 sites = 1 source, not 3
- "No sources found" is a finding, not a failure. Record it as UNVERIFIED
- Always search for the OPPOSING view, not just confirmation
- Check publication dates - old confirmations of time-sensitive claims are weak
- Agents do the search; the orchestrator orchestrates
- Note circular sourcing: A cites B cites C cites A = 1 source, not 3
- Update MB activeContext with cross-reference results
