output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

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
	python3 scripts/tools/axis-catalog-validate.py

axis-cheatsheet:
	mkdir -p tmp
	python3 scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md

axis-guardrails: axis-catalog-validate axis-cheatsheet
	@echo "Axis guardrails completed (catalog validation + cheat sheet)"

axis-guardrails-test: axis-guardrails
	python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py

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
