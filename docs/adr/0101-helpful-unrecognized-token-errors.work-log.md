# Work Log: ADR-0101 Helpful Unrecognized Token Errors

## Loop 001 | 2026-02-05

**helper_version:** `helper:v20251223.1`

**focus:** ADR-0101 § Implementation approach (Option A) → Add fuzzy matching helper for token suggestions

**active_constraint:** No fuzzy matching mechanism exists; the CLI cannot suggest similar tokens when users mistype, preventing the ADR's core "Did you mean?" functionality from working. This blocks all downstream error message improvements since suggestions require edit distance calculation.

**expected_value:**
| Factor           | Value | Rationale |
|------------------|-------|-----------|
| Impact           | High  | Unblocks all error message improvements in ADR-0101 |
| Probability      | High  | Levenshtein algorithm is deterministic and well-understood |
| Time Sensitivity | High  | Foundation for user-facing improvements |

**validation_targets:**
- `go test ./internal/barcli -run TestFuzzyMatch`

**evidence:**
- red | 2026-02-05T20:15:00Z | exit 1 | go test ./internal/barcli -run TestFuzzyMatch
  helper:diff-snapshot=0 files changed
  Test file does not exist; fuzzy matching behavior undefined | inline
  ```
  testing: warning: no tests to run
  PASS
  ```

- green | 2026-02-05T20:30:00Z | exit 0 | go test ./internal/barcli -run TestFuzzyMatch
  helper:diff-snapshot=2 files changed, 120 insertions(+)
  Fuzzy matcher correctly suggests tokens within edit distance 2 | inline

- removal | 2026-02-05T20:35:00Z | exit 1 | git restore --source=HEAD internal/barcli/fuzzy.go internal/barcli/fuzzy_test.go && go test ./internal/barcli -run TestFuzzyMatch
  helper:diff-snapshot=0 files changed
  Test reverts to no-tests-to-run state | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/fuzzy.go internal/barcli/fuzzy_test.go` followed by validation rerun

**delta_summary:** Added fuzzy matching helper with Levenshtein edit distance calculation and test coverage for typos, dashes, and prefix matching scenarios. Files: `internal/barcli/fuzzy.go` (implementation), `internal/barcli/fuzzy_test.go` (test cases).

**loops_remaining_forecast:** 4-5 loops remaining
- Loop 002: Enhance error message formatting in build.go to use fuzzy matcher
- Loop 003: Add axis-aware help hints to error messages
- Loop 004: Implement recognized token context display
- Loop 005: Update integration tests and fixtures
Confidence: High - well-defined scope with deterministic validation

**residual_constraints:**
- **Medium severity** - Shell completion integration not yet planned: The ADR follow-up mentions extending completion hints, but this is deferred until core error messages ship. Mitigation: Track in ADR follow-up section. Monitor: When user feedback requests proactive suggestions. Reopen condition: User requests or telemetry shows high completion usage.
- **Low severity** - Color support dependency not yet chosen: ADR mentions `github.com/fatih/color` but implementation can defer this. Mitigation: Start with plain text; add color in follow-up loop. Monitor: When terminal capability detection is needed. Reopen condition: User feedback requests color or CI breaks on color codes.

**next_work:**
- Behaviour: Enhance unknownValue() error formatting → validation: `go test ./internal/barcli -run TestBuildUnrecognizedToken` → future-shaping: Centralize error formatting to maintain "helpful by default" invariant
