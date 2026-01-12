# loop-002 evidence — helper:v20251223.1

## Behaviour outcome
Extract token override helpers into a shared package and update buildState to use it while keeping behaviour under test.

## Commands executed

### go test ./internal/barcli -run TestApplyOverrideToken_NotYetExtracted
- red | 2026-01-11T22:25:11Z | exit 1
  - helper:diff-snapshot=internal/barcli/build_test.go
  - failure: placeholder assertion `token override helper extraction pending` triggered, confirming the missing extraction.

### go test ./internal/barcli -run TestApplyOverrideToken
- green | 2026-01-11T22:32:08Z | exit 0
  - helper:diff-snapshot=internal/barcli/build.go, internal/barcli/build_test.go, internal/barcli/tokens/overrides.go
  - success: new characterization tests `TestApplyOverrideTokenScope`, `TestApplyOverrideTokenUnknown`, and `TestApplyOverrideTokenPersonaConflict` pass using the extracted helper.

### go test ./...
- green | 2026-01-11T22:32:25Z | exit 0
  - helper:diff-snapshot=internal/barcli/build.go, internal/barcli/build_test.go, internal/barcli/tokens/overrides.go
  - coverage: full suite passes, ensuring CLI/TUI and expect-dependent code remain stable.

## Artifacts
- Helper package: `internal/barcli/tokens/`
- Updated build logic: `internal/barcli/build.go`
- Characterization tests: `internal/barcli/build_test.go`
