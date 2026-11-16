---
allowed-tools: Read(/${CLAUDE_PLUGIN_ROOT}/**)
description: "BDD overlay - the Use Case → Gherkin → step definitions methodology. Loaded only when an experienced developer asks for it; the j-* commands do not load it on their own."
---

# BDD Overlay — Use Case → Gherkin → step definitions

**Loaded only on request.** Executable specifications are demanding work: an experienced developer
asks for this file, and the j-* commands never load it on their own. It goes together with the
language's `overlays/<language>/testing.md` and `overlays/<language>/tddab.md`, which own the style,
the tooling, the assertions and the RED/GREEN/VERIFY mechanics. This file adds only what they do not
have: how a use case becomes an executable specification.

## What this methodology is for

A use case is written for a person — it says who wants what, and why. A test is written for a
machine. Gherkin is the one artifact both can read, so it becomes **the specification itself**
rather than a description of one: the scenario is what gets run, and the implementation is done
when the scenario is green.

That only works if the scenarios are written against the real system — real HTTP, real database,
real authentication — because a scenario satisfied by mocks proves that the mocks agree with each
other.

## Step 1 — Analyse the use case

1. Read the use case document (`UC-<id>`) and name the actor, the action and the benefit
2. Map each business scenario onto a real endpoint or entry point, using the project's code
   navigation tool (`@code-nav-local`) on the endpoints involved
3. Separate what already exists from what has to be built
4. With the security branch, name the authentication and authorization each scenario needs
5. Present that analysis before writing any scenario

## Step 2 — Translate into Gherkin, with the real types

Before writing a scenario, look up the ACTUAL type the endpoint returns and the real names and
types of its fields — as declared, since serialization is as is (`code-principles.md` 3.5). A scenario written against invented field names passes review and then
fails for a reason that has nothing to do with the behaviour under test.

```gherkin
Feature: <use case name>
  As a <role>
  I want to <action>
  So that <benefit>

Background:
  Given the following users exist:
    | Email | FirstName | LastName | Role |

Scenario: <happy path>
  Given I am authenticated as "<email>"
  When I send a GET request to "<endpoint>"
  Then the response status should be 200
  And the response should contain User:
    | Field    | Value              | Type               |
    | Id       | {int}              | int                |
    | Email    | "user@example.com" | string             |
    | Role     | "SystemAdmin"      | UserRole as string |
    | IsActive | true               | bool               |
```

The type is named in the scenario, and so is each field's type: that is what makes the scenario a
contract instead of a sentence.

Scenarios cover the happy path, the error cases, the boundaries, and — with the security branch —
the authorization cases: the coverage `testing-principles.md` 2.2 asks of every test, expressed at the
use-case level.

## Step 3 — Implement the step definitions

Step definitions are a thin translation layer: parse the table, call the system, keep the
response. The business rules live in the code under test, never in a step definition — a rule
implemented twice drifts, and the scenario then proves the step definition right.

Reuse the shared steps the project already has rather than redefining them per feature:

```
Given I am authenticated as "<email>"
Given I am not authenticated
When I send a <METHOD> request to "<endpoint>"
Then the response status should be <code>
Then the response should contain: <table>
Then the response error should be "<message>"
```

The language's form — the runner, the host shared by the run, the bindings — is in
`overlays/<language>/bdd.md`.

Test isolation comes from a transaction against the real database, not from an in-memory
substitute: an in-memory provider accepts queries the real engine rejects, so the scenario is
green on something that would not run in production.

## Step 4 — Run the scenarios and let them be red

Run them with the command and the filter of the language's `overlays/<language>/tddab.md`, filtered
to the feature. Red is the starting point: the scenario now states
the gap in the terms of the use case.

## Step 5 — The loop

1. Read the failure and say what is missing
2. **Technical gaps you close yourself**: a missing import, a wrong signature, a step definition
   that does not exist yet, a typo in a route, a compilation error
3. **Domain questions go to the user**, because they change what "correct" means: should this
   endpoint exist, or should the scenario change? What may this role see? What is the business
   rule at this boundary? Is this the intended security behaviour? Present the issue as: what
   the scenario expects, what the system does, and the options with their consequence
4. Implement, re-run, repeat until green

## Step 6 — Close the use case

The use case is done when every scenario is green against the real system, the code is
refactored with the scenarios still green, and the use case document records which scenarios
cover it. Then the next use case starts from step 1.
