# ADR-0079 – Go CLI Regression Coverage for Build/Completion/Preset/TUI Paths
Status: Accepted
Date: 2026-01-12
Owners: CLI Reliability Working Group

## Context
- The Go CLI (`internal/barcli`) acts as the canonical entry point for Bubble Tea, completion scripts, preset management, and snapshot fixtures. Previous ADRs (e.g., ADR-0065 Portable Prompt Grammar CLI, ADR-0075 CLI Churn Refactor) standardised grammar handling and preset state, but their guardrails now rely mainly on unit tests for pure helpers.
- Unit coverage today focuses on token rendering, completion suggestion generation, preset persistence helpers, and TUI snapshot fixtures (`cmd/bar/main_test.go`). Error-handling branches inside `Run`, `runCompletion`, `runPreset`, and `runTUI` remain untested.
- The expect integration suite (`tests/integration/tui/cases/*.exp`) exercises happy-path TUI gestures, `--env` allowlists, and `--no-clipboard`, yet it never drives fixture mode, CLI flag validation failures, or grammar/load-time errors.
- Recent ADR 0077 loops highlighted multiple incidents where regressions slipped through: build command JSON emission, preset deletion guardrails, completion backend invocation, and environment allowlist messaging. Each was caught manually in expect transcripts or hand testing, not by automated coverage.

## Problem
- **`bar build` surface gaps** – there are no tests for `--input`, piped STDIN, `--output`, or JSON output. Errors when reading files, writing results, or encoding JSON (e.g., invalid unicode) can regress silently. Warnings triggered when caching the last build fails are unverified.
- **Completion entry points unguarded** – neither `bar completion <shell>` nor `bar __complete` are exercised. Missing shell arguments, invalid indices, grammar load failures, or script generation changes could break shell integration without detection.
- **Preset subcommands lack coverage** – the CLI handles `save`, `list`, `show (--json)`, `use`, and `delete --force`, but existing tests only cover `save`/`use`. Failure states (missing preset, disabled state, absent `--force`) and list/show happy paths are unchecked.
- **Flag validation regressions** – `cli.Parse` rejects zero/negative fixture dimensions, blank `--env` entries, and mutually exclusive `--prompt/--input`, yet no tests assert these errors. A parser regression could reintroduce ambiguous or silently discarded flags.
- **TUI command error handling** – `bar tui` exposes `--fixture`, width/height validation, `--env` missing-values messaging, grammar load failures, and clipboard fallbacks. Expect cases cover interactive success, but no automated test verifies the CLI’s error messages or fixture validation.

## Decision
- Establish a dedicated regression suite that exercises each CLI entry point (`build`, `completion`, `__complete`, `preset`, `tui`) through `barcli.Run` and the compiled binary where appropriate. The suite should cover both success and failure modes, mirroring the scenarios enumerated above.
- Introduce targeted unit tests for `cli.Parse` edge cases to freeze flag validation semantics (dimension > 0, deduped `--env`, mutually exclusive prompt/input, unknown flags).
- Expand expect coverage only where interactive behaviour is required (e.g., fixture overlays). CLI error validation remains in Go tests to keep expect scripts focused on terminal UX.
- Annotate new coverage with references to this ADR in work logs to make future gaps discoverable.

## Implementation Approach
1. **Build command coverage**
   - Add table-driven tests around `barcli.Run` for combinations of `--prompt`, `--input` (temp file), piped STDIN, `--output`, and `--json`.
   - Simulate file read/write failures using temp directories with restricted permissions to assert error messaging.
   - Verify warnings from `saveLastBuild` by injecting a failing state backend (e.g., via environment variable).
2. **Completion commands**
   - Add integration-style tests invoking `Run([]string{"completion", …})` and `Run([]string{"__complete", …})` with valid and invalid parameters. Assert script output, error strings, and non-zero exits for bad inputs.
3. **Preset lifecycle**
   - Create isolated config dirs in tests and cover `list` (empty/populated), `show` (plaintext & JSON), `delete` (with/without `--force`), and error cases for missing presets or disabled state.
4. **Parser edge cases**
   - Extend `internal/barcli/app_parse_test.go` to assert zero/negative fixture dimensions, blank `--env`, duplicate deduping, `--prompt`+`--input`, and unknown flags all return specific errors.
5. **TUI command guards**
   - Add tests that run `Run([]string{"tui", …})` with `--fixture`, invalid width/height, missing env vars, and grammar load failures. Reuse the existing `SetTUIStarter` hook to stub success without launching Bubble Tea.
6. **Expect alignment**
   - Optionally add a fixture-mode expect case that asserts snapshot diff errors, ensuring CLI and expect scripts stay in sync.

## Consequences
- Increased test runtime (additional CLI invocations) but improved regression detection across build, completion, preset, and TUI commands.
- Clearer division between Go-level regression tests and expect scripts, reducing the chance of overlapping responsibilities.
- New contributors gain a canonical suite demonstrating how to exercise CLI error states, lowering the risk of accidentally regressing flag semantics.

## Validation
- New Go tests run via `go test ./internal/barcli` and `go test ./cmd/bar`. Expect additions continue to run under `scripts/tools/run-tui-expect.sh --all`.
- Code coverage reports should show previously untested branches (flag validation, preset commands, completion engine) as exercised.
