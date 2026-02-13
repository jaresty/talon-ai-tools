# ADR-0111: Persona Token Labels and Label-First TUI Display

## Status

Accepted — Implementation complete (D1–D4). Also satisfies ADR-0109 D4 (tui2 label display)
which was previously deferred.

## Context

ADR-0109 added short `label` fields to grammar axis tokens and tasks and wired them through
`bar help tokens --plain` (tab-separated) and `bar help llm`. Two gaps remain:

### Gap 1: Persona/Audience/Tone/Voice/Intent tokens have no labels in `--plain`

`bar help tokens --plain` now emits `category:slug<TAB>label` for axis and task tokens.
But persona-space tokens emit bare slugs:

```
persona:design          ← no label
audience:to-ceo         ← no label
tone:casually           ← no label
voice:as-kent-beck      ← no label
intent:announce         ← no label
```

Persona *presets* already carry a `label` field (e.g., `"Designer to PM"`) but it is not
emitted in `--plain`. Audience/tone/voice/intent axis tokens have no `label` field at all —
only a long `docs` description identical in role to the axis `description` problem that
ADR-0109 solved for contract axes.

### Gap 2: tui2 displays truncated long descriptions instead of short labels

`tui_tokens.go:buildAxisOptions` and `buildStaticCategory` call `displayLabel(value,
description)`, which returns the full long prompt-injection description when available.
In the token list this appears as a multi-sentence wall of prose, often truncated, instead
of the 3-8 word label now available via `grammar.AxisLabel()` / `grammar.TaskLabel()`.

The same pattern applies to `buildPersonaOptions` for voice/audience/tone/intent tokens.

`buildPersonaPresetOptions` already uses `preset.Label` — that path is correct.

### What Already Exists

- Persona presets: `PersonaPreset.Label` exists in grammar and Go struct.
- Intent presets: `IntentPreset.Label` exists in grammar (via `persona.intent.presets[key].label`).
- Axis tokens: `grammar.AxisLabel()` added by ADR-0109 — not yet used in tui2.
- Task tokens: `grammar.TaskLabel()` added by ADR-0109 — not yet used in tui2.

---

## Decision 1: Add `labels` Map to Grammar `persona` Section

Add a `labels` section parallel to `docs` under `persona`, covering voice, audience, tone,
and intent axis tokens:

```json
{
  "persona": {
    "docs": { "voice": { "as programmer": "The response adopts..." } },
    "labels": { "voice": { "as-programmer": "Programmer stance" } }
  }
}
```

Labels use the slug form as key (consistent with how `bar help tokens --plain` emits them).

Authoring source: add `PERSONA_KEY_TO_LABEL` dict in `lib/personaConfig.py`, parallel to
`PERSONA_KEY_TO_VALUE`. Update `lib/promptGrammar.py` `_build_persona_section()` to include
the labels map.

---

## Decision 2: Expose `PersonaLabel()` on Grammar

```go
// PersonaLabel returns the short CLI-facing label for the given persona axis token.
// Returns empty string if no label is defined.
func (g *Grammar) PersonaLabel(axis, token string) string
```

Lookup uses the slug-normalised key, falling back to the canonical token key if absent.
Returns empty string; callers fall back to slug or description.

---

## Decision 3: Update `--plain` to Emit Tab-Separated Labels for Persona Space

When a label is available, `bar help tokens --plain` emits:

```
persona:design\tDesigner to PM
audience:to-ceo\tCEO-level audience
tone:casually\tCasual, conversational
voice:as-kent-beck\tKent Beck style
intent:announce\tAnnounce
```

When no label is defined, the line is emitted without a tab (bare `category:slug`).

Applies to: persona presets (use `PersonaPreset.Label`), persona axes (use `PersonaLabel()`),
intent tokens (use intent preset `Label` via grammar, falling back to `PersonaLabel("intent", token)`).

---

## Decision 4: Use Short Labels in TUI Token Lists

Update `tui_tokens.go` to prefer short labels over long descriptions in the `Label` field
of `TokenOption`:

| Function | Current | New |
|----------|---------|-----|
| `buildStaticCategory` | `displayLabel(value, description)` | prefer `grammar.TaskLabel(name)`, fall back to `displayLabel` |
| `buildAxisOptions` | `displayLabel(value, description)` | prefer `grammar.AxisLabel(axis, value)`, fall back to `displayLabel` |
| `buildPersonaOptions` | `displayLabel(value, description)` | prefer `grammar.PersonaLabel(axis, value)`, fall back to `displayLabel` |

`buildPersonaPresetOptions` already uses `preset.Label` — no change needed.

The `Description` field retains the full long text for hover/expand views.

---

## Consequences

### Positive

- `bar help tokens --plain` now provides selection hints for the complete token vocabulary
  (all 50+ persona-space tokens gain labels).
- tui2 token lists show concise, scannable labels instead of truncated prompt-injection prose.
- LLMs calling `bar help tokens --plain` get uniform `category:slug<TAB>label` format for
  all token types, enabling informed selection without `bar help llm`.
- Closes the ADR-0109 D4 deferred item (tui2 label display).

### Negative

- Editorial cost: ~50 persona axis token labels must be authored.
- Persona axis labels use slug keys in the JSON, which is slightly inconsistent with axis
  token labels (which use canonical token keys). Mitigation: the Go loader normalises both.

### Neutral

- Intent tokens benefit twice: labels appear in `--plain` and in tui2 list.
- `bar help tokens` non-plain display is unaffected (it already shows descriptions).
