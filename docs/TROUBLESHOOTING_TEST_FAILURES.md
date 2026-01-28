# Troubleshooting Test Failures After Token Changes

## Overview

When axis tokens are reorganized (e.g., moving tokens between axes, removing obsolete tokens, renaming tokens), tests often break because they reference the old token vocabulary. This guide explains how to systematically identify and fix these issues.

## Quick Diagnosis

### Step 1: Establish Baseline

First, identify the last known good state:

```bash
# Find a commit where tests were passing
git log --oneline --all --grep="test" | head -20

# Or check a specific recent commit
git checkout <commit-hash>
python3 -m unittest discover -s _tests 2>&1 | grep -E "^(Ran|OK|FAILED)"
```

**Example from this session:**
- Commit `1cb1399`: 1 failure + 7 errors (baseline)
- Commit `d233587` (ADR 0091 Phase 1): 58 failures + 46 errors (introduced issues)
- Current HEAD: 58 failures + 14 errors (partially fixed)

### Step 2: Identify What Changed

```bash
# Compare token vocabulary between commits
git show <old-commit>:lib/axisConfig.py > /tmp/old_axis.py
git show <new-commit>:lib/axisConfig.py > /tmp/new_axis.py
diff /tmp/old_axis.py /tmp/new_axis.py | grep "^[<>]" | head -50
```

Or use Python to compare:

```python
# At old commit
python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; \
  print('OLD scope:', sorted(AXIS_KEY_TO_VALUE['scope'].keys()))"

# At new commit
python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; \
  print('NEW scope:', sorted(AXIS_KEY_TO_VALUE['scope'].keys()))"
```

### Step 3: Categorize Failures

Run tests and categorize errors:

```bash
python3 -m unittest discover -s _tests 2>&1 > /tmp/test_output.txt

# Count errors vs failures
grep "^ERROR:" /tmp/test_output.txt | wc -l
grep "^FAIL:" /tmp/test_output.txt | wc -l

# See which test files have issues
grep "^ERROR:\|^FAIL:" /tmp/test_output.txt | \
  sed 's/.*(\(test_[^.]*\)\..*/\1/' | sort | uniq -c | sort -rn
```

Common categories:
- **Import/loader errors**: Pre-existing environmental issues (ignore)
- **Token reference errors**: Tests referencing removed/renamed tokens
- **Preset errors**: Tests expecting removed persona/intent presets
- **Assertion errors**: Tests with hardcoded expectations about token sets

## Common Fix Patterns

### Pattern 1: Removed Tokens in Test Data

**Symptom**: Tests fail with "token not in AXIS_KEY_TO_VALUE"

**Example**:
```python
# BROKEN: 'relations' no longer exists
GPTState.last_scope = "relations"

# FIXED: Use current token
GPTState.last_scope = "struct"
```

**Fix approach**:
```bash
# Find all references to obsolete token
grep -r "relations" _tests/

# Replace with current token
sed -i '' 's/ relations / struct /g' _tests/test_*.py
```

### Pattern 2: Removed Tokens in Expected Results

**Symptom**: Assertions fail because test expects old tokens

**Example**:
```python
# BROKEN: Test expects 'decide' intent
self.assertTrue("decide" in intent_keys)

# FIXED: Update to current intents
self.assertTrue({"teach", "inform", "announce"} <= intent_keys)
```

**Fix approach**:
1. Check current token set:
   ```python
   python3 -c "from lib.personaConfig import PERSONA_KEY_TO_VALUE; \
     print(sorted(PERSONA_KEY_TO_VALUE['intent'].keys()))"
   ```
2. Update test expectations to match current set

### Pattern 3: Tokens Moved Between Axes

**Symptom**: Test references form token that moved to channel (or vice versa)

**Example**:
```python
# BROKEN: 'adr' moved from form to channel
formModifier_list=["adr", "table"]

# FIXED: Use current form tokens
formModifier_list=["bullets", "table"]
```

**Fix approach**:
1. Check which axis currently contains the token:
   ```bash
   grep -A 3 "'adr':" lib/axisConfig.py
   ```
2. Update test to use token from correct axis

### Pattern 4: Recipe String Index Assumptions

**Symptom**: `IndexError: list index out of range` when accessing recipe parts

**Example**:
```python
# BROKEN: Assumes recipe always has 6 parts
recipe_parts = recipe.split("·")
channel_part = recipe_parts[5]  # May not exist!

# FIXED: Check presence instead of index
self.assertIn("slack", recipe_parts)
```

**Why this fails**: Recipe parts are filtered (`if part`), so empty axes are omitted and indices shift.

### Pattern 5: Removed Presets

**Symptom**: Tests expecting persona/intent presets that no longer exist

**Example**:
```python
# BROKEN: 'evaluate' preset removed
IntentPreset(key="evaluate", intent="evaluate")

# FIXED: Remove the preset entirely (if intent also removed)
# OR map to valid intent (if preset should stay):
IntentPreset(key="evaluate", intent="inform")
```

## Systematic Fix Workflow

### Step 1: Fix Import/Loader Errors (Skip)

These are usually environmental and pre-existing. Confirm with baseline check.

### Step 2: Fix Token Reference Errors

```bash
# Find tests using obsolete tokens
python3 -m unittest discover -s _tests 2>&1 | grep "AttributeError\|KeyError" | head -20

# For each obsolete token, find and replace
grep -rn "obsolete_token" _tests/
sed -i '' 's/obsolete_token/current_token/g' _tests/test_affected.py
```

### Step 3: Fix Preset Errors

```bash
# Find preset-related failures
python3 -m unittest discover -s _tests 2>&1 | grep "preset" -i | head -20

# Check current presets
python3 -c "from lib.personaConfig import INTENT_PRESETS; \
  print([p.key for p in INTENT_PRESETS])"

# Update tests to match
```

### Step 4: Verify Fixes

```bash
# Run specific test file
python3 -m unittest _tests.test_persona_presets -v

# Run full suite
python3 -m unittest discover -s _tests 2>&1 | grep -E "^(Ran|OK|FAILED)"
```

### Step 5: Document and Commit

```bash
git add _tests/
git commit -m "Fix tests after token reorganization

Updated test expectations to match current token vocabulary:
- Replaced 'obsolete_token' with 'current_token'
- Updated expected preset lists
- Fixed recipe index assumptions

Refs: <ADR or commit that changed tokens>
"
```

## Prevention

### When Removing/Renaming Tokens

1. **Search for test usage first**:
   ```bash
   grep -r "token_to_remove" _tests/
   ```

2. **Run tests immediately after token changes**:
   ```bash
   python3 -m unittest discover -s _tests
   ```

3. **Update tests in the same commit** that changes tokens

4. **Document token changes** in commit message:
   ```
   Remove 'obsolete' token from scope axis

   - Removed from AXIS_KEY_TO_VALUE['scope']
   - Updated test_*.py to use 'current' instead
   - Affects tests: test_foo, test_bar
   ```

### When Moving Tokens Between Axes

1. **Update both test data and assertions**:
   - Test data (input): `formModifier="adr"` → `channelModifier="adr"`
   - Assertions (output): `GPTState.last_form` → `GPTState.last_channel`

2. **Search for both form and meaning**:
   ```bash
   grep -r "adr" _tests/  # Find the token
   grep -r "formModifier.*adr\|adr.*formModifier" _tests/  # Find usage
   ```

## Real-World Example: ADR 0092 Token Changes

**What changed**: `plain` moved from form to channel axis

**Impact**: 32 test failures introduced

**Fixes needed**:
1. Replace `formModifier="plain"` → `formModifier="bullets"` (or remove)
2. Update recipe expectations from `["plain"]` in form position
3. Fix tests that assumed both `plain` form and channel could coexist

**Commits**:
- `d2d689c`: Made the change (introduced failures)
- `aa31a53`: Fixed immediate test failures
- `91004fb`: Fixed additional obsolete token references

## Tools and Commands Reference

### Check Current Token Vocabulary

```bash
# All axes
python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; \
  for axis in sorted(AXIS_KEY_TO_VALUE.keys()): \
    print(f'{axis}: {len(AXIS_KEY_TO_VALUE[axis])} tokens')"

# Specific axis
python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; \
  print('\\n'.join(sorted(AXIS_KEY_TO_VALUE['form'].keys())))"

# Persona/intent
python3 -c "from lib.personaConfig import PERSONA_KEY_TO_VALUE; \
  print('\\n'.join(sorted(PERSONA_KEY_TO_VALUE['intent'].keys())))"
```

### Find Test Failures by Pattern

```bash
# All failures with stack traces
python3 -m unittest discover -s _tests 2>&1 | grep -A 10 "^FAIL:"

# Specific error types
python3 -m unittest discover -s _tests 2>&1 | grep "AttributeError"
python3 -m unittest discover -s _tests 2>&1 | grep "KeyError"
python3 -m unittest discover -s _tests 2>&1 | grep "AssertionError"

# Test files with most failures
python3 -m unittest discover -s _tests 2>&1 | \
  grep "^FAIL:\|^ERROR:" | \
  sed 's/.*(\(test_[^.]*\)\..*/\1/' | \
  sort | uniq -c | sort -rn | head -10
```

### Bulk Replace Tokens

```bash
# Single file
sed -i '' 's/old_token/new_token/g' _tests/test_specific.py

# Multiple files
find _tests -name "*.py" -exec sed -i '' 's/old_token/new_token/g' {} \;

# With confirmation (shows what would change)
grep -r "old_token" _tests/ | head -20
# If OK, then run sed command above
```

## Summary

**Key Principle**: When tokens change, tests must change too.

**Quick Checklist**:
- [ ] Identify baseline (last passing commit)
- [ ] List what tokens changed (removed/moved/renamed)
- [ ] Find all test references to changed tokens
- [ ] Update test data (inputs)
- [ ] Update test assertions (expected outputs)
- [ ] Run tests to verify
- [ ] Document changes in commit message

**Most Common Mistakes**:
1. Forgetting to check test suite after token changes
2. Only fixing test data but not assertions (or vice versa)
3. Assuming recipe parts have fixed indices
4. Not searching for both token name and axis name together

**Pro Tips**:
- Use grepai to find token usage: `grepai search "usage of token_name in tests"`
- Run tests frequently during refactoring
- Keep token changes and test updates in the same commit
- Document removed tokens in ADRs for future reference
