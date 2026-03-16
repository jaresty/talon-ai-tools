# Grammar Schema

**Schema version**: 1.0
**Status**: Stable public contract

This document describes the public shape of `prompt-grammar.json` and the equivalent
YAML structure accepted by user-defined token set files (`BAR_EXTRA_GRAMMAR`).

---

## `prompt-grammar.json` top-level structure

```json
{
  "schema_version": "1.0",
  "reference_key": "<string>",
  "execution_reminder": "<string>",
  "meta_interpretation_guidance": "<string>",
  "axes": { ... },
  "tasks": { ... },
  "persona": { ... },
  "hierarchy": { ... },
  "slugs": { ... },
  "patterns": { ... },
  "starter_packs": { ... },
  "checksums": { ... }
}
```

Only `schema_version`, `axes`, `tasks`, and `persona` are part of the public contract.
The remaining top-level keys are implementation details subject to change.

---

## `axes`

```json
"axes": {
  "definitions":          { "<axis>": { "<token>": "<prompt-text>" } },
  "list_tokens":          { "<axis>": ["<token>", ...] },
  "labels":               { "<axis>": { "<token>": "<short display name>" } },
  "kanji":                { "<axis>": { "<token>": "<single CJK character>" } },
  "routing_concept":      { "<axis>": { "<token>": "<reference key phrase>" } },
  "categories":           { "<axis>": { "<token>": "<category name>" } },
  "axis_descriptions":    { "<axis>": "<prose description of this axis>" },
  "metadata":             { "<axis>": { "<token>": { ... } } },
  "cross_axis_composition": { ... },
  "form_default_completeness": { ... }
}
```

**Public sub-keys** (stable contract):

| Sub-key | Type | Description |
|---|---|---|
| `definitions` | `map[axis → map[token → string]]` | The prompt text injected for each token. This is the behavioral definition — the only thing that matters when the token is applied. |
| `list_tokens` | `map[axis → []string]` | Ordered list of all valid tokens on an axis. Drives tab completion and help output. |
| `labels` | `map[axis → map[token → string]]` | Short human-readable display name (used in TUI and SPA). Falls back to the token key if absent. |
| `kanji` | `map[axis → map[token → string]]` | Single CJK character compact label. Optional — absent means no compact label is shown. |
| `routing_concept` | `map[axis → map[token → string]]` | Reference key phrase shown in TUI/SPA detail panel. Optional. |
| `metadata` | `map[axis → map[token → TokenMetadata]]` | Structured discovery metadata per token (see below). |

The six sub-keys above are the ones user token sets can populate. The remaining
sub-keys (`categories`, `axis_descriptions`, `cross_axis_composition`,
`form_default_completeness`) are read by tooling but not settable from user token files.

### TokenMetadata shape

```json
{
  "definition":   "<string>",
  "heuristics":   ["<phrase>", ...],
  "distinctions": [
    { "token": "<other-token>", "note": "<contrast note>" }
  ]
}
```

| Field | Required | Description |
|---|---|---|
| `definition` | yes | The prompt text for this token (same value as `definitions[axis][token]`). |
| `heuristics` | no | Trigger phrases used for discovery (`bar lookup`). Not behavioral — only for token selection. |
| `distinctions` | no | Cross-references to related tokens that are easily confused with this one. |

---

## `tasks`

```json
"tasks": {
  "catalog":       { "<task>": { "profiled": bool, "talon_list_tokens": [...], "unprofiled_tokens": [...] } },
  "descriptions":  { "<task>": "<prompt-text>" },
  "labels":        { "<task>": "<short display name>" },
  "kanji":         { "<task>": "<single CJK character>" },
  "routing_concept": { "<task>": "<reference key phrase>" },
  "metadata":      { "<task>": { "definition": "...", "heuristics": [...], "distinctions": [...] } },
  "profiles":      { ... }
}
```

Tasks are the primary action tokens (`show`, `make`, `fix`, `probe`, etc.). They are not
settable from user token files in Phase 1.

---

## `persona`

```json
"persona": {
  "axes":      { "<axis>": ["<token>", ...] },
  "presets":   { "<preset>": { ... } },
  "labels":    { "<axis>": { "<token>": "<label>" } },
  "kanji":     { "<axis>": { "<token>": "<CJK>" } },
  "routing_concept": { "<axis>": { "<token>": "<phrase>" } },
  "metadata":  { "<axis>": { "<token>": { ... } } },
  "docs":      { ... },
  "spoken_map": { ... },
  "intent":    { ... }
}
```

Persona tokens (`voice`, `audience`, `tone`, `intent`) and presets are not settable
from user token files in Phase 1.

---

## User token set file format

User-defined token sets are YAML files (`.yaml` / `.yml`) or JSON files (`.json`).
YAML is recommended for hand-authored files — block scalars (`|`) keep long definitions
readable and comments (`#`) document intent.

The `BAR_EXTRA_GRAMMAR` environment variable points to the file. At load time bar
merges the file into the built-in grammar. **User tokens win on same-axis + same-key
conflicts** (user-last-wins), allowing built-in definitions to be overridden.

### File structure

```yaml
# optional: namespace: myteam   (reserved, ignored in Phase 1)

<axis-name>:
  <token-key>:
    definition: <string>          # REQUIRED — the prompt text injected when this token is used
    label: <string>               # optional — short display name; falls back to token key
    routing_concept: <string>     # optional — reference key shown in TUI/SPA detail panel
    kanji: <single CJK char>      # optional — compact visual label
    heuristics:                   # optional — trigger phrases for `bar lookup` discovery
      - <phrase>
    distinctions:                 # optional — contrast notes for easily confused tokens
      - token: <other-token>
        note: <contrast note>
```

Top-level keys name axes (`method`, `scope`, `form`, `completeness`, `channel`,
`directional`). Any key named `namespace` is reserved for Phase 3 and silently ignored
in Phase 1.

### Minimal example

```yaml
method:
  assess:
    definition: |
      The response evaluates the subject against readiness criteria,
      identifying gaps and risks before committing to a direction.
```

### Full example

```yaml
# ~/.config/bar/my-tokens.yaml
# Team-specific method tokens

method:
  assess:
    label: Evaluate readiness before committing
    routing_concept: Readiness evaluation pipeline
    kanji: 備
    definition: |
      The response evaluates the subject against the team's readiness criteria,
      identifying gaps, risks, and next steps before committing to a direction.
    heuristics:
      - are we ready
      - readiness check
      - go/no-go
    distinctions:
      - token: check
        note: check = evaluate against a condition; assess = evaluate readiness before committing
```

### Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `definition` | yes | string | Prompt text injected when the token is applied. Block scalar (`|`) recommended for multi-line prose. |
| `label` | no | string | Short display name in TUI/SPA. Falls back to token key if absent. |
| `routing_concept` | no | string | Reference key phrase in TUI/SPA detail panel. |
| `kanji` | no | string | Single CJK character compact label. |
| `heuristics` | no | `[]string` | Discovery trigger phrases used by `bar lookup`. Not behavioral — heuristics are for token selection only, not application. |
| `distinctions` | no | `[]object` | Each entry has `token` (string) and `note` (string). Cross-references to easily confused tokens. |

### Merge semantics

- User tokens are merged **after** the built-in grammar is loaded.
- On same-axis + same-key conflicts, the user value wins (overrides the built-in).
- Zero-value fields (absent fields) leave the existing built-in value unchanged — you
  can supply only `definition` to override the prompt text while keeping the built-in
  `label` and `kanji`.
- New tokens (keys not present in the built-in grammar) are appended to their axis.

### YAML footgun note

YAML has implicit type coercion: `yes` → `true`, bare numbers parsed as integers, `NO`
→ `false` (the Norway problem). Quote string values when the bare form could be
misread as a non-string type. Token keys should be plain snake_case strings and are
always safe; definition prose is always a string when expressed as a block scalar.

---

## Stability guarantees

| Item | Stability |
|---|---|
| `schema_version` field | Stable — will bump on breaking changes |
| `axes.definitions[axis][token]` | Stable |
| `axes.list_tokens[axis]` | Stable |
| `axes.labels[axis][token]` | Stable |
| `axes.kanji[axis][token]` | Stable |
| `axes.routing_concept[axis][token]` | Stable |
| `axes.metadata[axis][token]` shape | Stable |
| `tasks.*` top-level shape | Stable |
| `persona.*` top-level shape | Stable |
| All other top-level keys | Internal — may change without notice |
| User token set YAML format | Stable |
| Merge semantics (user-last-wins) | Stable |
