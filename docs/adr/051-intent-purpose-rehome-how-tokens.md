# 051 – Keep intent/intent purely “Why” and re-home “How/What” tokens

## Status
Accepted

## Context
- ADR 040/048 define persona/intent as **Who/Why** (voice, audience, tone, intent, presets). Contract axes (static prompt, completeness, scope, method, form, channel, directional) carry **What/How/Where**.
- The current `intent` axis contains several tokens that describe session style, techniques, or deliverable shapes instead of the reason for speaking. Examples: `for walk through`, `for collaborating`, `for facilitation`, `for discovery questions`, `for jobs to be done`, `for user value`, `for pain points`, `for definition of done`, `for team mapping`, `for project management`.
- Keeping these on the intent axis blurs Why vs How, makes validation/suggestion guardrails weaker, and duplicates semantics that already belong to method/form/destination or to a dedicated static prompt recipe.

## Decision
- **Restrict intent/intent to “Why” only.** Keep intent tokens that describe motivation/outcome (teach, decide, evaluate, brainstorm, appreciate, persuade, coach, collaborate-as-why, entertain, inform).
- **Re-home “How/What” intent tokens to contract axes or presets:**
  - Session/process (method): `for walk through` → method/pattern (step-by-step walkthrough); `for collaborating` → method (co-create/iterate), or leave only as preset seasoning; `for facilitation` → method (facilitation toolkit); `for discovery questions` → method (probing/interview).
  - Deliverable/shape (form/style/static prompt): `for jobs to be done`, `for user value`, `for pain points`, `for definition of done`, `for team mapping`, `for project management` → move to form/style tokens or explicit static prompt recipes; keep intent axis free of artifact labels.
- **Add/strengthen guardrails** so intent descriptions/tokens cannot include obvious container/process phrases and so reintroduced “How/What” tokens are rejected in tests.
- **Document migrations in help surfaces** (help hub, canvas quick help) so users see the new placements instead of intent tokens.

## Rationale
- Aligns with the Who/Why vs What/How split from prior ADRs, reducing overlap and ambiguity.
- Improves suggest/stance validation: intent validation can stay strict (“include a known intent token”), while process/deliverable controls live on the method/form axes that already model them.
- Keeps intent table understandable and compact, avoiding a catch-all bin for workshop techniques or output formats.

## Migration Plan
1) Remove the “How/What” tokens from `GPT/lists/modelIntent.talon-list` and `PERSONA_KEY_TO_VALUE["intent"]`.
2) For each removed token, add the appropriate replacement:
   - Method axis: walkthrough/step-by-step, collaborate/co-create, facilitation, discovery probing.
   - Form/style/static prompt: JTBD/value/pain/DoD/team mapping/PM artifacts (e.g., analysis write-ups, maps, acceptance criteria).
3) Update help/UX text (Help Hub, modelHelpCanvas, suggestion context) to point to the new axis homes.
4) Add/extend guardrail tests (axis-family separation, persona docs) to fail on reintroducing non-Why intent tokens or intent descriptions that encode containers/process.
5) Run validation/tests (`python3 -m pytest`) after regenerating any axis catalogs/configs.

## Consequences
- Clearer stance vocabulary; users pick intent for motivation and method/form/static prompt for process and outputs.
- Slight relearning cost for users who relied on these intent tokens; mitigated via help messaging and presets.
- Reduced risk of intent axis accumulating deliverable/process semantics, keeping validation simpler and hydration consistent.

## Token re-homing (one destination each, single-word names)
- `for walk through` → **Method: `walkthrough`**. Rationale: process/sequence, not motivation.
- `for collaborating` → **Method: `cocreate`**. Rationale: interaction style/how we work together.
- `for facilitation` → **Method: `facilitate`**. Rationale: workshop facilitation technique.
- `for discovery questions` → **Method: `probe`**. Rationale: questioning technique.
- `for jobs to be done` → **Static prompt: `jobs`**. Rationale: specific analysis/deliverable shape.
- `for user value` → **Static prompt: `value`**. Rationale: deliverable describing value/impact.
- `for pain points` → **Static prompt: `pain`**. Rationale: artifact capturing pains; not a why.
- `for definition of done` → **Static prompt: `done`**. Rationale: output format for acceptance gates.
- `for team mapping` → **Static prompt: `team`**. Rationale: structural mapping artifact.
- `for project management` → **Retire**. Rationale: low value as intent and unclear unique need elsewhere.
