# ADR-0154: Prompt Metadata Domain Separation — Structural Field Isolation

## Status

Draft

## Context

Prompt metadata for tokens (task, scope, method, form, channel, directional, persona) lives in two locations:

1. **`prompt-grammar.json`** — the grammar JSON exported for CLI/SPA/TUI
2. **`staticPromptConfig.py`** — Python SSOT for task token configuration

Both files contain multiple metadata fields that serve different purposes:

| Field | Location | Intended purpose |
|-------|----------|------------------|
| `definitions` | grammar.json | What the token means (semantic definition) |
| `guidance` | grammar.json | How this token differs from similar tokens |
| `use_when` | grammar.json | When to select this token (heuristics/triggers) |
| `_STATIC_PROMPT_GUIDANCE` | staticPromptConfig.py | Naming traps, ambiguity resolution |
| `_STATIC_PROMPT_USE_WHEN` | staticPromptConfig.py | Routing triggers (parallel to JSON) |
| `description` | tasks.catalog | Task profile description |

### Field Migration Mapping

This table maps the 6 existing fields to the 3 new structured fields:

| Current Field | Location | New Field | Notes |
|--------------|----------|-----------|-------|
| `definitions` | grammar.json | `definition` | Direct rename; strip heuristics/distinctions content |
| `guidance` | grammar.json | `distinctions` | Parse "Distinct from X" into token+note pairs |
| `use_when` | grammar.json | `heuristics` | Extract trigger phrases; parse "Heuristic:" content |
| `_STATIC_PROMPT_GUIDANCE` | staticPromptConfig.py | `distinctions` | Merge with grammar.json distinctions |
| `_STATIC_PROMPT_USE_WHEN` | staticPromptConfig.py | `heuristics` | Merge with grammar.json heuristics |
| `description` | tasks.catalog | `definition` | Migrates to definition; task.profile.description deprecated |

The problem: each of these fields contains free-form text that conflates multiple domains. For example, from `prompt-grammar.json` line 690:

```
"drift": "Conclusion-enforcement gap analysis: user wants to identify where a representation
treats conclusions as necessary but does not structurally enforce them, allowing interpretive
inference or hidden assumptions to substitute. Heuristic: 'where are we assuming necessity
without derivability', ... → drift. Distinct from gap method..."
```

This single string mixes:

1. **Definition**: "Conclusion-enforcement gap analysis"
2. **User intent**: "user wants to identify where..."
3. **Heuristic**: "'where are we assuming necessity without derivability'"
4. **Cross-token distinction**: "Distinct from gap method..."

Similarly, `use_when` strings contain both heuristics ("Heuristic: 'analyze', 'debug'") AND distinction ("Distinct from pull").

## Decision

Structure each metadata field to contain only one domain, using sub-fields rather than free-form text:

### Proposed schema

```json
{
  "$schema": "prompt-metadata/v2",
  "tasks": {
    "metadata": {
      "probe": {
        "definition": "The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.",
        "heuristics": ["analyze", "debug", "troubleshoot", "investigate"],
        "distinctions": [
          {
            "token": "pull",
            "note": "probe = analyze broadly; pull = extract subset"
          }
        ]
      }
    }
  }
}
```

### Field responsibilities

- **`definition`**: Pure semantic meaning — what the token does, no context about selection
- **`heuristics`**: Array of trigger phrases users would say to invoke this token
- **`distinctions`**: Structured map of other tokens this differs from, with explanation

### Changes required

1. Migrate `staticPromptConfig.py` dictionaries (`_STATIC_PROMPT_GUIDANCE`, `_STATIC_PROMPT_USE_WHEN`) to nested structure
2. Update grammar generator to flatten to JSON with new schema
3. Update consumer code (SPA, TUI, CLI help) to read structured fields
4. Add schema-based validation (see Validation section below)

### Schema Versioning and Migration Timeline

The new schema includes a `$schema` field for version detection:

| Phase | Timeline | Schema Version | Consumer Behavior |
|-------|----------|----------------|------------------|
| v1 (current) | Now | (none) | Read legacy free-form fields |
| v2 (transition) | Month 1-3 | `prompt-metadata/v2` | Check for `$schema`; fallback to legacy if missing |
| v3 (new) | Month 4-6 | `prompt-metadata/v2` | Read new structured fields only |
| v4 (cleanup) | Month 7+ | `prompt-metadata/v2` | Legacy format support removed |

### Migration Decision Rules

For entries where content doesn't cleanly separate into distinct fields:

| Scenario | Handling |
|----------|----------|
| Definition contains intent language (e.g., "user wants to...") | Keep in `definition`; extract separate `heuristics` if trigger phrases present |
| Heuristic IS the distinction (e.g., "use when 'pull'") | Duplicate to both `heuristics` (as trigger) and `distinctions` (with note) |
| Cannot separate at all | Mark with `unresolved: true`; defer to Phase 2 |
| Empty heuristics or distinctions | Use empty array `[]`; do not omit field |

### Validation

Replace fragile pattern-matching with JSON Schema validation:

```json
{
  "definition": { "type": "string", "maxLength": 500 },
  "heuristics": {
    "type": "array",
    "items": { "type": "string", "maxLength": 100 },
    "maxItems": 20
  },
  "distinctions": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["token", "note"],
      "properties": {
        "token": { "type": "string" },
        "note": { "type": "string", "maxLength": 200 }
      }
    }
  }
}
```

### Consumer Requirements

Different surfaces need different data fields:

| Consumer | Fields Needed | Rendering |
|----------|---------------|-----------|
| CLI help | `definition` + `heuristics[0:3]` | Text with inline examples |
| SPA tooltips | `heuristics` only | Chip/tag array display |
| SPA hover highlighting | `distinctions[].token` | On hover, find all entries where `token === hovered` for bidirectional highlighting |
| TUI panels | All fields | Full structured view |
| Documentation generation | `definition` | Prose paragraphs |
| Internal analytics | `heuristics` + `distinctions` | Structured export for analysis |

### Alternative considered: Leave as-is

Keep free-form text. Accept the coupling — changing `drift`'s definition requires updating 10+ "Distinct from drift" clauses in other tokens. This is the current state and works via human coordination.

### Rationale for change

- **Maintenance**: Token changes cascade across multiple entries; structured fields allow validation and targeted updates
- **Consumption**: Different surfaces need different grain sizes (UI wants heuristics array, docs want definition string)
- **Validation**: Currently impossible to verify that distinctions are consistent with definitions

## Consequences

### Positive

- Clearer ownership: definition changes don't require hunting "Distinct from" clauses
- Validation possible: can verify heuristics contain no definitions, definitions contain no heuristics
- Surface-specific rendering: UI can pull `heuristics` array for tooltips, `definition` string for help panels

### Negative

- Migration cost: all existing metadata must be refactored
- Backward compatibility: consumers require phased migration (see Migration Timeline)
- Some entries may not cleanly separate; decision rules provided for handling
- Validation requires schema migration alongside content migration

### Unknown

- Whether the "Distinct from" clauses are actually maintained consistently today — no validation exists
- How many tokens have cross-references that would need updating during migration
- How many entries will require `unresolved: true` deferral to Phase 2
