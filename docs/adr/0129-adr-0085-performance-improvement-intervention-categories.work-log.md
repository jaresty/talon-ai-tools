# ADR 0129 Work Log

## Loop History

- [Loop 1: Identify high-overlap token pairs in method axis](#loop-1-identify-high-overlap-token-pairs-in-method-axis)
- [Loop 2: Add differentiation guidance to AXIS_KEY_TO_GUIDANCE](#loop-2-add-differentiation-guidance-to-axis_key_to_guidance)
- [Loop 3: Validate bar shuffle with updated guidance](#loop-3-validate-bar-shuffle-with-updated-guidance)

---

## Loop 1: Identify high-overlap token pairs in method axis

**Date**: 2026-02-15

**Focus**: Phase 1 - Identify specific tokens requiring differentiation guidance

**Active Constraint**: Need concrete list of which tokens have overlapping descriptions

**Validation Targets**: None (documentation/analysis loop)

**Evidence**: N/A

**Rollback Plan**: N/A

**Delta Summary**: Initial work-log creation and analysis. Identified token pairs: abduce/deduce/induce, explore/branch, meld/cluster, resilience/robust, systemic/analysis

**Loops Remaining Forecast**: 2-3 loops for Phase 1 implementation

**Residual Constraints**: None

**Next Work**: 
- Add differentiation guidance to AXIS_KEY_TO_GUIDANCE in lib/axisConfig.py (NOT VALUE - that's prompt content)
- Regenerate grammar files

---

## Loop 2: Add differentiation guidance to AXIS_KEY_TO_GUIDANCE

**Date**: 2026-02-15

**Focus**: Add "Distinct from X" guidance to method tokens in AXIS_KEY_TO_GUIDANCE

**Active Constraint**: None (completed)

**Validation Targets**: 
- `make bar-grammar-update` - regenerate grammar files
- `python3 -m pytest _tests/test_axis_regen_all.py` - verify no drift

**Evidence**:
- green | 2026-02-15T... | exit 0 | make bar-grammar-update
- green | 2026-02-15T... | exit 0 | pytest test_axis_regen_all.py

**Rollback Plan**: git restore lib/axisConfig.py

**Delta Summary**: Added 20 lines to AXIS_KEY_TO_GUIDANCE["method"] in lib/axisConfig.py

**Loops Remaining Forecast**: 1 loop for validation

**Residual Constraints**: None

**Next Work**: 
- Validate bar shuffle works with updated guidance
- Commit grammar regeneration

---

## Loop 3: Validate bar shuffle with updated guidance

**Date**: 2026-02-15

**Focus**: Verify bar shuffle works and guidance shows in bar help llm

**Active Constraint**: None (completed)

**Validation Targets**: 
- `bar shuffle --seed 1` - verify shuffle works
- `bar help llm` - verify guidance displays

**Evidence**:
- green | 2026-02-15T... | exit 0 | bar shuffle --seed 1
- green | 2026-02-15T... | exit 0 | bar help llm | grep -E "abduce|branch|explore"

**Rollback Plan**: git restore on grammar files

**Delta Summary**: Regenerated grammar files (build/prompt-grammar.json, cmd/bar/testdata/grammar.json, internal/barcli/embed/prompt-grammar.json)

**Loops Remaining Forecast**: 0 for Phase 1

**Residual Constraints**: None

**Next Work**: 
- Phase 2: Skill heuristic updates (bar-autopilot, bar-suggest, bar-workflow)
- Or evaluate impact of Phase 1 changes first
