---
name: plan-feature
description: Produce a feature plan that captures the business idea, invariants, Given/When/Then scenarios for TDD, and the architecture approach. Use FIRST for any non-trivial new work — features, behavior changes, new domain rules. Skip for typo fixes, single-line bug fixes, or mechanical refactors. When in doubt, ask "is this a fix or a new feature?" before assuming.
---

# Plan Feature Skill

The first step of any non-trivial work in this project. Forces the session to start from the business: what is the user actually trying to do, what must always be true, what scenarios exercise the rules. The output drives both the implementation AND the Test-Driven Development step that follows — the Given/When/Then scenarios in the plan become the failing tests written first.

## When to invoke

- The user is starting a new feature, changing existing behavior, adding/changing a domain rule, or sketching a system change.
- The user asked you to "plan", "design", "scope", "think about", "figure out how to", or similar for a non-trivial change.
- You're about to write more than ~20 lines of new code that crosses any layer boundary.

## When to skip

- Typo or copy fix.
- A single-line or single-file bug fix where the root cause is already understood.
- Mechanical refactor (rename, file move, type-only change) that doesn't change behavior.
- The user explicitly says "skip planning, just do X".

If you're unsure whether the task qualifies, ask once: *"Is this a quick fix, or a new behavior worth planning?"* — then proceed accordingly.

## Process

1. **Call `recall` first.** Pass the topic/domain in plain English. Read what comes back: relevant existing business entries, architecture patterns to reuse, and any flagged conflicts. If `recall` surfaces a conflict between what the user wants and an existing invariant, raise it with the user before drafting the plan.

2. **Gather missing business context.** If the user's request leaves business intent ambiguous (who does this serve, what problem does it solve, what must always be true), ask 1–3 targeted questions via `AskUserQuestion`. Do not invent answers. Skip questions you can answer from `recall` results.

3. **Draft the plan to `.claude/plans/<slug>.md`** using the structure below. `<slug>` is kebab-case derived from the feature name. If a plan file already exists for this feature, edit it; do not create a duplicate.

4. **Walk the user through the plan and request approval** via `ExitPlanMode` (if you're in plan mode) or a direct ask. The plan should be tight enough to scan in a minute but explicit on invariants and scenarios.

5. **After approval**, remind the user (in one short sentence) that:
   - Implementation should follow the TDD steps in the plan inside-out, writing tests for the Given/When/Then scenarios first.
   - When work is shipped, run `/learn` to persist business + architecture knowledge.
   - If a backend change needs UI, run `/handover-frontend` before closing out.

## Required plan structure

```markdown
---
title: <Feature name>
slug: <kebab-slug>
status: draft
related-business: [<existing business slugs you consulted>]
related-architecture: [<existing architecture slugs you consulted>]
---

# <Feature name>

## Why
<Problem this solves. Intended outcome. Who benefits. 2–5 sentences.>

## Business idea
<The domain story in prose. What the system does, from the actor's point of view, when this feature is in place. 1–2 paragraphs.>

## Invariants
- <Rule that must always hold.>
- <Another rule.>
<Be specific. "Email is unique per user" beats "data is consistent".>

## Business scenarios (Given/When/Then)
These ARE the test cases. The implementation step writes failing tests for these first.

- **Scenario:** <short name>
  - Given <starting state>
  - When <actor action>
  - Then <observable outcome>

<Repeat for every meaningful path: happy path, edge cases, error paths.>

## Cross-cutting concerns
<Auth, permissions, audit, observability, rate-limiting, idempotency — only the ones that apply. Skip the section if none.>

## Architecture approach
<Which patterns from .claude/knowledge/architecture/ are reused (link them: [[architecture/<slug>]]). Any deltas or new patterns introduced. If a new pattern emerges, name it here so it has a slug for /learn to file under.>

## Implementation steps (inside-out, TDD)
1. **Domain** — entities, value objects, invariants.
2. **Application** — commands/queries/handlers (CQRS if applicable).
3. **Infrastructure** — repositories, services, migrations.
4. **Presentation** — endpoints/schemas, or whatever the project's outermost layer is called.

At each step: write failing tests from the scenarios above → implement minimum → green → move on.

## Open questions
- <Anything the user needs to decide before implementation can proceed.>

## After approval
- Run `/learn` once the feature ships to persist business + architecture knowledge.
- Run `/handover-frontend` if a UI change is downstream.
```

Sections that don't apply may be omitted (e.g. no cross-cutting concerns for a small isolated rule), but **Why / Business idea / Invariants / Business scenarios / Architecture approach / Implementation steps** are always required.

## Idempotency and edits

- If the plan file exists with the same `slug`, read it first, then edit in place — don't create `<slug>-2.md`.
- If the user changes their mind mid-planning, update the existing plan; don't accumulate stale drafts.
