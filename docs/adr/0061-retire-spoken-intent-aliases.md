# 0061 – Retire Spoken Intent Aliases in Favour of Canonical Tokens

- Status: Proposed  
- Date: 2025-12-23  
- Context: `talon-ai-tools` persona/intent SSOT (`lib/personaConfig.py`), GPT intent commands/helpers, docs and help surfaces that hydrate intent synonyms.  
- Related ADRs:  
  - 015 – Voice, Audience, Tone, Intent Axis Decomposition  
  - 040 – Axis Families and Persona/Contract Simplification  
  - 042 – Voice-First Persona and Intent Presets as First-Class Commands  
  - 053 – Retire the “purpose” axis label; make “intent” the single Why axis

---

## Summary (for users)

We are collapsing intent back to **single-word canonical tokens** such as `inform`, `decide`, and `plan`. Spoken phrases like `for information` or `for deciding` will stop behaving as separate alias tokens. Voice commands and help surfaces will teach and require the canonical words directly, reducing duplication and intent drift.

---

## Context

- `lib/personaConfig.py` defines `INTENT_SPOKEN_TO_CANONICAL`, inverting it into broader synonym maps via `persona_intent_maps()`. This lets every surface accept both `for information` and `inform` even though they are one-to-one.  
- Help docs, GPT help hub, and voice grammars surface both forms, so contributors maintain duplicate tables, Talon lists, and guardrails for each intent.  
- The alias layer hides violations of the “single word” rule for the intent axis (ADR 015/040). By normalising silently, we risk reintroducing multi-word tokens without noticing.  
- Field feedback prefers a crisp, memorable set of single-word intents; aliases add mental overhead and code churn without unlocking new behaviour.

---

## Decision

- Remove the spoken alias maps (`INTENT_SPOKEN_TO_CANONICAL`, `INTENT_CANONICAL_TO_SPOKEN`) and the synonym hydration they feed. Canonical tokens remain the only accepted values for the intent axis.  
- Update `persona_intent_maps()` and downstream helpers to return intent presets, display labels, and validation data without alias lookups.  
- Require canonical tokens across voice commands, Talon lists, GUIs, docs, and tests. When we need human-friendly phrasing, rely on `IntentPreset.label` (for example, “Teach / explain”) rather than alias tokens.  
- Add guardrails and tests ensuring that multi-word intent inputs raise validation errors instead of silently normalising.

---

## Consequences

- **Positive**: Single source of truth for intent tokens; fewer alias tables to maintain; simpler hydration code; easier auditing for the single-word contract.  
- **Positive**: Aligns user vocabulary with axis families (“intent = Why”), reinforcing ADR 040/053 language.  
- **Negative**: Users accustomed to `intent for information` (or GUI copy written that way) must update muscle memory; training materials need to call out the change.  
- **Negative**: We must touch several surfaces in one go (Talon lists, docs, guardrails, tests) to avoid regressions.

---

## Implementation notes / Next steps

1. Delete the spoken alias constants and adjust `persona_intent_catalog_snapshot()` so the snapshot only contains canonical tokens.  
2. Refresh Talon lists (`GPT/lists/modelIntent.talon-list`), command grammars, and help hub copy to show canonical intent tokens.  
3. Update tests and guardrails (for example `_tests/test_gpt_actions.py`, `_tests/test_gpt_suggest_context_snapshot.py`) to assert canonical-only behaviour and fail on multi-word inputs.  
4. Announce the change in release notes / help surfaces so users know to speak the canonical tokens directly.
