## loop-008 red | helper:rerun git show HEAD:CONTRIBUTING.md | rg "prompt-grammar"
- timestamp: 2026-01-08T03:37:55Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-008 green | helper:rerun rg "prompt-grammar" CONTRIBUTING.md
- timestamp: 2026-01-08T03:38:01Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 1 insertion(+)
- excerpt:
  ```
  - Prompt grammar artifact: whenever you change prompts, axes, persona vocabularies, or the exporter itself, run `python3 -m prompts.export --output build/prompt-grammar.json` and commit the refreshed JSON. CI now re-runs this command and fails if the tracked file drifts, so keep the artifact clean before sending a PR.
  ```
