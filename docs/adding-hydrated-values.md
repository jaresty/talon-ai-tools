# Adding Hydrated Axis/Persona Tokens

This is a crib sheet for adding new values for persona/intent (voice, audience, tone, purpose, stance), directional lenses, static prompts, and contract axes (completeness, scope, method, form, channel) while keeping Talon lists, hydration helpers, and tests aligned.

## 1) Add tokens to Talon lists (source of truth)
- Persona/intent lists: `GPT/lists/modelVoice.talon-list`, `modelAudience.talon-list`, `modelTone.talon-list`, `modelPurpose.talon-list`.
- Contract axes: `GPT/lists/completenessModifier.talon-list`, `scopeModifier.talon-list`, `methodModifier.talon-list`, `formModifier.talon-list`, `channelModifier.talon-list`, `directionalModifier.talon-list`.
- Static prompts: `GPT/lists/staticPrompt.talon-list`.
- Keep file format: `token: description` lines; no free-form prose or multiple tokens on one line.

## 2) Update structured configs
- Axis docs (hydrated descriptions): `lib/axisConfig.py` is generated from the registry. After editing the Talon lists, regenerate:
  - `python scripts/tools/generate_axis_config.py --out lib/axisConfig.py`
  - Commit the updated file so hydration maps stay in sync.
- Static prompts: add the token and axes/profile to `lib/staticPromptConfig.py` (description + axis defaults); descriptions are echoed in help/suggest prompts.
- Persona/intent presets: if adding preset-level stances, edit `lib/personaConfig.py` (persona presets) and `lib/personaConfig.py` intent sections, plus any supporting docs/examples in `docs/adr` if needed.

## 3) Wire tokens into hydration/canonicalisation helpers
- Axis hydration/canonical tokens come from `lib/axisMappings.py` and the registry it wraps. Once `axisConfig.py` is regenerated, helpers like `axis_hydrate_tokens` and `axis_key_to_value_map_for` will expose the new values.
- Static prompt hydration uses `lib/staticPromptConfig.py` + `lib/axisCatalog.py` (facade). Ensure your new static prompt has a profile (axes) so `_suggest_context_snapshot` and help views can show hydrated defaults.
- Stance validation for suggest results uses `lib/stanceValidation.py`; add any new persona/intent tokens/presets there if validation rejects them.

## 4) Keep Talon-facing catalogs in sync
- `lib/axisCatalog.py` reads both `axisConfig.py` and the Talon list files to detect drift. When adding tokens, rerun `python scripts/tools/axis-catalog-validate.py` (or run the full test suite) to ensure the lists and generated config match.
- If you add new lists, extend `_AXIS_LIST_FILES` in `lib/axisCatalog.py` so drift detection covers them.

## 5) Touch the suggest/rerun hydration paths
- Suggest context snapshot (tokens -> hydrated strings): `GPT/gpt.py` functions `_suggest_context_snapshot` and `_suggest_hydrated_context` pull persona/intent + axis defaults from `GPTState.system_prompt`. New tokens are surfaced automatically once the axis/persona maps are updated.
- Suggest parsing/normalisation: in `GPT/gpt.py`, `_normalise_recipe` enforces single static prompt and directional caps. If you add axes that affect caps, adjust here.
- Rerun/again canonicalisation: `_axis_value_from_token` (imported from `lib/modelPatternGUI.py`) and `modelPrompt` assembly rely on axis maps; regenerated `axisConfig.py` keeps them hydrated.

## 6) Update help and UI surfaces when adding user-facing values
- Help/cheatsheets pull from the catalogs: `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/promptPatternGUI.py`, and `docs/adr` fragments. Most stay in sync via `axisCatalog`, but new static prompt descriptions may need brief copy updates.
- Pattern/suggestion canvases use hydration helpers; no extra wiring is usually needed beyond the maps.

## 7) Tests to update/run
- Axis/list drift: `_tests/test_axis_catalog*.py`, `_tests/test_axis_docs.py`, `_tests/test_axis_mappings.py`.
- Static prompts: `_tests/test_static_prompt_*`.
- Persona/intent/stance: `_tests/test_persona_presets.py`, `_tests/test_suggestion_stance_validation.py`.
- Suggest integration: `_tests/test_integration_suggestions.py`.
- After changes, run `python3 -m pytest` from repo root.

## Quick checklist
1. Edit the appropriate `GPT/lists/*.talon-list` files with the new tokens/descriptions.
2. Add profiles/descriptions in `lib/staticPromptConfig.py` or `lib/personaConfig.py` as needed.
3. Regenerate `lib/axisConfig.py` via `scripts/tools/generate_axis_config.py`.
4. Verify drift/tests (`python3 -m pytest` or `scripts/tools/axis-catalog-validate.py`).
5. Spot-check suggest/help surfaces that display the new hydrated values.
