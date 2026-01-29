# ADR 0095: Future Token Migration Automation Improvements

## Status

Proposed

## Context

ADR 0094 established baseline token migration tooling (Go tests in CI, migration scripts, documentation). This ADR proposes additional automation to further reduce migration friction.

### Current State (Post-ADR 0094)

**What Works:**
- Go tests run in CI, catching breakages immediately
- Python migration scripts exist (`migrate-test-tokens.py`, `detect-obsolete-tokens.py`)
- Documentation captures migration process in `TROUBLESHOOTING_TEST_FAILURES.md`

**Remaining Friction:**
- Three grammar copies (`build/`, `embed/`, `testdata/`) must be manually synchronized
- Go test token migrations require manual find-replace (Python scripts don't support Go)
- Hard-coded token strings scattered across 40+ test files create coupling
- No automated verification that obsolete tokens are actually removed
- No pre-commit protection against committing obsolete tokens

### Prior Work

- **ADR 0091/0092**: Token reorganization that triggered the need for better tooling
- **ADR 0094**: Baseline migration infrastructure (Go tests in CI, scripts, docs)

## Decision

We propose the following additional improvements for future implementation:

### 1. Grammar Sync Validation (High Priority)

**Problem**: Three copies of grammar must stay in sync manually. Stale copies cause test failures.

**Solution**: Add Make targets for grammar validation:

```makefile
.PHONY: bar-grammar-check
bar-grammar-check:
	python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
	cp build/prompt-grammar.json cmd/bar/testdata/grammar.json
	git diff --exit-code build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json cmd/bar/testdata/grammar.json

.PHONY: bar-grammar-update
bar-grammar-update:
	python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
	cp build/prompt-grammar.json cmd/bar/testdata/grammar.json
	@echo "Grammar files updated. Review with 'git diff' before committing."
```

Add to CI in `.github/workflows/test.yml`:
```yaml
- name: Verify bar grammar is in sync
  run: make bar-grammar-check
```

**Rationale**: Prevents grammar drift from causing test failures.

**Estimated effort**: 1 hour (Make targets + CI update + testing)

### 2. Go Test Token Migration Support (Medium Priority)

**Problem**: Token renames require manual find-replace across Go tests. Python migration scripts only handle Python files.

**Solution**: Extend `scripts/tools/migrate-test-tokens.py` to support Go:

```python
# Token migration configuration (update this when tokens change)
GO_TOKEN_MIGRATIONS = {
    # Old token -> New token
    'focus': 'struct',
    'steps': 'flow',
    'todo': 'make',
    # ...
}

def migrate_go_tests(dry_run=True):
    """Apply token migrations to Go test files."""
    test_files = glob.glob('internal/barcli/*_test.go')
    for file_path in test_files:
        migrate_file(file_path, GO_TOKEN_MIGRATIONS, dry_run)
```

Usage:
```bash
# Preview changes
python scripts/tools/migrate-test-tokens.py --go --dry-run

# Apply changes
python scripts/tools/migrate-test-tokens.py --go
```

**Rationale**: Automates repetitive Go test updates during token migrations.

**Estimated effort**: 2-3 hours (extend script + test on real migration)

### 3. Test Token Constants (Low Priority)

**Problem**: Hard-coded token strings scattered across tests create coupling to vocabulary.

**Solution**: Define token constants in a shared test helper:

```go
// internal/barcli/test_tokens.go
package barcli

// Test token constants - update these when vocabulary changes
const (
    TestStaticToken    = "make"  // A valid static prompt
    TestScopeToken     = "struct" // A valid scope token
    TestMethodToken    = "flow"   // A valid method token
    TestPersonaPreset  = "teach_junior_dev" // A valid persona preset
)
```

Then in tests:
```go
words := []string{"bar", "build", TestStaticToken, TestScopeToken, ""}
```

**Rationale**: Single location to update test tokens during migrations.

**Tradeoff**: Adds indirection; tests become less self-documenting.

**Estimated effort**: 3-4 hours (create constants + update 40+ test files + verify)

### 4. Grammar Validation Test (Medium Priority)

**Problem**: No automated check that removed tokens are actually gone from source.

**Solution**: Add Python test:

```python
# _tests/test_obsolete_tokens.py
OBSOLETE_TOKENS = {
    # Removed in ADR 0091
    'todo', 'focus', 'steps', 'announce', 'coach_junior',
    # Add new obsolete tokens as migrations occur
}

def test_no_obsolete_tokens_in_axis_config():
    """Verify removed tokens don't appear in axisConfig.py"""
    from lib import axisConfig

    for axis_name, tokens in axisConfig.AXIS_KEY_TO_VALUE.items():
        for token in tokens:
            assert token not in OBSOLETE_TOKENS, \
                f"Obsolete token '{token}' found in axis '{axis_name}'"
```

**Rationale**: Prevents obsolete tokens from lingering in source after migration.

**Estimated effort**: 1 hour (create test + populate initial obsolete list)

### 5. Pre-commit Hook (Optional)

**Problem**: Developers can accidentally commit obsolete tokens.

**Solution**: Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for obsolete tokens before committing

python3 scripts/tools/detect-obsolete-tokens.py
if [ $? -ne 0 ]; then
    echo "❌ Obsolete tokens detected! Run 'python scripts/tools/migrate-test-tokens.py' to fix."
    exit 1
fi
```

**Rationale**: Catches obsolete tokens before they reach CI.

**Tradeoff**: Requires manual hook installation by each developer.

**Estimated effort**: 30 minutes (create hook + document installation)

## Consequences

### If Implemented

**Immediate Benefits:**
- Grammar sync validation prevents stale grammar copies (item #1)
- Go test migrations automated alongside Python (item #2)
- Obsolete tokens caught in CI (item #4)

**Long-term Benefits:**
- Token migrations could approach 30-60 minutes (from current 1-2 hours)
- Fewer manual steps = fewer opportunities for human error
- Test token constants reduce coupling (item #3)

**Costs:**
- Maintenance burden for new tooling (especially Go migration support)
- Test token constants add indirection (may reduce test clarity)
- Pre-commit hooks require developer onboarding

### If Not Implemented

Current state (post-ADR 0094) is serviceable:
- Token migrations take 1-2 hours (down from 4-6 hours pre-ADR 0094)
- Manual grammar sync is error-prone but documented
- Go test migrations are manual but manageable

### Success Metrics

A fully-implemented ADR 0095 should achieve:
- **Grammar sync**: Zero grammar drift incidents in CI
- **Go migrations**: Token renames touch <5 files manually (rest automated)
- **Obsolete detection**: CI fails if obsolete tokens detected
- **Migration time**: 30-60 minutes per token migration (from current 1-2 hours)

### Implementation Priority

**Recommended order:**
1. Grammar sync validation (item #1) - highest ROI, prevents common failure mode
2. Grammar validation test (item #4) - low effort, high safety value
3. Go test token migration (item #2) - medium effort, reduces manual work
4. Test token constants (item #3) - optional, evaluate after observing migration patterns
5. Pre-commit hook (item #5) - optional, requires developer buy-in

### Related Documents

- **ADR 0094**: Token migration tooling and CI coverage (baseline infrastructure)
- **ADR 0091/0092**: Token reorganization that motivated these improvements
- `docs/TROUBLESHOOTING_TEST_FAILURES.md`: Migration process documentation
- `scripts/tools/migrate-test-tokens.py`: Token migration script
- `scripts/tools/detect-obsolete-tokens.py`: Obsolete token detector
