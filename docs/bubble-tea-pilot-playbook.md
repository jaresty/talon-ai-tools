# Bubble Tea TUI Pilot Playbook

This playbook summarizes how to exercise the new `bar tui` Bubble Tea prompt editor during the pilot rollout. It consolidates the CLI usage patterns, smoke validation harness, and troubleshooting tips gathered while implementing ADR 0070.

## Prerequisites

- Go 1.21+ installed locally (`go version` should report 1.21 or newer).
- The `bar` CLI built from this repository (`go install ./cmd/bar` or run from the repo root with `go run ./cmd/bar`).
- Terminal that supports ANSI sequences. The TUI defaults to the alt screen but can be anchored to the primary buffer when needed.

## Launching the interactive editor

Start the editor with shorthand tokens to pre-populate the token rail:

```bash
bar tui todo focus steps
```

- The editor focuses the subject input immediately. Type the subject and watch the live preview refresh automatically.
- `Ctrl+C` or `Esc` exits the program.
- Press `?` to toggle the in-app shortcut overlay without leaving the session.
- Press `Ctrl+R` to pipe the current preview into the configured shell command.
- Use `PgUp`/`PgDn` to scroll whichever viewport is focused and `Home`/`End` to jump to its start or end. When the result viewport is focused (Tab after the command field), `Ctrl+U`/`Ctrl+D` half-page scroll and `Ctrl+T` toggles a condensed preview so long outputs do not drown the status or command metadata.
- Within the token controls, use Left/Right to change categories, Up/Down to browse options, `Enter`/`Space` to toggle the highlighted token, `Delete` to remove it, and `Ctrl+Z` to undo the most recent change.

- Press `Ctrl+P` to open the token palette for faster browsing and preset resets; the status bar now prompts “copy command”, press `Enter` to copy the CLI and close the palette, and press `Ctrl+W` at any time to clear the palette filter.
- Press `?` to open the shortcut overlay; it now reminds you about the palette copy command flow so pilots can rediscover it mid-session.
- Alt screen is enabled by default so the original shell buffer is restored. If your terminal does not support alt screen or you want to capture transcripts, launch with `--no-alt-screen`.
- Point at an alternate grammar bundle with `--grammar /path/to/grammar.json` when testing staged prompt changes.
- Repeat `--env NAME` to opt specific environment variables into the subprocess allowlist. Once inside the TUI, press `Tab` until the allowlist is focused (subject → tokens → command → allowlist), use Up/Down to highlight entries, `Ctrl+E` to toggle the selection, `Ctrl+A` to re-enable all allowlisted variables, and `Ctrl+X` to clear the list if you want to run without any secrets.

## Deterministic smoke harness

Use the fixture harness to capture deterministic previews without entering the interactive event loop:

```bash
bar tui --fixture cmd/bar/testdata/tui_smoke.json --no-alt-screen
```

Fixture fields:

| Field | Purpose |
| --- | --- |
| `tokens` | Overrides CLI tokens when present; leave empty to reuse command-line tokens. |
| `subject` | Sets the subject string for the snapshot. |
| `expected_preview` / `expected_view` | Assert the rendered preview/view exactly. Set to an empty string to skip assertion. |
| `expect_view_contains` | Optional list of substrings that must appear in the rendered view. |

Snapshot runs stream the rendered view to STDOUT, assert expectations, and exit with status 0 on success. They integrate with `go test ./cmd/bar/...` via `TestTUIFixtureEmitsSnapshot` so CI stays in sync with manual runs.

## Collecting transcripts for feedback

When capturing interactive transcripts for qualitative feedback:

1. Launch with `--no-alt-screen` to keep the session in the primary buffer.
2. Pipe output to `script` or `tee` to persist the transcript. Example:
   ```bash
   script -q /tmp/bar-tui-transcript.txt bar tui todo focus --no-alt-screen
   ```
3. Attach the transcript alongside fixture results when filing pilot feedback so maintainers can compare interactive and deterministic runs.

## Troubleshooting

| Symptom | Suggested action |
| --- | --- |
| `launch tui: build prompt: ...` | Confirm the shorthand tokens or fixture tokens are valid for the selected grammar. Run `bar help tokens` if unsure. |
| Alt screen leaves the terminal blank | Re-run with `--no-alt-screen` and report the terminal type in feedback. |
| Fixture snapshot mismatch | Regenerate the expected strings by running the harness locally and copy the new preview/view into the fixture. Commit changes once verified. |
| Terminal lacks color/styling | Bubble Tea falls back to plain text when colors are unavailable; this is expected. |

## Next steps

- Keep running `go test ./cmd/bar/...` and `python3 -m pytest _tests/test_bar_completion_cli.py` before sharing snapshots or transcripts.
- Send qualitative findings (navigation quirks, layout feedback, focus behavior) with the attached transcript and fixture results to the ADR 0070 pilot thread.
