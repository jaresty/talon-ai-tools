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
