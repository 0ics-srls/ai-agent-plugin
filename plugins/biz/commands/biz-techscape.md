---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Analyze existing software landscape - tools, OSS, vendors, APIs, licenses - for reuse, build-vs-buy and differentiation. Use when user says techscape, cosa esiste gia, build vs buy, license check, che tool ci sono. Runs AFTER /biz:biz-evaluate and BEFORE /biz:biz-research.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.

## What This Command Does

Maps the technical ecosystem around an idea or development task. Finds existing tools, open source projects, SaaS products, APIs, datasets, and hardware SDKs that could be reused, integrated, or must be competed against. Critical license analysis included.

**This is an ITERATIVE command.** Run it multiple times as you discover new tools, libraries, or data sources during exploration and development. Each run UPDATES the existing techscape report (appends new findings, updates changed entries) rather than replacing it.

**Use in BIZ phase**: "What exists? Should we build or buy? What's our real technical moat?"
**Use in DEV phase**: "What libraries/services should we integrate? What are the license implications?"
**Use ad-hoc**: "I just found this library/tool/dataset - add it to our techscape"

## Steps

### 1. Define Scope

Ask user:
```
What do you want to analyze?

a) Full scan for a specific idea (I'll read from the registry)
b) Full scan for a development task (tell me what you're building)
c) General domain exploration (e.g., "real-time collaboration tools")
d) Add a specific find (I found a tool/library/dataset to evaluate)
```

If (a): Read the idea's evaluation/research files for context.
If (b): Read the codebase, MVP spec, or current task context.
If (c): Ask for the domain keywords.
If (d): User provides the specific tool/library/dataset. Evaluate it, check license, and append to existing techscape report.

**Check for existing techscape report first.** If one exists, read it to avoid duplicate research and to build on previous findings.

### 1b. Identify Product Type

Determine which platform considerations apply:

| Product Type | Extra Considerations |
|-------------|---------------------|
| **SaaS/Web** | Hosting costs, CDN, browser compat, SSR frameworks |
| **Mobile App** | App store rules (30% cut), native vs cross-platform, push notification services, in-app purchase requirements |
| **Desktop** | Distribution (Electron, Tauri), auto-update, code signing, OS-specific APIs |
| **Hardware** | Hardware SDKs, firmware libraries, communication protocols (BLE, MQTT, Zigbee), certification requirements |
| **API/Backend** | Rate limiting, API gateway, documentation tools, SDK generation |
| **Data/ML** | Training data sources, model hosting, GPU providers, dataset licenses |

Flag platform-specific constraints that affect build-vs-buy decisions.

### 2. Identify Categories to Research

Break the problem into functional areas. Example for a "project management tool":
```
Functional areas to research:
1. Core functionality (project management engines)
2. Auth & user management
3. Real-time / collaboration
4. Notifications
5. Payments / billing
6. Analytics / tracking
7. Hosting / infrastructure
```

Confirm with user, adjust if needed.

### 3. Research Each Category

For each functional area, use WebSearch to find:

#### A. SaaS / Commercial Products
- Name, URL, what it does
- Pricing (free tier? per-seat? usage-based?)
- API available? (can we integrate instead of compete?)
- Lock-in risk (data portability, vendor dependency)

#### B. Open Source Projects
- Name, repo URL, stars/activity
- **LICENSE** (critical - see license analysis below)
- Maturity (production-ready? maintained? last commit?)
- Community size (contributors, issues, responsiveness)
- Can it be self-hosted?
- Integration effort estimate (drop-in vs significant work)

#### C. APIs & Services
- Name, what it provides
- Pricing model (free tier limits, cost at scale)
- SDK quality (official SDKs? which languages?)
- Reliability/SLA
- Data ownership implications

#### D. Datasets & Data Sources (when relevant)
- Name, what data it contains
- **License** (CC-BY, CC-BY-SA, CC-BY-NC, proprietary - commercial use allowed?)
- Freshness (static dump vs regularly updated?)
- Format and size
- Terms of use for commercial products

#### E. Build-vs-Buy Recommendation
For each area:
- **Build**: When it's your core differentiator or trivial to implement
- **Buy/Use SaaS**: When it's commodity and not your moat
- **Integrate OSS**: When good options exist with compatible licenses
- **Fork OSS**: Last resort - maintenance burden is real

### 4. License Deep-Dive

**This section is critical for any software startup.**

For every open source project considered, classify the license:

| License | Commercial use? | Must open-source? | Distribution | Notes |
|---------|----------------|-------------------|-------------|-------|
| **MIT** | Yes | No | Any | Best for startups. Do anything. |
| **Apache 2.0** | Yes | No | Any | Good. Patent grant included. |
| **BSD 2/3** | Yes | No | Any | Similar to MIT. |
| **ISC** | Yes | No | Any | Simplified MIT. |
| **MPL 2.0** | Yes | Modified files only | Any | File-level copyleft. Usually fine. |
| **LGPL** | Yes (with care) | If you modify it | Any | Link dynamically, don't modify. |
| **GPL v2/v3** | Risky | Yes, if distributed | **SaaS OK (no distribution)**, mobile/desktop AVOID | Mobile apps = distribution = must open-source. |
| **AGPL** | **DANGER** | Yes, even SaaS | All | **AVOID** - triggers even for server-side use. |
| **BUSL (Business Source) / SSPL** | Usually no | Source-available, not OSS | Varies | Read terms. Often blocks competing products. |
| **Proprietary** | Per EULA | N/A | Per EULA | Check redistribution rights carefully. |

**Platform-specific license traps:**
- **Mobile apps**: GPL = you MUST open-source your entire app (app store = distribution)
- **SaaS**: GPL is OK (no distribution), but AGPL is NOT (network use triggers)
- **Desktop**: Same as mobile - distribution triggers copyleft
- **Hardware/Firmware**: GPL in firmware = must provide source for entire firmware image
- **Datasets**: CC-BY-NC = **cannot use commercially**. CC-BY-SA = derivative works must share-alike

**Flag any GPL/AGPL/BUSL/SSPL/CC-BY-NC dependencies immediately.**

For each flagged dependency:
```
LICENSE WARNING: {library} uses {license}
Product type: {SaaS/mobile/desktop/hardware}
Impact: {what this means for YOUR specific product type}
Alternative: {MIT/Apache alternative if one exists}
Mitigation: {if no alternative, how to isolate - e.g., separate process, API boundary, microservice}
```

### 5. Integration Architecture Sketch

If the user is in dev phase, sketch how the recommended tools fit together:

```
Your Product ({product type})
+-- Core (build yourself - this is your value)
+-- Auth -> {recommendation} (e.g., Clerk, Supabase Auth)
+-- Database -> {recommendation}
+-- {Feature X} -> {OSS library} (MIT, integrate directly)
+-- {Feature Y} -> {SaaS API} (use their API)
+-- {Feature Z} -> Build (no good options exist)
+-- {Platform-specific} -> {e.g., push notifications, app signing, hardware SDK}
```

### 6. Create or Update Techscape Report

**If report exists**: Read it first, then APPEND new findings under the appropriate category. Update the changelog section. Don't duplicate existing entries - update them if information changed.

**If new report**: Create `ideas/research/{idea-slug}-techscape.md` (biz phase) or `{@tasks}/{task}/techscape.md` (dev phase; `@tasks` of `j-settings.md`, `tasks/` without it). Ensure the folder exists first (`mkdir -p ideas/research/` or `mkdir -p {@tasks}/{task}/`):

```markdown
# Technical Landscape: {domain/idea}

**Product Type**: {SaaS / Mobile / Web / Desktop / Hardware / API}
**Created**: {date}
**Last Updated**: {date}

## Executive Summary
{2-3 sentences: key findings, main recommendations}

## Landscape by Category

### {Category 1}: {name}

#### Commercial / SaaS
| Product | What It Does | Pricing | API? | Verdict |
|---------|-------------|---------|------|---------|
| {name} | {desc} | {price} | Yes/No | {use/avoid/watch} |

#### Open Source
| Project | License | Stars | Last Activity | Maturity | Verdict |
|---------|---------|-------|---------------|----------|---------|
| {name} | {license} | {n} | {date} | {prod/beta/alpha} | {integrate/fork/avoid} |

#### APIs & Services
| Service | What It Does | Free Tier | Cost at Scale | Verdict |
|---------|-------------|-----------|---------------|---------|
| {name} | {desc} | {limit} | {cost} | {use/avoid} |

#### Datasets (if applicable)
| Dataset | Contents | License | Commercial OK? | Format | Verdict |
|---------|----------|---------|---------------|--------|---------|
| {name} | {desc} | {license} | Yes/No | {format} | {use/avoid} |

#### Recommendation
**{Build / Buy / Integrate OSS}**: {reasoning}

### {Category 2}: {name}
...

## License Summary

### Safe to Use (MIT/Apache/BSD)
- {library 1} - {what for}

### Use with Caution (LGPL/MPL)
- {library} - {what for} - {specific precaution for your product type}

### AVOID for this product type
- {library} - {why it's tempting} - {why dangerous for your product type} - **Alternative**: {safe alternative}

## Build vs Buy Matrix

| Component | Recommendation | Why | Cost/Effort |
|-----------|---------------|-----|-------------|
| {component} | Build | Core differentiator | {effort} |
| {component} | Buy ({product}) | Commodity, not our moat | ${cost}/mo |
| {component} | OSS ({project}) | Good option, MIT licensed | Integration: {S/M/L} |

## Architecture Recommendation
{How pieces fit together, considering the product type}

## Impact on Business Model
- **Build cost reduced by**: {estimate} via reuse of {tools}
- **Recurring costs**: ~${X}/mo for {SaaS services}
- **License risks**: {none / list specific risks}
- **Vendor lock-in risks**: {none / list specific risks}
- **Platform costs**: {app store fees, hardware certification, etc.}

## Changelog
| Date | What Changed | Category |
|------|-------------|----------|
| {date} | Initial analysis | All |
| {date} | Added {library} after user discovery | {category} |
```

### 7. Update Context

**If biz phase**: Update idea's registry entry, add techscape file reference.
**If dev phase**: Update MB techContext with key findings, update activeContext.

### 8. Present Findings

```
Techscape {created/updated} for: {domain}

{If new}: Key findings:
- {N} existing solutions found across {M} categories
- Recommended: Build {X}, Buy {Y}, Integrate {Z}
- License flags: {none / N dependencies need attention}
- Estimated savings: {what you DON'T need to build}

{If update}: Added to techscape:
- {what was added/changed}
- License status: {safe / flagged}
- Recommendation: {build/buy/integrate}

Run `/biz:biz-techscape` again anytime you find something new to evaluate.
```

## When to Run This

- **After `/biz:biz-evaluate`**: Before deep market research, understand the tech landscape
- **After `/biz:biz-mvp-spec`**: Before starting development, know what to reuse
- **During dev**: When deciding whether to build a component or use existing
- **Before choosing a library**: License check before adding a dependency
- **When you discover something**: "I found this cool library" -> add it to techscape
- **Before adding any dependency**: Quick license + viability check

## Rules
- What a project built with this set depends on obeys `principles.md` 6.4, stricter than the table above, which reads the whole landscape
- ALWAYS check licenses. License implications differ by product type (SaaS vs mobile vs desktop)
- Don't just list tools - give actionable recommendations (build/buy/integrate)
- Star count alone doesn't mean quality. Check last commit, open issues, bus factor
- "No good open source exists" is a valid finding and potential business signal
- Be specific about costs. "$0 to start" means nothing if it's $500/mo at scale
- If a SaaS product has no public pricing, flag it as enterprise/sales-driven (usually expensive)
- APPEND to existing reports, don't overwrite. The techscape is a living document
- When user says "I found X", evaluate it immediately and add to report. Don't make them wait for a full scan
- Consider the FULL cost: license + integration effort + ongoing maintenance + vendor risk
- For mobile: always flag app store commission (Apple 30%, Google 30%) in cost analysis
- For hardware: flag certification costs (FCC, CE, etc.) when relevant
- Update MB with techscape findings - they inform both biz and dev decisions
