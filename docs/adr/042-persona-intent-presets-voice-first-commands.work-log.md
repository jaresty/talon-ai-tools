# 042 – Voice-First Persona and Intent Presets – Work Log

## 2025-12-11 – Slice: voice-first persona/intent preset commands

- Implemented dynamic Persona/Intent preset lists in `GPT/gpt.py`:
  - Added a `Context` and `mod.list` registrations for `personaPreset` and `intentPreset`.
  - Populated `ctx.lists["user.personaPreset"]` via `get_persona_intent_orchestrator()` (backed by `PERSONA_PRESETS`) using lowercased labels as spoken forms (for example, `teach junior dev`, `executive brief`).
  - Populated `ctx.lists["user.intentPreset"]` via `get_persona_intent_orchestrator()` (backed by `INTENT_PRESETS`) using lowercased keys as spoken forms (for example, `teach`, `decide`, `brainstorm`).
- Added stance actions to `GPT/gpt.py` under `UserActions` (ADR 042):
  - `persona_set_preset(preset_key: str)` – updates `GPTState.system_prompt` voice/audience/tone fields from a shared Persona preset while preserving Contract axes.
  - `intent_set_preset(preset_key: str)` – updates the `intent` field from an Intent preset while preserving Persona and Contract axes.
  - `persona_status()` / `intent_status()` – show current Persona/Intent stance vs defaults via `notify`, including a simple non-default/default suffix.
  - `persona_reset()` / `intent_reset()` – clear Persona (voice/audience/tone) or Intent (intent) back to default/empty while leaving Contract axes unchanged.
- Extended `GPT/gpt.talon` with new voice commands:
  - `persona {user.personaPreset}` → `user.persona_set_preset(personaPreset)`.
  - `intent {user.intentPreset}` → `user.intent_set_preset(intentPreset)`.
  - `persona status` / `intent status` → stance recaps.
  - `persona reset` / `intent reset` → stance resets.
- Updated `lib/modelPatternGUI.py` to make Persona/Intent presets clickable:
  - Added click bounds for each preset row in the "Who / Why presets" section.
  - Wired clicks to `actions.user.persona_set_preset(preset.key)` / `actions.user.intent_set_preset(preset.key)`.
- Added focused tests:
  - `_tests/test_gpt_actions.py` – Persona/Intent preset actions, status/reset behaviour.
  - `_tests/test_persona_presets.py` – token integrity and preset key coverage.
  - `_tests/test_prompt_pattern_gui.py` – pattern GUI behaviour remains correct with new preset rows.
- Ran targeted tests:
  - `python3 -m pytest _tests/test_gpt_actions.py _tests/test_persona_presets.py _tests/test_prompt_pattern_gui.py` (all passing).

## 2025-12-11 – Slice: stance recap and voice hints in help canvas

- Extended `lib/modelHelpCanvas.py` Who/Why/How section:
  - Kept the existing Persona/Intent preset summary lines.
  - Added a stance recap that reads `GPTState.system_prompt` and compares Persona/Intent axes (voice, audience, tone, intent) against their defaults.
  - When Persona/Intent are non-default, show:
    - `Persona: <voice>, <audience>, <tone>`
    - `Intent: <intent>`
    - A short example command hint: `Say: persona teach junior dev · intent teach`.
  - When Persona/Intent are at defaults, show a single hint line: `Stance: defaults active (say 'persona teach junior dev' to switch)`.
- This keeps ADR 042’s behaviour bounded to the help canvas for this loop; suggestions GUI stance recaps/buttons remain future work.
- Re-ran targeted tests for GPT/help surfaces:
  - `python3 -m pytest _tests/test_gpt_actions.py _tests/test_persona_presets.py _tests/test_model_help_canvas.py` (all passing).
