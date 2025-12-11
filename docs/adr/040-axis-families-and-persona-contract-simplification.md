# 040 – Axis Families and Persona/Contract Simplification

- Status: Accepted  
- Date: 2025-12-10  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style + directional modifiers + voice/audience/tone/purpose)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation for Axis-Based Grammar  
  - 012 – Style and Method Prompt Refactor  
  - 013 – Static Prompt Axis Refinement and Streamlining  
  - 015 – Voice, Audience, Tone, Purpose Axis Decomposition  
  - 018 – Axis Modifier Decomposition into Pure Elements  
  - 026 – Axis Multiplicity for Scope/Method/Style  
  - 032 – Constraint Hierarchy Meta-Spec for Completeness/Method/Scope/Style  
  - 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails  

---

## Summary (for users)

The current grammar exposes **eight conceptual knobs** around a `model` command:

- **Persona / social**: voice, audience, tone, purpose.  
- **Contract / mechanics**: completeness, scope, method, style.

Existing ADRs (005, 012, 015, 018, 026, 032, 033) have already:

- Clarified each axis in isolation,  
- Moved many overloaded items into the “right” axis, and  
- Added hierarchy/overlap guardrails.

However, when you are *actually* trying to speak or teach the grammar, these eight knobs still feel like **too many overlapping concepts**. Users struggle to decide:

- “Is this ‘briefly’ or `gist` or `tight`?”  
- “Am I talking to `to junior engineer`, using `scaffold`, or both?”  
- “Is ‘adversarial review’ a voice, a purpose, or a method?”

This ADR does **not** add or remove axes. Instead, it introduces a **three-family mental model** and corresponding **teaching/UX constraints** so that, in practice, people experience:

- **Who** → Persona family: `voice` + `audience` + `tone` (optionally bundled as presets).  
- **Why** → Intent family: `purpose`.  
- **How** → Contract family: `completeness`, `scope`, `method`, `style`.

We standardise question-based gates and adversarial tests for each family, and we recommend that default docs and GUIs **present families, not raw axes**, so most users see 3–4 big levers instead of 8.

This reduces cognitive load without removing power: advanced users can still manipulate all axes directly, and all existing semantics remain available.

---

## Context

Prior ADRs give us:

- A clear **contract layer** (completeness/scope/method/style) with orthogonality and hierarchy (005, 012, 018, 026, 032, 033).  
- A trimmed, more principled **persona/intent layer** (voice/audience/tone/purpose) with most “how/shape” semantics moved into axes and recipes (015, 017, 018).

Despite this work, real-world usage and help-surface feedback show recurring confusion:

1. **Persona vs contract leakage**  
   - “Explain to junior engineer, briefly, in plain language” plausibly touches:  
     - Audience: `to junior engineer`.  
     - Completeness: `gist` / `minimal`.  
     - Style: `plain`, `tight`.  
     - Tone: `kindly`.  
   - Users regularly try to encode this as **only** an audience (`to dummy`-style), **only** tone (`briefly`), or a mix of axes.

2. **Tone vs style confusion**  
   - ADR 015 defines tone as emotional register (casual/formal, gentle/direct, kind), while ADR 005/012 treat style as surface form (`plain`, `tight`, `bullets`, `table`, `code`, `slack`, `adr`, etc.).  
   - In practice, users conflate:  
     - `casually` vs `plain`,  
     - `directly` vs “headline first” (`headline` style/method),  
     - “friendly but concise” → tone *and* style *and* completeness.

3. **Purpose vs method/directional**  
   - ADR 015 already migrates `for diverging/converging/mapping/discovery/framing/sensemaking` into method + scope + directional.  
   - Yet phrases like “brainstorm options then converge on a decision” still attract both purpose (`for brainstorming`, `for deciding`) and method (`diverge`, `converge`) and directional lenses.  
   - Without a simple “which family?” gate, new purposes risk re-introducing method/contract semantics.

4. **Voice vs audience overlap**  
   - We now have roles on both axes (for example, `as PM` vs `to product manager`, `as CEO` vs `to CEO`).  
   - ADR 015 pushes org roles toward audience, but the **surface grammar** still encourages stacking (`as PM to PM to team`), which reads redundant and invites misuse (“should I say this as CEO or to CEO?”).

5. **Axis proliferation at the point of use**  
   - `model` help currently presents separate tables for: static prompts, directional/goal modifiers, voice/audience/tone/purpose, and four contract axes.  
   - Even with small lists, that’s 8+ conceptual dimensions visible at once.  
   - New contributors must learn both **semantics** and **where to add new tokens** across multiple files and ADRs.

The net effect: the *design* is clean, but the **experienced complexity** at the speech/UI layer is still high.

---

## Adversarial stress tests

This section applies an adversarial stance to the current axis set, focusing on where a reasonable but confused user could misfile behaviour.

### Test 1 – “Explain simply to a junior engineer”

Desired behaviour (intuitively):

- Audience: a junior engineer.  
- Contract: low completeness, simple language, stepwise scaffolding.  
- Tone: kind, not patronising.

Plausible encodings today:

- `to junior engineer` (audience) + `briefly` (tone, now retired into completeness/style) + `plain` (style) + `scaffold` (method) + `gist` (completeness).  
- Or only `to dummy` (audience, removed) or `as teacher` (voice) with no axes.  
- Or a static prompt like “explain like I’m five”.

Failure mode: users repeatedly re-encode the **same behaviour** in different combinations of audience, tone, completeness, method, style, and sometimes static prompts. ADR 015/018/032/033 mitigate this by tightening definitions, but they don’t give a *single, ergonomic way* to answer: “Where should this idea live?”

### Test 2 – “Adversarial review for resistant stakeholders”

Desired behaviour:

- Persona: probably `as programmer` or `as editor`, `to stakeholders`.  
- Intent: `for evaluating`.  
- Contract: adversarial reasoning, full/deep coverage, case-building structure, critical but not hostile tone.

Possible encodings users try:

- `as adversary` (voice, now retired) + `to resistant` (audience, now retired) + `for debugging` (purpose, retired) + some axes.  
- Tone: `directly`, or an imagined `adversarial` tone.  
- Method: `adversarial`, `case`, `debugging`.  
- Style: `bug` or `table`.

Even after ADR 015’s migration, it is easy to place “adversarial” in **voice, tone, purpose, method, or style** unless you carry the entire ADR stack in your head. The **family boundary** (“Is this about *who* is speaking, or *how* they reason?”) needs to be foregrounded, not buried in ADR prose.

### Test 3 – “Executive brief vs deep technical write-up”

Desired contrast:

- Persona: `to CEO` vs `to programmer/principal engineer`.  
- Intent: `for information` or `for deciding`.  
- Contract:  
  - Exec brief → narrow, high-level scope; `gist` completeness; `headline` method; `tight` style.  
  - Deep write-up → `system`/`relations` scope; `full`/`deep` completeness; `structure` + `analysis` methods; `plain` or `adr` style.

Users often reach for:

- Voice: `as CEO`, `as principal engineer`.  
- Purpose: `for announcing`, `for mapping`.  
- Tone: `formally`, `directly`.  
- Contract axes.

The line between **persona** (“this is for CEO”) and **contract** (“headline gist only”) is conceptually clean in ADR 005/015, but hard to see in the help tables. Adversarially, it is too easy to encode presentation/coverage/shape into voice/purpose tokens again.

### Test 4 – “Playful but dense explanation”

Desired behaviour:

- Persona: maybe unchanged; audience `to team`.  
- Intent: `for teaching` or `for entertainment`.  
- Contract: high completeness (`full`), playful/`casually` tone, possibly `tight` style.

Where does “playful but dense” live?

- Tone: `casually`, `kindly`.  
- Completeness: `full`.  
- Style: `tight` (concise), maybe `plain`.  
- Purpose: `for entertainment` or `for information`.

Without a **family-first** framing, contributors are tempted to add playful-specific purposes, tones, or styles, re-introducing axis drift ADR 015/018 worked to eliminate.

---

## Decision

We introduce an explicit **axis family model** and associated **design rules**:

1. **Three axis families**  
   We treat the eight concepts as belonging to three question-based families:

   - **Persona (WHO)** – social framing:  
     - `voice`: who is speaking?  
     - `audience`: who is this for?  
     - `tone`: what emotional/relational register?  
   - **Intent (WHY)** – interaction-level intent:  
     - `purpose`: why are we talking? (inform, persuade, decide, coach, etc.).  
   - **Contract (HOW)** – behavioural contract with the model:  
     - `completeness`: how much coverage?  
     - `scope`: what territory is in-bounds?  
     - `method`: how does reasoning proceed?  
     - `style`: in what visible shape/container?

   These families are **conceptual and UX-level**: existing code and tests continue to treat each axis separately, but documentation and help surfaces should consistently teach the three questions first: **Who? Why? How?**

2. **Question gates for axis assignment**  
   When deciding where a behaviour lives (or whether to introduce a token at all), contributors must answer **exactly one primary question**:

   - Does this primarily change **who** is speaking or addressed?  
     - → Persona family (`voice`/`audience`).  
   - Does this primarily change the **emotional feel** of the response?  
     - → Persona family (`tone`).  
   - Does this primarily change **why** the interaction is happening?  
     - → Intent family (`purpose`).  
   - Does this primarily change **how much** must be covered?  
     - → Contract (`completeness`).  
   - Does this primarily change **what is in-bounds vs out-of-bounds**?  
     - → Contract (`scope`).  
   - Does this primarily change **how the model thinks or decomposes** the task?  
     - → Contract (`method`).  
   - Does this primarily change the **surface container or layout** of the answer?  
     - → Contract (`style`).

   If honest answers hit *more than one* bullet, the behaviour **must be decomposed** into:

   - A small recipe across existing axes, or  
   - A named pattern/static prompt that sets multiple axis values,  

   rather than a new raw axis token.

3. **Persona presets instead of raw knob piles**  
   For end users, **default help and GUIs** should present persona as presets, not four independent controls:

   - Examples:  
     - “Peer engineer explanation” → `as programmer` + `to programmer` + `tone=neutrally`.  
     - “Teach junior dev” → `as teacher` + `to junior engineer` + `tone=kindly`.  
     - “Executive brief” → `as programmer` + `to CEO` + `tone=directly`/`formally`.  
   - Internally, these presets still map to voice/audience/tone.  
   - Advanced users can override individual axes, but the **first-class UX primitive** is a small set of persona recipes, not the raw lists.

4. **Intent presets layered on top of persona**  
   Similarly, we recommend exposing `purpose` as **named intent presets** rather than a long flat list:

   - “Teach”, “Decide”, “Plan”, “Evaluate”, “Brainstorm”, “Appreciate”.  
   - These are already present as purposes; this ADR says:  
     - Default help/GUI surfaces should group them explicitly under **Why?**  
     - Axis docs should emphasise that new purposes must be interaction-level whys (per ADR 015), not containers, methods, or destinations.

5. **Contract remains the primary power surface**  
   For power users and static prompt authors, the **contract family** remains the main way to tune behaviour:

   - `completeness` – scalar, per ADR 005/018/026.  
   - `scope`, `method`, `style` – multi-tag, per ADR 026, with purity constraints from ADR 018 and hierarchy from ADR 032/033.  

   This ADR adds one constraint: **persona and intent should not attempt to carry contract semantics**. When stress-tested:

   - If an audience/voice/purpose description makes strong claims about coverage, territory, reasoning steps, or containers, those claims must be moved into contract axes or patterns.

6. **Teaching surfaces present families, not raw lists**  
   We standardise how help/GUI surfaces should present axes:

   - In `model` quick help / Help Hub / axis docs:  
     - Group sections as **Persona (Who)**, **Intent (Why)**, **Contract (How)**.  
     - Within each family, show axis names and their main question.  
     - De-emphasise raw axis names in user-facing copy where it is clearer to say “Who / Why / How”.

   - Example structure for quick help:  
     - Persona: a 2–3 row cheat sheet with presets and their underlying axes.  
     - Intent: short list of purposes under a “Why” header.  
     - Contract: tabular summary of completeness/scope/method/style, as today, but explicitly labelled under “How”.

---

## Consequences

### Benefits

- **Lower cognitive load at the speech/UI layer**  
  - Users learn three questions—Who, Why, How—instead of eight semi-overlapping nouns.  
  - Axis-specific details become an implementation detail for power users and contributors.

- **Stronger guardrails against reintroducing overlap**  
  - The question-gate checklist gives a concrete, adversarial test for every new behaviour: if it answers multiple questions, it cannot be a single axis token.  
  - This complements ADR 018/032/033’s per-axis purity and hierarchy rules.

- **Easier teaching and docs**  
  - Docs, quick help, and examples can explain the system as:  
    - Pick **a task** (static prompt).  
    - Optionally pick **Who** (persona preset) and **Why** (intent).  
    - Tune **How** (contract axes).  
  - Migration tables from ADR 012/015/018 can be re-framed under these families, making them easier to internalise.

- **No loss of expressive power**  
  - All existing axes, tokens, and recipes remain valid.  
  - We only change how they are grouped and taught, not how they are interpreted.

### Risks and mitigations

- **Risk: more documentation churn**  
   - Help and README surfaces must be updated to use the family model.  
   - Mitigation: do this incrementally, starting with Help Hub axis docs and quick help; static prompt docs can follow.
 
 - **Risk: hidden complexity for advanced users**  
   - If GUIs over-emphasise presets, some users may not realise they can still set raw axes.  
   - Mitigation: provide an “Advanced view” / “Show axes” toggle in GUIs, and keep `gpt_help` tables comprehensive.
 
 - **Risk: overserving configuration vs “just help me”**  
   - If persona/intent presets, persistence, and status/reset commands are surfaced too prominently, users who only want a quick answer may face more decisions, not fewer.  
   - Mitigation: keep the basic “get help” path focused on static prompts + contract axes; treat persona/intent presets and persistence controls as **advanced** affordances in docs and UIs, and do not require them for everyday use.
 
 - **Risk: family model drifts from implementation**  
   - If future ADRs modify axis semantics without updating families, confusion could return.  
   - Mitigation: require new axis-related ADRs to state which family(ies) they touch and update this ADR’s work-log if they change family boundaries.


---

### Current status (this repo – 2025-12-11)

- Persona / Intent SSOT is implemented via `lib/personaConfig.py`, with shared `PERSONA_PRESETS` and `INTENT_PRESETS` used by help surfaces and GUIs.
- Help Hub, canvas quick help, pattern GUI, and the suggestions GUI all now expose the Persona / Intent / Contract (Who / Why / How) framing in some form.
- Prompt recipe suggestions (ADR 008) still treat `Recipe` as primarily a Contract (How) recommendation, but the parsing and suggestion GUI now support optional per-recipe `Stance:` and `Why:` metadata.
- The `model write …` / `model reset writing` flow is the primary way to change/reset Persona/Intent; suggestions are intended to teach good combinations rather than silently alter stance.
- Remaining in-repo work for this ADR is mostly prompt-tuning (improving how consistently the LLM emits useful `Stance:`/`Why:` segments) and small UX polish, not structural changes.


## Implementation sketch (this repo)

1. **Docs and help updates**  
   - In `GPT/readme.md` and axis docs:  
     - Introduce “Persona / Intent / Contract” framing early.  
     - Add a short “Who / Why / How” table mapping to axes.  
   - In quick help / Help Hub (for example, `lib/modelHelpGUI.py`, `lib/modelHelpCanvas.py`, ADR 022/028 surfaces):  
     - Group sections under Persona / Intent / Contract headings.  
     - Show small persona and intent preset tables, with underlying axis decompositions in secondary text.

2. **Persona and intent presets**  
   - Define a small set of shared persona presets in a SSOT (for example, a `PERSONA_PRESETS` mapping in an appropriate module):  
     - Each preset: `{name, voice, audience, tone}`.  
   - Similarly define intent presets for common purposes.  
   - Align `modelVoice.talon-list`, `modelAudience.talon-list`, `modelTone.talon-list`, and `modelPurpose.talon-list` with the axis list pattern by keeping them as token→key carriers (for example, `spoken: key` or effectively `key: key`), and move longer labels/descriptions into a Python-side doc/lookup layer that is only hydrated when constructing prompts for the model.  
   - Surface these presets in pattern GUIs, the suggestions modal, and/or a lightweight persona/intent picker, without changing the underlying lists or system prompt representation.

3. **Axis-family contribution rules**  
   - Update contributor docs (`CONTRIBUTING.md` “GPT prompts, axes, and ADRs” section) to:
     - Require using the question-gate list in this ADR when adding tokens.  
     - Explicitly answer “Which family?” and “Why not a recipe/pattern instead?” for any new behaviour.  
   - Optionally add a small lint/test helper that asserts:  
     - New tokens in voice/audience/tone/purpose do not contain obviously contract-shaped words (for example, “brief”, “table”, “diagram”, “debugging”).  
     - New contract tokens do not contain obvious persona/intent words (“executive”, “novice”, “persuasion”).
 
  4. **Stance-aware suggestions (Who / Why / How)**  
   - See also ADR 041 for stance-aware prompt suggestions GUI behaviour and preset-free design.

   - When implementing prompt recipe suggestions (ADR 008) in this repo, treat each suggestion as a small, teachable three-step flow:
     - Step 1 – **Set stance (Who / Why)** using Persona and Intent presets (for example, a `model write …` command that sets voice/audience/tone/purpose for writing).  
     - Step 2 – **Run contract (How)** using `model run <staticPrompt> [completeness] [scope] [method] [style] <directional>` as today.  
     - Step 3 – **Optionally reset stance** (for example, `model reset writing`) to return to defaults after a focused interaction.  
   - When calling the LLM to generate suggestions, provide:
     - The current request and source summary.  
     - The current stance snapshot (active Persona/Intent presets or raw axis keys).  
     - The available Persona presets (`PERSONA_PRESETS`), Intent presets (`INTENT_PRESETS`), and contract axes/tokens that are safe to suggest.  
   - Ask the LLM to return, for each suggestion:
     - A recommended Persona/Intent preset (or “keep current” stance), expressed as preset keys and/or a concrete “set stance” command.  
     - A recommended contract recipe (static prompt + completeness/scope/method/style + directional) and its `model run …` form.  
     - Whether to recommend a stance reset afterwards and, if so, the concrete reset command.  
     - A short, one-line explanation of why this stance+contract pairing is appropriate for the current task.  
   - In the suggestions GUI, surface these as **compact** rows that respect vertical space:
     - Show at most a handful of stance suggestions (for example, 2–3 Persona presets and 2–3 Intent presets) and keep each explanation to a single line.  
     - Keep the existing contract `Say: model run …` and `Axes:` summaries; do not enlarge the window purely for Who/Why text.
 
 5. **Adversarial examples in docs**  

   - Add a small appendix (in README or quick help) that revisits the stress tests above (“Explain simply to a junior engineer”, “Adversarial review for resistant stakeholders”, “Executive brief vs deep write-up”) and shows:  
     - How each is expressed using Persona + Intent + Contract,  
     - Where *not* to encode each behaviour (for example, not as a new purpose or voice).

5. **Work-log and guardrails**  
   - Track concrete slices of this ADR in a `docs/adr/040-axis-families-and-persona-contract-simplification.work-log.md` file as changes land.  
   - Ensure tests that already guard axis semantics (for example, `_tests/test_voice_audience_tone_purpose_lists.py`, and any axis/readme/help Hub tests) continue to pass as help/README structure changes, adding small assertions where useful (for example, that help surfaces show the family grouping text).

6. **Voice-first ergonomics (Talon)**  
   - Treat persona and intent presets, and high-value pattern recipes, as **spoken commands first** and GUI labels second.  
   - Ensure each preset and suggested recipe has a **short, phonetically distinct spoken form** that fits the `model` grammar and can be re-spoken by users.  
   - Bias examples and suggestions toward **one-utterance combinations**, pushing more complex behaviour into named patterns rather than long chains of raw axis tokens.  
   - When updating Help Hub and quick-help, ensure there are **voice-accessible entry points** for the three families (for example, `model help who`, `model help why`, `model help how`).  
   - Treat persona and intent as **persistent session stance** where helpful, but provide short voice commands to inspect and reset them (for example, `persona status`, `intent status`, `persona reset`, `intent reset`), with recaps that clearly call out non-default Who/Why.  
   - Keep contract axes primarily **per-invocation**, and when any contract values do persist, recap them alongside persona/intent so users can understand the full current stance by voice alone.  
   - In the patterns GUI and suggestions modal, apply persona/intent presets **one-shot by default** (for that invocation only); only change persistent persona/intent when the user issues an explicit “make this default” style command, and make such changes visible in recaps.  

This ADR is intentionally **meta-level**: it does not change how prompts are parsed or how axes are stored. Instead, it standardises the *conceptual frame, teaching surfaces, and voice ergonomics* so that the existing design work in ADRs 005/012/015/018/026/032/033 becomes easier to use, extend, and explain.
