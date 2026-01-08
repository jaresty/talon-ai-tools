## loop-009 red | helper:rerun git show HEAD:readme.md | rg "bar help tokens"
- timestamp: 2026-01-08T03:46:15Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-009 green | helper:rerun rg "bar help tokens" readme.md
- timestamp: 2026-01-08T03:46:29Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 17 insertions(+)
- excerpt:
  ```
     bar help tokens                      # list prompts, axes, persona presets
  ```
