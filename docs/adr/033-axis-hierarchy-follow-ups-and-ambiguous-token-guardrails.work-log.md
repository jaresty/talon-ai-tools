# 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails – Work Log

## 2025-12-09 – Slice: Ambiguous token guardrail + UI surfacing

**ADR focus**: 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails  
**Loop goal**: Add regression coverage for ambiguous tokens/prefix priority and surface the hierarchy in help/docs.

### Summary of this loop

- Audit: current axis lists show no overlapping tokens/values across completeness/scope/method/style.
- Tests: added `_tests/test_talon_settings_model_prompt.py::test_ambiguous_token_uses_priority_order`, monkeypatching overlapping tokens to assert the Completeness>Method>Scope>Style resolution and ensure misfiled tokens land on the higher-priority axis.
- UI/help: updated `_build_axis_docs` in `GPT/gpt.py` to include the hierarchy and prefix syntax so quick help surfaces explain how conflicts resolve.
- Downstream consumers: added `_tests/test_talon_settings_model_prompt.py::test_last_recipe_uses_resolved_axes` to confirm `last_recipe` serialises the resolved axes (not raw misfiled tokens).

### Behaviour impact

- Ambiguous tokens (when present) now have explicit regression coverage for the hierarchy and priority resolution.
- Users see the hierarchy and prefix rules in help surfaces, reducing confusion about cross-axis interpretation.
- Recipes now explicitly asserted to reflect resolved axes for replay/suggestions.

### Follow-ups

- Consider a lightweight notification/tooltip when tokens are reassigned across axes.
- Add tests for prefix overrides on ambiguous tokens if overlapping vocab is introduced in the lists.

## 2025-12-09 – Slice: Request history stores resolved recipe

**ADR focus**: 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails  
**Loop goal**: Ensure request history/log entries capture the resolved axis recipe for replay/inspection.

### Summary of this loop

- Added `recipe` field to `RequestLogEntry` and plumbed it through `append_entry`.
- Persist `GPTState.last_recipe` (already hierarchy-resolved) into history via `modelHelpers.append_entry` call.
- Extended `_tests/test_request_log.py` to assert stored recipes.

### Behaviour impact

- Request history entries now retain the resolved recipe so downstream viewers (drawer, future replay) can show the enforced axes rather than raw/misfiled tokens.

### Follow-ups

- Consider rendering the recipe in history list/drawer surfaces.

## 2025-12-09 – Slice: Manual overlap analysis (documented)

**ADR focus**: 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails  
**Loop goal**: Perform manual, subjective overlap analysis per ADR 033 methods and record fixed-axis decisions.

### Summary of this loop

- Added `docs/adr/033-axis-overlap-analysis.md` with qualitative assessments using substitution, conflict-stress, and meaning decomposition.
- Classified ambiguous tokens (e.g., deep, focus, compact, steps, structure, bullets, table, faq, bug, codetour) to fixed axes and noted replacement/disambiguation guidance.
- Removed the prior heuristic script to keep the process manual and documented.

### Behaviour impact

- Provides a human-reviewed mapping of ambiguous adjectives to axes, aligning profiles/help with the intended hierarchy without automated heuristics.

### Follow-ups

- Keep profiles/help text in sync with the fixed-axis decisions; add lint/tests only if they enforce these explicit choices rather than heuristics.

## 2025-12-09 – Slice: Align lists/README with fixed-axis decisions

**ADR focus**: 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails  
**Loop goal**: Apply ADR 032 guardrails and manual axis decisions to vocab lists and README.

### Summary of this loop

- Moved `deep` to method; moved `headline` to style; moved `taxonomy` to method; kept `compact/tight` and related ambiguity resolved per analysis.
- Updated `GPT/lists/*Modifier.talon-list` accordingly and refreshed `GPT/readme.md` axis token lists to match.
- Confirmed tests for README/list parity and axis handling still pass.

### Behaviour impact

- Axis vocab now reflects the manual overlap decisions and ADR 032 guardrails; help text matches the current lists.

### Follow-ups

- Optional: surface resolved recipes in history/drawer UIs and add a small lint to prevent future drift from the documented fixed-axis mapping.
