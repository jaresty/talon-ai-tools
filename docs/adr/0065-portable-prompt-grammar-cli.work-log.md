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

## 2026-01-08 — loop 012
- helper_version: helper:v20251223.1
- focus: Decision — ship grammar-driven completion scripts for the portable CLI
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Restores ADR 0065 completion behaviour so shells stay grammar-aligned |
  | Probability | High | Implementing the documented CLI surfaces deterministically resolves the undefined references |
  | Time Sensitivity | Medium | Deferral would keep contributors without completions until the next release |
  | Uncertainty note | Low | Grammar contract already specified in ADR 0065 |
- active_constraint: `go run ./cmd/bar completion fish` failed with undefined references (`runCompletionEngine`, `GenerateCompletionScript`), leaving ADR 0065’s completion requirement unmet because the CLI exposed no grammar-driven completion generator.
- validation_targets:
  - go run ./cmd/bar completion fish
  - go run ./cmd/bar __complete bash 1 bar
  - go test ./internal/barcli
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-012.md#loop-012-red--helper-rerun-go-run-cmdbar-completion-fish
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-012.md#loop-012-green--helper-rerun-go-run-cmdbar-completion-fish
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-012.md#loop-012-green--helper-rerun-go-run-cmdbar-__complete-bash-1-bar
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-012.md#loop-012-green--helper-rerun-go-test-internalbarcli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-012.md`
- delta_summary: helper:diff-snapshot=6 files changed, 818 insertions(+), 3 deletions(-) — add grammar-driven completion engine, shell installers, regression tests, and update ADR/work-log evidence
- loops_remaining_forecast: 0 loops — high confidence with completion scripts shipping and coverage in place
- residual_constraints:
  - Completion scripts depend on the exported grammar staying fresh (severity: low; mitigation: continue running `go test ./internal/barcli` after each `python3 -m prompts.export` regen; monitor CI prompt grammar step; owning ADR 0065 Decision)
- next_work:
  - Behaviour: When the grammar schema changes, refresh completion fixtures and rerun `go test ./internal/barcli` to confirm shell suggestions stay aligned (validation via `go test ./internal/barcli`)

## 2026-01-08 — loop 013
- helper_version: helper:v20251223.1
- focus: Decision — guard CLI completions with pytest coverage so ADR 0065 behaviour stays observable
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Prevents silent regression of `bar completion` behaviour mandated by ADR 0065 |
  | Probability | High | Focused pytest invoking the CLI will fail if completions drift |
  | Time Sensitivity | Medium | Without a guardrail regressions could linger until manual discovery |
  | Uncertainty note | Low | Behaviour already specified by ADR 0065 Decision |
- active_constraint: No automated test exercised `bar completion`/`bar __complete`, so CLI completions could regress unnoticed (`rg --stats "bar completion" _tests` returned zero matches).
- validation_targets:
  - python3 -m pytest _tests/test_bar_completion_cli.py
  - .venv/bin/python -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-013.md#loop-013-red--helper-rerun-python3--m-pytest-_tests-test_bar_completion_clipy
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-013.md#loop-013-green--helper-rerun-venvbinpython--m-pytest-_tests-test_bar_completion_clipy
- rollback_plan: `git restore --source=HEAD -- _tests/test_bar_completion_cli.py docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-013.md`
- delta_summary: helper:diff-snapshot=4 files changed, 99 insertions(+) — add pytest guard, update ADR guidance, capture loop evidence
- loops_remaining_forecast: 0 loops — high confidence with automated guard in place (monitor future schema changes)
- residual_constraints:
  - Virtualenv usage is manual; contributors must run `.venv/bin/python -m pytest _tests/test_bar_completion_cli.py` when validating completions (severity: low; mitigation: document command in README if adoption grows; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: Monitor future grammar updates to ensure completion guard stays green and adjust test fixtures when tokens change (validation via `.venv/bin/python -m pytest _tests/test_bar_completion_cli.py`)

## 2026-01-08 — loop 014
- helper_version: helper:v20251223.1
- focus: Decision — document completion guard command so contributors can run the new pytest slice
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Documentation keeps the new completion guard usable across releases |
  | Probability | High | Adding README instructions directly addresses the missing guidance |
  | Time Sensitivity | Medium | Without docs, contributors may skip the guard until reminded in reviews |
  | Uncertainty note | Low | Behaviour already validated by loop 013 |
- active_constraint: README lacked instructions for running `.venv/bin/python -m pytest _tests/test_bar_completion_cli.py`, so the completion guard added in loop 013 was undiscoverable (`rg --stats "\.venv/bin/python -m pytest _tests/test_bar_completion_cli.py" readme.md` returned no matches).
- validation_targets:
  - rg --stats "\.venv/bin/python -m pytest _tests/test_bar_completion_cli.py" readme.md
  - rg -n "\.venv/bin/python -m pytest _tests/test_bar_completion_cli.py" readme.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-014.md#loop-014-red--helper-rerun-rg---stats-venvbinpython--m-pytest-_tests-test_bar_completion_clipy-readmemd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-014.md#loop-014-green--helper-rerun-rg--n-venvbinpython--m-pytest-_tests-test_bar_completion_clipy-readmemd
- rollback_plan: `git restore --source=HEAD -- readme.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-014.md`
- delta_summary: helper:diff-snapshot=3 files changed, 18 insertions(+) — document completion guard command and record loop evidence
- loops_remaining_forecast: 0 loops — documentation, guard, and evidence now align; reopen if guard workflow changes
- residual_constraints:
  - Virtualenv instructions remain lightweight; monitor for requests to standardise dependency installation (severity: low; mitigation: add CONTRIBUTING note if repeated questions arise; owning ADR 0065 Consequences)
- next_work:
  - Behaviour: When tooling guidance changes (e.g., new guard or dependency), refresh README and guardrail docs accordingly (validation via `rg -n "bar completion" readme.md`)

## 2026-01-08 — loop 015
- helper_version: helper:v20251223.1
- focus: Decision — add a `make bar-completion-guard` helper so the completion pytest runs consistently
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Streamlines running the ADR-mandated completion guard for every contributor |
  | Probability | High | Make target automates venv setup and pytest invocation |
  | Time Sensitivity | Medium | Without automation, guardrail adoption depends on manual steps |
  | Uncertainty note | Low | Guard behaviour already validated in loops 013–014 |
- active_constraint: Running the completion guard required manual venv creation and pip install, increasing friction (`make bar-completion-guard` failed with “No rule to make target”).
- validation_targets:
  - make bar-completion-guard
  - make bar-completion-guard
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-015.md#loop-015-red--helper-rerun-make-bar-completion-guard
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-015.md#loop-015-green--helper-rerun-make-bar-completion-guard
- rollback_plan: `git restore --source=HEAD -- Makefile .gitignore readme.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-015.md`
- delta_summary: helper:diff-snapshot=5 files changed, 43 insertions(+) — add make target, ignore venv, update README guidance, record evidence
- loops_remaining_forecast: 0 loops — automation in place; reopen if guard target needs CI integration
- residual_constraints:
  - `.venv` may accumulate packages; periodically recreate if dependencies change (severity: low; mitigation: rerun `make bar-completion-guard` to refresh)
- next_work:
  - Behaviour: Consider CI integration for the completion guard if future loops require automated enforcement (validation via GitHub Actions update)

## 2026-01-08 — loop 016
- helper_version: helper:v20251223.1
- focus: Decision — integrate the completion guard with `make ci-guardrails` / `make guardrails`
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Ensures ADR 0065 completion behaviour runs in the standard guardrail suites |
  | Probability | High | Wiring the make target guarantees execution in local/CI guardrails |
  | Time Sensitivity | Medium | Without integration, guardrails would omit the completion slice until run manually |
  | Uncertainty note | Low | Guard command already validated in loops 013–015 |
- active_constraint: `bar-completion-guard` was not part of `make ci-guardrails`, so automated guardrails skipped the portable CLI completion pytest (`git show HEAD:Makefile | rg -n "ci-guardrails"` showed no dependency on the target).
- validation_targets:
  - git show HEAD:Makefile | rg -n "ci-guardrails"
  - make -n ci-guardrails
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-016.md#loop-016-red--helper-rerun-git-show-headmakefile--rg--n-ci-guardrails
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-016.md#loop-016-green--helper-rerun-make--n-ci-guardrails
- rollback_plan: `git restore --source=HEAD -- Makefile readme.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-016.md`
- delta_summary: helper:diff-snapshot=4 files changed, 26 insertions(+), 0 deletions — add guardrails dependency, update help/README, record loop evidence
- loops_remaining_forecast: 0 loops — completion guard now part of guardrails; reopen only if CI wiring changes
- residual_constraints:
  - Ensure CI environments have Go available for `go run ./cmd/bar`; monitor for failures and update guard if build tags change (severity: low; mitigation: revalidate guard execution in CI)
- next_work:
  - Behaviour: If guard becomes too heavy for regular guardrails, consider adding a focused target for smoke tests (validation via `make bar-completion-guard`)

## 2026-01-08 — loop 017
- helper_version: helper:v20251223.1
- focus: Decision — document the completion guard in CONTRIBUTING so contributors run it proactively
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Keeps ADR 0065 guard observable for new contributors |
  | Probability | High | Updating CONTRIBUTING ensures docs mention the guardrail workflow |
  | Time Sensitivity | Medium | Without docs, contributors may miss the guard until review |
  | Uncertainty note | Low | Guard already integrated with make targets |
- active_constraint: CONTRIBUTING’s guardrail section omitted the new `bar-completion-guard`, so contributor docs lacked instructions (`rg --stats "bar-completion-guard" CONTRIBUTING.md` returned 0 matches).
- validation_targets:
  - rg --stats "bar-completion-guard" CONTRIBUTING.md
  - rg -n "bar-completion-guard" CONTRIBUTING.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-017.md#loop-017-red--helper-rerun-rg---stats-bar-completion-guard-contributingmd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-017.md#loop-017-green--helper-rerun-rg--n-bar-completion-guard-contributingmd
- rollback_plan: `git restore --source=HEAD -- CONTRIBUTING.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-017.md`
- delta_summary: helper:diff-snapshot=3 files changed, 20 insertions(+) — document guard in CONTRIBUTING, update work-log, capture evidence
- loops_remaining_forecast: 0 loops — documentation parity achieved; reopen if further guardrail workflows change
- residual_constraints:
  - None newly identified; guard messaging now present across README and CONTRIBUTING
- next_work:
  - Behaviour: Revisit README/CONTRIBUTING when guard automation evolves (validation via `rg -n "bar-completion-guard" readme.md CONTRIBUTING.md`)

## 2026-01-08 — loop 018
- helper_version: helper:v20251223.1
- focus: Decision — ensure CI installs Go so the completion guard runs in automation
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Without Go, `make ci-guardrails` fails to exercise ADR 0065 behaviours |
  | Probability | High | Adding `actions/setup-go` deterministically installs a working toolchain |
  | Time Sensitivity | Medium | CI would miss regressions until manual guardrails run locally |
  | Uncertainty note | Low | Guard already validated locally |
- active_constraint: GitHub Actions workflow lacked a Go toolchain, so `make ci-guardrails` could not run the completion guard (`git show HEAD:.github/workflows/test.yml | rg --stats "setup-go"` produced zero matches).
- validation_targets:
  - git show HEAD:.github/workflows/test.yml | rg --stats "setup-go"
  - rg -n "setup-go" .github/workflows/test.yml
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-018.md#loop-018-red--helper-rerun-git-show-headgithubworkflowstestyml--rg---stats-setup-go
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-018.md#loop-018-green--helper-rerun-rg--n-setup-go-githubworkflowstestyml
- rollback_plan: `git restore --source=HEAD -- .github/workflows/test.yml docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-018.md`
- delta_summary: helper:diff-snapshot=3 files changed, 18 insertions(+) — add Go setup to CI workflow, log loop evidence
- loops_remaining_forecast: 0 loops — CI now provisions Go before running guardrails; reopen if workflow fails on other runners
- residual_constraints:
  - Monitor CI runtimes; if Go setup slows guardrails significantly, evaluate caching or prebuilt binaries
- next_work:
  - Behaviour: Revisit workflows if Go version requirements change (validation via review of `.github/workflows/test.yml`)

## 2026-01-08 — loop 019
- helper_version: helper:v20251223.1
- focus: Decision — fail fast when Go is missing before running the completion guard
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Provides actionable feedback instead of opaque pytest/go errors |
  | Probability | High | `command -v go` guard ensures clear messaging |
  | Time Sensitivity | Low | Improves DX but does not block automation |
  | Uncertainty note | Low | Behaviour deterministic |
- active_constraint: `make bar-completion-guard` surfaced opaque failures when Go was absent (no preflight check; `rg "command -v go" Makefile` yielded no matches).
- validation_targets:
  - rg "command -v go" Makefile
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-019.md#loop-019-red--helper-rerun-rg-command--v-go-makefile
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-019.md#loop-019-green--helper-rerun-rg--n-command--v-go-makefile
- rollback_plan: `git restore --source=HEAD -- Makefile docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-019.md`
- delta_summary: helper:diff-snapshot=3 files changed, 17 insertions(+) — add Go preflight check and record evidence
- loops_remaining_forecast: 0 loops — guard now reports missing Go clearly
- residual_constraints:
  - If alternative Go locations emerge, consider parameterising target (severity: low)
- next_work:
  - Behaviour: Monitor guard output for other common failures and extend preflight checks as needed (validation via `make bar-completion-guard`)

## 2026-01-08 — loop 020
- helper_version: helper:v20251223.1
- focus: Decision — document Go toolchain prerequisite for completion guard workflows
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Prevents confusing guardrail failures on contributor machines |
  | Probability | High | Docs explicitly call out Go 1.21+ requirement |
  | Time Sensitivity | Low | Documentation improvement |
  | Uncertainty note | Low | Behaviour deterministic |
- active_constraint: README/CONTRIBUTING lacked Go prerequisite guidance (`rg --stats "Go 1.21" readme.md CONTRIBUTING.md` returned no matches), leaving contributors unaware that the guard relies on Go.
- validation_targets:
  - rg --stats "Go 1.21" readme.md CONTRIBUTING.md
  - rg -n "Go 1.21" readme.md CONTRIBUTING.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-020.md#loop-020-red--helper-rerun-rg---stats-go-121-readmemd-contributingmd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-020.md#loop-020-green--helper-rerun-rg--n-go-121-readmemd-contributingmd
- rollback_plan: `git restore --source=HEAD -- readme.md CONTRIBUTING.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-020.md`
- delta_summary: helper:diff-snapshot=4 files changed, 27 insertions(+) — add Go requirement messaging and record documentation evidence
- loops_remaining_forecast: 0 loops — guard prerequisites now documented across README/CONTRIBUTING
- residual_constraints:
  - None additional; monitor for other dependency questions from contributors
- next_work:
  - Behaviour: Update docs again if guard starts requiring additional tooling (validation via docs search)

## 2026-01-08 — loop 023
- helper_version: helper:v20251223.1
- focus: Status transition — mark ADR 0065 as Accepted
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Signals completion to readers and automation |
  | Probability | High | Status flip straightforward |
  | Time Sensitivity | Low | Administrative wrap-up |
  | Uncertainty note | Low | All behaviours already closed |
- active_constraint: ADR status remained `Proposed` despite guardrails and documentation being complete (`rg -n "^Proposed$" docs/adr/0065-portable-prompt-grammar-cli.md` located the stale status line).
- validation_targets:
  - rg -n "^Proposed$" docs/adr/0065-portable-prompt-grammar-cli.md
  - rg -n "^Accepted$" docs/adr/0065-portable-prompt-grammar-cli.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-023.md#loop-023-red--helper-rerun-rg--n-proposed-docsadr0065-portable-prompt-grammar-climd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-023.md#loop-023-green--helper-rerun-rg--n-accepted-docsadr0065-portable-prompt-grammar-climd
- rollback_plan: `git restore --source=HEAD -- docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-023.md`
- delta_summary: helper:diff-snapshot=3 files changed, 14 insertions(+), 1 deletion(-) — set status to Accepted and log evidence
- loops_remaining_forecast: 0 loops — ADR officially complete
- residual_constraints:
  - None
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 025
- helper_version: helper:v20251223.1
- focus: Release automation — publish bar binaries for install script
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Enables install-bar.sh to succeed by providing release assets |
  | Probability | High | CI workflow builds binaries for supported targets |
  | Time Sensitivity | Medium | Without releases the installer fails |
  | Uncertainty note | Low | Build steps deterministic |
- active_constraint: Repository had no workflow producing release tarballs for the bar CLI and the README remote install snippet pointed at a nonexistent URL (`ls .github/workflows` contained only test/pyright pipelines and `rg -n "raw.githubusercontent.com/talonvoice" readme.md` located the stale path).
- validation_targets:
  - ls .github/workflows
  - cat .github/workflows/release-bar.yml
  - rg -n "raw.githubusercontent.com/jaresty/talon-ai-tools/main/scripts/install-bar.sh" readme.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-025.md#loop-025-red--helper-rerun-ls-githubworkflows
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-025.md#loop-025-green--helper-rerun-cat-githubworkflowsrelease-baryml
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-025.md#loop-025-green--helper-rerun-rg--n-rawgithubusercontentjaresty-talon-ai-toolsmain-scriptsinstall-barsh-readmemd
- rollback_plan: `git restore --source=HEAD -- .github/workflows/release-bar.yml docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-025.md`
- delta_summary: helper:diff-snapshot=2 files changed, 47 insertions(+) — add release workflow and log evidence
- loops_remaining_forecast: 0 loops — releases now automated when tags pushed
- residual_constraints:
  - Ensure tags follow `bar-v*` pattern and publish release notes as needed
- next_work:
  - Behaviour: Trigger release on next version tag (validation via GitHub release page)

## 2026-01-08 — loop 026
- helper_version: helper:v20251223.1
- focus: Installer ergonomics — auto-detect macOS install directory
...
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 027
- helper_version: helper:v20251223.1
- focus: Installer verification — support shasum checksum tool
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Lets macOS users verify downloads without sha256sum |
  | Probability | High | Script now handles shasum syntax |
  | Time Sensitivity | Low | Quality-of-life improvement |
  | Uncertainty note | Low | Deterministic change |
- active_constraint: `install-bar.sh` piped checksum data into `sha256sum` options (`--status --ignore-missing`) that don’t exist on `shasum`, causing failures on macOS.
- validation_targets:
  - rg -n "compute_checksum" scripts/install-bar.sh
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md#loop-027-red--helper-rerun-rg--n-compute_checksum-scriptsinstall-barsh
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md#loop-027-green--helper-rerun-rg--n-compute_checksum-scriptsinstall-barsh
- rollback_plan: `git restore --source=HEAD -- scripts/install-bar.sh docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md`
- delta_summary: helper:diff-snapshot=2 files changed, 22 insertions(+), 4 deletions(-) — add shasum-compatible verification and log evidence
- loops_remaining_forecast: 0 loops — install script now supports both checksum tools
- residual_constraints:
  - None
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 026
- helper_version: helper:v20251223.1
- focus: Installer ergonomics — auto-detect macOS install directory
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Ensures Apple silicon users get `bar` on PATH without manual tweaks |
  | Probability | High | Script now prefers /opt/homebrew/bin when available |
  | Time Sensitivity | Low | Quality-of-life improvement |
  | Uncertainty note | Low | Detection is deterministic |
- active_constraint: `scripts/install-bar.sh` defaulted to `/usr/local/bin`, which is not on PATH for Homebrew-on-Apple-silicon installs; README guidance relied on the script.
- validation_targets:
  - rg -n "INSTALL_DIR" scripts/install-bar.sh
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-026.md#loop-026-red--helper-rerun-rg--n-install_dir-scriptsinstall-barsh
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-026.md#loop-026-green--helper-rerun-rg--n-install_dir-scriptsinstall-barsh
- rollback_plan: `git restore --source=HEAD -- scripts/install-bar.sh docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-026.md`
- delta_summary: helper:diff-snapshot=2 files changed, 18 insertions(+) — auto-detect install target and log evidence
- loops_remaining_forecast: 0 loops — installer now selects sensible default on macOS
- residual_constraints:
  - None
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 027
- helper_version: helper:v20251223.1
- focus: Installer verification — support shasum checksum tool
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Lets macOS users verify downloads without sha256sum |
  | Probability | High | Script now handles shasum syntax |
  | Time Sensitivity | Low | Quality-of-life improvement |
  | Uncertainty note | Low | Deterministic change |
- active_constraint: `install-bar.sh` piped checksum data into `sha256sum` options (`--status --ignore-missing`) that do not exist on `shasum`, causing failures on macOS during verification.
- validation_targets:
  - rg -n "verify_checksum" scripts/install-bar.sh
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md#loop-027-red--helper-rerun-rg--n-verify_checksum-scriptsinstall-barsh
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md#loop-027-green--helper-rerun-rg--n-verify_checksum-scriptsinstall-barsh
- rollback_plan: `git restore --source=HEAD -- scripts/install-bar.sh docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-027.md`
- delta_summary: helper:diff-snapshot=2 files changed, 22 insertions(+), 4 deletions(-) — add shasum-compatible verification and log evidence
- loops_remaining_forecast: 0 loops — install script now supports both checksum tools
- residual_constraints:
  - None
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 025
- helper_version: helper:v20251223.1
- focus: Docs — clarify remote installer command for non-clone setups
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Helps users without a local checkout install the CLI |
  | Probability | High | README snippet provides direct copy-paste command |
  | Time Sensitivity | Low | Documentation improvement |
  | Uncertainty note | Low | Script already in repo |
- active_constraint: README mentioned `scripts/install-bar.sh` but didn’t show how to fetch it remotely (`rg --stats "install-bar.sh" readme.md` only referenced the helper path).
- validation_targets:
  - rg --stats "install-bar.sh" readme.md
  - rg -n "curl -fsSL" readme.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-024.md#loop-024-red--helper-rerun-rg---stats-install-barsh-readmemd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-024.md#loop-024-green--helper-rerun-rg--n-curl--fssl-readmemd
- rollback_plan: `git restore --source=HEAD -- readme.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-024.md`
- delta_summary: helper:diff-snapshot=3 files changed, 18 insertions(+) — add curl command to README and log evidence
- loops_remaining_forecast: 0 loops — docs now provide clone-free install path
- residual_constraints:
  - Keep installer command updated if release hosting changes
- next_work:
  - Behaviour: None

## 2026-01-08 — loop 023
- helper_version: helper:v20251223.1

- focus: Completion summary — ADR 0065 guardrails and documentation alignment
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Confirms ADR closure and provides auditors a wrap-up pointer |
  | Probability | High | Work-log entry finalises the loop history |
  | Time Sensitivity | Low | Administrative wrap-up |
  | Uncertainty note | Low | All behaviours already green |
- active_constraint: Work-log lacked an explicit completion summary tying guardrails, docs, and CI integration together (`rg --stats "Completion summary" docs/adr/0065-portable-prompt-grammar-cli.work-log.md` returned no matches).
- validation_targets:
  - rg --stats "Completion summary" docs/adr/0065-portable-prompt-grammar-cli.work-log.md
  - rg -n "Completion summary" docs/adr/0065-portable-prompt-grammar-cli.work-log.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-022.md#loop-022-red--helper-rerun-rg---stats-completion-summary-docsadr0065-portable-prompt-grammar-cliworldogmd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-022.md#loop-022-green--helper-rerun-rg--n-completion-summary-docsadr0065-portable-prompt-grammar-cliworldogmd
- rollback_plan: `git restore --source=HEAD -- docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-022.md`
- delta_summary: helper:diff-snapshot=2 files changed, 14 insertions(+) — add completion summary entry and evidence pointer
- loops_remaining_forecast: 0 loops — ADR 0065 guardrails, docs, CI, and installers now aligned
- residual_constraints:
  - None — monitor future ADRs for new behaviours
- next_work:
  - Behaviour: None — ADR considered complete pending new decisions

## 2026-01-08 — loop 021
- helper_version: helper:v20251223.1
- focus: Decision — document Go prerequisite directly in ADR 0065
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Keeps ADR as single source of truth for guardrail requirements |
  | Probability | High | Simple doc edit ensures future loops reference the requirement |
  | Time Sensitivity | Low | Alignment/documentation improvement |
  | Uncertainty note | Low | No ambiguity |
- active_constraint: ADR 0065 did not mention the Go toolchain requirement, risking drift between decision and guardrail (`rg --stats "Go 1.21" docs/adr/0065-portable-prompt-grammar-cli.md` returned 0).
- validation_targets:
  - rg --stats "Go 1.21" docs/adr/0065-portable-prompt-grammar-cli.md
  - rg -n "Go 1.21" docs/adr/0065-portable-prompt-grammar-cli.md
- evidence:
  - red: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-021.md#loop-021-red--helper-rerun-rg---stats-go-121-docsadr0065-portable-prompt-grammar-climd
  - green: docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-021.md#loop-021-green--helper-rerun-rg--n-go-121-docsadr0065-portable-prompt-grammar-climd
- rollback_plan: `git restore --source=HEAD -- docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0065-portable-prompt-grammar-cli.work-log.md docs/adr/evidence/0065-portable-prompt-grammar-cli/loop-021.md`
- delta_summary: helper:diff-snapshot=3 files changed, 16 insertions(+) — add Go prerequisite note to ADR and record evidence
- loops_remaining_forecast: 0 loops — ADR decision/docs now consistent
- residual_constraints:
  - None additional identified
- next_work:
  - Behaviour: Revisit ADR if guard command surface changes (validation via docs search)
