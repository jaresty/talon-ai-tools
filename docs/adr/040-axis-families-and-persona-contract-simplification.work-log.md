# 040 – Axis Families and Persona/Contract Simplification – Work Log

> **2025-12-24 update (ADR 0061)**: intent tokens are now single-word canonical forms (`inform`, `decide`, `teach`, etc.). Historical notes below may reference legacy “for …” phrases.

## 2025-12-10 – Slice: Introduce Persona/Intent/Contract framing into GPT README

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Docs and help updates (GPT/readme.md) and ADR work-log wiring.

### Changes

- Updated `docs/adr/040-axis-families-and-persona-contract-simplification.md` to refer to the correct work-log filename and to point at the existing `_tests/test_voice_audience_tone_purpose_lists.py` rather than non-existent `tests/` paths.
- Added a `Persona / Intent / Contract (Who / Why / How)` section to `GPT/readme.md` ahead of the modifier axes, briefly explaining:
  - Persona (Who) = voice + audience + tone.
  - Intent (Why) = intent.
  - Contract (How) = completeness + scope + method + style.
- Clarified that:
  - Persona/intent presets are optional “stance” controls for tailoring explanations.
  - The main power surface for behaviour/shape remains the contract axes.

### Rationale

- Aligns the README with ADR 040’s family model so users first learn **Who / Why / How**, not eight raw axis names.
- Avoids broken test references in ADR 040 and establishes a concrete work-log for future slices under this ADR.

### Follow-ups

- Extend Help Hub / quick-help GUIs to group axis docs and examples under Persona / Intent / Contract headings.
- Add small persona and intent preset tables to Help Hub and/or pattern GUIs.
- Consider adding voice-accessible help entry points (for example, `model help who`, `model help why`, `model help how`) once the GUI changes are in place.

---

## 2025-12-10 – Slice: Persona lists → key-only + Python hydration

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Persona/intent list structure, hydration, and docs.

### Changes

- Updated persona Talon lists to be key-only carriers:
  - `GPT/lists/modelVoice.talon-list` now uses `as programmer: as programmer`, etc.
  - `GPT/lists/modelAudience.talon-list` now uses `to managers: to managers`, etc.
  - `GPT/lists/modelTone.talon-list` now uses `casually: casually`, etc.
  - `GPT/lists/modelIntent.talon-list` now uses `for information: for information`, etc.
- Introduced `lib/personaConfig.py` as the Python SSOT for persona/intent semantics:
  - `voice` – keys like `as programmer`, `as teacher`, `as Kent Beck` mapped to rich “Act as …” descriptions.
  - `audience` – keys like `to managers`, `to junior engineer`, `to CEO`, `to XP enthusiast` mapped to audience descriptions.
  - `tone` – keys like `casually`, `formally`, `directly`, `gently`, `kindly` mapped to tone guidance.
  - `intent` – keys like `for information`, `for deciding`, `for brainstorming`, `for teaching`, etc., mapped to intent descriptions.
- Updated `lib/modelTypes.GPTSystemPrompt.format_as_array` to hydrate persona and intent via `persona_hydrate_tokens` before sending the system prompt to the model:
  - `Voice: …`, `Tone: …`, `Audience: …`, and `Intent: …` lines now expand short keys into full descriptions while contract axes (`completeness`, `scope`, `method`, `style`, `directional`) continue to hydrate via `axis_hydrate_tokens`.
- Kept Help docs rich after the list change by updating `GPT/gpt.py`’s `gpt_help` builder:
  - When rendering the Voice/Tone/Audience/Intent tables, pass `description_overrides` built from `persona_docs_map('voice'/'tone'/'audience'/'intent')` so the HTML docs show the full Python-side descriptions instead of the key-only list values.
- Added `_tests/test_gpt_system_prompt_axes_hydration.py` to assert that contract axes in the system prompt still hydrate via `axis_hydrate_tokens` (guarding against regressions while persona hydration moved to `personaConfig`).
- Re-ran focused tests:
  - `_tests/test_voice_audience_tone_purpose_lists.py`
  - `_tests/test_help_hub.py`
  - `_tests/test_axis_docs.py`
  - `_tests/test_gpt_system_prompt_axes_hydration.py`

### Rationale

- Aligns persona and intent with the axis pattern (keys in Talon, rich descriptions in Python), reducing duplication and making it easier to:
  - Hydrate persona/intent cleanly into the system prompt.
  - Drive GUIs and help surfaces from a single Python SSOT.
- Ensures that changing the Talon lists to key-only values does **not** weaken the behavioural contract sent to ChatGPT: hydrated descriptions are still provided when executing prompts.
- Adds an explicit regression test so contract axis hydration cannot be accidentally broken while iterating on persona/intent.

### Follow-ups

- Use the persona/intent docs in `personaConfig` to:
  - Drive Help Hub search and categorisation under Persona / Intent.
  - Feed persona/intent preset tables in pattern GUIs and the suggestions modal.
- Consider small tests around persona hydration (for example, asserting that `GPTSystemPrompt(voice="as programmer").format_as_array()` includes `Act as a programmer.` in the system prompt lines).

---

## 2025-12-10 – Slice: Help Hub cheat sheet and ADR links reflect Persona / Intent / Contract

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Help Hub surface framing and ADR discoverability.

### Changes

- Updated `lib/helpHub._cheat_sheet_text` to include the Who / Why / How family model from ADR 040:
  - Added a “Who / Why / How (ADR 040)” section showing:
    - Persona (Who): voice, audience, tone.
    - Intent (Why): intent.
    - Contract (How): completeness, scope, method, style.
- Extended `lib/helpHub._adr_links_text` so Help Hub’s “ADR links” button now also includes:
  - `docs/adr/040-axis-families-and-persona-contract-simplification.md`.
- Re-ran `_tests/test_help_hub.py` to confirm Help Hub behaviour remains green.

### Rationale

- Ensures the Help Hub cheat sheet surfaces the Persona / Intent / Contract framing, so voice users can see the three families without diving into the full README.
- Makes ADR 040 directly discoverable from the “ADR links” button, aligning help surfaces with the new axis family model.

### Follow-ups

- Consider adding a short “Who / Why / How” framing to other help surfaces (for example, quick help canvas) so the family model is consistent across all entry points.

---

## 2025-12-10 – Slice: Contributor docs include Persona / Intent / Contract and question-gate rules

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Contributor guidance for prompts/axes.

### Changes

- Updated `CONTRIBUTING.md` “GPT prompts, axes, and ADRs” section to:
  - Add `docs/adr/040-axis-families-and-persona-contract-simplification.md` to the list of ADRs contributors should read before changing static prompts or axis lists.
  - Introduce a design rule that explicitly frames axes in terms of the three families from ADR 040:
    - Persona (Who): voice, audience, tone.
    - Intent (Why): intent.
    - Contract (How): completeness, scope, method, style.
  - Add a question-gate guideline: when adding a new behaviour, decide which single question it primarily answers (Who, Why, or How). If it honestly spans more than one family, encode it as a recipe/pattern that sets multiple axes, rather than introducing a new raw axis token.

### Rationale

- Brings the contributor docs into alignment with ADR 040 so new tokens and behaviours are evaluated using the Persona / Intent / Contract framing instead of only the older per-axis ADRs.
- Makes the question-gate rule (“exactly one primary question per raw token; otherwise use a recipe/pattern”) an explicit part of the contributor workflow, reducing the chance of future axis overlap.

### Follow-ups

- Optionally expand CONTRIBUTING with a couple of short examples (for example, “Teach junior dev” vs “Executive brief”) showing how to decompose them into Persona + Intent + Contract for contributors unfamiliar with the ADR.

---

## 2025-12-10 – Slice: README includes Who / Why / How adversarial examples

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Docs – concrete examples of the family model.

### Changes

- Extended the `Persona / Intent / Contract (Who / Why / How)` section in `GPT/readme.md` with a new subsection “Who / Why / How – examples” that decomposes common prompts into the three families:
  - “Explain simply to a junior engineer” → Persona (`as teacher` + `to junior engineer` + `tone=kindly`), Intent (`for teaching`), Contract (`completeness=gist/minimal`, `scope=focus`, `method=scaffold`, `style=plain`/`tight`), with a note not to encode it as a single new audience or intent token.
  - “Executive brief for CEO” vs “Deep technical write-up for engineers” → contrasting Persona (different audiences and tones), Intent (for deciding vs for information/evaluating), and Contract (gist/focus/headline/tight vs full/system/structure/analysis/plain/adr), again emphasising that coverage/territory/reasoning/containers live on the contract axes.

### Rationale

- Gives contributors and users concrete, adversarial examples of how to apply the Persona / Intent / Contract model from ADR 040 in practice, directly in the main GPT README.
- Reinforces the question-gate rule by showing where **not** to encode behaviours (for example, not as new intent/audience tokens) and instead use recipes across existing axes.

### Follow-ups

- Optionally mirror a shortened version of these examples into quick help or Help Hub docs so the same patterns are visible in in‑Talon surfaces.

---

## 2025-12-10 – Slice: Persona and intent presets SSOT

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Persona/intent presets SSOT and tests.

### Changes

- Extended `lib/personaConfig.py` with dataclass-based presets and (later in ADR-0062) wrapped them with `get_persona_intent_orchestrator()` so downstream surfaces consume a single façade:
  - `PERSONA_PRESETS`: small set of named persona recipes (for example, `peer_engineer_explanation`, `teach_junior_dev`, `executive_brief`) that map to existing `voice`/`audience`/`tone` tokens.
  - `INTENT_PRESETS`: named intent presets (for example, `teach`, `decide`, `plan`, `evaluate`, `brainstorm`, `appreciate`) that map to existing `intent` tokens.
- Added `_tests/test_persona_presets.py` to ensure:
  - All persona and intent presets reference valid axis tokens from `PERSONA_KEY_TO_VALUE`.
  - Expected core presets are present.
  - Persona and intent preset keys are unique.
- Ran `python3 -m pytest _tests/test_persona_presets.py _tests/test_voice_audience_tone_purpose_lists.py` to confirm tests pass.

### Rationale

- Establishes a concrete SSOT for Persona (Who) and Intent (Why) presets, so future GUIs and suggestion surfaces can consume a shared, typed structure instead of hard-coding combinations.
- Keeps presets aligned with existing axis tokens and ADR 015/040 semantics by test-guarding their mappings.

### Follow-ups

- Surface `PERSONA_PRESETS` and `INTENT_PRESETS` (via `get_persona_intent_orchestrator()` so aliases stay canonical) in one or more UX surfaces (for example, pattern picker, suggestions modal, quick help) as persona/intent pickers.
- Consider small docs/help snippets that reference these preset names so users see concrete Who/Why recipes, not just raw axes.

---

## 2025-12-10 – Slice: Quick-help canvas shows Persona / Intent / Contract

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Canvas quick-help framing for Who / Why / How.

### Changes

- Updated `lib/modelHelpCanvas.py` to consume presets via `get_persona_intent_orchestrator()` (falling back to `lib.personaConfig` when needed).
- Extended the default canvas renderer (`_default_draw_quick_help`) to show a concise axis-family summary immediately after the grammar/caps lines:
  - "Who / Why / How (ADR 040):" header.
  - "Who – Persona: voice, audience, tone."
  - "Why – Intent: intent."
  - "How – Contract: completeness, scope, method, style."
- Added lightweight persona/intent preset hints to the same section so users see concrete Who/Why recipes in quick help:
  - "Persona presets: …" using the first few orchestrator-backed persona preset labels.
  - "Intent presets: …" using the first few orchestrator-backed intent preset labels.
  - Both blocks are guarded so quick help still renders if presets cannot be imported.
- Ran `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_help_hub.py` to confirm help-related tests remain green.

### Rationale

- Brings the canvas-based quick help in line with ADR 040’s family model so users see **Persona / Intent / Contract (Who / Why / How)** in the primary grammar reference, not only in README/Help Hub.
- Reuses the shared persona/intent preset SSOT to surface a small, concrete set of default Who/Why recipes without hard-coding combinations in the canvas module.

### Follow-ups

- Consider adding dedicated voice entrypoints (`model help who`, `model help why`, `model help how`) that focus the canvas on the new section once their semantics are designed.
- Iterate on the quick-help layout to show a slightly richer preset table (for example, preset name plus decomposed axes) if this remains readable within the canvas height constraints.

---

## 2025-12-10 – Slice: Voice entrypoints for Who / Why / How help

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Voice-accessible help entrypoints for Persona / Intent / Contract.

### Changes

- Updated `GPT/gpt-help-gui.talon` to add three new commands that open canvas quick help using the Who/Why/How framing from ADR 040:
  - `{user.model} help who` → `user.model_help_canvas_open_who()`.
  - `{user.model} help why` → `user.model_help_canvas_open_why()`.
  - `{user.model} help how` → `user.model_help_canvas_open_how()`.
- Extended `lib/modelHelpCanvas.UserActions` with matching actions that set dedicated sections before opening the canvas:
  - `model_help_canvas_open_who` sets `HelpGUIState.section = "who"`.
  - `model_help_canvas_open_why` sets `HelpGUIState.section = "why"`.
  - `model_help_canvas_open_how` sets `HelpGUIState.section = "how"`.
- Updated `_tests/test_model_help_canvas.py` to assert that calling these actions:
  - Opens the canvas, and
  - Leaves `HelpGUIState.section` set to `"who"`, `"why"`, or `"how"` respectively.
- Ran `python3 -m pytest _tests/test_model_help_canvas.py` to confirm the canvas help suite remains green.

### Rationale

- Provides explicit, memorable voice entrypoints for the three axis families (Persona / Intent / Contract) outlined in ADR 040, aligning the help ergonomics with the conceptual model.
- Prepares the canvas for future slices that may render family-specific focus states based on `HelpGUIState.section` while already exposing stable voice commands to users.

### Follow-ups

- Consider teaching `model help who/why/how` in README or Help Hub so users discover the new commands.
- In a later slice, adjust the canvas renderer to highlight the Persona / Intent / Contract section more strongly when `HelpGUIState.section` is `"who"`, `"why"`, or `"how"`.
---

## 2025-12-10 – Slice: Axis-family token guardrails

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Guardrail tests for axis-family wording.

### Changes

- Added `_tests/test_axis_family_token_guardrails.py` to enforce simple word-level guardrails between persona/intent docs and contract axis docs:
  - `test_persona_docs_do_not_contain_contract_shaped_words` asserts that persona/intent descriptions in `personaConfig.PERSONA_KEY_TO_VALUE` do not contain obviously container/format words such as `table`, `diagram`, `jira`, `slack`, `checklist`, `gherkin`, `code`, `shellscript`, `html`, or `cards` (which belong on style/method instead).
  - `test_contract_docs_do_not_contain_persona_shaped_words` asserts that contract axis docs from `axisMappings.axis_docs_map` (for `completeness`, `scope`, `method`, `style`) do not contain clearly persona/role words like `executive`, `ceo`, `junior`, `novice`, or `manager`.
- Ran `python3 -m pytest _tests/test_axis_family_token_guardrails.py _tests/test_voice_audience_tone_purpose_lists.py` to confirm the new guardrails and existing persona-axis tests pass together.

### Rationale

- Provides a lightweight, test-backed check that aligns with ADR 040’s guidance: persona/intent should not quietly accumulate container/format semantics, and contract axes should not slip back toward audience/role semantics.
- The guardrails are deliberately conservative (word-based, small banned sets) so they flag only clear violations while staying compatible with current axis docs.

### Follow-ups

- If future ADRs adjust axis wording, refine or extend the banned-word sets to cover any newly problematic patterns (for example, additional persona-ish roles or strongly style-shaped phrases).
- Consider mirroring similar checks in any lint tooling outside the test suite once these patterns have settled.
---

## 2025-12-10 – Slice: Pattern GUI surfaces Persona / Intent presets

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Model pattern picker shows Persona / Intent presets.

### Changes

- Updated `lib/modelPatternGUI.py` (now orchestrator-backed per ADR-0062 Loop 119) so the pattern picker uses `get_persona_intent_orchestrator()` for Persona/Intent presets, falling back to `lib.personaConfig` when the façade is unavailable.
- Extended the canvas renderer `_draw_pattern_canvas` so that, when a domain is selected, it shows a compact Who/Why section above the pattern list:
  - Heading: `Who / Why presets (ADR 040):`.
  - `Persona (Who):` followed by the first few persona presets, rendered as `label: voice · audience · tone` (omitting any empty axes).
  - `Intent (Why):` followed by the first few intent presets, rendered as `label: intent-token`.
  - Both blocks are wrapped in `try/except` so the pattern picker still renders even if presets cannot be imported under the Talon test harness.
- Left existing pattern buttons, recipes, and "Say: model …" hints unchanged so this remains a purely additive affordance.
- Ran `python3 -m pytest _tests/test_model_pattern_gui.py` to confirm the pattern GUI tests remain green.

### Rationale

- Surfaces the Persona (Who) and Intent (Why) presets from ADR 040 directly in the pattern picker, which is the main "recipes" surface for everyday use of the `model` grammar.
- Reinforces the Who/Why/How model without forcing users to remember preset names from docs: they can glance at the pattern picker to see exemplar persona and intent combinations alongside contract-focused patterns.

### Follow-ups

- Consider adding a small dedicated Persona/Intent preset picker in this canvas (clickable rows that pre-fill axes) once the current passive presentation proves stable.
- Mirror a similar Who/Why section into the suggestions modal so both major recipe surfaces stay aligned with ADR 040.
---

## 2025-12-10 – Slice: Suggestions GUI surfaces Persona / Intent presets

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Suggestions GUI shows Persona / Intent presets alongside contract recipes.

### Changes

- Updated `lib/modelSuggestionGUI.py` to hydrate suggestions via `get_persona_intent_orchestrator()` (with legacy `persona_intent_maps` as fallback) so the suggestions canvas reuses the shared Persona/Intent SSOT.
- Extended `_draw_suggestions` so that, when there are suggestions to show, it renders a compact Who/Why section above the suggestion rows:
  - Heading: `Who / Why presets (ADR 040):`.
  - `Persona (Who):` followed by the first few persona presets, as `label: voice · audience · tone` (omitting empty axes).
  - `Intent (Why):` followed by the first few intent presets, as `label: intent-token`.
  - Both blocks are wrapped in `try/except` so the suggestions canvas still renders if presets cannot be imported under the Talon test harness.
- Left the suggestion rows themselves unchanged: they still show `Say: model …` grammar phrases and a compact `Axes:` summary for the contract axes.
- Ran `python3 -m pytest _tests/test_model_suggestion_gui.py` to confirm the suggestions GUI tests remain green.

### Rationale

- Aligns the suggestions modal with ADR 040’s Persona/Intent/Contract framing, so users who open suggestions see Who/Why presets in the same place they browse contract-focused recipes.
- Reuses the same Persona/Intent SSOT as Help/Pattern GUIs, reducing duplication and keeping presets consistent across recipe-oriented surfaces.

### Follow-ups

- Consider making Persona/Intent presets in the suggestions canvas clickable in a future slice so users can quickly pivot the suggested contract recipes to a different Who/Why stance.
- Optionally add a short README/Help Hub note that `model suggest` plus the suggestions GUI now surfaces Who/Why presets as part of the ADR 040 family model.
---

## 2025-12-11 – Slice: Stance-aware suggest meta-prompt

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Enrich `model suggest` meta-prompt with Persona/Intent context and Stance/Why guidance.

### Changes

- Updated `docs/adr/040-axis-families-and-persona-contract-simplification.md` with a **Current status (this repo – 2025-12-11)** section summarising:
  - Persona/Intent SSOT and presets,
  - Help/GUI surfaces that already expose the Persona / Intent / Contract framing, and
  - The fact that prompt recipe suggestions now support optional per-recipe `Stance:` and `Why:` metadata.
- Extended the `model suggest` meta-prompt in `GPT/gpt.py` to:
  - Include a compact list of Persona presets (Who) and Intent presets (Why) derived from `PERSONA_PRESETS` and `INTENT_PRESETS`.
  - Explicitly instruct the LLM that, when helpful, each suggestion line may include an optional `Stance:` segment with a full `model write` command and a `Why:` segment explaining why that stance pairs well with the contract recipe.
  - Keep the existing, backward-compatible `Name: … | Recipe: …` format intact so older tests and suggestions remain valid; `Stance:` and `Why:` remain optional extra segments.
- Left the parsing logic and GUI wiring (added in earlier slices) unchanged; they already handle optional `Stance:` and `Why:` fields on a per-suggestion basis.

### Rationale

- Aligns the actual `model suggest` meta-prompt with ADR 040’s stance-aware suggestions design: the LLM now sees concrete Persona/Intent options and is explicitly invited to recommend a stance and a short explanation for each recipe.
- Keeps tests and existing behaviour stable by treating `Stance:` and `Why:` as optional add-ons; suggestions that only emit `Name` + `Recipe` continue to work as before.

### Follow-ups

- Observe how often the LLM now emits `Stance:`/`Why:` segments in practice and, if needed, further tighten the instructions (for example, making `Why:` mandatory for teaching/decision-oriented subjects).
- Consider adding a small footer hint in the suggestions GUI reminding users that `model reset writing` returns Persona/Intent and default contract settings to their base state after experimentation.

