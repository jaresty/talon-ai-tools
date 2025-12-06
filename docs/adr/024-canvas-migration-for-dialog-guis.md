# 024 – Canvas Migration for Dialog GUIs

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT dialogs and menus (`model …`)  
- Related ADRs:  
  - 006 – Pattern Picker and Recap  
  - 008 – Prompt Recipe Suggestion Assistant  
  - 019 – Meta Interpretation Channel and Surfaces  
  - 020 – Richer Meta Interpretation Structure  
  - 021 – Browser Meta and Answer Layout  
  - 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
  - 023 – Canvas-Based Response Viewer and Controls  

## Context

The current GPT UI surfaces in Talon span two families of primitives:

- **Legacy `imgui` dialogs**, including:
  - `modelHelpGUI` (`lib/modelHelpGUI.py`) – grammar quick reference and axis lists.  
  - `modelConfirmationGUI` (`lib/modelConfirmationGUI.py`) – confirmation / paste modal (now mostly a shell around shared actions).  
  - `modelSuggestionGUI` (`lib/modelSuggestionGUI.py`) – prompt recipe suggestions.  
  - `modelPatternGUI` (`lib/modelPatternGUI.py`) – domain-based model pattern picker.  
  - `modelPromptPatternGUI` (`lib/modelPromptPatternGUI.py`) – static-prompt-specific pattern picker.  
- **Canvas-based windows**, introduced in ADR 022 and ADR 023:
  - `modelHelpCanvas` (`lib/modelHelpCanvas.py`) – canvas quick help for grammar, axes, and directional map.  
  - `modelResponseCanvas` (`lib/modelResponseCanvas.py`) – canvas response viewer and confirmation surface.  

ADR 022 and ADR 023 intentionally treated canvas UIs as **primary surfaces** for quick help and responses, while keeping the `imgui` implementations as:

- Fallbacks during migration.  
- Shared homes for domain helpers and actions.  

In practice, this leaves us with:

- Two UI stacks (imgui + canvas) for similar concerns.  
- Extra coordination cost when wiring new behaviour (every button or action must be plumbed through both stacks).  
- Accessibility and layout constraints driven by `imgui` even where canvases already provide better affordances (scrolling, coordinate maps, draggable panels).  

We now have stable patterns for:

- **Canvas state singletons** (`HelpCanvasState`, `ResponseCanvasState`).  
- **Lazy canvas construction** and lifecycle (`_ensure_canvas`, `_ensure_response_canvas`).  
- **Shared action wiring** that keeps paste/copy/context/query/thread/browser/meta/patterns behaviour consistent across surfaces.  

This is a good point to **finish the migration** and treat canvas windows as the canonical GUI surface for Talon GPT interactions.

## Decision

We will:

1. **Migrate all remaining GPT dialogs from `imgui` to canvas-based implementations**, using the patterns and helpers from ADR 022/023.  
2. **Remove the legacy `imgui` dialog code paths** once the canvas equivalents reach feature parity and tests are updated.  
3. **Standardise on a small set of canvas surfaces** as the canonical Talon GUIs for GPT:
   - Quick help / grammar and directional map (help canvas).  
   - Response viewer and confirmation (response canvas).  
   - Pattern pickers and suggestion menus (new small canvases sharing the same layout conventions).  
4. **Retain shared domain logic** (pattern definitions, prompt construction, axis helpers) in reusable modules so that canvas GUIs consume them without duplicating behaviour.  

Concretely, this ADR commits us to:

- Designing **canvas replacements** for:
  - Prompt recipe suggestions (replacing `model_suggestion_gui`).  
  - Model patterns (`model_pattern_gui`), with domain tabs or sections.  
  - Prompt-specific patterns (`prompt_pattern_gui`), scoped to a static prompt.  
  - Any remaining `imgui`-only quick-help entrypoints still relying on `model_help_gui`.  
- Updating **voice actions and tags** so that:
  - Commands that today open `imgui` dialogs instead open the appropriate canvas window.  
  - Window-open tags (for example, `user.model_pattern_window_open`, `user.model_prompt_pattern_window_open`, `user.model_suggestion_window_open`) are driven by canvas state rather than `imgui.showing`.  
- Deleting or deprecating:
  - Direct uses of `imgui.open()` for GPT dialogs in `lib/`.  
  - Test paths and helper actions that assume `imgui` windows are the primary UI.  

The browser destination (ADR 021) remains available as an optional external surface; this ADR only concerns **Talon-native dialogs and menus**.

## Current Status (2025-12-05)

For this repo:

- Prompt recipe suggestions, model pattern picker, prompt-specific pattern picker, and quick help are all implemented as **canvas-based GUIs** with consistent chrome and interaction patterns.  
- The legacy `imgui` dialogs `modelHelpGUI`, `modelSuggestionGUI`, `modelPatternGUI`, and `prompt_pattern_gui` have been **removed**; their behaviour is now served by the corresponding canvas modules.  
- Voice tags and commands (`user.model_suggestion_window_open`, `user.model_pattern_window_open`, `user.model_prompt_pattern_window_open`) are driven by canvas state and continue to work without changes to spoken grammar.  
- Tests that previously targeted the imgui GUIs have been updated to exercise the canvas-backed actions and shared quick-help/pattern state.  
- The remaining `imgui` surface (`modelConfirmationGUI`) is intentionally retained only as a backing implementation detail for ADR 023; confirmation and response viewing are canvas-first (`modelResponseCanvas`).  

## Implementation Sketch

1. **Introduce canvas primitives for small menus**
   - Extract shared helpers for:
     - Button rows / stacked buttons.  
     - Scrollable lists with “Say: …” grammar hints.  
     - Basic chrome (title, `[X]` close, drag-anywhere behaviour) reused across all GPT canvases.  
   - Align styling and placement with `modelHelpCanvas` / `modelResponseCanvas` (centered panels, consistent padding and fonts).  

2. **Canvas prompt recipe suggestion window**
   - Add a `SuggestionCanvasState` and `model_suggestion_canvas_open/close` actions mirroring `SuggestionGUIState`.  
   - Render:
     - A header (`Prompt recipe suggestions`).  
     - One button per suggestion, showing name, recipe, and a `Say: model …` hint derived from `GPTState.last_suggest_source`.  
   - Wire:
     - `model_prompt_recipe_suggestions_gui_open` / `…_close` to call the canvas actions instead of `imgui.show()/hide()`, preserving existing voice command names.  
   - Once behaviour is stable, remove `@imgui.open()` and the `model_suggestion_gui` function.  

3. **Canvas model pattern picker**
   - Introduce a `PatternCanvasState` with current domain, scroll offsets, and open flag.  
   - Implement a `model_pattern_canvas_open_*` family that:
     - Mirrors the domain selection flow in `model_pattern_gui` (coding vs writing/product/reflection).  
     - Renders pattern buttons and grammar hints using the existing `PATTERNS` list and `_run_pattern` helper.  
   - Update actions (`model_pattern_gui_open`, `_coding`, `_writing`, `_close`, `model_pattern_run_name`) to delegate to the canvas implementation and tags.  
   - Remove `@imgui.open()` + `model_pattern_gui` once tests pass.  

4. **Canvas prompt-specific pattern picker**
   - Create a prompt pattern canvas that:
     - Accepts a static prompt and profile from `staticPromptConfig`.  
     - Renders profile defaults, grammar skeleton, and the `PROMPT_PRESETS` list with buttons and `Say (grammar): …` lines.  
   - Update `prompt_pattern_gui_open_for_static_prompt`, `prompt_pattern_gui_close`, and `prompt_pattern_run_preset` to use this canvas surface.  
   - Remove the `prompt_pattern_gui` `imgui` function after migration.  

5. **Retire legacy quick help `imgui` surface**
   - Confirm that all quick-help entrypoints and links from other canvases (for example, “Show grammar help” from the response viewer) route through `modelHelpCanvas`.  
   - For any remaining references to `model_help_gui`:
     - Replace with `model_help_canvas_*` entrypoints.  
     - Remove the `model_help_gui` implementation and its `imgui` import once no callers remain.  

6. **Testing and diagnostics**
   - Extend existing tests to cover:
     - Opening/closing each new canvas via the current user actions.  
     - Correct use of `GPTState` and prompt configuration helpers when buttons are clicked.  
     - Tag lifecycles for window-open tags used in Talon grammars.  
   - Keep tests focused on **behaviour and wiring**, not pixel-perfect layout.  

## Consequences

### Positive

- **Single UI primitive** for in-Talon GPT dialogs, reducing coordination cost and cognitive load.  
- **Better layout and interaction** for all dialogs:
  - Draggable, scrollable, and more predictable than `imgui` under long content.  
  - Consistent chrome and keyboard behaviour (Esc to close, etc.) across help, responses, patterns, and suggestions.  
- **Clearer domain homes**:
  - Domain logic (patterns, prompts, axes) lives in shared helpers.  
  - Canvas modules focus on rendering and interaction only.  
- **Easier future iteration** on accessibility and theming, since canvas is the single place to improve font handling, contrast, and hit targets.  

### Negative

- Short-term **migration cost**:
  - Implementing three new canvas surfaces.  
  - Updating callers, tags, and tests.  
- Potential for **regressions in edge-case flows** (for example, very long pattern lists or suggestion sets) until the canvas menus see enough real usage.  

### Risks and Mitigations

- **Risk:** Users rely on established `imgui` behaviours (for example, exact window placement).  
  - **Mitigation:** Keep canvas placement familiar (centered panels, similar sizing), and ensure voice commands and action names remain stable.  
- **Risk:** Canvas APIs behave differently across platforms or Talon builds.  
  - **Mitigation:** Reuse proven patterns from `modelHelpCanvas` and `modelResponseCanvas`, constrain drawing to primitives that are already in production use, and fall back to browser surfaces for highly formatted content.  
- **Risk:** Over-coupling canvas code with GPT state.  
  - **Mitigation:** Keep state singletons thin, and route all GPT interactions through existing helpers (`GPTState`, `modelPrompt`, `ApplyPromptConfiguration`, pattern maps).  
