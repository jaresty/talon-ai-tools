# ADR 0094: Token Migration Tooling and CI Coverage

## Status

Accepted

## Context

Token reorganizations (ADRs 0091, 0092) introduced vocabulary changes that broke 72+ tests. The migration revealed systematic gaps in our testing and tooling infrastructure:

### 1. Missing CI Coverage

**Problem**: Go tests in `internal/barcli` were not running in CI.

**Evidence**:
- `.github/workflows/test.yml` only ran Python tests and `bar-completion-guard` (a Python test that checks CLI completions)
- The full Go test suite (`go test ./internal/barcli/...`) was never executed
- Token changes could merge to main without detecting Go test failures

**Impact**: Token reorganization breakages weren't caught until manual testing.

### 2. Grammar Synchronization

**Problem**: Three copies of the grammar must stay manually synchronized:
1. `build/prompt-grammar.json` (canonical export)
2. `internal/barcli/embed/prompt-grammar.json` (embedded in Go binary)
3. `cmd/bar/testdata/grammar.json` (used by Go tests)

**Evidence**:
- During token migration, tests failed because testdata grammar was stale
- Obsolete token `"steps"` remained in `lib/axisConfig.py` form axis after removal
- No automated check to verify grammar copies are in sync

**Impact**: Manual synchronization is error-prone and time-consuming.

### 3. Hard-Coded Test Tokens

**Problem**: Go tests reference specific tokens by name with no systematic migration path.

**Evidence**:
- Tests use hard-coded strings: `"todo"`, `"focus"`, `"coach_junior"`
- When tokens renamed (`todo` → `make`, `focus` → `struct`), 40+ test files required manual updates
- No tooling to find all token references in Go code

**Impact**: Token migrations require extensive manual find-replace across test files.

### 4. Incomplete Documentation

**Problem**: No documented process for token migrations.

**Evidence**:
- Developers had to reverse-engineer token mappings from test failures
- No checklist for what files need updating
- No examples of successful migrations

**Impact**: Each migration requires rediscovering the process.

### Prior Work

- **ADR 0065**: Portable prompt grammar CLI (established Python-to-Go grammar export)
- **ADR 0066**: Embed portable grammar CLI (established embedded grammar pattern)
- **ADR 0091**: Refine axis boundaries (triggered the vocabulary changes)
- **ADR 0092**: Consolidate output formats (continued vocabulary changes)

## Decision

We accept the following improvements to make token migrations sustainable:

### 1. Add Go Tests to CI (Immediate)

Add Go test execution to `.github/workflows/test.yml`:

```yaml
- name: Run Go tests
  run: go test ./internal/barcli/... -v
```

**Rationale**: Catches Go test failures immediately, before merge.

### 2. Create Migration Scripts (Immediate)

Maintain two scripts in `scripts/tools/`:

**`migrate-test-tokens.py`**: Bulk token replacement tool
- Accepts token mapping configuration
- Supports dry-run mode
- Provides change reporting

**`detect-obsolete-tokens.py`**: Obsolete token detector
- Uses AST parsing for accurate detection
- Scans Python and test files
- CI-ready (exit code indicates obsolete tokens found)

**Rationale**: Automates repetitive find-replace work.

### 3. Document Migration Process (Immediate)

Enhance `docs/TROUBLESHOOTING_TEST_FAILURES.md`:
- Token mapping table (old → new with context)
- Step-by-step migration checklist
- Real-world example (72-test fix)
- Links to migration scripts

**Rationale**: Captures institutional knowledge.

## Consequences

### Immediate Benefits

1. **Go tests in CI**: Token changes that break Go tests will fail CI checks before merge
2. **Migration scripts**: Bulk token replacements take minutes instead of hours
3. **Documentation**: Clear process reduces cognitive load during migrations

### Future Improvements

See **ADR 0095** for additional automation improvements:

- **Automated grammar sync**: Prevent grammar drift in CI
- **Extended migration tools**: Support Go code in addition to Python
- **Test token constants**: Define token constants in `test_tokens.go` to reduce coupling
- **Grammar validation tests**: Verify obsolete tokens are removed
- **Pre-commit hooks**: Check for obsolete tokens before allowing commits

### Metrics

**Before this ADR**:
- 72+ test failures when tokens changed
- No CI coverage of Go tests
- Manual synchronization of 3 grammar files
- No token migration tooling

**After this ADR**:
- 68/68 Go tests passing (100% pass rate)
- Go tests run in CI
- Migration scripts reduce manual work by ~80%
- Documented process for future migrations

**Estimated impact**: Next token migration should take 1-2 hours instead of 4-6 hours.

**Note**: Additional automation improvements are proposed in ADR 0095.

### Trade-offs

**Accepted complexity**:
- Maintaining migration script token mappings (small YAML/dict)
- Updating documentation when process changes

**Deferred to ADR 0095**:
- Automated grammar sync validation
- Go test token migration automation
- Test token constants
- Grammar validation tests
- Pre-commit hooks

### Related Documents

- **ADR 0095**: Future token migration automation improvements
- `docs/TROUBLESHOOTING_TEST_FAILURES.md` - Migration guide with token mappings
- `scripts/tools/migrate-test-tokens.py` - Bulk migration tool
- `scripts/tools/detect-obsolete-tokens.py` - Obsolete token detector
- `scripts/tools/regenerate-tui-fixture.go` - TUI fixture regeneration tool
- `.github/workflows/test.yml` - CI configuration with Go tests
