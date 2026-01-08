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
- loops_remaining_forecast: 0 loops (ADR ready for closure; watch next release run for first green with guard) — high confidence after automation guardrail lands
- residual_constraints:
  - Observe the next `release-bar` workflow to confirm guarded exporter step passes in CI (severity: low; mitigation: monitor Actions logs; trigger: release failure; owning ADR 0066 Consequences)
- next_work:
  - Behaviour: Monitor upcoming `release-bar` execution to ensure new guardrail runs green (validation via GitHub Actions run)
