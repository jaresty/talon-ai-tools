# ADR 0128: Token Guidance and Tooling Fixes from Task-Gap Analysis

## Status

**Implemented: Token guidance items (G-04, G-05, G-06, G-07, G-08, G-09)**

## Context

ADR-0113 (Task-Gap-Driven Catalog Refinement) identified several gaps in skill guidance and tooling. ADR-0127 already addressed channel-form conflicts in token guidance.

This ADR addresses remaining gaps: task-level guidance for probe/pull/show/make distinctions (better in token guidance than help_llm), plus tooling bugs.

## Implemented Changes

### Token Guidance Updates ✅

All token guidance items have been implemented:

#### 1. G-04: Probe vs Pull for Risk Tasks ✅

Added to `lib/staticPromptConfig.py`:

```python
"probe": "For extraction tasks ('what are the risks?', 'list the issues'), prefer 'pull' over 'probe'. "
    "probe = analyze broadly; pull = extract subset.",
```

#### 2. G-05: Scaffold + Make Conflict ✅

Added to `lib/axisConfig.py` AXIS_KEY_TO_GUIDANCE:

```python
"scaffold": "Learning-oriented explanation. Avoid with 'make' task producing "
    "artifacts (code, diagram, adr) - use only when user wants accompanied "
    "explanation. scaffold = explain from first principles.",
```

#### 3. G-06: Summarisation Routing ✅

Added to `lib/staticPromptConfig.py`:

```python
"show": "For summarisation of long documents, prefer 'pull' (extraction). "
    "show = explain a concept; pull = compress source material.",
"pull": "For summarisation: extract the conceptual core from source material with gist scope. "
    "For risk extraction: works well with fail scope.",
```

#### 4. G-07: Test Plan vs Coverage Gap ✅

Enhanced in `lib/staticPromptConfig.py`:

```python
"check": "Works well with: log, gherkin, test. "
    "For test coverage gaps: use check, not make ('check' = evaluate existing; 'make' = create new).",
"make": "Works well with: svg, adr, diagram, codetour. "
    "For test plans: use make, not check ('make' = create artifact; 'check' = evaluate existing).",
```

#### 5. G-08: Pre-mortem / Inversion ✅

Already present in existing `inversion` guidance in `lib/axisConfig.py`.

#### 6. G-09: Multi-turn Scope Note ✅

Already present in `internal/barcli/help_llm.go` (lines 1097-1100).

---

### Completed (Pre-ADR)

- **SF-01**: Persona token slug format - already fixed
- **SF-02**: Case form hang - user error (not a bug)
