## loop-002 green | helper:rerun go run ./cmd/bar build todo gist --json
- timestamp: 2026-01-08T07:36:48Z
- exit status: 0
- helper:diff-snapshot=7 files changed, 84 insertions(+), 29 deletions(-) + new internal/barcli/embed/prompt-grammar.json
- excerpt:
  ```
  {
    "schema_version": "1.0",
    "subject": "",
    "task": "Task:\n  Format this as a todo list.",
    "constraints": [
      "Completeness (gist): The response offers a short but complete answer or summary that touches the main points once without exploring every detail."
    ],
    "axes": {
      "static": "todo",
      "completeness": "gist"
    },
    "persona": {}
  }
  ```
- context: Ran after moving `build/prompt-grammar.json` out of the workspace to confirm the embedded payload satisfies the CLI without an on-disk grammar file.
