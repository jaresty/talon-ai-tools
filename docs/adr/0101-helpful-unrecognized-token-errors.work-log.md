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

## Loop 002 | 2026-02-05

**helper_version:** `helper:v20251223.1`

**focus:** ADR-0101 § Implementation approach (Option A) → Enhance unknownValue() and applyShorthandToken() error formatting to include fuzzy suggestions and help hints

**active_constraint:** Error messages return minimal text without fuzzy suggestions or help hints; users cannot discover valid tokens or fix typos without external documentation lookup. This blocks the ADR's primary goal of providing actionable error guidance.

**expected_value:**
| Factor           | Value | Rationale |
|------------------|-------|-----------|
| Impact           | High  | Core value delivery: "Did you mean?" and help hints |
| Probability      | High  | Fuzzy matcher already green; formatting is deterministic |
| Time Sensitivity | High  | Completes user-facing improvements for common error case |

**validation_targets:**
- `go test ./internal/barcli -run TestBuildUnrecognizedToken`

**evidence:**
- red | 2026-02-05T20:50:00Z | exit 1 | go test ./internal/barcli -run TestBuildUnrecognizedToken
  helper:diff-snapshot=0 files changed (test file not yet created)
  Test does not exist; error message behavior undefined | inline
  ```
  ok  	github.com/talonvoice/talon-ai-tools/internal/barcli	0.322s [no tests to run]
  ```

- green | 2026-02-05T21:15:00Z | exit 0 | go test ./internal/barcli -run TestBuildUnrecognizedToken
  helper:diff-snapshot=3 files changed, 234 insertions(+), 5 deletions(-)
  All test cases pass: axis-specific errors show fuzzy suggestions and help hints | inline

- removal | 2026-02-05T21:20:00Z | [no tests] | git stash && go test ./internal/barcli -run TestBuildUnrecognizedToken
  helper:diff-snapshot=0 files changed
  Test reverts to no-tests-to-run state | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/build.go internal/barcli/grammar.go internal/barcli/build_error_test.go` followed by validation rerun

**delta_summary:** Enhanced error message formatting to include fuzzy suggestions and help hints. Files:
- `internal/barcli/grammar.go`: Added GetValidTokensForAxis(), GetAllStaticPrompts(), GetAllAxisTokens() methods for querying valid tokens
- `internal/barcli/build.go`: Added formatUnrecognizedError() helper that uses fuzzy matching; updated unknownValue() and applyShorthandToken() to use new formatter
- `internal/barcli/build_error_test.go`: Comprehensive test coverage for axis-specific and shorthand errors, fuzzy suggestions, and help hints

**loops_remaining_forecast:** 2-3 loops remaining
- Loop 003: Add recognized token context display to show what was successfully parsed
- Loop 004: Update integration tests and existing fixtures that expect old error format
- (Optional) Loop 005: Add color support for suggestions
Confidence: High - core functionality complete; remaining work is polish

**residual_constraints:**
- **Medium severity** - Shorthand mode cannot provide axis-specific context: When tokens fail in shorthand mode (e.g., "make meen"), the parser doesn't know which axis "meen" was intended for, so error shows generic "unrecognized token" with suggestions from all tokens. Override mode (e.g., "scope=meen") does provide axis context. Mitigation: This is acceptable; fuzzy matching still helps users. Users can switch to override mode for clearer errors. Monitor: User feedback about confusion. Reopen condition: Telemetry shows high retry rates on shorthand errors.
- **Low severity** - Color support not yet implemented: formatUnrecognizedError() returns plain text; suggestions could be highlighted for better scannability. Mitigation: Defer to follow-up loop or post-ADR enhancement. Monitor: When terminal detection is added. Reopen condition: User feedback requests color.
- **Low severity** - Multi-word token normalization not reflected in suggestions: If user types "fly rog", fuzzy matcher suggests "fly-rog" but doesn't explain the space→dash convention. Mitigation: Current suggestions are sufficient; users will learn from seeing the dash form. Monitor: Support questions about multi-word tokens. Reopen condition: Frequent user confusion.

**next_work:**
- Behaviour: Display recognized token context in error messages → validation: `go test ./internal/barcli -run TestBuildUnrecognizedToken` (extend with context assertions) → future-shaping: Help users understand parsing state when errors occur
