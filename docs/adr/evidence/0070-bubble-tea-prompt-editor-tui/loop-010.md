## loop-010 green | helper:diff-snapshot git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
- timestamp: 2026-01-09T08:23:18Z
- exit status: 0
- helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 7 ++++---
- excerpt:
  ```
  docs/adr/0070-bubble-tea-prompt-editor-tui.md | 7 ++++---
  1 file changed, 4 insertions(+), 3 deletions(-)
  ```

## loop-010 green | helper:diff-snapshot git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- timestamp: 2026-01-09T08:23:18Z
- exit status: 0
- helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 7 ++++---
- excerpt (truncated):
  ```diff
- `go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen` provides a smoke run that the pilot group can execute to confirm preview/render behaviour before each session.
-- Capture pilot cohort notes in a shared doc after each run, treating the aggregated feedback as the go/no-go signal for expanding beyond the initial users.
+- `go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen` provides a smoke run you can execute to confirm preview/render behaviour before each session.
+- Capture personal notes after each run and use them to decide when to expand beyond the MVP.
   ...
-- Publish a lightweight pilot guide (key bindings, known limitations, quit path) so a small user group can try the TUI and share feedback.
-- Capture pilot feedback and triage follow-on work (completions refresh, telemetry, advanced layout) into the backlog after validation.
+- Publish a lightweight quickstart note (key bindings, known limitations, quit path) so you can reference the workflow quickly during trials.
+- Capture your feedback after each session and triage follow-on work (completions refresh, telemetry, advanced layout) into the backlog when the MVP holds up.
   ...
-- Prepare pilot enablement: document the MVP workflow, outline known gaps (completions, telemetry, advanced panes), and set up a feedback channel for the initial user cohort.
+- Prepare personal enablement: document the MVP workflow, outline known gaps (completions, telemetry, advanced panes), and set up a simple feedback loop for yourself.
  ```
