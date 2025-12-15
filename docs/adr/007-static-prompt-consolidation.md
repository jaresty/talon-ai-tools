# 007 – Static Prompt Consolidation for Axis-Based Grammar

- Status: Accepted  
- Date: 2025-12-02  
- Context: `talon-ai-tools` GPT integration (`model` commands)  
- Related ADRs:
  - `005-orthogonal-prompt-modifiers-and-defaults.md`
  - `006-pattern-picker-and-recap.md`
  - `0011-concordance-static-prompt-axis-mapping-domain-boundaries.md`

## Context

ADR 005 introduced explicit, orthogonal modifier axes for:

- Completeness (`completenessModifier`)
- Scope (`scopeModifier`)
- Method (`methodModifier`)
- Style (`styleModifier`)

alongside persistent defaults (`model_default_*`). ADR 006 then added GUI-based pattern/preset pickers and recipe recap, making these axes more visible and easier to reuse.

Separately, the static prompt surface (`user.staticPrompt` plus `STATIC_PROMPT_CONFIG`) has grown organically over time. Many prompts encode:

- Purely *how* to answer (completeness, style, method, scope),
- Rather than *what* to do (semantic task or domain lens), or
- Behaviour that is now better expressed as a pattern recipe over the new axes.

The addition of a relational scope flavour (`relations`) further reduces the need for narrowly tailored “talk about relationships” static prompts.

Without consolidation, we risk:

- Cognitive overload: many near-duplicate prompts which differ only in style/completeness.
- Drift and ambiguity: unclear boundaries between “goal/static prompt” and “axis/pattern”.
- Underuse of the axes: users gravitate to old prompts instead of combining axes as intended.

This ADR proposes a principled pruning and demotion of static prompts in favour of:

- A smaller, more semantic static prompt set, and
- Axis-driven patterns and recipes (per ADR 006) for common behavioural profiles.

## Decision

We will:

1. **Demote “axis-shaped” static prompts to patterns or aliases**
   - Treat certain prompts as *named recipes* over axes rather than first-class goals.
   - Remove them from primary static prompt documentation and pattern menus once replacement recipes exist.

2. **Mark certain relational and planning prompts as consolidation targets**
   - Prefer expressing “talk about relationships/plans” via:
     - A semantic goal (for example, `describe`, `map`, `motifs`), plus
     - Scope (`relations`, `narrow`, `focus`) and method (`steps`, `diagnose`, `plan`) axes.
   - Keep only a small number of static prompts where domain semantics are genuinely richer than an axis bundle.

3. **Introduce a small set of new axis values to enable consolidation**
   - Add method and style values that capture recurring behaviours currently baked into multiple static prompts:
     - `method=filter` – extract only items matching a named criterion (for example, “pain points”, “risks”, “open questions”) rather than restating everything.
     - `method=prioritize` – assess and order items by importance/impact to the stated audience, making rankings explicit.
     - `method=cluster` – group similar items into labeled categories and describe each cluster, emphasising recurring patterns over singletons.
     - `style=checklist` – express the main answer as an actionable checklist (imperative, task-shaped bullets) rather than generic prose or bullets.

4. **Keep domain-heavy and format-/method-heavy prompts as static prompts (then refine via ADR 012/013)**
   - Retain static prompts that encode domain knowledge, specialised output contracts, or complex safety constraints that cannot be reconstructed from axes alone.
   - In this repo, many of the format-/method-heavy prompts originally kept by this ADR (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `motifs`) have since been retired as static prompts and re-expressed as style/method axis values and patterns by:
     - ADR 012 – Style and Method Prompt Refactor, and
     - ADR 013 – Static Prompt Axis Refinement and Streamlining.
   - The remaining static prompts in this repo focus on semantic/domain lenses and structured tasks; new format/method behaviours should usually be added as axes or patterns rather than new static prompts.

This ADR explicitly opts **not** to preserve backwards compatibility at the static-prompt level. Once adopted, we will update the static prompt list, axis vocabularies, and patterns in one coordinated change:

- Demote or remove axis-shaped prompts from the staticPrompt surface.
- Introduce the new axis values (`filter`, `prioritize`, `cluster`, `checklist`) immediately.
- Consolidate relational and planning prompts in the same pass.

## Analysis

### 1. Prompts that overlap most strongly with axes

These prompts primarily express *style, completeness, or tone* and add little semantic task on top. They now overlap heavily with ADR 005 axes and ADR 006 patterns.

**Candidates to demote to axis-based patterns or aliases:**

- `simple`
  - Current role: “Rewrite this in a simpler way while preserving the core meaning.”
  - Axis equivalent: a generic goal (for example, `describe` or `fix`) with `completeness=gist` and `style=plain` or `tight`.
  - Issue: blurs the line between goal and style; hides the underlying axis vocabulary.
  - Decision: **demote**:
    - Keep a pattern recipe like “Simplify locally” (for example, `describe · gist · narrow · plain`).
    - Remove `simple` from the primary staticPrompt surface once patterns are in place.

- `short`
  - Current role: “Shorten this while preserving meaning; return only the modified text.”
  - Axis equivalent: `gist` + `tight` + possibly `minimal`.
  - Decision: **demote**:
    - Represent this behaviour via patterns (for example, “Tighten summary”) using axes.
    - Remove `short` from the primary staticPrompt surface.

- `clear`
  - Current role: remove jargon and produce accessible language.
  - Axis equivalent: `style=plain` plus appropriate `modelAudience`.
  - Decision: **demote or narrow**:
    - Prefer `style=plain` plus audience and domain-specific prompts.
    - If retained, tighten semantics towards explicit jargon detection/explanation (beyond what `style=plain` implies).

- `style`
  - Current role: meta-prompt about style instructions.
  - Overlaps with `styleModifier` axis and ADR 006 grammar help.
  - Decision: **demote**:
    - Fold into `model quick help style` and/or pattern recipes; do not treat as a general-intent static prompt, and remove it from the staticPrompt list once help/patterns cover its use.

- `silly`
  - Current role: tonal change, not a task.
  - Axis equivalent: a `modelTone` or `modelIntent` flavour, or a pattern.
  - Decision: **demote**:
    - Prefer modelling this as a tone axis value and/or pattern (“Silly recap”) rather than a standalone static prompt, and remove it from the staticPrompt list.

- `announce`
  - Current role: “Announce this to the audience.”
  - Axis equivalent: combination of `modelVoice`, `modelAudience`, and `modelTone`.
  - Decision: **demote**:
    - Keep as a pattern recipe (“Announce to team”) built from axes and a generic goal (for example, `describe` or `format`), and remove it from the staticPrompt list.

### 2. Relational prompts vs relational scope

The addition of `scope=relations` makes it easier to express “talk about relationships between elements” without a flock of narrowly-scoped static prompts.

**Static prompts most affected:**

- `relation`
  - Current role: invert perspective to focus on relationships between things.
  - Now largely expressible as: `describe` (or `map`/`motifs`) + `scope=relations`.
  - Decision: **consolidate**:
    - Either narrow its semantics to something genuinely distinct (for example, a specific “inversion” behaviour), or
    - Replace it with a recipe over `describe`/`map`/`motifs` plus `scope=relations`, and remove it from the staticPrompt list.

- `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`
  - Current role: variants of “explain how these elements relate” (dependencies, co-change, independence, parallelisation risk).
  - With `relations` and a semantic goal (for example, `map` or `motifs`), much of this contract can be expressed via:
    - Natural-language task description,
    - `scope=relations`,
    - Method choices (`diagnose`, `steps`, `rigor`).
  - Decision: **mark as consolidation targets**:
    - Avoid adding more fine-grained “relationship words” as new static prompts.
    - Prefer a smaller set of relational prompts (for example, one for dependencies, one for co-evolution/interaction) plus recipes with `relations` scope, and remove redundant ones in the consolidation pass.

### 3. Planning and filter-style prompts

Several prompts bundle a light planning/filtering semantic with a heavily axis-shaped contract (`gist`, `steps`, `bullets`, `focus`).

**Planning cluster:**

- `todo`, `bridge`
  - Common structure: “extract/plan steps for X”, usually with `completeness=gist`/`full`, `method=steps`, and focused scope.
  - Decision:
    - Keep `todo` and `bridge` as the small core set of planning static prompts.
    - Express “quick how-to” and “incremental next step” behaviours as **pattern recipes** over these prompts and the axes (for example, `steps` + `gist` + `checklist` or `minimal` + `steps` + `focus`), rather than as separate static prompts.

**Filter-style cluster:**

- `pain`, `question`, `relevant`, `misunderstood`, `risky`
  - Common structure: “list items of type X (pain points, questions, relevant bits, misunderstandings, risks)” with `gist` + `bullets` + `focus`.
  - Decision:
    - Retain their *semantic* meaning (they remain useful lenses).
    - However, bias new design towards:
      - Expressing them as recipes over more general prompts (`describe`, `system`, `product`) plus constrained wording, and
      - Using `method=filter` (and sometimes `method=prioritize`) to encode “X-only, possibly ordered” behaviour at the axis level, and
      - Avoiding further proliferation of similar “X-only bullets” prompts when an axis-driven pattern would suffice.

### 4. Prompts to keep as static prompts

We explicitly *do not* propose consolidation for:

- Format/transform heavy prompts (original ADR 007 scope):
  - `diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`, `commit`, `ADR`, `HTML`.
  - Rationale at the time: encode strong, specific output formats and safety constraints that go beyond axes.

- Domain or lens heavy prompts:
  - `math`, `orthogonal`, `bud`/`boom`/`meld`/`order`/`logic`/`probability`, `map`, `graph`, `document`, `wardley`, `com b`, `operations`, `science`, `experiment`, `debug`, `system`, `tao`, `jim`, `domain`, `tune`, `effects`, `problem`, `lens`, `motifs`, `knowledge`, `taste`, `assumption`, `objectivity`, etc.
  - Rationale: these encode non-trivial semantic frames or specialised workflows that are not recoverable from axes alone.

These remain the “semantic backbone” of the static prompt surface and are good anchors for ADR 006 pattern recipes.

> **Note (added after ADR 012/013):** In this repo, later ADRs have refined this decision:
> 
> - ADR 012 migrated several of the format/transform prompts (`diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `commit`, `ADR`, `HTML`, `emoji`, `lens`) into the style axis and removed them as static prompts.
> - ADR 013 further moved some axis‑shaped prompts (`structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `motifs`, and others) into method/scope/style axes and patterns.
> 
> ADR 007’s intent still applies conceptually (keep semantic/domain prompts as the backbone), but the concrete list of “kept” static prompts in this repository is now smaller and should be read together with ADR 012 and ADR 013.

## Consequences

- **Pros**
  - Reduces cognitive load: fewer, more meaningful static prompt names.
  - Encourages axis literacy: users see style, completeness, scope, and method more directly, rather than through opaque prompt names.
  - Strengthens ADR 006 patterns: recipes become the primary place to encode “how” bundles, leaving static prompts for “what”.
  - Makes future evolution easier: adding a new axis or scope flavour is less likely to require new static prompts.

- **Cons / Risks**
  - Behavioural churn: users who rely on `simple`/`short`/`clear`/`announce` and related prompts will see them replaced by recipes over axes.
  - Transitional complexity: none at the staticPrompt level; we changed prompts and axes together in one coordinated update.
  - Potential under-documentation: without careful docs and pattern examples, users may not discover axis combinations that replace retired prompts.

We mitigate churn by:

- Using ADR 006 pattern GUIs to surface clear replacements (“Simplify locally”, “Tighten summary”, etc.),
- Updating quick help and docs to emphasise axis-first alternatives and new recipes,
- Ensuring the consolidation pass is tested and applied coherently in one change.

## Implementation Sketch and Next Steps

Implementation will proceed in one coordinated consolidation pass (possibly composed of several mechanical patches), validated by tests in `tests/test_talon_settings_model_prompt.py` and manual exercise via ADR 006 flows.

### Short-term steps

1. **Mark demotion targets in `STATIC_PROMPT_CONFIG`**
   - Add comments or metadata for:
     - `simple`, `short`, `clear`, `style`, `silly`, `announce`.
   - Optionally tag relational and planning clusters as “consolidation candidates”.

2. **Add replacement recipes to pattern pickers**
   - In `lib/modelPatternGUI.py` / `lib/modelPromptPatternGUI.py`:
     - Add patterns like:
       - “Simplify locally” (profile: `gist`, `narrow`, `plain`),
       - “Tighten summary” (`gist`, `tight`),
       - “Announce to team” (tuned voice/audience/tone).

3. **Update help surfaces**
   - In `lib/modelHelpGUI.py` and related docs:
     - Steer users toward axes and patterns for “simple/short/clear/silly/announce”.
     - Clarify the role of `relations` scope and how to combine it with semantic prompts.

### Medium-term steps

4. **Consolidate relational and planning prompts and update discovery surfaces**
   - Remove demoted prompts from:
     - `GPT/lists/staticPrompt.talon-list`,
     - ADR 006 usage examples and GUI labels,
     - Help GUIs that list static prompts.
   - Consolidate relational and planning prompts:
   - Evaluate usage and redundancy for:
     - `relation`, `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`,
     - `how to`, `incremental`, `bridge` (relative to `todo` and generic patterns).
   - Where safe, fold them into:
     - Fewer, clearer static prompts, plus
     - ADR 006 recipes with `relations` scope and appropriate methods.

Progress and concrete changes for this ADR should be recorded in a dedicated work-log:

- `docs/adr/007-static-prompt-consolidation.work-log.md`

## Current Status (this repo)

- Axis vocabularies:
  - New method and style values from this ADR are implemented and wired through lists, help, and patterns:
    - `methodModifier`: now includes `filter`, `prioritize`, `cluster` alongside existing values.
    - `styleModifier`: now includes `checklist` alongside existing values.
  - Scope now includes a relational flavour:
    - `scopeModifier`: includes `relations` for relationship-focused prompts and recipes.
- Static prompt surface:
  - Axis-shaped prompts have been removed from `GPT/lists/staticPrompt.talon-list`:
    - `announce`, `simple`, `short`, `clear`, `silly`, `style`, `how to`, `incremental`.
  - Planning prompts are consolidated around:
    - `todo` (gist, steps, checklist, focus) and `bridge` (full, steps, focus).
  - Relational prompts now encode relational scope in their profiles:
    - `relation`, `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel` use `scope: "relations"`.
- Patterns and help:
  - Pattern picker includes axis-based recipes that replace removed prompts and showcase the axes:
    - Simplification: `Simplify locally` and `Tighten summary`.
    - Planning: `Extract todos` uses `style=checklist`.
    - Relational/risk: `Map dependencies` (relations scope) and `Risk scan` (filter method).
    - Filter-style: `Pain points` uses `method=filter`.
  - Quick-help GUI and README are updated to show the new axis values and the checklist style for TODOs.
- Tests:
  - `tests/test_talon_settings_model_prompt.py` asserts that:
    - `todo` drives `GPTState.system_prompt.style == "checklist"`.
    - `GPTState.last_recipe` for `todo` reflects `steps · checklist`.
    - Filter-style prompts like `pain` drive `method="filter"` and associated axes.
    - Relationship-style prompts like `dependency` use `scope="relations"` in the effective axes.

## Everyday usage after consolidation (this repo)

After ADR 007, everyday usage should lean on a small static prompt set plus axes and patterns:

- Simplification:
  - Use `model describe gist plain …` or the “Simplify locally” pattern instead of `simple`.
  - Use `model describe gist tight …` or the “Tighten summary” pattern instead of `short`.
- TODOs and planning:
  - Use `model todo … checklist …` (or the “Extract todos” pattern) for actionable task lists.
  - Use `model bridge … steps …` when you need a deeper plan from current to desired state.
- Relationships:
  - Use `model dependency … relations …` (or the “Map dependencies” pattern) to focus on how elements depend on each other.
  - Use `model describe … relations …` with `map`/`motifs` for broader relationship or pattern mapping.
- Filter-style lenses:
  - Use prompts like `pain`, `question`, `relevant`, `misunderstood`, `risky` with `method=filter` (or the “Pain points” / “Risk scan” patterns) for X-only lists.

These flows replace older, more numerous static prompts with a consistent axis-first grammar, surfaced through ADR 006’s pattern pickers and grammar help.
- Tests:
  - `tests/test_talon_settings_model_prompt.py` asserts that:
    - `todo` drives `GPTState.system_prompt.style == "checklist"`.
    - `GPTState.last_recipe` for `todo` reflects `steps · checklist`.
