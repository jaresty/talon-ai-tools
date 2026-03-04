# ADR-0151 Work Log — Cross-Boundary Architectural Concerns

---

## Loop-3 — 2026-03-03T00:20:00Z

```yaml
helper_version: helper:v20260227.1
focus: >
  ADR-0151 §Grammar Pipeline — record that bar-grammar-check already addresses
  the concern; update ADR and close work-log. Salient task: T-3.

active_constraint: >
  ADR-0151 Recommendation 3 documents a gap that does not actually exist:
  bar-grammar-check validates all 5 consumer copies including web/static/
  prompt-grammar.json and runs in CI. The constraint is a documentation
  inaccuracy, not a missing implementation.

validation_targets:
  - T-3: >
      git diff docs/adr/0151-cross-boundary-arch-concerns.md exits 0 after
      updating Recommendation 3 to reflect the pre-existing bar-grammar-check
      coverage. Documentation-only loop; blocker evidence: no executable
      artifact to add because the concern is already mitigated.

evidence:
  - red | 2026-03-03T00:20:00Z | documentation-only |
      ADR-0151 Recommendation 3 states "Formalize the update sequence as a
      make target or CI check" — but bar-grammar-check already does this and
      runs in CI test.yml step "Verify grammar sync across all copies". | inline
  - green | 2026-03-03T00:22:00Z | documentation-only |
      ADR updated: Recommendation 3 crossed out and annotated "Resolved
      (pre-existing)" with enumeration of all 5 checked files. | inline

rollback_plan: >
  git restore docs/adr/0151-cross-boundary-arch-concerns.md
  No executable artefacts changed; rollback has no observable test impact.

delta_summary: >
  helper:diff-snapshot=1 file changed (docs/adr/0151-cross-boundary-arch-concerns.md)
  Recommendation 3 updated to strike-through + resolved annotation.
  All three salient tasks now complete: T-1 (loop-1), T-2 (loop-2), T-3 (loop-3).

loops_remaining_forecast: >
  0 loops remaining. All three validated concerns from ADR-0151 triage have
  been addressed: T-1 (axis import guard), T-2 (persona resolution logging),
  T-3 (grammar pipeline — pre-existing). Two speculative concerns (request
  state triplication, canvas coordination) remain deferred as documented.

residual_constraints:
  - Request state triplication | severity: Low | No causal evidence (no race
    condition observed). Deferred in ADR. Reopen if a race condition is debugged
    to this triplication. Owning ADR: 0151.
  - Canvas coordination | severity: Low | No coordination failure observed.
    Deferred in ADR. Reopen if a canvas coordination bug is reported. Owning: 0151.

next_work: >
  Work-log closed. No open behaviour outcomes remain. ADR-0151 status: Accepted.
  Future reopening conditions: race condition in request state modules, or
  canvas coordination failure in production.
```

---

## Loop-2 — 2026-03-03T00:10:00Z

```yaml
helper_version: helper:v20260227.1
focus: >
  ADR-0151 §Persona Resolution Observability — add debug logging at the docs-map
  fallback level in _canonical_persona_value (GPT/gpt.py:270-329).
  Salient task: T-2 (Persona Resolution Observability).

active_constraint: >
  _canonical_persona_value has a 5-level implicit fallback with no observability;
  the docs-map fallback (level 5) is reached silently when all higher-priority
  levels miss. Demonstrated by:
  python3 -m pytest _tests/test_persona_resolution_fallback_log.py exits 1
  ("no logs of level DEBUG or higher triggered on talon_user.GPT.gpt").
  Outranks T-3 (grammar pipeline already mitigated by bar-grammar-check).

validation_targets:
  - T-2: >
      python3 -m pytest _tests/test_persona_resolution_fallback_log.py exits 0.
      Test patches orchestrator to None and canonical_persona_token to "", then
      asserts assertLogs captures a "docs_map" record at DEBUG level.

evidence:
  - red | 2026-03-03T00:10:00Z | exit=1 |
      python3 -m pytest _tests/test_persona_resolution_fallback_log.py
      (test file present, logging absent in gpt.py —
      "no logs of level DEBUG or higher triggered on talon_user.GPT.gpt") | inline
  - green | 2026-03-03T00:14:00Z | exit=0 |
      python3 -m pytest _tests/test_persona_resolution_fallback_log.py
      (1 passed after adding _log = logging.getLogger(__name__) and
      _log.debug("persona_resolution_fallback ... level=docs_map ...") before
      the docs loop in _canonical_persona_value) | inline
  - removal | 2026-03-03T00:15:00Z | exit=1 |
      git stash && python3 -m pytest _tests/test_persona_resolution_fallback_log.py
      (reverted gpt.py logging; test fails again with "no logs"; git stash pop) | inline

rollback_plan: >
  git restore GPT/gpt.py && rm _tests/test_persona_resolution_fallback_log.py
  Re-run red validation to confirm failure returns.

delta_summary: >
  helper:diff-snapshot=2 files changed
  - GPT/gpt.py: import logging + _log = logging.getLogger(__name__) at top;
    _log.debug("persona_resolution_fallback axis=%s raw=%r level=docs_map
    orchestrator=%s", ...) inserted before the docs loop in _canonical_persona_value
  - _tests/test_persona_resolution_fallback_log.py: new specifying validation;
    patches orchestrator/personaConfig/persona_docs_map, asserts assertLogs fires
    at DEBUG level with "docs_map" in message

loops_remaining_forecast: >
  1 loop remaining (confidence: high).
  T-3 (Grammar pipeline) — bar-grammar-check already addresses this concern;
  loop will update ADR-0151 to record it as resolved and close the work-log.

residual_constraints:
  - T-3 | Grammar pipeline | severity: Low |
    bar-grammar-check validates all 5 consumer copies including web/static.
    Concern from ADR-0151 is already mitigated. ADR update pending in loop-3.

next_work:
  - Behaviour T-3: Update ADR-0151 to note grammar pipeline concern is already
    resolved by bar-grammar-check (no code change needed). Close work-log.
```

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
