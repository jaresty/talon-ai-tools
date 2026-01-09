## loop-001 green | helper:diff-snapshot git diff --no-index --stat /dev/null docs/adr/0069-cli-preset-state-management.md
- timestamp: 2026-01-09T02:49:40Z
- exit status: 0
- helper:diff-snapshot=docs/adr/0069-cli-preset-state-management.md | 46 insertions(+)
- excerpt:
  ```
  .../adr/0069-cli-preset-state-management.md        | 46 ++++++++++++++++++++++
  1 file changed, 46 insertions(+)
  ```

## loop-001 green | helper:diff-snapshot git diff --no-index /dev/null docs/adr/0069-cli-preset-state-management.md
- timestamp: 2026-01-09T02:49:40Z
- exit status: 0
- helper:diff-snapshot=docs/adr/0069-cli-preset-state-management.md | 46 insertions(+)
- excerpt (truncated):
  ```
  - `bar preset save <name>` which copies the cached `last_build.json` payload into `~/.config/bar/presets/<slugged-name>.json` (again `0600`), redacting the prior subject before writing. Names are slugged via lowercase + `-` to keep filenames portable; collisions overwrite only when explicitly confirmed via `--force`.
  - `bar preset use <name>` to print the canonical token sequence captured by the preset so it can be piped back into `bar build` while supplying a fresh subject on demand. Presets intentionally omit the previous subject to avoid leaking sensitive content and to encourage editing before reuse. (Future work can add helpers that combine `use` + `build`.)
  - Preset files exclude the previous subject to prevent stale context leaks; `preset use` guides users to provide the subject explicitly on each invocation.
  ```
