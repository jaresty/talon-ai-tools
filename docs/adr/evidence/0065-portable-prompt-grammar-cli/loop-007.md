## loop-007 red | helper:rerun git show HEAD:.github/workflows/test.yml | rg "prompt-grammar"
- timestamp: 2026-01-08T03:28:52Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-007 green | helper:rerun rg "prompt-grammar" .github/workflows/test.yml
- timestamp: 2026-01-08T03:29:38Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 6 insertions(+)
- excerpt:
  ```
          run: python3 -m prompts.export --output build/prompt-grammar.json
          run: git diff --exit-code build/prompt-grammar.json
  ```
  (Manual run of the regeneration + diff pairing succeeded locally to confirm the new CI step passes.)
