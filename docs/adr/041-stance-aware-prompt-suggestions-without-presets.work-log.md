# 041 – Stance-Aware Prompt Suggestions Without Presets in GUI – Work-log

## 2025-12-11 – Initial ADR drafted

- Captured the design intent that prompt recipe suggestions should:
  - Be driven by LLM-curated stance (Who/Why) and contract (How) recommendations, not by static Persona/Intent preset tables in the GUI.
  - Express stance recommendations as full `model write` commands using raw axis tokens (voice/audience/tone/purpose), with a short `Why` explanation per suggestion where helpful.
  - Keep the suggestions GUI focused on per-suggestion rows (`Name`, `Say: model run …`, `Axes: …`, optional `S1`/`Why` line) rather than a separate preset catalogue.
- Noted that Persona/Intent presets remain useful for pattern GUIs and documentation, but should not be rendered as a dedicated section in the suggestions window.
- No code changes in this slice; the current implementation (LLM-driven suggestions, optional stance/why metadata, no static preset table in the suggestions GUI) is already broadly aligned with this ADR.

## 2025-12-11 – Suggestions GUI behaviour confirmed

- Re-ran the `_tests/test_model_suggestion_gui.py` suite to confirm the current suggestions GUI behaviour.
- Verified that each suggestion row renders as `[Name]`, `Say: model run …`, `Axes: C:… S:… M:… St:… D:…`, plus an optional compact `S1: <stance_command> · Why: <reason>` line when stance/why metadata is present.
- Confirmed that clicking a suggestion row only executes the `model run` contract recipe and closes the GUI; stance (`model write …`) and reset (`model reset writing`) remain separate commands that are not implicitly bundled into the suggestion click path.
- Updated ADR 041's Implementation sketch to state explicitly that the GUI mimics verbal commands (`model run …`, `model write …`, `model reset writing`) rather than introducing a new combined "suggestion recipe" primitive.
- For this repo, there is currently no additional in-repo behaviour required for ADR 041 beyond ongoing prompt-tuning and minor UX polish; remaining work is primarily meta-prompt iteration, not structural changes.

## 2025-12-11 – ADR linkage updates

- Updated ADR 008 to reference ADR 041 in its Decision section where it describes the prompt recipe suggestions GUI, clarifying that ADR 041 refines this behaviour for stance-aware, preset-free suggestions.
- Updated ADR 040 to reference ADR 041 in the "Stance-aware suggestions (Who / Why / How)" implementation sketch, so contributors know to consult ADR 041 for the concrete suggestions GUI behaviour and preset treatment.
- This loop completes ADR 041's in-repo "Docs and ADR linkage" task; remaining work for this ADR is limited to future prompt-tuning and UX tweaks rather than additional structural changes in this repository.

## 2025-12-11 – Reset footer hint in suggestions GUI

- Implemented a compact, non-interactive footer hint in `lib/modelSuggestionGUI.py` that reads `Tip: say "model reset writing" to reset stance.` at the bottom of the suggestions window when suggestions are present.
- Kept the hint purely informational: it does not change per-suggestion behaviour or introduce a new control; clicking suggestion rows still only runs the `model run …` recipe and leaves stance/reset as separate, explicit commands per ADR 040/041.
- Re-ran `_tests/test_model_suggestion_gui.py` to confirm suggestion execution and GUI behaviour remain unchanged apart from the visual tip; all tests pass.
- This slice implements the optional reset footer tip described in ADR 041's Implementation sketch while preserving the "verbal commands, not new recipe primitive" constraint.

## 2025-12-11 – Suggest meta-prompt stance/why alignment

- Updated the `model suggest` meta-prompt in `GPT/gpt.py` so each suggestion line is still required to use the `Name: … | Recipe: …` shape, but may optionally append `| Stance: model write … | Why: …` segments when helpful.
- Clarified in the prompt that `Stance:` commands must be full `model write` commands expressed directly in terms of Persona/Intent axis tokens (`voice` / `audience` / `tone` / `purpose`) plus a `purpose`, and that `Why:` is a short explanation of why that stance+contract fit the subject.
- Tightened formatting rules to keep all segments for a suggestion on a single line, use literal `Name:`, `Recipe:`, `Stance:`, and `Why:` labels, and avoid extra commentary or multi-line explanations.
- Re-ran `_tests/test_gpt_actions.py`, `_tests/test_suggestion_coordinator.py`, and `_tests/test_model_suggestion_gui.py` to confirm parsing and GUI behaviour remain intact; 63 tests passed.
- This slice advances ADR 041's "Meta-prompt alignment" task by explicitly teaching the LLM how to emit optional stance/why metadata in a way that matches the parser and GUI, without changing the underlying `Name | Recipe` contract format.
