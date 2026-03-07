# ADR-0156: Persona Token Structured Metadata

## Status

Draft

## Context

ADR-0154 introduced the `definition / heuristics / distinctions` schema for task tokens (11 tokens). ADR-0155 extended this schema to all 6 axis token types (~162 tokens). Both ADRs explicitly deferred persona tokens.

Persona tokens (5 axes, 45 tokens) currently carry two free-form text fields in `lib/personaConfig.py`:

| Field | Dict | Axes | Token count |
|-------|------|------|-------------|
| `use_when` | `PERSONA_KEY_TO_USE_WHEN` | voice, audience, tone, intent, presets | 45 |
| `guidance` | `PERSONA_KEY_TO_GUIDANCE` | presets, intent, tone (partial) | ~7 |

The `use_when` strings follow the same recognizable pattern seen in axis tokens: an intent description, heuristic trigger phrases, and "Distinct from X" comparisons. The `guidance` strings are sparse selection notes. Both mix semantic domains within unstructured text.

### Content mapping to ADR-0154 schema

| Current source | Content pattern | Target field |
|----------------|----------------|--------------|
| `use_when` first sentence | Intent description | `definition` |
| `use_when` `Heuristic:` clause | Trigger phrases | `heuristics[]` |
| `use_when` + `guidance` "Distinct from" | Comparison notes | `distinctions[]` |

### Pipeline (current)

```
personaConfig.py (PERSONA_KEY_TO_USE_WHEN / PERSONA_KEY_TO_GUIDANCE)
  → promptGrammar.py._build_persona_section()
    → prompt-grammar.json (persona.use_when, persona.guidance)
      → grammar.go (PersonaUseWhen / PersonaGuidance accessors)
        → help_llm.go (persona tables)
        → tui_tokens.go (buildPersonaOptions / buildPersonaPresetOptions)
        → grammar.ts / SPA TokenSelector.svelte
```

### Pipeline (target)

```
personaConfig.py (PERSONA_TOKEN_METADATA)
  → promptGrammar.py._build_persona_section()
    → prompt-grammar.json (persona.metadata)
      → grammar.go (PersonaMetadataFor accessor)
        → help_llm.go (uses PersonaMetadataFor; falls back to PersonaUseWhen)
        → tui_tokens.go (uses PersonaMetadataFor; falls back)
        → grammar.ts / SPA TokenSelector.svelte (reads metadata field)
```

## Decision

Apply the ADR-0154/ADR-0155 `definition / heuristics / distinctions` schema to all 5 persona axes (voice, audience, tone, intent, presets). The migration follows the co-existence pattern from ADR-0155: content migration (T-2–T-6) runs before consumer cutover (T-7–T-9), with legacy dict removal at T-10.

### Schema

Identical to ADR-0154 task token schema and ADR-0155 axis token schema:

```python
PERSONA_TOKEN_METADATA: Dict[str, Dict[str, PersonaTokenMetadata]] = {
    "voice": {
        "as programmer": {
            "definition": "...",
            "heuristics": ["..."],
            "distinctions": [{"token": "as designer", "note": "..."}],
        },
        ...
    },
    "audience": { ... },
    "tone": { ... },
    "intent": { ... },
    "presets": { ... },
}
```

### Python SSOT

`lib/personaConfig.py` is the SSOT. The generator (`scripts/tools/generate_persona_config.py` or equivalent) canonicalises the pprint format. After any manual edit, run the generator before committing.

### Pipeline

- New key `persona_token_metadata` added to `_build_persona_section()` output in `promptGrammar.py`
- Grammar JSON gains `persona.metadata` key: `{axis: {token: {definition, heuristics, distinctions}}}`
- `grammar.go` gains `PersonaSection.Metadata` field and `PersonaMetadataFor(axis, token)` accessor
- `grammar.ts` gains `personaMetadata` type on `grammar.persona`

### Consumer requirements

| Consumer | Change |
|----------|--------|
| `help_llm.go` | Persona tables swap to `Heuristics \| Distinctions` columns via `PersonaMetadataFor()` |
| `tui_tokens.go` | `buildPersonaOptions()` + `buildPersonaPresetOptions()` use `PersonaMetadataFor()` → `UseWhen`/`Guidance`; fall back to legacy if nil |
| SPA `TokenSelector.svelte` | Already handles `activeMeta.metadata` block; axis token panel renders for persona tokens automatically |

### Migration order

1. T-1: pipeline wiring (schema only, no content)
2. T-2 through T-6: content migration per axis (voice → audience → tone → intent → presets)
3. T-7: SPA specifying tests for persona token metadata panel
4. T-8: Wire `help_llm.go` to `PersonaMetadataFor()`
5. T-9: Wire `tui_tokens.go` to `PersonaMetadataFor()`
6. T-10: Remove migrated axes from `PERSONA_KEY_TO_USE_WHEN` and `PERSONA_KEY_TO_GUIDANCE`

## Salient Task List

- **T-1** Python/Go/TS pipeline: `PersonaTokenMetadata` TypedDicts + empty `PERSONA_TOKEN_METADATA` in `personaConfig.py`; `persona_token_metadata` key in `promptGrammar.py`; `PersonaSection.Metadata` + `PersonaMetadataFor()` in `grammar.go`; `grammar.ts` type update — schema only, no content
- **T-2** voice axis migration (11 tokens: as programmer, as prompt engineer, as scientist, as writer, as designer, as teacher, as facilitator, as PM, as junior engineer, as principal engineer, as Kent Beck)
- **T-3** audience axis migration (15 tokens: to managers, to product manager, to CEO, to LLM, to junior engineer, to stakeholders, to team, to designer, to analyst, to programmer, to principal engineer, to Kent Beck, to platform team, to stream aligned team, to XP enthusiast)
- **T-4** tone axis migration (5 tokens: casually, formally, directly, gently, kindly)
- **T-5** intent axis migration (6 tokens: inform, persuade, appreciate, announce, coach, teach)
- **T-6** presets axis migration (8 tokens: peer_engineer_explanation, teach_junior_dev, stakeholder_facilitator, designer_to_pm, product_manager_to_team, executive_brief, scientist_to_analyst, fun_mode)
- **T-7** SPA specifying tests: verify persona tokens with structured metadata render Heuristics + Distinctions sections in the token detail panel
- **T-8** Wire `help_llm.go` persona tables to use `PersonaMetadataFor()`; column headers swap to `Heuristics | Distinctions`
- **T-9** Wire `tui_tokens.go` `buildPersonaOptions()` + `buildPersonaPresetOptions()` to use `PersonaMetadataFor()` adapter
- **T-10** Remove migrated axes from `PERSONA_KEY_TO_USE_WHEN` and `PERSONA_KEY_TO_GUIDANCE`

## Alternatives Considered

### Keep free-form strings
Same arguments as ADR-0155: fragile, mixes semantic domains, blocks distinction cross-reference UX. Rejected for same reasons.

### Merge into ADR-0155
ADR-0155 was already mid-flight. Separate ADR keeps audit trail clean and allows persona-specific validation contracts.

## Consequences

### Positive
- Persona token metadata rendered in SPA distinction panel (same chip-highlight UX as task/axis tokens)
- `bar help llm` persona tables show structured `Heuristics | Distinctions` columns
- TUI persona token detail populated from structured source
- `PERSONA_KEY_TO_USE_WHEN` and `PERSONA_KEY_TO_GUIDANCE` eliminated

### Negative
- T-2–T-6 content migration requires hand-curation for 45 tokens across 5 axes
- Co-existence period (T-1 through T-9) means legacy dicts remain temporarily

### Residual
- Cross-type distinction references (e.g., voice token referencing audience token) are semantically permitted by the schema but unusual; accepted as needed
