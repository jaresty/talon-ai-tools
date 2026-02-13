output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

# Use .venv Python if it exists, otherwise fall back to system python3
PYTHON ?= $(shell test -f .venv/bin/python && echo .venv/bin/python || echo python3)

.venv/bin/pytest:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install pytest

bar-completion-guard: .venv/bin/pytest
	@command -v go >/dev/null 2>&1 || { echo "Go toolchain not found; install Go 1.21+ to run bar completion guard" >&2; exit 1; }
	.venv/bin/python -m pytest _tests/test_bar_completion_cli.py

bar-help-llm-test: .venv/bin/pytest
	@command -v go >/dev/null 2>&1 || { echo "Go toolchain not found; install Go 1.21+ to run bar help llm validation" >&2; exit 1; }
	.venv/bin/python -m pytest _tests/test_bar_help_llm_examples.py -v

bar-grammar-check:
	@echo "Regenerating grammar to check for drift..."
	@$(PYTHON) -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
	@cp build/prompt-grammar.json cmd/bar/testdata/grammar.json
	@echo "Checking for grammar drift..."
	@git diff --exit-code build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json cmd/bar/testdata/grammar.json || \
		(echo "ERROR: Grammar files are out of sync. Run 'make bar-grammar-update' to fix." && exit 1)
	@echo "✓ Grammar files are in sync"

bar-grammar-update:
	@echo "Regenerating grammar files..."
	@$(PYTHON) -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
	@cp build/prompt-grammar.json cmd/bar/testdata/grammar.json
	@echo "✓ Grammar files updated. Review with 'git diff' before committing."

grammar-update-all: bar-grammar-update axis-regenerate-apply
	@echo "Updating README axis modifier lines..."
	@PYTHONPATH=. $(PYTHON) scripts/tools/refresh_readme_axis_section.py
	@echo "✓ Grammar, axis config, and README all updated. Review with 'git diff' before committing."

.PHONY: output_tags test churn-scan adr010-check adr010-status axis-regenerate axis-regenerate-apply axis-regenerate-all axis-catalog-validate axis-cheatsheet axis-guardrails axis-guardrails-ci axis-guardrails-test talon-lists talon-lists-check adr0046-guardrails ci-guardrails guardrails help overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails request-history-guardrails-fast readme-axis-lines readme-axis-refresh static-prompt-docs static-prompt-refresh doc-snapshots bar-completion-guard bar-help-llm-test bar-grammar-check bar-grammar-update grammar-update-all

test:
	$(PYTHON) -m unittest discover -s tests

churn-scan:
	$(PYTHON) .claude/skills/churn-concordance-adr-helper/scripts/churn-git-log-stat.py
	$(PYTHON) .claude/skills/churn-concordance-adr-helper/scripts/line-churn-heatmap.py

adr010-check:
	$(PYTHON) -m unittest \
		tests.test_static_prompt_config \
		tests.test_axis_mapping \
		tests.test_model_pattern_gui \
		tests.test_prompt_pattern_gui \
		tests.test_static_prompt_docs \
		tests.test_model_help_gui

adr010-status:
	$(PYTHON) scripts/tools/adr010-status.py

axis-regenerate:
	mkdir -p tmp
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_axis_config.py --out tmp/axisConfig.generated.py
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_axis_config.py --markdown --out tmp/readme-axis-tokens.md
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_axis_config.py --json --out tmp/axisConfig.json
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_axis_config.py --catalog-json --out tmp/axisCatalog.json
	PYTHONPATH=. $(PYTHON) scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_static_prompt_docs.py --out tmp/static-prompt-docs.md
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_readme_axis_lists.py --out tmp/readme-axis-lists.md
	PYTHONPATH=. $(PYTHON) scripts/tools/refresh_readme_axis_section.py --out tmp/readme-axis-readme.md
	PYTHONPATH=. $(PYTHON) scripts/tools/refresh_static_prompt_readme_section.py --out tmp/static-prompt-readme.md
	PYTHONPATH=. $(PYTHON) scripts/tools/axis-catalog-validate.py --skip-list-files

axis-regenerate-apply: axis-regenerate
	@if ! cmp -s tmp/axisConfig.generated.py lib/axisConfig.py; then \
		cp tmp/axisConfig.generated.py lib/axisConfig.py; \
	fi

axis-regenerate-all:
	mkdir -p tmp
	PYTHONPATH=. $(PYTHON) scripts/tools/axis_regen_all.py

readme-axis-lines:
	mkdir -p tmp
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_readme_axis_lists.py --out tmp/readme-axis-lists.md

readme-axis-refresh:
	mkdir -p tmp
	PYTHONPATH=. README_AXIS_LISTS_DIR="$(README_AXIS_LISTS_DIR)" bash -c '\
		LISTS_ARG=""; \
		if [ -n "$$README_AXIS_LISTS_DIR" ]; then \
			LISTS_ARG="--lists-dir $$README_AXIS_LISTS_DIR"; \
		fi; \
		$(PYTHON) scripts/tools/refresh_readme_axis_section.py --out tmp/readme-axis-readme.md $$LISTS_ARG \
	'

static-prompt-docs:
	mkdir -p tmp
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_static_prompt_docs.py --out tmp/static-prompt-docs.md

static-prompt-refresh:
	mkdir -p tmp
	PYTHONPATH=. $(PYTHON) scripts/tools/refresh_static_prompt_readme_section.py --out tmp/static-prompt-readme.md

doc-snapshots: readme-axis-lines readme-axis-refresh static-prompt-docs static-prompt-refresh
	@echo "Doc snapshots generated in tmp/ (README untouched)"
	@echo "Apply manually if you want to update README sections."
axis-catalog-validate:
	$(PYTHON) scripts/tools/axis-catalog-validate.py --verbose --skip-list-files

axis-cheatsheet:
	mkdir -p tmp
	$(PYTHON) scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md

axis-guardrails: axis-regenerate-all axis-catalog-validate axis-cheatsheet
	@echo "Axis guardrails completed (catalog validation + cheat sheet; list files skipped)"
	$(PYTHON) -m pytest _tests/test_make_axis_regenerate_apply.py

axis-guardrails-ci: axis-regenerate-all axis-catalog-validate
	@echo "Axis guardrails (CI-friendly) completed (catalog validation; list files skipped)"
	$(PYTHON) -m pytest _tests/test_make_axis_regenerate_apply.py

axis-guardrails-test: axis-guardrails
	$(PYTHON) -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_generate_talon_lists.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_axis_regenerate_apply.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_make_doc_snapshots.py _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_readme_markers.py _tests/test_serialize_axis_config.py

ci-guardrails: axis-guardrails-ci overlay-guardrails overlay-lifecycle-guardrails bar-completion-guard
	$(PYTHON) -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_talon_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_make_doc_snapshots.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_axis_regenerate_apply.py _tests/test_request_gating_macros.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_readme_markers.py _tests/test_serialize_axis_config.py

guardrails: ci-guardrails overlay-guardrails overlay-lifecycle-guardrails
	@echo "Guardrails complete (CI + parity checks)"

overlay-guardrails:
	$(PYTHON) -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py

overlay-lifecycle-guardrails:
	$(PYTHON) -m pytest _tests/test_overlay_lifecycle.py

request-history-guardrails:
	@echo "request-history-guardrails is now a manual debugging helper."
	@echo "Export telemetry inside Talon (model export telemetry) and run scripts/tools/history-axis-validate.py manually if you need history summaries."
	@echo "No automated telemetry processing runs as part of this target."

request-history-guardrails-fast: request-history-guardrails
	@echo "Quick history summaries are manual-only. Inspect telemetry artifacts locally if available."
	@echo "Use scripts/tools/history-telemetry-inspect.py after exporting telemetry from Talon."




help:
	@echo "Available guardrails:"
	@echo "  make axis-catalog-validate  # catalog validation (skips Talon list files by default; use --lists-dir/--no-skip-list-files for list checks; lists-dir required when enforcing)"
	@echo "  make axis-cheatsheet        # generate axis cheat sheet from catalog"
	@echo "  make axis-guardrails        # catalog validate + cheat sheet (skips on-disk list files)"
	@echo "  make axis-regenerate-apply  # regenerate axisConfig into tmp and apply to lib/axisConfig.py (catalog-only lists by default)"
	@echo "  make axis-regenerate-all    # regenerate axisConfig/catalog/README list/cheatsheet/static prompt docs into tmp/ (runs catalog validation)"
	@echo "  make axis-guardrails-ci     # catalog validate only (fast, skips on-disk list files)"
	@echo "  make axis-guardrails-test   # regen + catalog/cheatsheet + axis SSOT regen guardrail tests"
	@echo "  make talon-lists            # optional: export axis/static prompt Talon lists locally (untracked) from catalog"
	@echo "  make talon-lists-check      # optional: drift-check local Talon lists against catalog without writing"
	@echo "  make ci-guardrails          # CI-friendly guardrails + parity tests (honors GUARDRAILS_TARGET env override)"
	@echo "  make guardrails             # run CI-friendly guardrails + parity tests"
	@echo "  make bar-completion-guard   # run portable CLI completion pytest guard"
	@echo "  make bar-help-llm-test      # validate examples in bar help llm output"
	@echo "  make overlay-lifecycle-guardrails # run overlay lifecycle guardrail tests"
	@echo "  make overlay-guardrails     # run overlay helper guardrail tests"
	@echo "  make request-history-guardrails     # optional: export history summaries (runs locally only)"
	@echo "  make request-history-guardrails-fast # optional: quick history summaries (manual telemetry access required)"
	@echo "  make readme-axis-lines      # generate catalog-derived README axis lines into tmp/readme-axis-lists.md"
	@echo "  make readme-axis-refresh    # generate catalog-derived README axis snapshot to tmp/readme-axis-readme.md (README untouched; optional README_AXIS_LISTS_DIR for list tokens)"
	@echo "  make static-prompt-docs     # generate catalog-derived static prompt docs snapshot (tmp/static-prompt-docs.md)"
	@echo "  make static-prompt-refresh  # generate catalog-derived static prompt README snapshot to tmp/static-prompt-readme.md (README untouched)"
	@echo "  make doc-snapshots          # generate all doc snapshots into tmp/ (README untouched)"

talon-lists:
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_talon_lists.py --out-dir GPT/lists

talon-lists-check:
	PYTHONPATH=. $(PYTHON) scripts/tools/generate_talon_lists.py --out-dir GPT/lists --check

adr0046-guardrails:
	make axis-guardrails-test
	$(PYTHON) -m pytest \
		_tests/test_model_destination.py \
		_tests/test_request_history_actions.py \
		_tests/test_recipe_header_lines.py \
		_tests/test_gpt_source_snapshot.py \
		_tests/test_streaming_coordinator.py \
		_tests/test_streaming_lifecycle_presenter.py \
		_tests/test_pattern_debug_coordinator.py
