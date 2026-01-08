## loop-001 red | helper:rerun python3 -m prompts.export --output build/prompt-grammar.json
- timestamp: 2026-01-08T00:53:48Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  ModuleNotFoundError: No module named 'prompts'
  ```

## loop-001 green | helper:rerun python3 -m pytest _tests/test_prompt_grammar_export.py
- timestamp: 2026-01-08T00:54:00Z
- exit status: 0
- helper:diff-snapshot=6 files changed, 2012 insertions(+)
- excerpt:
  ```
  _tests/test_prompt_grammar_export.py ..                                  [100%]
  ```

## loop-001 green | helper:rerun python3 -m prompts.export --output build/prompt-grammar.json
- timestamp: 2026-01-08T00:54:09Z
- exit status: 0
- helper:diff-snapshot=6 files changed, 2012 insertions(+)
- excerpt:
  ```
  Wrote prompt grammar to build/prompt-grammar.json
  ```
