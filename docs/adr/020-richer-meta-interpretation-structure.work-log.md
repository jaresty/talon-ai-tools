## 2025-12-05 – Slice: ADR drafted and default system prompt updated

- Focus: Introduce ADR 020 to define a richer, structured meta interpretation bundle and implement the configuration changes needed in this repo, without altering parsing logic or destinations.

### Changes

- **ADR**
  - Added `docs/adr/020-richer-meta-interpretation-structure.md`:
    - Describes the motivation for a structured meta bundle:
      - Model interpretation.
      - Assumptions.
      - Gaps and checks.
      - Better prompt.
      - Axis tweak suggestion.
    - Standardises on:
      - A single meta block anchored by `## Model interpretation`.
      - Optional subsections (`### Assumptions`, `### Gaps and checks`, `### Better prompt`, `### Axis tweak suggestion`) that live entirely inside meta.
    - Emphasises that:
      - The main answer remains the only pasteable content.
      - The meta bundle is exposed via `last_meta`, the `meta` source, and recap surfaces.

- **Default system prompt**
  - `lib/talonSettings.py`
    - Updated the `model_system_prompt` default to:
      - Preserve the existing main-answer behaviour (no extra prose, avoid markdown unless requested or implied by axes, code-only for code generation).
      - Explicitly request a trailing, structured meta section starting with `## Model interpretation`, asking the model to:
        - Explain how it interpreted the request and chose its approach.
        - List key assumptions and constraints as short bullets.
        - Call out major gaps/caveats and up to three things the user should verify.
        - Propose one improved version of the original prompt in one or two sentences.
        - Optionally suggest a single axis tweak in the form `Suggestion: <axis>=<token>`.

### Behavioural impact

- For now, behaviour is unchanged; this slice is documentation-first:
  - The meta splitter and surfaces continue to behave as described in ADR 019; this ADR only changes how we ask the model to populate the meta channel.
- ADR 020 now provides a clear, repo-specific specification for how to extend the system prompt so that:
  - Meta sections are structured and consistently anchored on `## Model interpretation`.
  - Additional diagnostics (assumptions, gaps, better prompt, axis tweaks) are encouraged but optional.

### Next steps for future loops

- Update `GPT/readme.md`:
  - Extend the “Meta interpretation channel (ADR 019)” section to mention:
    - The richer structure from ADR 020.
    - How these subsections should be used (non-pasteable diagnostics).
- Optionally add a small guardrail test to assert that:
  - The default `model_system_prompt` string references `## Model interpretation` and the key subsection names, so future refactors do not silently drop the richer meta instructions.

## 2025-12-05 – Slice: tighten meta split heuristic and add prompt contract tests

- Focus: Reduce accidental mis-splits of the main answer vs. meta, and add guardrails so future changes don’t silently drop the richer meta structure from system prompts.

### Changes

- **Heuristic tightening for `split_answer_and_meta`**
  - `lib/modelHelpers.py`
    - Updated `split_answer_and_meta` to require an explicit `Model interpretation` heading:
      - Previously:
        - Split on the first Markdown heading whose text contained the word `"interpretation"`.
      - Now:
        - Only splits on a heading where:
          - The line starts with `#` (any heading level).
          - After stripping leading `#` and whitespace, the remaining text is exactly `"model interpretation"`, case-insensitive.
        - Everything before that line is the main answer; that line and all following lines are meta.
    - This avoids accidentally splitting on unrelated headings such as `## Interpretation of results`.

- **Splitter tests**
  - `_tests/test_model_helpers_meta_split.py`
    - Existing tests continue to validate:
      - Basic split on `## Model interpretation`.
      - Case-insensitive detection (`## MODEL INTERPRETATION`).
      - Leading whitespace before the heading (`   ## Model interpretation`).
    - Added:
      - `test_does_not_split_on_unrelated_interpretation_heading`:
        - Verifies that a heading like `## Interpretation of results` does **not** trigger a meta split, and the entire text remains in the answer portion.

- **System prompt contract tests**
  - `_tests/test_system_prompt_meta_contract.py`
    - New `SystemPromptMetaContractTests` suite:
      - `test_model_system_prompt_default_mentions_model_interpretation`:
        - Retrieves `settings.get("user.model_system_prompt")`.
        - Asserts that:
          - It contains the literal `## Model interpretation`.
          - It mentions `Suggestion:` and `axis`, to reflect the richer meta structure.
      - `test_gpt_system_prompt_includes_model_interpretation_heading`:
        - Builds a default `GPTSystemPrompt` and inspects `format_as_array()`.
        - Asserts that the final guidance line:
          - Mentions `## Model interpretation`.
          - Mentions `Suggestion:` and `axis`.
    - These contract tests ensure that future refactors cannot silently:
      - Drop the meta heading from system prompts.
      - Remove the axis-tweak suggestion guidance without breaking tests.

### Behavioural impact

- The meta split is now **more conservative and explicit**:
  - Only a clearly-marked `## Model interpretation` heading starts the meta block.
  - Headings that merely contain the word “interpretation” (for example, in analytical content) will not be treated as meta.
- The system prompt contract tests make it much harder to:
  - Reintroduce inline metadata instructions.
  - Drift away from ADR 020’s richer structure without test failures.

## 2025-12-05 – Slice: consolidate meta guidance into a shared constant

- Focus: Reduce duplication and drift risk by centralising the structured meta-interpretation guidance in a single constant used by both the global system prompt and the axis-driven prompt.

### Changes

- **Shared meta guidance**
  - `lib/metaPromptConfig.py`
    - Added `META_INTERPRETATION_GUIDANCE`, a single string that encodes the richer meta contract:
      - Start a structured, non-pasteable meta section with `## Model interpretation`.
      - In that section only:
        - Explain how the request was interpreted and why the approach was chosen.
        - List key assumptions/constraints as short bullets.
        - Call out major gaps/caveats and up to three items to verify.
        - Propose one improved version of the original prompt (1–2 sentences).
        - Optionally suggest a single axis tweak in `Suggestion: <axis>=<token>` form, using existing axis tokens.

- **Global system prompt wiring**
  - `lib/talonSettings.py`
    - Updated the `model_system_prompt` default to:
      - Keep the main-answer guidance inline:
        - Output just the main answer.
        - Avoid markdown backticks unless requested or implied by style/method axes.
        - For code generation, output code only in the main answer.
      - Append `META_INTERPRETATION_GUIDANCE` to supply the meta instructions.

- **Axis-driven prompt wiring**
  - `lib/modelTypes.py`
    - Updated `GPTSystemPrompt.format_as_array()` to use `META_INTERPRETATION_GUIDANCE` as part of its final guidance line:
      - Retains the “answer fully and accurately” phrasing for the main answer.
      - Appends the same structured meta instructions as the global system prompt.

- **Docs alignment**
  - `GPT/readme.md`
    - Updated the `user.model_system_prompt` default row to match the new combined main-answer + `META_INTERPRETATION_GUIDANCE` string, including:
      - The example axis styles (`'code', 'table', 'presenterm'`).
      - The full description of the structured meta section and axis tweak suggestion.

### Behavioural impact

- The behaviour requested from the model is unchanged from the previous slice, but:
  - There is now a single source of truth for meta guidance.
  - Future edits to the meta contract only need to change `META_INTERPRETATION_GUIDANCE`.
- Contract tests in `_tests/test_system_prompt_meta_contract.py` still pass and now implicitly validate the shared constant via both:
  - `user.model_system_prompt`.
  - `GPTSystemPrompt.format_as_array()`.

## 2025-12-05 – Slice: richer meta previews in confirmation GUI and quick help

- Focus: Make the “information radar” surfaces more useful by showing multiple, non-heading meta lines instead of a single, often uninformative heading.

### Changes

- **Shared preview helper**
  - `lib/metaPromptConfig.py`
    - Added `meta_preview_lines(meta_text: str, max_lines: int = 3) -> list[str]`:
      - Splits `meta_text` into lines, strips blanks.
      - Skips markdown-style headings (lines starting with `#`).
      - Returns up to `max_lines` non-heading lines, or the first non-empty lines when no better candidate exists.
    - Refactored `first_meta_preview_line` to delegate to `meta_preview_lines(..., max_lines=1)`, so both helpers share logic.

- **Confirmation GUI radar**
  - `lib/modelConfirmationGUI.py`
    - Previously:
      - Used `first_meta_preview_line` and showed a single `Meta: …` line (often `## Model interpretation`).
    - Now:
      - Calls `meta_preview_lines(GPTState.last_meta, max_lines=3)`.
      - If any preview lines exist:
        - Shows the first as `Meta: <line>` (truncated to 80 characters).
        - Shows subsequent lines beneath it, indented, also truncated per line.
      - This yields a richer multi-line meta recap while still staying compact.

- **Quick help radar**
  - `lib/modelHelpGUI.py`
    - Previously:
      - Used `first_meta_preview_line` and rendered a single wrapped line under “Model interpretation”.
    - Now:
      - Uses `meta_preview_lines(GPTState.last_meta, max_lines=2)`.
      - Renders each line with `_wrap_and_render`, allowing up to two informative lines from the meta section to appear under the “Model interpretation” header.

- **Tests**
  - `_tests/test_model_confirmation_gui.py`
    - Existing tests still ensure a `Recipe:` line and at least one `Meta:` line appear when meta is present.
    - `test_meta_preview_skips_markdown_heading` remains valid and now also covers the case where:
      - `last_meta` starts with `## Model interpretation`.
      - The `Meta:` preview shows the first non-heading line (for example, “Interpreted as: …”), not the raw heading.

### Behavioural impact

- Confirmation GUI:
  - The meta radar can now show up to three concise lines (for example, interpretation + key assumption + a gap/check), instead of a single heading or sentence.
  - Markdown headings are skipped, so users see substantive content rather than `## Model interpretation`.
- Quick help:
  - Shows up to two wrapped lines of meta under “Model interpretation”, giving a slightly deeper sense of how the last request was interpreted without overwhelming the grammar overview.
