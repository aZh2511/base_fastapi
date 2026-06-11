---
name: handover-frontend
description: Produce a backend→frontend handover document so the FE team can pick up new backend work without needing context from the BE session. Output goes to docs/handovers/<YYYY-MM-DD>-<slug>.md. Pulls business context from the matching plan or business knowledge entry. Use when a backend change is ready for UI work.
---

# Frontend Handover Skill

Write a self-contained document that lets the frontend team implement against new backend work without reading the backend session, the backend code, or the planning history. The doc is the contract.

## When to invoke

- A backend feature is shipped (or merged into a feature branch) and needs UI work.
- The user says "write a handover for the FE team", "doc this for frontend", `/handover-frontend`, or similar.
- During `plan-feature`'s post-approval reminders, you flagged that a handover would be needed.

Do NOT invoke:
- Mid-implementation when the backend isn't settled yet (the doc would go stale).
- For BE-only changes with no UI surface.

## Inputs

- `--from-plan <path>` — base on a `.claude/plans/<slug>.md`. **Preferred** — the plan already has business idea, invariants, scenarios.
- `--from-business <slug>` — base on a `.claude/knowledge/business/<slug>.md` entry.
- No flag — ask the user which source artifact to use.

## Output location

`docs/handovers/<YYYY-MM-DD>-<slug>.md` (visible — the FE team consumes this; it lives in the doc tree, not under `.claude/`).

## Required structure

```markdown
# Handover: <Feature> — backend → frontend

**Date:** <YYYY-MM-DD>
**Source plan:** `.claude/plans/<slug>.md` (or business entry path)
**Backend status:** <Merged into main / On branch X / Ready for QA>

## 1. Business idea
<Short prose. Pulled from the plan/business entry's "Business idea" section, lightly edited for an FE audience. No backend jargon.>

## 2. Why / what for
<Motivation. Why this matters to the user. What problem it solves.>

## 3. Invariants
<Bullet list. These are rules the UI must also respect — disabling a button, hiding a field, etc.>

## 4. Logic
<The flow, step by step. Who triggers it, what happens server-side, what the UI sees back. Sequence diagrams (text-form) are welcome.>

## 5. Backend changes

### Endpoints
For each new/changed endpoint:

- **`METHOD /path`** — short description.
  - **Auth:** <none | bearer | cookie>
  - **Request:**
    ```json
    {
      "<field>": "<type — constraint>"
    }
    ```
  - **Response (success):** status code + body schema.
  - **Errors:** list each error case with status code + body shape.

### New error codes / exceptions
<Any new error responses the FE needs to handle.>

### New env vars / config
<Public-facing config the FE needs to know about (e.g. new public keys, new origins). Skip if none.>

### Migration / breaking-change notes
<If this is a breaking change, what FE must update. Skip if not.>

## 6. Frontend asks
What the FE team needs to build. Be concrete.

- **UI surface:** screens/components affected.
- **Validation:** what to validate client-side (mirror server invariants).
- **Error handling:** which error codes map to which user-facing messages.
- **Empty / loading / error states.**
- **Accessibility / i18n notes** (if any).

## 7. Test scenarios for FE (Given/When/Then)
<Carry the scenarios from the plan into FE-flavored form. Map server outcomes to user-visible UI outcomes.>

- **Scenario:** <name>
  - Given <UI state>
  - When <user action>
  - Then <UI outcome> (and: backend received `<request>` → returned `<response>`).

## 8. Open questions for FE
<Anything you couldn't answer from the backend side. Skip if none.>
```

## Process

1. **Locate the source artifact** (plan or business entry). If neither is given, ask.
2. **Skim the source.** Pull sections 1–4 + 7 from the source's `Why`, `Business idea`, `Invariants`, and `Business scenarios` sections.
3. **For section 5 (backend changes)**, read the actual implementation:
   - For each new endpoint, find the route definition and schema files. Cite real request/response shapes — don't paraphrase from the plan.
   - For exceptions, read the exception-handler mapping (or equivalent) to confirm status codes.
4. **Translate scenarios from BE language to FE language** in section 7. Each Given/When/Then should make sense to a developer who hasn't seen the backend.
5. **Write the file** to `docs/handovers/<YYYY-MM-DD>-<slug>.md`. Create `docs/handovers/` if missing.
6. **Report:** path written + a one-line summary suitable for posting in chat to the FE team.

## Idempotency

- If a handover for the same `<slug>` already exists for an earlier date, that's fine — leave it. New handover gets today's date prefix and supersedes it. Reference the prior doc at the top of the new one (*"Supersedes `docs/handovers/<prior-date>-<slug>.md`"*).
- If a handover for **today's** date and the same slug already exists, edit it instead of creating a duplicate.

## Style

- Write for an FE developer who hasn't read the backend code. No backend jargon (no "handler", "Protocol", "command/query"; instead "endpoint", "response", "request").
- Be concrete with shapes. If a response has a UUID, say so (and what it represents).
- Keep prose tight. The doc gets skimmed first; nobody reads 500 words to find the request schema.
