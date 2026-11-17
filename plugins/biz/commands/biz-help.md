---
description: Help - overview of all business development commands and the idea funnel. Use when user says biz help, come funziona il funnel, business commands, aiuto business.
---

## Show
```
=== BUSINESS DEVELOPMENT WORKFLOW HELP ===

THE FUNNEL:
  Capture → Evaluate → Techscape → Research → Validate → MVP Spec → Build → Review

COMMANDS:

  IDEATION:
    /biz:biz-capture    → Capture a new idea, problem, or insight
    /biz:biz-status     → Dashboard of all ideas and their funnel stage
    /biz:biz-help       → This help screen

  EVALUATION:
    /biz:biz-evaluate   → Score idea against 6 criteria (problem, market, WTP, competition, advantage, feasibility)
    /biz:biz-research   → Deep market research (competitors, TAM/SAM/SOM, monetization)
    /biz:biz-techscape  → Map existing tools, OSS, APIs, licenses (build vs buy)
    /biz:biz-validate   → Test critical assumptions before committing to build

  BUILD:
    /biz:biz-mvp-spec   → Generate technical MVP spec (bridge to dev: /dev:j-new-project, /dev:bbc-analyze)
    /biz:biz-review     → Check if development is still aligned with business goals

  LIFECYCLE:
    /biz:biz-pivot      → Fork an idea into a new direction (preserves original + history)
    /biz:biz-close      → Kill an idea with documented reasons and lessons learned

=== HOW IT WORKS ===

1. Have an idea? → /biz:biz-capture (just talk, it structures everything)
2. Is it any good? → /biz:biz-evaluate (scores 1-60, honest assessment)
3. Score >= 25? → /biz:biz-techscape (what exists: tools, OSS, licenses, build vs buy — cheap scan first)
4. Still promising? → /biz:biz-research (competitors, market size, money — deeper and costlier)
5. Will it work? → /biz:biz-validate (test assumptions with evidence)
6. Ready to build? → /biz:biz-mvp-spec (technical spec, weeks not months)
7. During dev → /biz:biz-review (are we building the right thing?)

=== SCORING ===

6 dimensions, each 1-10 (total /60):
  < 25  → Park it, not worth pursuing
  25-35 → Weak, needs passion to justify
  35-45 → Worth researching seriously
  45+   → Strong candidate, move fast

=== KEY PRINCIPLES ===

- Problem first, solution second
- Evidence over opinion
- Kill bad ideas early (it's smart, not failure)
- MVP = weeks, not months
- Every idea gets tracked in ideas/registry.md

=== FILE STRUCTURE ===

ideas/
  registry.md          → Master list of all ideas
  evaluations/         → Scores and assessments (pivot records also live here)
  research/            → Market research reports
  research/*-techscape → Build vs buy analysis
  validations/         → Assumption testing results
  mvp-specs/           → Technical specifications

=== REPO STRATEGY ===

Phase 1 - Ideation (standalone repo):
  Create a repo for your ideas. Use /biz:biz-capture through /biz:biz-mvp-spec here.
  All output goes to ideas/ folder with its own Memory Bank.

Phase 2 - Development (ideas repo becomes submodule):
  When an idea is ready, create the dev project repo, then:
    git submodule add <ideas-repo-url> ideas
  Now /biz:biz-review works in the dev project (sees code + ideas/).
  The ideas repo stays independently updatable.

=== QUICK START ===

Never used before? Just run: /biz:biz-capture
It creates everything you need.
```
