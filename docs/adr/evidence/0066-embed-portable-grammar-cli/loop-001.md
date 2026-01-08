## loop-001 red | helper:rerun go run ./cmd/bar help tokens --grammar nonexistent.json
- timestamp: 2026-01-08T07:14:56Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  error: open grammar: open nonexistent.json: no such file or directory
  exit status 1
  ```
