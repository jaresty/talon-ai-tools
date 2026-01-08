# 0065 — Portable prompt grammar CLI (work log)

## 2026-01-08 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision — baseline exporter slice to unblock portable CLI grammar
- active_constraint: Portable grammar export path failed because `python3 -m prompts.export --output build/prompt-grammar.json` could not import the prompts package, preventing downstream CLIs from consuming Concordance configuration outside Talon
- validation_targets:
  - python3 -m prompts.export --output build/prompt-grammar.json
  - python3 -m pytest _tests/test_prompt_grammar_export.py
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-001.md#loop-001-red--helper-rerun-python3---m-prompts.export---output-build-prompt-grammarjson
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-001.md#loop-001-green--helper-rerun-python3---m-pytest-_tests-test_prompt_grammar_exportpy
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-001.md#loop-001-green--helper-rerun-python3---m-prompts.export---output-build-prompt-grammarjson
- rollback_plan: `git restore --source=HEAD -- build/prompt-grammar.json lib/promptGrammar.py lib/talonSettings.py prompts/export.py prompts/__init__.py _tests/test_prompt_grammar_export.py docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-001.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=8 files changed, 2061 insertions(+) — add prompt grammar exporter payload, CLI entry point, tests, generated JSON artefact, and loop documentation
- loops_remaining_forecast: 3 loops (Go CLI command surface, CLI error contract fixtures, CI regen hook) — medium confidence pending tooling parity and automation coverage
- residual_constraints:
  - Go `bar build` CLI absent (severity: high; mitigation: scaffold Go parser that consumes `build/prompt-grammar.json`, validate with `bar build todo gist --json`; monitor go build + targeted recipe tests; owning ADR 0065 Decision)
  - Structured error fixtures still pending (severity: medium; mitigation: add regression tests covering `conflict`/`format` JSON output once CLI exists; monitor future `_tests` Go harness; owning ADR 0065 Decision)
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Implement Go `bar build` portable CLI using exported grammar (`go test ./cmd/bar` and `bar build todo gist --json`)
  - Behaviour: Wire CI regen + structured error fixtures (`python3 -m prompts.export --output build/prompt-grammar.json` && go test harness once CLI lands)

## 2026-01-08 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision — ensure portable CLI honours multi-word tokens and emphasises plain-text sections for LLM consumption
- active_constraint: Portable `bar build` CLI failed to parse multi-word directional tokens and its plain-text output buried task directives; `BAR_DISABLE_MULTIWORD=1 go run ./cmd/bar --prompt "Fix onboarding" build todo steps fly rog` returned `error: unrecognized token`, breaking ADR Decision expectations for shorthand parity and clear prompt framing
- validation_targets:
  - BAR_DISABLE_MULTIWORD=1 go run ./cmd/bar --prompt "Fix onboarding" build todo steps fly rog
  - go run ./cmd/bar --prompt "Fix onboarding" build todo steps fly rog
  - go test ./...
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-002.md#loop-002-red--helper-rerun-bar_disable_multiword1-go-run-.-cmd-bar----prompt-fix-onboarding-build-todo-steps-fly-rog
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-002.md#loop-002-green--helper-rerun-go-run-.-cmd-bar----prompt-fix-onboarding-build-todo-steps-fly-rog
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-002.md#loop-002-green--helper-rerun-go-test-.
- rollback_plan: `git restore --source=HEAD -- cmd/bar/main.go cmd/bar/testdata/grammar.json internal/barcli/app.go internal/barcli/app_test.go internal/barcli/build.go internal/barcli/build_test.go internal/barcli/render.go internal/barcli/render_test.go lib/promptGrammar.py docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-002.md`
- delta_summary: helper:diff-snapshot=4 files changed, 123 insertions(+), 48 deletions(-) — normalize multi-word tokens, emphasise section headings, add regression tests, and document loop evidence
- loops_remaining_forecast: 1 loop (structured error schema & CI regeneration) — medium confidence contingent on aligning Go error payloads with ADR contract and automating artifact checks
- residual_constraints:
  - Structured error fixtures pending (severity: medium; mitigation: add regression tests covering `conflict`/`format` JSON output once CLI exists; monitor future `_tests` Go harness; owning ADR 0065 Decision)
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Align Go CLI error schema with ADR contract and add failure fixtures (`go test ./internal/barcli` exercising `unknown_token`, `conflict`, `format` paths)
  - Behaviour: Automate prompt grammar regeneration in CI and guardrail cleanliness (`python3 -m prompts.export --output build/prompt-grammar.json` in pipeline, followed by `git diff --exit-code build/prompt-grammar.json`)
