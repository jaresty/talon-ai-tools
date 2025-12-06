# 023 – Canvas-Based Response Viewer and Controls

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT response display (`model …`)  
- Related ADRs:  
  - 006 – Pattern Picker and Recipe Recap  
  - 019 – Meta Interpretation Channel and Surfaces  
  - 020 – Richer Meta Interpretation Structure  
  - 021 – Browser Meta and Answer Layout  
  - 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  

## Context

Today, GPT responses are surfaced in three main ways:

- **Paste destinations** (clipboard, insert, etc.) – receive only the **answer** text.  
- **Meta/recap surfaces** – expose the structured meta channel (`last_meta`, recap, pattern picker) as described in ADR 019/020.  
- **Browser destination** (`model … to browser`) – shows:
  - A minimal prompt recap.  
  - A plain-text “Model interpretation” section (meta).  
  - A plain-text “Response” section (answer).  

This has several practical drawbacks inside Talon:

- For **long answers**, users must:
  - Open a full browser window.  
  - Scroll with mouse/trackpad to inspect content.  
  - Context-switch away from Talon, and manually close the browser when done.  
- The browser view is currently the only **scrollable** inspection surface for full answers; imgui UIs are used for menus and quick help, not for the main answer stream.  
- The existing answer/recap GUIs (confirmation, suggestions, quick help) use **Talon GUI primitives**, while the browser response view uses HTML and an external window:
  - This splits the UX into “Talon surfaces” vs. “browser surfaces”.  
  - Buttons and controls (repeat last, tweak axes, open quick help, etc.) are not co-located with the full answer.  

ADR 022 has already shown that:

- A **canvas-based window** can provide:
  - Precise layout.  
  - A draggable, modal-feeling surface.  
  - A richer teaching/inspection experience for grammar and directional lenses.  

We would like a similar, **scrollable canvas window for responses**:

- So that long answers can be read, scrolled, and re-used **without** leaving Talon.  
- With in-panel controls (buttons/shortcuts) for common follow-ups (copy, rerun, open in browser, show meta, tweak axes).  

## Decision

We introduce a **canvas-based response viewer** as the **primary confirmation and inspection surface** for GPT answers and meta inside Talon, while keeping the browser destination as an optional external view.

At the end of this ADR’s implementation:

- The existing **imgui confirmation modal** (`confirmation_gui`) is fully replaced in normal workflows by a canvas implementation:
  - All entrypoints that previously opened the imgui confirmation window now open the canvas response viewer.  
  - The imgui confirmation implementation remains only as a backing surface for shared actions and tests.  
- There is a **`model_response_canvas` window** that:
  - Displays the **current text to confirm / last answer** with internal scrolling.  
  - Optionally displays a compressed and expandable **meta / interpretation summary**.  
  - Provides a set of **inline controls** that reach feature parity with the old confirmation modal, including:
    - Paste response (and mark `last_response` / `last_was_pasted`).  
    - Copy response.  
    - Discard/close.  
    - Pass to context / query / thread.  
    - Open in browser.  
    - Analyze prompt.  
    - Show grammar / quick help.  
    - Open the prompt pattern menu for the last static prompt.  
  - Is draggable, closable via `[X]`/Esc, and uses a centered placement similar to the quick help canvas.  
- We add and standardise voice commands / actions to open or revisit the response viewer, such as:
  - `model last response` → toggle the canvas viewer for `GPTState.last_response`.  
  - Confirmation GUI paths call `model_response_canvas_open()` instead of showing the imgui modal.  
- The browser destination **remains available**, but:
  - The default way to **inspect and act on** answers in Talon is the canvas response viewer.  
  - The browser destination becomes a secondary / optional surface for users who prefer an external HTML window.  

This ADR focuses on the **response viewing, scrolling, and confirmation surface**, not on changing how answers/meta are generated or stored.

### Current status in this repo (2025‑12‑05)

As of the latest work‑log entries for this ADR:

- The **canvas response viewer** (`lib/modelResponseCanvas.py`) is implemented and wired in as the **default confirmation surface**:
  - `ModelDestination.insert` always routes through `actions.user.confirmation_gui_append`, which opens the canvas viewer instead of the legacy imgui modal.  
  - The legacy imgui confirmation GUI remains available only as an implementation detail for shared actions (paste/copy/context/query/thread/browser/analyze/patterns) and tests.  
- The viewer:
  - Opens as a centered, draggable canvas window with a white background, `[X]` close affordance, and Escape‑to‑close.  
  - Displays a **prompt recap** (`Talon GPT Result`, `Prompt recap`, `Recipe: …`, `Say: model …`) derived from `GPTState.last_recipe` / `last_directional`.  
  - Shows a **compact meta interpretation preview** when `GPTState.last_meta` is present:
    - A header toggle `[Show meta]` / `[Hide meta]` lives in the top‑right chrome.  
    - A single‑line summary `Meta: …` (first line of the interpretation) appears under the recap “even before clicking”.  
    - When expanded, a **diagnostic meta panel** (interpretation, assumptions/constraints, gaps/checks, better prompt, axis tweak suggestion, extra notes) renders above the answer body and is explicitly marked as non‑pasteable.  
  - Renders the **answer body** as a scrollable text region:
    - Prefers `GPTState.text_to_confirm` (current confirmation payload), falling back to `GPTState.last_response` when there is no active confirmation.  
    - Applies simple wrapping and bullet handling for readability.  
    - Uses an internal `scroll_y` offset with clamping (no scrolling past the end of content) and a minimal scrollbar drawn on the right edge.  
  - Provides a footer row of **inline controls** that reach feature parity with the old confirmation modal:
    - `[Paste]`, `[Copy]`, `[Discard]`, `[Context]`, `[Query]`, `[Thread]`, `[Browser]`, `[Analyze]`, `[Patterns]`, `[Quick help]`.  
    - Each button forwards to the existing `confirmation_gui_*` / GPT actions and then closes the viewer (except Quick help, which leaves it open).  
- Mouse and keyboard behaviour:
  - Dragging anywhere on the panel moves the window based on global mouse position.  
  - Mouse wheel / trackpad scroll events (`scroll` / `wheel` / `mouse_scroll`) adjust `scroll_y` using pixel deltas when available.  
  - Keyboard shortcuts:
    - Esc → close.  
    - PageUp / PageDown → coarse scroll.  
    - Up/Down / `j`/`k` → fine scroll.  
- Font handling:
  - After experiments with `talon.skia` (`FontMgr`, `FontStyle`, `Typeface`) showed that per‑canvas font overrides are not reliably available on this runtime, the viewer intentionally **does not attempt to change the font family**.  
  - It relies on Talon’s default canvas font; emoji/special glyph coverage is best handled by the browser destination when needed.  

## Design

### 1. Response canvas lifecycle

The module `lib/modelResponseCanvas.py` mirrors the quick help canvas structure from ADR 022, but is specialised for responses:

- A `ResponseCanvasState` singleton tracking:
  - `showing: bool` – whether the viewer is visible.  
  - `scroll_y: float` – current vertical scroll offset for the answer body.  
  - `meta_expanded: bool` – whether the diagnostic meta panel is expanded.  
- Lazy `canvas.Canvas` creation via `_ensure_response_canvas()`:
  - Computes a centered rect on `ui.main_screen()` using a bounded‑center strategy (padding from edges, minimum width/height).  
  - Creates the canvas with `canvas.Canvas.from_rect(rect)` and, when supported, sets `blocks_mouse=True` so underlying windows do not receive clicks while the viewer is open.  
  - Registers:
    - A `"draw"` handler that delegates to a list of draw handlers (`_response_draw_handlers`), with `_default_draw_response` registered by default.  
    - A `"mouse"` handler for close, drag, footer buttons, and a conservative scroll fallback.  
    - `"scroll"` / `"wheel"` / `"mouse_scroll"` handlers for high‑level wheel events, using pixel deltas when available.  
    - A `"key"` handler for Esc / PageUp / PageDown / Up/Down / `j`/`k`.  

The viewer is toggled via `actions.user.model_response_canvas_open()`, which:

- Lazily creates the canvas (if needed).  
- Toggles `ResponseCanvasState.showing`.  
- Resets `scroll_y` to `0.0` when (re)opening or closing.  

### 2. Layout and content

The canvas is laid out as a **single, focused panel**:

- **Header band** at the top:
  - Title: `Model response viewer`.  
  - Close affordance `[X]` in the top‑right, with a hover hotspot.  
  - Compact **prompt recap** when `GPTState.last_recipe` is available:
    - `Talon GPT Result`, `Prompt recap`, `Recipe: …`, and `Say: model …` (derived from recipe + directional lens).  
  - **Meta band** when `GPTState.last_meta` is non‑empty:
    - A single labelled line just under the recap:  
      `Meta (diagnostic) – <short interpretation summary>`  
      where the summary is taken from the parsed interpretation or a first non‑header meta line, truncated with an ellipsis when needed so it does not overlap the toggle or window edge.  
    - A `[Show meta]` / `[Hide meta]` toggle on the same horizontal band (right‑aligned) so the control is visually tied to the meta surface.  
- **Diagnostic meta panel** (optional, non‑scrolling):
  - When `meta_expanded` is true and parsed meta is available, an **indented annotation block** renders **above** the answer body:  
    - Interpretation text (multi‑line).  
    - Assumptions/constraints (bulleted).  
    - Gaps/checks (bulleted).  
    - Better prompt (multi‑line).  
    - Axis tweak suggestion.  
    - Any extra lines.  
  - A short note at the end of this block emphasises that meta is **diagnostic context about how the model read the request**, not part of the main answer body.  
- **Scrollable answer body**:
  - The scroll area starts below the header/meta section (`body_top`), so header + meta do not scroll with the answer.  
  - The answer text source is:
    - First, `GPTState.text_to_confirm` (current confirmation payload; for example, pass‑clip text, thread recap, or destination output).  
    - Otherwise, `GPTState.last_response` (the last LLM answer).  
  - Text is normalised into display lines via `_format_answer_lines`:
    - Word‑boundary wrapping.  
    - Collapsed blank lines.  
    - Simple bullet recognition (`- ` / `* `) with aligned continuation lines (`  • …`).  
  - `scroll_y` is clamped between `0` and `max_scroll = max(content_height − visible_height, 0)` so users cannot scroll into empty space.  
  - A light‑weight scrollbar track and thumb are drawn along the right edge of the body when content overflows.  
- **Response heading and footer row**:
  - A simple `Response:` heading separates diagnostic meta from the pasteable answer, with additional vertical padding before the first line of text.  
  - A row of text buttons: `[Paste] [Copy] [Discard]   [Context] [Query] [Thread]   [Browser] [Analyze] [Patterns] [Quick help]`, where the added spaces reflect slightly larger gaps between the three logical button groups; when the window is too narrow, the footer wraps to a second line instead of overflowing horizontally.  
  - Each button has an absolute hit‑target recorded during draw and is wired in the mouse handler.  
  - The chrome remains intentionally simple and theme‑agnostic (text‑only, no icons), matching ADR 022.  

### 3. Integration with existing workflows

The viewer is integrated into existing workflows as follows:

- **Confirmation flows**:
  - `ModelDestination.insert` always calls `actions.user.confirmation_gui_append(presentation)`.  
  - `confirmation_gui_append` now:
    - Sets `GPTState.text_to_confirm` to the presentation’s display text (or raw string).  
    - Records the current `ResponsePresentation` (for paste/open‑browser behaviour).  
    - Opens the canvas via `actions.user.model_response_canvas_open()`.  
  - The legacy imgui confirmation GUI remains available but is no longer opened by default; it backs shared actions only.  
- **Voice commands**:
  - `model last response` opens or closes the canvas viewer around `GPTState.last_response` (when no active confirmation is present).  
  - Existing confirmation voice flows (for example, “model …”) automatically surface their answers in the canvas.  
- **Browser destination**:
  - Calling `model … to browser` still opens the HTML browser view as described in ADR 021.  
  - The **paste/insert destinations** no longer auto‑fallback to browser for long answers; opening a browser is a deliberate user action via the `[Browser]` footer button or explicit destination choice.  

### 4. Buttons and affordances

Buttons and clickable labels inside the canvas:

- Use text buttons, visually bracketed (for example, `[Paste]`) to keep the surface simple and theme‑agnostic.  
- Are wired to existing actions:
  - `[Paste]` → `confirmation_gui_paste()`; also updates `GPTState.last_response` / `last_was_pasted` and closes the canvas.  
  - `[Copy]` → `confirmation_gui_copy()` + close.  
  - `[Discard]` → `confirmation_gui_close()` + close.  
  - `[Context]` → `confirmation_gui_pass_context()` + close.  
  - `[Query]` → `confirmation_gui_pass_query()` + close.  
  - `[Thread]` → `confirmation_gui_pass_thread()` + close.  
  - `[Browser]` → opens the browser:
    - Prefer the same text as the canvas body (current `text_to_confirm` when present, otherwise `last_response`).  
    - Fall back to `confirmation_gui_open_browser()` when a presentation‑supplied `open_browser` callback is present.  
  - `[Analyze]` → `confirmation_gui_analyze_prompt()` + close.  
  - `[Patterns]` → `confirmation_gui_open_pattern_menu_for_prompt()` + close.  
  - `[Quick help]` → `model_help_canvas_open_for_last_recipe()` (leaves the response canvas open).  
- Treat the **meta header toggle** `[Show meta]` / `[Hide meta]` as another clickable control:
  - Clicking it flips `ResponseCanvasState.meta_expanded` and redraws the viewer.  
  - Its hit‑target is stored alongside the footer buttons.  

Additional controls (for example, “Tighten answer”, “Explain meta”) are intentionally left for future ADRs once this surface is stable.

## Consequences

### Positive

- **Reduced browser dependency** for inspection:
  - Long answers can be read and scrolled entirely within Talon.  
  - Users do not need to context-switch to a full browser window just to read or re-skim a response.  
- **Unified canvas-based UX**:
  - Quick help (ADR 022) and the response viewer share similar chrome:
    - Centered canvas, header band, `[X]`, drag anywhere.  
  - Common interaction patterns (drag, Esc to close, hover hints) become familiar across GPT tools.  
- **Better co-location of controls**:
  - Answer, meta summary, and common actions live in one place.  
  - Users can copy, rerun, or tweak patterns without leaving the viewer.  

### Negative / Risks

- **Canvas complexity**:
  - Implementing smooth scrolling, hit-testing for buttons, and keyboard navigation increases canvas code complexity compared to static UIs.  
  - There is a risk of subtle bugs (for example, scroll offset not clamped properly, click targets misaligned on HiDPI).  
- **Potential performance concerns**:
  - Very long answers might require careful drawing (for example, avoiding re-laying out the entire text on every scroll).  
  - We mitigate this by keeping the implementation simple and text-only, and avoiding heavy shapes or animations.  
- **Overlap with browser layout work (ADR 021)**:
  - We now have two “rich” response surfaces (browser HTML + canvas).  
  - Keeping them conceptually aligned (sections, wording) requires some discipline.  

## Mitigations

- Keep the canvas viewer implementation **conservative**:
  - No rich styling beyond headings, basic spacing, and a few buttons.  
  - No attempt to fully replicate HTML layout; just good-enough paragraph/list grouping.  
- Reuse existing helpers where possible:
  - Meta parsing from ADR 021 / 020.  
  - Canvas patterns (drag, close, header) from ADR 022.  
  - Existing GPT actions for copying, opening browser, patterns, quick help.  
- Add focused tests:
  - Ensure the open/close actions work under the test harness.  
  - Verify that scroll offset is reset when reopening.  
  - Confirm that buttons/handlers call the correct actions (by stubbing `actions.user.*` in tests).  
- Document the intended scope:
  - The canvas viewer is for **reading and light interaction**, not for editing; paste behaviour remains defined by destinations.  
  - Browser layout work (ADR 021) is still valuable for users who prefer external windows or browser-based reading.  

## Next Steps

1. **Keep polishing scroll and drag behaviour**
   - Continue to tune scroll step sizes for different devices (trackpads vs. wheels).  
   - Ensure drag feels smooth across platforms and remains drag‑anywhere on the panel.  

2. **Meta and layout refinements**
   - Make the diagnostic meta panel feel like a distinct, secondary **annotation block**, not part of the main answer:
     - Add a clear “Meta (diagnostic)” label and slightly different styling (for example, lighter text or subtle banding) so users can visually separate it from the response.  
     - Introduce an explicit “Response” heading and additional padding between recap, meta, and answer to break up the current wall of text.  
     - Keep the `[Show/Hide meta]` toggle visually coupled to the meta label (same horizontal band) so its relationship to the block is obvious.  
   - Optionally group footer actions into logical clusters (for example, output actions vs. thread/context vs. analysis/browser) with a bit more spacing to improve scanability.  
   - Consider optional keyboard shortcuts or small visual hints that distinguish “pasteable answer” from “diagnostic meta”.  

3. **Tests and guardrails**
   - Extend tests in `_tests/test_model_response_canvas.py` to cover meta toggle behaviour and answer selection semantics (`text_to_confirm` vs. `last_response`).  
   - Add small end‑to‑end checks for the new confirmation wiring to ensure browser fallback behaviour stays intentional.  
