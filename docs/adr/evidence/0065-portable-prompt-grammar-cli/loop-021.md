## loop-021 red | helper:rerun rg --stats "Go 1.21" docs/adr/0065-portable-prompt-grammar-cli.md
- timestamp: 2026-01-08T06:15:10Z
- exit status: 0
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  0 matches
  0 matched lines
  0 files contained matches
  ```

## loop-021 green | helper:rerun rg -n "Go 1.21" docs/adr/0065-portable-prompt-grammar-cli.md
- timestamp: 2026-01-08T06:16:01Z
- exit status: 0
- helper:diff-snapshot=3 files changed, 16 insertions(+)
- excerpt:
  ```
  docs/adr/0065-portable-prompt-grammar-cli.md:84:- Regression guard `_tests/test_bar_completion_cli.py` exercises `bar completion` and the hidden `bar __complete` surface so shell installers stay aligned with the exported grammar. Running the guard (locally or via `make bar-completion-guard`) requires Go 1.21+ in addition to Python 3.11+.
  ```
