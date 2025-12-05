# 018 – Axis Modifier Decomposition into Pure Elements

- Status: Draft  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style + directional modifiers + voice/audience/tone/purpose + destination)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 012 – Style and Method Prompt Refactor  
  - 014 – Static Prompt Axis Simplification from Clusters  
  - 015 – Voice, Audience, Tone, Purpose Axis Decomposition  
  - 016 – Directional and Axis Decomposition  
  - 017 – Goal Modifier Decomposition and Simplification  

## Context

ADR 005 introduced four contract-style axes – completeness, scope, method, and style – and described them as orthogonal:

- **Completeness** – how much of the chosen territory must be covered.  
- **Scope** – which territory is in-bounds.  
- **Method** – how reasoning proceeds / which tool is used.  
- **Style** – how the answer is presented.

ADR 012 and ADR 014 added and refined specific modifiers on these axes, and ADR 015 split out audience, tone, purpose, and voice as separate dimensions. ADR 016 decomposed the directional lenses.

However, the concrete Talon lists that implement the axes (`GPT/lists/completenessModifier.talon-list`, `scopeModifier.talon-list`, `methodModifier.talon-list`, `styleModifier.talon-list`) now contain many **composite tokens** whose descriptions span multiple axes at once. Examples (as of this ADR’s date):

- `path` (completeness) encodes trajectory, dynamic scope, and narrative structure.  
- `framework` (completeness) encodes a framework-shaped territory and structural method.  
- `samples` (completeness) encodes multiple options, concision, and explicit probabilities (format).  
- `actions`, `edges`, `relations`, `system`, `dynamics` (scope) encode selection rules and reasoning emphases as well as territory.  
- `xp`, `adversarial`, `novice`, `diverge`, `converge`, `mapping`, `analysis`, `contextualise` (method) mix stance, audience, output restrictions, and reasoning style.  
- Many style tokens (`adr`, `bug`, `story`, `spike`, `commit`, `gherkin`, `html`, `shellscript`, `presenterm`, `diagram`, `codetour`, `taxonomy`, etc.) behave as **output genres** with implicit structure and sometimes implicit completeness/method.

This blurs the intended orthogonality:

- Users cannot reliably predict interactions when combining modifiers.  
- Behaviours are encoded as opaque bundles rather than visible axis combinations.  
- Adding new composite tokens increases cross-coupling instead of reusing existing axis elements.

We want to preserve the four contract axes (plus audience, tone, purpose, voice, and destination) but ensure each **axis token is “pure”**: its description lives on a single axis. Complex behaviours should be expressed as **recipes** (combinations across axes or patterns), not as single overloaded adjectives.

This ADR focuses on:

- Tightening the semantics of the four axis Talon lists.  
- Moving stance and audience semantics to the dedicated tone/audience axes.  
- Representing composite behaviours as explicit axis combinations and patterns.

## Decision

### Purity constraints per axis

We adopt strict semantics for each axis list:

- **Completeness modifiers** may only talk about:
  - Coverage density / thoroughness *within* the already-chosen scope.
  - They MUST NOT prescribe:
    - Output format (bullets, tables, probabilities, code, etc.).  
    - Reasoning method (steps, plans, paths, experiments).  
    - Audience stance or tone.

- **Scope modifiers** may only talk about:
  - What conceptual territory is in-bounds vs out-of-bounds.  
  - They MAY express this as filters (“only X”, “exclude Y”), but:
    - They MUST NOT dictate how to reason about that territory.  
    - They MUST NOT demand particular list lengths, depths, or narrative structures.

- **Method modifiers** may only talk about:
  - Internal reasoning patterns, workflows, or decomposition strategies (steps, plan-then-execute, cluster, diagnose, etc.).  
  - They MUST NOT:
    - Fix the external format (for example, “answer as a table”).  
    - Encode audience stance (“hostile”, “novice”).  
    - Implicitly cap or demand coverage beyond what the method logically requires.

- **Style modifiers** may only talk about:
  - The visible presentation: layout, container, and surface form (narrative vs bullets, table vs checklist, code-only, document genre like ADR/bug/story).  
  - They MUST NOT:
    - Dictate how much content to include (beyond what the container logically enforces).  
    - Change the reasoning algorithm or scope of what is considered.

Composite behaviours SHOULD be expressed as:

- **Axis recipes**: explicit combinations like `deep + flow + dynamics + checklist`.  
- Or **static prompts / patterns** that internally set axis values, instead of introducing new composite axis tokens.

### Reclassification and decomposition of existing tokens (high level)

We will refactor the current lists so that each remaining token is pure, and composite behaviours are represented by combinations or patterns. Detailed token-by-token changes live in the ADR 018 work-log.

#### Completeness list (`GPT/lists/completenessModifier.talon-list`)

We keep the core coverage tokens as pure completeness (possibly with minor wording tweaks):

- `skim`, `gist`, `full`, `max`, `minimal`, `deep`.

These describe “how much of the room you clean” given a fence, without specifying format or method.

We decompose composite entries:

- `framework`  
  - **Issue**: encodes a framework-shaped scope and structural method, not just coverage density.  
  - **Decision**:
    - Retire `framework` from `completenessModifier.talon-list` as a first-class axis value.  
    - Represent “framework-style” behaviour via combinations such as:
      - `completeness: full` (or `deep`, depending on the profile).  
      - `method: structure` or `mapping`.  
      - `scope: system` or a framework-specific static prompt.  
    - Provide `framework`-shaped behaviours via **static prompts or patterns** (for example, Wardley, COM‑B) that set these axis values.

- `path`  
  - **Issue**: mixes trajectory, dynamic scope, and narrative structure with completeness.  
  - **Decision**:
    - Retire `path` from `completenessModifier.talon-list` as a first-class axis value.  
    - Represent “path-like” behaviour with combinations such as:
      - `method: flow` (sequential, path-oriented reasoning).  
      - `scope: dynamics` (time / transitions) or `system`, as appropriate.  
      - `completeness: deep` (or `full`) within that dynamic scope.  
    - Preserve recipes like “Systems path” as **patterns** that pin `flow + dynamics + deep` (and any lenses) explicitly rather than via a single completeness token.

- `samples`  
  - **Issue**: bundles multi-option coverage, concision, and explicit probabilities (format) into completeness.  
  - **Decision**:
    - Remove `samples` from `completenessModifier.talon-list`.  
    - Introduce / reuse a **method** token (for example, `samples`) that encodes:
      - “Generate multiple distinct options and calibrate approximate probabilities; avoid near-duplicates.”  
    - Optionally add or reuse a **style** token (for example, `bullets` or a dedicated `options`-like style) for formatting.  
    - Where needed, pair this sampling method with ordinary completeness values (`gist`, `full`) in static prompt profiles or patterns.

#### Scope list (`GPT/lists/scopeModifier.talon-list`)

We keep `narrow`, `focus`, and `bound` as pure territory controls.

We retain the remaining scope tokens but tighten their wording so they stay on the scope axis:

- `edges`, `relations`, `dynamics`, `interfaces`, `system`, `actions`.

For each, we will:

- Define **what is in the fence** (for example, “only interactions between components”, “only aspects that change over time”, “only concrete actions/tasks”).  
- Avoid verbs that imply method or style (for example, “emphasise”, “explain”, “summarise”).  

Example rephrasing direction (exact text to be captured in a work-log and the list file):

- `actions`: “Within the selected target, treat concrete user/team actions or tasks as the only in-scope elements; other content is out of scope.” (No checklist or narrative wording.)

This preserves the useful scoped lenses while keeping scope values focused on inclusion/exclusion rather than reasoning or format.

#### Method list (`GPT/lists/methodModifier.talon-list`)

We keep the core reasoning-pattern tokens as method-only:

- `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`, `systemic`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `mapping`, `ladder`, `analysis`, `contextualise`, `diverge`, `converge`, `wasinawa`, `xp`, `liberating` (with definitions tightened where needed).

We move stance and audience modifiers into the appropriate axes:

- `adversarial`, `receptive`, `resistant`, `novice`:
  - **Issue**: these describe stance and assumed audience, not a reasoning algorithm.  
  - **Decision**:
    - Remove them from `methodModifier.talon-list`.  
    - Add corresponding items to:
      - `GPT/lists/modelTone.talon-list`: `adversarial`, `receptive`, `resistant`.  
      - `GPT/lists/modelAudience.talon-list`: `novice`.  
    - Ensure their definitions talk about attitude, framing, and assumed knowledge, not step patterns.

We tighten composite method tokens so they describe only reasoning patterns:

- `xp`, `liberating`, `diverge`, `converge`, `mapping`, `analysis`, `contextualise`, `systemic`, `wasinawa`:
  - Update definitions to:
    - Focus on how to structure thinking (phases, loops, decomposition, mapping vs exposition).  
    - Avoid explicit coverage promises (“several options”), explicit audience stance, or format constraints.

#### Style list (`GPT/lists/styleModifier.talon-list`)

We keep all existing style tokens on a single axis, but recognise two conceptual sub-groups:

1. **Layout / surface style** (pure formatting):
   - `plain`, `tight`, `bullets`, `table`, `code`, `cards`, `checklist`.  
   - These describe layout, brevity pressure, and immediate container, without changing reasoning or territory.

2. **Genre / container style** (document shapes and channels):
   - `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy`, `codetour`, `story`, `bug`, `spike`.  
   - These are acknowledged as **output genres** that strongly shape the container, but still live on the style axis.

For the genre-style tokens, we will:

- Keep their specific format / schema requirements (for example, ADR sections, bug report sections, Gherkin syntax, presenterm rules).  
- Ensure their descriptions avoid embedding completeness or method guarantees (“short”, “exhaustive”, “deep dive”); those should be specified via completeness and method when needed.

We do **not** introduce a separate “genre axis” in this ADR. Instead we clarify in documentation that:

- Many style tokens are “heavy containers” that strongly constrain output.  
- Completeness, scope, and method must still be set explicitly (or via profiles) if callers care about those aspects.

### Representation of composite behaviours

For behaviours previously covered by composite tokens, we will:

- Express them as **axis recipes** in `STATIC_PROMPT_CONFIG` or pattern definitions.  
- Document those recipes in GUIs and quick-help as canonical examples of composing axes.

Examples:

- “Framework review”:
  - `scope: system`, `method: mapping`, `completeness: full`, `style: bullets` (or `table`).  
- “Path from here to there”:
  - `scope: dynamics`, `method: flow`, `completeness: deep`, `style: plain`.  
- “Sampling with probabilities”:
  - `method: samples`, `completeness: gist`, `style: bullets` (or a dedicated options style).

## Salient Tasks

- **Axis list refactors**
  - Make `GPT/lists/completenessModifier.talon-list` pure by retiring `framework`, `path`, and `samples` as completeness values and, where needed, introducing or reusing method/style tokens to capture their structural/format semantics.  
  - Tighten wording in `GPT/lists/scopeModifier.talon-list` so each entry describes only conceptual territory (including filters like “only actions” or “only relations”) without prescribing method or style.  
  - Move stance/audience tokens out of `GPT/lists/methodModifier.talon-list` into `GPT/lists/modelTone.talon-list` and `GPT/lists/modelAudience.talon-list`, and tighten remaining method definitions so they describe reasoning patterns only.  
  - Review `GPT/lists/styleModifier.talon-list` to ensure style entries (including heavy genres like `adr`, `bug`, `story`, `presenterm`, `codetour`) do not embed completeness or method promises beyond what their containers inherently require.

- **Static prompt and pattern recipes**
  - In `lib/staticPromptConfig.py`, express behaviours previously tied to composite axis tokens (`framework`, `path`, `samples`, and any others identified in the work-log) as explicit axis combinations and/or static prompt profiles.  
  - In pattern GUIs, add or refine recipes that surface these combinations as named behaviours (for example, “Framework review”, “Systems path”, “Sampling with probabilities”) without reintroducing composite axis tokens.

- **Guardrails, tests, and docs**
  - Extend axis mapping and static prompt tests (for example, `tests/test_axis_mapping.py`, `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`) to assert that:
    - Each axis token lives on a single conceptual axis.  
    - Behaviours formerly implemented by composite tokens are now produced by explicit axis combinations or patterns.  
  - Update `GPT/readme.md`, quick-help, and any GUI help text to:
    - Reflect the refined axis vocabularies.  
    - Show axis-composition examples in place of the removed composite modifiers.

## Current Status (this repo)

As of this ADR’s date:

- **Completeness axis** (`GPT/lists/completenessModifier.talon-list`):
  - Pure coverage tokens: `skim`, `gist`, `full`, `max`, `minimal`, `deep`.  
  - Composite tokens that mix coverage with structure or format: `framework`, `path`, `samples`.

- **Scope axis** (`GPT/lists/scopeModifier.talon-list`):
  - Pure territory tokens: `narrow`, `focus`, `bound`.  
  - Tokens that encode both territory and a reasoning/filtering lens: `edges`, `relations`, `dynamics`, `interfaces`, `system`, `actions`.

- **Method axis** (`GPT/lists/methodModifier.talon-list`):
  - Reasoning-pattern tokens: `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`, `systemic`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`, `ladder`, `contextualise`, `xp`, `liberating`, `diverge`, `converge`, `mapping`, `analysis`.  
  - Tokens that primarily express stance or audience rather than method: `adversarial`, `receptive`, `resistant`, `novice`.

- **Style axis** (`GPT/lists/styleModifier.talon-list`):
  - Layout/surface tokens: `plain`, `tight`, `bullets`, `table`, `code`, `cards`, `checklist`.  
  - Heavy genre/container tokens that impose strong format contracts: `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy`, `codetour`, `story`, `bug`, `spike`.

These observations drive the concrete list changes and recipes in the Implementation Plan.

## Consequences

### Benefits

- **Stronger orthogonality**:
  - Each axis token now clearly lives on a single axis.  
  - Complex behaviours are visible compositions (`deep + flow + dynamics`) instead of opaque single words.

- **Clearer semantics for stance and audience**:
  - Stance (`adversarial`, `receptive`, `resistant`) and audience level (`novice`) are expressed on the dedicated tone/audience axes, not hidden inside method.

- **Predictable composition**:
  - Users can better predict how `tight + samples + actions + adr` will behave, because each contributes along one dimension.

- **Easier evolution**:
  - New behaviours can be added by introducing pure axis tokens and/or patterns, without overloading existing modifiers.

### Costs and risks

- **Compatibility and behaviour shifts**:
  - Existing usage of composite tokens (`framework`, `path`, `samples`, method-level stance tokens) may change if we simply remove or move them.  
  - Mitigation:
    - Introduce compatibility aliases that map deprecated modifiers to their closest recipe for a deprecation window.  
    - Mark the deprecated tokens in docs and help surfaces and steer users toward axis combinations or patterns.

- **Implementation and documentation churn**:
  - Requires coordinated updates to:
    - `GPT/lists/completenessModifier.talon-list`, `scopeModifier.talon-list`, `methodModifier.talon-list`, `styleModifier.talon-list`.  
    - `GPT/lists/modelTone.talon-list` and `modelAudience.talon-list` for moved stance/audience tokens.  
    - `lib/staticPromptConfig.py` axis profiles that currently reference composite modifiers.  
    - Tests that assert specific axis values (`tests/test_axis_mapping.py`, `tests/test_static_prompt_config.py`, Talon settings tests).  
    - User docs and quick-help (`GPT/readme.md`, pattern GUIs).

## Implementation Plan

1. **Characterise current tokens**  
   - In a new work-log for this ADR, build a table listing each modifier in the four axis lists and its implied semantics across axes (completeness/scope/method/style/stance/format).  
   - Mark which tokens are already pure and which are composite.

2. **Apply list refactors**  
   - Update `GPT/lists/completenessModifier.talon-list`, `scopeModifier.talon-list`, `methodModifier.talon-list`, and `styleModifier.talon-list` to:
     - Remove or move composite tokens as per this ADR.  
     - Tighten definitions so each remaining token is pure.  
   - Add stance/audience items to `GPT/lists/modelTone.talon-list` and `GPT/lists/modelAudience.talon-list` for moved tokens.

3. **Add recipes and patterns**  
   - For behaviours previously carried by composite tokens (`framework`, `path`, `samples`, and any others identified during characterisation):
     - Add patterns or static-prompt profiles in `lib/staticPromptConfig.py` that implement them as axis combinations.  
     - Surface these recipes in pattern GUIs and `gpt_help` quick-help as canonical examples of composing axes.

4. **Update tests and docs**  
   - Extend existing tests to assert that:
     - Each axis token maps to a single conceptual axis.  
     - Composite behaviours are produced by combinations or patterns, not standalone modifiers.  
   - Refresh `GPT/readme.md` and help GUIs to:
     - Document the refined axis vocabularies.  
     - Show examples of composing pure tokens (for example, `deep + flow + dynamics + checklist`).

5. **Manage deprecation and cleanup**  
   - Introduce compatibility handling (for example, mapping `path` completeness to the nearest recipe) and document deprecations.  
   - After a grace period and sufficient test coverage, remove the compatibility mappings where appropriate, keeping only pattern-based behaviours.

## How to Exercise ADR‑018 Checks (this repo)

Until ADR‑018 is fully implemented, the most relevant checks are:

- **Axis mapping and static prompt config tests**
  - `python -m unittest tests.test_axis_mapping tests.test_static_prompt_config`
- **Static prompt docs and list alignment**
  - `python -m unittest tests.test_static_prompt_docs`
- **Full test sweep (this repo)**
  - `make test`

As list refactors and recipes land for this ADR, these same tests should be extended (per the Implementation Plan) to assert that:

- Each axis token stays on a single conceptual axis.  
- Former composite behaviours are covered by explicit axis combinations or patterns rather than single overloaded modifiers.
