## loop-020 red | helper:rerun rg --stats "Go 1.21" readme.md CONTRIBUTING.md
- timestamp: 2026-01-08T06:11:20Z
- exit status: 0
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  0 matches
  0 matched lines
  0 files contained matches
  ```

## loop-020 green | helper:rerun rg -n "Go 1.21" readme.md CONTRIBUTING.md
- timestamp: 2026-01-08T06:12:31Z
- exit status: 0
- helper:diff-snapshot=4 files changed, 27 insertions(+)
- excerpt:
  ```
  readme.md:93:5. Completion guardrail (requires Go 1.21+ and Python 3.11+):
  CONTRIBUTING.md:52:- Portable prompt CLI: run `make bar-completion-guard` (or rely on the guardrails targets above) whenever you touch prompt grammar/completion code to keep the `bar completion` pytest guard green. This target requires Go 1.21+ (`go version` should succeed) and Python 3.11+ locally.
  ```
