# 014 – Static Prompt Axis Simplification from Clustered Behaviours

- Status: Accepted  
- Date: 2025-12-XX  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style axes + directional lenses)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation for Axis-Based Grammar  
  - 012 – Style and Method Prompt Refactor  
  - 013 – Static Prompt Axis Refinement and Streamlining  

## Context

ADR 005 introduced four orthogonal “contract” axes:

- **Completeness** – how much of the chosen conceptual territory is covered.  
- **Scope** – what conceptual territory is in-bounds.  
- **Method** – how reasoning should proceed.  
- **Style** – how the answer should be expressed.

ADR 007 and ADR 012/013 then:

- Moved clearly format- or method-shaped static prompts (for example, `diagram`, `presenterm`, `debug`) into **style** or **method** axes.
- Tightened the role of static prompts to be mostly **semantic lenses and domains** (for example, `system`, `product`, `math`, `wardley`, `tune`).

However, the remaining static prompts still encode a substantial amount of **implicit axis behaviour**:

- Many prompts strongly imply a **method** (for example, group items, rank by importance, design experiments, reflect using WASINA–WA).
- Others imply a characteristic **scope** (for example, dependencies/relations, second- and third‑order effects, only actionable next steps).
- Some carry recognisable **completeness** patterns (for example, 3–5 items, full framework coverage, full path from A to B).
- Several share a consistent **style** (for example, checklists, ordered steps, tables).

This means:

- **Behaviour is duplicated**: axis semantics are baked into both static prompts and `*_Modifier` lists.  
- **Conceptual clusters are hidden**: similar behaviours across prompts (for example, “group into categories”, “map dependencies”, “list risks”) are not explicitly represented in the axes even though they recur.  
- **Static prompt vocabulary is harder to reason about**: the same axis-level idea appears under multiple static prompt names.

This ADR starts from the remaining static prompts, treats each one as an implicit profile over (completeness, scope, method, style), **clusters those profiles**, and then proposes explicit axis tokens for the clusters. The goal is to:

- Make more of the “how” explicit in the axes.  
- Simplify static prompts to be mostly “what” (semantic lens/domain).  
- Reduce hidden duplication between static prompts and axes.

## Decision

We will:

1. **Treat the remaining static prompts as evidence for latent axis values.**  
   For each prompt, we infer implied completeness/scope/method/style behaviours and group similar behaviours into clusters.

2. **Introduce or confirm a small set of axis tokens** (for completeness, scope, method, style) that represent those clusters.  
   Each token:
   - Is a single, unhyphenated word.  
   - Lives in exactly one axis.  
   - Has a concise, reusable definition.

3. **Express static prompt behaviour in terms of these axis tokens** via `STATIC_PROMPT_CONFIG`.  
   - Existing axis values are reused where they are a clear match.  
   - New axis tokens are added only where clusters are common and not well-covered by existing values.

4. **Demote remaining “axis-shaped” prompts** (those whose behaviour is largely captured by the new axis tokens) to:
   - Thin aliases over axis combinations, and/or  
   - Pattern recipes exposed in GUIs.  

Static prompts will then be:

- Primarily **semantic** (“what”): domain lenses, frameworks, problem flavours.  
- Axes will be the primary home of **behavioural contracts** (“how much”, “where”, “how”, “in what shape”).

### 1. Clustered behaviours and chosen axis tokens

This section summarises the main behaviour clusters discovered across static prompts, and the **axis tokens** chosen to represent them. Many clusters align with existing axis values; only a few require genuinely new tokens.

#### Completeness axis clusters

We keep the existing core completeness values (`skim`, `gist`, `full`, `max`, `minimal`, `deep`) from ADR 005 and augment them with two clustered behaviours that appear frequently in static prompts:

- `framework` – “Cover all major parts of an explicit named framework or map (for example, COM‑B, Wardley, Concordance) within the chosen scope.”  
  - Appears in prompts like `com b`, `wardley`, `tune`, `melody`.

- `path` – “Describe a continuous path from current to desired state, covering intermediate stages sufficiently to make the transition coherent.”  
  - Appears in prompts like `bridge` and some planning/transition prompts.

Other inferred completeness patterns (for example, “3–5 items”, “multi-format enumeration”) map adequately to existing values:

- Short lists (3–7 items) → `gist`.  
- Thorough local edits → `full` with a narrow scope.  
- Full ladders (for example, `problem`) → `full` within a small scope.

#### Scope axis clusters

We retain existing scope values (`narrow`, `focus`, `bound`, `edges`, `relations`, `dynamics`, `interfaces`) and make explicit two clustered scope behaviours that recur across static prompts:

- `system` – “Within the selected target, focus on the system as a whole: its components, boundaries, stakeholders, and internal structure, rather than individual lines or snippets.”  
  - Latent in `system`, `wardley`, `constraints`, `tune`, `melody`, `effects`.

- `actions` – “Within the selected target, focus only on concrete actions or tasks a user or team could take, not analysis or background.”  
  - Latent in `todo`, parts of `bridge`, and action-oriented planning prompts.

Other clustered scopes align with existing values:

- Relational views (`dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`) → `relations`.  
- Behaviour over time (`effects`, `constraints`) → `dynamics`.  
- Interfaces and boundaries between components → `interfaces`.  
- Local-region transformations (`fix`, `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`) → `narrow` within the selection.

#### Method axis clusters

Many clusters discovered from static prompts already map cleanly to existing method values from ADR 005/012/013 (`steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`, `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`).

For the remaining recurring patterns, we introduce two new method tokens:

- `ladder` – “Use abstraction laddering: place the focal problem, then step up to higher-level causes and down to consequences, ordered by importance.”  
  - Latent in `problem`.

- `contextualise` – “Add or reshape context for another operation (for example, supplying background for an LLM or reframing content) without rewriting the main text.”  
  - Latent in `context`, partially in `LLM`.

Other method clusters are adequately captured by existing tokens:

- “Group into categories” (`group`) → `cluster`.  
- “Sort by importance” (`sort`, `pain`, `risky`) → `prioritize` (possibly combined with `filter`).  
- “Generate questions” (`challenge`, `question`) → `filter` plus style-controlled enumeration.  
- “Analyse via frameworks” (`com b`, `tao`, `math`, `wardley`, `jim`, `domain`, `tune`, `melody`) → `rigor` or `systems` within framework-specific static prompts.  
- “Design experiments” (`experiment`, `science`) → `experimental`.  
- “Reflection over time” (`retro`) → `wasinawa` or `steps` + `deep` depending on how strong the structure needs to be.

#### Style axis clusters

Static prompts reinforce and reuse the existing style values (`plain`, `tight`, `bullets`, `table`, `code`, `cards`, `checklist`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy`).

No new style tokens are required for the clustered behaviours. Instead:

- Checklist-shaped outputs (`todo`, some `bridge` recipes) → `checklist`.  
- Ordered plans (`bridge`, `facilitate`) → `bullets` or `checklist` with `steps` method.  
- Tables (`wardley`, some `document` outputs) → `table`.  
- Pure transforms (`fix`, `group`, `split`, `shuffled`, `match`, `blend`, `join`) → `code`/`plain` with “text-only” semantics already expressed in descriptions.

### 2. Mapping static prompts onto axis tokens

Using the axis tokens above (and existing ones), we define conceptual profiles for representative prompts. These mappings live in `STATIC_PROMPT_CONFIG` and are illustrative rather than exhaustive:

- `todo`  
  - completeness: `gist`  
  - scope: `actions`  
  - method: `steps`  
  - style: `checklist`

- `bridge`  
  - completeness: `path`  
  - scope: `focus`  
  - method: `steps`  
  - style: `bullets`

- `problem`  
  - completeness: `full`  
  - scope: `focus`  
  - method: `ladder`  
  - style: `plain`

- `group`  
  - completeness: `full` (over the selected items)  
  - scope: `narrow`  
  - method: `cluster`  
  - style: `plain`

- `sort`  
  - completeness: `full` (over the selected items)  
  - scope: `narrow`  
  - method: `prioritize`  
  - style: `plain`

- `context`  
  - completeness: `gist`  
  - scope: `focus`  
  - method: `contextualise`  
  - style: `plain`

- `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`  
  - completeness: `normal` (expressed via `gist` or `full` as appropriate)  
  - scope: `relations`  
  - method: `structure` or `compare` depending on the flavour  
  - style: `plain` or `bullets`

- `effects`  
  - completeness: `full`  
  - scope: `dynamics`  
  - method: `steps` or `rigor`  
  - style: `plain`

- `system`, `constraints`, `tune`, `melody`  
  - completeness: `framework`  
  - scope: `system`  
  - method: `systems` / `rigor`  
  - style: `plain`

This pattern extends across the remaining static prompts: each is described as a semantic lens plus an axis profile.

### 3. Retiring axis-shaped prompts

Once the above mappings are in place and tested, we will:

1. **Retire axis-shaped static prompts from the user-facing static prompt surface.**
   - For example, `problem` becomes “`describe` + `method=ladder` + `scope=focus`”, exposed only as a named recipe in pattern pickers rather than as a standalone static prompt.
   - `group` becomes “any semantic prompt + `method=cluster`” via recipes; the `group` static prompt entry is removed.

2. **Update documentation and GUIs** to:
   - Show semantic prompts and axes as the primary knobs.  
   - Surface recipes that mirror the retired static prompts so existing workflows have clear, discoverable replacements.

3. **Track and execute the static prompt removals** in the associated work-log (no separate ADR required), so the code, lists, and docs converge with this decision.

## Consequences

**Pros**

- **Clearer separation of concerns**: static prompts describe *what* to think about; axes describe *how*, *how much*, *where*, and *in what shape*.  
- **Reduced duplication**: behaviours like “cluster into categories” or “describe 2nd/3rd order effects” live primarily as axis tokens and profiles rather than being repeated across many static prompts.  
- **Better composability**: users can combine semantic prompts with axis tokens (`framework`, `path`, `actions`, `ladder`, `contextualise`, `system`, `dynamics`, `interfaces`, `relations`) to express new behaviours without adding more static prompts.  
- **Easier evolution**: future static prompts can be added with lightweight axis profiles, and new behaviours can usually be added as axis values instead of new static prompts.

**Cons / Risks**

- **Cognitive overhead**: users must understand a slightly richer axis vocabulary (for example, what `framework` or `ladder` imply) even if they are mostly surfaced via recipes.  
- **Migration complexity**: behaviour must be kept consistent while moving semantics from static prompts into axis profiles and recipes.  
- **Axis bloat risk**: adding too many narrow axis tokens could recreate static prompt sprawl at the axis level if not kept in check.

We mitigate these risks by:

- Keeping the number of **new** axis tokens small and clustered around widely reused behaviours.  
- Introducing them first through **recipes and GUIs**, so users see concrete, named behaviours rather than raw axis tokens.  
- Using work-logs and tests to validate that behaviour before/after the refactor remains predictable and useful.

## Implementation Sketch

1. **Finalize axis token list**
   - Confirm the new completeness tokens: `framework`, `path`.  
   - Confirm the new scope tokens: `system`, `actions`.  
   - Confirm the new method tokens: `ladder`, `contextualise`.  
   - Ensure names are single, unhyphenated words and do not conflict with existing static prompt keys.

2. **Extend axis list files**
   - Update `GPT/lists/completenessModifier.talon-list`, `GPT/lists/scopeModifier.talon-list`, and `GPT/lists/methodModifier.talon-list` with the new tokens and concise descriptions.
   - Regenerate or refresh any help surfaces that list axis values.

3. **Update `STATIC_PROMPT_CONFIG` profiles**
   - Encode the clustered axis profiles for representative static prompts (`todo`, `bridge`, `problem`, `group`, `sort`, `context`, `dependency`/`cochange`/`interact`/`dependent`/`independent`/`parallel`, `effects`, `system`, `constraints`, `tune`, `melody`).  
   - Where possible, reuse existing axis tokens and only use new ones where clusters justify them.

4. **Add or update recipes in pattern GUIs**
   - Surface axis-based recipes that mirror the behaviour of demoted static prompts (for example, “Bridge plan”, “Abstraction ladder”, “Cluster items”, “Map dependencies”, “Second-order effects”).  
   - Ensure recipes use the new axis tokens so users learn them indirectly.

5. **Adjust documentation and quick-help**
   - Update `GPT/readme.md` and help GUIs to reflect the expanded axis vocabulary and show examples of composing semantic prompts with axis tokens.  
   - Clarify which static prompts are semantic anchors and which are effectively recipes over axes.

6. **Validate with tests and work-logs**
   - Extend `tests/test_static_prompt_config.py` and `tests/test_talon_settings_model_prompt.py` to assert that:
     - Static prompts now produce the expected axis profiles.  
     - Recipes that replace axis-shaped prompts behave as intended.  
  - Track concrete step-by-step changes in a new work-log (for example, `docs/adr/014-static-prompt-axis-simplification-from-clusters.work-log.md`).

## Current Status (this repo)

- Axis vocabularies:
  - `GPT/lists/completenessModifier.talon-list` includes `framework` and `path` alongside existing completeness values.
  - `GPT/lists/scopeModifier.talon-list` includes `system` and `actions` (as well as `dynamics` and `interfaces` from earlier work).
  - `GPT/lists/methodModifier.talon-list` includes `ladder` and `contextualise` alongside other method tokens.
- Static prompt profiles:
  - `lib/staticPromptConfig.py` uses the new axis tokens for key prompts:
    - `system` → `completeness=framework`, `scope=system`, `method=systems`, `style=plain`.
    - `todo` → `scope=actions` (with `gist · steps · checklist`).
    - `bridge` → `completeness=path`.
    - `effects` → `scope=dynamics`.
    - `context` → `method=contextualise` (plus `gist · focus · plain`).
- Retired axis-shaped prompts:
  - `group`, `sort`, and `problem` have been removed from `GPT/lists/staticPrompt.talon-list` and from `STATIC_PROMPT_CONFIG`.
  - Their behaviours are now represented via:
    - Axis tokens (`cluster`, `prioritize`, `ladder`) and
    - Named recipes/patterns in `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py`.
- Patterns and help:
  - Model pattern GUIs expose axis-based recipes for clustering, ranking, and abstraction laddering, plus an updated “Extract todos” pattern that uses `scope=actions`.
  - `GPT/readme.md` documents the expanded axis vocabularies so users can see and combine the new tokens directly.
- Tests:
  - `tests/test_static_prompt_config.py` asserts that `system`, `bridge`, `effects`, `context`, and `todo` use the new axis tokens.
  - Pattern and model-prompt tests continue to pass with the updated axis behaviour.

At this point, the main objectives of ADR 014 are implemented for this repo. Future loops may still fine-tune individual static prompt profiles or add more recipes, but no large in-repo behaviour slices remain for this ADR.
