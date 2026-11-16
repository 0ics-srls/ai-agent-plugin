---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Help - overview of all intelligence research & verification commands
---

## Show
```
=== INTELLIGENCE RESEARCH & VERIFICATION HELP ===

THE PIPELINE:
  Search → Cross-Reference → Audit → Report

COMMANDS:

  RESEARCH:
    /info:info-search    → Multi-agent parallel search (agents gather, the orchestrator synthesises)
    /info:info-cross     → Cross-reference each claim against independent sources

  VERIFICATION:
    /info:info-audit     → Deep truth audit (reads everything, can spawn investigators)
    /info:info-report    → Final report with traffic-light confidence (🟢🟡🔴)

  UTILITIES:
    /info:info-help      → This help screen

=== HOW IT WORKS ===

1. /info:info-search "{topic}"
   The orchestrator breaks the topic into 3-5 angles, launching agents in parallel.
   Each agent searches independently. Results merged into sources + claims.

2. /info:info-cross
   For each claim, agents search for INDEPENDENT confirmation or denial.
   Builds verification matrix: confirmed / partially supported / contested / unverified / contradicted.

3. /info:info-audit
   It reads EVERYTHING. Evaluates source reliability (Tier 1-5), detects
   bias, checks logical consistency. If doubts arise, spawns new agents to
   investigate. Assigns confidence scores (1-5) per claim:
   5=VERIFIED, 4=LIKELY TRUE, 3=PLAUSIBLE, 2=DOUBTFUL, 1=UNRELIABLE.

4. /info:info-report
   Clean, shareable report with traffic lights:
     🟢 HIGH CONFIDENCE - multiple independent sources confirm
     🟡 MODERATE - some verification, minor gaps
     🔴 LOW CONFIDENCE - unverified, contested, or single-source

=== FILE STRUCTURE ===

research/{topic-slug}/
  sources.md    → Raw sources with attribution
  claims.md     → Extracted verifiable claims
  cross-ref.md  → Verification matrix
  audit.md      → Truth audit with confidence scores
  report.md     → Final intelligence report

=== KEY PRINCIPLES ===

- Collect first, judge later (search ≠ audit)
- Independent sources only (same article on 3 sites = 1 source)
- "Not found" is a finding, not a failure
- Circular sourcing: A cites B cites A = 1 source, not 2
- Lower confidence is honest, false confidence is dangerous
- The audit can recursively investigate its own doubts

=== QUICK START ===

Just run: /info:info-search "your question here"
It handles everything from there.
```
