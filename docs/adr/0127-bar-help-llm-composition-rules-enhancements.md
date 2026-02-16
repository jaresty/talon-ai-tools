# ADR 0127: Token Guidance Enhancements for Incompatibilities

## Status

Proposed

## Context

ADR 0085 (Shuffle-Driven Catalog Refinement) Cycle-5 evaluated 20 random prompt combinations. The evaluation revealed:

1. **Channel-form conflicts**: sketch + indirect/prose forms
2. **Task-channel mismatches**: shellscript + pick/diff/sort, gherkin + sort/fix/make
3. **Token count impact**: Low-fill (4.4/5) vs high-fill (3.3/5)

The meta-evaluation found that existing guidance in `AXIS_KEY_TO_GUIDANCE` (axisConfig.py) helps for some cases but misses:
- sketch channel + form conflicts
- shellscript + pick/diff/sort (currently only warns about "narrative tasks")

The guidance field is better than help_llm because it shows in the TUI at decision time.

## Decision

Add guidance to token definitions in `lib/axisConfig.py`:

### 1. Add sketch channel guidance

Add to `AXIS_KEY_TO_GUIDANCE["channel"]`:

```python
"sketch": "D2 diagram output only. Avoid with prose forms (indirect, case, walkthrough) - "
          "choose diagram OR prose, not both.",
```

### 2. Enhance shellscript guidance

Update existing guidance to include pick/diff/sort:

```python
"shellscript": "Shell script output. Avoid with narrative tasks (sim, probe) and "
                "selection tasks (pick, diff, sort) - these don't produce code.",
```

### 3. Add gherkin task-channel guidance

The existing gherkin guidance warns about sort, probe, diff but not fix/make. Add:

```python
# Already has: "Avoid with sim, sort, probe, or diff"
# Add fix/make to existing guidance
```

### 4. Add effective pairs to task guidance

Add to `STATIC_PROMPT_GUIDANCE_OVERRIDES` (staticPromptConfig.py) for task tokens:

```python
"diff": "Works well with: jira (comparison tables), log (structured diff)",
"make": "Works well with: svg (SVG diagrams), adr (decision records)",
"check": "Works well with: log (validation output), gherkin (acceptance criteria)",
"plan": "Works well with: adr (architecture decisions), diagram (flowcharts)",
"sim": "Works well with: diagram (Mermaid scenarios), slack (session format)",
```

## Implementation

1. Edit `lib/axisConfig.py` - add/update guidance in `AXIS_KEY_TO_GUIDANCE`
2. Edit `lib/staticPromptConfig.py` - add effective pairs in `STATIC_PROMPT_GUIDANCE_OVERRIDES`
3. Regenerate grammar and verify TUI shows new guidance
