# 042 – Voice-First Persona and Intent Presets as First-Class Commands

- Status: Accepted  
- Date: 2025-12-11  
- Context: `talon-ai-tools` GPT `model` commands, Persona/Intent presets in `lib/personaConfig.py` and GUI/help surfaces (ADR 015, 026, 040, 041).

---

## Summary (for users)

This ADR turns **Persona/Intent presets** from “documentation-only examples” into **first-class, voice-first commands**.

Today:

- Persona/Intent presets live in `lib/personaConfig.py` as `PERSONA_PRESETS` and `INTENT_PRESETS`.
- Quick help, pattern GUI, and suggestions GUI show these presets as **labels plus axis decompositions** (for example, “Teach junior dev: as teacher · to junior engineer · kindly”).
- However:
  - There is **no voice command** to apply a preset directly.
  - Presets are **not clickable** in GUIs.
  - Users must **manually reconstruct** presets via `model write …` (voice/audience/tone/intent).

This ADR:

- Adds **short, distinct voice commands** for Persona/Intent presets:
  - `persona <preset>` (for example, `persona teach junior dev`).
  - `intent <preset>` (for example, `intent decide`, `intent brainstorm`).
  - `persona status`, `persona reset`, `intent status`, `intent reset`.
- Wires GUI presets so that **clicking** them applies the same commands.
- Keeps **Contract (How)** axes (`completeness`, `scope`, `method`, `style`, directional) **per-invocation** and unchanged.

Net effect: you can say or click “Teach junior dev” as a concrete action, not just read it as an example.

---

## Context

From ADR 040 and current implementation:

- **Persona/Intent families (Who/Why)**:
  - Persona (Who) – `voice`, `audience`, `tone`.
  - Intent (Why) – `intent`.
- **Contract (How)**:
  - `completeness`, `scope`, `method`, `style`.

Implementation status (this repo, 2025-12-11):

- `lib/personaConfig.py` defines:
  - `PERSONA_KEY_TO_VALUE` (axis token → description).
  - `PERSONA_PRESETS` – small, curated Persona recipes:
    - `"peer_engineer_explanation"` → `"Peer engineer explanation"` → `as programmer · to programmer`.
    - `"teach_junior_dev"` → `"Teach junior dev"` → `as teacher · to junior engineer · kindly`.
    - `"executive_brief"` → `"Executive brief"` → `as programmer · to CEO · directly`.
  - `INTENT_PRESETS` – similarly for `intent` (`teach`, `decide`, `plan`, `evaluate`, `brainstorm`, `appreciate`).
- Help surfaces (quick help, pattern GUI, suggestions GUI) render these presets as **text only**:
  - Quick help:  
    - `Persona presets: Peer engineer explanation, Teach junior dev, Executive brief`  
    - `Intent presets: Teach / explain, Decide, Plan / organise, Evaluate / review, Brainstorm, Appreciate / thank`
  - Pattern GUI:  
    - `Who / Why presets (ADR 040): Persona (Who): …, Intent (Why): …` with exact axis decompositions.

Speech layer today:

- Persona/Intent **axes** are only reachable via:

  - `model write [{user.modelVoice} | {user.modelAudience} | {user.modelIntent} | {user.modelTone}]+`
  - `model reset writing`

- `model run …` / `model …` commands only see:

  - `<user.modelPrompt>` → `[staticPrompt] [completeness] [scope+] [method+] [style+] {directional}` or `{customPrompt}`.

There is **no** command like `persona teach junior dev`, `intent decide`, or `persona status`, even though ADR 040 explicitly recommends such commands in its “Voice-first ergonomics” section.

---

## Problem

From an adversarial, user-focused perspective:

1. **Presets look like commands but aren’t**

   - GUIs and docs show names like “Teach junior dev”, “Executive brief”, “Teach / explain”.
   - They are presented alongside real commands and patterns.
   - A reasonable user expects:
     - Being able to **speak** the preset name (for example, `persona teach junior dev`, `model persona executive brief`).
     - Or being able to **click** it to change stance.
   - In reality, presets are just **rendered text**; clicking them does nothing, and there are no matching speech rules.

2. **Voice-only users have no ergonomic path from preset to action**

   - To “use” the “Teach junior dev” persona, a user must infer:
     - Preset → `as teacher · to junior engineer · kindly`.
     - Then synthesize:
       - `model write as teacher to junior engineer kindly for teaching`
   - It is easy to try:
     - `model describe teach junior dev fog`
     - `persona teach junior dev`
   - These phrases do **not** match any capture:
     - No `persona` or preset-capture rule exists.
     - Tokens like `teach`, `junior`, `dev` either get ignored or misparsed under other captures.
   - There is no explicit feedback that “presets are examples only; you must translate them into `model write …` yourself.”

3. **GUI users can “click on text-shaped buttons” that don’t act**

   - In pattern GUI, Persona/Intent presets are drawn above clickable patterns, with similar typographic emphasis.
   - Patterns are clickable and run recipes; presets are not.
   - A user may click a preset, see nothing, and:
     - Assume something subtle changed, or
     - Conclude the feature is broken or unfinished.

4. **ADR 040’s voice-first goals are only partially realized**

   ADR 040 says (paraphrased):

   - Treat Persona/Intent presets as **spoken commands first** and GUI labels second.
   - Provide `persona status`, `intent status`, `persona reset`, `intent reset`.
   - Keep Contract (How) per-invocation, with Persona/Intent as stance.

   Current implementation only delivers:

   - Python SSOT for Persona/Intent and presets.
   - Documentation and GUIs that show them.

   It does **not** deliver:

   - Any preset-level speech commands.
   - Status/reset commands scoped to Persona/Intent (beyond the broader `model reset writing`).
   - Clickable presets.

The net effect: Persona/Intent presets increase **cognitive load** (more names and tables) without adding **commensurate ergonomic power**.

---

## Decision

We will:

1. **Introduce first-class Persona/Intent preset commands**

   Add short, distinct voice commands:

   - `persona <personaPreset>`  
     - Example: `persona teach junior dev`, `persona executive brief`.
     - Applies the corresponding preset’s `voice`/`audience`/`tone` to the current stance.
   - `intent <intentPreset>`  
     - Example: `intent teach`, `intent decide`, `intent brainstorm`.
     - Applies the corresponding preset’s `intent`.

   These commands are defined over the existing SSOT:

   - Preset token sets from `PERSONA_PRESETS` and `INTENT_PRESETS`.
   - They **do not** introduce new axis semantics; they are a more ergonomic front end to existing lists and `model write`.

2. **Define clear semantics: stance vs per-invocation**

   - Persona/Intent presets **update the persistent writing stance** (same layer as `model write`):
     - `persona <preset>` and `intent <preset>` are equivalent to a focused `model write …` call for Persona/Intent only.
     - Example:
       - `persona teach junior dev`  
         ≈ `model write as teacher to junior engineer kindly`
       - `intent teach`  
         ≈ `model write for teaching` (preserving existing voice/audience/tone where possible).
   - Contract axes remain **per-invocation**, driven by:
     - `model …` grammar (completeness/scope/method/style/directional),
     - Static-prompt profiles,
     - Existing defaults.

   Rationale:

   - Keeps ADR 040’s contract: Persona/Intent = “stance”; Contract = “How”.
   - Avoids adding “one-shot persona overlay” complexity until there is a concrete need.

3. **Add Persona/Intent status and reset commands**

   Implement dedicated commands:

   - `persona status` – speak and/or show a recap:
     - Current `voice`, `audience`, `tone`.
     - Whether they differ from defaults.
     - Example recap:
       - `Persona: as teacher · to junior engineer · kindly (non-default)`
   - `intent status` – recap:
     - Current `intent`, whether it is non-default.
   - `persona reset` – reset Persona axes to defaults:
     - Clears explicit `voice`/`audience`/`tone` stance.
   - `intent reset` – reset `intent` to default.
   - `persona clear` / `intent clear` can be aliases or folded into `reset` semantics depending on existing conventions.

   These coexist with the broader:

   - `model reset writing` – full reset of Persona + any other writing-level defaults.

4. **Wire presets into GUIs as actual actions**

   - In quick help, pattern GUI, and suggestions GUI:
     - Ensure Persona/Intent preset labels have **matching spoken forms** and act as **entry points** to the same actions as the voice commands.
   - Concretely:
     - Pattern GUI:
       - Preset labels become clickable; clicking:
         - Calls the same action as `persona <preset>` / `intent <preset>`.
         - Optionally shows a short toast/recap:  
           - `Persona set to: as teacher · to junior engineer · kindly`
     - Suggestions GUI:
       - When suggestions include recommended stance:
         - Show a small “Apply persona” / “Apply intent” button that triggers the preset commands.
   - Keep interaction **compact**:
     - No extra popups.
     - Use recaps in existing help/confirmation surfaces.

5. **Preserve the simple “just help me” path**

   - All new commands are **optional**:
     - `model describe fog` continues to work with defaults.
   - Presets and stance commands are treated as **advanced** affordances:
     - Shown in quick help and GUIs but not required for normal usage.
   - Defaults and confirmation surfaces are updated to explicitly call out when Persona/Intent stance is non-default:

     - Example:
       - `Recipe: todo · full · focus · steps · plain · rog`
       - `Stance: Persona=Teach junior dev, Intent=Teach / explain`

---

## Consequences

### Benefits

- **Ergonomic alignment with ADR 040**

  - Persona/Intent presets become **spoken commands first, GUI labels second**.
  - Voice-only users can say exactly what GUIs show.
  - The Who/Why framing has clear, actionable entry points.

- **Reduced confusion and mis-guessing**

  - Users no longer need to reverse-engineer `model write` commands from textual presets.
  - Fewer “I thought I could say ‘teach junior dev’ and nothing happened” failure modes.

- **Reuse of existing SSOTs**

  - No new axis semantics.
  - Presets remain defined in `personaConfig.PERSONA_PRESETS` / `INTENT_PRESETS`.
  - Speech and GUIs call into the same Python actions.

### Risks and mitigations

1. **Risk: new commands clutter the grammar**

   - Mitigation:
     - Keep preset names short, distinct, and few (already enforced by tests).
     - Scope commands under clear prefixes (`persona …`, `intent …`).

2. **Risk: stance becomes “sticky” and users forget they changed it**

   - Mitigation:
     - `persona status` / `intent status` for visibility.
     - Explicit recap lines in confirmation GUI / quick help.
     - Encourage `persona reset` / `intent reset` in docs and suggestions.
     - Optionally bias suggestions to recommend a reset after focused persona usage.

3. **Risk: confusion vs existing `model write` semantics**

   - Mitigation:
     - Implement preset commands as **thin wrappers** around `gpt_set_system_prompt` / `model write` equivalents.
     - Document that:
       - `persona <preset>` = “set Persona stance to preset axes”.
       - `model write` still exists for arbitrary combinations.

4. **Risk: GUI clicks silently fail if actions break**

   - Mitigation:
     - Wrap preset-click handlers in robust error handling.
     - Notify users on error (“Could not apply persona preset; see logs”).

---

## Implementation Sketch

1. **Preset name mapping**

   - Extend `personaConfig.PersonaPreset` / `IntentPreset` to expose a **short spoken name**, or derive one from `label`:
     - For example:
       - `key="teach_junior_dev"`, `spoken="teach junior dev"`.
       - `key="executive_brief"`, `spoken="executive brief"`.
   - Add helper functions:
     - `persona_preset_by_spoken_name(spoken: str) -> PersonaPreset | None`
     - `intent_preset_by_spoken_name(spoken: str) -> IntentPreset | None`
   - Keep SSOT in Python; do not hard-code preset names in Talon lists beyond what is necessary for speech captures.

2. **Talon module + actions**

   - In a suitable Python module (likely `GPT/gpt.py` or a small helper):

     - Add actions:

       - `user.persona_set_preset(preset_key: str)`:
         - Looks up preset in `PERSONA_PRESETS`.
         - Applies `voice`/`audience`/`tone` via existing system prompt/`GPTState` setters.
       - `user.intent_set_preset(preset_key: str)`:
         - Looks up preset in `INTENT_PRESETS`.
         - Applies `intent`.
       - `user.persona_status()`, `user.intent_status()`:
         - Read current Persona/Intent from `GPTState.system_prompt`.
         - Show recap via notification / help canvas.
       - `user.persona_reset()`, `user.intent_reset()`:
         - Reset Persona/Intent fields to defaults or empty.
         - Optionally share implementation with `gpt_reset_system_prompt`.

3. **Talon grammar**

   - In a `*.talon` file (likely `GPT/gpt.talon` or a new persona-focused file):

     - Register lists:

       - `list: user.personaPreset`
       - `list: user.intentPreset`

     - Populate them from Python (`mod.list`) using `PERSONA_PRESETS` / `INTENT_PRESETS` at load time, so there is one SSOT.

     - Add rules:

       - `persona {user.personaPreset}: user.persona_set_preset(personaPreset)`
       - `intent {user.intentPreset}: user.intent_set_preset(intentPreset)`
       - `persona status: user.persona_status()`
       - `intent status: user.intent_status()`
       - `persona reset: user.persona_reset()`
       - `intent reset: user.intent_reset()`

     - Optionally add `model persona …` / `model intent …` aliases if they fit the existing naming scheme better.

4. **GUI integration**

   - `lib/modelPatternGUI.py`:

     - For each Persona preset row:
       - Add a button region (like patterns already have).
       - On click, call `actions.user.persona_set_preset(preset.key)`.

     - For each Intent preset row:
       - Similar, calling `actions.user.intent_set_preset(preset.key)`.

    - `lib/modelHelpCanvas.py`:
 
      - Keep listing of Persona/Intent presets in the Who/Why/How section.
      - Add a stance recap that reads `GPTState.system_prompt` Persona/Intent axes
        (voice, audience, tone, intent) versus defaults and shows a single
        example stance voice command, e.g. `Say: persona teach junior dev · intent teach`.
 
    - `lib/modelSuggestionGUI.py`:
 
      - Treat Persona/Intent as the canonical stance model while preserving a
        flexible, model-authored stance string for each suggestion.
      - Extend the `Suggestion` dataclass conceptually to include both:
        - Structured axes (all optional, empty string when not applicable):
          - `persona_voice`, `persona_audience`, `persona_tone`, `intent_purpose`.
        - A free-form, voice-friendly `stance_command` string that the model can
          compose (for example, `persona teach junior dev · intent teach` or
          `model write as teacher to junior engineer kindly for teaching`).
      - In the GUI stance block for each suggestion:
        - When any structured Persona/Intent axes are present, render them as
          the primary stance summary, e.g.
          - `Stance: Persona=Teach junior dev, Intent=Teach / explain`
          - `Persona: as teacher · to junior engineer · kindly`
          - `Intent: for teaching`.
        - When `stance_command` is present and meaningfully different from the
          axis summary, render it as a single S1 line, e.g.
          - `S1: persona teach junior dev · intent teach`.
        - When no structured axes are available but `stance_command` is, fall
          back to rendering only the S1 line as the stance for that suggestion.
      - Do not introduce a second, independent "Stance" concept; instead,
        always interpret stance in terms of Persona/Intent (Who/Why) plus a
        single flexible `stance_command` string.


5. **Recap surfaces**

   - Extend confirmation GUI / quick help recaps to include Persona/Intent when non-default:

     - Example line:
       - `Stance: Persona=Teach junior dev, Intent=Teach / explain`

   - Use existing `GPTState.system_prompt` fields plus `PERSONA_PRESETS` / `INTENT_PRESETS` to map back from raw tokens to preset labels where possible.

6. **Tests**

   - Add focused tests (for example in `_tests/test_persona_presets.py` and new test modules):

     - Preset lists:
       - All preset spoken names map to valid keys.
     - Actions:
       - `persona_set_preset` and `intent_set_preset` correctly apply axis tokens to `GPTState.system_prompt`.
       - `persona_reset` / `intent_reset` clear Persona/Intent without touching contract axes.
     - Recaps:
       - `persona_status` / `intent_status` correctly reflect default vs non-default stance.
     - GUI behaviour:
       - Pattern GUI clicks call the correct actions (covered via small integration tests if feasible).

---

## Adversarial Stress Tests (for this ADR)

1. **Voice-only user, no docs open**

   - Says: `persona teach junior dev`.
   - Expected:
     - No error from Talon.
     - Persona stance set to `as teacher · to junior engineer · kindly`.
     - `persona status` reflects this.
   - Contract-only `model describe fog` uses that stance.

2. **User clicks “Teach junior dev” in pattern GUI**

   - Expected:
     - Same effect as `persona teach junior dev`.
     - Optional toast: “Persona set to Teach junior dev: as teacher · to junior engineer · kindly”.

3. **User forgets stance and asks “what’s going on?”**

   - Says: `persona status`.
   - Expected:
     - Explicit recap:
       - Defaults vs current values.
       - Friendly hint: “Say ‘persona reset’ to return to defaults.”

4. **User mixes presets and manual `model write`**

   - Flow:
     - `persona executive brief`
     - `model write as programmer to team directly`
     - `intent decide`
   - Expected:
     - Last command wins on overlapping axes.
     - Status shows the final, effective stance (not both).

5. **User never touches Persona at all**

   - Expected:
     - No change in behaviour vs current repo.
     - Preset commands and status/reset are invisible unless used.

If the implementation passes these adversarial cases, Persona/Intent presets will finally behave like the “spoken first” primitives ADR 040 envisioned, instead of remaining as static examples.
