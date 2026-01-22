# ADR 0088: Adopt Universal Task Taxonomy - Work Log

## Status

**ADR Status**: Proposed
**Work Status**: Planning

---

## Implementation Phases

### Phase 1: Add Universal Tasks and New Axis Values

- [ ] Update lib/staticPromptConfig.py
  - [ ] Add 10 universal task definitions (make, fix, pull, sort, diff, show, probe, pick, plan, check)
  - [ ] Remove all 46 specialized tasks
- [ ] Update lib/axisConfig.py
  - [ ] Add 28 new scope values (no hyphens: jobs not jtbd, operations not or-concepts, pain not pain-points, etc.)
  - [ ] Add 5 new method values (depends, independent, cochange, split, merge)
  - [ ] Add 2 new form values (questions, wardley)
  - [ ] Remove method=probe (conflicts with task=probe)
- [ ] Regenerate artifacts
  - [ ] make axis-regenerate
  - [ ] make axis-regenerate-apply
  - [ ] python3 -m prompts.export (with correct flags)
- [ ] Update documentation
  - [ ] Update GPT/readme.md with new tokens
  - [ ] Create migration guide docs/MIGRATION-0088.md
  - [ ] Update examples to use universal tasks
- [ ] Rebuild bar CLI
  - [ ] cd cmd/bar && go build

### Phase 2: Testing and Validation

- [ ] Shuffle validation for all universal tasks
- [ ] Shuffle validation for new scope values
- [ ] Run ci-guardrails
- [ ] Manual testing of equivalences
- [ ] Update test coverage
  - [ ] Update _tests/test_talon_settings_model_prompt.py
  - [ ] Add tests for new scope/method/form values
  - [ ] Verify migration mappings in tests

### Phase 3: Documentation and Migration Support

- [ ] Create migration guide (docs/MIGRATION-0088.md)
  - [ ] Document all 45 task mappings
  - [ ] Provide examples for common use cases
  - [ ] Explain universal task model
- [ ] Update README examples
  - [ ] Replace specialized tasks with universal equivalents
  - [ ] Show task + scope + method combinations
  - [ ] Add "Common Patterns" section
- [ ] Consider deprecation warnings (optional)

---

## Progress Notes

### 2026-01-21: ADR Created and Revised

**Work Completed:**
- Created comprehensive ADR 0088 documenting universal task taxonomy
- Analyzed all 46 current tasks and mapped to 10 universal types
- Identified 36 new axis values needed (28 scope, 5 method, 2 form, 1 method retired)
- Created detailed migration mapping table
- Documented rationale and consequences

**Revisions based on user feedback:**
- Made all universal task tokens single-syllable for voice optimization:
  - generate → make, transform → fix, extract → pull, classify → sort, compare → diff
  - explain → show, analyze → probe, recommend → pick, verify → check, plan → plan
- Removed hyphenated tokens: or-concepts → operations, jtbd → jobs, pain-points → pain, etc.
- Removed duplicate tokens across axes: removed scope=cochange (kept only method=cochange)
- Retired method=probe to avoid conflict with task=probe
- Updated all migration examples and validation scripts

**Next Steps:**
- Await user approval of revised ADR
- Begin Phase 1 implementation if approved

---

## Key Decisions

### Universal Task Types (10 - all single syllable)

1. make - Success = something new exists
2. fix - Success = same content, different form
3. pull - Success = subset identified correctly
4. sort - Success = correct placement into categories
5. diff - Success = meaningful relationships surfaced
6. show - Success = understanding enabled
7. probe - Success = structure or insight revealed
8. pick - Success = justified choice made
9. plan - Success = actionable sequence defined
10. check - Success = correctness assessed

### Tasks to Retire (46)

All 46 specialized tasks will be retired and replaced with universal task + axis combinations.

### Method to Retire (1)

- method=probe - Now conflicts with task=probe, so retiring the method

---

## Migration Examples

### High-Value Patterns

```bash
# Jobs To Be Done analysis
# Old: bar build jobs
# New: bar build probe scope=jobs method=analysis form=bullets

# Wardley mapping
# Old: bar build wardley
# New: bar build make form=wardley scope=strategy

# Connascence analysis
# Old: bar build jim
# New: bar build probe scope=connascence method=rigor

# Extract assumptions
# Old: bar build assumption
# New: bar build pull scope=assumptions

# Identify risks
# Old: bar build risky
# New: bar build pull scope=risks method=filter

# Explain rationale
# Old: bar build why
# New: bar build show scope=rationale
```

---

## Open Questions

1. **Should "fix" be retired?**
   - Current: Keep as general action task
   - Alternative: Retire in favor of generate/transform
   - Decision: Keep for now, revisit if usage overlaps heavily

2. **Method vs scope for cochange?**
   - Current: Include both (method=cochange for how, scope=cochange for what)
   - Alternative: Pick one
   - Decision: Include both initially, refine based on usage

3. **Form=wardley vs form=diagram + scope=strategy?**
   - Current: Include form=wardley for specificity
   - Alternative: Use generic form=diagram
   - Decision: Include form=wardley to preserve Wardley-specific structure

**Resolution**: Implement as proposed, gather usage data via ADR 0085 shuffle cycle, refine based on evidence.

---

## Risks and Mitigations

### Risk: Migration friction for existing users

**Mitigation:**
- Comprehensive migration guide with 1:1 mappings
- Examples for all common patterns
- Clear communication about rationale
- Consider deprecation warnings for transition period

### Risk: Multi-token expressions more verbose

**Mitigation:**
- Emphasize clarity benefit (extract + scope=assumptions vs assumption)
- Document common patterns in README
- Show composition reveals structure

### Risk: Some specialized nuance lost

**Mitigation:**
- Scope values preserve specificity (scope=connascence, scope=jtbd, etc.)
- Combination is more honest about operation (analyze connascence vs "jim")
- Common patterns documented for discoverability

---

## Validation Checklist

- [ ] All 10 universal tasks defined and documented (all single-syllable)
- [ ] All 36 new axis values added (28 scope, 5 method, 2 form, 1 method retired)
- [ ] All 46 specialized tasks removed from catalog
- [ ] method=probe retired (conflicts with task=probe)
- [ ] No hyphenated tokens in new axis values
- [ ] No tokens duplicated across multiple axes
- [ ] Migration guide covers all 46 retired tasks
- [ ] README updated with universal task examples
- [ ] All tests pass (make ci-guardrails)
- [ ] Shuffle generates valid combinations for all universal tasks
- [ ] Manual equivalence testing confirms migrations work
- [ ] User testing: New users understand universal tasks

---

## References

- ADR document: docs/adr/0088-adopt-universal-task-taxonomy.md
- Analysis document: tmp/task-taxonomy-rehoming.md
- Source material: Framing the idea.md
- Related: ADR 0083 (task defines success), ADR 0086 (retired infer), ADR 0087 (token addition pattern)
