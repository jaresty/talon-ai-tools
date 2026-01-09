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
- `go test ./cmd/bar/...` exercises the `bar tui` subcommand wiring, covering grammar loading, Bubble Tea program bootstrap, and command flag handling without accessing real providers.
- `go test ./internal/barcli` keeps TUI state models equivalent to existing CLI behaviour by reusing shared build/preset fixtures.
- `go run ./cmd/bar tui --fixture testdata/grammar.json --no-alt-screen` validates interactive panes and preview rendering against the embedded grammar fixture; capture transcript snapshots for dogfooding review.
- Collect operator feedback via internal dogfooding to confirm the UI addresses identified JTBD pain points and to monitor clipboard/subprocess integrations before wide release.

## Follow-up
- Define command-line wiring for the `bar tui` subcommand inside the existing CLI and update packaging scripts/release notes accordingly.
- Draft user documentation: quickstart, key bindings, pane descriptions, troubleshooting for terminal quirks.
- Establish telemetry or logging (opt-in) to monitor usage and detect failure hotspots without leaking prompt content.
- Plan backlog items for advanced features (template libraries, diffing, multi-buffer support) once baseline TUI stabilizes.

---

## Salient Tasks
- Bootstrap a Bubble Tea program that shells around `barcli` grammar loading and exposes an initial layout with subject, token list, preview, and destination panes.
- Model state atop existing `barcli` types so token selections, subject buffer, presets/history, and validation errors stay synchronized with CLI behaviour.
- Integrate asynchronous `tea.Cmd` pipelines to call `barcli.LoadGrammar`, `barcli.Build`, clipboard/command dispatch, and background IO without blocking the TUI.
- Implement keyboard shortcuts and pane focus management using Bubbles components (`textarea`, `list`, `tabs`, `viewport`) styled with Lip Gloss for readability.
- Add Go unit tests covering model update transitions and command sequencing, plus integration smoke tests that confirm TUI output matches CLI `bar build` results.
- Extend user docs/quickstart with TUI setup, keyboard cheatsheet, preset reuse guidance, and opt-in telemetry/configuration notes.

## Anti-goals
- Do not replace or deprecate the existing non-interactive CLI; scripted workflows must remain supported and unchanged by default.
- Do not introduce Talon-specific overlays or GUI dependencies—the TUI must remain terminal-native and portable.
- Avoid embedding LLM calls or new prompt-mutation logic; the TUI should orchestrate existing `barcli` capabilities rather than redefine recipe semantics.
