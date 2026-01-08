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

## 2026-01-08 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision — document CLI help surfaces and distribution path so collaborators discover the prompt grammar without repo spelunking
- active_constraint: ADR 0065 lacked guidance on invoking `bar --help` / `bar help tokens` and offered no installation path, leaving downstream consumers without a documented way to access the grammar outside the repo (`git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md | rg "bar --help"` exited 1)
- validation_targets:
  - git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "bar --help"
  - git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "install-bar"
  - rg "bar --help" docs/adr/0065-portable-prompt-grammar-cli.md
  - rg "install-bar" docs/adr/0065-portable-prompt-grammar-cli.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-003.md#loop-003-red--helper-rerun-git-show-headdocsadr0065-portable-prompt-grammar-climd--rg-bar----help
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-003.md#loop-003-red--helper-rerun-git-show-headdocsadr0065-portable-prompt-grammar-climd--rg-install-bar
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-003.md#loop-003-green--helper-rerun-rg-bar----help-docsadr0065-portable-prompt-grammar-climd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-003.md#loop-003-green--helper-rerun-rg-install-bar-docsadr0065-portable-prompt-grammar-climd
- rollback_plan: `git restore --source=HEAD -- docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-003.md`
- delta_summary: helper:diff-snapshot=2 files changed, 12 insertions(+) — add CLI help + installer guidance to ADR and record loop evidence
- loops_remaining_forecast: 2 loops (error schema fixtures, CI regeneration hook) — medium confidence pending automation work from prior residual constraints
- residual_constraints:
  - Structured error fixtures pending (severity: medium; mitigation: add regression tests covering `conflict`/`format` JSON output once CLI exists; monitor future `_tests` Go harness; owning ADR 0065 Decision)
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Align Go CLI error schema with ADR contract and add failure fixtures (`go test ./internal/barcli` exercising `unknown_token`, `conflict`, `format` paths)
  - Behaviour: Automate prompt grammar regeneration in CI and guardrail cleanliness (`python3 -m prompts.export --output build/prompt-grammar.json` in pipeline, followed by `git diff --exit-code build/prompt-grammar.json`)

## 2026-01-08 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision — expose token ordering rules and shorthand guidance via the CLI help entry point
- active_constraint: `bar help` only echoed the build usage string, leaving ADR consumers without in-tool documentation of shorthand token ordering or override rules (`go run ./cmd/bar help` exited with `usage: bar build ...`)
- validation_targets:
  - go run ./cmd/bar help (pre-change)
  - go run ./cmd/bar help (post-change)
  - go test ./...
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-004.md#loop-004-red--helper-rerun-go-run-.-cmd-bar-help
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-004.md#loop-004-green--helper-rerun-go-run-.-cmd-bar-help
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-004.md#loop-004-green--helper-rerun-go-test-.
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/app_test.go internal/barcli/render_test.go docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-004.md`
- delta_summary: helper:diff-snapshot=3 files changed, 196 insertions(+), 8 deletions(-) — add CLI help topics/text, token ordering guidance, and adjust regression tests
- loops_remaining_forecast: 2 loops (error schema fixtures, CI regeneration hook) — medium confidence pending automation work from prior residual constraints
- residual_constraints:
  - Structured error fixtures pending (severity: medium; mitigation: add regression tests covering `conflict`/`format` JSON output once CLI exists; monitor future `_tests` Go harness; owning ADR 0065 Decision)
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Align Go CLI error schema with ADR contract and add failure fixtures (`go test ./internal/barcli` exercising `unknown_token`, `conflict`, `format` paths)
  - Behaviour: Automate prompt grammar regeneration in CI and guardrail cleanliness (`python3 -m prompts.export --output build/prompt-grammar.json` in pipeline, followed by `git diff --exit-code build/prompt-grammar.json`)

## 2026-01-08 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision — require shell completions tied to the grammar so CLI usage stays discoverable
- active_constraint: ADR 0065 did not mandate tab completion, leaving contributors without auto-suggested tokens (`git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md | rg "completion"` returned no matches)
- validation_targets:
  - git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "completion"
  - rg "completion" docs/adr/0065-portable-prompt-grammar-cli.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-005.md#loop-005-red--helper-rerun-git-show-headdocsadr0065-portable-prompt-grammar-climd--rg-completion
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-005.md#loop-005-green--helper-rerun-rg-completion-docsadr0065-portable-prompt-grammar-climd
- rollback_plan: `git restore --source=HEAD -- docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-005.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) — add tab-completion requirement tied to exported grammar
- loops_remaining_forecast: 2 loops (error schema fixtures, CI regeneration hook) — medium confidence pending automation work from prior residual constraints
- residual_constraints:
  - Structured error fixtures pending (severity: medium; mitigation: add regression tests covering `conflict`/`format` JSON output once CLI exists; monitor future `_tests` Go harness; owning ADR 0065 Decision)
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Align Go CLI error schema with ADR contract and add failure fixtures (`go test ./internal/barcli` exercising `unknown_token`, `conflict`, `format` paths)
  - Behaviour: Automate prompt grammar regeneration in CI and guardrail cleanliness (`python3 -m prompts.export --output build/prompt-grammar.json` in pipeline, followed by `git diff --exit-code build/prompt-grammar.json`)

## 2026-01-08 — loop 006
- helper_version: helper:v20251223.1
- focus: Decision — align Go CLI error schema with ADR contract by surfacing recognized/unrecognized metadata
- active_constraint: `go test ./internal/barcli` lacked regression coverage for structured error payloads, so conflict/format/unknown token paths emitted JSON without recognized context, breaking ADR 0065 Decision expectations for portable error parity
- validation_targets:
  - go test ./internal/barcli
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-006.md#loop-006-red--helper-rerun-go-test-internalbarcli
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-006.md#loop-006-green--helper-rerun-go-test-internalbarcli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/app_test.go internal/barcli/errors.go docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-006.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=3 files changed, 148 insertions(+), 31 deletions(-) — annotate CLI errors with recognized snapshots, expose recognized in JSON, and add regression tests covering conflict, format, and unknown token scenarios
- loops_remaining_forecast: 1 loop (CI regeneration hook to enforce prompt export cleanliness) — medium confidence pending pipeline alignment
- residual_constraints:
  - CI automation does not regenerate or verify `build/prompt-grammar.json` (severity: medium; mitigation: add export step to CI and guard with `git diff --exit-code build/prompt-grammar.json`; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Automate prompt grammar regeneration in CI and guardrail cleanliness (`python3 -m prompts.export --output build/prompt-grammar.json` in pipeline, followed by `git diff --exit-code build/prompt-grammar.json`)

## 2026-01-08 — loop 007
- helper_version: helper:v20251223.1
- focus: Decision — enforce prompt grammar regeneration in CI to keep the portable CLI artifact canonical
- active_constraint: `.github/workflows/test.yml` lacked any step that reran `python3 -m prompts.export --output build/prompt-grammar.json`, so CI could not surface drift between the tracked grammar JSON and the exporter; the missing guardrail let stale prompt contracts ship unnoticed
- validation_targets:
  - rg "prompt-grammar" .github/workflows/test.yml
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-007.md#loop-007-red--helper-rerun-git-show-headdgithubworkflowstestyml--rg-prompt-grammar
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-007.md#loop-007-green--helper-rerun-rg-prompt-grammar-githubworkflowstestyml
- rollback_plan: `git restore --source=HEAD -- .github/workflows/test.yml docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-007.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 6 insertions(+) — add CI steps that regenerate the prompt grammar and fail the job if the tracked JSON drifts
- loops_remaining_forecast: 0 loops — high confidence after CI guardrail lands; future slices only if exporter contract shifts
- residual_constraints:
  - Grammar exporter still depends on contributors re-running `python3 -m prompts.export --output build/prompt-grammar.json` locally after schema changes (severity: low; mitigation: rely on CI failure plus README guidance; monitor first CI run containing new guardrail)
- next_work:
  - Behaviour: Monitor the next `ci` GitHub Actions run to confirm the new regeneration step stays green (`GitHub Actions: ci` job showing “Regenerate prompt grammar artifacts” success)

## 2026-01-08 — loop 008
- helper_version: helper:v20251223.1
- focus: Decision — document prompt grammar exporter expectations for contributors
- active_constraint: Contributor docs omitted the requirement to rerun `python3 -m prompts.export --output build/prompt-grammar.json` after grammar changes, so developers could open PRs with stale artifacts despite the new CI guardrail; without guidance, local workflows stayed brittle and delayed loop closure
- validation_targets:
  - rg "prompt-grammar" CONTRIBUTING.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-008.md#loop-008-red--helper-rerun-git-show-headcontributingmd--rg-prompt-grammar
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-008.md#loop-008-green--helper-rerun-rg-prompt-grammar-contributingmd
- rollback_plan: `git restore --source=HEAD -- CONTRIBUTING.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-008.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) — add CONTRIBUTING guidance so prompt grammar edits regenerate the artifact before PRs
- loops_remaining_forecast: 0 loops — high confidence with CI and contributor docs aligned; only reopen if exporter semantics change
- residual_constraints:
  - Monitor the first CI run containing a prompt grammar change to ensure contributor guidance plus guardrail catch drifts early (severity: low; mitigation: watch `ci` workflow for prompt grammar steps)
- next_work:
  - Behaviour: Observe upcoming prompt grammar-affecting PRs to confirm contributors follow the documented exporter workflow (validation via PR checklist review)

## 2026-01-08 — loop 009
- helper_version: helper:v20251223.1
- focus: Decision — surface portable CLI usage in the README so collaborators can discover the grammar tooling without spelunking
- active_constraint: The root `readme.md` lacked any mention of `bar build`/`bar help`, leaving ADR consumers without a quickstart for the portable CLI (validated by `git show HEAD:readme.md | rg "bar help tokens"` returning no matches)
- validation_targets:
  - rg "bar help tokens" readme.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-009.md#loop-009-red--helper-rerun-git-show-headreadmemd--rg-bar-help-tokens
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-009.md#loop-009-green--helper-rerun-rg-bar-help-tokens-readmemd
- rollback_plan: `git restore --source=HEAD -- readme.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-009.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 17 insertions(+) — add README quickstart covering grammar regeneration, CLI install, and common `bar` commands
- loops_remaining_forecast: 0 loops — high confidence; README/CONTRIBUTING now align with ADR documentation contract
- residual_constraints:
  - Monitor future CLI feature loops to ensure README snippets stay synced with `bar help` examples (severity: low; mitigation: re-run README search when CLI surface changes)
- next_work:
  - Behaviour: During the next CLI enhancement, confirm README examples still reflect exported grammar commands (validation via `rg "bar build" readme.md`)

## 2026-01-08 — loop 010
- helper_version: helper:v20251223.1
- focus: Decision — add an automated guardrail keeping README portable CLI docs in sync
- active_constraint: No test enforced the presence of the README portable CLI section, so contributors could remove or drift the quickstart snippet without detection (verified by `git show HEAD^:_tests/test_readme_portable_cli.py` failing prior to this slice)
- validation_targets:
  - python3 -m unittest _tests.test_readme_portable_cli
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-010.md#loop-010-red--helper-rerun-git-show-head_tests-test-readme-portable-clipy
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-010.md#loop-010-green--helper-rerun-python3--m-unittest-_tests-test-readme-portable-cli
- rollback_plan: `git restore --source=HEAD -- _tests/test_readme_portable_cli.py docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-010.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) & 1 new test file — add README guardrail test ensuring key CLI commands stay documented
- loops_remaining_forecast: 0 loops — high confidence; CI + docs + guardrails now cover exporter, contributor guidance, and README visibility
- residual_constraints:
  - Watch for future README reorganisations that might move the CLI section; update the guardrail test accordingly (severity: low; mitigation: adjust expected snippets when layout changes)
- next_work:
  - Behaviour: When README structure changes, update `_tests.test_readme_portable_cli` expectations so the guardrail continues to reflect live documentation

## 2026-01-08 — loop 011
- helper_version: helper:v20251223.1
- focus: Decision — document the README guardrail command for developers
- active_constraint: README did not mention the `_tests.test_readme_portable_cli` guardrail, leaving contributors unaware of the fast path to verify CLI docs (`git show HEAD:readme.md | rg "python3 -m unittest _tests.test_readme_portable_cli"` returned nothing)
- validation_targets:
  - rg "python3 -m unittest _tests.test_readme_portable_cli" readme.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-011.md#loop-011-red--helper-rerun-git-show-headreadmemd--rg-python3--m-unittest-_tests-test-readme-portable-cli
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-011.md#loop-011-green--helper-rerun-rg-python3--m-unittest-_tests-test-readme-portable-cli-readmemd
- rollback_plan: `git restore --source=HEAD -- readme.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-011.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 5 insertions(+) — add README step mapping the guardrail test to the quickstart instructions
- loops_remaining_forecast: 0 loops — documentation, guardrails, and automation now cover CLI quickstart expectations end-to-end
- residual_constraints:
  - Keep README instructions synced with guardrail test updates (severity: low; mitigation: adjust both when CLI commands change)
- next_work:
  - Behaviour: When CLI snippets change, update both the README and `_tests.test_readme_portable_cli` so the quickstart and guardrail stay aligned (validation via `rg "bar help tokens" readme.md` and rerunning the guardrail test)
