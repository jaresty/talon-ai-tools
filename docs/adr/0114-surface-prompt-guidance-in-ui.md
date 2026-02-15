# ADR-0114: Surface Prompt Guidance Maps in UI Surfaces

## Status

Draft

## Context

### The Problem: Guidance Exists But Is Not Visible

The codebase contains rich selection guidance for tokens in Python maps, but none of the UI surfaces consume or display this guidance to users.

#### What Guidance Exists

**AXIS_KEY_TO_GUIDANCE** (`lib/axisConfig.py:736-788`):
- Channel tokens: warnings about incompatible tasks
  - `codetour`: "Best for code-navigation tasks: fix, make, show, pull. Avoid with sim, sort, probe, diff (no code subject), or plan."
  - `gherkin`: "Best for behavior specification: check, plan, make. Avoid with sim, sort, probe, diff."
  - `code`, `html`, `shellscript`: "Avoid with narrative tasks (sim, probe) that produce prose."
- Form tokens: conflict warnings
  - `contextualise`: "Works well with text-friendly channels. Avoid with output-only channels."
  - `faq`: "Conflicts with executable output channels."
  - `recipe`, `socratic`: Similar conflicts
- Method tokens: usage hints
  - `actors`: "Well-suited for security threat modelling..."
  - `inversion`: "Well-suited for architecture evaluation..."
- Scope tokens
  - `cross`: "Use when the question is about where a concern lives across the system..."

**STATIC_PROMPT_GUIDANCE** (`lib/staticPromptConfig.py:168-173`):
- `fix`: "In bar's grammar, fix means reformat — not debug. To correct defects, use make or show with diagnose, inversion, or adversarial."

**PERSONA_KEY_TO_GUIDANCE** (`lib/personaConfig.py:114-134`):
- Selection hints for persona/intent/tone tokens (ADR-0112)

### Where Guidance Currently Lives

These maps are exported in the grammar payload via `promptGrammar.py`:
- `axis_guidance` section in payload (lines 150-161)
- `static_prompt_guidance` section (lines 174-184)
- `persona_guidance` section (lines 294-311)

### Where Guidance Is NOT Surfaced

Despite being in the payload, **no UI component actually reads or displays the guidance**:

1. **helpHub.py `_cheat_sheet_text()`**: Builds the cheat sheet from axis catalog but does NOT include guidance
2. **modelHelpCanvas.py**: Shows axis-specific help but does NOT include selection guidance
3. **bartui2/program.go**: Shows `Label` and `Description` but does NOT include `guidance` field
4. **modelPatternGUI.py**: Pattern menu does not surface why certain combos work

### Evidence of the Gap

Grep results confirm guidance is not consumed:
- `axis_key_to_guidance_map` defined in `axisConfig.py:810` but only called from `axisCatalog.py:204` (payload building)
- No calls from `helpHub.py`, `modelHelpCanvas.py`, or any TUI component
- Guidance is effectively "dead data" once exported

---

## Decision

### Phase 1: High-Impact Surfaces (Priority 1)

#### 1.1: bartui2 Completions with Guidance

Modify `internal/bartui2/program.go` to:
- Read guidance from the grammar payload
- Display guidance as a third field in completions (Label | Description | Guidance)
- Show warning icon or highlight when guidance exists for a token

Implementation path:
1. Add `Guidance` field to the `completion` struct in Go
2. Populate from `grammar.AxisGuidance()` / `grammar.TaskGuidance()` methods
3. Display in the detail pane when a completion is selected

#### 1.2: helpHub Cheat Sheet with Guidance

Modify `lib/helpHub.py` `_cheat_sheet_text()` to:
- Call `axis_key_to_guidance_map()` for each axis
- Append guidance text next to tokens that have it
- Use a distinctive marker (e.g., "[!]" or "→") to indicate guidance exists

### Phase 2: Medium-Impact Surfaces (Priority 2)

#### 2.1: modelHelpCanvas Axis Help

Modify `lib/modelHelpCanvas.py` to:
- Include guidance when displaying axis-specific help
- Show warnings for tokens with selection hints
- Add "guidance" section in the axis help view

#### 2.2: modelPatternGUI Pattern Suggestions

Modify `lib/modelPatternGUI.py` to:
- Surface guidance about why certain token combinations work
- Show warnings when patterns contain potentially conflicting tokens

---

## Consequences

### Positive
- Users can see selection guidance at point of choice
- Prevents incompatible token combinations before they happen
- Makes the "why" behind guidance discoverable

### Negative
- Additional complexity in UI surfaces
- Guidance text adds to UI clutter if not carefully designed
- Must maintain guidance maps as tokens evolve

### Trade-offs
- Showing all guidance vs. showing on-demand (cheat sheet could get long)
- Guidance in completions vs. guidance on selection (completions are transient)

---

## Alternatives Considered

### Alt 1: Only bar help llm
- Problem: Only CLI users see it, not Talon users
- Rejected: Must surface in Talon UIs

### Alt 2: Tooltips on hover
- Problem: Talon doesn't have reliable hover state
- Rejected: Not feasible in current UI paradigm

### Alt 3: Modal warnings on selection
- Problem: Too intrusive, would annoy users
- Rejected: Bad UX

---

## Implementation Notes

1. Start with bartui2 completions - smallest change, highest visibility
2. Guidance text should be brief (under 50 chars) - existing guidance follows this
3. Consider a "guidance available" indicator first, full text on expand/select
4. Test with users to calibrate how much guidance is too much

---

## Related ADRs

- ADR-0109: Token Labels (short CLI descriptions)
- ADR-0110: Token Guidance Field (the guidance maps being not surfaced)
- ADR-0111: Persona Token Labels and TUI Display
- ADR-0112: Persona Axis Guidance (TUI display)
