---
name: learn
description: Persist business and architecture knowledge from an approved plan or shipped feature into .claude/knowledge/. Splits the plan into a business entry (the domain rules, scenarios, motivation) and an architecture entry (the reusable pattern that stands alone without business context). Cross-links the two. Updates the INDEX. Use after a plan is approved/shipped, at session end if substantive work landed, or when the user says "save this", "remember this", "/learn".
---

# Learn Skill

Take the durable knowledge from this session — what the system now does and how it's structured — and write it down so future sessions (in this project, or any project reusing the architecture entry) can pick it up cold.

## When to invoke

- A `/plan-feature` plan was just approved.
- A feature shipped this session (PR merged, work landed).
- The user said "save this", "remember this", "capture this", or `/learn`.
- At session end, if anything substantive landed and hasn't been captured yet.

Do NOT invoke for:
- In-flight work that hasn't settled.
- Ephemeral debugging state.
- Anything already in `.claude/knowledge/` (update, don't duplicate — see Idempotency).

## Two artifacts per feature

Every invocation produces (or updates) two files:

- **Business entry** → `.claude/knowledge/business/<slug>.md`. Carries Why, Business idea, Invariants, Scenarios. This is project-specific knowledge — it depends on the product.
- **Architecture entry** → `.claude/knowledge/architecture/<slug>.md`. Carries the pattern, its rationale, structural sketches, and trade-offs. **Written so it stands alone without the business context** — that's what makes it portable to other projects.

The two files cross-link via `related:` in frontmatter and `[[business/<slug>]]` / `[[architecture/<slug>]]` inside the body.

## Frontmatter (both types)

```yaml
---
name: <kebab-slug>
type: business | architecture
status: draft | approved
description: <one-line — used by recall to score relevance; be specific>
related: ["business/<slug>", "architecture/<slug>", ...]
---
```

## Business entry body

```markdown
# <Title>

## Why
<Problem this solves. Who benefits.>

## Business idea
<Domain story in prose.>

## Invariants
- <Rule.>

## Scenarios (Given/When/Then)
- **<name>**
  - Given …
  - When …
  - Then …

## Architecture patterns this exercises
- [[architecture/<slug>]] — why this pattern fits.

## History
- <YYYY-MM-DD>: Captured from `.claude/plans/<slug>.md` (status: approved).
```

## Architecture entry body

```markdown
# <Pattern name>

## What it is
<One paragraph: the pattern's shape, the problem it solves, the trade-off it accepts.>

## When to use
- <Trigger 1>
- <Trigger 2>

## When NOT to use
- <Counter-trigger 1>

## Structure
<Code sketch, file layout, or diagram fragment. Just enough to seed an implementation. Keep names generic — `Entity`, `Service`, not the project's specific names — so the pattern transfers.>

## Trade-offs
- **Pro:** …
- **Con:** …

## Where this lives in the project
<Concrete file paths in the current project. The only project-specific section — readers in other projects will skip it.>

## Cross-references
- [[business/<slug>]] — example use case.

## History
- <YYYY-MM-DD>: Captured. Source plan: `.claude/plans/<slug>.md`.
```

## Process

1. **Locate the source.** Usually a plan file under `.claude/plans/<slug>.md`. If the user invoked `/learn` ad-hoc without a plan, ask them to point at the source artifact (a plan, a PR, an inline summary).

2. **Check for existing entries.** Read `.claude/knowledge/INDEX.md`. If a business or architecture entry already exists for this slug:
   - If the body is unchanged, skip and report.
   - If the body needs updating, edit in place; bump `History` with today's date.
   - Never create `<slug>-2.md` — slug is the stable identity.

3. **Split the plan.** Map plan sections to entries:
   - Plan → business: `Why`, `Business idea`, `Invariants`, `Business scenarios`.
   - Plan → architecture: `Architecture approach` (the named pattern, its rationale, any sketches). If the plan reuses an existing pattern wholesale and introduces no new pattern, skip writing a new architecture entry — just update the existing one's cross-reference list to include the new business slug.

4. **Write the two entries** to their respective paths.

5. **Update `.claude/knowledge/INDEX.md`** — one new line per new entry in the matching section:
   ```
   - [Title](business/<slug>.md) — one-line hook
   ```
   Keep the INDEX under ~200 lines; truncate older entries or factor by topic if it grows.

6. **Cross-link.** Update `related:` in both frontmatters and add `[[business/<slug>]]` / `[[architecture/<slug>]]` markers in bodies as appropriate.

7. **Mark the source plan** by editing its frontmatter `status: approved` and adding a footer line: `Persisted via /learn on <YYYY-MM-DD> → business/<slug>.md, architecture/<slug>.md`.

8. **Report** what was written, one short block. Group by type. Mention any skips.

## What NOT to save

Same exclusions as auto-memory, applied to the knowledge base:

- Code patterns trivially derivable from the current source tree.
- Git history, who-changed-what.
- Debugging recipes — the fix is in the code.
- Ephemeral or in-progress state.
- "What we did this session" summaries — the diff is the record.

If a candidate falls in this list, push back: ask the user what was non-obvious about it that's worth keeping.

## Promotion to global blueprint

If a brand-new architecture pattern emerges that you think belongs in the user-global blueprint (so future projects start with it), flag it to the user at the end: *"Pattern `<slug>` looks general — want me to also save it as a starter entry in the global blueprint?"* Don't write to the global blueprint without explicit confirmation.

## Report format

```
Saved knowledge:

Business:
- [Title](business/<slug>.md) — gist

Architecture:
- [Pattern](architecture/<slug>.md) — gist

INDEX updated: 2 new entries.
Plan `.claude/plans/<slug>.md` marked approved.
```
