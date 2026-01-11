Proposed — Expect-based integration suite for Bubble Tea TUI (2026-01-11)

## Context
- The Bubble Tea TUI (`bar tui`) now ships a compact layout (ADR 0071) but its behaviour is only partially covered by Go unit tests and deterministic snapshot fixtures.
- Critical interactions (palette focus, command execution, preset workflows, environment allowlist, help overlay, clipboard flows) rely on manual verification or ad-hoc `expect` scripts captured in ADR evidence loops.
- Regression loops (e.g., 0070 loop-082/083, 0071 loop-003) proved `expect` can validate Bubble Tea focus transitions while logging `BARTUI_DEBUG_PALETTE`, yet there is no canonical test harness, naming scheme, or CI entry point.
- Without a structured suite we miss coverage for multi-step keyboard sequences, risk layout regressions escaping review, and duplicate fragile scripts across ADR loops.

## Decision
- Establish a repository-backed `expect` integration suite under `tests/integration/tui/` that provides reusable helpers for Bubble Tea workflows and runs with `NO_COLOR=1` to stabilise output.
- Define a canonical harness command `scripts/tools/run-tui-expect.sh <case>` that wraps `expect`, provisions `BARTUI_DEBUG_*` logs, seeds deterministic grammar fixtures, and records transcripts for evidence.
- Curate a happy-path interaction inventory that each receives a dedicated expect case and golden log:
  1. **Launch & status strip** — confirm compact summary renders above the fold, result summary default, and `helper:diff-snapshot` parity with `tui_smoke.json`.
  2. **Focus cycle** — Tab through Subject → Tokens → Command → Result viewport → Environment allowlist, asserting status copy and viewport scroll hints.
  3. **Token palette workflows** — open via `Ctrl+P`, filter, apply option, reset to preset, undo, ensure Enter from filter advances to options and palette stays docked.
  4. **Token chip editing** — keyboard removal (`Del`), confirmation status messages, divergence indicator updates.
  5. **Preset management** — open preset pane, load, save, delete, confirm divergence and undo semantics.
  6. **Command execution** — run subject and preview commands, capture success/failure summaries, exit code, environment chips, cancellation (`Esc`).
  7. **Environment allowlist** — toggle entries (`Ctrl+E`, `Ctrl+A`), verify summaries and command input gating.
  8. **Clipboard flows** — load subject from clipboard, copy preview and CLI command, reinsert stdout, ensure status hints persist.
  9. **Help overlay** — toggle `?`, assert grouped headings align with ADR 0071 copy.
   10. **Window resize** — send `WindowSizeMsg` via expect to confirm token and result viewports stay within 20-row terminals.
- Seed the suite with initial `launch-status` and `focus-cycle` cases to exercise the harness while we backfill the remaining inventory.
- Store deterministic transcripts (`*.log`) and palette debug outputs in `tests/integration/tui/fixtures/`, referencing them via helper assertions rather than ad-hoc `grep` in scripts.

- Integrate the suite into CI via a `make expect-integration` target executed after Go tests; failures emit pointer to transcript diff and associated debug log.
- Require new interactive features to land with an expect case plus Go/Snapshot coverage, documented in ADR work logs using `helper:rerun scripts/tools/run-tui-expect.sh <case>`.

## Rationale
- Bubble Tea behaviour depends on asynchronous focus changes that Go unit tests cannot easily observe; expect can simulate keystrokes and read the rendered view exactly as operators experience it.
- Formalising the harness reduces duplication across ADR loops and ensures evidence captured during loops becomes regression coverage.
- Enumerating happy-path scenarios keeps the suite focused on high-value interactions while leaving space for future negative tests as needed.
- CI integration prevents regressions from shipping unnoticed and shortens manual verification cycles for UX-focused ADRs.

## Consequences
- Contributors must maintain expect transcripts alongside Go fixtures; copying or updating layout text will require running the integration suite and reviewing diffs.
- CI runners need `expect` tooling available; local developer environments must install `expect` (documented in onboarding).
- Additional runtime (a few seconds per case) is added to the test pipeline; we mitigate by grouping cases and using deterministic fixtures to avoid flakes.
- The harness introduces shell scripting to orchestrate expect runs; these scripts must follow repository security guidelines (no untrusted eval, consistent path usage).

## Validation
- `scripts/tools/run-tui-expect.sh focus-cycle` — confirms focus ring cycles Subject → Tokens → Command → Result viewports with the expected status copy.
- `scripts/tools/run-tui-expect.sh launch-status` — confirms compact status strip, result summary, and smoke snapshot parity.
- `go test ./internal/bartui` — unit guardrails remain green after expect suite integration.
- `go test ./cmd/bar/...` — snapshot harness still matches CLI output with the expect suite enabled.

## Follow-up
- Expand the expect suite by migrating existing ADR expect snippets (`loop-081`–`loop-083`, `loop-003`) into reusable cases for palette workflows, presets, clipboard flows, and window resize coverage.
- Add CI wiring (`make expect-integration`) and document developer workflow in `docs/testing.md`.
- Expand inventory with negative-case coverage (e.g., failed command exit code, missing env var warnings) once the happy-path suite is stable.
- Monitor runtime and flake rate; adjust harness timeouts or fixture size as needed to keep the suite reliable.

## Anti-goals
- Do not replace Go unit tests or snapshot fixtures; expect augments, not supersedes, existing guardrails.
- Do not cover every failure permutation immediately; focus on canonical happy paths and expand iteratively as regressions appear.
