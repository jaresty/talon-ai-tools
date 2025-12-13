# 022 – Canvas‑Based Quick Help GUI for Model Grammar and Directional Map

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT `model` quick help / grammar reference (`model quick help`, axis‑specific variants, directional map)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
  - 012 – Style and Method Prompt Refactor  
  - 016 – Directional Axis Decomposition and Simplification  
  - 019 – Meta Interpretation Channel and Surfaces  
  - 020 – Richer Meta Interpretation Structure  

## Context

The current quick help GUI (`lib/modelHelpGUI.py`) is implemented with `talon.imgui` and is designed to:

- Teach the **model grammar** (static prompts + axes + directional lens).  
- Surface **axis vocab lists** for completeness/scope/method/style.  
- Provide **examples** and a short **directional lens** explanation.  
- Show a simple **last‑recipe recap** when opened in context.  

Recent work (ADR 016 and subsequent slices) has:

- Clarified the **directional lens axis** and its mapping to abstract/grounded and reflect/act stances.  
- Tried to present directional lenses as a **coordinate map** (up/down vs left/right) inside quick help.  

However, there are practical constraints:

- `talon.imgui` uses the system/UI proportional font, with **no supported way from user code to force a monospaced font** or change the font family for a single GUI.  
- ASCII tables and coordinate diagrams **do not align reliably** in proportional fonts, even with careful spacing and wrapping.  
- The directional section is now textually correct but still **visually noisy and hard to scan** compared to a true grid/diagram.  
- We would like to:
  - Show a **clear XY map** for directional lenses (abstract/center/concrete × reflect/mixed/act).  
  - Potentially introduce small visual cues (boxes, shading, arrows) and richer typography (emoji, emphasis) without fighting imgui’s layout.  

Talon’s `canvas` API:

- Allows choosing a **monospaced or emoji‑capable font** per window.  
- Supports **absolute positioning** and drawing primitives (rectangles, lines, text).  
- Is already proven in more advanced Talon UIs (for example, talon‑hud).  

Given these constraints and goals, it is reasonable to treat imgui as the wrong tool for the most visual parts of quick help, especially the directional map.

## Decision

We will introduce a **canvas‑based quick help GUI** dedicated to the model grammar and directional map, while keeping the existing imgui quick help as a fallback during the transition.

At the end of this ADR’s implementation:

- The **imgui-based quick help GUI will be fully replaced** by a canvas implementation for all quick-help entrypoints.  
- There will be a **canvas window** (`model_help_canvas`) that:
  - Uses the Talon canvas text API (shared `canvas.paint`) so layout is no longer constrained by imgui’s vertical flow, while still respecting Talon’s platform font choices.  
  - Renders the grammar axes and directional lens map as an explicit **XY coordinate map** (abstract/center/concrete × reflect/mixed/act). The initial implementation may present this as **clearly labelled rows and columns of text** rather than fully boxed diagrams; box outlines or richer visuals are treated as optional follow‑up polish.  
  - Supports minimal interactivity (close button, scroll if needed).  
- The primary user command `model quick help` will **open the canvas‑based quick help**, and all axis‑specific quick help commands (for example, `model quick help completeness` / `scope` / `method` / `style` / directional) will be **portals into the same canvas view**, not separate imgui surfaces.  
- Once the canvas view reaches feature parity, the existing imgui quick help implementation will be **removed** (kept only in history); tests and docs will be updated to treat the canvas version as the canonical quick help surface.  

This ADR does **not** change the model grammar, axes, or directional semantics themselves—it only changes how they are visualised and taught in‑Talon.

### Current status in this repo (2025‑12‑05)

As of the latest work-log entries for this ADR:

- All quick-help entrypoints (`model quick help`, axis-specific variants, directional, examples, and `model show grammar`) are wired to the **canvas-based** quick help actions.  
- The canvas view:
  - Renders the grammar skeleton, last-recipe recap (`Last recipe` + `Say: model …`), two-column axis summaries, and a directional coordinate map.  
  - Provides focused entrypoints for completeness/scope/method/style/directional/examples that visually emphasise the chosen section.  
  - Supports mouse-based close (`[X]` hotspot), Escape-to-close, and basic header drag behaviour.  
- The legacy imgui quick help implementation remains only as:
  - A shared source of axis helpers and examples content, and  
  - A target for `tests/test_model_help_gui.py`, which now acts as a legacy regression guard.  

Taken together, ADR 022 is considered **implemented for this codebase**, with any future canvas refinements (visual polish, additional shortcuts, or full imgui removal) treated as incremental follow-up work rather than open ADR obligations.

## Design

### 1. High‑level structure

We will add a new module (for example, `lib/modelHelpCanvas.py`) that:

- Owns a `canvas.Canvas` instance.  
- Renders a **single quick help window** with:
  - A **title band** (e.g. “Model grammar quick reference”) that clearly separates the canvas from the underlying app and can host a close affordance.  
  - A **grammar skeleton** section (`model run <staticPrompt> [completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>`) plus:
    - A **last‑recipe recap** line (tokens + speakable `model …` form) when `GPTState.last_recipe` / `last_directional` are present.  
    - A static‑prompt focus line when opened via `model quick help <staticPrompt>`.  
  - **Axis summaries** (short, scannable lists for completeness/scope/method/style), grouped so that:
    - Axis lists appear in **two compact columns** rather than a single tall list (for example, completeness/scope on the left, method/style on the right).  
    - The axis corresponding to the focused quick‑help variant (for example, completeness) is visually emphasised (for example, bold heading, slight offset, or subtle colour change), so focus modes (`model quick help completeness` / `scope` / `method` / `style`) are obvious at a glance.  
  - A **directional lens XY map**, laid out as a coordinate view:
    - Vertical: `ABSTRACT (up)` → `CENTER` → `CONCRETE (down)`.  
    - Horizontal: `REFLECT (left)` → `MIXED (center)` → `ACT (right)`.  
    - Each combination lists the directional tokens assigned to that position (for example, `fly rog`, `fog`, `ong`, etc.) in the corresponding cell.
    - Cells are represented as clearly labelled rows and columns whose **visual alignment reinforces the grid** (for example, REFLECT/MIXED/ACT columns aligned across ABSTRACT/CENTER/CONCRETE rows). A later slice should experiment with **true 3×3 boxes** and labels (`UP / ABSTRACT`, `LEFT / REFLECT`, etc.) once a robust per-theme visual style is identified.  
  - A minimal **examples** pane (optional, but aligned with the most common quick recipes) that can be toggled on/off to avoid excessive height.  
- Exposes actions such as:

  ```python
  @mod.action_class
  class UserActions:
      def model_help_canvas_open():
          """Open the canvas-based model grammar quick reference"""

      def model_help_canvas_close():
          """Close the canvas-based model grammar quick reference"""
  ```

The canvas view will reuse existing state and helpers where possible:

- `HelpGUIState` for section/static prompt focus (or a sibling state object that mirrors its fields).  
- `GPTState` for last‑recipe / last‑directional context.  
- Axis and directional lists from the same `.talon-list` files used by imgui (via the helpers already in `modelHelpGUI.py`).  

### 2. Layout and rendering with canvas

We will use `canvas.Canvas` roughly as follows (specific names may vary):

- **Creation and lifecycle**
  - The canvas is created lazily when `model_help_canvas_open` is called.  
  - It is bound to `ui.main_screen()` (or a configurable screen) and sized relative to the screen (for example, centered 700×500 window).  
  - A `draw` callback renders the entire quick help view each time the canvas is invalidated.  
  - `model_help_canvas_close` hides and unregisters the canvas.  
- **Font and text**
  - Choose a **monospaced font** with good Unicode/emoji coverage (for example, Menlo, Fira Code, or a system‑appropriate default) and fallbacks.  
  - Use a small internal helper for:
    - Text measurement (for line breaks).  
    - Drawing multi‑line text blocks at `(x, y)` with padding.  
- **Layout**
  - Implement a simple layout helper layer (no full flexbox), for example:
    - Fixed margins (e.g. 16–24px).  
    - A light border or drop-shadow around the canvas region so the panel is visually distinct from the background app.  
    - Vertical stacking of major sections (title + grammar, axes, directional map, examples).  
    - Within the axes section:
      - Render as two columns (for example, completeness/scope on the left, method/style on the right), keeping each axis as a compact block with controlled wrapping so the canvas never grows excessively tall.  
    - For the directional map:
      - Reserve a region within the canvas for the directional section.  
      - Render **row/column labels and their token lists** in a consistent order so the abstract/center/concrete × reflect/mixed/act structure is obvious at a glance, even in a pure‑text layout.  
      - Add enough spacing or lightweight separators between rows (and optionally columns) that users can visually parse the grid without tracing long lines.  
      - Treat drawing literal boxes or arrows as a stretch goal, and only adopt them if they do not regress readability under different Talon themes.  
- **Interactivity**
  - Provide a clickable “Close” affordance (for example, an `X` in the top‑right or a labelled button) and a corresponding action to hide the canvas.  
  - Optionally support:
    - A scroll wheel or `PageUp/PageDown` for very small screens.  
    - A simple hover highlight for cells (purely cosmetic).  
  - Consider minimal **drag behaviour** for repositioning:
    - Implement a small `on_mouse` handler that allows the user to drag the panel by its title bar, mirroring patterns used in other Talon canvas UIs (for example, talon_hud).  

### 3. Behaviour and integration with existing commands
Once the canvas view is stable and covers the key teaching goals from ADR 006/016:

- `model quick help` will be updated to open `model_help_canvas_open()` instead of `model_help_gui` (imgui).  
- All existing **axis‑specific quick help variants** will be wired to the canvas view as focused entrypoints, for example:
  - `model quick help completeness` – open canvas quick help with the **completeness section emphasised** (for example, scrolled into view and/or visually highlighted).  
  - `model quick help scope` / `method` / `style` – analogous focus on their respective sections.  
  - A `model quick help direction` variant (if added) – open quick help focused on the directional map region.  
- The imgui quick help implementation and its actions will be removed once:
  - The canvas quick help is wired to all entrypoints, and  
  - Tests have been updated to target the canvas‑backed helpers.  

We will avoid changing the **semantics of any existing commands** (for example, `model patterns`, `model show grammar`) as part of this ADR; those commands may eventually add buttons/links that open the canvas quick help, but their primary behaviour should remain intact.

### 3.1 Adversarial UX review – canvas quick help

An adversarial review of the first canvas iteration, based on real usage, surfaced several gaps between the intended experience and the actual behaviour:

- **Dragging felt janky and was header‑only**:
  - The initial implementation relied on Talon’s `draggable=True` panel behaviour plus a minimal custom mouse handler.
  - In practice this made the window feel laggy and only reliably draggable from the header area.
  - It was also unclear which regions were draggable and which were “click‑through”.
- **Hit‑testing and focus were surprising**:
  - In some versions the panel allowed clicks to pass through to underlying windows, which is confusing for a “modal‑style” quick help surface.
  - The close affordance existed but was visually and behaviourally inconsistent.
- **Directional section was still too text‑heavy**:
  - The “ABSTRACT/CENTER/CONCRETE × reflect/mixed/act” structure was described in prose and row‑by‑row lists.
  - Even with improved wording, users struggled to see it as a **coordinate system** at a glance.
  - There was duplication between the directional map, explanatory bullets, and earlier imgui text that were never fully reconciled.
- **Semantic hints for axes and directions were under‑specified**:
  - The panel named axes and directional tokens, but gave little inline explanation of what “abstract”, “concrete”, “reflect”, “act”, or “center” meant behaviourally.
  - This forced users back to ADRs/docs instead of learning in‑panel.
- **Cursor affordances are constrained by Talon’s API**:
  - There is no supported way to change the OS cursor for a single canvas, so we cannot use a pointer cursor to indicate clickable regions.
  - Instead, we must rely on clear hints, visual cues (for example, underlines), and robust hit‑testing.

These findings drive the refinements below and will be treated as explicit, testable intent for the canvas quick help rather than incidental polish.

### 4. Testing and diagnostics

- Add targeted tests around the **canvas wiring**, not the pixel layout:
  - That `model_help_canvas_open` creates and shows a canvas instance without error under the test harness.  
  - That canvas uses the same axis/directional lists as the imgui quick help (for example, by introspecting a small “axis docs” structure exported from the renderer rather than the actual drawing calls).  
- Keep existing quick help tests for `modelHelpGUI` as regression checks until we are confident the canvas view is stable.  
- As the canvas view matures:
  - Prefer **behavioural tests** (open/close, section focus, state resets) over pixel‑ or coordinate‑perfect assertions.
  - When we change interaction contracts (for example, dragging anywhere on the panel, Escape to close, click‑to‑close hotspot), capture these in tests and/or the work‑log so regressions are obvious even if the drawing code evolves.

## Consequences

### Positive

- Directional lenses gain a **clear, visual coordinate map** that matches ADR 016’s mental model (vertical abstraction vs grounding, horizontal reflect vs act vs mixed), instead of a fragile ASCII approximation. The first iteration may be text‑only but still aligned as an XY grid.  
- The quick help surface can:
  - Use the canvas text APIs to control placement and grouping (title, sections, coordinate map) more precisely than imgui’s linear flow allows.  
  - Optionally incorporate icons or simple shapes once the basic text layout is stable, without depending on imgui’s widget set.  
- The in‑Talon teaching story for the grammar becomes:
  - More discoverable for new users.  
  - Easier to tweak visually without fighting proportional fonts.  
- Having **all quick help entrypoints** share a single canvas implementation reduces long‑term duplication and avoids drift between “legacy” (imgui) and “new” (canvas) views.  

### Negative / Risks

- Canvas introduces a **custom layout and input layer**:
  - More code to maintain than the current imgui‑only quick help.  
  - Potential for subtle bugs around window sizing, HiDPI scaling, or click targets.  
- It may be harder to **unit‑test visual details** of the canvas layout compared to simple imgui text.  
- There is a small performance risk if the canvas redraws too often or uses heavy drawing primitives (we should keep the design simple and static).  

### Mitigations

- Keep the first canvas iterations **minimal and focused**, but allow targeted UX refinements driven by adversarial review:
  - Core content: title, grammar skeleton, axis summaries, and a directional map that **reads as an XY grid**, not just text.  
  - Interaction: simple, predictable behaviours (drag anywhere on the panel, Escape to close, visible `[X]` close affordance) instead of many small controls.  
- Reuse existing **axis/directional helpers** from `modelHelpGUI` so there is a single source of truth for keys and descriptions.  
- Preserve and run existing quick help tests; add lightweight tests for the canvas wiring and axis data, not for pixel‑perfect layout.  

In addition, later slices for this ADR will:

- Prefer **single, panel‑level drag behaviour** implemented via a canvas mouse handler over mixing Talon’s built‑in `draggable` logic with custom code, to avoid jank and header‑only dragging.  
- Ensure the canvas uses `block_mouse=True` (or equivalent) so clicks are not forwarded to underlying windows while quick help is visible.  
- Reshape the directional section into a **five‑block XY layout** that matches the mental model:
  - Top: `UP / ABSTRACT` (reflect/mixed/act rows derived from the grid).  
  - Left: `LEFT / REFLECT` (abstract/center/concrete rows).  
  - Center: `CENTER / MIXED`.  
  - Right: `RIGHT / ACT`.  
  - Bottom: `DOWN / CONCRETE`.  
- Include short, inline semantic hints for axes and directional stances (for example, “abstract – generalise / zoom out”, “concrete – ground / specify”, “reflect – analyse”, “act – change / extend”, “center – mix / balance”) so users can learn meaning without leaving the panel.  
## Open Questions

- How much **visual styling** do we want to invest in for the first pass (colour accents, subtle shading, emojis), given Talon’s cross‑platform font differences?  
- Should the canvas quick help support **keyboard shortcuts** (for example, Escape to close, arrow keys to move focus between cells), or is click‑only interaction sufficient?  
- Longer term, should other GPT UIs (for example, the pattern picker or confirmation GUI) also move to canvas for richer visualisation, or should canvas remain limited to the directional/grammar teaching surface?  
 - If future Talon versions change canvas theme behaviour (for example, background colour or font handling), what minimal set of assumptions (use of `canvas.paint.color` with hex strings, text‑only grid) should this quick‑help view rely on to remain robust?  
 - How strongly should the directional map lean into a **true 3×3 visual grid** (borders, background bands) versus a lighter, text‑only grid, given the constraints of Talon themes and mixed-content apps behind the panel?  
