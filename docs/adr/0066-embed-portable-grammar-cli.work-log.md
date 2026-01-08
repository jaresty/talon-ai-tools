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
