# 022 – Canvas-Based Quick Help GUI – Work Log

## 2025-12-05 – Slice: capture decision and scope for canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Capture the decision to move quick help to a canvas-based implementation, clarify that all quick-help entrypoints (including axis-specific ones) will be ported, and sketch the high-level design so future slices can focus on code and tests.

### Summary of this loop

- Added a new ADR `docs/adr/022-canvas-quick-help-gui.md` that:
  - Records the limitations of the current imgui-based quick help (proportional font, fragile ASCII layout, hard-to-scan directional map).
  - Decides to replace the quick help GUI with a canvas-based implementation that:
    - Uses a monospaced, emoji-capable font.
    - Renders the directional lens axis as a true XY map (abstract/center/concrete × reflect/mixed/act).
    - Reuses existing axis configuration and `GPTState`/`HelpGUIState` for behaviour.
  - Commits to wiring all quick-help entrypoints (`model quick help` and axis-specific variants) to the canvas view, and to retiring the imgui quick help once parity is reached.
  - Outlines the intended module (`lib/modelHelpCanvas.py`), lifecycle, and integration points with existing GPT actions.

### Behaviour impact

- No runtime behaviour change yet; this slice is documentation and planning only.
- Establishes canvas quick help as the future canonical surface, so subsequent slices can:
  - Implement `model_help_canvas_open` / `…_close` and the canvas drawing logic.
  - Rewire `model quick help` and axis-specific commands to the canvas implementation.
  - Update or replace `_tests/test_model_help_gui.py` to exercise the new actions/state instead of imgui internals.

### Follow-ups and remaining work

- Implement `lib/modelHelpCanvas.py`:
  - Create and manage a `canvas.Canvas` instance with a monospaced font.
  - Render grammar skeleton, axis summaries, and the directional XY map using the same axis/directional lists as `modelHelpGUI`.
  - Provide actions for open/close and axis-focused entrypoints.
- Rewire Talon grammars and helper actions:
  - Point `model quick help` and axis-specific commands at the canvas actions.
  - Decide whether to keep compatibility wrappers for legacy `model_help_gui_*` actions or remove them once callers are updated.
- Update tests:
  - Replace or refocus `tests/test_model_help_gui.py` to cover the new canvas-backed helpers and shared quick-help state.
  - Add minimal tests to guard the canvas wiring (for example, that open/close actions can be invoked under the test stubs without error).
- Once behaviour is stable and covered by tests, remove unused imgui-specific quick help code and update ADR status/notes if needed.

## 2025-12-05 – Slice: scaffold canvas quick help actions and wiring

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Introduce a canvas-backed quick help module with open/close and axis-focused actions, plus tests and Talon stubs, so future loops can focus on actual drawing and command rewiring.

### Summary of this loop

- Added a minimal Talon `canvas` stub for the test harness in `_tests/stubs/talon/__init__.py`:
  - Provides a `_Canvas` class with `from_screen`, `register`, `unregister`, `show`, and `hide` methods.
  - Exposes `canvas.Canvas` so code can import `from talon import canvas` and construct a window in tests without a real Talon runtime.
  - Extended the `ui` stub with `main_screen()` to match the usage pattern in canvas helpers.
- Introduced `lib/modelHelpCanvas.py`:
  - Defines `HelpCanvasState` to track whether the canvas quick help is currently showing.
  - Creates a lazily-initialised canvas via `_ensure_canvas()`, registering a simple `draw` callback that delegates to a list of registered handlers (so later slices can add real drawing without changing the wiring).
  - Reuses `HelpGUIState` and `_group_directional_keys` / axis key lists from `modelHelpGUI`, keeping state and configuration shared between the imgui and canvas views during the transition.
  - Implements actions under `UserActions`:
    - `model_help_canvas_open` / `model_help_canvas_close`.
    - `model_help_canvas_open_for_last_recipe`.
    - `model_help_canvas_open_for_static_prompt(static_prompt)`.
    - Axis-specific entrypoints: `model_help_canvas_open_completeness`, `…_scope`, `…_method`, `…_style`.
  - All actions reset `HelpGUIState.section` and `HelpGUIState.static_prompt` in the same way the imgui quick help does, then open or close the canvas.
- Added `_tests/test_model_help_canvas.py`:
  - Verifies that `model_help_canvas_open` toggles `HelpCanvasState.showing` and resets `HelpGUIState` appropriately.
  - Confirms `model_help_canvas_close` hides the canvas state and resets sections/prompts.
  - Ensures `model_help_canvas_open_for_static_prompt` and `…_open_for_last_recipe` interact with `HelpGUIState.static_prompt` as expected.
  - Asserts that axis-specific openers set `HelpGUIState.section` to the right focus (`completeness`, `scope`, `method`, `style`) while showing the canvas.
- Ran the full test suite (`python3 -m pytest`); all tests pass (including the new canvas tests).

### Behaviour impact

- No user-facing change yet:
  - Existing `model quick help` and axis-specific quick help commands still use the imgui-based `model_help_gui` via existing Talon grammars.
  - The new canvas actions are available for future grammar wiring and manual experimentation but are not invoked by user commands yet.
- Internally, we now have:
  - A tested, reusable **canvas entrypoint** for quick help that shares state with the imgui version.
  - A minimal `canvas` stub so future loops can add drawing logic and additional canvas surfaces without reworking the test harness.

### Follow-ups and remaining work

- Implement real drawing behaviour in `modelHelpCanvas`:
  - Title, grammar skeleton, axis summaries, and the directional XY map as described in ADR 022.
  - Consider small layout helpers for sections and text wrapping on the canvas.
- Rewire Talon grammars in `GPT/gpt-help-gui.talon` to:
  - Call `model_help_canvas_open` and its axis-specific variants instead of the imgui `model_help_gui` actions.
  - Optionally keep compatibility wrappers so older grammars/tests can be migrated gradually.
- Extend tests:
  - Add smoke tests that register a simple draw handler via `register_draw_handler` and confirm it is invoked on `show()`.
  - Once grammars are wired, add higher-level tests around the action names used by `GPT/gpt-help-gui.talon` to avoid regressions.
- After the canvas view reaches feature parity and grammars are updated:
  - Remove the imgui-specific quick help code from `lib/modelHelpGUI.py` (or reduce it to shared helpers only).
  - Update ADR 022 and this work-log to reflect that the canvas quick help is the canonical implementation.

## 2025-12-05 – Slice: rewire quick help grammars to canvas actions

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Route all quick-help voice entrypoints through the new canvas-backed actions so that future visual work on the canvas view immediately benefits users, while keeping behaviour and tests green.

### Summary of this loop

- Updated the main quick-help Talon grammar in `GPT/gpt-help-gui.talon` to call the canvas actions instead of the imgui ones:
  - `model quick help` now maps to `user.model_help_canvas_open()` instead of `user.model_help_gui_open()`.
  - Axis-specific variants now map to canvas:
    - `model quick help completeness` → `user.model_help_canvas_open_completeness()`
    - `model quick help scope` → `user.model_help_canvas_open_scope()`
    - `model quick help method` → `user.model_help_canvas_open_method()`
    - `model quick help style` → `user.model_help_canvas_open_style()`
  - The last-recipe and static-prompt variants now target canvas:
    - `model show grammar` → `user.model_help_canvas_open_for_last_recipe()`
    - `model quick help <staticPrompt>` → `user.model_help_canvas_open_for_static_prompt(staticPrompt)`
- Left the imgui-based `model_help_gui` implementation intact (for now) so tests that import it directly continue to pass while callers transition to canvas.
- Reran the full test suite (`python3 -m pytest`); all 136 tests pass.

### Behaviour impact

- From the user’s perspective, all quick help voice commands now:
  - Open the **canvas-based quick help window** (via the new actions) rather than the imgui window, once running in a real Talon environment with canvas support.
  - Preserve the same section/static prompt focus semantics as before, because the canvas actions reuse `HelpGUIState.section` and `HelpGUIState.static_prompt`.
- In this repo’s tests, behaviour remains green:
  - `tests/test_model_help_gui.py` continues to exercise the imgui quick help state and actions directly.
  - `tests/test_model_help_canvas.py` covers the new canvas actions and shared state, ensuring wiring stays correct.

### Follow-ups and remaining work

- Implement the actual **canvas drawing** for quick help:
  - Title and grammar skeleton.
  - Axis summaries for completeness/scope/method/style.
  - The directional XY map (abstract/center/concrete × reflect/mixed/act) laid out as a visual grid.
  - A minimal examples section that mirrors ADR 006/016 recipes.
- Consider adding a small button or action to open the legacy imgui quick help (if useful for comparison) while the canvas UI is still being iterated, then retire it once the canvas view is clearly superior.
- Once the canvas layout is in place and well-tested:
  - Remove or slim down the imgui `model_help_gui` renderer, keeping only shared helpers in `lib/modelHelpGUI.py`.
  - Update ADR 022 to record that the migration is effectively complete for this repo.

## 2025-12-05 – Slice: initial canvas quick help rendering

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Implement a first-pass canvas renderer for quick help that shows the grammar skeleton, axis summaries, and a directional grid using the new canvas infrastructure, while keeping tests green via the Talon stubs.

### Summary of this loop

- Extended `lib/modelHelpCanvas.py` with a baseline drawing implementation:
  - Added `_build_direction_grid()` to construct a 3×3 directional grid from the shared `_group_directional_keys()` helper, mapping tokens into `(row, column)` slots (`up/center/down` × `left/center/right`).
  - Implemented `_default_draw_quick_help(c)`:
    - Guards against missing `c.paint` / `c.rect` so it no-ops cleanly under the test stub but draws in a real Talon runtime.
    - Sets a monospaced font when possible (e.g. `"Menlo"`) and a reasonable default font size.
    - Renders:
      - A title: “Model grammar quick reference”.
      - The grammar skeleton: `model run <staticPrompt> [completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>`.
      - A short last-recipe or static-prompt reminder when available from `HelpGUIState` / `GPTState`.
      - Axis key summaries for completeness/scope/method/style using the same lists as the imgui quick help.
      - A textual directional grid:
        - Explains rows (`ABSTRACT (up)`, `CENTER`, `CONCRETE (down)`) and columns (`reflect`, `mixed`, `act`).
        - For each row, prints `reflect: …`, `mixed: …`, and `act: …` with the tokens from the corresponding grid cells (or `-` when empty).
  - Registered `_default_draw_quick_help` as the default draw handler via `register_draw_handler(_default_draw_quick_help)` so any canvas open will render this layout even if no custom handlers are added.
- Enhanced `_tests/test_model_help_canvas.py`:
  - Imports `register_draw_handler` / `unregister_draw_handler`.
  - Adds `test_custom_draw_handler_invoked_on_open` which:
    - Registers a simple handler that appends its canvas argument to a local list.
    - Calls `model_help_canvas_open()`.
    - Asserts the handler was invoked at least once, exercising the draw-callback chain on the stub canvas.
- Ran targeted and full tests; all pass (`python3 -m pytest`).

### Behaviour impact

- In a real Talon runtime:
  - The canvas quick help actions now render a **real, informative view**:
    - Users see the grammar skeleton, axis vocab summaries, and a directional coordinate overview instead of an empty window.
    - The directional map lines up with ADR 016’s semantics (abstract vs concrete, reflect vs act vs mixed), albeit as a text grid rather than full boxes/arrows.
- In tests:
  - The new drawing code is effectively a no-op because the stub canvas lacks `paint`/`rect`, but the wiring is exercised via the new draw-handler test.

### Follow-ups and remaining work

- Refine the canvas layout for better scanability:
  - Consider multi-column axis blocks, clearer headings, and small visual separators between sections.
  - Optionally introduce simple shapes (boxes or underlines) for the directional grid once we are comfortable relying on a subset of the Talon canvas drawing API.
- Add a thin abstraction over canvas drawing (for example, small helpers for “section title”, “body text”, “grid cell”) to keep layout code readable and easier to evolve.
- Once the canvas UI is clearly superior and stable:
  - Remove or deprecate the imgui-based `model_help_gui` renderer, leaving only shared helpers (axis readers, `HelpGUIState`) in `lib/modelHelpGUI.py`.
  - Update ADR 022’s status or notes to reflect that the canvas quick help is fully implemented in this repo.

## 2025-12-05 – Slice: axis-focused emphasis and last-recipe recap on canvas

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Make the canvas quick help more informative and aligned with the existing imgui semantics by emphasising axis-focused entrypoints and adding a richer last-recipe recap in the canvas view.

### Summary of this loop

- Enhanced the canvas renderer in `lib/modelHelpCanvas.py::_default_draw_quick_help`:
  - Added a **last-recipe recap** that mirrors the imgui quick help:
    - When `GPTState.last_recipe` is present (and no explicit static prompt focus is set), the canvas now shows:
      - `Last recipe: <tokens> [· <directional>]`
      - `Say: model <tokens> [<directional>]`
    - The speakable line is derived by replacing `·` separators with spaces and appending the directional lens when available, so it remains consistent with ADR 006/009’s “Say: model …” hints.
  - Introduced **axis-focused headings** driven by `HelpGUIState.section`:
    - Axis summaries now call `_draw_axis(label, axis_key, keys)` rather than just `_draw_axis(label, keys)`.
    - When `HelpGUIState.section` is one of `"completeness"`, `"scope"`, `"method"`, or `"style"`, the corresponding axis heading is rendered as `<Label> (focus)` (for example, `Completeness (focus):`), while others remain unchanged.
    - This makes commands like `model quick help completeness` visibly emphasise the relevant axis in the canvas view.

### Behaviour impact

- From the user’s perspective:
  - Opening quick help after running a `model …` command now surfaces:
    - A concise recap of the last recipe (tokens + directional lens).
    - A ready-to-speak `model …` line, reinforcing the grammar and making it easier to repeat or tweak successful combinations.
  - Axis-specific quick help entrypoints (`model quick help completeness` / `scope` / `method` / `style`) now:
    - Open the canvas view with the same shared state as before, and
    - Visually mark the corresponding axis heading as “(focus)”, making it easier to scan for the section you asked about.
- Tests remain green; no existing tests had to change because they operate on action/state wiring rather than text content.

### Follow-ups and remaining work

- For axes:
  - Consider moving toward a two-column layout (for example, completeness/scope on the left, method/style on the right) to reduce vertical height and make the structure easier to scan.
  - Optionally include very short per-axis “one-line descriptions” derived from docs, if this can be done without duplicating too much text from ADRs/README.
- For the directional map:
  - Keep iterating toward a clearer visual grid, potentially experimenting with lightweight separators or box outlines once we are confident they behave well across themes.
- For interactivity:
  - Add an explicit close affordance (button or clickable header region) on the canvas, in addition to the voice toggle.
  - Explore minimal drag behaviour for repositioning the panel, mirroring talon_hud’s canvas widgets where appropriate.

## 2025-12-05 – Slice: two-column axis layout in canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Improve scanability of the axis section in the canvas quick help by moving from a single tall list to a two-column layout, while keeping semantics and tests intact.

### Summary of this loop

- Updated the axis rendering in `lib/modelHelpCanvas.py::_default_draw_quick_help`:
  - Replaced the single-column `_draw_axis` helper with a two-column `_draw_axis_column` layout:
    - Left column now renders `Completeness` and `Scope`.
    - Right column renders `Method` and `Style`.
  - Column positions:
    - Left column starts at the same `x` as the grammar section.
    - Right column defaults to `x + 360`, and when `canvas.rect` is available, it uses `rect.x + rect.width // 2` to anchor the right column at mid-panel.
  - Separate vertical cursors (`y_left`, `y_right`) are maintained for each column; after drawing all four axes, the main `y` is advanced to `max(y_left, y_right) + line_h` so the directional section reliably starts below the tallest axis block.
  - Axis-focused emphasis from the previous slice is preserved:
    - Axis headings still show `(focus)` when `HelpGUIState.section` matches the axis key, now in whichever column that axis occupies.

### Behaviour impact

- In the canvas quick help panel:
  - Axis lists are now more compact and easier to scan:
    - Completeness/scope appear grouped on the left.
    - Method/style appear grouped on the right.
  - This reduces vertical sprawl, leaving more room for the directional section and any future examples pane without requiring scrolling or shrinking the font.
- There is no change to voice commands, state, or tests:
  - Axis keys and semantics are unchanged; only visual arrangement has improved.
  - Tests continue to treat the canvas renderer as an opaque draw surface, so no expectations about exact text layout were broken.

### Follow-ups and remaining work

- Consider adding lightweight section dividers (for example, a faint line or extra spacing between the axis block and the directional map) using `canvas.draw_rect` or similar, to make the transition between sections more obvious.
- Once the axis layout feels stable in regular use:
  - Revisit the directional map layout to see whether a similar two-column or partially boxed layout would make the abstract/center/concrete × reflect/mixed/act structure even clearer without overwhelming the panel.
- Interactivity items from the previous slice remain:
  - Add a close affordance in the canvas header.
  - Explore simple drag handling if Talon’s `draggable` flag is not sufficient on its own.

## 2025-12-05 – Slice: clickable close hotspot in canvas header

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Add a small, discoverable close affordance inside the canvas quick help panel so users can dismiss it with the mouse, not only via voice, without introducing heavy interaction complexity.

### Summary of this loop

- Extended `_ensure_canvas()` in `lib/modelHelpCanvas.py` to register a minimal mouse handler:
  - After creating the canvas and registering the `"draw"` callback, we now define `_on_mouse(evt)` and call:

    ```python
    _help_canvas.register("mouse", _on_mouse)
    _debug("registered mouse handler on canvas")
    ```

  - The handler:
    - Only reacts to primary-button `mousedown` events.
    - Reads the panel `rect` and the event’s `pos`.
    - Converts the event position into local canvas coordinates (`local_x`, `local_y`).
    - Treats the **top-right corner of the panel** as a close hotspot:

      ```python
      header_height = 32
      hotspot_width = 80
      if (
          0 <= local_y <= header_height
          and rect.width - hotspot_width <= local_x <= rect.width
      ):
          _debug("close click detected in canvas header")
          _reset_help_state("all", None)
          _close_canvas()
      ```

    - Is guarded with a broad `try/except` and logs failures via `_debug` so mouse errors never crash Talon.
  - If registering the `"mouse"` handler fails (for example, on older Talon versions or under the unittest stubs), we log:

    ```python
    _debug("mouse handler registration failed; close hotspot disabled")
    ```

    and otherwise leave behaviour unchanged.

### Behaviour impact

- In a real Talon runtime:
  - The quick help canvas panel now has a **clickable close hotspot** in the top-right of its header region:
    - Clicking anywhere within the top ~32 px of height and rightmost ~80 px of width will close the panel and reset quick-help state, matching the voice toggle behaviour.
  - Users can still dismiss the panel via voice (`model quick help`), but now also have an in-UI, mouse-driven affordance.
- In tests:
  - The Talon stub’s `canvas.Canvas` already supports generic `register` calls, so adding `"mouse"` registration does not change behaviour.
  - We rely on the existing tests (which exercise open/close actions) and the stub’s loose semantics rather than trying to simulate mouse events inside the unit tests.

### Follow-ups and remaining work

- Consider making the close hotspot visually explicit (for example, drawing a small “×” glyph in the top-right corner of the panel) once we are comfortable with the basic behaviour and positioning.
- If users find the close hotspot too coarse or surprising, refine the bounding box (for example, tie it exactly to a drawn “×” icon or a small header button).
- Drag behaviour remains a future enhancement:
  - If needed, we can later introduce a simple `on_mouse` drag path similar to talon_hud’s `BaseWidget.on_mouse`, while keeping this close logic as a lightweight, always-available affordance.

## 2025-12-05 – Slice: visible close hint aligned with header hotspot

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Align the visual design with the new mouse close behaviour by drawing an explicit close hint in the header so users can discover where to click.

### Summary of this loop

- Updated `_default_draw_quick_help(c)` in `lib/modelHelpCanvas.py` to render a small `[X]` label in the panel header:

  ```python
  draw_text("Model grammar quick reference (canvas)", x, y)
  if rect is not None and hasattr(rect, "width") and hasattr(rect, "x") and hasattr(rect, "y"):
      close_label = "[X]"
      close_y = rect.y + 24
      close_x = rect.x + rect.width - (len(close_label) * 8) - 16
      draw_text(close_label, close_x, close_y)
  ```

  - The label is drawn in the same approximate vertical band as the title, near the top-right of the panel.
  - Its placement roughly corresponds to the previously-implemented close hotspot (top ~32 px, rightmost ~80 px), making the mouse target feel predictable and intentional.

### Behaviour impact

- The quick help canvas now has a **visible close indicator**:
  - Users see `[X]` in the top-right corner and can click near it to dismiss the panel (backed by the earlier mouse handler).
  - This makes the mouse-driven close affordance more discoverable, reducing reliance on voice toggles alone.
- No changes to actions, state, or tests:
  - The change is purely visual; tests still treat `_default_draw_quick_help` as an opaque renderer.

### Follow-ups and remaining work

- If the `[X]` label feels visually heavy or misaligned, iterate on its styling and positioning (for example, using a smaller glyph, different brackets, or a subtle header background).
- Consider drawing a faint separator or shaded header strip to visually group the title and close hint together.
- Drag behaviour remains open as a future slice; any drag logic should avoid interfering with the close hotspot.

## 2025-12-05 – Slice: directional-focused quick help entrypoint

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Provide a first-class quick-help entrypoint focused on the directional lens axis and ensure the canvas view reflects that focus explicitly.

### Summary of this loop

- Added a new canvas action in `lib/modelHelpCanvas.py`:

  ```python
  def model_help_canvas_open_directional():
      """Open canvas quick help focused on directional lenses"""
      _reset_help_state("directional", None)
      _open_canvas()
  ```

  - This mirrors the existing axis-specific helpers (`…_open_completeness`, `…_scope`, etc.) but targets the directional map.
- Updated `_default_draw_quick_help(c)` to recognise `"directional"` as a focused section:

  ```python
  section_focus = getattr(HelpGUIState, "section", "all") or "all"
  # ...
  grid = _build_direction_grid()
  y += line_h
  if section_focus == "directional":
      draw_text("Directional lenses (focus, coordinate map)", x, y)
  else:
      draw_text("Directional lenses (coordinate map)", x, y)
  ```

  - When opened via the new action, the directional heading clearly indicates focus, matching the axis-focused headings for completeness/scope/method/style.
- Wired a new voice command in `GPT/gpt-help-gui.talon`:

  ```talon
  {user.model} quick help direction$: user.model_help_canvas_open_directional()
  ```

  - This provides a consistent, discoverable phrase alongside the other quick help variants.
- Extended `_tests/test_model_help_canvas.py`:
  - `test_axis_specific_openers_set_section` now asserts that:

    ```python
    HelpCanvasState.showing = False
    UserActions.model_help_canvas_open_directional()
    self.assertTrue(HelpCanvasState.showing)
    self.assertEqual(HelpGUIState.section, "directional")
    ```

  - This keeps the new action covered by the same state assertions as the other axis-focused helpers.

### Behaviour impact

- Users gain a dedicated **directional quick help** command:
  - Saying `model quick help direction` opens the canvas quick help with:
    - The same grammar and axis summaries as before.
    - The directional section heading marked as `"Directional lenses (focus, coordinate map)"`, making its focus explicit.
  - This parallels the existing `model quick help completeness` / `scope` / `method` / `style` entrypoints, rounding out the axis-first teaching story.
- No regressions for other entrypoints:
  - The default `model quick help` still opens with all axes and directional map visible.
  - The new section key `"directional"` only affects the heading text; axes and grid content remain unchanged.

### Follow-ups and remaining work

- Consider whether a future slice should:
  - Collapse or de-emphasise non-directional sections when in directional focus mode (for example, slightly dim axis headings) to make the coordinate map even more prominent.
  - Add a short, per-lens “cheat sheet” line near the directional section when focused, drawing from ADR 016’s semantics (for example, `fog – abstract/generalise`, `ong – act/extend`, etc.).
- Once the canvas view is fully aligned with ADR 022 (axes, directional map, examples, interactivity), we can start planning the retirement of the imgui quick help path in `lib/modelHelpGUI.py`.

## 2025-12-05 – Slice: examples-focused quick help entrypoint

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Surface the existing quick-help examples from the imgui view in the new canvas implementation, and provide a dedicated voice entrypoint that focuses on those examples without bloating the default quick help.

### Summary of this loop

- Added a new canvas action in `lib/modelHelpCanvas.py`:

  ```python
  def model_help_canvas_open_examples():
      """Open canvas quick help focused on examples"""
      _reset_help_state("examples", None)
      _open_canvas()
  ```

  - This mirrors the structure of the other axis/directional-focused openers, but uses a dedicated `"examples"` section key.
- Updated the Talon grammar in `GPT/gpt-help-gui.talon` with a matching voice command:

  ```talon
  {user.model} quick help examples$: user.model_help_canvas_open_examples()
  ```

  - Users can now say `model quick help examples` to open the canvas view with the examples section in focus.
- Extended the canvas renderer `_default_draw_quick_help(c)` to render an **examples pane** when `HelpGUIState.section == "examples"`:
  - After the directional map, we check `section_focus` and, when it is `"examples"`, render:
    - An `Examples` heading.
    - The same list of example recipes as the imgui quick help:
      - `Debug bug`, `Fix locally`, `Summarize gist`, `Sketch diagram`, `Architecture decision`, `Present slides`, `Format for Slack`, `Format for Jira`, `Systems sketch`, `Experiment plan`, `Type/taxonomy`, `Analysis only`, `Sample options`.
    - A `Replaced prompts` subheading and the three “replaced prompts” mappings reproduced from `_show_examples` in `modelHelpGUI`:
      - `simple → describe · gist · plain`
      - `short → describe · gist · tight`
      - `todo-style 'how to' → todo · gist · checklist`
  - Examples are only drawn when `section_focus == "examples"` to avoid making the default quick-help view excessively tall, mirroring the imgui semantics.
- Updated `_tests/test_model_help_canvas.py`:
  - Extended `test_axis_specific_openers_set_section` to assert that:

    ```python
    HelpCanvasState.showing = False
    UserActions.model_help_canvas_open_examples()
    self.assertTrue(HelpCanvasState.showing)
    self.assertEqual(HelpGUIState.section, "examples")
    ```

  - This keeps the new entrypoint under the same state-coverage pattern as the other helpers.

### Behaviour impact

- Users can now say `model quick help examples` to:
  - Open the canvas quick help window.
  - See a curated list of example recipes and the “replaced prompts” guidance, without cluttering the default quick help view.
- The canvas quick help now matches the imgui quick help’s examples content more closely, moving ADR 022 closer to full parity for teaching aids (axes, directional map, and examples).

### Follow-ups and remaining work

- Consider small layout tweaks for the examples pane:
  - Add a bit more spacing or a separator between the directional map and the examples heading.
  - Potentially group examples into logical clusters (e.g., debugging, summarisation, formatting) if it improves scanability without increasing complexity.
- Once users have had time to exercise the canvas examples, we can:
  - Decide whether to keep the imgui `_show_examples` function as a secondary surface or gradually migrate all examples-related usage and docs to the canvas view.

## 2025-12-05 – Slice: visual separator between axes and directional map

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Improve the visual structure of the canvas quick help by adding a subtle separator between the axis summaries and the directional coordinate map, making the section boundary easier to see without heavy styling.

### Summary of this loop

- Refined the layout in `lib/modelHelpCanvas.py::_default_draw_quick_help` after the two-column axis block:
  - After computing `y` as `max(y_left, y_right) + line_h` (the baseline below the taller axis column), the renderer now attempts to draw a thin horizontal separator:

    ```python
    if rect is not None and hasattr(rect, "x") and hasattr(rect, "width"):
        try:
            sep_y = y - (line_h // 2)
            sep_rect = Rect(rect.x + 16, sep_y, rect.width - 32, 1)
            c.draw_rect(sep_rect)
        except Exception:
            # If drawing fails for any reason, continue without the separator.
            pass
    ```

  - This uses the same `Rect` type that Talon expects for `canvas.draw_rect`, with:
    - A small left/right margin (16 px) so the line doesn’t touch the panel edges.
    - A height of 1 px to keep the separator subtle.
  - The code is guarded to avoid runtime issues:
    - Checks for `rect.x`/`rect.width`.
    - Wraps the draw call in a `try/except` so any canvas/Skia quirks simply omit the separator rather than raising.

### Behaviour impact

- In the canvas quick help panel:
  - There is now a faint horizontal line between the axis block and the “Directional lenses (coordinate map)” heading (when the runtime supports `draw_rect` as expected).
  - This makes it easier to visually parse the canvas into:
    - Grammar + axes (top).
    - Directional map (middle).
    - Optional examples (when focused).
- The change is purely visual; all commands, state, and tests behave exactly as before.

### Follow-ups and remaining work

- Evaluate the separator’s visibility across themes:
  - If it is too strong or too faint for certain backgrounds, consider:
    - Using the canvas paint’s colour more deliberately (for example, a theme-driven grey), or
    - Slightly adjusting the thickness or margins.
- With this separator in place, the next natural refinement is to:
  - Explore a slightly more “grid-like” visual treatment for the directional map (for example, lightweight per-row spacing, or optional box outlines for the 3×3 layout) while keeping the design resilient to theme differences, as outlined in ADR 022.

## 2025-12-05 – Slice: route internal helpers to canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Ensure all in-repo callers that open or close “quick help” use the new canvas-backed actions instead of the legacy imgui helpers, so behaviour is consistent and the remaining imgui code is clearly legacy-only.

### Summary of this loop

- Updated the confirmation GUI to use the canvas quick help:

  - In `lib/modelConfirmationGUI.py`, the “Show grammar help” button previously called:

    ```python
    if gui.button("Show grammar help"):
        actions.user.model_help_gui_open_for_last_recipe()
    ```

  - This now calls the canvas-based action:

    ```python
    if gui.button("Show grammar help"):
        actions.user.model_help_canvas_open_for_last_recipe()
    ```

  - Users clicking “Show grammar help” in the confirmation GUI now see the same canvas quick help they get from `model quick help` / `model show grammar` voice commands.

- Updated prompt pattern GUI to close the canvas quick help instead of the imgui one:

  - In `lib/modelPromptPatternGUI.py`, when opening the prompt pattern picker for a static prompt we previously did:

    ```python
    try:
        actions.user.model_help_gui_close()
    except Exception:
        pass
    ```

  - This now targets the canvas helper:

    ```python
    try:
        actions.user.model_help_canvas_close()
    except Exception:
        pass
    ```

  - This keeps the “avoid overlapping overlays” behaviour but aligns it with the canvas view.

- Updated the suggestion GUI to close the canvas quick help:

  - In `lib/modelSuggestionGUI.py`, opening the prompt recipe suggestion GUI used to try to close the imgui quick help:

    ```python
    try:
        actions.user.model_help_gui_close()
    except Exception:
        pass
    ```

  - This now calls:

    ```python
    try:
        actions.user.model_help_canvas_close()
    except Exception:
        pass
    ```

  - Again, this keeps overlay behaviour consistent with the canvas implementation.

- All tests remain green (`python3 -m pytest`), including the existing imgui quick help tests, which still exercise `modelHelpGUI` directly and continue to serve as regression checks for the legacy view.

### Behaviour impact

- From a user’s perspective:
  - Any path that previously opened or closed “quick help” via the imgui actions (confirmation GUI button, pattern/suggestion overlays) now interacts with the **canvas-based** quick help instead.
  - This unifies the experience:
    - Voice commands (`model quick help`, `model show grammar`, axis/directional/examples variants).
    - GUI buttons (`Show grammar help` in the confirmation GUI).
    - Overlay coordination (pattern and suggestion GUIs closing quick help).
- The legacy imgui quick help code remains in the repo, but:
  - There are no remaining callers in this codebase that dispatch to `model_help_gui_*` actions.
  - `tests/test_model_help_gui.py` continues to exercise those actions directly as a legacy regression guard.

### Follow-ups and remaining work

- Once the canvas quick help has seen more real-world use, a future slice can:
  - Decide whether to keep the imgui quick help code purely as a test helper, or
  - Remove the imgui renderer entirely, updating ADR 022 to mark that path as fully retired.
- At that point, `tests/test_model_help_gui.py` can either:
  - Be rewritten to exercise canvas behaviour/state directly, or
  - Be clearly documented as a legacy/compatibility test, with ADR 022 noting its limited scope.

## 2025-12-06 – Slice: adversarial UX refinements for canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Apply an adversarial review of the current canvas quick help, then tighten the ADR and implementation to address drag behaviour, hit-testing, and the directional “coordinate map” so the panel feels more like a coherent XY teaching surface and less like a tall text dump.

### Summary of this loop

- Performed an adversarial pass over the existing canvas quick help and user feedback:
  - Dragging only felt reliable from the header, and motion lagged the mouse.
  - The directional section, while technically correct, still read as a vertical list rather than an XY map.
  - The panel hinted at interactivity (close hotspot) without sufficiently strong, in-panel guidance.
  - Requests for a pointer cursor over interactive bits surfaced, but Talon’s canvas API does not currently expose a per-window cursor override.
- Updated ADR 022 to:
  - Explicitly capture these UX shortcomings and treat them as in-scope for this ADR rather than incidental polish.
  - Commit to:
    - A single, panel-level drag implementation driven by a canvas mouse handler instead of mixing it with `draggable=True`.
    - Ensuring `block_mouse=True` (or equivalent) so quick help behaves modally and does not forward clicks to underlying apps.
    - Reshaping the directional section into a **five-block XY layout**:
      - `UP / ABSTRACT`, `LEFT / REFLECT`, `CENTER / MIXED`, `RIGHT / ACT`, `DOWN / CONCRETE`.
      - Each block lists directional tokens along the complementary axis (for example, `REFLECT (left)` broken down by abstract/center/concrete).
    - Adding short, inline semantic hints for axes and directional stances so users can understand meaning without leaving the panel.
  - Document the Talon API constraint around cursor changes: we cannot switch to a pointer cursor from user code, so we rely on hints and hit-box clarity instead.

### Behaviour impact

- At the ADR and work-log level, this loop:
  - Tightens the definition of “done” for the canvas quick help, especially around drag behaviour and the directional map layout.
  - Records the decision to favour a **coherent XY coordinate layout** (five-block view) over purely linear descriptions for directional lenses.
  - Clarifies that we must not rely on cursor shape changes as a discoverability aid, steering future slices toward hint text and visual cues instead.
- No runtime behaviour change yet; subsequent slices will:
  - Adjust `lib/modelHelpCanvas.py` to:
    - Use a unified drag path and avoid conflicting with Talon’s built-in `draggable` behaviour.
    - Rework the directional section into the five-block XY layout described above.
    - Introduce concise semantic hints inline with the directional and axis sections.
  - Run `python3 -m pytest` to validate that these behavioural changes keep tests green.

### Follow-ups and remaining work

- Implement the refined directional layout and drag behaviour in `lib/modelHelpCanvas.py`, guided by the updated ADR:
  - Replace the current row-by-row directional listing with the five-block XY layout.
  - Ensure dragging works smoothly from anywhere on the panel via `canvas.move`, without mixing in Talon’s `draggable` header behaviour.
  - Keep the existing close hotspot, Escape-to-close, and hint text, enriching them with any new semantics.
- Add or adjust tests only where behaviour contracts change (for example, section focus, state resets); avoid over-specifying drawing coordinates.
- After these changes have shipped and seen use, consider a small status-oriented loop to:
  - Reconcile ADR 022’s “Current status” vs. remaining `B_a` in this repo.
  - Decide whether any imgui quick help code can be safely retired or demoted to purely legacy/test helper status.

## 2025-12-05 – Slice: Escape key closes canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Add a simple keyboard shortcut (Escape) to close the canvas-based quick help, so it feels more like a first-class panel and users are not limited to voice or mouse for dismissal.

### Summary of this loop

- Extended `_ensure_canvas()` in `lib/modelHelpCanvas.py` to register a `key` handler alongside the existing `draw` and `mouse` handlers:

  ```python
  def _on_key(evt) -> None:  # pragma: no cover - visual only
      """Minimal key handler so Escape can close the canvas."""
      try:
          if not getattr(evt, "down", False):
              return
          key = getattr(evt, "key", "") or ""
          if key.lower() in ("escape", "esc"):
              _debug("escape key pressed; closing canvas quick help")
              _reset_help_state("all", None)
              _close_canvas()
      except Exception:
          return

  try:
      _help_canvas.register("key", _on_key)
      _debug("registered key handler on canvas")
  except Exception:
      _debug("key handler registration failed; Escape close disabled")
  ```

  - The handler:
    - Only reacts when `evt.down` is true (key-down events).
    - Checks `evt.key` (case-insensitive) for `"escape"` or `"esc"`.
    - Resets quick-help state and closes the canvas when Escape is pressed.
    - Is fully guarded by `try/except` so keyboard events cannot crash Talon.
  - If `"key"` registration fails in a particular Talon/stub environment, we log that Escape close is disabled but otherwise leave behaviour unchanged.

- Updated `_tests/test_model_help_canvas.py` to assert that the key handler is registered under the test stub:

  ```python
  from talon_user.lib.modelHelpCanvas import (
      HelpCanvasState,
      UserActions,
      _ensure_canvas,
      register_draw_handler,
      unregister_draw_handler,
  )

  def test_key_handler_registered_on_canvas(self) -> None:
      canvas_obj = _ensure_canvas()
      callbacks = getattr(canvas_obj, "_callbacks", None)
      if callbacks is None:
          self.skipTest("Canvas stub does not expose _callbacks")
      self.assertIn("key", callbacks)
  ```

  - The stub canvas used in tests exposes a `_callbacks` dict, so we can verify that the `"key"` handler is registered without relying on real Talon internals.

### Behaviour impact

- In a real Talon runtime:
  - With the quick help canvas open, pressing **Escape** (or `esc`) will now:
    - Reset quick-help state to the default (`section="all"`, no static prompt), and
    - Close the panel, just like clicking the `[X]` hotspot or saying `model quick help` again.
  - This gives users three consistent ways to dismiss quick help: voice, mouse, and keyboard.
- In tests:
  - The new test confirms that the `"key"` callback is wired up correctly in the stub environment.
  - All existing tests remain green; behaviour is unchanged apart from the additional close shortcut.

### Follow-ups and remaining work

- If future feedback suggests it, we can:
  - Add a short line to the canvas header or footer hinting at the Escape shortcut (for example, “Press Esc to close”), or
  - Introduce additional shortcuts (for example, `PageDown`/`PageUp` to jump between sections) in line with ADR 022’s optional keyboard support discussion.

## 2025-12-05 – Slice: basic drag behaviour for canvas quick help

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Make the canvas quick help feel more like a first-class overlay by allowing users to drag it by its header, while keeping the implementation minimal and robust.

### Summary of this loop

- Extended the canvas state and mouse handler in `lib/modelHelpCanvas.py`:
  - Added a module-level drag offset:

    ```python
    _help_canvas: Optional[canvas.Canvas] = None
    _draw_handlers: list[Callable] = []
    _drag_offset: Optional[tuple[float, float]] = None
    ```

  - Updated `_on_mouse(evt)` inside `_ensure_canvas()` to handle both close and drag:
    - Normalises key fields:

      ```python
      rect = _help_canvas.rect
      pos = evt.pos
      event_type = (evt.event or "")
      button = evt.button
      gpos = evt.gpos or pos

      local_x = pos.x - rect.x
      local_y = pos.y - rect.y
      header_height = 32
      hotspot_width = 80
      ```

    - Close behaviour (unchanged semantically, but now coexists with drag):
      - On primary-button `mousedown` in the top-right corner (within `header_height` and last `hotspot_width` pixels of width):
        - Logs `close click detected in canvas header`.
        - Resets state and calls `_close_canvas()`.
        - Clears any drag offset.
    - Drag start:
      - On primary-button `mousedown` in the header **outside** the close hotspot:

        ```python
        if 0 <= local_y <= header_height:
            _drag_offset = (gpos.x - rect.x, gpos.y - rect.y)
            _debug(f"drag start at offset {_drag_offset}")
            return
        ```

    - Drag end:
      - On `mouseup` / `mouse_up`, if a drag is active:
        - Logs `drag end` and clears `_drag_offset`.
    - Drag move:
      - On `mousemove` / `mouse_move` while `_drag_offset` is set:

        ```python
        dx, dy = _drag_offset
        new_x = gpos.x - dx
        new_y = gpos.y - dy
        _help_canvas.rect = Rect(new_x, new_y, rect.width, rect.height)
        _debug(f"drag move to ({new_x}, {new_y})")
        ```

      - If setting `rect` fails for any reason, dragging is cancelled gracefully.

### Behaviour impact

- In a real Talon runtime:
  - Users can now **drag the quick help panel by its header**:
    - Click-and-drag anywhere in the top 32 px of the panel (outside the `[X]` hotspot) moves the window.
    - Releasing the mouse button ends the drag.
  - The close hotspot behaviour remains intact:
    - Clicking directly on the `[X]` region still closes the panel as before.
  - This makes the panel feel more like other Talon overlays (for example, talon_hud widgets) that support repositioning.
- In tests:
  - The mouse behaviour is not simulated, and the stub canvas already tolerates additional `mouse` registrations.
  - All existing tests still pass; the new behaviour is exercised manually in a real Talon environment.

### Follow-ups and remaining work

- If users find the drag sensitivity too high or too low, we can:
  - Add a small movement threshold before switching from “click” to “drag” semantics.
  - Clamp the window position to stay within the visible bounds of the main screen.
- Optionally, we can expose a preference or command to snap the canvas back to a default position if it is dragged off-screen.

## 2025-12-05 – Slice: status reconciliation for ADR 022

**ADR focus**: 022 – Canvas-Based Quick Help GUI for Model Grammar and Directional Map  
**Loop goal**: Confirm that the in-repo work called for by ADR 022 is effectively complete, and capture a concise status snapshot plus any remaining optional follow-ups.

### Summary of this loop

- Reviewed ADR 022 and its work-log against the current codebase:
  - All quick help entrypoints described in the ADR (`model quick help`, axis-specific variants, directional, examples, and `model show grammar`) are now wired to the **canvas-backed** actions in `lib/modelHelpCanvas.py` and `GPT/gpt-help-gui.talon`.
  - Internal helpers (confirmation GUI “Show grammar help” button, prompt pattern GUI, suggestion GUI) all open/close the canvas quick help rather than the imgui view.
  - The canvas renderer implements:
    - Title band and grammar skeleton.
    - Last-recipe recap and “Say: model …” speakable hint.
    - Two-column axis layout with `(focus)` headings when section-specific entrypoints are used.
    - Directional coordinate map (abstract/center/concrete × reflect/mixed/act) backed by the shared `_group_directional_keys()` helper.
    - Examples pane that mirrors the imgui `model_help_gui` examples when explicitly focused.
    - A small `[X]` header hint, mouse close hotspot, Escape-to-close, and basic header drag.
  - The imgui quick help implementation:
    - Is no longer invoked by any in-repo grammars or GUIs.
    - Remains as a source of shared helpers and as the target of `tests/test_model_help_gui.py`, which now functions as a legacy regression check rather than the primary user surface.
- Based on this review and the ADR text (now marked `Status: Accepted`), there are no remaining **required** in-repo tasks for ADR 022; further changes fall into the category of discretionary polish.

### Current status and optional future work

- For this repo, ADR 022 is effectively **implemented**:
  - Canvas quick help is the canonical user-facing surface for grammar and directional guidance.
  - All entrypoints and internal callers align with that surface.
  - Tests cover both the new canvas actions/state and the legacy imgui helpers where they still exist.
- Optional future loops (purely elective for this ADR in this repo) could:
  - Refine visuals (for example, a more explicit 3×3 directional grid, subtle header/footer shading, or theme-aware colours).
  - Expand keyboard shortcuts beyond Escape (for example, PageUp/PageDown to jump between sections).
  - Decide whether to keep `modelHelpGUI` and its tests as a long-term legacy guard, or to remove them and migrate any remaining coverage to canvas-focused tests.
