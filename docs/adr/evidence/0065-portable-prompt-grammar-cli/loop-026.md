## loop-026 red | helper:rerun rg -n "INSTALL_DIR" scripts/install-bar.sh
- timestamp: 2026-01-08T06:54:22Z
- exit status: 0
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
  ```

## loop-026 green | helper:rerun rg -n "INSTALL_DIR" scripts/install-bar.sh
- timestamp: 2026-01-08T06:55:01Z
- exit status: 0
- helper:diff-snapshot=2 files changed, 18 insertions(+)
- excerpt:
  ```
  INSTALL_DIR="${INSTALL_DIR:-}"
  ```
