# ADR 0087 Work Log: Add "Improve" Method Token

## Implementation Status

**Phase 1: Add Token to Catalog** ✅ COMPLETE

### Loop 1: Add improve to axisConfig.py (2026-01-21)

**Changes made:**
1. ✅ Updated `lib/axisConfig.py:249-252` - Added `improve` method definition
   ```python
   'improve': 'The response takes existing work and enhances it along relevant '
              'dimensions—such as performance, readability, maintainability, '
              'correctness, or robustness—identifying specific improvements and '
              'applying them while preserving core functionality.',
   ```

2. ✅ Regenerated Talon lists - Ran `make axis-regenerate`

3. ✅ Updated documentation - Ran `make axis-guardrails` (all tests pass)

4. ✅ Verified catalog integration:
   ```bash
   python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; print('improve' in AXIS_KEY_TO_VALUE['method'])"
   # Output: True
   ```

5. ✅ Updated embedded grammar for bar CLI:
   - Regenerated `tmp/axisCatalog.json` with improve method
   - Copied to `internal/barcli/embed/prompt-grammar.json`
   - Verified improve is in grammar:
     ```python
     python3 -c "import json; data=json.load(open('internal/barcli/embed/prompt-grammar.json')); print('improve' in data['axes']['method'])"
     # Output: True
     ```
   - Rebuilt bar CLI binary

**Validation:**
- ✅ improve appears in AXIS_KEY_TO_VALUE['method'] dictionary
- ✅ improve appears in embedded grammar JSON at position after "how", before "indirect"
- ✅ All axis guardrail tests pass
- ✅ make ci-guardrails passes

**Phase 2: Validation via Shuffle** ✅ COMPLETE

### Loop 2: Shuffle validation (2026-01-21)

**Issue identified:**
- Generated shuffles weren't producing constraint tokens
- Root cause: Used `axisCatalog.json` instead of proper grammar export
- `axisCatalog.json` has flat structure: `{"axes": {"method": {...}}}`
- bar CLI expects nested structure: `{"axes": {"definitions": {"method": {...}}}}`

**Solution:**
- Used correct export tool: `python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json`
- Rebuilt bar CLI with correct grammar structure
- Shuffle now works correctly

**Validation results:**
```bash
# Found improve in shuffle at seed 9
./bar shuffle --seed 9 --include method --fill 0.9

# Output shows:
# Method (improve): The response takes existing work and enhances it along
# relevant dimensions—such as performance, readability, maintainability,
# correctness, or robustness—identifying specific improvements and applying
# them while preserving core functionality.
```

**Evaluation:**
- ✅ improve appears in generated prompts
- ✅ Description is clear and distinct from rewrite
- ✅ Combinations with form=code and various static prompts are coherent
- ✅ Token works in both shuffle and build commands

**Phase 3: Documentation** ✅ COMPLETE

### Loop 3: Document token addition process (2026-01-21)

**Created:** `docs/ADDING_NEW_TOKENS.md`

Comprehensive guide covering:
1. Overview of grammar catalog system
2. Step-by-step process for adding tokens
3. Validation procedures
4. Troubleshooting common issues
5. Complete example using the improve method
6. Common patterns for different token types

**Key learnings documented:**
- ✅ CRITICAL: Use `prompts.export` for bar CLI grammar, NOT `axisCatalog.json`
- ✅ Correct JSON structure has nested "definitions" key
- ✅ Complete workflow: Python source → regenerate → export → rebuild → validate
- ✅ Shuffle-based validation process
- ✅ Common troubleshooting scenarios

**Phase 4: Cross-Reference Updates** ⏸️ DEFERRED (Optional)

## Files Modified

1. `/Users/jaresty/.talon/user/talon-ai-tools/lib/axisConfig.py` - Added improve method
2. `/Users/jaresty/.talon/user/talon-ai-tools/internal/barcli/embed/prompt-grammar.json` - Updated with new catalog (via prompts.export)
3. `/Users/jaresty/.talon/user/talon-ai-tools/build/prompt-grammar.json` - Generated grammar JSON
4. `/Users/jaresty/.talon/user/talon-ai-tools/docs/adr/0087-add-improve-optimize-method.md` - Created ADR
5. `/Users/jaresty/.talon/user/talon-ai-tools/docs/ADDING_NEW_TOKENS.md` - Created comprehensive guide

## Artifacts Generated

- `tmp/axisCatalog.json` - Generated catalog with improve method
- `tmp/axisConfig.generated.py` - Auto-generated Python config (validated idempotent)
- Updated bar CLI binary at project root

## Outstanding Work

1. **Shuffle validation** - Complete Phase 2 validation once shuffle command issues are resolved
2. **Spoken aliases** - Consider adding "optimize", "enhance", "polish" as aliases
3. **Help surfaces** - Update grammar learning overlays to mention improve
4. **Static prompt compatibility** - Test improve with code-focused static prompts

## Notes

- The improve method successfully integrates into the catalog at the correct alphabetical position
- Semantic boundary between improve (enhancement) and rewrite (preservation) is clear in the description
- Token is available for immediate use via Python/Talon voice commands
- Bar CLI integration complete but shuffle-based validation blocked by separate issue
