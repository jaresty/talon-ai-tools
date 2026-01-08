## loop-019 red | helper:rerun rg "command -v go" Makefile
- timestamp: 2026-01-08T06:07:30Z
- exit status: 0
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches)
  ```

## loop-019 green | helper:rerun rg -n "command -v go" Makefile
- timestamp: 2026-01-08T06:08:25Z
- exit status: 0
- helper:diff-snapshot=3 files changed, 17 insertions(+)
- excerpt:
  ```
  12:	@command -v go >/dev/null 2>&1 || { echo "Go toolchain not found; install Go 1.21+ to run bar completion guard" >&2; exit 1; }
  ```
