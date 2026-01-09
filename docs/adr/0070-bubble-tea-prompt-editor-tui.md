Proposed — Bubble Tea TUI improves prompt editing ergonomics for the Go CLI (2026-01-09)

## Context
- The existing `bar` Go CLI offers scripted prompt assembly but leaves subject capture, preview, and downstream dispatch to ad-hoc shell workflows.
- Operators currently juggle token selection, subject text, and result inspection via repeated `bar build` invocations, manual piping, and external editors.
- The CLI already exposes reusable grammar logic (`internal/barcli`) yet lacks an ergonomic, stateful interface that keeps recipes, previews, and destinations in view.
- Bubble Tea provides a battle-tested TUI framework (model/update/view, async `tea.Cmd`s, component ecosystem) that can host multi-pane editors while reusing our Go domain packages.

## Decision
- Build a Bubble Tea-based prompt editing TUI that shells around the existing CLI logic, exposing subject capture, token management, live preview, and output dispatch in one workspace.
- Model state around our `barcli` types: grammar metadata, token selections, subject buffer, preset/history entries, validation state, and target destination (clipboard, subprocess, file, etc.).
- Use Bubbles components (`textarea`, `textinput`, `list`, `tabs`, `viewport`) for editing panes, template browsing, and previews; style them with Lip Gloss to keep layout readable.
- Leverage `tea.Cmd` pipelines to invoke `barcli.LoadGrammar`, `barcli.Build`, downstream clipboard/subprocess actions, and any background IO without blocking the UI thread.
- Ship the TUI as an optional `bar tui` subcommand within the existing CLI binary so it coexists with the current surface while reusing shared configuration/preset directories.
- Document the workflow in README/usage docs and offer quickstart examples highlighting keyboard shortcuts, pane toggles, preset reuse, and export options.

## Rationale
- Bubble Tea’s Elm-like architecture matches our need for deterministic state transitions and composable async commands (per Bubble Tea docs and tutorials).
- The component ecosystem keeps us from rewriting inputs, lists, or viewports; we can focus on wiring `barcli` outputs into ergonomic panes.
- Reusing `internal/barcli` avoids duplicating grammar parsing/rendering logic and keeps parity with existing CLI behavior and tests.
- Providing an interactive editor addresses the JTBD gaps (compose prompt quickly, apply subject context, dispatch downstream, reuse history, validate structure) identified during CLI analysis.
- Keeping the feature optional preserves current scriptable workflows while offering a richer interface for operators who prefer in-terminal editing.

## Consequences
- We must maintain a Bubble Tea program alongside the CLI, including shared release packaging and binary distribution.
- Additional keyboard/mouse handling, focus management, and layout logic introduces new complexity that will require regression coverage.
- We take on UI accessibility and terminal compatibility considerations (alt screen, mouse modes, bracketed paste) that the pure CLI previously avoided.
- The TUI will need runtime coordination with preset/state files; we must guard against concurrent writes or stale caches when both surfaces run.
- Introducing clipboard and subprocess integrations expands attack surface (shell execution, sensitive text retention) and demands clear opt-outs/logging guidance.

## Validation
- `go test ./cmd/bar/...` covers the minimal `bar tui` wiring by compiling and exercising the CLI entrypoint with existing shared helpers.
- `go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen` provides a smoke run that the pilot group can execute to confirm preview/render behaviour before each session.
- Capture pilot cohort notes in a shared doc after each run, treating the aggregated feedback as the go/no-go signal for expanding beyond the initial users.

## Follow-up
- Deliver an MVP `bar tui` subcommand that reuses existing `cmd/bar` and `internal/barcli` packages, loads the grammar, accepts subject input, and renders the preview (validation via `go test ./cmd/bar/...` and a smoke run of `go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen`).
- Publish a lightweight pilot guide (key bindings, known limitations, quit path) so a small user group can try the TUI and share feedback.
- Capture pilot feedback and triage follow-on work (completions refresh, telemetry, advanced layout) into the backlog after validation.

---

## Salient Tasks
- Scaffold the minimal `bar tui` entrypoint that loads grammar metadata, captures subject text, and streams preview output without blocking the CLI.
- Keep CLI parity by reusing `barcli` state helpers, covering the happy path with `go test ./cmd/bar/...`, and adding a smoke script that runs `go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen`.
- Prepare pilot enablement: document the MVP workflow, outline known gaps (completions, telemetry, advanced panes), and set up a feedback channel for the initial user cohort.

## Anti-goals
- Do not replace or deprecate the existing non-interactive CLI; scripted workflows must remain supported and unchanged by default.
- Do not introduce Talon-specific overlays or GUI dependencies—the TUI must remain terminal-native and portable.
- Avoid embedding LLM calls or new prompt-mutation logic; the TUI should orchestrate existing `barcli` capabilities rather than redefine recipe semantics.
