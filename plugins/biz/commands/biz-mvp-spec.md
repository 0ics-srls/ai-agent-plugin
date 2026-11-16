---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: Generate technical MVP specification from a validated idea (bridge biz to dev). Use when user says mvp spec, specifica mvp, ready to build, prepariamo lo sviluppo, ide sa stavat.
---

## Prerequisites
- If not read this session: `${CLAUDE_PLUGIN_ROOT}/commands/mind-sets/startup-strategist.md`
- Read the Memory Bank (skip the subdirectories) if not already done this session.
- Idea should be validated (run `biz-validate`). Starting from an idea only researched is the user's decision, and the spec says so

## What This Command Does

Translates a validated business idea into a concrete technical MVP specification. This is the **bridge from business to development** - the output feeds directly into dev workflows (`j-new-project`).

## Steps

### 1. Select Idea

Read `ideas/registry.md`. Show validated ideas:
```
Which idea do you want to spec for MVP?

Validated ideas:
- IDEA-02: {title} (Confidence: High)
```

Read all existing files: evaluation, research, validation.

### 2. Define MVP Scope with User

This is the most critical step. Ask:

```
MVP means the MINIMUM product that tests your core hypothesis.
Not the dream product. Not v2. The smallest thing that proves the idea works.

Let's define what's IN and what's OUT.

What is the ONE core thing this product must do to be useful?
```

Guide the user to ruthlessly cut scope:
- **Must have**: Without this, the product is useless
- **Should have**: Important but can ship without
- **Won't have (yet)**: Future features, explicitly deferred

### 3. Define User Journey

Map the critical path - what a user does from start to value:

```
1. User arrives at {entry point}
2. User does {action 1}
3. System does {response 1}
4. User gets {value moment} ← THIS is what we're building toward
```

Keep it to 5-7 steps max. If it's longer, the MVP is too big.

### 4. Technical Decisions

Discuss with user:

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Platform** | Web / Mobile / Desktop / CLI | {rec + why} |
| **Architecture** | Monolith / Microservices / Serverless | Monolith (it's an MVP) |
| **Frontend** | React / Vue / Angular / None | {based on user's skills} |
| **Backend** | Node / Python / C# / Java | {based on user's skills} |
| **Database** | Postgres / SQLite / Firebase | {based on complexity} |
| **Hosting** | Vercel / Railway / VPS / Local | {based on budget} |
| **Auth** | DIY / Auth0 / Clerk / None | {based on need} |

**Key principle**: Choose what you already know. MVP is not the time to learn new tech.

### 5. Define Data Model

High-level entities only:
```
User
  - email, name, ...

{CoreEntity}
  - {key fields}
  - belongs_to: User

{SupportEntity}
  - {key fields}
  - belongs_to: {CoreEntity}
```

### 6. Define API / Key Screens

List the core endpoints or screens:

**If API-first:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/{resource} | Create {thing} |
| GET | /api/{resource} | List {things} |
| ... | ... | ... |

**If UI-first:**
| Screen | Purpose | Key Actions |
|--------|---------|-------------|
| Landing | Explain value prop | Sign up |
| Dashboard | Show {core data} | Create, view |
| {Core Screen} | {main interaction} | {main action} |

### 7. Create MVP Spec Document

Create `ideas/mvp-specs/{idea-slug}.md`:
```markdown
# MVP Spec: IDEA-{NN} - {title}

**Date**: {today}
**Target**: {timeline estimate - weeks, not months}

## One-Liner
{What it does in one sentence}

## Problem → Solution
**Problem**: {from research}
**Solution**: {how MVP solves it}
**Success Metric**: {how we know it works - e.g., "10 users complete the core flow"}

## MVP Scope

### Must Have (v0.1)
- [ ] {feature 1}
- [ ] {feature 2}
- [ ] {feature 3}

### Won't Have Yet
- {deferred feature 1} - {why deferred}
- {deferred feature 2} - {why deferred}

## User Journey
1. {step 1}
2. {step 2}
3. ...
4. {value moment}

## Tech Stack
- **Platform**: {choice}
- **Frontend**: {choice}
- **Backend**: {choice}
- **Database**: {choice}
- **Hosting**: {choice}
- **Auth**: {choice}

## Data Model
{entities and relationships}

## Core Screens / API
{screens or endpoints}

## Development Approach
**Recommended workflow**: j-new-project, j-cvm-exec-plan, j-close; bbc-analyze to design the project as black boxes before its code, when it is too large for one context window
**Estimated effort**: {S/M/L}

## Launch Checklist
- [ ] Core flow works end-to-end
- [ ] Can onboard a new user without help
- [ ] Basic error handling (won't crash)
- [ ] Deployed and accessible
- [ ] Analytics/tracking to measure success metric
```

### 8. Update Registry

Update `ideas/registry.md`:
- Set **Status** to `mvp-specced`
- When development actually starts (j-new-project/j-cvm-exec-plan kicked off), set **Status** to `building` — this is the ONLY transition into `building` (biz-status/biz-pivot/biz-review read it)
- Add MVP spec file to **Files**

### 9. Bridge to Dev

```
MVP Spec complete for IDEA-{NN}: {title}

NEXT STEPS - Setting up the development project:

1. Create a new repo for the project
2. Add this ideas repo as a submodule:
     git submodule add <this-ideas-repo-url> ideas
3. Inside the new repo, run: `j-new-project`
   (use the MVP spec at ideas/mvp-specs/{idea-slug}.md as input)
4. `j-cvm-exec-plan` executes the plan it wrote, `j-close` merges it
5. `bbc-analyze` to design the project as black boxes before its code, when it is too large for one context window

This way:
  - ideas/ stays a separate repo (you can keep capturing new ideas)
  - biz-review works in the dev project (sees both code and ideas/)
  - Business context and dev context stay cleanly separated
```

## Rules
- MVP = weeks, not months. If the spec feels like 3+ months of work, cut more
- No premature optimization. No "scalability" concerns. It's an MVP
- Pick boring technology. The product idea is the risk, not the tech
- Auth is optional for many MVPs. "Does the core value work?" comes first
- Update MB with MVP spec details (update productContext.md with vision)
