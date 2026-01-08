## loop-003 red | helper:rerun git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "bar --help"
- timestamp: 2026-01-08T02:38:40Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-003 red | helper:rerun git show HEAD:docs/adr/0065-portable-prompt-grammar-cli.md \| rg "install-bar"
- timestamp: 2026-01-08T02:39:14Z
- exit status: 1
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  (no matches found)
  ```

## loop-003 green | helper:rerun rg "bar --help" docs/adr/0065-portable-prompt-grammar-cli.md
- timestamp: 2026-01-08T02:39:35Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 2 insertions(+)
- excerpt:
  ```
  - The Go CLI surfaces its own documentation. `bar --help` introduces shorthand vs. override usage along with piping/JSON examples, while `bar help tokens` renders the exported grammar (static prompts, contract axes, persona presets, and multi-word tokens) so contributors can explore the vocabulary without opening the repository.
  ```

## loop-003 green | helper:rerun rg "install-bar" docs/adr/0065-portable-prompt-grammar-cli.md
- timestamp: 2026-01-08T02:39:58Z
- exit status: 0
- helper:diff-snapshot=1 file changed, 2 insertions(+)
- excerpt:
  ```
  - Distribution includes a lightweight installer: a `scripts/install-bar.sh` helper (and README snippet) that fetches the latest release tarball, verifies the checksum, and drops the `bar` binary on the user’s `$PATH`. Contributors can alternatively run `go install github.com/talonvoice/talon-ai-tools/cmd/bar@latest` when the Go toolchain is available.
  ```
