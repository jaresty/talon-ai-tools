# 041 – Stance-Aware Prompt Suggestions Without Presets in GUI

- Status: Accepted  
- Date: 2025-12-11  
- Context: Prompt recipe suggestions (ADR 008) and Persona / Intent / Contract framing (ADR 040) in `talon-ai-tools`.

---

## Summary (for users)

Prompt recipe suggestions (`model run suggest …`) are meant to do two things:

- Help you **execute** well-shaped `model run` prompts quickly.
- Help you **learn** how stance (Who/Why) and contract (How) interact with the LLM.

ADR 040 introduces Persona (Who), Intent (Why), and Contract (How). This ADR clarifies how prompt suggestions should surface **stance**:

- The suggestions GUI is driven by the **LLM’s own recommendations**, not by a local Persona/Intent preset catalog.
- Each suggestion may include a concrete **stance command** (`model write …`) and a short **Why** explanation, expressed directly in terms of `voice` / `audience` / `tone` / `intent` axis tokens.
- Persona/Intent **presets** remain useful in other surfaces (for example, the pattern GUI), but the suggestions GUI should not show a separate preset table or treat presets as first-class suggestion items.

---

## Context

Related ADRs:

- **008 – Prompt Recipe Suggestion Assistant** – defines `model suggest` and the prompt recipe suggestions GUI.
- **040 – Axis Families and Persona/Contract Simplification** – introduces Persona (Who), Intent (Why), Contract (How) families and stance-aware suggestions.

From these ADRs we have:

- A mature **Contract** surface: static prompts + completeness/scope/method/style + directional.
- A Persona/Intent SSOT in `lib/personaConfig.py` and small Persona/Intent preset lists for teaching and patterns.
- A suggestions GUI that already:
  - Displays `Name`, `Say: model run …`, and `Axes:` for each recipe.
  - Can render optional per-suggestion `stance_command` and `why` fields when present.

However, earlier iterations experimented with showing a static **Who/Why presets** block or leaning on presets as a primary teaching surface inside the suggestions window. That risks:

- Blurring the boundary between **LLM-calculated recommendations** and **hard-coded presets**.
- Consuming limited vertical space with duplicate information that is better suited to the pattern GUI or quick help.

---

## Decision

We adopt the following principles for prompt recipe suggestions:

1. **LLM-driven stance, raw axis tokens**  
   - Each suggestion line may include an optional **stance recommendation** expressed as a full `model write` command, for example:  
     - `Stance: model write as teacher to junior engineer kindly for teaching`  
   - This stance is defined directly in terms of Persona/Intent **axis tokens** (`voice` / `audience` / `tone` / `intent`), not via a preset name.

2. **Why explanations are per suggestion**  
   - Each suggestion may also include a short `Why:` segment:  
     - `Why: Kind, stepwise explanation for less-experienced devs.`  
   - This is the main teaching affordance: it explains *why* that particular stance+contract pairing is appropriate for the subject and source.

3. **Suggestions GUI does not display Persona/Intent preset tables**  
   - The suggestions GUI should **not** render a static list of Persona/Intent presets (for example, a “Who / Why presets” header with preset rows).  
   - Instead, it should:
     - Show, per suggestion:  
       - `[Name]`  
       - `Say: model run …` (contract recipe)  
       - `Axes: C:… S:… M:… St:… D:…`  
       - Optional compact line: `S1: <stance_command> · Why: <reason>` when metadata is present.  
     - Use vertical space for **LLM-generated** guidance rather than for preset catalogs.

4. **Presets remain for patterns and docs, not suggestion rows**  
   - Persona/Intent presets from `PERSONA_PRESETS` / `INTENT_PRESETS` remain useful for:
     - Pattern GUIs and recipe definitions.  
     - Docs and examples that introduce common stances (for example, “Teach junior dev”, “Executive brief”).
   - They may be used as *examples* in the `model suggest` meta-prompt, but suggestions themselves should always be expressed in terms of **raw axis tokens**.

5. **Reset remains a single, global command**  
   - `model reset writing` resets Persona/Intent and default contract settings.  
   - The suggestions GUI may include a single footer tip referencing this command, but **reset is not a per-suggestion field**; it is part of the overall workflow, not the individual recipe.

---

## Consequences

### Benefits

- Keeps the suggestions GUI focused on **LLM-curated recommendations**, not local preset tables.
- Users see the exact `model write` / `model run` sequences they can practice and adapt, with a short `Why` explanation per suggestion.
- Preserves Persona/Intent presets for places where they shine (pattern GUIs, docs) without coupling them tightly to the suggestion surface.

### Risks and mitigations

- **Risk: fewer obvious “preset names” in suggestions**  
  - Mitigation: keep presets visible in pattern GUIs and docs; use `Why` text in suggestions to convey the flavour of the stance instead of the preset label.

- **Risk: suggestions prompt becomes more complex**  
  - Mitigation: treat `Stance:` and `Why:` as optional segments; keep the existing `Name | Recipe` contract shape intact and rely on tests to enforce backward compatibility.

---

## Implementation sketch (this repo)

1. **Meta-prompt alignment**  
   - Ensure the `model suggest` meta-prompt:
     - Describes available Persona/Intent options primarily as **axis tokens** (voice/audience/tone/intent) grouped by axis.  
     - Uses Persona/Intent presets only as **examples**, not as the primary format for suggestions.  
     - Clearly documents the `Stance:` and `Why:` segments and encourages the LLM to emit them when helpful.

2. **Suggestions GUI behaviour**  
   - The suggestions GUI should mimic the **verbal commands**, not introduce a new combined "suggestion recipe" primitive.  
   - For each suggestion, keep a four-line layout:  
     - `[Name]`  
     - `Say: model run …` — the literal `model run` contract command the user can speak or click.  
     - `Axes: C:… S:… M:… St:… D:…` — compact contract summary matching that `model run`.  
     - Optional **Who/Why hint line**: `S1: model write … · Why: …` — the literal `model write` stance command plus its explanation, which the user may also invoke (by speech or a separate click affordance).  
   - Clicking the main suggestion row is equivalent to saying the `model run …` command only; any stance or reset actions (for example `model write …`, `model reset writing`) remain separate, explicit commands.  
   - Do **not** reintroduce a static Persona/Intent preset section at the top of the suggestions window.

3. **Docs and ADR linkage**  
   - Reference this ADR from ADR 008 and ADR 040 where they describe prompt recipe suggestions and stance-aware flows, so future contributors understand that presets are not first-class objects in the suggestions GUI.
