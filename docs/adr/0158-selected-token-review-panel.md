# ADR-0158: Selected Token Review Panel

## Status

Accepted

## Context

The SPA has 9 axes (persona, task, completeness, scope, method, form, channel, directional, presets). Users select tokens across multiple axes to build prompts. The current UI scatters selection state:

- Command bar shows: `bar build persona=designer_to_pm probe shellscript`
- Selected chips show: `probe ×`, `shellscript ×` (no axis context, buried after subject/addendum inputs)
- Conflict warnings show inline in command box

This creates an **orientation gap**: users cannot quickly answer "what have I built?" without mentally reconstructing state from fragmented locations.

## Decision

Add a **fixed bottom bar** (persistent summary strip) that shows all currently selected tokens across all axes. This bar is the single source of truth for:

1. **Selection state**: axis=token pairs, visible at a glance
2. **Conflicts**: visual indicator on conflicting tokens (dimmed, strikethrough, warning icon)

The command box becomes purely about the generated string. The existing warning in the command box is removed.

### UI Specification

| Element | Behavior |
|---------|----------|
| Bar position | Fixed bottom of viewport, above FAB and action overlay |
| Content | List of `axis=token` pairs (mirrors command format) |
| Interaction | Click token to deselect |
| Conflicts | Conflicting tokens dimmed + strikethrough + warning icon |
| Empty state | Show placeholder text: "Select tokens from the axes above" |
| Accessibility | Keyboard navigation to bar, Enter/Space to deselect (match existing selected-chip behavior) |

### Mobile Considerations

- Bottom bar may compete with FAB and action overlay for viewport space
- Priority: review bar > FAB on mobile (or FAB moves to top-right)
- Height: compact (single line if possible, wrap if needed)

## Consequences

- Conflict warning moves from command box to review panel (single source of truth)
- Command box now purely displays generated command string
- Single place to scan "what have I selected?"
- Single place to see conflicts
- Matches the scanning/selecting user journey (not editing)
- Consistent axis=token format across command bar and review panel
- Minor viewport competition on mobile (FAB placement adjustment)

## Alternatives Considered

- **Collapsible side panel**: Rejected—requires explicit expansion, adds friction for scanning
- **Keep warning in command box**: Rejected—violates single source of truth principle; users check two places
- **Review panel as modal**: Rejected—overkill for a status display; modal implies editing/detailed view

## Test Cases

### Happy Path

**Test: Review panel displays selected tokens**
- **Setup**: User has selected tokens on multiple axes (e.g., `probe` on task, `shellscript` on channel, `voice=as-designer` on persona)
- **Execution**: Load the SPA with these selections active
- **Assertion**: Review panel shows `task=probe`, `channel=shellscript`, `voice=as-designer` in axis=token format

**Test: Click token ins it**
- **Setup**: User review panel deselect has selected `probe` token on task axis
- **Execution**: Click `task=probe` in review panel
- **Assertion**: Token is removed from selection; review panel updates to reflect the change

**Test: Empty state shows placeholder**
- **Setup**: No tokens selected
- **Execution**: Load SPA with clean state
- **Assertion**: Review panel shows placeholder text "Select tokens from the axes above"

### Conflicts

**Test: Conflicting tokens are visually distinct**
- **Setup**: User has selected `probe` (task) and `shellscript` (channel) which are incompatible
- **Execution**: Load SPA with both tokens selected
- **Assertion**: Review panel shows both tokens with visual indicator (dimmed + strikethrough + warning icon)

**Test: Click on conflicting token still deselects it**
- **Setup**: `probe` and `shellscript` selected, conflict shown
- **Execution**: Click the conflicting token in review panel
- **Assertion**: Token is deselected; conflict indicator updates or disappears

### Command Box

**Test: Command box shows no warning after removal**
- **Setup**: `probe` and `shellscript` selected (conflicting)
- **Execution**: Review panel is implemented, command box warning removed
- **Assertion**: Command box displays `bar build probe shellscript` without any warning text

### Accessibility

**Test: Keyboard navigation to review panel**
- **Setup**: Page loaded with selected tokens
- **Execution**: Tab through page elements
- **Assertion**: Review panel is reachable via keyboard; tokens are focusable

**Test: Enter/Space deselects token from review panel**
- **Setup**: `probe` selected, focus on review panel token
- **Execution**: Press Enter or Space
- **Assertion**: Token is deselected

### Mobile

**Test: Review panel visible on mobile viewport**
- **Setup**: Mobile viewport (375px width)
- **Execution**: Load SPA with selections
- **Assertion**: Review panel is visible above the action overlay/FAB

**Test: FAB repositions when review panel is present**
- **Setup**: Mobile viewport, review panel implemented
- **Execution**: FAB button is present
- **Assertion**: FAB is positioned above review panel or moved to top-right

### Edge Cases

**Test: Many selected tokens wrap in review panel**
- **Setup**: User has selected 5+ tokens across different axes
- **Execution**: Load SPA with all selections
- **Assertion**: Review panel wraps to multiple lines without horizontal scroll

**Test: All tokens on single axis displayed**
- **Setup**: Multiple tokens selected on form axis (if multi-select allowed)
- **Execution**: Load SPA with multiple form tokens
- **Assertion**: All selected form tokens appear in review panel
