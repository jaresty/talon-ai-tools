# 0066 — Embed prompt grammar in `bar` (work log)

## 2026-01-08 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision — capture portability requirement for embedding grammar into the CLI
- active_constraint: `go run ./cmd/bar help tokens --grammar nonexistent.json` fails with `open grammar: open nonexistent.json: no such file or directory`, proving the binary still depends on an external JSON file and is not portable on its own.
- validation_targets:
  - go run ./cmd/bar help tokens --grammar nonexistent.json
- evidence:
  - red: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-001.md#loop-001-red--helper-rerun-go-run-.-cmd-bar-help-tokens---grammar-nonexistentjson
- rollback_plan: `git restore --source=HEAD -- docs/adr/0066-embed-portable-grammar-cli.md docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-001.md`
- delta_summary: helper:diff-snapshot=3 files changed, 56 insertions(+) — add ADR 0066 decision document, work-log entry, and red evidence capturing the external grammar dependency
- loops_remaining_forecast: 2 loops (embed grammar bytes into the Go binary; update completions/tests to consume embedded payload) — medium confidence while implementation details are pending
- residual_constraints:
  - Grammar still loaded from disk; embed payload with `go:embed` and provide override hooks (severity: high; mitigation: update `internal/barcli/grammar.go`, add unit coverage; owning ADR 0066 Decision)
  - Release pipeline must regenerate the grammar before embedding to avoid drift (severity: medium; mitigation: enforce exporter step in CI; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Embed grammar JSON with `go:embed` and make embedded payload the default (`go test ./cmd/bar`)
  - Behaviour: Update release/test automation to verify embedded grammar stays in sync (validation via `go test` and release workflow dry-run)

## 2026-01-08 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision § runtime behaviour — embed grammar into the CLI binary and update exporter workflows so `bar` runs without on-disk JSON
- active_constraint: Without an embedded default, `go run ./cmd/bar build todo gist --json` fails once `build/prompt-grammar.json` is absent, preventing the CLI from running as a single portable binary.
- validation_targets:
  - go run ./cmd/bar build todo gist --json
- evidence:
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-002.md#loop-002-green--helper-rerun-go-run-.-cmd-bar-build-todo-gist---json
- rollback_plan: `git restore --source=HEAD -- .github/workflows/release-bar.yml CONTRIBUTING.md docs/adr/0066-embed-portable-grammar-cli.md docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-002.md internal/barcli/app.go internal/barcli/grammar.go internal/barcli/grammar_embed.go internal/barcli/grammar_loader_test.go internal/barcli/embed/prompt-grammar.json prompts/export.py readme.md`
- delta_summary: helper:diff-snapshot=7 files changed, 84 insertions(+), 29 deletions(-) plus new `internal/barcli/embed/prompt-grammar.json` mirror — embed the grammar, add loader tests, refresh docs/automation, and wire the exporter + release workflow to maintain the mirrored asset
- loops_remaining_forecast: 1 loop (ensure release workflow guards fail on grammar drift; observe post-landing CI) — medium confidence pending guardrail verification
- residual_constraints:
  - Release workflow lacks a diff guard on regenerated grammar; add explicit check so CI fails on drift (severity: medium; mitigation: update release workflow; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Add diff/identity guardrail to release pipeline (validation via exporter + diff checks)

## 2026-01-08 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § automation — enforce grammar regeneration guardrail in release pipeline
- active_constraint: The `release-bar` workflow regenerates the grammar but succeeds even if tracked artifacts drift because no diff guard fails the job; without a guardrail, stale grammars can ship.
- validation_targets:
  - python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
  - git diff --exit-code -- build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - cmp --silent build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - go test ./internal/barcli
- evidence:
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-003.md#loop-003-green--helper-rerun-python3--m-prompts-export----output-build-prompt-grammarjson---embed-path-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-003.md#loop-003-green--helper-rerun-git-diff---exit-code----build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-003.md#loop-003-green--helper-rerun-cmp---silent-build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-003.md#loop-003-green--helper-rerun-go-test-.-internal-barcli
- rollback_plan: `git restore --source=HEAD -- .github/workflows/release-bar.yml docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-003.md`
- delta_summary: helper:diff-snapshot=1 file changed, 5 insertions(+), 1 deletion(-) — add guarded exporter step to fail CI on grammar drift and verify commands locally
- loops_remaining_forecast: 1 loop (prove guardrail fails closed on drift; observe post-landing CI) — medium confidence pending failure verification
- residual_constraints:
  - Guardrail failure path unverified; simulate drift and ensure pipeline command exits non-zero (severity: medium; mitigation: induce drift and capture failure evidence; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Induce grammar drift locally and observe guardrail failure (validation via git diff/ cmp commands)

## 2026-01-08 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § automation — demonstrate release guardrail fails closed on grammar drift
- active_constraint: Without validating the failure path, we cannot trust the new guardrail to catch stale grammars; `git diff --exit-code -- build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json` must exit non-zero when artifacts diverge.
- validation_targets:
  - git diff --exit-code -- build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - cmp --silent build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
  - go test ./internal/barcli
- evidence:
  - red: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-red--helper-rerun-git-diff---exit-code----build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - red: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-red--helper-rerun-cmp---silent-build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-green--helper-rerun-python3--m-prompts-export----output-build-prompt-grammarjson---embed-path-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-green--helper-rerun-git-diff---exit-code----build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-green--helper-rerun-cmp---silent-build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md#loop-004-green--helper-rerun-go-test-.-internal-barcli
- rollback_plan: `git restore --source=HEAD -- docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-004.md`
- delta_summary: helper:diff-snapshot=2 files changed, 78 insertions(+), 2 deletions(-) — simulated drift without landing code changes, captured red failure, and confirmed guardrail returns to green after re-export
- loops_remaining_forecast: 0 loops (ADR ready for closure; continue to watch next release run) — high confidence after failure path validation
- residual_constraints:
  - Observe the next `release-bar` workflow to confirm guarded exporter step passes in CI (severity: low; mitigation: monitor Actions logs; trigger: release failure; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Monitor upcoming `release-bar` execution to ensure guardrail runs green (validation via GitHub Actions run)

## 2026-01-08 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision § automation — verify guardrail steady state and release build flow with embedded grammar
- active_constraint: After inducing drift, we must confirm the guardrail succeeds once artifacts align so release builds do not fail spuriously; `go build ./cmd/bar` represents the release step.
- validation_targets:
  - python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
  - git diff --exit-code -- build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - cmp --silent build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - go build ./cmd/bar
- evidence:
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-005.md#loop-005-green--helper-rerun-python3--m-prompts-export----output-build-prompt-grammarjson---embed-path-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-005.md#loop-005-green--helper-rerun-git-diff---exit-code----build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-005.md#loop-005-green--helper-rerun-cmp---silent-build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-005.md#loop-005-green--helper-rerun-go-build-.-cmd-bar
- rollback_plan: `git restore --source=HEAD -- docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-005.md`
- delta_summary: helper:diff-snapshot=2 files changed, 56 insertions(+), 0 deletions(-) — capture steady-state guardrail evidence and document final parity check
- loops_remaining_forecast: 0 loops (ADR ready for closure; only external release observation outstanding) — high confidence in guardrail coverage
- residual_constraints:
  - Observe the next `release-bar` workflow to confirm guarded exporter step passes in CI (severity: low; mitigation: monitor Actions logs; trigger: release failure; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Monitor upcoming `release-bar` execution to ensure guardrail runs green (validation via GitHub Actions run)

## 2026-01-08 — loop 006
- helper_version: helper:v20251223.1
- focus: Decision § runtime verification — ensure embedded grammar preserves completion guardrails
- active_constraint: After embedding the grammar, we must confirm `make bar-completion-guard` still passes so shell completions and grammar-dependent flows remain portable.
- validation_targets:
  - make bar-completion-guard
- evidence:
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-006.md#loop-006-green--helper-rerun-make-bar-completion-guard
- rollback_plan: `git restore --source=HEAD -- docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-006.md`
- delta_summary: helper:diff-snapshot=2 files changed, 61 insertions(+), 0 deletions(-) — run completion pytest guard to prove embedded grammar keeps CLI completions working
- loops_remaining_forecast: 0 loops (ADR work complete; external release observation only) — high confidence after guardrails validated
- residual_constraints:
  - Observe the next `release-bar` workflow to confirm guarded exporter step passes in CI (severity: low; mitigation: monitor Actions logs; trigger: release failure; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Monitor upcoming `release-bar` execution to ensure guardrail runs green (validation via GitHub Actions run)

## 2026-01-08 — loop 007
- helper_version: helper:v20251223.1
- focus: Decision § closure — certify embedded grammar workflow and mark ADR completed
- active_constraint: Before closing ADR 0066 we must prove the exporter and CLI tests pass in steady state so the embedded grammar remains canonical (`python3 -m prompts.export` and `go test ./internal/barcli`).
- validation_targets:
  - python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
  - git diff --exit-code -- build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - cmp --silent build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
  - go test ./internal/barcli
- evidence:
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-007.md#loop-007-green--helper-rerun-python3--m-prompts-export----output-build-prompt-grammarjson---embed-path-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-007.md#loop-007-green--helper-rerun-git-diff---exit-code----build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-007.md#loop-007-green--helper-rerun-cmp---silent-build-prompt-grammarjson-internal-barcli-embed-prompt-grammarjson
  - green: docs/adr/evidence/0066-embed-portable-grammar-cli/loop-007.md#loop-007-green--helper-rerun-go-test-.-internal-barcli
- rollback_plan: `git restore --source=HEAD -- docs/adr/0066-embed-portable-grammar-cli.md docs/adr/0066-embed-portable-grammar-cli.work-log.md docs/adr/evidence/0066-embed-portable-grammar-cli/loop-007.md`
- delta_summary: helper:diff-snapshot=3 files changed, 60 insertions(+), 1 deletion(-) — reran exporter/tests, flipped ADR status to completed, and documented closure
- loops_remaining_forecast: 0 loops (ADR closed; external release monitoring remains informational) — high confidence after closure
- residual_constraints:
  - Monitor upcoming `release-bar` execution to ensure guardrail runs green (severity: low; mitigation: watch Actions logs; trigger: release failure; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Passive monitoring of `release-bar` workflow (no further repo work required)
