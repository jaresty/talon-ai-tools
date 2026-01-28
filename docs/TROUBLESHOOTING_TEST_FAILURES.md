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

## Automation Scripts

### Token Migration Script

Use `scripts/tools/migrate-test-tokens.py` to automate bulk replacements:

```bash
# Preview changes without writing:
python scripts/tools/migrate-test-tokens.py --dry-run --verbose

# Apply migrations:
python scripts/tools/migrate-test-tokens.py

# Migrate specific file:
python scripts/tools/migrate-test-tokens.py --file _tests/test_foo.py
```

**How to use:**

1. Edit the script to add your token migrations:
   ```python
   TOKEN_MIGRATIONS = {
       'focus': 'struct',
       'actions': 'act',
       'steps': 'flow',
       # Add more mappings here
   }
   ```

2. Run with `--dry-run` to preview changes

3. Apply migrations: `python scripts/tools/migrate-test-tokens.py`

4. Review and commit: `git diff _tests/`

**For context-sensitive replacements** (e.g., 'plan' method vs 'plan' static prompt):
```python
CONTEXTUAL_MIGRATIONS = [
    ('plan', 'flow', r'GPTState\.last_method\s*=\s*["\']plan["\']'),
]
```

### Obsolete Token Detector

Use `scripts/tools/detect-obsolete-tokens.py` to find removed token usage:

```bash
# Check test files:
python scripts/tools/detect-obsolete-tokens.py

# Check all Python files (including lib/):
python scripts/tools/detect-obsolete-tokens.py --include-lib

# Show current vocabulary to update detector:
python scripts/tools/detect-obsolete-tokens.py --update-list
```

**Add to CI** to prevent regressions:
```yaml
# .github/workflows/test.yml
- name: Check for obsolete tokens
  run: python scripts/tools/detect-obsolete-tokens.py
```

## Token Mapping Reference

Common token migrations from ADR 0091/0092 Phase 1:

| Old Token     | New Token  | Axis      | Notes                                      |
|---------------|------------|-----------|-------------------------------------------|
| `focus`       | `struct`   | scope     | Structural focus                          |
| `narrow`      | `struct`   | scope     | Narrow structural scope                   |
| `bound`       | `struct`   | scope     | Bounded structure                         |
| `edges`       | `fail`     | scope     | Edge cases → failure modes                |
| `relations`   | `struct`   | scope     | Relationships → structure                 |
| `actions`     | `act`      | scope     | Action-oriented scope (form token exists) |
| `steps`       | `flow`     | method    | Step-by-step → flow (form token exists)   |
| `plan`        | `flow`     | method    | Planning → flow (static prompt exists)    |
| `debugging`   | `diagnose` | method    | Debug process → diagnosis                 |
| `xp`          | `experimental` | method | Extreme Programming                       |
| `cluster`     | `analysis` | method    | Clustering → analysis                     |
| `decide`      | `inform`   | intent    | Decision-making → informing               |
| `describe`    | `show`     | static    | Universal task taxonomy                   |
| `todo`        | `make`     | static    | Universal task taxonomy                   |

**Context-sensitive tokens:**
- `plan`: Valid as **static prompt**, use `flow` for **method**
- `actions`: Valid as **form** token, use `act` for **scope**
- `steps`: Valid as **form** token, use `flow` for **method**

## When Changing Tokens: Checklist

Follow this checklist when removing, renaming, or moving tokens:

### Before Making Changes

- [ ] **Document the change** in an ADR or issue
- [ ] **Search for usage** in tests: `grep -r "token_name" _tests/`
- [ ] **Check patterns** in `lib/modelPatternGUI.py` (31 patterns reference tokens)
- [ ] **Check ADRs** that document token-axis mappings (e.g., ADR 033)
- [ ] **Note context-sensitive usage** (e.g., 'plan' as static vs method)

### Making Changes

- [ ] **Update axis configuration** (`lib/axisConfig.py` or equivalent)
- [ ] **Update pattern definitions** in `lib/modelPatternGUI.py`:
  - Recipe strings in all 31 patterns
  - `SCOPE_TOKENS`, `METHOD_TOKENS` sets at bottom of file
- [ ] **Update test files** using migration script or manually
- [ ] **Update ADR documentation** (e.g., ADR 033 axis overlap mappings)
- [ ] **Update scripts** that hardcode tokens (e.g., `history-axis-validate.py`)
- [ ] **Add to obsolete token detector** in `detect-obsolete-tokens.py`

### After Making Changes

- [ ] **Run full test suite**: `pytest _tests/ -v`
- [ ] **Check for obsolete tokens**: `python scripts/tools/detect-obsolete-tokens.py`
- [ ] **Review test coverage**: Are the new tokens tested?
- [ ] **Update troubleshooting guide** token mapping table (this document)
- [ ] **Commit with clear message** documenting what changed and why

### Special Case: Updating modelPatternGUI.py

When token vocabulary changes, `lib/modelPatternGUI.py` requires systematic updates:

**1. Update pattern recipes** (all 31 patterns):
```python
# BEFORE:
PromptPattern(
    name="Debug bug",
    recipe="describe · full · narrow · debugging · rog",
),

# AFTER:
PromptPattern(
    name="Debug bug",
    recipe="show · full · struct · diagnose · rog",
),
```

**2. Update token validation sets** (bottom of file):
```python
# BEFORE:
SCOPE_TOKENS = {
    "narrow", "focus", "bound", "edges", "relations", "system", "actions",
}

# AFTER:
SCOPE_TOKENS = {
    "act", "fail", "good", "mean", "struct", "thing", "time",
}
```

**Search patterns to find all occurrences:**
```bash
# Find patterns using obsolete token:
grep -n "obsolete_token" lib/modelPatternGUI.py

# Count patterns (should be 31):
grep -c "PromptPattern(" lib/modelPatternGUI.py
```

**Tip:** Update all patterns in a single pass to avoid inconsistencies.

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

**Recommended:** Use the migration script for safer bulk replacements:
```bash
# See "Automation Scripts" section above
python scripts/tools/migrate-test-tokens.py --dry-run --verbose
```

**Manual approach** (use with caution):
```bash
# Single file
sed -i '' 's/old_token/new_token/g' _tests/test_specific.py

# Multiple files
find _tests -name "*.py" -exec sed -i '' 's/old_token/new_token/g' {} \;

# With confirmation (shows what would change)
grep -r "old_token" _tests/ | head -20
# If OK, then run sed command above
```

**Warning:** Manual `sed` replacements don't handle context-sensitive tokens (e.g., 'plan' as static vs method).

## Real-World Example: Complete ADR 0091/0092 Phase 1 Fix

**What changed**: 72 test failures after removing/renaming multiple tokens

**Scope**:
- 24 test files needed updates
- 31 patterns in `modelPatternGUI.py` updated
- 1 ADR document (033) corrected
- 1 script (`history-axis-validate.py`) fixed

**Token migrations applied**:
```
focus → struct, actions → act, steps → flow, plan → flow
decide → inform, describe → show, todo → make
bound → struct, edges → fail, debugging → diagnose
```

**Files changed**:
- Tests: `test_model_pattern_gui.py` (34 tests), `test_help_hub.py` (6 tests), etc.
- Patterns: Updated all 31 pattern recipes and token sets
- Docs: Fixed ADR 033 axis overlap mappings (deep, actions, steps, socratic, direct)
- Scripts: Fixed hardcoded test data

**Result**: All 1205 tests passing (100% success rate)

**Time to fix**: ~4 hours manual (would be ~1 hour with automation scripts)

**Key insight**: Most failures were simple token replacements that could have been automated. The migration script would have saved ~3 hours.

## Summary

**Key Principle**: When tokens change, tests must change too.

**Quick Start** (with automation):
1. Run obsolete token detector: `python scripts/tools/detect-obsolete-tokens.py`
2. Update migration script with token mappings
3. Preview migrations: `python scripts/tools/migrate-test-tokens.py --dry-run`
4. Apply migrations: `python scripts/tools/migrate-test-tokens.py`
5. Fix remaining context-sensitive cases manually
6. Run tests: `pytest _tests/ -v`
7. Commit with clear message

**Traditional Checklist** (manual approach):
- [ ] Identify baseline (last passing commit)
- [ ] List what tokens changed (removed/moved/renamed)
- [ ] Find all test references to changed tokens
- [ ] Update test data (inputs)
- [ ] Update test assertions (expected outputs)
- [ ] Update `modelPatternGUI.py` patterns if needed
- [ ] Run tests to verify
- [ ] Document changes in commit message

**Most Common Mistakes**:
1. Forgetting to check test suite after token changes
2. Only fixing test data but not assertions (or vice versa)
3. Assuming recipe parts have fixed indices
4. Not searching for both token name and axis name together
5. **Not using automation scripts** (newest, most time-consuming mistake)

**Pro Tips**:
- **Use the migration script** for bulk replacements (saves hours)
- **Run obsolete token detector** before and after changes
- Use grepai to find token usage: `grepai search "usage of token_name in tests"`
- Run tests frequently during refactoring
- Keep token changes and test updates in the same commit
- Document removed tokens in ADRs for future reference
- Add CI check for obsolete tokens to prevent regressions
