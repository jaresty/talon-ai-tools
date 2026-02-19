# ADR-0142: Task Token `use_when` — Routing Hints for Navigation Surfaces

## Status

Accepted

## Context

Axis tokens (scope, method, form, channel, directional) carry a `use_when` field in the grammar
JSON that renders as a "When to use" column in the Token Catalog and drives the dot-indicator +
expandable panel in the SPA. Task tokens have no equivalent: their `guidance` field (ADR-0110)
carries a "Notes" column but not routing trigger phrases.

As a result:

1. The "Choosing Task" routing table in `bar help llm` is hardcoded in `help_llm.go` rather than
   data-driven from the grammar — a SSOT violation that means updating task selection guidance
   requires two edits (staticPromptConfig.py + help_llm.go).
2. The SPA's `getTaskTokens()` hard-codes `use_when: ''` for every task token, so the dot
   indicator and "When to use" panel never appear for tasks.
3. The TUI task stage has no routing hint available even though it renders the same TokenSelector
   component that shows use_when for axis tokens.

The fix: add `use_when` to task tokens, following the identical pattern already established for
axis and persona tokens.

## Decision

Add a `use_when` map to the `tasks` section of the grammar JSON, parallel to `axes.use_when` and
`persona.use_when`. Populate it for all 11 task tokens via `staticPromptConfig.py` (SSOT). Surface
it in `bar help llm`, the SPA, and the TUI.

### Schema extension

```json
{
  "tasks": {
    "descriptions": { ... },
    "labels": { ... },
    "guidance": { ... },
    "use_when": {
      "probe": "Analyze structure or surface assumptions. Debug/troubleshoot: probe + diagnose method. Heuristic: 'analyze', 'what's going on', 'debug', 'investigate', 'why is this' → probe.",
      "sim": "Temporal scenario walkthrough. Heuristic: 'what would happen if', 'play out', 'simulate' → sim.",
      ...
    }
  }
}
```

### SSOT

`lib/staticPromptConfig.py` gains `_STATIC_PROMPT_USE_WHEN: dict[str, str]` — the same pattern
as `_STATIC_PROMPT_GUIDANCE`. The grammar generator reads it and emits `tasks.use_when`.

### Surfaces

| Surface | Change |
|---------|--------|
| `bar help llm` Token Catalog | Task table gains 5th "When to use" column (matches axis format) |
| `bar help llm` "Choosing Task" | Generated from `tasks.use_when` instead of hardcoded strings |
| SPA TokenSelector | `getTaskTokens()` reads `tasks.use_when`; dot indicator + panel appear |
| TUI tui2 task stage | Token data includes `use_when`; shown in token detail area |

## Consequences

### Positive

- Single SSOT for task routing guidance (staticPromptConfig.py only; no more hardcoding in Go)
- SPA and TUI gain routing hints for task tokens, matching the axis token experience
- "Choosing Task" routing table auto-updates when staticPromptConfig.py changes

### Tradeoffs

- 11 `use_when` strings must be written and maintained
- Minor grammar JSON size increase

---

*Work-log: `0142-task-token-use-when.work-log.md`*
*Evidence: `docs/adr/evidence/0142/`*
