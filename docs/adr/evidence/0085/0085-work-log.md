# ADR 0085 Work Log

**ADR:** 0085-shuffle-driven-catalog-refinement  
**Helper:** helper:v20251223.1

---

## Loop 1: Precedence Rules in Reference Key (P1) ✅

**Date:** 2026-02-15  
**Focus:** Add precedence rules to reference key (prompts work without skills)

### Changes Made

1. **Reference Key** (in both Go and Python versions):
   - Added precedence rules to `referenceKeyText` / `PROMPT_REFERENCE_KEY`
   - This is the canonical source - prompts work correctly without skills

2. **Help documentation** (`internal/barcli/help_llm.go`):
   - Simplified to "Precedence Examples" - references reference key
   - Kept practical examples (helpful for learning)
   - Removed redundant precedence table (now in reference key)

3. **Token guidance** (`internal/barcli/embed/prompt-grammar.json`):
   - Added svg token guidance (dynamic, read from grammar)
   - This is the per-token guidance that supplements general rules

### Philosophy

- **Reference Key**: Canonical precedence rules (used by prompts directly)
- **Help**: Reference lookup + practical examples (not redundant)
- **Token Guidance**: Per-token specifics (dynamic from grammar)

### Validation

Precedence rules now appear in:
- Reference key (used by prompts directly - works without skills)
- bar help llm (reference documentation)
- Individual token guidance (dynamic from grammar)

### Next Steps

- Rebuild bar to see changes in CLI output
- Validate svg guidance appears in `bar help llm`
