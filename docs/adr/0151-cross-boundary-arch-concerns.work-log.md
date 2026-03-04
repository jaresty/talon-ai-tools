# ADR-0151 Work Log — Cross-Boundary Architectural Concerns

---

## Loop-1 — 2026-03-03T00:00:00Z

```yaml
helper_version: helper:v20260227.1
focus: >
  ADR-0151 §Axis Drift Guard — create ast-grep lint rule, re-export axisConfig
  symbols through axisMappings façade, fix 4 production violations, wire CI.
  Salient task: T-1 (Axis Import Guard).

active_constraint: >
  No structural enforcement prevents production code from importing axisConfig
  symbols directly, bypassing the axisMappings/axisCatalog façades. Demonstrated
  by: ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
  exits 1 with 4 error-level matches. This outranks persona resolution
  (T-2) because SSOT regression has occurred twice and the fix is mechanical;
  outranks grammar pipeline (T-3) which is already mitigated by bar-grammar-check.

validation_targets:
  - T-1: >
      ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
      exits 0 (no error-level matches in production code excluding façades).

evidence:
  - red | 2026-03-03T00:00:00Z | exit=6 |
      ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
      (rule file absent — "Cannot read rule rules/no-direct-axisconfig-import.yml")
      | inline
  - red | 2026-03-03T00:01:00Z | exit=1 |
      ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
      (rule present, 4 violations found: modelTypes.py:4, modelHelpCanvas.py:8,
      modelResponseCanvas.py:27, modelPatternGUI.py:31) | inline
  - green | 2026-03-03T00:05:00Z | exit=0 |
      ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
      (no matches after adding axisMappings re-exports and fixing 4 callers) | inline
  - removal | 2026-03-03T00:06:00Z | exit=1 |
      git stash && ast-grep scan --rule rules/no-direct-axisconfig-import.yml lib/ GPT/
      (reverted to pre-fix state; violations returned; git stash pop restored) | inline

rollback_plan: >
  git restore lib/axisMappings.py lib/modelHelpCanvas.py lib/modelResponseCanvas.py
  lib/modelPatternGUI.py lib/modelTypes.py Makefile .github/workflows/test.yml
  && git rm rules/no-direct-axisconfig-import.yml
  Re-run red validation to confirm failures return.

delta_summary: >
  helper:diff-snapshot=7 files changed + 1 new file (rules/)
  - rules/no-direct-axisconfig-import.yml: new ast-grep YAML rule (severity: error,
    patterns: from .axisConfig import $SYMBOL and from ..lib.axisConfig import $SYMBOL,
    ignores: axisConfig.py, axisMappings.py, axisCatalog.py, _tests/, tests/)
  - lib/axisMappings.py: added axis_docs_for, axis_key_to_kanji_map to the import
    from axisConfig, making them available as façade re-exports
  - lib/modelHelpCanvas.py, lib/modelResponseCanvas.py: axisConfig → axisMappings
  - lib/modelPatternGUI.py: axisConfig → axisMappings (AXIS_KEY_TO_VALUE already
    imported at axisMappings module level; no alias needed)
  - lib/modelTypes.py: axisConfig → axisMappings
  - Makefile: added axis-import-guard target + axis-import-guard to .PHONY
  - .github/workflows/test.yml: added Install ast-grep (npm) + Run axis import guard
    steps after Run tests

loops_remaining_forecast: >
  2 loops remaining (confidence: high).
  T-2 (Persona resolution observability) — next loop.
  T-3 (Grammar pipeline) — already covered by bar-grammar-check (includes
  web/static/prompt-grammar.json); ADR update only.

residual_constraints:
  - T-2 | Persona resolution chain implicit fallback | severity: Medium |
    _canonical_persona_value() 5-level fallback has no observability; loop-23
    slug bug demonstrates silent wrong-alias selection. Mitigation: add fallback
    logging in next loop. Monitoring: test_persona_proper_noun_slug_normalization
    in build.go covers known case. Owning ADR: 0151.
  - T-3 | Grammar pipeline | severity: Low |
    bar-grammar-check already validates all 5 consumer copies including
    web/static/prompt-grammar.json. Concern is effectively mitigated. ADR
    update pending. Owning ADR: 0151.

next_work:
  - Behaviour T-2: Add observability logging at each fallback level in
    _canonical_persona_value() (GPT/gpt.py:270-329). Specifying validation:
    new pytest test that patches orchestrator to return empty, fires the
    fallback path, and asserts the log record is emitted.
```
