# ADR-0154: Prompt Metadata Domain Separation — Structural Field Isolation

## Status

Active

## Context

Prompt metadata for task tokens lives in two locations:

1. **`prompt-grammar.json`** — the grammar JSON exported for CLI/SPA/TUI
2. **`staticPromptConfig.py`** — Python SSOT for task token configuration

Both files contain multiple metadata fields that serve different purposes:

| Field | Location | Intended purpose |
|-------|----------|------------------|
| `definitions` | grammar.json tasks | What the token means (semantic definition) |
| `guidance` | grammar.json tasks | How this token differs from similar tokens |
| `use_when` | grammar.json tasks | When to select this token (heuristics/triggers) |
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

Structure each metadata field to contain only one domain, using sub-fields rather than free-form text.

This project is the sole consumer of `prompt-grammar.json` (CLI, SPA, and TUI all live in this repository). There is no phased migration or backward compatibility requirement — consumers are updated in the same commit sequence as the schema change.

### Proposed schema

```json
{
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
- **`distinctions`**: Structured array of other tokens this differs from, with explanation

### Changes required

1. Migrate `staticPromptConfig.py` dictionaries (`_STATIC_PROMPT_GUIDANCE`, `_STATIC_PROMPT_USE_WHEN`) to nested `_TASK_METADATA` structure — **done (Loop 1)**
2. Wire SPA `grammar.ts` types to read structured `metadata` field — **done (Loop 2)**
3. Add schema-based validation test — **done (Loop 3)**
4. Fix review gaps (add `fix` ≠ debug/repair distinction; add token coverage assertion; remove `$schema` field from export) — **T-4**
5. Wire Go `grammar.go` structs and `TaskMetadataFor()` accessor — **T-5**
6. Replace Go `help_llm.go` free-form rendering with structured field rendering; remove old `TaskGuidance()`/`TaskUseWhen()` static accessors — **T-6**
7. Replace SPA `TokenSelector.svelte` task `use_when` section with `metadata.heuristics` and `metadata.distinctions` rendering — **T-7**
8. Remove old Python flat dicts (`_STATIC_PROMPT_GUIDANCE`, `_STATIC_PROMPT_USE_WHEN`) and stop exporting `guidance`/`use_when` for static tasks in `_build_static_section` — **T-8**

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

| Consumer | Fields Needed | Rendering |
|----------|---------------|-----------|
| CLI help (`help_llm.go`) | `definition` + `heuristics` + `distinctions` | Structured table — definition prose, heuristics as comma-separated triggers, distinctions as token→note pairs |
| SPA token panel (`TokenSelector.svelte`) | `heuristics` + `distinctions` | Heuristics as chip/tag array; distinctions as structured notes replacing free-form `use_when` text |
| TUI panels | All fields | Full structured view |

### Alternative considered: Leave as-is

Keep free-form text. Accept the coupling — changing `drift`'s definition requires updating 10+ "Distinct from drift" clauses in other tokens. This is the current state and works via human coordination.

### Rationale for change

- **Maintenance**: Token changes cascade across multiple entries; structured fields allow validation and targeted updates
- **Consumption**: Different surfaces need different grain sizes (UI wants heuristics array, docs want definition string)
- **Validation**: Currently impossible to verify that distinctions are consistent with definitions

## Salient Task List

- **T-1** Migrate Python SSOT (`staticPromptConfig.py`) to `_TASK_METADATA` nested structure — **complete**
- **T-2** Wire SPA `grammar.ts` types — **complete**
- **T-3** Add schema validation test — **complete**
- **T-4** Fix review gaps: `fix` ≠ debug distinction; token coverage assertion; remove `$schema` from export
- **T-5** Wire Go `grammar.go` `TaskMetadata` structs + `TaskMetadataFor()` accessor
- **T-6** Replace `help_llm.go` free-form task rendering with structured metadata
- **T-7** Replace SPA `TokenSelector.svelte` task `use_when` section with `metadata.heuristics`/`distinctions`
- **T-8** Remove Python flat dicts; stop exporting `guidance`/`use_when` for static tasks

## Consequences

### Positive

- Clearer ownership: definition changes don't require hunting "Distinct from" clauses
- Validation possible: can verify heuristics contain no definitions, definitions contain no heuristics
- Surface-specific rendering: UI can pull `heuristics` array for chip display, `definition` string for help panels
- No migration complexity: single-consumer repository allows clean cutover

### Negative

- Migration cost: all existing metadata must be refactored (scope limited to task tokens for this ADR)
- Some entries may not cleanly separate; decision rules provided for handling

### Unknown

- Whether the "Distinct from" clauses are actually maintained consistently today — no validation exists
- How many entries will require `unresolved: true` deferral
