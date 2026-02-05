# ADR 0102: Work Log

## Status

Implemented

## Implementation Summary

Single-loop implementation: validation added, help updated, tests verified.

---

## Loop 1: Implement Validation and Update Documentation

**Goal**: Add static prompt requirement validation to Go CLI

**Date**: 2026-02-05

### Changes Made

1. **`internal/barcli/build.go`** (lines 679-703)
   - Added validation in `finalise()` to check if `state.static == ""`
   - Returns `errorMissingStatic` error with helpful message
   - Lists all available static prompts with descriptions from grammar
   - Includes example usage in error message

2. **`internal/barcli/app.go`** (line 100)
   - Updated help text from `(0..1 tokens, default: open-ended)` to `(REQUIRED: 1 token)`

3. **`lib/promptGrammar.py`** (lines 107-111)
   - Updated `_default_static_prompt()` docstring
   - Clarified that static prompt is now required by Go CLI
   - Kept return value as `""` for grammar schema compatibility

### Testing

```bash
# Verified validation works
go run ./cmd/bar build --prompt "test"
# Returns error listing all static prompts

# Verified success case
go run ./cmd/bar build make --prompt "test"
# Succeeds and generates prompt

# Verified all tests pass
go test ./internal/barcli/...
go test ./...
# All tests pass
```

### Error Message Format

```
error: static prompt (task) is required

Available static prompts:
  check - The response evaluates the subject against a condition...
  diff - The response compares two or more subjects...
  fix - The response changes the form or presentation...
  make - The response creates new content...
  pick - The response chooses one or more options...
  plan - The response proposes steps, structure, or strategy...
  probe - The response analyzes the subject to surface structure...
  pull - The response selects or extracts a subset...
  show - The response explains or describes the subject...
  sim - The response plays out a concrete or hypothetical scenario...
  sort - The response arranges items into categories...

Example: bar build make full code <prompt>
```

### Validation Results

✅ Implementation complete
✅ Error message clear and helpful
✅ All tests pass
✅ Help text updated
✅ Documentation updated

---

## Completion

**Status**: Implemented
**Date**: 2026-02-05
**Total Loops**: 1

All requirements met:
- Validation enforces static prompt requirement
- Error message provides clear guidance
- Help text reflects new requirement
- Tests continue to pass
- Breaking change documented in ADR
