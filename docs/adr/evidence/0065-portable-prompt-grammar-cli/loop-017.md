## loop-017 red | helper:rerun rg --stats "bar-completion-guard" CONTRIBUTING.md
- timestamp: 2026-01-08T05:58:12Z
- exit status: 0
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  0 matches
  0 matched lines
  0 files contained matches
  ```

## loop-017 green | helper:rerun rg -n "bar-completion-guard" CONTRIBUTING.md
- timestamp: 2026-01-08T05:59:24Z
- exit status: 0
- helper:diff-snapshot=3 files changed, 20 insertions(+)
- excerpt:
  ```
  51:- One-command guardrails: `make guardrails` runs the CI guardrails and key parity tests (now including the portable CLI completion guard); `make ci-guardrails` is the CI-friendly alias without the extra parity; use these before PRs to catch catalog/list drift.
  52:- Portable prompt CLI: run `make bar-completion-guard` (or rely on the guardrails targets above) whenever you touch prompt grammar/completion code to keep the `bar completion` pytest guard green.
  ```
