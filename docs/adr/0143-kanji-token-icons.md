# ADR: Kanji Icon Display for Bar Token Catalog

**Date:** 2026-02-22
**Status:** Proposed
**Authors:** jaresty

## Context

The bar token catalog contains 144 tokens across 6 axes (channel, completeness, directional, form, method, scope). Users must scan these tokens visually to find relevant modifiers, which can be time-consuming. The user can read kanji and believes LLMs can interpret them effectively.

## Decision

We will add a `kanji` field to each token in the axis configuration, containing 1-2 character kanji icons for visual display only. These icons will:

1. **Not** be part of the input grammar — tokens are selected by their existing ASCII names
2. **Appear** in display contexts: help output, SPA, TUI2
3. **Be optional** — clients may choose to not render them
4. **Follow** semantic mapping principles where possible

### Axes and Token Counts

| Axis | Token Count | Example Mappings |
|------|-------------|------------------|
| channel | 15 | 記 (record/ADR), 図 (diagram), 演 (presentation) |
| completeness | 7 | 略 (gist), 深 (deep), 全 (full) |
| directional | 16 | 抽象 (abstract/fog), 具体 (concrete/dig), 実行 (execute/jog) |
| form | 34 | 論 (argue), 問 (question), 表 (table) |
| method | 59 | 因 (abduce), 演 (adversarial), 類 (analog/induce) |
| scope | 13 | 実 (act), 仕 (agent), 時 (time) |

### Semantic Mapping Principles

1. **Core concept first** — Choose kanji representing the token's primary meaning
2. **Consistency within categories** — Related tokens share radicals when possible
3. **Readability** — Prefer common kanji (JLPT N3-N5 level)
4. **Uniqueness** — No two tokens in the same axis should share the same kanji

### Data Model

```python
# In AXIS_KEY_TO_VALUE, extend descriptions with kanji field
AXIS_KEY_TO_KANJI: Dict[str, Dict[str, str]] = {
    "method": {
        "abduce": "因果",
        "balance": "均衡",
        # ...
    },
    # ...
}

# Or as a separate constant
AXIS_TOKEN_TO_KANJI: Dict[str, Dict[str, str]]  # token -> kanji
```

### Implementation Locations

1. **lib/axisConfig.py** — Add `AXIS_KEY_TO_KANJI` constant
2. **internal/barcli/embed/prompt-grammar.json** — Add kanji to grammar metadata
3. **Help output** — Render kanji alongside token names
4. **SPA/TUI2** — Display kanji in token selectors

## Consequences

### Positive

- Faster visual scanning for kanji-literate users
- LLMs can interpret kanji and use them as semantic hints
- No impact on input grammar or existing workflows
- Display-only means gradual adoption (clients opt-in)

### Negative

- Other users may not understand the icons
- Maintenance burden: new tokens need kanji assignments
- Risk of inconsistent or confusing mappings
- Additional complexity in rendering code

### Mitigation

- Document kanji meanings in help output (hover or inline)
- Provide plain-text fallback for accessibility
- Create mapping guidelines to ensure consistency

## Alternatives Considered

| Alternative | Rationale for Rejection |
|------------|------------------------|
| Emoji icons | Too opinionated, limited set |
| Single-letter codes | Not enough unique letters for 144 tokens |
| Color coding | Requires color perception, less precise |
| Numeric codes | No semantic meaning, hard to remember |

## Implementation Notes

1. Map all 144 tokens across 6 axes (not just method as pilot)
2. Draft mappings in a spreadsheet for review
3. Validate LLMs can interpret kanji correctly via `bar help llm`
4. Add to axisConfig.py in the same PR as token additions
5. Document mapping rationale in code comments

## Open Questions

- Should kanji appear in the static prompt context? (likely: yes, as metadata)
- Should there be a toggle in bar CLI to show/hide kanji?
- How to handle tokens with no clear kanji mapping?
