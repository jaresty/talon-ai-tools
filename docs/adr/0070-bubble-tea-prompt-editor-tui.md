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
- Let operators adjust prompt tokens, destinations, and preset selections from within the TUI itself so launching with CLI shorthand remains optional.
- Provide subject import/export affordances: operators can type subject text directly, pull it from the clipboard or a shell command, edit it in place, and push the rendered prompt to another command or the clipboard with the response surfaced in a dedicated TUI pane (and optionally reinserted into the subject field). The single-command flow must:
  - label the command input as optional and highlight when it is empty so pilots know the editor works without piping;
  - show a running-state indicator (spinner or countdown) while the command executes and allow cancellation (Esc) before timeout;
   - differentiate success and failure in the result pane with explicit cues (✔/✖, headings, truncated output controls) and include the command/exit code metadata;
   - retain follow-up instructions (for example “Press Ctrl+Y to insert stdout”) until the operator acts or dismisses them;
   - expose a shortcut to copy the current configuration’s equivalent `bar build` command to the clipboard (and surface a palette entry) so operators can drop back to scripts without re-entering tokens or subjects; confirm when the command has been copied before returning focus;
   - prompt before replacing the subject (clipboard load or stdout reinsertion), summarise what will change, and offer a one-step undo if the change is not desired;

  - provide an explicit opt-in affordance for passing environment variables to the command (for example `--env CHATGPT_API_KEY --env ORG_ID`), defaulting to no pass-through, echoing the variable names prior to execution, and warning when secrets are requested.
- Surface interactive token editing controls inline with the subject so operators can adjust voice, audience, tone, purpose, static/completeness, scope, method, form, channel, directional, and other grammar axes without leaving the session, while offering an optional `Ctrl+P` command palette accelerator that docks beside the summary strip instead of covering it. The TUI must:
  - keep the current token selections visible at all times, grouped by category with both slug and human label, including while the palette is open;
  - allow full keyboard navigation (arrow keys/Enter/Space) and offer optional mouse support without relying on hover-only affordances;
  - refresh the preview immediately after each change whether initiated inline or via the palette, while showing a transient confirmation in both contexts (for example “Scope → focus applied”);
  - provide an undo/revert affordance for the last token change and indicate when the active tokens diverge from a loaded preset, with palette entries that surface reset targets explicitly;
  - surface errors inline when a token cannot be applied and restore the previous value automatically;
  - let the palette support Tab-cycling between token categories and filtered options, chaining multiple edits before closing with `Esc`, and returning focus to the prior view predictably;
  - expose quick removal paths (focused chip `Del`/`Backspace` plus a “reset to preset” entry in the palette) so operators never depend solely on the modal interaction to clear selections.
- Provide preset management inside the TUI so operators can load, save, and remove prompt configurations without leaving the session. The workflow must:
  - keep the active preset name and divergence indicator visible in the summary strip at all times, opening a docked preset pane (via `Enter` on the summary or `Ctrl+S`) without obscuring token selections;
  - list presets with slug, label, and last-updated metadata, applying the focused entry with `Enter` while flashing the standard confirmation message and enabling `Ctrl+Z` to restore the previous state;
  - let operators save the current diverged state through an inline form (name and optional description) that confirms success without shifting focus away from the preset pane, while `Esc` cancels cleanly;
  - support deletion via `Del` on the focused preset, presenting a lightweight confirmation overlay that keeps the summary visible and leaves undo available until another change occurs;
  - return focus predictably to the prior view when the pane closes (via `Esc`) and support Tab/arrow navigation so keyboard-only pilots can chain edits quickly.
- Bake discoverability and recovery affordances into the TUI itself by:
  - exposing an in-app shortcut reference (for example press `?` to open help) wherever the subject/command or token modes shift, including palette gestures, preset save/load/delete shortcuts, and removal/reset hotkeys;
  - keeping focus changes obvious with visual highlights, not just arrow glyphs;
  - separating success and failure states in the result pane (iconography, headings, truncation with “view more” affordances) so operators can scan outcomes quickly;
  - warning before destructive subject replacements and offering an undo path for clipboard/command reinsertion;
  - persisting command guidance (for example “Press Ctrl+Y to insert stdout”) until the operator dismisses or completes the follow-up action.
- Document the workflow in README/usage docs and offer quickstart examples highlighting keyboard shortcuts, pane toggles, preset reuse, export options, and a dedicated pilot playbook for transcript capture.

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
- Preset creation, updates, and deletion introduce additional persistence and history management that require deterministic tests to assert focus behavior, confirmation messaging, and undo paths across both inline chips and the docked pane.
- Introducing clipboard and subprocess integrations expands attack surface (shell execution, sensitive text retention) and demands clear opt-outs/logging guidance; the TUI must surface command results safely and handle failures without dropping subject state.
- Environment variable pass-through must remain an explicit opt-in with visible allowlists so operators cannot leak credentials accidentally; logs and UI messaging should confirm which variables were shared each run.
- UX guardrails carry ongoing cost: we need to keep shortcut hints, status messaging, focus highlights, result-pane signaling, and token-pane ergonomics consistent so stressed operators do not misinterpret state or lose subject text unintentionally. Every loop that touches the TUI should re-validate the help overlay, focus colors, result-pane differentiation, truncation behaviour, subject-replacement confirmations, command-running indicators, and token keyboard navigation to prevent regressions.
- The optional command palette introduces extra focus states, shortcut surfaces, and inline confirmation cues that must be covered by tests to ensure the summary strip remains visible and undo feedback stays consistent.

## Validation
- `go test ./cmd/bar/...` covers the minimal `bar tui` wiring by compiling and exercising the CLI entrypoint with existing shared helpers.
- `bar tui --fixture cmd/bar/testdata/tui_smoke.json --no-alt-screen` exercises the deterministic snapshot harness and validates preview/layout output without entering the interactive loop.
- `go test ./internal/bartui/...` verifies preset load/save/delete flows, ensuring the docked pane keeps the summary visible and undo/confirmation signalling stays consistent.
- `python3 -m pytest _tests/test_bar_completion_cli.py` keeps CLI completions and installers aligned with the prompt grammar, ensuring the `bar tui` command surfaces in shell hints.

---

## Salient Tasks
- Scaffold the minimal `bar tui` entrypoint that loads grammar metadata, captures subject text, and streams preview output without blocking the CLI.
- Keep CLI parity by reusing `barcli` state helpers, covering the happy path with `go test ./cmd/bar/...`.
- Update release packaging and installer scripts so `bar tui` ships alongside existing binaries, with guardrails such as `make guardrails` verifying the distribution manifests.
- Implement interactive token editing controls inside `bar tui`, covering both inline chips and the optional `Ctrl+P` command palette accelerator so operators can modify prompt parts without restarting the CLI.
- Build preset management inside the TUI, including the docked pane, save/load/delete flows, divergence indicators, and undo/confirmation cues that keep the summary strip visible throughout.
- Add subject import/export plumbing: clipboard capture, shell command piping (prompt → command, command → subject), in-TUI result display, and optional re-insertion of subprocess output into the subject field.
- Add environment variable pass-through guardrails so commands can access opt-in credentials: surface an allowlist UI, confirm the names before execution, and cover the behaviour with `go test ./internal/bartui`.

## Anti-goals
- Do not replace or deprecate the existing non-interactive CLI; scripted workflows must remain supported and unchanged by default.
- Do not introduce Talon-specific overlays or GUI dependencies—the TUI must remain terminal-native and portable.
- Avoid embedding LLM calls or new prompt-mutation logic; the TUI should orchestrate existing `barcli` capabilities rather than redefine recipe semantics.
