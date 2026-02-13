# ADR-0109: Token Labels — Short CLI-Facing Descriptions for Axis Tokens and Tasks

## Status

Accepted — Implementation complete (D1–D7). D4 (tui2 label display) completed via ADR-0111
Loop 3. Schema version bump deferred (labels/guidance added as optional fields; no breaking
change). ADR-0110 D2 description trimming complete (see that ADR).

## Context

Every axis token and task token has a single `description` field. This description is a
**prompt-injection text**: verbose, LLM-instruction-facing prose designed to shape how the LLM
executing the bar prompt behaves. For example, the `scope:act` description reads:

> "The response focuses on what is being done or intended—tasks, activities, operations, or work to
> be performed—suppressing interpretation, evaluation, structural explanation, or
> perspective-shifting."

This text serves the **executing LLM** well. It serves the **selecting agent or human** poorly.

### The Selection Problem

LLMs generating bar commands frequently produce invalid tokens and must fall back to
`bar help tokens --plain` for discovery. When they do, they receive bare `category:slug` lines
with no context:

```
scope:act
scope:mean
scope:struct
scope:thing
scope:time
scope:view
```

With no label, the LLM cannot distinguish between these tokens from the output alone. It either
injects the full `bar help tokens` output (noisy, costs tokens, mixes prompt-injection text with
selection guidance) or guesses based on the slug name (which is often ambiguous — `act` could mean
"action", `mean` could mean "average", `thing` is opaque).

### The Persona Precedent

Persona presets already have this solved. Each preset has:

- **`label`**: short, human-facing (`"Designer to PM"`)
- **`docs[axis][token]`**: the longer description for reference

Axis tokens and tasks have no equivalent of `label`. The inconsistency is structural.

### What a Label Is Not

A label is not a synonym for the existing description. The distinction:

| Field | Audience | Purpose | Length |
|-------|----------|---------|--------|
| `description` | Executing LLM | Shapes prompt behavior | 1-3 sentences |
| `label` *(new)* | Selecting agent or human | Guides token choice | 3-8 words |

Examples:

| Token | Current description (excerpt) | Proposed label |
|-------|-------------------------------|----------------|
| `scope:act` | "The response focuses on what is being done or intended—tasks, activities…" | "Tasks and intended actions" |
| `scope:mean` | "The response focuses on how something should be understood prior to judgment…" | "Conceptual meaning and framing" |
| `method:diagnose` | "The response identifies the root cause or source of a problem…" | "Root cause and failure analysis" |
| `form:bullets` | "The response presents content as a bulleted list…" | "Bulleted list" |
| `task:make` | "The response creates new content that did not previously exist…" | "Create new content" |

---

## Decision 1: Add `labels` Map to Grammar Schema

Add a `labels` section parallel to `definitions` under `axes`, and a `labels` field under `tasks`:

```json
{
  "axes": {
    "definitions": { "scope": { "act": "...long description..." } },
    "labels":      { "scope": { "act": "Tasks and intended actions" } },
    "list_tokens": { ... }
  },
  "tasks": {
    "catalog": { ... },
    "labels": {
      "make": "Create new content",
      "fix":  "Correct or repair existing content"
    }
  }
}
```

Labels are **optional per token**: if absent, consumers fall back to the existing description (or
slug). This allows incremental authoring and custom grammar compatibility.

---

## Decision 2: Expose `AxisLabel()` and `TaskLabel()` on Grammar

Add two accessor methods to `Grammar`:

```go
// AxisLabel returns the short CLI-facing label for the given axis token.
// Falls back to empty string if no label is defined.
func (g *Grammar) AxisLabel(axis, token string) string

// TaskLabel returns the short CLI-facing label for the given task token.
// Falls back to empty string if no label is defined.
func (g *Grammar) TaskLabel(name string) string
```

Fallback chain: `label` → empty string (callers decide whether to fall back to description or slug).

---

## Decision 3: Update `--plain` to Emit Tab-Separated `category:slug\tlabel`

When a label is available, `bar help tokens --plain` emits:

```
scope:act	Tasks and intended actions
scope:mean	Conceptual meaning and framing
scope:struct	Arrangement and relationships
task:make	Create new content
```

When no label is defined for a token, the line is emitted without a tab (bare `category:slug`),
preserving backwards compatibility for tokens in custom grammars without labels.

**Backwards compatibility:** All existing scripts are preserved:
- `grep '^scope:'` — still matches
- `cut -f1` — extracts bare `category:slug`
- `fzf` — now benefits from the label text for matching
- LLM token selection — gets description without the full `bar help llm` payload

---

## Decision 4: Use Labels in TUI and `bar help tokens` Default View

**TUI (`bar tui2`):** Show label in the token selection list instead of the truncated long
description. The long description remains accessible (e.g., on hover or expanded view).

**`bar help tokens` (non-plain):** Show label inline after the token slug, and the long description
in a separate line or on demand:

```
CONTRACT AXES
  scope:
    • act  [Tasks and intended actions]
      The response focuses on what is being done or intended—tasks, activities…
```

Or in compact mode: `• act: Tasks and intended actions` (label only).

---

## Decision 5: Add Label Column to `bar help llm` Token Catalog

The Token Catalog in `bar help llm` currently renders as a two-column table:

```markdown
| Token | Description |
|-------|-------------|
| `act` | The response focuses on what is being done or intended—tasks, activities… |
```

The description column is too long to scan. Add a `Label` column as the second column:

```markdown
| Token | Label | Description |
|-------|-------|-------------|
| `act` | Tasks and intended actions | The response focuses on what is being done or intended—tasks, activities… |
| `mean` | Conceptual meaning and framing | The response focuses on how something should be understood prior to judgment… |
```

This enables a two-pass reading strategy:
1. **Skim labels** to find candidate tokens (fast, one word-group per token)
2. **Read description** only for the 1-2 candidates that look right (targeted, avoids reading all descriptions)

When a token has no label defined, the Label cell is left empty and the behavior is unchanged.

The same three-column format applies to all axes in the catalog (tasks, completeness, scope,
method, form, channel, directional) and to the persona docs tables where labels are available.

---

## Decision 6: Update `lib/promptGrammar.py` to Pass Labels Through

The JSON is generated by `prompts/export.py` calling `lib/promptGrammar.py:prompt_grammar_payload()`.
The `_build_axis_section` and `_build_static_section` functions read from a `catalog` dict but
currently have no `labels` handling.

Two catalog keys must be added and threaded through:

| New catalog key | Shape | Consumed by |
|----------------|-------|-------------|
| `axis_labels` | `{axis: {token: label}}` | `_build_axis_section` → `axes.labels` in JSON |
| `static_prompt_labels` | `{task: label}` | `_build_static_section` → `tasks.labels` in JSON |

Labels are optional per token — missing entries produce no JSON entry, and the Go loader falls
back gracefully. This means labels can be added incrementally without blocking a schema version
bump on authoring completeness.

The authoring source (wherever `catalog["axes"]` token descriptions are maintained) needs new
`label` entries alongside existing descriptions. This is the main editorial cost.

---

## Decision 7: Update `bar-manual` Skill to Document New `--plain` Format

`bar-manual/skill.md` documents `--plain` in its Advanced section:

```bash
bar help tokens --plain             # category:slug one per line
bar help tokens scope --plain       # scope axis only
bar help tokens --plain | grep '^task:'  # just tasks
```

Update the comment on the first line and add a note about the tab format:

```bash
bar help tokens --plain             # category:slug[\tlabel] — tab-separated when labels exist
bar help tokens scope --plain       # scope axis only
bar help tokens --plain | grep '^task:'        # just tasks (label included if present)
bar help tokens --plain | cut -f1              # slugs only, strip labels
```

No changes are needed to `bar-autopilot`, `bar-suggest`, or `bar-workflow` — those skills only
reference `bar help tokens` (non-plain) for fallback token discovery, which is unaffected.

---

## Consequences

### Positive

- **Closes the persona inconsistency.** All token types now have label (short) + description (long),
  matching the existing persona preset pattern.
- **`--plain` becomes LLM-useful.** A selecting agent can do a single `bar help tokens --plain`
  call and make an informed token choice without loading the full `bar help llm` reference.
- **TUI improves.** Token selection lists show concise, scannable text instead of truncated
  prompt-injection prose.
- **Backwards compatible.** Existing `--plain` consumers (grep, cut, fzf) are unaffected.
- **Custom grammar compatible.** Labels are optional; grammars without labels degrade gracefully.

### Negative

- **Editorial cost.** Labels must be written for ~50+ tokens. Quality matters — a poor label
  misdirects token selection.
- **Schema version bump.** Adding `labels` to the grammar JSON requires incrementing `schema_version`
  and updating the loader.
- **Two sources of truth risk.** If a token's description changes substantially, its label may
  become stale. Labels should be reviewed whenever descriptions change.

### Neutral

- The Python grammar source (if generating the JSON) needs a `label` field added to token
  definitions. The Go loader change is small.
- `bar help llm` gains a scannable label column in the Token Catalog but its role as the
  comprehensive reference is unchanged. Labels improve scanning speed; descriptions remain
  the authoritative source for understanding token behavior.
