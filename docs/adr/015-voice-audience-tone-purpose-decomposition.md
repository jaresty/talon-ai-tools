# 015 – Voice, Audience, Tone, Intent Axis Decomposition

- Status: Accepted  
- Date: 2025-12-04  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style + goal/directional modifiers + voice/audience/tone/intent)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation for Axis-Based Grammar  
  - 012 – Style and Method Prompt Refactor  
  - 013 – Static Prompt Axis Refinement and Streamlining  
  - 014 – Static Prompt Axis Simplification from Clusters  

## Context

ADR 005/007/012/013/014 together did a lot of work to:

- Make **completeness**, **scope**, **method**, and **style** explicit axes.  
- Reserve **static prompts** mostly for semantic/domain lenses and a few structured tasks.  
- Move “how to think” and “in what shape” into axes and patterns.

The `modelVoice`, `modelAudience`, `modelTone`, and `modelIntent` lists were developed earlier and have grown organically. Today they carry a mix of:

- True **speaker identity** (`as programmer`, `as Kent Beck`, `as CEO`).  
- True **audience identity** (`to managers`, `to team`, `to junior engineer`).  
- **Method-shaped stances** that overlap with method/directional axes (`as XP enthusiast`, `as adversary`, `as various`, `as perspectives`, `as systems thinker`, `to receptive`, `to resistant`, `to various`, `to perspectives`, `to systems thinker`).  
- **Completeness/shape constraints** that fit better into existing axes (`briefly`, parts of `to dummy`, `to receptive/resistant`).  
- **Format/destination contracts** that duplicate style/destination (`for slack`, `for table`, `for presenterm`, `for code tour`).  
- **Thinking frames** that are closer to method/goal than pure intent (`for coding`, `for debugging`, `for prompting`).

This leads to similar problems ADR 014 addressed for static prompts:

- Behaviour is duplicated across **voice/audience/tone/intent** and **axes**.  
- Some items read more like **temporary hats or stances** than stable voices/audiences.  
- Lists are harder to reason about because “what”, “who”, “how”, and “shape” are mixed.

This ADR applies the same clustering and decomposition approach used in 014 to:

- Clarify what each of `voice`, `audience`, `tone`, and `intent` is for.  
- Identify items that are actually **completeness/scope/method/style/goal**.  
- Recommend retiring or demoting those items, expressing their behaviour via axes and/or recipes instead.

## Decision

We will:

1. **Tighten the semantics** of `modelVoice`, `modelAudience`, `modelTone`, and `modelIntent`.  
2. **Cluster existing list items** by their dominant behaviour (identity vs method vs style vs completeness vs goal).  
3. **Retire axis-shaped and style-shaped items** from these lists, representing them instead via:
   - Existing **completeness/scope/method/style** modifiers,  
   - `goalModifier` / `directionalModifier`, and/or  
   - Named **recipes/patterns**.  
4. **Keep voices and audiences focused on “who”**, not on how they think in the moment:
   - Voices: “who is speaking?”  
   - Audiences: “who is being addressed?”  
5. **Keep tones focused on affect/relational stance** (kind vs direct, casual vs formal), not on verbosity or format.  
6. **Keep purposes focused on conversational intent** (inform, persuade, debug, plan, etc.), not on output medium or strict formatting contracts.

### 1. Refined semantics

**Voice (`GPT/lists/modelVoice.talon-list`)**

- Represents a **speaker identity** or stable role:  
  “If this message had a From: line, who is it from?”  
- May imply:  
  - Domain knowledge,  
  - Perspective and priorities,  
  - Level/seniority.  
- Must **not** primarily encode:  
  - A thinking **method** (for example, “systems thinking”, “adversarial reviewing”),  
  - A temporary “hat” or stance (“various perspectives”),  
  - Output **style** (“diagram”, “table”), or  
  - Multi-speaker composites.

**Audience (`GPT/lists/modelAudience.talon-list`)**

- Represents **who the message is for**: role, group, or specific person.  
- May imply:  
  - What context they already know,  
  - What they care about,  
  - What jargon is appropriate.  
- Must **not** primarily encode:  
  - Cognitive state (“receptive”, “resistant”),  
  - Complexity level via insults (“dummy”),  
  - Multi-perspective decomposition (“various stakeholders”, “perspectives”),  
  - Thinking style of the audience (“systems thinker”).

**Tone (`GPT/lists/modelTone.talon-list`)**

- Represents the **emotional and relational register**:  
  - Casual vs formal,  
  - Gentle vs direct,  
  - Kind vs neutral.  
- Must **not** primarily encode:  
  - Answer length or coverage (completeness),  
  - Output format (style).

**Intent (`GPT/lists/modelIntent.talon-list`)**

- Represents **why** the user is invoking the model in this interaction:  
  - Inform, entertain, persuade,  
  - Brainstorm/diverge, converge/decide,  
  - Plan, debug, coach, evaluate, appreciate, etc.  
- May include:  
  - Some high-level framing of the interaction (teaching, collaborating, walkthrough).  
- Must **not** primarily encode:  
  - Output medium/format (Slack, table, presenterm deck, code tour),  
  - Strict output contracts that belong in **style**,  
  - Fine-grained reasoning methods already covered by `methodModifier` / `directionalModifier`.

### 2. Clustered behaviours and re-homing

Below, “keep” means remain in the list under the new semantics; “retire” means remove from the list and express behaviour elsewhere.

#### 2.1 Voice clusters

**Voices to keep (speaker identities/roles) – aggressively trimmed core**

To keep the surface small and distinct, we retain only a **core set** of high-signal roles that represent clearly different “who is speaking?” stances:

- Technical / creative roles:  
  - `as programmer`, `as prompt engineer`, `as scientist`,  
  - `as writer`, `as designer`.  
- Educational / guidance roles:  
  - `as teacher`.  
- Communication / management roles:  
  - `as facilitator`, `as PM`.  
- Seniority / exemplar:  
  - `as junior engineer`, `as principal engineer`,  
  - `as Kent Beck`.

These voices primarily set perspective, seniority, and domain—not method or style—and form the recommended default set for this repo.

**Voices to retire or demote (method/stance-shaped or low-yield)**

In addition to the method-shaped items already discussed, we recommend **retiring** the following from `modelVoice` for this repository:

- Method/stance-shaped (better as methods or purposes):  
  - `as logician` → use `method=rigor` / `method=compare`.  
  - `as negotiator`, `as mediator` → use `intent=for persuasion` / `for mapping` plus `method=adversarial` or `method=systems` where needed.  
  - `as reader`, `as editor` → use `intent=for evaluating` / `for coaching`.  
- Style- or medium-shaped:  
  - `as artist` → use `style=abstractvisual` / `style=diagram` plus appropriate purposes.  
- Org-structural roles where audience is usually the better fit:  
  - `as CEO`, `as CTO`, `as CFO`,  
  - `as platform team`, `as stream aligned team`, `as enabling team`, `as complicated subsystem team`.  
    - Prefer expressing these as **audiences** (“to CEO”, “to platform team”) rather than as speaker voices.

Contributors who need additional voices beyond this core set can still add them in local/custom lists, but the shared repo surface stays small and sharp.

**Voices to retire or demote (method/stance-shaped)**

- `as XP enthusiast`  
  - Behaviour: strong **method**/practice stance:  
    - Validate assumptions early with working software in production,  
    - Prefer small batches and social programming,  
    - Balanced generalist teams, etc.  
  - Decision:  
    - **Retire as a voice**.  
    - Represent core behaviour via:  
      - Method axis: `experimental`, `steps`, possibly an `xp`-flavoured method token or recipe if needed.  
      - Scope: `actions` / `system` where relevant.  
      - Intent: `for project management`, `for coding`, `for debugging` as appropriate.  
    - Provide a **pattern** such as “XP-flavoured recommendations” rather than a voice.

- `as adversary`  
  - Behaviour: adversarial review, finding weaknesses and flaws → **evaluation method**, not a person.  
  - Decision:  
    - **Retire from voice**.  
    - Represent as:  
      - Intent: `for evaluating`,  
      - Tone: `directly` (optionally combined with `kindly`),  
      - Potential method token or pattern for adversarial testing if needed.

- `as blender`  
  - Behaviour: text transformer → output shape and method.  
  - Decision:  
    - **Retire from voice**.  
    - Express as:  
      - Style: `plain` or `code` with explicit transform instructions,  
      - Method: existing transformation-oriented methods or static prompt recipes.

- `as liberator`  
  - Behaviour: facilitation via **Liberating Structures** → facilitation method.  
  - Decision:  
    - Keep `as facilitator` as the **voice**.  
    - **Retire `as liberator`** from voice, and represent LS-heavy techniques as:  
      - Method: new `liberating` method token (see below), and/or  
      - Intent: `for project management`, `for discovery`, `for framing`, `for sensemaking`.

- `as various`, `as perspectives`  
  - Behaviour: multi-perspective/multi-stakeholder synthesis → **method + completeness**.  
  - Decision:  
    - **Retire both from voice**.  
    - Represent via:  
      - Method axis: clustering/compare combinations,  
      - Scope/shape: relations-focused, multi-angle patterns (see ADR 016 for directional lens decomposition),  
      - Recipes like “multi-stakeholder view” that use scope/method tokens.

- `as systems thinker`  
  - Behaviour: systems thinking: loops, reinforcing/balancing, delays → already covered.  
  - Decision:  
    - **Retire from voice**.  
    - Use:  
      - Method: `systems`,  
      - Scope: `system`, `relations`, `dynamics` (per ADR 014),  
      - Intent: `for mapping`, `for discovery`, `for sensemaking` where needed.

- `as other`  
  - Behaviour: “someone who does not know the author” → mainly audience context and information gap.  
  - Decision:  
    - **Retire from voice**.  
    - Represent via:  
      - Audience: generic roles (`to reader`, `to stakeholders`, `to managers`),  
      - Completeness: `gist`/`framework` depending on how much context to include,  
      - Style: `plain`.

#### 2.2 Audience clusters

**Audiences to keep (who it’s for) – aggressively trimmed core**

We keep a focused set of audiences that show up frequently in practice and have clearly distinct concerns:

- Core work roles and groups:  
  - `to managers`, `to team`, `to stakeholders`,  
  - `to product manager`, `to designer`, `to analyst`,  
  - `to programmer`, `to LLM`.  
- Seniority / exemplar:  
  - `to junior engineer`, `to principal engineer`, `to Kent Beck`.  
- Org leadership and platform-ish teams:  
  - `to CEO`,  
  - `to platform team`, `to stream aligned team`.

**Ambiguous but acceptable audience**

- `to XP enthusiast`  
  - Behaviour: describes a persona with strong practice preferences.  
  - Decision:  
    - Keep as an **audience persona**, but:  
      - Trim the description to focus on *what they care about* (early feedback, production validation, pairing), not *how to structure the whole response* (that lives in method/scope).  
      - Encourage axis-based recipes for strong XP-flavoured behaviour, rather than overloading the audience description.

**Audiences to retire/demote (state/style-shaped)**

- `to receptive`, `to resistant`  
  - Behaviour: rhetorical strategy for ordering:  
    - Receptive: lead with main point, then details.  
    - Resistant: lead with background/evidence, end with main point.  
  - Decision:  
    - **Retire from audience**.  
    - Represent via:  
      - Method: new `receptive` and `resistant` method tokens (see below) that encode rhetorical ordering and framing.  
      - Completeness: pair `receptive` with `gist`/`tight` when appropriate and `resistant` with `deep` where more supporting detail is needed.

- `to dummy`  
  - Behaviour: extremely simple, minimal response; implies low completeness and simplified vocabulary.  
  - Decision:  
    - **Retire from audience** (and avoid derogatory naming).  
    - Represent via:  
      - Completeness: `minimal` / `gist`,  
      - Style: `plain`,  
      - Method: new `novice` method token (see below) to emphasise beginner-friendly explanation and rebuilding from first principles,  
      - Possibly a friendlier pattern (for example, “explain like I’m new”).

- `to various`, `to perspectives`  
  - Behaviour: multi-audience/multi-perspective breakdown, similar to `as various` / `as perspectives`.  
  - Decision:  
    - **Retire from audience**.  
    - Represent via:  
      - Method: `cluster` / `compare`,  
      - Scope: `relations`,  
      - Pattern recipes like “map stakeholders and concerns”.

- `to systems thinker`  
  - Behaviour: assumes audience is comfortable with loops/dynamics → this is more like **scope/method**.  
  - Decision:  
    - **Retire from audience**.  
    - Represent via:  
      - Scope: `system`, `relations`, `dynamics`,  
      - Method: `systems`, `mapping`, and/or directional lenses (for example, `fog`, `fig`).

We also recommend retiring the following **low-yield or redundant** audiences from the shared list (they can still live in local overlays if desired):

- `to CTO`, `to CFO`, `to enabling team`, `to complicated subsystem team` – keep `to CEO` and `to platform team`/`to stream aligned team` as representative leadership/team shapes; express other nuances via content rather than separate list entries.

#### 2.3 Tone clusters

Current tones:

- `casually`, `neutrally`, `formally`, `directly`, `gently`, `briefly`, `kindly`.

**Tones to keep (affect/relationship)**

- `casually` – relaxed, informal tone; emoji are acceptable but not required.  
- `formally` – professional, formal wording.  
- `directly` – get to the point, low hedging.  
- `gently` – soften / hedge; emphasise care.  
- `kindly` – explicitly warm, appreciative.

**Tone to retire/demote (completeness-shaped)**

- `briefly`  
  - Behaviour: “keep this message as brief as possible” → completeness + style.  
  - Decision:  
    - **Retire from tone**.  
    - Represent via:  
      - Completeness: `minimal` or `gist`,  
      - Style: `tight`.

We also retire `neutrally` from the shared list and treat it as the **default** when no other tone is specified; users can still reach a neutral tone by omitting tone modifiers.

#### 2.4 Intent clusters

Current purposes include:

- Classic communication intents:  
  - `for information`, `for entertainment`, `for persuasion`,  
  - `for brainstorming`, `for deciding`,  
  - `for planning`, `for evaluating`, `for coaching`, `for appreciation`,  
  - `for diverging`, `for converging`, `for comparison`, `for contrast`, `for mapping`,  
  - `for triage`, `for discovery`, `for framing`, `for sensemaking`,  
  - `for announcing`, `for walk through`, `for collaborating`, `for teaching`,  
  - `for project management`.  
- Format/destination:  
  - `for slack`, `for table`, `for presenterm`, `for code tour`.  
- Method/contract heavy:  
  - `for coding`, `for debugging`, `for prompting`.

**Intents to keep (interaction-level intent)**

These are appropriate high-level “why” values:

- Inform / entertain / persuade:  
  - `for information`, `for entertainment`, `for persuasion`.  
- Explore vs converge (at the interaction level):  
  - `for brainstorming`,  
  - `for deciding`.  
- Compare/relate:  
  - `for comparison`.  
- Workflows and guidance:  
  - `for planning`, `for coaching`, `for project management`,  
  - `for triage`, `for evaluating`,  
  - `for appreciation`,  
  - `for announcing`, `for walk through`, `for collaborating`, `for teaching`.

As an aggressive simplification, we **retire** several intent tokens whose semantics are better expressed as methods or directional lenses:

- Diverge / converge: treat `for diverging` and `for converging` as **methods** (see `diverge` / `converge` below), not purposes; keep `for brainstorming` / `for deciding` as the interaction-level “why”.  
- Compare / contrast: represent both through `method=compare`; retire `for contrast` as a separate intent.  
- Mapping / discovery / framing / sensemaking: retire `for discovery`, `for framing`, `for sensemaking`, and `for mapping` as purposes and instead use combinations of:  
  - Directional lenses (`fog`, `fig`, `ong`, `rog`, `bog`, etc.),  
  - Scope (`system`, `relations`, `dynamics`),  
  - Methods (`systemic`, `mapping`, `motifs`, `structure`, `flow`).

**Intents to retire or demote (style/method/destination)**

- `for slack`  
  - Behaviour: Slack-specific formatting.  
  - Decision:  
    - **Retire from intent**.  
    - Use style `slack` (already in `styleModifier`) plus any other axes.

- `for table`  
  - Behaviour: “format result as a table”.  
  - Decision:  
    - **Retire from intent**.  
    - Use style `table`.

- `for presenterm`  
  - Behaviour: Presenterm deck with strict formatting and safety.  
  - Decision:  
    - **Retire from intent**.  
    - Use style `presenterm` (per ADR 012).

- `for code tour`  
  - Behaviour: output strict VS Code CodeTour JSON and nothing else.  
  - Decision:  
    - **Retire from intent**.  
    - Represent via a dedicated **style** (for example, `codetour`) or static prompt/recipe for “Code Tour” with a strict output contract.

- `for coding`  
  - Behaviour: “You are programming code. Return only syntactically valid code and comments. Explanation must be in comments.”  
  - Decision:  
    - **Retire from intent**.  
    - Represent via:  
      - Style: `code` (output only code/markup),  
      - Goal: `solve` from `goalModifier`,  
      - Optional pattern “code-only solution” that emphasises comment-based explanation.

- `for debugging`  
  - Behaviour: blocked on an issue; need path forward → debugging method.  
  - Decision:  
    - **Retire from intent**.  
    - Represent via:  
      - Method axis: `debugging`,  
      - Goal modifier: `solve`,  
      - Optionally a recipe “debugging conversation” that sets expectations (ask questions first, etc.).

- `for prompting`  
  - Behaviour: building up context for subsequent prompts; concise, with examples and counterexamples.  
  - Decision:  
    - Prefer to **demote** this into a pattern (and possibly a semantic static prompt) rather than a intent, to keep `modelIntent` focused on end-user intents.  
    - Represent via:  
      - Completeness: `framework`/`full`,  
      - Style: `plain` or `taxonomy`,  
      - Goal: `just` (descriptive, not problem-solving).

#### 2.5 New axis tokens and canonical replacements

To avoid losing expressive power when retiring voice/audience/intent items, we introduce a small set of **new axis tokens** and explicit **axis recipes** as canonical replacements.

**New method tokens (`GPT/lists/methodModifier.talon-list`)**

- `xp` – “Adopt an Extreme Programming stance: favour very small, incremental changes; working software in production as the main feedback channel; pairing/mobbing and shared ownership; tests as executable design; and tight feedback loops over big-bang plans.”  
  - Canonical replacement for `as XP enthusiast` (voice):  
    - Use `as programmer` (or another appropriate role) plus `method=xp`, typically with `scope=actions` and/or `scope=system`.  
  - Canonical reinforcement for `to XP enthusiast` (audience):  
    - Keep `to XP enthusiast` as an audience persona, and pair it with `method=xp` when you want the response itself to embody XP practices (not just talk to someone who likes XP).

- `adversarial` – “Think like a constructive adversary: systematically search for weaknesses, edge cases, counterexamples, failure modes, and unstated assumptions; prioritise critique and stress-testing over agreement, while still aiming to improve the work.”  
  - Canonical replacement for `as adversary` (voice):  
    - Use any suitable voice (for example, `as programmer`, `as editor`) plus `method=adversarial` and `intent=for evaluating`.

- `headline` – “Use a headline-first structure: state the main point or recommendation up front, then layer in supporting details, evidence, and caveats in a simple, easy-to-skim order.”  
  - Canonical replacement for `to receptive` (audience):  
    - Use any audience (for example, `to managers`) plus `method=headline`, optionally combined with `completeness=gist` and `style=tight`.

- `case` – “Build the case before the conclusion: lay out background, evidence, trade-offs, and alternatives first, then converge on a clear recommendation that shows how objections and constraints are addressed.”  
  - Canonical replacement for `to resistant` (audience):  
    - Use any audience (for example, `to stakeholders`) plus `method=case`, typically combined with `completeness=deep`.

- `scaffold` – “Explain with scaffolding: start from first principles, introduce ideas gradually, use concrete examples and analogies, and revisit key points so a beginner can follow and retain the concepts.”  
  - Canonical replacement for `to dummy` (audience):  
    - Use any audience (for example, `to junior engineer`) plus `method=scaffold` with `completeness=gist/minimal` and `style=plain`.

- `liberating` – “Facilitate using Liberating Structures: emphasise distributed participation, short structured interactions, concrete invitations, and visual, stepwise processes; name or evoke specific LS patterns when helpful (for example, 1-2-4-All, TRIZ, 15% Solutions).”  
  - Canonical replacement for `as liberator` (voice):  
    - Use `as facilitator` plus `method=liberating`, combined with purposes such as `for discovery`, `for framing`, or `for sensemaking`.

- `diverge` – “Open up the option space: generate multiple, diverse possibilities or angles without prematurely judging or collapsing to a single answer.”  
  - Canonical replacement for `for diverging` (intent):  
    - Use `intent=for brainstorming` plus `method=diverge` (and, if helpful, a directional lens like `fog`/`fig`).

- `converge` – “Narrow down and make a call: weigh trade-offs, eliminate weaker options, and arrive at a small set of recommendations or a single decision.”  
  - Canonical replacement for `for converging` (intent):  
    - Use `intent=for deciding` plus `method=converge`.

- `mapping` – “Emphasise mapping over exposition: surface elements, relationships, and structure; organise them into a coherent map (textual, tabular, or visual), rather than a linear narrative.”  
  - Canonical replacement for `for mapping` (intent):  
    - Use `method=mapping` plus appropriate scope (`system`, `relations`, `dynamics`) and, if needed, styles like `diagram`, `table`, or `abstractvisual`.

**New style token (`GPT/lists/styleModifier.talon-list`)**

- `codetour` – “Output only a valid VS Code CodeTour `.tour` JSON document (schema-compatible), using steps and fields appropriate to the task; do not include any extra prose or surrounding explanation.”  
  - Canonical replacement for `for code tour` (intent):  
    - Use `style=codetour` plus whatever intent best matches the intention (for example, `for teaching`, `for walk through`).

**Axis recipes for other retired items (no new tokens)**

- `as liberator` (voice) → pattern such as “Liberating Structures facilitation”:  
  - Use `as facilitator` plus:  
    - `intent=for discovery` / `for framing` / `for sensemaking` as appropriate,  
    - `scope=system` or `scope=relations`,  
    - and a recipe that names specific Liberating Structures where useful.

- `as various` / `as perspectives` / `to various` / `to perspectives` → multi-angle patterns:  
  - Use:  
    - `method=cluster` and/or `method=compare`,  
    - `scope=relations`,  
    - with a pattern that explicitly introduces each stakeholder/perspective and why it matters.

- `to dummy` → simple-explanation pattern (without derogatory naming):  
  - Use:  
    - Completeness: `gist` or `minimal`,  
    - Style: `plain`,  
    - Optionally a static prompt or pattern name like “explain simply” or “explain like I’m new”.

## Consequences

**Pros**

- **Cleaner separation of concerns**:  
  - Voice/audience: “who”.  
  - Tone: “emotional register”.  
  - Intent: “why”.  
  - Axes and patterns: “how”, “how much”, “where”, “in what shape”.  
- **Reduced duplication and hidden coupling**:  
  - “XP-flavoured”, “systems-thinking”, “various perspectives”, “briefly”, “Slack-formatted”, “presenterm deck”, “code-only” no longer appear as voices/audiences/purposes when they’re really methods/styles/completeness.  
- **More composable grammar**:  
  - A single behavioural idea (for example adversarial evaluation, multi-angle view, extremely brief answer) lives in one place (method/style/completeness/directional) and can be reused with any voice/audience/intent.  
- **Clearer mental model for users**:  
  - Voice/audience lists become recognisably about people and roles, not hats and stances.

**Cons / Risks**

- **Breaking changes** for users who rely on retired tokens.  
- **Axis bloat risk** if every retired item becomes a new axis token instead of recipes.  
- **Migration complexity** around subtle behaviours (especially `for coding`, `for debugging`, `for prompting`, `to XP enthusiast`).

We mitigate these by:

- Preferring **recipes and patterns** over adding new raw axis tokens.  
- Maintaining a small number of new style/method tokens only where no good existing token/recipe exists (for example, `codetour` style).  
- Documenting clear “before/after” equivalents in the README and in pattern GUIs.

## Implementation Sketch

1. **Update list definitions**

   - `GPT/lists/modelVoice.talon-list`:  
     - Keep the identity-shaped roles/persons.  
     - Remove: `as XP enthusiast`, `as adversary`, `as blender`, `as liberator`, `as various`, `as perspectives`, `as systems thinker`, `as other`.  
   - `GPT/lists/modelAudience.talon-list`:  
     - Keep role/person/group entries and `to XP enthusiast` (with trimmed description).  
     - Remove: `to receptive`, `to resistant`, `to dummy`, `to various`, `to perspectives`, `to systems thinker`.  
   - `GPT/lists/modelTone.talon-list`:  
     - Remove: `briefly`.  
   - `GPT/lists/modelIntent.talon-list`:  
     - Keep interaction-level intents.  
     - Remove or demote: `for slack`, `for table`, `for presenterm`, `for code tour`, `for coding`, `for debugging`, `for prompting` (if fully moved to patterns).

2. **Add or adjust style/method tokens where needed**

   - Confirm we already have:  
     - Style: `slack`, `table`, `presenterm`, `code`.  
     - Method: `debugging`, `systems`, `experimental`.  
   - Add the following tokens and descriptions:  
     - Method: `xp`, `adversarial`, `headline`, `case`, `scaffold`, `liberating`, `diverge`, `converge`, `mapping`.  
     - Style: `codetour` with a strict “output only valid .tour JSON” contract.  
   - Ensure descriptions in `styleModifier.talon-list` and `methodModifier.talon-list` carry the long-form behavioural constraints described above.

3. **Add/adjust recipes in pattern GUIs**

   In `lib/modelPatternGUI.py` / `lib/modelPromptPatternGUI.py`:

   - Add recipes that mirror retired tokens:  
     - “XP-flavoured recommendations” → uses `method=experimental`, `scope=actions`, `system` where appropriate.  
     - “Adversarial review” → `for evaluating` plus method/directional recipe; strong critical tone.  
     - “Multi-stakeholder view” → uses `flop` plus `cluster` and `scope=relations`.  
     - “Explain simply” → `gist` plus `plain` (replacing `to dummy`).  
     - “Debugging help” → `method=debugging`, `goal=solve`.  
     - “Slack-formatted summary”, “Table summary”, “Presenterm deck”, “Code Tour”.

4. **Wire new behaviours into `talonSettings` / prompt composition**

   - Ensure voice/audience/tone/intent are only used for their refined roles when composing the combined prompt string in `lib/talonSettings.py`.  
   - Move any retired-item-specific logic to the relevant axis or pattern layer.

5. **Update documentation**

   - In `GPT/readme.md` (and any quick-help UIs), document:  
     - The refined semantics of `voice`, `audience`, `tone`, `intent`.  
     - The deprecations and their axis/recipe replacements (a small migration table).  
   - Mention that “XP enthusiast”, “systems thinker”, “various stakeholders/perspectives”, “briefly”, and format-heavy purposes are now expressed via axes and recipes.

6. **Extend tests**

   - In tests under `tests/` (for example, extend `test_talon_settings_model_prompt.py` or add new tests):  
     - Assert that the removed tokens no longer appear in lists.  
     - Assert that representative axis/recipe combinations (XP-flavoured, adversarial review, multi-stakeholder mapping, debugging help, Slack/table/presenterm/CodeTour outputs) produce the expected contracts.

## Appendix – Migration cheat sheet (old tokens → axis/recipes)

This appendix summarises concrete replacements for the most common retired tokens so existing habits can be carried over with minimal friction. When in doubt, prefer these axis/recipe forms over adding new voice/audience/intent entries.

### Voices → methods / patterns

- `as XP enthusiast`  
  - Use: `as programmer` + `method=xp` (+ `scope=actions` / `scope=system` as needed).  
  - Example: `model describe xp ong`.

- `as adversary`  
  - Use: any suitable voice (for example, `as programmer`, `as editor`) + `method=adversarial` + `for evaluating`.  
  - Example: `model describe adversarial rog for evaluating`.

- `as liberator`  
  - Use: `as facilitator` + `method=liberating` (+ `for discovery` / `for framing` / `for sensemaking` as appropriate).  
  - Pattern: “Liberating facilitation” in the model pattern GUI.

- `as various` / `as perspectives`  
  - Use: a normal voice + directional `flop` (separate angles) + `method=cluster`/`compare` + `scope=relations`.  
  - Example: `model describe cluster flop` (often with `relations` scope).

- `as systems thinker`  
  - Use: a normal voice + `method=systemic` and `scope=system` / `relations` / `dynamics` (optionally `method=mapping`).  
  - Example: `model describe systemic mapping fog`.

### Audiences → methods / scopes

- `to receptive`  
  - Use: normal audience (for example, `to managers`) + `method=headline`.  
  - Example: `model describe headline fog to managers`.

- `to resistant`  
  - Use: normal audience (for example, `to stakeholders`) + `method=case`.  
  - Example: `model describe case rog to stakeholders`.

- `to dummy`  
  - Use: friendlier form + `method=scaffold` + `gist`/`minimal` + `plain`.  
  - Example: `model describe gist scaffold plain fog to junior engineer`.

- `to various` / `to perspectives`  
  - Use: normal primary audience + `flop` + `method=cluster`/`compare` + `scope=relations`.  
  - Example: `model describe diverge cluster flop to stakeholders`.

- `to systems thinker`  
  - Use: normal audience (for example, `to architect`) + `method=systemic` / `mapping` + `scope=system` / `relations` / `dynamics`.  
  - Example: `model describe systemic mapping fog to programmer`.

### Tone → completeness/style

- `briefly`  
  - Use: `completeness=minimal` or `gist` + `style=tight`.  
  - Example: `model describe gist tight fog`.

### Intents → methods / styles / goals

- `for coding`  
  - Use: `goal=solve` + `style=code` (and/or relevant static prompt such as `fix` / `describe`).  
  - Example: `model fix skim code rog` with `goal=solve`.

- `for debugging`  
  - Use: `goal=solve` + `method=debugging`.  
  - Example: `model describe debugging rog for deciding`.

- `for slack` / `for table` / `for presenterm` / `for code tour`  
  - Use styles: `slack`, `table`, `presenterm`, `codetour`.  
  - Examples:  
    - `model describe slack fog`.  
    - `model describe table rog`.  
    - `model describe presenterm rog`.  
    - `model describe mapping codetour rog`.

- `for diverging` / `for converging`  
  - Use: `for brainstorming` + `method=diverge`; `for deciding` + `method=converge`.  
  - Examples:  
    - `model describe diverge fog for brainstorming`.  
    - `model describe converge rog for deciding`.

- `for mapping`  
  - Use: `method=mapping` + `scope=relations` / `system` / `dynamics` (+ diagram/table styles as needed).  
  - Example: `model describe mapping diagram fog`.

- `for discovery` / `for framing` / `for sensemaking`  
  - Use: combinations of directional lenses, scopes, and methods rather than a separate intent:  
    - Discovery: `fog`/`fig` + `diverge` + `mapping` / `motifs`.  
    - Framing: `rog` + `structure` / `mapping`.  
    - Sensemaking: `fog`/`rog` + `systemic` / `mapping` / `motifs`.  
  - Example: `model describe systemic mapping fog for brainstorming`.

## Current status (this repo)

- Lists and axes:  
  - `GPT/lists/modelVoice.talon-list`, `modelAudience.talon-list`, `modelTone.talon-list`, and `modelIntent.talon-list` are trimmed to the core sets defined in this ADR.  
  - New method/style tokens (`xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`, `codetour`) are present in `methodModifier`/`styleModifier` and wired through `modelPatternGUI` and `modelHelpGUI`.

- Patterns and UX:  
  - `lib/modelPatternGUI.py` exposes patterns for key new methods (for example, “XP next steps”, “Explain for beginner”, “Liberating facilitation”, “Diverge options”, “Converge decision”, “Mapping scan”).  
  - `lib/modelHelpGUI.py` and `GPT/readme.md` surface the expanded method/style vocab, example recipes, and a quick “legacy tokens → new grammar” mapping.

- Tests and guardrails:  
  - `tests/test_readme_axis_lists.py` enforces alignment between method/style lists and the README axis lines.  
  - `tests/test_model_pattern_gui.py` asserts that representative patterns use the expected method/scope/style combinations, including the new methods from this ADR.  
  - `tests/test_voice_audience_tone_purpose_lists.py` locks in the trimmed voice/audience/tone/intent sets and ensures deprecated tokens remain removed.

Taken together, these changes mean ADR 015 is fully implemented and guarded in this repo; remaining work, if any, should be limited to small pattern or documentation refinements rather than structural changes.
