# 032 – Constraint Hierarchy Meta-Spec for Completeness/Method/Scope/Style – Work Log

## 2025-12-09 – Slice: Embed hierarchy in axis interpreter

**ADR focus**: 032 – Constraint Hierarchy Meta-Spec for Completeness/Method/Scope/Style  
**Loop goal**: Enforce the completeness>method>scope>style hierarchy inside the axis interpreter with prefix handling and cross-axis recovery.

### Summary of this loop

- Added hierarchy-aware helpers in `lib/talonSettings.py`:
  - `_resolve_axis_for_token` respects explicit `Completeness:/Method:/Scope:/Style:` prefixes and uses priority order to disambiguate adjectives found in multiple axes.
  - `_apply_constraint_hierarchy` reassigns misfiled tokens across axes, canonicalises with existing caps/conflicts, and feeds the resolved axes into the system prompt and recipe state.
  - Constraint rendering now surfaces reclassified tokens (for example, prefixed or cross-axis matches) so the Task block reflects the effective axes.
- Updated `modelPrompt` to run all axis tokens through the hierarchy before composing prompts and GPTState fields.
- Added tests in `_tests/test_talon_settings_model_prompt.py` covering prefixed overrides and cross-axis recovery (method token provided under style).

### Behaviour impact

- Axis interpretation now honours the ADR hierarchy automatically, correcting prefixed or misfiled adjectives into the highest-priority matching axis and exposing the resolved axes in both state and prompt text.

### Follow-ups

- Consider surfacing a compact/verbose hierarchy description in help/GUI surfaces drawn from ADR 032.
- Add coverage for ambiguous adjectives once we introduce overlapping tokens or richer adjective vocabularies.
