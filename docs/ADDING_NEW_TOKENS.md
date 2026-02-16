# How to Add New Tokens to the Grammar Catalog

This guide documents the end-to-end process for adding new tokens (static prompts, method values, persona presets, etc.) to the talon-ai-tools grammar catalog.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Process](#step-by-step-process)
4. [Validation](#validation)
5. [Troubleshooting](#troubleshooting)
6. [Example: Adding the "improve" Method](#example-adding-the-improve-method)

## Overview

The grammar catalog system has multiple layers:
- **Python source**: `lib/axisConfig.py` - canonical source of truth
- **Generated artifacts**: Talon lists, README docs, JSON catalogs
- **Go CLI**: Embedded grammar JSON for bar CLI
- **Validation**: Test suites ensure catalog consistency

Adding a token requires updating the Python source, regenerating artifacts, and validating the changes.

## Prerequisites

- Python virtual environment set up (`.venv/`)
- Go toolchain for bar CLI (if updating embedded grammar)
- Make available for running Makefile targets

## Before You Begin: Token Design Checklist

Before adding a new token, verify:

### 1. Distinctiveness
- [ ] Does this token produce a **different effect** from existing tokens in this axis?
- [ ] Can a user distinguish the output from similar tokens?
- [ ] Does the description avoid overlap with other axes (e.g., no "over time" in method if scope handles time)?

### 2. Axis Purity
- [ ] Does this token belong in the axis I'm adding it to?
- [ ] Would it make more sense in a different axis? (e.g., "tight" as completeness, not form)

### 3. Compatibility
- [ ] What happens when combined with each other axis? (document the behavior, don't just forbid)
- [ ] Does it work with the primary task types (static prompts)?
- [ ] Are there known conflicts that need documentation in the description?

### 4. Precedence Awareness
- [ ] If this token conflicts with another axis, which wins? (see reference key precedence)
- [ ] Channel > Form > Task > Intent > Persona — does this token override or get overridden?

### 5. Description Quality
- [ ] Description starts with "The response..." and describes the effect on output
- [ ] Description includes "Works best with..." or "Incompatible with..." clauses if needed
- [ ] Description avoids anchoring to other axes' territory

### 6. Meta-Evaluation
- [ ] Can bar-autopilot skills explain when to use this token?
- [ ] Would `bar help llm` provide adequate guidance for this token?

> **Why this matters:** Most issues discovered in shuffle/task refinement cycles (ADR-0085/0113) could have been caught at token creation if these questions had been asked.

## Step-by-Step Process

### 1. Add Token to Python Configuration

Edit `lib/axisConfig.py` and add your token to the appropriate axis dictionary.

**For method axis:**
```python
# lib/axisConfig.py, inside AXIS_KEY_TO_VALUE['method']

'your_token_name': 'The response [clear description of what this method does].',
```

**Important:** Add the token in **alphabetical order** within its axis.

**Example:**
```python
'method': {
    # ... other tokens ...
    'how': 'The response concentrates on mechanical explanation...',
    'improve': 'The response takes existing work and enhances it along relevant dimensions...',
    'indirect': 'The response begins with brief background...',
    # ... other tokens ...
}
```

### 2. Regenerate Python Artifacts

Run the axis regeneration target to update all Python-based artifacts:

```bash
make axis-regenerate
```

This generates:
- `tmp/axisConfig.generated.py` - Formatted Python config
- `tmp/readme-axis-tokens.md` - Markdown token list
- `tmp/axisCatalog.json` - JSON catalog (DO NOT use for bar CLI)
- `tmp/readme-axis-cheatsheet.md` - Quick reference
- `tmp/static-prompt-docs.md` - Static prompt documentation

### 3. Apply Generated Config

Copy the generated Python config back to source:

```bash
make axis-regenerate-apply
```

This ensures `lib/axisConfig.py` has consistent formatting.

### 4. Update Embedded Grammar for bar CLI

**CRITICAL:** Use `prompts.export`, NOT `axisCatalog.json`:

```bash
python3 -m prompts.export \
  --output build/prompt-grammar.json \
  --embed-path internal/barcli/embed/prompt-grammar.json
```

This generates the correct grammar structure:
```json
{
  "axes": {
    "definitions": {      // Note: nested "definitions" key!
      "method": {"improve": "...", ...},
      ...
    },
    "list_tokens": {}     // Note: "list_tokens" not "axis_list_tokens"
  },
  ...
}
```

**Why this matters:** `axisCatalog.json` has a flat structure that doesn't match the Go struct tags. Only `prompts.export` produces the correct nested structure.

### 5. Rebuild bar CLI

```bash
cd cmd/bar
go build -o ../../bar .
cd ../..
```

### 6. Update GPT/readme.md

**IMPORTANT:** Manually add the token to the axis line in `GPT/readme.md`:

```bash
# Find the axis line (around line 248 for method axis)
# Example for method axis:
# Method (`methodModifier`): `adversarial`, `analysis`, ..., `how`, `improve`, `indirect`, ...
```

**Location:** `GPT/readme.md:246-250` (varies by axis)

**Important:** Add your token in **alphabetical order** between the existing tokens.

**Why manual?** The README has a specific format that the automated generators respect but don't update directly. This ensures the README stays in sync with the catalog.

### 7. Run Validation

```bash
# Run all guardrails (includes axis validation + tests)
make ci-guardrails
```

This validates:
- Axis catalog structure
- Test coverage
- Documentation consistency (including README)
- Overlay components

**If this fails with "Mismatch for README axis line":**
- You forgot to update `GPT/readme.md` (step 6 above)
- The token isn't in alphabetical order in the README

### 8. Test with Shuffle

Validate the token appears and works correctly:

```bash
# Search for your token in random prompts
for seed in {1..100}; do
  result=$(./bar shuffle --seed $seed --include method --fill 0.9 2>&1)
  if echo "$result" | grep -q "Method (your_token)"; then
    echo "Found at seed $seed"
    ./bar shuffle --seed $seed --include method --fill 0.9
    break
  fi
done
```

### 9. Manual Testing

Test the token in actual usage:

```bash
# Build command with key=value syntax
./bar build method=improve --prompt "Optimize this function"

# Build command with positional syntax (method is position 4)
./bar build todo full focus improve
```

## Validation

After adding a token, verify:

- ✅ Token appears in `lib/axisConfig.py` in alphabetical order
- ✅ `make axis-regenerate-apply` runs without changes (idempotent)
- ✅ Token appears in `GPT/readme.md` axis line in alphabetical order
- ✅ `make ci-guardrails` passes all tests
- ✅ Token appears in `internal/barcli/embed/prompt-grammar.json`
- ✅ bar CLI shuffle can generate prompts using the token
- ✅ bar CLI build accepts the token in both syntaxes

## Troubleshooting

### Token doesn't appear in bar shuffle output

**Symptom:** Shuffle generates prompts but never includes your new token.

**Causes:**
1. Grammar JSON not regenerated with `prompts.export`
2. bar CLI not rebuilt after grammar update
3. Wrong grammar structure (used `axisCatalog.json` instead)

**Fix:**
```bash
# Regenerate with correct tool
python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json

# Rebuild
cd cmd/bar && go build -o ../../bar . && cd ../..

# Verify token is in grammar
python3 -c "import json; data=json.load(open('internal/barcli/embed/prompt-grammar.json')); print('improve' in data['axes']['definitions']['method'])"
# Should print: True
```

### bar build rejects the token

**Symptom:** `./bar build method=improve` returns "unrecognized token for method"

**Cause:** Grammar JSON structure mismatch.

**Fix:** Use `prompts.export` as shown above, not `axisCatalog.json`.

### make axis-guardrails fails with "Mismatch for README axis line"

**Symptom:** Test failure in `_tests/test_readme_axis_lists.py`:
```
AssertionError: Mismatch for README axis line 'Method (`methodModifier`)'
```

**Cause:** `GPT/readme.md` not updated with new token.

**Fix:**
```bash
# Edit GPT/readme.md and add your token in alphabetical order
# For method axis, find the line starting with:
# Method (`methodModifier`): `adversarial`, `analysis`, ...

# Add your token in alphabetical order, e.g.:
# ..., `how`, `improve`, `indirect`, ...
```

### make axis-guardrails fails with regenerate apply issue

**Symptom:** Test failures in `_tests/test_make_axis_regenerate_apply.py`

**Cause:** `lib/axisConfig.py` not in sync with generated output.

**Fix:**
```bash
make axis-regenerate-apply
```

### Shuffle only shows constraints sometimes

**Symptom:** Shuffle generates prompts without method/scope/form tokens even with `--fill 1.0`

**Cause:** This is expected behavior - shuffle uses probabilistic selection.

**Fix:** Use `--include method` to force method token selection:
```bash
./bar shuffle --seed 42 --include method --fill 0.9
```

## Example: Adding the "improve" Method

This example shows the complete workflow for adding the `improve` method token (ADR 0087).

### 1. Add to axisConfig.py

```python
# lib/axisConfig.py:249-252
'improve': 'The response takes existing work and enhances it along relevant '
           'dimensions—such as performance, readability, maintainability, '
           'correctness, or robustness—identifying specific improvements and '
           'applying them while preserving core functionality.',
```

### 2. Regenerate artifacts

```bash
make axis-regenerate
make axis-regenerate-apply
```

### 3. Export grammar for bar CLI

```bash
python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
# Output: Wrote prompt grammar to build/prompt-grammar.json (mirrored to internal/barcli/embed/prompt-grammar.json)
```

### 4. Rebuild bar

```bash
cd cmd/bar && go build -o ../../bar . && cd ../..
```

### 5. Update GPT/readme.md

```bash
# Edit GPT/readme.md line 248 (method axis)
# Change:
# Method (`methodModifier`): `adversarial`, `analysis`, ..., `how`, `indirect`, ...
# To:
# Method (`methodModifier`): `adversarial`, `analysis`, ..., `how`, `improve`, `indirect`, ...
```

### 6. Validate

```bash
# Run guardrails
make ci-guardrails
# Output: All tests pass (100/100)
```

### 7. Find in shuffle

```bash
for seed in {1..200}; do
  if ./bar shuffle --seed $seed --include method --fill 0.9 2>&1 | grep -q "Method (improve)"; then
    echo "Found at seed $seed"
    break
  fi
done
# Output: Found at seed 9

# View full prompt
./bar shuffle --seed 9 --include method --fill 0.9
# Output shows: Method (improve): The response takes existing work and enhances it...
```

### 8. Test build command

```bash
./bar build method=improve form=code --prompt "Refactor this class"
# Should generate a prompt with method=improve constraint
```

## Common Patterns

### Adding a Static Prompt

Edit `lib/promptConfig.py`:
```python
STATIC_PROMPTS = {
    # ... existing prompts ...
    "your_prompt": "The response [what it does].",
}
```

Then follow steps 2-6 above.

### Adding a Persona Preset

Edit `lib/personaConfig.py`:
```python
PERSONA_PRESETS = [
    PersonaPreset(
        key="your_preset_key",
        label="Your Preset Label",
        voice="as professional",
        audience="to team",
        tone="directly",
    ),
    # ... other presets ...
]
```

Add implicit intent mapping if needed:
```python
PERSONA_PRESET_IMPLICIT_INTENTS = {
    # ... existing mappings ...
    "your_preset_key": "inform",  # or teach, plan, etc.
}
```

Then follow steps 2-6 above.

## Files Modified

When adding a token, these files are typically modified:

**Source (manual edits):**
- `lib/axisConfig.py` - Axis token definitions
- `lib/promptConfig.py` - Static prompt definitions
- `lib/personaConfig.py` - Persona presets and axes
- `GPT/readme.md` - Axis token lists (must be manually updated)

**Generated (automated):**
- `tmp/axisConfig.generated.py` - Formatted Python config
- `tmp/axisCatalog.json` - JSON catalog (not used by bar CLI)
- `tmp/readme-axis-*.md` - Documentation
- `build/prompt-grammar.json` - Grammar for bar CLI
- `internal/barcli/embed/prompt-grammar.json` - Embedded grammar
- `lib/axisConfig.py` - Updated by `make axis-regenerate-apply`

**Binary:**
- `bar` - Rebuilt Go CLI with new embedded grammar

## Documentation

After adding a token, consider:

1. **ADR Documentation** - Create an ADR if the token represents a significant decision
2. **Work Log** - Document the implementation in `docs/adr/XXXX-work-log.md`
3. **Help Surfaces** - Tokens automatically appear in bar CLI help and Talon voice commands
4. **README Updates** - Run `make axis-guardrails` to auto-update README sections

## References

- ADR 0087: Add "improve" method (example implementation)
- ADR 0085: Shuffle-driven catalog refinement (validation process)
- ADR 0086: Catalog refinements from first shuffle cycle (precedent)
- `prompts/export.py`: Grammar export module
- `scripts/tools/generate_axis_config.py`: Axis config generator
