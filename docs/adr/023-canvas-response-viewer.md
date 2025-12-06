# 023 – Canvas-Based Response Viewer and Controls

- Status: Proposed  
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
- The browser view is currently the only **scrollable** inspection surface for full answers; imgui/canvas UIs are used for menus and quick help, not for the main answer stream.  
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

We will introduce a **canvas-based response viewer** as the **primary confirmation and inspection surface** for GPT answers and meta inside Talon, while keeping the browser destination as an optional external view.

At the end of this ADR’s implementation:

- The existing **imgui confirmation modal** (`confirmation_gui`) will be fully replaced in normal workflows by a canvas implementation:
  - All entrypoints that previously opened the imgui confirmation window will instead open the canvas response viewer.  
  - The imgui confirmation implementation may remain in the repo as a legacy/testing surface, but will no longer be used for day‑to‑day confirmation flows.  
- There will be a **`model_response_canvas` window** that:
  - Displays the **current text to confirm / last answer** with internal scrolling.  
  - Optionally displays a compressed **meta / interpretation summary**.  
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
- We will add and standardise voice commands / actions to open or revisit the response viewer, such as:
  - `model last response` → toggle the canvas viewer for `GPTState.last_response`.  
  - Confirmation GUI paths will call `model_response_canvas_open()` instead of showing the imgui modal.  
- The browser destination will **remain available**, but:
  - The default way to **inspect and act on** answers in Talon will be via the canvas response viewer.  
  - The browser destination becomes a secondary / optional surface for users who prefer an external HTML window.  

This ADR focuses on the **response viewing, scrolling, and confirmation surface**, not on changing how answers/meta are generated or stored.

## Design

### 1. Response canvas lifecycle

We will add a new module `lib/modelResponseCanvas.py` that mirrors the quick help canvas structure:

- A `ResponseCanvasState` singleton tracking:
  - Whether the viewer is currently showing.  
  - Current scroll offset.  
  - Which section is in focus (for example, answer vs. meta).  
- Lazy `canvas.Canvas` creation via `_ensure_canvas()`:
  - Centered on `ui.main_screen()` using a similar “bounded center” strategy as the quick help canvas.  
  - Uses `Canvas.from_rect(Rect(...))` (not `panel=True`) and:
    - Draw handler for layout.  
    - Mouse handler for drag, scroll, and button clicks.  
    - Key handler for Esc to close, PgUp/PgDn / arrow keys to scroll.  
- Actions under `@mod.action_class`:
  - `model_response_canvas_open()` – open/close toggle for the current `GPTState.last_answer`.  
  - `model_response_canvas_close()` – explicit close.  
  - Optionally: `model_response_canvas_open_meta()` – open focusing on meta.  

The viewer should **not** alter the paste destinations; it simply reads from the same `GPTState` answer/meta fields that the browser uses.

### 2. Layout and scrolling model

The response canvas will have a layout roughly analogous to the browser destination’s sections, but adapted for canvas:

- Header band:
  - Title, for example: `Model response viewer`.  
  - Close `[X]` in the top-right, with hover underline.  
- Optional recap strip:
  - Last recipe tokens and `Say: model …` speakable line (as in confirmation GUI / quick help).  
- Main scrollable body:
  - **Answer section** (primary):
    - Rendered in a vertically scrollable region.  
    - Paragraph grouping and bullet detection similar to ADR 021’s browser design.  
    - Scroll controlled by:
      - Mouse wheel / trackpad (if available).  
      - PgUp/PgDn and arrow keys via the key handler.  
  - **Meta summary** (secondary, optional):
    - Either:
      - A compressed one- or two-line summary (for example, “Interpretation: …”) at the top or bottom of the body, **or**  
      - A collapsible section (for example, a `[show meta]` link) that expands the meta summary within the same scroll region.  
    - Uses the same meta parsing as ADR 021 to avoid re-implementing structure parsing.  
- Footer strip:
  - Inline controls (text buttons) aligned left or right, for example:
    - `[Copy answer] [Copy meta] [Open in browser] [Patterns] [Quick help]`.  
  - Click targets handled via the canvas mouse handler; actions delegate to existing `actions.user.*` helpers where possible.

The scroll model:

- Maintain a `scroll_y` offset inside `ResponseCanvasState`.  
- Clamp scroll between 0 and `max(0, content_height - visible_height)`.  
- On mouse wheel / PgUp/PgDn / arrow keys:
  - Adjust `scroll_y`, then request a redraw.  
- Draw the answer/meta content starting at `body_top_y - scroll_y`.  

We will initially keep scrolling **vertical-only** and avoid complex region-resizing; the focus is “can I comfortably read the last answer without opening a browser?”.

### 3. Integration with existing workflows

We will add small, targeted integrations so the viewer feels natural:

- Confirmation GUI:
  - Add a `View in canvas` (or similar) button that calls `model_response_canvas_open()`.  
- Suggestions / pattern picker:
  - Optionally add a `View last answer` button to open the response viewer when relevant.  
- Voice commands:
  - `model last response` → open/close the response viewer.  
  - Later, we may add commands like `model scroll down` / `model scroll up` that call canvas scroll helpers.  

The browser destination remains unchanged; if a user explicitly invokes `model … to browser`, we still open a browser tab/window and render the HTML as in ADR 021.

### 4. Buttons and affordances

Buttons and clickable labels inside the canvas will:

- Use text buttons, visually bracketed (for example, `[Copy answer]`) to keep the surface simple and theme-agnostic.  
- Have hover feedback:
  - Slight underline or colour shift on hover.  
- Invoke existing actions:
  - `Copy answer` → copy `GPTState.last_answer` to clipboard.  
  - `Copy meta` → copy structured meta summary to clipboard.  
  - `Open in browser` → call the existing browser destination action for the last response.  
  - `Patterns` → open the pattern picker for the last recipe.  
  - `Quick help` → open the canvas quick help focused on grammar/directional lenses.  

We will initially keep the button set small and focused; additional controls (for example, “Tighten answer”, “Explain meta”) can be considered in later ADRs.

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
  - We will mitigate by keeping the first iteration simple and text-only, and avoiding heavy shapes or animations.  
- **Overlap with browser layout work (ADR 021)**:
  - We now have two “rich” response surfaces (browser HTML + canvas).  
  - Keeping them conceptually aligned (sections, wording) will require some discipline.

## Mitigations

- Keep the initial canvas viewer implementation **conservative**:
  - No rich styling beyond headings, basic spacing, and a few buttons.  
  - No attempt to fully replicate HTML layout; just good-enough paragraph/list grouping.  
- Reuse existing helpers where possible:
  - Meta parsing from ADR 021.  
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

1. **Scaffold `lib/modelResponseCanvas.py`**
   - Implement canvas lifecycle, state, and basic draw/mouse/key handlers.  
   - Reuse conventions from `modelHelpCanvas` for header, drag, and close.  

2. **Render answer + minimal meta summary**
   - Start with answer-only scroll (no meta), then add a small meta summary once scrolling is robust.  
   - Wire `model_response_canvas_open` to `GPTState.last_answer`.  

3. **Add buttons and basic tests**
   - Implement `[Copy answer]`, `[Open in browser]`, `[Quick help]` as clickable labels.  
   - Add tests around action wiring and state resets.  

4. **Iterate based on real usage**
   - Adjust fonts, margins, and scroll step sizes for readability.  
   - Decide whether to promote the canvas viewer to the **default** inspection surface for long answers or keep it as an explicit opt-in alongside the browser.  
