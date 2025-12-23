output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

PYTHON ?= python3.11

.PHONY: output_tags test churn-scan adr010-check adr010-status axis-regenerate axis-regenerate-apply axis-regenerate-all axis-catalog-validate axis-cheatsheet axis-guardrails axis-guardrails-ci axis-guardrails-test talon-lists talon-lists-check adr0046-guardrails ci-guardrails guardrails help overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails request-history-guardrails-fast readme-axis-lines readme-axis-refresh static-prompt-docs static-prompt-refresh doc-snapshots

test:
	$(PYTHON) -m unittest discover -s tests

churn-scan:
	$(PYTHON) scripts/tools/churn-git-log-stat.py
	$(PYTHON) scripts/tools/line-churn-heatmap.py

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
	$(PYTHON) -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_generate_talon_lists.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_axis_regenerate_apply.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_make_doc_snapshots.py _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_readme_markers.py _tests/test_serialize_axis_config.py

ci-guardrails: axis-guardrails-ci overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails
	$(PYTHON) -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_static_prompt_catalog_merge_lists.py _tests/test_help_index_catalog_only.py _tests/test_talon_settings_catalog_lists.py _tests/test_generate_talon_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_generate_readme_axis_lists.py _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_make_doc_snapshots.py _tests/test_run_guardrails_ci.py _tests/test_make_help_guardrails.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_no_tracked_axis_lists.py _tests/test_gitignore_talon_lists.py _tests/test_gpt_readme_axis_lists.py _tests/test_axis_catalog_validate_help.py _tests/test_axis_catalog_validate_defaults.py _tests/test_guardrail_targets_no_talon_lists.py _tests/test_run_guardrails_ci_default_target.py _tests/test_ci_workflow_guardrails.py _tests/test_make_axis_regenerate.py _tests/test_make_axis_regenerate_apply.py _tests/test_make_request_history_guardrails.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_readme_markers.py _tests/test_serialize_axis_config.py

guardrails: ci-guardrails overlay-guardrails overlay-lifecycle-guardrails request-history-guardrails
	@echo "Guardrails complete (CI + parity checks)"

overlay-guardrails:
	$(PYTHON) -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py

overlay-lifecycle-guardrails:
	$(PYTHON) -m pytest _tests/test_overlay_lifecycle.py

request-history-guardrails:
	mkdir -p artifacts/telemetry
	@if [ -z "$$CI" ]; then \
		$(PYTHON) scripts/tools/check-telemetry-export-marker.py || exit $$?; \
	fi
	PYTHONPATH=. $(PYTHON) -m lib.telemetryExport --output-dir artifacts/telemetry --reset-gating || \
		( $(PYTHON) scripts/tools/history-axis-validate.py --summary-path artifacts/telemetry/history-validation-summary.json ; \
		  if [ ! -f artifacts/telemetry/suggestion-skip-summary.json ]; then \
		    $(PYTHON) scripts/tools/suggestion-skip-export.py --output artifacts/telemetry/suggestion-skip-summary.json --pretty ; \
		  fi ; \
		  $(PYTHON) scripts/tools/history-axis-export-telemetry.py artifacts/telemetry/history-validation-summary.json --output artifacts/telemetry/history-validation-summary.telemetry.json --top 5 --pretty --skip-summary artifacts/telemetry/suggestion-skip-summary.json )
	$(PYTHON) -m pytest _tests/test_request_history_actions.py
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json --summary-format streaming
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json --summary-format json > artifacts/telemetry/history-validation-summary.streaming.json
	printf 'Streaming gating summary (json): ' && cat artifacts/telemetry/history-validation-summary.streaming.json && printf '\n'
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json
	printf 'Suggestion skip summary (json): ' && cat artifacts/telemetry/suggestion-skip-summary.json && printf '\n'
	$(PYTHON) -c "import json; from pathlib import Path; path = Path('artifacts/telemetry/suggestion-skip-summary.json'); data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}; total = data.get('total_skipped', 0); reasons = data.get('reason_counts', []); formatted = ', '.join('{0}={1}'.format(item.get('reason'), item.get('count')) for item in reasons if isinstance(item, dict) and item.get('reason')) if isinstance(reasons, list) and reasons else 'none'; print('Suggestion skip total: {}'.format(total)); print('Suggestion skip reasons: {}'.format(formatted))"
	printf 'Telemetry summary (json): ' && cat artifacts/telemetry/history-validation-summary.telemetry.json && printf '\n'
	printf '%s\n' \
	    "import json" \
	    "from pathlib import Path" \
	    "" \
	    "telemetry_path = Path('artifacts/telemetry/history-validation-summary.telemetry.json')" \
	    "marker_path = telemetry_path.with_name('talon-export-marker.json')" \
	    "" \
	    "defaults = {'reschedule_count': 0, 'last_interval_minutes': None, 'last_reason': '', 'last_timestamp': ''}" \
	    "" \
	    "def normalize(payload):" \
	    "    scheduler = defaults.copy()" \
	    "    if not isinstance(payload, dict):" \
	    "        return scheduler" \
	    "    rc = payload.get('reschedule_count')" \
	    "    if isinstance(rc, (int, float)) and not isinstance(rc, bool):" \
	    "        scheduler['reschedule_count'] = int(rc)" \
	    "    elif isinstance(rc, str) and rc.strip():" \
	    "        try:" \
	    "            scheduler['reschedule_count'] = int(rc.strip())" \
	    "        except ValueError:" \
	    "            pass" \
	    "    li = payload.get('last_interval_minutes')" \
	    "    if li is None:" \
	    "        scheduler['last_interval_minutes'] = None" \
	    "    elif isinstance(li, (int, float)) and not isinstance(li, bool):" \
	    "        scheduler['last_interval_minutes'] = int(li)" \
	    "    elif isinstance(li, str) and li.strip():" \
	    "        try:" \
	    "            scheduler['last_interval_minutes'] = int(li.strip())" \
	    "        except ValueError:" \
	    "            scheduler['last_interval_minutes'] = None" \
	    "    lr = payload.get('last_reason')" \
	    "    if isinstance(lr, str):" \
	    "        scheduler['last_reason'] = lr.strip()" \
	    "    lt = payload.get('last_timestamp')" \
	    "    if isinstance(lt, str):" \
	    "        scheduler['last_timestamp'] = lt.strip()" \
	    "    return scheduler" \
	    "" \
	    "def load(path):" \
	    "    try:" \
	    "        return json.loads(path.read_text(encoding='utf-8'))" \
	    "    except Exception:" \
	    "        return {}" \
	    "" \
	    "payload = load(telemetry_path)" \
	    "scheduler = normalize(payload.get('scheduler'))" \
	    "if scheduler == defaults:" \
	    "    scheduler = normalize(load(marker_path).get('scheduler'))" \
	    "print('Telemetry scheduler stats: {}'.format(json.dumps(scheduler)))" \
	    "reschedules = scheduler.get('reschedule_count', 0)" \
	    "try:" \
	    "    reschedules = int(reschedules)" \
	    "except Exception:" \
	    "    reschedules = 0" \
	    "interval = scheduler.get('last_interval_minutes')" \
	    "interval_text = 'none' if interval in (None, '') else str(interval)" \
	    "reason_text = scheduler.get('last_reason')" \
	    "if not isinstance(reason_text, str) or not reason_text.strip():" \
	    "    reason_text = 'none'" \
	    "timestamp_text = scheduler.get('last_timestamp')" \
	    "if not isinstance(timestamp_text, str) or not timestamp_text.strip():" \
	    "    timestamp_text = 'none'" \
	    "print(f'- Scheduler reschedules: {reschedules}')" \
	    "print(f'- Scheduler last interval (minutes): {interval_text}')" \
	    "print(f'- Scheduler last reason: {reason_text}')" \
	    "print(f'- Scheduler last timestamp: {timestamp_text}')" \
	| $(PYTHON)


request-history-guardrails-fast:
	mkdir -p artifacts/telemetry
	@if [ -z "$$CI" ]; then \
		$(PYTHON) scripts/tools/check-telemetry-export-marker.py || exit $$?; \
	fi
	PYTHONPATH=. $(PYTHON) -m lib.telemetryExport --output-dir artifacts/telemetry || \
		( $(PYTHON) scripts/tools/history-axis-validate.py --summary-path artifacts/telemetry/history-validation-summary.json ; \
		  if [ ! -f artifacts/telemetry/suggestion-skip-summary.json ]; then \
		    $(PYTHON) scripts/tools/suggestion-skip-export.py --output artifacts/telemetry/suggestion-skip-summary.json --pretty ; \
		  fi ; \
		  $(PYTHON) scripts/tools/history-axis-export-telemetry.py artifacts/telemetry/history-validation-summary.json --output artifacts/telemetry/history-validation-summary.telemetry.json --top 5 --pretty --skip-summary artifacts/telemetry/suggestion-skip-summary.json )
	$(PYTHON) -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_filename_includes_provider_slug _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_includes_provider_id_in_header _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_blocks_when_request_in_flight _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_sequence_inflight_then_terminal
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json --summary-format streaming
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json --summary-format json > artifacts/telemetry/history-validation-summary.streaming.json
	printf 'Streaming gating summary (json): ' && cat artifacts/telemetry/history-validation-summary.streaming.json && printf '\n'
	$(PYTHON) scripts/tools/history-axis-validate.py --summarize-json artifacts/telemetry/history-validation-summary.json
	printf 'Suggestion skip summary (json): ' && cat artifacts/telemetry/suggestion-skip-summary.json && printf '\n'
	$(PYTHON) -c "import json; from pathlib import Path; path = Path('artifacts/telemetry/suggestion-skip-summary.json'); data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}; total = data.get('total_skipped', 0); reasons = data.get('reason_counts', []); formatted = ', '.join('{0}={1}'.format(item.get('reason'), item.get('count')) for item in reasons if isinstance(item, dict) and item.get('reason')) if isinstance(reasons, list) and reasons else 'none'; print('Suggestion skip total: {}'.format(total)); print('Suggestion skip reasons: {}'.format(formatted))"
	printf 'Telemetry summary (json): ' && cat artifacts/telemetry/history-validation-summary.telemetry.json && printf '\n'
	printf '%s\n' \
	    "import json" \
	    "from pathlib import Path" \
	    "" \
	    "telemetry_path = Path('artifacts/telemetry/history-validation-summary.telemetry.json')" \
	    "marker_path = telemetry_path.with_name('talon-export-marker.json')" \
	    "" \
	    "defaults = {'reschedule_count': 0, 'last_interval_minutes': None, 'last_reason': '', 'last_timestamp': ''}" \
	    "" \
	    "def normalize(payload):" \
	    "    scheduler = defaults.copy()" \
	    "    if not isinstance(payload, dict):" \
	    "        return scheduler" \
	    "    rc = payload.get('reschedule_count')" \
	    "    if isinstance(rc, (int, float)) and not isinstance(rc, bool):" \
	    "        scheduler['reschedule_count'] = int(rc)" \
	    "    elif isinstance(rc, str) and rc.strip():" \
	    "        try:" \
	    "            scheduler['reschedule_count'] = int(rc.strip())" \
	    "        except ValueError:" \
	    "            pass" \
	    "    li = payload.get('last_interval_minutes')" \
	    "    if li is None:" \
	    "        scheduler['last_interval_minutes'] = None" \
	    "    elif isinstance(li, (int, float)) and not isinstance(li, bool):" \
	    "        scheduler['last_interval_minutes'] = int(li)" \
	    "    elif isinstance(li, str) and li.strip():" \
	    "        try:" \
	    "            scheduler['last_interval_minutes'] = int(li.strip())" \
	    "        except ValueError:" \
	    "            scheduler['last_interval_minutes'] = None" \
	    "    lr = payload.get('last_reason')" \
	    "    if isinstance(lr, str):" \
	    "        scheduler['last_reason'] = lr.strip()" \
	    "    lt = payload.get('last_timestamp')" \
	    "    if isinstance(lt, str):" \
	    "        scheduler['last_timestamp'] = lt.strip()" \
	    "    return scheduler" \
	    "" \
	    "def load(path):" \
	    "    try:" \
	    "        return json.loads(path.read_text(encoding='utf-8'))" \
	    "    except Exception:" \
	    "        return {}" \
	    "" \
	    "payload = load(telemetry_path)" \
	    "scheduler = normalize(payload.get('scheduler'))" \
	    "if scheduler == defaults:" \
	    "    scheduler = normalize(load(marker_path).get('scheduler'))" \
	    "print('Telemetry scheduler stats: {}'.format(json.dumps(scheduler)))" \
	    "reschedules = scheduler.get('reschedule_count', 0)" \
	    "try:" \
	    "    reschedules = int(reschedules)" \
	    "except Exception:" \
	    "    reschedules = 0" \
	    "interval = scheduler.get('last_interval_minutes')" \
	    "interval_text = 'none' if interval in (None, '') else str(interval)" \
	    "reason_text = scheduler.get('last_reason')" \
	    "if not isinstance(reason_text, str) or not reason_text.strip():" \
	    "    reason_text = 'none'" \
	    "timestamp_text = scheduler.get('last_timestamp')" \
	    "if not isinstance(timestamp_text, str) or not timestamp_text.strip():" \
	    "    timestamp_text = 'none'" \
	    "print(f'- Scheduler reschedules: {reschedules}')" \
	    "print(f'- Scheduler last interval (minutes): {interval_text}')" \
	    "print(f'- Scheduler last reason: {reason_text}')" \
	    "print(f'- Scheduler last timestamp: {timestamp_text}')" \
	| $(PYTHON)



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
	@echo "  make ci-guardrails          # CI-friendly guardrails + parity tests"
	@echo "  make guardrails             # run CI-friendly guardrails + parity tests"
	@echo "  make overlay-lifecycle-guardrails # run overlay lifecycle guardrail tests"
	@echo "  scripts/tools/run_guardrails_ci.sh [--help]   # CI entrypoint (honours GUARDRAILS_TARGET, default guardrails)"
	@echo "  make overlay-guardrails     # run overlay helper guardrail tests"
	@echo "  make request-history-guardrails     # optional: export history summaries before resetting gating counters"
	@echo "  make request-history-guardrails-fast # optional: quick history summaries before reset"
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
