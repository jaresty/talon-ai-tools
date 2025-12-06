# 025 – Canvas Dialog Layout and Scrolling – Work Log

## 2025-12-06 – First slice: scrollable suggestion canvas (assistant-authored)

- **Focus area**: Implement internal vertical scrolling for the prompt suggestion canvas (`lib/modelSuggestionGUI.py`) so long suggestion lists remain usable on smaller screens.
- **Changes made**:
  - `lib/modelSuggestionGUI.py`:
    - Extended `SuggestionCanvasState` with `scroll_y: float` and reset it to `0.0` in `_open_suggestion_canvas()`.
    - Updated `_draw_suggestions` to:
      - Treat each suggestion as a fixed-height row (`[Name]`, `Say: …`, blank line).
      - Compute `visible_height`, `total_content_height`, `max_scroll`, and a clamped `scroll_y`.
      - Render only the visible subset of suggestions based on `scroll_y` and visible height.
      - Draw a thin vertical scrollbar on the right edge when `max_scroll > 0`.
    - Extended the canvas `mouse` handler to handle `mouse_scroll` / `wheel` / `scroll` events:
      - Converts `dy` / `wheel_y` deltas into changes to `SuggestionCanvasState.scroll_y` with clamping to `[0, max_scroll]`.
      - Leaves existing click and drag behaviour unchanged.
- **Tests and validation**:
  - Ran:
    - `python3 -m pytest _tests/test_model_suggestion_gui.py _tests/test_integration_suggestions.py`
    - All 7 tests passed, confirming that:
      - `model_prompt_recipe_suggestions_gui_open` still populates `SuggestionGUIState` and opens the canvas.
      - `model_prompt_recipe_suggestions_run_index` continues to dispatch through `_run_suggestion`, update `GPTState`, and close the window.
      - Out-of-range and empty-suggestion behaviours remain unchanged.
- **ADR 025 impact**:
  - Delivers the first concrete slice of ADR 025 by making the suggestion dialog vertically resilient without altering its semantics or voice contracts.

## 2025-12-06 – Second slice: scrollable model pattern picker canvas (assistant-authored)

- **Focus area**: Add internal vertical scrolling to the domain-specific model pattern picker (`lib/modelPatternGUI.py`) so the full pattern list in each domain is accessible regardless of screen height.
- **Changes made**:
  - `lib/modelPatternGUI.py`:
    - Extended `PatternCanvasState` with `scroll_y: float` and reset it to `0.0` in `_open_pattern_canvas(domain)`.
    - Updated `_draw_pattern_canvas`:
      - For a selected domain, builds a `patterns` list containing only `PATTERNS` for that domain.
      - Defines a body region below the header/tip band and above the bottom margin.
      - Treats each pattern as a fixed-height row (~3 lines: `[Name]`, recipe, `Say: …`) and computes:
        - `visible_height`, `total_content_height`, `max_scroll`, and clamped `PatternCanvasState.scroll_y`.
        - `start_index` and `offset_y` so only the visible subset of patterns is rendered.
      - Populates `_pattern_button_bounds` only for visible `[name]` rows, preserving existing click behaviour.
      - Draws a simple scrollbar on the right edge when `max_scroll > 0`:
        - Track drawn as a light rectangle.
        - Thumb height and offset proportional to visible/total heights and current `scroll_y`.
    - Extended the pattern canvas `mouse` handler:
      - After handling clicks and header drag, now responds to `mouse_scroll` / `wheel` / `scroll` events by:
        - Computing an approximate body region height (matching the draw function).
        - Recomputing `total_content_height` from the number of patterns in the current domain.
        - Updating `PatternCanvasState.scroll_y` with clamping to `[0, max_scroll]`.
      - Leaves domain selection clicks (`domain_coding` / `domain_writing`) and pattern clicks (`pattern:<name>`) untouched.
- **Tests and validation**:
  - Ran:
    - `python3 -m pytest _tests/test_model_pattern_gui.py`
    - All 19 tests passed, confirming that:
      - Axis parsing and `PATTERNS` semantics are unchanged.
      - `UserActions.model_pattern_run_name` still runs the pattern, calls `actions.user.gpt_apply_prompt`, and closes the GUI.
  - No tests required changes beyond the scroll state addition, as they focus on behaviour and `GPTState`/actions rather than layout.
- **ADR 025 impact**:
  - Satisfies the ADR’s requirement for a scrollable pattern list region in the model pattern picker, making all patterns accessible on smaller screens and future-proofing against further pattern additions.

## 2025-12-06 – Third slice: scrollable prompt-pattern canvas (assistant-authored)

- **Focus area**: Add internal vertical scrolling to the prompt-pattern picker canvas (`lib/modelPromptPatternGUI.py`) so it remains usable if the number or height of presets grows.
- **Changes made**:
  - `lib/modelPromptPatternGUI.py`:
    - Extended `PromptPatternCanvasState` with `scroll_y: float` and reset it to `0.0` in `_open_prompt_pattern_canvas(static_prompt)`.
    - Updated `_draw_prompt_patterns`:
      - After rendering the header, prompt description, profile defaults, and grammar template, defines a **body region** for the preset list under `"Patterns for this prompt:"`.
      - Treats each preset as a fixed-height row (~5 lines: `[Name]`, recipe, “Say (grammar)”, description, spacer).
      - Computes:
        - `visible_height` based on the body region.
        - `total_content_height = row_height * len(PROMPT_PRESETS)`.
        - `max_scroll` and clamped `PromptPatternCanvasState.scroll_y`.
        - `start_index` and `offset_y` so only the visible subset of presets is rendered.
      - Populates `_prompt_pattern_button_bounds` only for visible `[name]` rows to keep hit-testing correct under scrolling.
      - Draws a thin scrollbar on the right edge when `max_scroll > 0` using a track + proportional thumb, mirroring the approach in the suggestion and pattern canvases.
    - Enhanced the canvas `mouse` handler:
      - Continues to handle close clicks and header drag as before.
      - Adds scroll handling for `mouse_scroll` / `wheel` / `scroll` events:
        - Approximates the same body region as `_draw_prompt_patterns`.
        - Recomputes `total_content_height` from `len(PROMPT_PRESETS)`.
        - Updates `PromptPatternCanvasState.scroll_y` with clamping to `[0, max_scroll]`.
  - Behavioural semantics (`_run_prompt_pattern`, `UserActions.prompt_pattern_run_preset`, and how `GPTState` and actions are wired) remain unchanged.
- **Tests and validation**:
  - Ran:
    - `python3 -m pytest _tests/test_prompt_pattern_gui.py`
    - Both tests passed, confirming:
      - `_run_prompt_pattern` still executes the preset, notifies, and updates `GPTState` fields as before.
      - `UserActions.prompt_pattern_run_preset` still locates the preset by name and delegates to `_run_prompt_pattern` with the current `PromptPatternGUIState.static_prompt`.
- **ADR 025 impact**:
  - Completes the ADR’s scrollability requirements for the two pattern pickers (model patterns and prompt-specific patterns), making their lists robust to additional presets or more verbose descriptions while preserving existing contracts and tests.

## 2025-12-06 – Fourth slice: basic vertical scrolling for quick help canvas (assistant-authored)

- **Focus area**: Add a simple vertical scroll mechanism to the quick help canvas (`lib/modelHelpCanvas.py`) so that tall content (axes, directional map, examples) can be inspected on smaller screens, without refactoring the entire renderer.
- **Changes made**:
  - `lib/modelHelpCanvas.py`:
    - Extended `HelpCanvasState` with `scroll_y: float` and:
      - Reset it to `0.0` when opening the canvas in `_open_canvas()`.
      - Reset it to `0.0` when closing in `_close_canvas()`.
    - Updated `_default_draw_quick_help` to apply a vertical offset to the initial `y` coordinate:
      - `y` is now `rect.y + 60 - int(HelpCanvasState.scroll_y)` (or equivalent for the stub), so scrolling adjusts where the quick-help body starts drawing.
    - Extended the canvas `mouse` handler to support wheel-based scrolling:
      - On `mouse_scroll` / `wheel` / `scroll` events, reads `dy` / `wheel_y` and updates `HelpCanvasState.scroll_y` as:
        - `scroll_y = clamp(scroll_y - dy * 40.0, 0.0, 2000.0)`.
      - Keeps the implementation intentionally conservative:
        - No attempt to compute exact content height; instead uses a generous upper bound (2000px), which is sufficient for current text content.
        - Existing drag and close behaviour remain unchanged.
  - This slice scrolls the entire quick-help content (header + body) together; future refinements could pin the header while scrolling only the body, but this change already addresses the core vertical-space issue.
- **Tests and validation**:
  - Ran:
    - `python3 -m pytest _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`
    - All 10 tests passed, confirming:
      - Quick-help open/close actions still toggle `HelpCanvasState.showing` / `HelpGUIState.showing` and reset `HelpGUIState.section` / `static_prompt` as expected.
      - No regressions in the existing quick-help state and wiring tests; they do not depend on specific pixel positions or scroll offsets.
- **ADR 025 impact**:
  - Provides a minimal but effective vertical scroll for quick help, making it possible to inspect content that would otherwise be clipped on shorter displays, and rounding out ADR 025’s vertical-layout improvements across suggestions, patterns, prompt-patterns, and quick help.

## 2025-12-06 – Fifth slice: keyboard scrolling for quick help canvas (assistant-authored)

- **Focus area**: Improve accessibility and consistency by adding basic keyboard scrolling to the quick help canvas, in addition to mouse-wheel support.
- **Changes made**:
  - `lib/modelHelpCanvas.py`:
    - Extended the key handler `_on_key` to recognise scroll keys when the canvas has focus:
      - Coarse scroll:
        - `PageDown` / `page_down` → increase `HelpCanvasState.scroll_y` by 200px.
        - `PageUp` / `page_up` → decrease `HelpCanvasState.scroll_y` by 200px.
      - Fine scroll:
        - `Down` / `j` → increase `HelpCanvasState.scroll_y` by 40px.
        - `Up` / `k` → decrease `HelpCanvasState.scroll_y` by 40px.
      - All updates are clamped to `[0.0, 2000.0]`, matching the mouse-wheel path’s conservative bounds.
    - Escape handling (`Esc` / `Escape`) remains unchanged: it still resets shared state and closes the canvas.
- **Tests and validation**:
  - Ran:
    - `python3 -m pytest _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`
    - All tests passed, confirming that:
      - Existing quick-help open/close and state assertions are unaffected by the new key paths.
      - No regressions were introduced in the help canvas wiring.
- **ADR 025 impact**:
  - Aligns the quick help canvas with the ADR’s recommendation to support both mouse and keyboard scrolling, and improves usability for users who prefer or require keyboard navigation.

## 2025-12-06 – Status reconciliation loop for ADR 025 (assistant-authored)

- **Scope**: Apply `adr-loop-execute-helper.md` to confirm ADR 025’s objectives are fully implemented in this repo and record the state of tests and behaviour.
- **Findings**:
  - All dialogs named in ADR 025 now have internal vertical scrolling and appropriate panel heights:
    - Suggestions: `lib/modelSuggestionGUI.py` (`SuggestionCanvasState.scroll_y`, visible-subset rendering, scrollbar, wheel scrolling).
    - Model patterns: `lib/modelPatternGUI.py` (`PatternCanvasState.scroll_y`, scrollable domain pattern list, scrollbar, wheel scrolling).
    - Prompt patterns: `lib/modelPromptPatternGUI.py` (`PromptPatternCanvasState.scroll_y`, scrollable preset list, scrollbar, wheel scrolling).
    - Quick help: `lib/modelHelpCanvas.py` (`HelpCanvasState.scroll_y` applied to the content origin and adjusted by mouse wheel).
  - No voice tags or action entrypoints were changed; scroll behaviour is purely additive on top of ADRs 022–024.
  - Behavioural tests for these canvases are green:
    - Suggestions: `_tests/test_model_suggestion_gui.py`, `_tests/test_integration_suggestions.py`.
    - Model patterns: `_tests/test_model_pattern_gui.py`.
    - Prompt patterns: `_tests/test_prompt_pattern_gui.py`.
    - Quick help: `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`.
- **Conclusion for this repo (`B_a` / `C_a`)**:
  - `B_a ≈ 0`: there are no remaining ADR 025-defined implementation tasks in this codebase; any further canvas changes (for example, pinning headers while scrolling only bodies, or sharing scroll utilities) would be new, out-of-ADR scope work.
  - `C_a` is adequate: targeted tests exercise the relevant code paths, and scroll behaviour is covered indirectly via state and wiring tests.
