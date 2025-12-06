# 025 – Canvas Dialog Layout and Scrolling

- Status: Accepted  
- Date: 2025-12-06  
- Context: `talon-ai-tools` GPT canvas dialogs and menus (`model …`)  
- Related ADRs:  
  - 006 – Pattern Picker and Recap  
  - 008 – Prompt Recipe Suggestion Assistant  
  - 019 – Meta Interpretation Channel and Surfaces  
  - 020 – Richer Meta Interpretation Structure  
  - 021 – Browser Meta and Answer Layout  
  - 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
  - 023 – Canvas-Based Response Viewer and Controls  
  - 024 – Canvas Migration for Dialog GUIs  

## Context

ADR 024 migrated the main GPT dialogs and menus in this repo from `imgui` to **canvas-based** implementations:

- Prompt recipe suggestions → `lib/modelSuggestionGUI.py` (canvas).  
- Model pattern picker → `lib/modelPatternGUI.py` (canvas).  
- Prompt-specific pattern picker → `lib/modelPromptPatternGUI.py` (canvas).  
- Quick help → `lib/modelHelpCanvas.py` (canvas).  
- Response viewer / confirmation → `lib/modelResponseCanvas.py` (canvas, from ADR 023).  

These canvases share several design goals:

- Present GPT surfaces as **centered, modal-feeling windows** inside Talon.  
- Keep voice tags (`user.model_suggestion_window_open`, `user.model_pattern_window_open`, `user.model_prompt_pattern_window_open`, `user.model_window_open`) driving GUI-specific commands.  
- Avoid the font and accessibility constraints of `imgui`, while maintaining readable, text-first layouts.  

An initial adversarial review of the new canvases surfaced vertical layout and scrolling concerns:

- The **response viewer** has an explicit scrollable body with a scrollbar and keyboard/mouse scroll handling; long answers are well supported.  
- The **quick help canvas** (`modelHelpCanvas`) uses a large fixed panel height (default ~900px) with no internal scroll; on short screens, the directional map and examples can be clipped.  
- The **model pattern picker** (`modelPatternGUI` canvas) has a finite panel height with no scroll; the writing/product domain in particular has many patterns, so lower entries may be unreachable on typical displays.  
- The **suggestion** and **prompt-pattern** canvases have modest default heights but no scroll; they are safe today with small lists, but future expansion in the number of items risks vertical overflow.  

To keep canvas dialogs robust across screen sizes and future content growth, we should treat **vertical space and scrolling as first-class layout concerns**, not incidental details.

## Decision

We will standardise vertical layout and scrolling for GPT canvas dialogs as follows:

1. **Introduce internal scrolling for tall content regions**, rather than relying solely on fixed panel heights:
   - Quick help (`modelHelpCanvas`) will gain a scrollable body region for the axis summaries, directional map, and optional examples.  
   - The model pattern picker (`modelPatternGUI` canvas) will gain a scrollable pattern list region within each domain.  
2. **Keep headers and primary chrome fixed**:
   - Titles, close affordances (`[X]`), and key tips remain visible while scrolling content below them.  
3. **Make suggestion and prompt-pattern canvases resilient to larger lists**:
   - Add simple vertical scrolling for their list regions once the number of items exceeds a modest threshold.  
   - Until that threshold is reached, their current fixed heights remain acceptable.  
4. **Preserve existing voice and action contracts**:
   - No changes to voice tags or action names (for example, `model prompt recipes`, `model patterns`, `model pattern menu …`, `model quick help`).  
   - Scrolling is additive: users can still click buttons and use voice commands as before.  

This ADR does **not** change substantive behaviour of GPT workflows (what suggestions/patterns/quick help show) or browser-based views; it focuses only on **layout, scrolling, and vertical resilience** of the Talon canvas dialogs.

## Implementation Sketch

1. **Shared scrolling primitives (optional but preferred)**
   - Add a small internal helper for canvas dialogs (in a shared module or as a pattern) that can:
     - Track a `scroll_y` offset for a given content region.  
     - Compute visible lines or items for that region based on `rect.height` and line height.  
     - Draw a minimal vertical scrollbar (track + thumb) when content exceeds the visible height.  
   - Reuse the response viewer’s approach as a reference for scroll behaviour and scrollbar drawing.  

2. **Quick help canvas (`lib/modelHelpCanvas.py`)**
   - Introduce a `HelpCanvasState.scroll_y` for the body region (below the header band).  
   - Update `_default_draw_quick_help` to:
     - Measure total content height for the sections chosen by `HelpGUIState.section`.  
     - Clamp and apply `scroll_y` when rendering lines (similar to the response viewer’s answer body).  
     - Draw a thin scrollbar on the right edge when content height exceeds the visible height.  
   - Extend the canvas `mouse`/`key` handlers to:
     - Adjust `scroll_y` on wheel/scroll events and PageUp/PageDown / j/k / up/down when the pointer is inside the panel.  
   - Keep the header (title, close button, summary hints) pinned at the top while only the body scrolls.  

3. **Model pattern picker canvas (`lib/modelPatternGUI.py`)**
   - Introduce a `PatternCanvasState.scroll_y` for the pattern list region when a domain is selected.  
   - In `_draw_pattern_canvas`:
     - Reserve a fixed header area for the title + tips.  
     - For the pattern list, compute visible range based on `scroll_y`, line height, and available body height.  
     - Only render the subset of patterns that fit in the visible window, and draw a scrollbar when necessary.  
   - Update the canvas `mouse`/`key` handlers to scroll the pattern list:
     - Mouse wheel inside the panel adjusts `scroll_y`.  
     - Up/Down / j/k (and optionally PageUp/PageDown) scroll the list in small/large increments.  
   - Keep per-pattern content concise (button label + recipe + “Say: …” line), but do not change semantics in this ADR.  

4. **Suggestion canvas (`lib/modelSuggestionGUI.py`)**
   - Keep the default `_PANEL_HEIGHT` but:
     - Add a `SuggestionCanvasState.scroll_y` when `len(suggestions)` exceeds a small threshold (for example, > 6).  
     - For many suggestions, render only the visible subset based on `scroll_y` and available body height; add a scrollbar column on the right.  
   - Make mouse wheel and basic keys (Up/Down / PageUp/PageDown) drive `scroll_y` when focus is inside the panel.  
   - Preserve per-item layout (button + “Say: …” hint) and click semantics.  

5. **Prompt-pattern canvas (`lib/modelPromptPatternGUI.py`)**
   - Mirror the suggestion canvas approach, but for `PROMPT_PRESETS`:
     - Add a `PromptPatternCanvasState.scroll_y` and apply scrolling when the number of presets (or their rendered height) exceeds the visible area.  
   - Keep the prompt header, profile defaults, and grammar skeleton fixed; only scroll the preset list section.  

6. **Testing and diagnostics**
   - Extend or add tests (within Talon’s test harness constraints) to cover:
     - That opening each canvas with many items does **not** raise errors and that the corresponding `scroll_y` fields are initialised and updated via the actions/handlers.  
     - That scroll-related state stays bounded and does not underflow/overflow (for example, `scroll_y >= 0` and clamped to content height minus visible height).  
   - Prefer behavioural tests (for example, calling scroll actions or simulating wheel events under the stub canvas) over pixel-perfect layout assertions.  

## Consequences

### Positive

- **More robust dialogs on small screens**: Tall content (axes, examples, long pattern lists, many suggestions) no longer depends solely on panel height; users can scroll instead of losing access to lower items.  
- **Consistent interaction model**: All major GPT canvases share a similar scroll behaviour, reducing surprise (response viewer, quick help, patterns, suggestions, prompt patterns).  
- **Future-proofing**: Adding new patterns, presets, or help content is less likely to require revisiting panel heights or trimming content for vertical fit.  

### Negative

- Slightly more **complex drawing and state** in canvas modules (scroll offsets, visible ranges, scrollbars).  
- Some tests may need to be adjusted to account for new state fields (`scroll_y`) and the presence of scroll handlers.  

### Risks and Mitigations

- **Risk**: Scroll behaviour may be inconsistent across Talon versions or platforms (different event shapes for wheel/scroll).  
  - **Mitigation**: Follow the proven pattern in `modelResponseCanvas.py` for handling `mouse_scroll` / `wheel` / `scroll` events and clamp deltas defensively.  
- **Risk**: Over-scrolling or awkward thresholds could make short lists feel harder to navigate.  
  - **Mitigation**: Only enable scrolling behaviour when content height clearly exceeds the visible region (for example, more than N items or measured pixel height). For short lists, behave exactly as today.  
- **Risk**: Scrollbars and hit regions may be visually subtle under some themes.  
  - **Mitigation**: Use simple, high-contrast scroll tracks and thumbs that match the existing response viewer style; prioritise legibility over heavy decoration.  

## Current Status (2025-12-06)

For this repo:

- The **suggestion canvas** (`lib/modelSuggestionGUI.py`) now maintains a `scroll_y` offset, renders only the visible subset of suggestions, and shows a simple scrollbar when there are more rows than fit vertically.  
- The **model pattern picker** (`lib/modelPatternGUI.py`) maintains a per-domain `scroll_y`, scrolls the pattern list region with the mouse wheel, and draws a scrollbar when patterns exceed the visible area.  
- The **prompt-pattern picker** (`lib/modelPromptPatternGUI.py`) scrolls its preset list via `PromptPatternCanvasState.scroll_y`, with a matching scrollbar, while keeping the prompt header/profile/grammar template fixed.  
- The **quick help canvas** (`lib/modelHelpCanvas.py`) exposes a basic vertical scroll offset (`HelpCanvasState.scroll_y`) that is adjusted by mouse wheel events and applied to the overall content `y` origin, allowing tall quick-help content to be inspected even on smaller displays.  
- Behavioural tests for these canvases remain green:
  - Suggestions: `_tests/test_model_suggestion_gui.py`, `_tests/test_integration_suggestions.py`.  
  - Model patterns: `_tests/test_model_pattern_gui.py`.  
  - Prompt patterns: `_tests/test_prompt_pattern_gui.py`.  
  - Quick help: `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`.  
- No voice tags, action names, or GPT semantics were changed as part of this ADR; the scroll behaviour is additive and fully compatible with ADRs 022–024.  
