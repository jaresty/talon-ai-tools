# 040 – Axis Families and Persona/Contract Simplification – Work Log

## 2025-12-10 – Slice: Introduce Persona/Intent/Contract framing into GPT README

- **ADR**: 040 – Axis Families and Persona/Contract Simplification
- **Focus area**: Docs and help updates (GPT/readme.md) and ADR work-log wiring.

### Changes

- Updated `docs/adr/040-axis-families-and-persona-contract-simplification.md` to refer to the correct work-log filename and to point at the existing `_tests/test_voice_audience_tone_purpose_lists.py` rather than non-existent `tests/` paths.
- Added a `Persona / Intent / Contract (Who / Why / How)` section to `GPT/readme.md` ahead of the modifier axes, briefly explaining:
  - Persona (Who) = voice + audience + tone.
  - Intent (Why) = purpose.
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
  - `GPT/lists/modelPurpose.talon-list` now uses `for information: for information`, etc.
- Introduced `lib/personaConfig.py` as the Python SSOT for persona/intent semantics:
  - `voice` – keys like `as programmer`, `as teacher`, `as Kent Beck` mapped to rich “Act as …” descriptions.
  - `audience` – keys like `to managers`, `to junior engineer`, `to CEO`, `to XP enthusiast` mapped to audience descriptions.
  - `tone` – keys like `casually`, `formally`, `directly`, `gently`, `kindly` mapped to tone guidance.
  - `purpose` – keys like `for information`, `for deciding`, `for brainstorming`, `for teaching`, etc., mapped to intent descriptions.
- Updated `lib/modelTypes.GPTSystemPrompt.format_as_array` to hydrate persona and intent via `persona_hydrate_tokens` before sending the system prompt to the model:
  - `Voice: …`, `Tone: …`, `Audience: …`, and `Purpose: …` lines now expand short keys into full descriptions while contract axes (`completeness`, `scope`, `method`, `style`, `directional`) continue to hydrate via `axis_hydrate_tokens`.
- Kept Help docs rich after the list change by updating `GPT/gpt.py`’s `gpt_help` builder:
  - When rendering the Voice/Tone/Audience/Purpose tables, pass `description_overrides` built from `persona_docs_map('voice'/'tone'/'audience'/'purpose')` so the HTML docs show the full Python-side descriptions instead of the key-only list values.
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
    - Intent (Why): purpose.
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
    - Intent (Why): purpose.
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
  - “Explain simply to a junior engineer” → Persona (`as teacher` + `to junior engineer` + `tone=kindly`), Intent (`for teaching`), Contract (`completeness=gist/minimal`, `scope=focus`, `method=scaffold`, `style=plain`/`tight`), with a note not to encode it as a single new audience or purpose token.
  - “Executive brief for CEO” vs “Deep technical write-up for engineers” → contrasting Persona (different audiences and tones), Intent (for deciding vs for information/evaluating), and Contract (gist/focus/headline/tight vs full/system/structure/analysis/plain/adr), again emphasising that coverage/territory/reasoning/containers live on the contract axes.

### Rationale

- Gives contributors and users concrete, adversarial examples of how to apply the Persona / Intent / Contract model from ADR 040 in practice, directly in the main GPT README.
- Reinforces the question-gate rule by showing where **not** to encode behaviours (for example, not as new purpose/audience tokens) and instead use recipes across existing axes.

### Follow-ups

- Optionally mirror a shortened version of these examples into quick help or Help Hub docs so the same patterns are visible in in‑Talon surfaces.
