# 013 – Static Prompt Axis Refinement and Streamlining

- Status: Accepted  
- Date: 2025-12-XX  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style axes + directional lenses)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation  
  - 012 – Style and Method Prompt Refactor

## Context

ADR 005 and ADR 007 established a separation between:

- **Static prompts** – short, semantic “what” descriptors (for example, `describe`, `system`, `product`, `todo`).
- **Axes** – orthogonal “how”/“shape” controls:
  - Completeness (`skim`, `gist`, `full`, `max`, …)
  - Scope (`narrow`, `focus`, `bound`, `relations`, …)
  - Method (`steps`, `plan`, `rigor`, `filter`, `cluster`, …)
  - Style (`plain`, `tight`, `bullets`, `code`, `diagram`, `presenterm`, …)
- **Directional lenses** – cognitive stance overlays (`fog`, `rog`, `ong`, etc.).

ADR 012 then moved several format-heavy and method-heavy static prompts entirely into the axes:

- Format-heavy prompts such as `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR` were retired as static prompts and now live solely as styles (`diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`).
- Method-heavy prompts such as `debug` have had their stance moved into the method axis (`debugging`).

After those refactors, the remaining static prompts still include a number of entries that:

- Primarily describe **scope** (for example, focus only on structure or flow).
- Primarily describe **method** (for example, compare two items, cluster items, scan for motifs).
- Combine method, scope, and style in a way that could be expressed more cleanly as a **recipe over axes**.

Examples include:

- `structure`, `flow`, `relation`, `type`.
- `compare`, `clusters`, `motifs`.
- Filter-style prompts such as `pain`, `question`, `relevant`, `misunderstood`, `risky`.
- Reflection/process prompts such as `wasinawa`, `experiment`, `science`.

These prompts are useful, but they blur the line between “what” (semantic lens) and “how” (scope/method/style). The emerging grammar for `model` is rich enough that we can express many of these bundles more cleanly as:

> semantic prompt (for example, `describe` or `system`)  
> + scope (for example, `relations`)  
> + method (for example, `structure`, `flow`, `compare`, `motifs`)  
> + style (for example, `taxonomy`, `table`, `bullets`).

The goal of this ADR is to streamline the static prompt set further in favour of the richer grammar, making:

- Static prompts mostly semantic lenses and domains.
- Axes and pattern recipes the primary place where “how” bundles live.

## Decision

We will:

1. **Introduce a small set of new method and style axis tokens** to capture behaviours currently baked into static prompts.
2. **Define axis‑equivalents for several “axis‑shaped” static prompts** such as `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, and `motifs`.
3. **Gradually demote or retire those static prompts** in favour of axis combinations and named recipes, similar to how ADR 012 retired `diagram`/`presenterm`/`code`/`commit`/`ADR`.
4. **Keep semantic/static prompts as the backbone** for domain frames and lenses that are not cleanly recoverable from axes (for example, `system`, `product`, `math`, `wardley`, `com b`, `tune`, `constraints`).

### New axis tokens

Add the following **method modifiers** (`methodModifier` values), using single, pronounceable tokens:

- `structure` – “Focus on structural aspects: outline parts, hierarchy, containment, and links among sections/components.”
- `flow` – “Focus on flow over time or sequence: steps, transitions, and control/data paths.”
- `compare` – “Compare two or more items: list similarities and differences, highlighting subtle distinctions.”
- `motifs` – “Scan for recurring motifs/patterns: identify repeated elements, themes, and notable outliers.”
- `wasinawa` – “Apply a What–So What–Now What reflection process with clearly separated stages.”

Add the following **style modifier** (`styleModifier` value):

- `taxonomy` – “Express the answer as a type or taxonomy: categories, subtypes, and their relationships.”

We may later decide to refine or split these, but this ADR treats them as the canonical axis tokens for these behaviours.

### Axis-equivalents for existing static prompts

Define **conceptual equivalences** between certain static prompts and axis combinations. These are not yet deletions; they are the target semantics we want to converge on:

- `structure` ≈
  - Static prompt: `describe`
  - Method: `structure`
  - Example recipe: `describe · full · focus · structure · plain · rog`.

- `flow` ≈
  - Static prompt: `describe`
  - Method: `flow`
  - Example recipe: `describe · full · focus · flow · plain · rog`.

- `relation` ≈
  - Static prompt: `describe`
  - Scope: `relations`
  - Example recipe: `describe · gist · relations · plain · fog`.

- `type` ≈
  - Static prompt: `describe`
  - Style: `taxonomy`
  - Example recipe: `describe · full · focus · taxonomy · rog`.

- `compare` ≈
  - Static prompt: `describe`
  - Method: `compare`
  - Style: `table` (often, though not mandatory)
  - Example recipe: `describe · full · focus · compare · table · rog` over two sources.

- `clusters` ≈
  - Static prompt: `describe`
  - Method: `cluster`
  - Style: `table`
  - Example recipe: `describe · full · focus · cluster · table · rog`.

- `motifs` ≈
  - Static prompt: `describe`
  - Scope: `relations`
  - Method: `motifs`
  - Style: `bullets`
  - Example recipe: `describe · gist · relations · motifs · bullets · fog`.

For **filter‑style prompts**:

- `pain`, `question`, `relevant`, `misunderstood`, `risky` already use `method=filter` and `style=bullets` in their profiles.
  - We treat these as semantic names for “what to filter” (pain points, questions, relevant items, misunderstandings, risks) layered on top of:
    - Base: `describe`
    - Method: `filter`
    - Style: `bullets`
    - Scope: `focus`.
  - Long‑term, these may become **pattern recipes** rather than full static prompts, but this ADR does not require their immediate retirement.

For **reflection/process prompts**:

- `wasinawa` ≈
  - Static prompt: `describe` (or `retro`)
  - Method: `wasinawa`
  - Style: `plain`
  - Scope: `focus`.

- `experiment` / `science`:
  - Already express their stance via `method=experimental`.
  - Static prompts exist primarily to provide a named recipe:
    - `experiment`: propose experiments.
    - `science`: generate hypotheses.
  - We treat these as **candidate recipes** over `method experimental` and do not retire them in this ADR, but we consider them method‑heavy prompts rather than pure static lenses.

### Static prompts to demote vs keep

We distinguish between:

- **Demotion candidates** – prompts whose behaviour will increasingly be represented via axes and recipes, with a view to possible retirement later:
  - `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `motifs`.
  - Filter cluster: `pain`, `question`, `relevant`, `misunderstood`, `risky`.
  - Reflection cluster: `wasinawa`, and potentially `experiment` / `science`.

- **Semantic backbone prompts to keep** – prompts that encode non‑trivial semantic frames, lenses, or domains:
  - Q‑axes / perspective prompts: `describe`, `who`, `what`, `when`, `where`, `why`, `how`, `assumption`, `objectivity`, `true`.
  - Domain/lens heavy: `knowledge`, `taste`, `system`, `tao`, `com b`, `math` family, `wardley`, `document`, `domain`, `tune`, `melody`, `constraints`, `effects`, `operations`, `facilitate`, `challenge`, `critique`, `retro`, `easier`, `unknown`, `team`, etc.
  - Transformations that encode specific operations rather than generic axes: `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`.
  - Planning and product prompts: `todo`, `product`, `metrics`, `value`, `jobs`, `done`, `bridge`.
  - Variation like `problem`, which encodes a specific laddering exercise beyond a simple axis combination.

This ADR does **not** immediately remove any of the demotion candidates; instead, it:

- Introduces the necessary axis tokens.
- Encourages future slices to:
  - Update profiles and patterns to use axes.
  - Then, where appropriate, retire static prompts once they are truly redundant.

## Consequences

**Pros**

- Reduces the cognitive load of the static prompt set by:
  - Moving scope/method/style bundles into the axes where they belong.
  - Leaving static prompts to encode semantic frames, domains, and rich lenses.
- Makes it easier to compose behaviours:
  - `describe systems flow diagram rog` is now clearly “describe, systems thinking, flow method, diagram style, rog lens”.
- Strengthens the role of **pattern recipes** (ADR 006) as the primary place to encode “how” bundles:
  - Patterns can highlight combinations like “Motif scan”, “Compare two designs”, or “Wasinawa reflection” without needing separate static prompts.

**Cons / Risks**

- Additional axis tokens:
  - Introduces a few more method/style values that users must learn (`structure`, `flow`, `compare`, `motifs`, `wasinawa`, `taxonomy`).
- Transitional complexity:
  - Users familiar with `structure`, `flow`, or `compare` as prompts will need to shift toward axis‑based commands or recipes.
  - Patterns and help UIs must be updated to make these axis combinations discoverable.

## Implementation Sketch and Next Steps

Implementation should proceed in small, testable slices, similar to ADR 012:

1. **Extend axis vocabularies**
   - Add new entries to `GPT/lists/methodModifier.talon-list`:
     - `structure`, `flow`, `compare`, `motifs`, `wasinawa`.
   - Add a new entry to `GPT/lists/styleModifier.talon-list`:
     - `taxonomy`.
   - Keep descriptions aligned with the intent of the corresponding static prompts (so we do not lose process fidelity).

2. **Update static prompt profiles to reference new axes**
   - In `lib/staticPromptConfig.py`, adjust profiles for:
     - `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `motifs`, `wasinawa` to use the new method/style/scope where appropriate.
       - For example, `relation` already uses `scope: "relations"`.
       - `motifs` can be updated to use `method: "motifs"` if desired.
   - Do **not** remove these prompts yet; this step makes their axis semantics explicit and consistent.

3. **Add or update pattern recipes**
   - In `lib/modelPatternGUI.py` and/or `lib/modelPromptPatternGUI.py`, add patterns that:
     - Use `describe` (or other semantic prompts) plus the new axis tokens (for example, “Structure outline”, “Flow walkthrough”, “Compare alternatives”, “Motif scan”, “Wasinawa reflection”).
   - Ensure these patterns appear in help UIs so axis‑heavy recipes are discoverable.

4. **Gradually retire redundant static prompts (optional but recommended)**
   - Once patterns and docs clearly surface axis‑based recipes, consider:
     - Removing `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `motifs`, `wasinawa` from `GPT/lists/staticPrompt.talon-list`.
     - Removing their profiles from `STATIC_PROMPT_CONFIG` (or keeping minimal description‑only entries if they remain useful for help text).
   - For the filter cluster (`pain`, `question`, `relevant`, `misunderstood`, `risky`) and method‑heavy prompts (`experiment`, `science`):
     - Decide whether to keep them as semantic shortcuts or re‑express them as patterns over `describe` + `method=filter` / `method=experimental`.

5. **Adjust docs and tests**
   - Update `GPT/readme.md`, ADR 005/007/012 examples, and help GUIs to:
     - Highlight new method/style tokens.
     - Show axis‑based recipes instead of pure static prompts for structure/flow/compare/motifs/etc.
   - Update or add tests to:
     - Validate that new axis tokens round‑trip correctly (`tests/test_axis_mapping.py`).
     - Confirm that `modelPrompt` applies the correct axes when these prompts are used (until they are fully retired).

## Status

- This ADR is **Proposed** for this repo.
- Concrete implementation (axis additions, profile updates, patterns, optional static prompt retirements) should be recorded in a dedicated work‑log file:
  - `docs/adr/013-static-prompt-axis-refinement-and-streamlining.work-log.md`.

