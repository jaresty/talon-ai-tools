## 2025-12-05 – Slice: core meta channel plumbing and source

- Focus: ADR 019 – implement the core meta-interpretation channel (state, splitter, and model source) without yet touching UI surfaces.

### Changes

- **State (`lib/modelState.py`)**
  - Added `GPTState.last_meta: str` to store the most recent meta-interpretation.
  - Ensured `last_meta` is reset in both `GPTState.clear_all()` and `GPTState.reset_all()`.

- **Splitting and capture (`lib/modelHelpers.py`)**
  - Introduced `split_answer_and_meta(text: str) -> tuple[str, str]`:
    - By default treats the entire response as `answer` and empty `meta`.
    - When it finds a trailing Markdown heading whose text contains “interpretation” (for example, `## Model interpretation`), it splits:
      - `answer` = content before the heading.
      - `meta` = the heading and everything after it.
  - Updated `send_request` so that:
    - It applies `split_answer_and_meta` to the stripped model response.
    - Stores `answer` in `GPTState.last_response` and `meta` in `GPTState.last_meta`.
    - Pushes only the `answer` text into the assistant thread.

- **Presentation (`lib/modelPresentation.py`)**
  - Extended `ResponsePresentation` with a `meta_text: str = ""` field to carry meta alongside the main content.
  - Updated `render_for_destination` to:
    - Use `split_answer_and_meta` on the extracted message text.
    - Populate `display_text`, `paste_text`, and `browser_lines` from the `answer` portion only.
    - Store the `meta` portion in `meta_text`.
    - Preserve existing browser auto-open behaviour based on answer length.

- **Meta model source (`lib/modelSource.py`, `GPT/lists/modelSource.talon-list`)**
  - Added a `Meta` `ModelSource` that returns `GPTState.last_meta`, and raises with a notification when no meta is available.
  - Registered the new source key `"meta"` in `create_model_source`, including the `modelSimpleSource` tag.
  - Exposed the source in the Talon list as:
    - `meta: meta`
    - allowing commands such as `model meta to browser` or `model meta to context`.

- **Tests**
  - `tests/test_model_state.py`
    - Extended reset tests to assert that `GPTState.last_meta` is cleared by both `clear_all` and `reset_all`.
  - `tests/test_talon_settings_model_prompt.py`
    - Updated `test_clear_all_resets_last_recipe_and_response` to also assert that `GPTState.last_meta` is reset to `""`.
  - `tests/test_prompt_pipeline.py`
    - Extended `test_prompt_result_builds_presentations` to cover the new `meta_text` field (which is empty for single-part responses).
  - Added a new test module `tests/test_model_source_meta.py` to verify:
    - The `Meta` source returns `GPTState.last_meta` when present.
    - The `Meta` source raises and notifies when no meta is available.

### Behavioural impact

- **Pasting and destinations**
  - `send_request` and `render_for_destination` now treat the response as two channels:
    - **Answer**: what gets stored in `last_response`, fed into `ResponsePresentation.paste_text`, and pushed into the assistant thread.
    - **Meta**: stored in `last_meta` and exposed via the new `Meta` model source.
  - For now, `display_text` and browser content are still derived from the answer only; UI surfaces will start consuming `meta_text` in a later slice.

- **New capabilities**
  - Users can route the model’s last interpretation to any destination on demand:
    - `model meta to browser`
    - `model meta to context`
    - `model meta to query`
  - If no meta was captured for the last run, attempts to use the `meta` source will notify and fail cleanly, mirroring the behaviour of `gptResponse`.

### Follow-ups for future loops

- Update recap and UI surfaces per ADR 019:
  - Confirmation GUI: show a compact “Meta:” line beneath the `Recipe:` line when `last_meta` is present.
  - Quick help GUI: add a “Model interpretation” preview alongside the last recipe.
  - Browser destination: add a “Model interpretation” section based on `ResponsePresentation.meta_text` / `GPTState.last_meta`.
- Consider documenting a recommended meta delimiter (for example, `## Model interpretation`) in the README or a dedicated docs section so users can opt into structured meta more easily.
- Add targeted tests around `split_answer_and_meta` once a canonical delimiter format is finalised.

## 2025-12-05 – Slice: meta on recap surfaces, splitter tests, and docs

- Focus: Wire meta into the main recap UIs (confirmation GUI, quick help, browser), document the recommended delimiter, and add tests for the splitter heuristic.

### Changes

- **UI surfaces**
  - `lib/modelConfirmationGUI.py`
    - After the existing `Recipe:` line, added a compact meta radar when `GPTState.last_meta` is non-empty:
      - Uses the first line of `last_meta`, truncated to 80 characters.
      - Renders as `Meta: <preview>`, keeping meta visible but separate from paste text.
  - `lib/modelHelpGUI.py`
    - In the “Last recipe” branch (when `HelpGUIState.static_prompt` is `None` and `GPTState.last_recipe` is set), added:
      - A `Model interpretation` label.
      - A wrapped preview of the first line of `GPTState.last_meta`, using `_wrap_and_render`, when meta is available.
  - `lib/modelDestination.py` (`Browser` destination)
    - Kept the existing recipe recap (`Recipe:`, `Say:`, and grammar/pattern tips).
    - Added a dedicated “Model interpretation” section:
      - Uses `presentation.meta_text` when available, falling back to `GPTState.last_meta`.
      - Renders each meta line as its own paragraph.
    - Followed by a “Response” section that shows the main answer body (`presentation.browser_lines`) as before.

- **Splitter tests**
  - Added `_tests/test_model_helpers_meta_split.py` covering `split_answer_and_meta`:
    - `test_returns_all_answer_when_no_interpretation_heading` – asserts that text without a matching heading yields `answer == text`, `meta == ""`.
    - `test_splits_on_markdown_interpretation_heading` – verifies that a trailing `## Model interpretation` section is split into meta, with the main body as answer.
    - `test_interpretation_heading_detection_is_case_insensitive` – confirms headings like `## MODEL INTERPRETATION` are recognised.
    - `test_leading_whitespace_before_heading_is_ignored` – ensures indented headings (for example, `   ## Model interpretation`) are still detected.

- **Docs**
  - Updated `GPT/readme.md` with a new subsection “Meta interpretation channel (ADR 019)”:
    - Recommends a concrete structure for meta sections:
      - End the main answer, then add a `## Model interpretation` heading followed by one or more lines explaining how the request was interpreted.
    - Explains that:
      - Everything before the heading is treated as the main answer (pasted and rendered as the primary body).
      - The heading and following lines are treated as meta:
        - Stored in `last_meta`.
        - Accessible via the `meta` model source.
        - Surfaced near last-recipe recaps in the confirmation GUI, quick help, and browser views.

### Behavioural impact

- When responses follow the `## Model interpretation` pattern:
  - **Pasting remains clean** – only the answer portion is pasted.
  - **Recap surfaces become richer**:
    - Confirmation GUI shows both `Recipe:` and a short `Meta:` preview.
    - Quick help shows last recipe + exact `model …` line + a “Model interpretation” preview.
    - Browser view shows a “Model interpretation” section above the “Response” body.
- The new tests lock in the delimiter-based splitting heuristic, making future changes to `split_answer_and_meta` safer.

### Remaining follow-ups

- Optionally add a small in-Talon helper action (for example, `model show meta`) to pop the last interpretation into a notification or dedicated GUI.
- Consider toggles or truncation strategies if meta sections become very long in practice (for example, “Show more” affordances in the browser or quick help views).

## 2025-12-05 – Slice: `model last meta` helper

- Focus: Add a small, voice-first helper to surface the last meta-interpretation directly, complementing `model last recipe`.

### Changes

- **New action and grammar**
  - `GPT/gpt.py`
    - Added `gpt_show_last_meta()`:
      - Reads `GPTState.last_meta`.
      - If empty/whitespace, calls `notify("GPT: No last meta interpretation available")`.
      - Otherwise sends a desktop notification via `actions.app.notify` with:
        - A `Last meta interpretation:` header.
        - The full meta text on subsequent lines.
  - `GPT/gpt.talon`
    - Added a new command:
      - `{user.model} last meta$: user.gpt_show_last_meta()`
    - This mirrors `model last recipe` and completes a simple recap pair:
      - `model last recipe` → recipe tokens.
      - `model last meta` → interpretation of the last prompt.

- **Tests**
  - `_tests/stubs/talon/__init__.py`
    - Extended the `app` stub:
      - `_AppNamespace` now records calls:
        - `self.calls: list[tuple[str, tuple, dict]]`.
        - `notify(self, message: str, *args, **kwargs)` appends `("notify", (message, *args), kwargs)` before returning.
      - This enables tests to assert on notifications issued via `actions.app.notify`.
  - `_tests/test_gpt_actions.py`
    - In `GPTActionPromptSessionTests`:
      - `tearDown` now clears `actions.app.calls` so tests remain independent.
      - Added:
        - `test_gpt_show_last_meta_notifies_when_present`:
          - Seeds `GPTState.last_meta` with a short interpretation string.
          - Calls `gpt_module.UserActions.gpt_show_last_meta()`.
          - Asserts that at least one `actions.app.calls` entry contains `"Last meta interpretation:"` in the message.
        - `test_gpt_show_last_meta_notifies_when_missing`:
          - Sets `GPTState.last_meta` to `""`.
          - Calls `gpt_module.UserActions.gpt_show_last_meta()`.
          - Asserts that at least one `actions.app.calls` entry contains `"No last meta interpretation available"`.

### Behavioural impact

- Users now have a direct, low-friction way to recall how the model interpreted the last request, even when:
  - The confirmation GUI is closed.
  - They don’t want to open the browser or quick-help surfaces.
- The helper aligns with existing recap patterns:
  - `model last recipe` shows what was asked (in grammar tokens).
  - `model last meta` shows how the model says it understood that request.
- Tests ensure:
  - A clear notification path both when meta exists and when it does not.
  - The `app` stub can be reused by future tests that need to assert on notifications.

## 2025-12-05 – Slice: Confirmation GUI meta recap guardrail

- Focus: Add a targeted test for the confirmation GUI’s meta recap and expose the underlying imgui function in the test harness so ADR 019’s modal radar remains stable.

### Changes

- **Imgui stub enhancement**
  - `_tests/stubs/talon/__init__.py`
    - Updated the `imgui.open` decorator to attach the wrapped function:
      - In `open()`, the decorator now:
        - Creates `wrapper = _ImguiFunction(func)`.
        - Sets `wrapper.__wrapped__ = func`.
        - Returns `wrapper`.
      - This mirrors common Python decorator practice and allows tests to call `confirmation_gui.__wrapped__` with a custom GUI stub, bypassing the `_DummyGUI` used by the wrapper.

- **New confirmation GUI test**
  - `_tests/test_model_confirmation_gui.py`
    - Added `ConfirmationGUIMetaTests`:
      - `setUp` calls `GPTState.reset_all()` to ensure a clean starting state.
      - `test_includes_meta_preview_when_last_meta_present`:
        - Seeds:
          - `GPTState.text_to_confirm = "Body"`.
          - `GPTState.last_recipe = "describe · full · focus · plain"`.
          - `GPTState.last_directional = "fog"`.
          - `GPTState.last_meta = "Interpreted as: summarise the design tradeoffs."`.
        - Defines a `_StubGUI` with `text`, `line`, `spacer`, and `button` methods that records every `text` call.
        - Invokes the underlying GUI function via `confirmation_gui.__wrapped__(_StubGUI())`.
        - Asserts that:
          - At least one rendered line starts with `"Recipe: "`.
          - At least one rendered line starts with `"Meta: "`.
      - This directly validates that, when meta is available, the confirmation GUI surfaces both:
        - The last recipe recap.
        - A compact `Meta:` preview, as required by ADR 019.

### Behavioural impact

- The confirmation modal’s meta radar now has an explicit, automated guardrail:
  - If a future change accidentally removes or renames the `Meta:` preview, the new test will fail.
  - The imgui stub remains backwards-compatible for other tests but is now more introspection-friendly via the `__wrapped__` attribute.
