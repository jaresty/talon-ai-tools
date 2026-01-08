## loop-011 red | helper:rerun git show HEAD:readme.md | rg "python3 -m unittest _tests.test_readme_portable_cli"
- timestamp: 2026-01-08T04:26:58Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-011 green | helper:rerun rg "python3 -m unittest _tests.test_readme_portable_cli" readme.md
- timestamp: 2026-01-08T04:27:10Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 5 insertions(+)
- excerpt:
  ```
     python3 -m unittest _tests.test_readme_portable_cli
  ```
- additional_notes: Guardrail test executed via `python3 -m unittest _tests.test_readme_portable_cli` at 2026-01-08T04:27:43Z to confirm README instructions stay accurate.
