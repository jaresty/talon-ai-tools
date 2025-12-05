# 016 – Directional Axis Decomposition and Simplification

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style + goal/directional modifiers + voice/audience/tone/purpose)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation for Axis-Based Grammar  
  - 012 – Style and Method Prompt Refactor  
  - 013 – Static Prompt Axis Refinement and Streamlining  
  - 014 – Static Prompt Axis Simplification from Clusters  
  - 015 – Voice, Audience, Tone, Purpose Axis Decomposition  

## Context

ADR 005/007/012/013/014 establish a grammar where:

- **Static prompts** carry the semantic/task lens.  
- **Axes** – `completeness`, `scope`, `method`, `style`, and the **directional lens axis** (`directionalModifier`) – shape *how* work is done.  
- **Goal modifiers** describe broad intent (for example, `todo`, `product`, `risky`).  

At the time of this ADR, the `directionalModifier` list (`GPT/lists/directionalModifier.talon-list`) consisted of:

- `fog`, `fly ong`, `fly rog`, `fly bog`, `fig`, `fip ong`, `fip rog`, `fip bog`  
- `ong`, `rog`, `bog`  
- `dig`, `dip ong`, `dip rog`, `dip bog`  
- `flip`, `flop`, `tap`, `jog`

Directional modifiers are already treated as an axis: they are appended alongside the other axes and recorded as `GPTState.last_directional`. However, several of these tokens have grown to encode:

- Implicit **completeness** defaults (how exhaustive or deep).  
- Implicit **scope** defaults (system vs actions vs relations).  
- Implicit **method** defaults (systems thinking, mapping, adversarial review, diverging vs converging).  
- Mild **style** preferences (cards vs taxonomy vs bullets).  

This is very similar to the “static prompts carrying axis semantics” problem ADR 014 addressed. It has three main consequences:

- Directional tokens are harder to teach and remember: they bundle several concepts at once.  
- Some directionals are almost pure **recipes** rather than distinct, reusable lenses.  
- It is harder to build ad‑hoc prompts out of the grammar, because some behaviours are only accessible via opaque directional bundles.

We would like to:

- Make the **directional axis** conceptually simple and teachable.  
- Move axis‑shaped semantics into `completeness`/`scope`/`method`/`style` where possible.  
- Preserve at least one **“jog‑like” neutral confirmation lens** for non‑directional “okay, go” utterances.

## Directional behaviour decomposition

This section summarises how each directional token maps onto the existing axes plus any residual “purely directional” meaning.

### `fog` / `fig` / `dig`

- `fog` – abstracting/generalising lens.  
  - Completeness: tends toward `gist` (or `full` for deep but non‑exhaustive synthesis).  
  - Scope: `system` or `relations`.  
  - Method: `contextualise`, `systemic`, or `mapping`.  
  - Style: typically `plain` / `bullets`.  
  - Residual directional meaning: “look upwards / synthesise; one fused, higher‑level frame.”

- `fig` – abstracting + grounding lens.  
  - Completeness: tends toward `full`.  
  - Scope: both `system` and local `actions` as needed.  
  - Method: `ladder` + `mapping` (explicitly traversing abstraction levels).  
  - Style: `plain`.  
  - Residual: “span across levels in a single coherent pass.”

- `dig` – concretising/grounding lens.  
  - Completeness: tends toward `deep`.  
  - Scope: `actions` or `narrow`.  
  - Method: `diagnose`, `steps`.  
  - Style: `plain`.  
  - Residual: “go downward into concrete details rather than staying at the overview.”

### `ong` / `rog` / `bog`

- `ong` – acting/extending lens.  
  - Completeness: tends toward `path` (or `full` when expanded).  
  - Scope: `actions`.  
  - Method: `steps`, `xp`, sometimes `experimental`.  
  - Style: usually `bullets` / `checklist`.  
  - Residual: “prioritise forward motion and concrete next steps over analysis.”

- `rog` – reflective/structural lens.  
  - Completeness: `framework` or `deep`.  
  - Scope: `system` or `relations`.  
  - Method: `structure`, `wasinawa`, sometimes `systemic`.  
  - Style: `plain` / `bullets`.  
  - Residual: “prioritise sensemaking/structure over immediate action.”

- `bog` – blended act + reflect lens.  
  - Completeness: `full`.  
  - Scope: often `relations`.  
  - Method: `systemic`, `mapping`, sometimes `steps`.  
  - Style: `plain` / `bullets`.  
  - Residual: “hold action and reflection together in one fused stance.”

### Combined forms: `fly` / `fip` / `dip` + `ong` / `rog` / `bog`

Tokens like:

- `fly ong`, `fly rog`, `fly bog`  
- `fip ong`, `fip rog`, `fip bog`  
- `dip ong`, `dip rog`, `dip bog`

combine “vertical” semantics (`fly`/`fip`/`dip`) with the act/reflect blend of `ong`/`rog`/`bog`. In practice they behave like **pre‑baked bundles** of:

- abstraction vs concreteness (already expressible via `system`/`actions`, `ladder`, `mapping`, `framework`, `deep`, etc.), plus  
- act vs reflect vs both (already expressible via `actions` vs `system`/`relations` + `steps`/`xp`/`experimental` vs `structure`/`wasinawa`/`systemic`).

They do not introduce a new axis; they pack more defaults into the directional axis value.

### Shape and interaction tokens: `flip` / `flop` / `tap` / `jog`

- `flip` – invert/skew/surprise (now **retired** as a directional token).  
  - Axes: resembles `method=adversarial` plus possibly `scope=edges`.  
  - Residual: “aim for surprising reframes,” i.e. an adversarial sub‑flavour.

- `flop` – multiple distinct angles, separately presented (now **retired** as a directional token).  
  - Axes: `method=diverge` and/or `compare`, with `style=cards` or `bullets`.  
  - Residual: “do not synthesise; keep perspectives clearly separated.”

- `tap` – 5–7 abstract categories with labels and short phrases, no how‑to (now **retired** as a directional token).  
  - Axes: essentially `completeness=framework`, `scope=system`, `method=mapping`, `style=taxonomy`.  
  - Residual: almost none; this is a recipe.

- `jog` – interpret and act, don’t ask back.  
  - Axes: no strong defaults for completeness/scope/method/style.  
  - Residual: **interaction mode**: “treat this as neutral confirmation / phrase end; apply existing axes and avoid meta‑questions unless necessary.”

## Clusters

From this decomposition, directional semantics cluster into:

1. **Vertical abstraction vs grounding**  
   - Tokens: `fog`, `fig`, `dig`, and the `fly`/`fip`/`dip` prefixes.  
   - Largely expressible via:
     - completeness: `gist` / `full` / `deep` / `framework`,  
     - scope: `system` / `relations` / `actions`,  
     - method: `ladder`, `mapping`, `systemic`.

2. **Act vs reflect stance**  
   - Tokens: `ong`, `rog`, `bog`, plus their `*_ong` / `*_rog` / `*_bog` combined forms.  
   - Mostly expressible via:
     - scope: `actions` vs `system` / `relations`,  
     - method: `steps` / `xp` / `experimental` vs `structure` / `wasinawa` / `systemic`,  
     - completeness: `path` / `framework` / `full`.

3. **Perspective multiplicity vs single lens**  
   - Tokens (historically): `flop` (multi‑angle, separate), `flip` (skewed/adversarial), plus `fog`‑like synthesis.  
   - Expressible via:
     - method: `diverge`, `compare`, `adversarial`, `cluster`,  
     - style: `cards` vs `plain` / `bullets`.
   - There is a useful conceptual contrast between:
     - “single fused lens” vs  
     - “multiple explicit perspectives, shown separately,”
     but this can be expressed via methods and styles rather than as extra directional dimensions.

4. **Interaction / confirmation**  
   - Token: `jog`.  
   - This is best thought of as:
     - “Use whatever static prompt + axes are already present; I’m done specifying; please act without extra clarifying questions.”

## Simplified directional axis

Based on the above, we can simplify the **directional axis** while preserving expressive power via the other axes.

### Core directional lenses

We keep a small set of **archetypal** directional values that are primarily about stance, not recipes:

- `fog` – **upwards/generalising lens**  
  - Guidance (not hard‑coded):  
    - If no other axes are given, prefer `completeness=gist`, `scope=system|relations`, `method=contextualise|mapping`.  
  - Mental model: “synthesise and generalise; one higher‑level frame.”

- `dig` – **downwards/grounding lens**  
  - Guidance:  
    - If no other axes are given, prefer `completeness=deep`, `scope=actions|narrow`, `method=diagnose|steps`.  
  - Mental model: “go down into details and concrete ground.”

- `fig` – **span across abstraction levels**  
  - Guidance:  
    - If no other axes are given, prefer `completeness=full`, `scope=system + some actions`, `method=ladder|mapping`.  
  - Mental model: “move across levels in one coherent pass.”

- `ong` – **act/extend lens**  
  - Guidance:  
    - If no other axes are given, prefer `scope=actions`, `completeness=path`, `method=steps|xp|experimental`.  
  - Mental model: “bias toward concrete next actions and forward motion.”

- `rog` – **reflect/structure lens**  
  - Guidance:  
    - If no other axes are given, prefer `scope=system|relations`, `completeness=framework|deep`, `method=structure|wasinawa`.  
  - Mental model: “bias toward sensemaking and structural clarity.”

- `bog` – **act + reflect blended lens**  
  - Guidance:  
    - If no other axes are given, prefer mixtures like `scope=relations`, `completeness=full`, `method=systemic|mapping` with some `steps`.  
  - Mental model: “hold action and reflection together as a single stance.”

- `jog` – **neutral confirmation lens**  
  - Semantics:  
    - “Treat this as confirmation / phrase end; apply the existing static prompt and axes as‑is; avoid extra meta‑clarification unless needed for safety.”  
    - Does **not** introduce additional completeness/scope/method/style defaults.

These core values are what we should teach as “the directional axis.”

### Composite directional values

Combined tokens (`fly ong`, `fip rog`, `dip bog`, etc.) remain **valid values of the directional axis** for backwards compatibility and brevity, but we treat them as **named composite lenses**:

- Example explanatory recipes:
  - `fly ong` ≈ `describe · gist · system · mapping · steps · ong`  
  - `fip rog` ≈ `describe · full · system · systemic · rog`  
  - `dip bog` ≈ `describe · deep · relations · mapping · steps · bog`

We do **not** introduce new conceptual axes for these; instead:

- Docs and quick‑help can show how each composite value roughly corresponds to a recipe built from:
  - the core directional lenses (`fog`/`fig`/`dig`, `ong`/`rog`/`bog`), plus  
  - completeness/scope/method/style.
- Advanced users can always spell out the explicit axes (`mapping`, `ladder`, `systemic`, `actions`, `relations`, etc.) instead of relying on the composite token.

### Shape‑ and method‑heavy directionals (historical `tap` / `flop` / `flip`)

For `tap` (and historically `flop` and `flip`), we treat their **semantics** as belonging primarily to the other axes:

- `tap`  
  - Expressed as a canonical axis recipe, for example:  
    - `describe · framework · system · mapping · taxonomy · fog`  
  - Directional role: none beyond choosing a base lens (`fog` in the example).  
  - Decision in this ADR:
    - **Remove `tap` from `directionalModifier`** and encourage expressing its behaviour via the taxonomy recipe and patterns (for example, the `Tap map` pattern).

Historically, two additional directional tokens (`flop` and `flip`) encoded shape and method semantics:

- `flop`  
  - Behaviour: “multi‑angle view” – do not synthesise; keep perspectives separate.  
  - Axis expression, for example:  
    - `describe · full · system · diverge · cards · rog`  
  - Decision in this ADR:
    - **Remove `flop` from `directionalModifier`** and encourage expressing its behaviour via `method=diverge|compare` and `style=cards|bullets`, plus patterns.

- `flip`  
  - Behaviour: adversarial/skewed perspective; “flip it” / devil’s advocate.  
  - Axis expression, for example:  
    - `describe · gist · edges · adversarial · fog`  
  - Decision in this ADR:
    - **Remove `flip` from `directionalModifier`** and encourage expressing its behaviour via `method=adversarial` (and `scope=edges` where useful).

In all three cases, the *behaviour* is defined via completeness/scope/method/style and patterns; the directional token primarily serves as a short‑hand.

## Consequences

### Positive

- **Directional semantics are simpler and more orthogonal**:
  - The core directional axis is a small, teachable set of lenses (`fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`).  
  - Vertical abstraction, act/reflect stance, and multi‑angle vs single‑lens behaviours are exposed more explicitly via the main axes.

- **Ad‑hoc prompts become easier to compose**:
  - Users can build recipes from static prompt + completeness/scope/method/style and then optionally add a simple directional lens, rather than needing opaque bundles that mix everything.  
  - Composite directionals can be understood in terms of explicit axis combinations.

- **Teaching and docs become clearer**:
  - Quick‑help can present:  
    - the four main axes,  
    - the directional axis with core lenses, and  
    - a small number of example recipes (including explanations for composite lenses like `fly/fip/dip`, tap-style taxonomy maps, multi-angle stakeholder views, and “flip it” style adversarial reviews).  
  - `jog` has a clearly defined role as the neutral confirmation / “just go” lens.

### Negative / trade‑offs

- Some users currently relying on composite directionals (`fly/fip/dip`) and the now‑removed `tap`/`flop`/`flip` tokens as *the* way to access certain behaviours will need to learn that those behaviours are now modelled via the main axes plus a simpler directional lens.  
- There is some documentation and mental overhead in explaining that composite tokens are “named bundles” on the same axis, not new dimensions.

## Current status in this repo

As of 2025‑12‑05, the following pieces of this ADR are implemented in `talon-ai-tools`:

- `GPT/lists/directionalModifier.talon-list`:
  - Contains the core directional lenses described here: `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`.
  - Retains composite values (`fly`/`fip`/`dip` + `ong`/`rog`/`bog`) as directional tokens.
  - Has removed `tap`, `flop`, and `flip` in favour of axis-based recipes and patterns.
- Quick-help and axis docs:
  - `_build_axis_docs()` in `GPT/gpt.py` lists the directional axis alongside completeness/scope/method/style and points readers at ADR 016.
  - `lib/modelHelpGUI.py`:
    - Uses the shared lists to display directional lenses.
    - Surfaces the core lenses explicitly via a “Core lenses: fog, fig, dig, ong, rog, bog, jog” line, and includes `jog` in its fallback list.
- README axis cheat sheet:
  - `GPT/readme.md` includes a “Directional lenses” subsection under “Common axis recipes (cheat sheet)” that documents the core lenses and their typical axis biases.
- Tests:
  - `tests/test_static_prompt_docs.py`:
    - Asserts that `directionalModifier.talon-list` contains the core lenses from this ADR.
    - Asserts that retired tokens `flip` and `flop` are absent.
  - `tests/test_model_pattern_gui.py`:
    - Asserts that the `Tap map`, `Multi-angle view`, `Flip it review`, and `Systems path` patterns use the axis combinations described in this ADR’s appendix.

Still to do (optional future loops):

- Optionally add composite-lens-focused patterns in prompt pattern GUIs for other `fly`/`fip`/`dip` recipes, and keep accompanying tests and documentation aligned with this ADR. These are incremental improvements; ADR 016 is Accepted without them.
- Optionally extend quick-help examples (`lib/modelHelpGUI.py::_show_examples`) to include one or two directional-focused recipes derived from this ADR.

## Migration notes

This ADR describes a decomposition and simplification strategy. Follow‑up changes should:

- **Update `GPT/lists/directionalModifier.talon-list`** to:
  - Clarify which tokens are core lenses (`fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`).  
  - Remove `tap`, `flop`, and `flip` from the list.  
  - Reword composite tokens (`fly`/`fip`/`dip`) in terms of their implied axis defaults and example recipes, explicitly noting that they do not introduce new axes.

- **Align quick‑help / grammar docs** (for example, `lib/modelHelpGUI.py`, `GPT/readme.md`) to:
  - Present the directional axis alongside completeness/scope/method/style.  
  - Include example recipes showing:
    - how to spell out behaviours like “tap map”, “multi‑angle view”, and “flip it” using axes, and  
    - how composite directional tokens map to those recipes conceptually.

- **Keep `_build_axis_docs` in sync**:
  - Ensure `_build_axis_docs()` (used by quick-help surfaces) continues to:
    - List the directional axis alongside completeness/scope/method/style, and  
    - Point readers at ADR 016 (in addition to ADR 005/012/013) and the README cheat sheet for the current directional lens semantics and examples.

- **Optionally add or adjust patterns** (`lib/modelPatternGUI.py`, prompt‑specific pattern GUIs) to:
  - Provide explicit patterns for “Tap map”, “Multi‑angle view”, “Flip it”, “XP path”, etc., using axes + a simple directional.  
  - Ensure patterns are documented in terms of axis combinations, so users can derive their own ad‑hoc recipes from them.

## Appendix – Example recipes for directional and axis combinations

This appendix gives concrete, non-exhaustive recipes that illustrate how to express behaviours previously tied to directional bundles using the core directional lenses plus completeness/scope/method/style.

### Tap-style taxonomy map

- Goal: 5–7 abstract categories with labels and short phrases; no how-to.  
- Recipe:
  - `describe · framework · system · mapping · taxonomy · fog`  
- Semantics:
  - Completeness: `framework` – cover all major parts of the map.  
  - Scope: `system` – treat the subject as a whole system.  
  - Method: `mapping` – emphasise structure over narrative.  
  - Style: `taxonomy` – named categories and subtypes.  
  - Directional: `fog` – upwards/generalising lens.

### Multi-angle stakeholder view (successor to `flop`)

- Goal: surface several distinct perspectives (for example, stakeholders), presented separately rather than synthesised.  
- Example recipe:
  - `describe · full · relations · diverge · cards · rog`  
- Semantics:
  - Completeness: `full` – cover all major perspectives in scope.  
  - Scope: `relations` – focus on relationships and interactions.  
  - Method: `diverge` (and/or `cluster` / `compare`) – emphasise multiple angles over a single summary.  
  - Style: `cards` – one card per perspective.  
  - Directional: `rog` – reflective/structural lens.

### “Flip it” adversarial review (successor to `flip`)

- Goal: stress-test assumptions and surface weaknesses or counterexamples (“devil’s advocate”).  
- Example recipe:
  - `describe · gist · edges · adversarial · fog`  
- Semantics:
  - Completeness: `gist` – concise but pointed critique.  
  - Scope: `edges` – emphasise edge cases and failure modes.  
  - Method: `adversarial` – constructive adversarial stance.  
  - Style: default (`plain`) unless combined with bullets/table.  
  - Directional: `fog` – synthesise the main lines of critique.

### Composite directional lens example

- Goal: show how a composite directional value can be understood as a bundle over axes + a core lens.  
- Example: `fly ong` can be approximated as:
  - `describe · gist · system · mapping · steps · ong`  
- Semantics:
  - Completeness: `gist` – short but complete pass.  
  - Scope: `system` – whole-system framing.  
  - Method: `mapping` + `steps` – map key elements, then outline how to act.  
  - Directional: `ong` – act/extend lens.

These examples are illustrative rather than prescriptive; they are meant to:

- Show how behaviours once bundled into directional tokens can be expressed through the main axes plus a simple directional lens.  
- Provide seeds for patterns and quick-help examples without freezing every recipe into a fixed contract.

## Migration cheat sheet – directional tokens → axis/recipes

This section summarises how to think about existing or historical directional tokens in terms of axes and recipes, so older habits can be migrated without reintroducing hidden bundle semantics.

- `fog` / `fig` / `dig` – vertical lenses:
  - `fog`: upwards/generalising; bias toward `gist` + `system|relations` + `contextualise|mapping`.  
  - `fig`: span abstraction levels; bias toward `full` + `system`(+some `actions`) + `ladder|mapping`.  
  - `dig`: downwards/grounding; bias toward `deep` + `actions|narrow` + `diagnose|steps`.  
  - Migration: keep using these as directional lenses; when writing examples or patterns, make their axis defaults explicit (for example, `system` scope, `mapping` method).

- `ong` / `rog` / `bog` – act/reflect lenses:
  - `ong`: act/extend; bias toward `path` + `actions` + `steps|xp|experimental`.  
  - `rog`: reflect/structure; bias toward `framework|deep` + `system|relations` + `structure|wasinawa`.  
  - `bog`: blended act+reflect; bias toward `full` + `relations` + `systemic|mapping` (+ some `steps`).  
  - Migration: keep using these as directional lenses; when expanding recipes, spell out the supporting completeness/scope/method axes.

- Composite values (`fly`/`fip`/`dip` + `ong`/`rog`/`bog`):
  - Behaviour: named bundles that sit on the same directional axis as the core lenses.  
  - Migration:
    - Treat them as advanced shorthand values for the directional axis, not new axes.  
    - When documenting or designing patterns, prefer explicit recipes like `describe · gist · system · mapping · steps · ong` rather than relying solely on the composite token name.

- `tap`:
  - Behaviour: taxonomy-style, framework-level map of categories and subtypes (see “Tap-style taxonomy map” recipe).  
  - Migration:
    - Encourage `framework` + `system` + `mapping` + `taxonomy` + `fog` as the explicit recipe, surfaced via patterns (for example, `Tap map`) and docs.
    - Do **not** use `tap` as a directional token; its semantics now live only in axes and patterns.

- Historical `flop` and `flip`:
  - `flop`: multi-angle stakeholder view; successively present several perspectives without synthesising them (see “Multi-angle stakeholder view” example).  
  - `flip`: adversarial “devil’s advocate” review; skew the view toward weaknesses and counterexamples (see “Flip it” adversarial review example).  
  - Migration:
    - Do not reintroduce `flop`/`flip` as directional tokens.  
    - Express their behaviour via:
      - Multi-angle: `scope=relations` + `method=diverge|cluster|compare` + `style=cards|bullets` + an appropriate directional lens (`rog` in the example pattern).  
      - Adversarial: `scope=edges` + `method=adversarial` + a suitable directional lens (`fog` in the example).
