# ADR-0167: TUI Harness Mode for LLM-Driven UX Exploration

**Status**: Proposed
**Date**: 2026-03-15

---

## Context

The `bar tui2` terminal interface (Bubble Tea) can only be driven by a human with a PTY. There
is no way for an LLM or automated test to navigate the TUI, observe what is shown, and surface
UX friction — without either: (a) a PTY + ANSI-stripping pipeline, which is fragile and loses
semantic structure, or (b) a purpose-built structured interface.

The use case is LLM-as-user testing: give an LLM access to the TUI's state and action space, ask
it to complete a goal (e.g., "build a command for a refactoring task"), and observe where it gets
confused, makes wrong selections, or cannot find what it needs. This is the most direct way to
discover UX gaps that ADR-0113 evaluation loops only approximate indirectly.

Bubble Tea's architecture already has the right shape for this. The `Model` struct is the full
state; `Update(msg) -> (Model, Cmd)` is a pure reducer. What is missing is:

1. A way to serialize `Model` to structured JSON (so an LLM can read the current screen state
   without interpreting ANSI codes).
2. A way to inject named actions from JSON (so an LLM can drive the TUI without keypresses).
3. A mode that skips terminal rendering entirely (so no PTY is required).

### Alternatives considered

**A — ANSI capture + strip**: Run the TUI in a PTY, capture output, strip escape codes, feed to
LLM. Problems: structure is lost (which item is focused? what is selectable?), fragile against
layout changes, requires PTY setup that is awkward in automated contexts.

**B — SPA via browser devtools**: The SPA is already accessible to LLMs via the chrome devtools
MCP tools (snapshot, click, fill). This covers the web surface but not the terminal TUI, and the
two surfaces have different affordances and keyboard interaction patterns.

**C — `bar build` output as proxy**: An LLM can already construct bar commands directly via
`bar help llm`. This is useful for prompt construction but tells us nothing about TUI UX — it
bypasses the interface entirely.

**D — Harness mode (chosen)**: Add a `--harness` flag to `bar tui2` that skips terminal rendering
and instead reads JSON actions from stdin, writing JSON state snapshots to stdout after each
action. The LLM acts as a user: it reads a state snapshot, decides on an action, submits it, and
observes the next state.

### Why harness mode is the right choice

- Bubble Tea already provides the state machine; the harness only adds a serialization layer and
  stdin reader — it does not require restructuring the TUI.
- The same JSON state format can serve both LLM exploration and automated regression tests.
- No PTY required. The harness can be driven from a simple bash pipe or a Go test.
- The LLM receives semantic state (focused item, visible tokens, selected tokens, current stage)
  rather than rendered bytes, so it can reason about the interface at the right level of
  abstraction.

---

## Decision

Add a `--harness` flag to `bar tui2` that activates headless mode:

### State output (stdout, after each action)

```json
{
  "stage": "method",
  "focused_token": "diagnose",
  "visible_tokens": [
    {"key": "diagnose", "label": "Root cause identification", "selected": false},
    {"key": "analysis", "label": "Component decomposition", "selected": true}
  ],
  "selected": {
    "task": "probe",
    "completeness": "full",
    "scope": [],
    "method": ["analysis"],
    "form": "",
    "channel": "",
    "directional": ""
  },
  "command_preview": "bar build probe full analysis",
  "help_visible": false,
  "error": ""
}
```

### Action input (stdin, one JSON object per line)

```json
{"type": "nav", "target": "method"}
{"type": "select", "token": "diagnose"}
{"type": "deselect", "token": "analysis"}
{"type": "key", "key": "tab"}
{"type": "filter", "text": "root cause"}
{"type": "quit"}
```

`nav` moves to a named stage/axis. `select`/`deselect` toggle a token by key. `key` injects a
raw Bubble Tea `KeyMsg` for actions not covered by semantic types (e.g., scrolling). `filter`
sets the search filter text. `quit` terminates the harness and emits the final state.

### Transcript capture

When `--harness-transcript <path>` is passed, each `(state, action)` pair is appended to a JSONL
file. This enables replay, regression suites, and prompt improvement data.

### No PTY requirement

The harness replaces the Bubble Tea `Program` renderer with a no-op writer. The Bubble Tea update
loop still runs; only the renderer is suppressed.

---

## Consequences

- `internal/bartui2/` gains a `Harness` type that wraps the existing `Model` and exposes
  `Observe() HarnessState` and `Act(action HarnessAction) error` methods.
- The `bar tui2 --harness` flag wires stdin/stdout to `Harness.Act` / `Harness.Observe` in a
  read-action → emit-state loop.
- The `HarnessState` JSON schema is the first stable, versioned contract for the TUI's observable
  state. Changes to it are breaking changes for consumers of the harness.
- Automated tests can use `Harness` directly in Go without spawning a subprocess.
- LLM-driven exploration sessions produce transcripts that feed back into ADR-0113 loop evaluation
  and UX improvement work.
- The SPA is not affected; it already has a more direct interaction path via browser devtools.
