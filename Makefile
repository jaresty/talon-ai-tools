output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

.PHONY: output_tags test churn-scan adr010-check adr010-status axis-regenerate axis-catalog-validate axis-cheatsheet axis-guardrails axis-guardrails-ci axis-guardrails-test talon-lists talon-lists-check adr0046-guardrails ci-guardrails guardrails help overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails request-history-guardrails-fast readme-axis-lines readme-axis-refresh static-prompt-docs static-prompt-refresh

test:
	python3 -m unittest discover -s tests

churn-scan:
	python3 scripts/tools/churn-git-log-stat.py
	python3 scripts/tools/line-churn-heatmap.py

adr010-check:
	python3 -m unittest \
		tests.test_static_prompt_config \
		tests.test_axis_mapping \
		tests.test_model_pattern_gui \
		tests.test_prompt_pattern_gui \
		tests.test_static_prompt_docs \
		tests.test_model_help_gui

adr010-status:
	python3 scripts/tools/adr010-status.py

axis-regenerate:
	mkdir -p tmp
	PYTHONPATH=. python3 scripts/tools/generate_axis_config.py --out tmp/axisConfig.generated.py
	PYTHONPATH=. python3 scripts/tools/generate_axis_config.py --markdown --out tmp/readme-axis-tokens.md
	PYTHONPATH=. python3 scripts/tools/generate_axis_config.py --json --out tmp/axisConfig.json
	PYTHONPATH=. python3 scripts/tools/generate_axis_config.py --catalog-json --out tmp/axisCatalog.json
	PYTHONPATH=. python3 scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md
	PYTHONPATH=. python3 scripts/tools/generate_static_prompt_docs.py --out tmp/static-prompt-docs.md
	PYTHONPATH=. python3 scripts/tools/generate_readme_axis_lists.py --out tmp/readme-axis-lists.md

readme-axis-lines:
	mkdir -p tmp
	PYTHONPATH=. python3 scripts/tools/generate_readme_axis_lists.py --out tmp/readme-axis-lists.md

readme-axis-refresh:
	PYTHONPATH=. python3 scripts/tools/refresh_readme_axis_section.py

static-prompt-docs:
	mkdir -p tmp
	PYTHONPATH=. python3 scripts/tools/generate_static_prompt_docs.py --out tmp/static-prompt-docs.md

static-prompt-refresh:
	mkdir -p tmp
	PYTHONPATH=. python3 scripts/tools/refresh_static_prompt_readme_section.py --out tmp/static-prompt-readme.md
axis-catalog-validate:
	python3 scripts/tools/axis-catalog-validate.py --verbose --skip-list-files

axis-cheatsheet:
	mkdir -p tmp
	python3 scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md

axis-guardrails: axis-catalog-validate axis-cheatsheet
	@echo "Axis guardrails completed (catalog validation + cheat sheet; list files skipped)"

axis-guardrails-ci: axis-catalog-validate
	@echo "Axis guardrails (CI-friendly) completed (catalog validation; list files skipped)"

axis-guardrails-test: axis-guardrails
	python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_generate_talon_lists.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py

ci-guardrails: axis-guardrails-ci overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails
	python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_talon_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_request_history_guardrails.py

guardrails: ci-guardrails overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails
	@echo "Guardrails complete (CI + parity checks)"

overlay-guardrails:
	python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py

overlay-lifecycle-guardrails:
	python3 -m pytest _tests/test_overlay_lifecycle.py

request-history-guardrails:
	python3 -m pytest _tests/test_request_history_actions.py

request-history-guardrails-fast:
	python3 -m pytest \
		_tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_filename_includes_provider_slug \
		_tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_includes_provider_id_in_header \
		_tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_blocks_when_current_state_in_flight \
		_tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_sequence_inflight_then_terminal

help:
	@echo "Available guardrails:"
	@echo "  make axis-catalog-validate  # catalog validation (skips Talon list files by default; use --lists-dir/--no-skip-list-files for list checks; lists-dir required when enforcing)"
	@echo "  make axis-cheatsheet        # generate axis cheat sheet from catalog"
	@echo "  make axis-guardrails        # catalog validate + cheat sheet (skips on-disk list files)"
	@echo "  make axis-guardrails-ci     # catalog validate only (fast, skips on-disk list files)"
	@echo "  make axis-guardrails-test   # full guardrail suite (catalog, cheat sheet, parity tests)"
	@echo "  make talon-lists            # optional: export axis/static prompt Talon lists locally (untracked) from catalog"
	@echo "  make talon-lists-check      # optional: drift-check local Talon lists against catalog without writing"
	@echo "  make ci-guardrails          # CI-friendly guardrails + parity tests"
	@echo "  make guardrails             # run CI-friendly guardrails + parity tests"
	@echo "  make overlay-lifecycle-guardrails # run overlay lifecycle guardrail tests"
	@echo "  scripts/tools/run_guardrails_ci.sh [--help]   # CI entrypoint (honours GUARDRAILS_TARGET, default guardrails)"
	@echo "  make overlay-guardrails     # run overlay helper guardrail tests"
	@echo "  make request-history-guardrails # run history save/resilience guardrail tests"
	@echo "  make request-history-guardrails-fast # run a fast subset of history guardrails"
	@echo "  make request-history-guardrails # run history save/resilience guardrail tests"
	@echo "  make readme-axis-lines      # generate catalog-derived README axis lines into tmp/readme-axis-lists.md"
	@echo "  make readme-axis-refresh    # rewrite README axis lines in-place from the catalog generator"
	@echo "  make static-prompt-docs     # generate catalog-derived static prompt docs snapshot (tmp/static-prompt-docs.md)"
	@echo "  make static-prompt-refresh  # rewrite README static prompt section from the catalog snapshot"

talon-lists:
	PYTHONPATH=. python3 scripts/tools/generate_talon_lists.py --out-dir GPT/lists

talon-lists-check:
	PYTHONPATH=. python3 scripts/tools/generate_talon_lists.py --out-dir GPT/lists --check

adr0046-guardrails:
	make axis-guardrails-test
	python3 -m pytest \
		_tests/test_model_destination.py \
		_tests/test_request_history_actions.py \
		_tests/test_recipe_header_lines.py \
		_tests/test_gpt_source_snapshot.py \
		_tests/test_streaming_coordinator.py \
		_tests/test_streaming_lifecycle_presenter.py \
		_tests/test_pattern_debug_coordinator.py
