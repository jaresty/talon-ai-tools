# ADR: Kanji + UseWhen Rendering Interaction

**Status:** Accepted
**Date:** 2026-02-23
**Relates to:** ADR-0143 (Kanji), ADR-0142/0132/0133 (UseWhen)

## Context

ADR-0143 added kanji icons to token displays, and ADR-0142/0132/0133 added `use_when` guidance. Both features modify the same rendering surfaces:
- TUI2 token detail panes
- SPA TokenSelector meta-panels
- bar help llm token catalog

These features can collide when both metadata types exist for the same token, especially on constrained displays (mobile, small terminals).

## Decision

### Display Priority

When both kanji and `use_when` exist for a token:

1. **Desktop (>= 768px):** Display both
   - Kanji appears inline with token name
   - `use_when` appears in expandable detail panel

2. **Mobile (< 768px):** Display both, with scroll
   - Kanji visible in token chip
   - `use_when` accessible via token detail drawer
   - Detail drawer scrolls if content exceeds 60vh

### Rendering Order

**TUI2 detail pane:**
```
Token Name 漢
─────────────
Description: ...

When to use: ...  # use_when content (cyan)

Notes: ...        # guidance content
```

**SPA TokenSelector meta-panel:**
```
┌─────────────────────────┐
│ token 漢  [label]    ✕  │  ← kanji inline
├─────────────────────────┤
│ Description text...     │
│                         │
│ WHEN TO USE             │  ← use_when section
│ • guidance text...      │
│                         │
│ NOTES                   │  ← guidance section
│ • additional context... │
└─────────────────────────┘
```

**bar help llm Token Catalog:**
```
| Token  | Kanji | Label | Description | When to use |
|--------|-------|-------|-------------|-------------|
| probe  | 探    | ...   | ...         | ...         |
```

### Responsive Breakpoints

**SPA:**
- Desktop: `.meta-panel` uses `position: sticky` with `top: 1rem; bottom: 1rem`
- Mobile: `.meta-panel` uses `position: fixed; bottom: 0` (full-width drawer)

**TUI2:**
- Narrow terminals (< 80 cols): word-wrap both kanji and use_when
- Wide terminals (>= 80 cols): render side-by-side if space permits

### Content Truncation

Never truncate:
- Kanji (always 1-3 chars, fits in all views)
- use_when (scrollable in detail panels)

## Implementation

**Files modified:**
- `web/src/lib/TokenSelector.svelte` - SPA rendering
- `internal/bartui2/program.go` - TUI2 detail pane
- `internal/barcli/help_llm.go` - Token catalog table

**Test coverage:**
- `web/src/lib/TokenSelector.test.ts` - SPA kanji+use_when display
- `internal/bartui2/program_test.go` - TUI2 kanji+use_when rendering
- `internal/barcli/app_help_cli_test.go` - bar help llm table format

## Consequences

### Benefits
- Clear precedence: both features render, no hidden metadata
- Consistent across surfaces (TUI2, SPA, CLI)
- Mobile-friendly (scrollable detail panels)

### Risks
- Detail panels can grow tall if many tokens have both kanji + use_when
- Small terminals may have cramped layout

### Mitigations
- Use `max-height` constraints on detail panels
- Add vertical scroll for overflow content
- Test on 320px mobile and 80-column terminals

## Future Considerations

If more metadata types are added (e.g., examples, anti-patterns):
1. Establish consistent section ordering in detail panels
2. Consider collapsible sections for lengthy content
3. Add user preference for metadata visibility
