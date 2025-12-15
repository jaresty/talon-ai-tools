output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

.PHONY: output_tags test churn-scan adr010-check adr010-status axis-regenerate axis-catalog-validate axis-cheatsheet axis-guardrails axis-guardrails-ci axis-guardrails-test talon-lists talon-lists-check adr0046-guardrails ci-guardrails guardrails help

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
	python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_talon_lists.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py

ci-guardrails: axis-guardrails-ci
	python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_talon_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py

guardrails: ci-guardrails
	@echo "Guardrails complete (CI + parity checks)"

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
	@echo "  scripts/tools/run_guardrails_ci.sh [--help]   # CI entrypoint (honours GUARDRAILS_TARGET, default guardrails)"

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
