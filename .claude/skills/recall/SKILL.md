---
name: recall
description: Query the project knowledge base in .claude/knowledge/. Surfaces relevant business and architecture entries and flags conflicts with proposed work. Use at the start of plan-feature, before settling on an approach, when touching an unfamiliar domain area, or when the user asks "what do we know about X?"
---

# Recall Skill

Look up what this project already knows about a topic before deciding how to extend it. Two outputs: (1) a short summary of relevant entries so you can write with context, and (2) any **conflict warnings** when the proposed work would contradict an existing invariant or pattern.

## When to invoke

- At the start of `plan-feature` (mandatory — every plan starts with one recall call).
- Before choosing an approach for any non-trivial change.
- When touching a domain area you haven't worked in this session.
- When the user asks "what do we have on X?", "any prior decisions about Y?", or `/recall`.

## Inputs

One of:
- `--query "<free text>"` — natural-language topic (e.g. `"user signup flow"`, `"how do we handle JWT refresh"`).
- `--topic <slug>` — fetch a specific entry by slug (e.g. `business/user-signup`).
- `--against "<proposed change>"` — additionally run a conflict pass against the proposed change.

If invoked with no input, ask the user what to look up.

## Process

1. **Read `.claude/knowledge/INDEX.md`.** If it doesn't exist or is empty, return: *"No knowledge captured yet."* and stop.

2. **Score candidates.** For each indexed entry, compute relevance from (a) the `description` line in the INDEX and (b) the entry's own frontmatter `description` if you read it. Match against the query. Pick the top 5 (or fewer if the INDEX is short).

3. **Read top matches in full.** Use `Read` for each candidate file. If a business entry's `related:` lists architecture entries (or vice versa), pull those too — they belong together.

4. **Conflict-detection pass** — only when `--against` is set OR when the user message that triggered this recall describes a proposed change.
   - For each relevant entry, scan its `Invariants` (business) and `When NOT to use` (architecture) sections.
   - If the proposed change violates an invariant or triggers a "when not to use" clause, mark it a conflict.
   - Include the conflicting file path and quote the violated line.

5. **Return a structured summary to the conversation.** Format:

```
## Recall: <query>

### Relevant business knowledge
- [Title](business/<slug>.md) — one-line summary of what it says.

### Relevant architecture knowledge
- [Pattern](architecture/<slug>.md) — what it provides; when used.

### Conflicts ⚠
- `business/<slug>.md` invariant "<quote>" is contradicted by the proposed change. Resolve before planning.

### Nothing else relevant.
```

If no matches: *"No relevant entries. Knowledge base has N business, M architecture entries; none score above the relevance threshold."*

## Heuristics for relevance scoring

- Treat exact slug match as the strongest signal.
- Treat description-line word overlap as the next signal.
- Title-word overlap matters less.
- Boost entries whose `related:` list includes another entry you already matched.

You don't need a numeric score — a qualitative "definitely relevant / maybe relevant / skip" is enough. Err on the side of including borderline matches; the cost of an extra read is small and missing a conflict is expensive.

## Conflict-detection examples

- Proposed: *"Let users have multiple email addresses."* Existing invariant: *"Email is unique per user."* → conflict.
- Proposed: *"Use a Redis cache for session state."* Architecture entry's "When NOT to use" list: *"don't reach for caches before a measured perf bottleneck."* → conflict (soft — surface it; the user may have a reason).
- Proposed: *"Add a new commit inside `LoginCommandHandler`."* Existing architecture pattern says: *"One commit per use case."* → conflict.

When you flag a conflict, include the proposed change's wording AND the existing rule verbatim so the user can adjudicate.

## What NOT to do

- Don't paraphrase entries — quote them. The user needs the original wording to judge conflicts.
- Don't make recommendations beyond surfacing knowledge. The skill informs; `plan-feature` decides.
- Don't read every entry on every call — that's why the INDEX exists. Scope ruthlessly.
