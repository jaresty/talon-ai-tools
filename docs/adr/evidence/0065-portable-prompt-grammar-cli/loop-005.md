## loop-005 red | helper:rerun git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "completion"
- timestamp: 2026-01-08T02:56:09Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-005 green | helper:rerun rg "completion" docs/adr/0065-portable-prompt-grammar-cli.md
- timestamp: 2026-01-08T02:58:06Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 1 insertion(+)
- excerpt:
  ```
  - Interactive shell completions ship alongside the binary: `bar completion` (and installation helpers) provide Bash/Zsh/Fish tab completion informed by the exported grammar so shorthand tokens, `key=value` overrides, and persona hints appear in the correct order. Fish support is mandatory, and completions must refresh when `build/prompt-grammar.json` changes.
  ```
