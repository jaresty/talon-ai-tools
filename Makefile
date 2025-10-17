output_tags:
	/opt/homebrew/bin/ctags -Rx GPT

test:
	python3 -m unittest discover -s tests
