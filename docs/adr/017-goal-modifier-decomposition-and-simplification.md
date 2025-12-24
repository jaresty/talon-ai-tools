# 017 – Goal Modifier Decomposition and Simplification

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT `model` commands (static prompts + completeness/scope/method/style + directional modifiers + voice/audience/tone/intent; legacy `goalModifier` shorthands)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 015 – Voice, Audience, Tone, Intent Axis Decomposition  
  - 016 – Directional Axis Decomposition and Simplification  

> **2025-12-24 update (ADR 0061)**: intent tokens are now single-word canonical forms (for example, `plan`, `decide`, `teach`). Legacy phrases such as “for deciding” appear below to describe historical tokens.

## Context

ADR 005 introduced `goalModifier` as part of the overall grammar:

- **Goal / task**: via `staticPrompt` and `goalModifier` (for example, `fix`, `todo`, `product`).  
- **Thinking lens**: via `directionalModifier`.  
- **Contract axes**: completeness/scope/method/style.  
- **System-level style**: via voice/audience/tone/intent.  

Historically, the `goalModifier` Talon list contained:

- `just` – “Keep this descriptive, not problem-solving. Do not offer suggestions, solutions, or recommendations.”  
- `solve` – “Keep this problem-solving, not descriptive.”  
- `sample` – “Generate N diverse responses with explicit numeric probabilities (total ≈1)…”.

In practice:

- `staticPrompt` already carries most of the *what* (for example, `fix`, `todo`, `describe`, `retro`, `product`, `dependency`, `risky`, etc.).  
- `goalModifier` acted as a small, orthogonal **mode/intent** knob on top of that.  
- The axis set (completeness/scope/method/style) plus `directionalModifier` covers much of what `just`/`solve` describe in prose (for example, “descriptive vs problem-solving”) without needing a separate goal axis.

As with `directionalModifier` before ADR 016, there is a mild risk that `goalModifier` accumulates heterogeneous meanings over time (mode, method, sampling contract) unless we clarify what belongs here and what belongs in other axes.

This ADR focuses on:

- Decomposing `goalModifier` behaviour into completeness/scope/method/style (and related axes) where appropriate.  
- Deciding which remaining semantics, if any, deserve a dedicated goal axis.  
- Simplifying the grammar where `goalModifier` is redundant.

## Behaviour decomposition

For reference, the legacy `goalModifier` tokens were:

- `just`  
  - Text: “Keep this descriptive, not problem-solving. Do not offer suggestions, solutions, or recommendations.”  
  - Behaviour:
    - **Goal/mode**: “describe/analyse only” vs “suggest/fix”.  
    - Implicit method bias: descriptive/explanatory, not “solve”.  
  - Axis-shaped aspects:
    - Intent (`for information`) or “describe” static prompt.  
    - Method leaning toward explanation/analysis, not `steps`/`plan`.  
  - Residual goal semantics:
    - A hard constraint that **forbids** solution proposals, even if axes might otherwise encourage them.

- `solve`  
  - Text: “Keep this problem-solving, not descriptive.”  
  - Behaviour:
    - **Goal/mode**: “take action / propose solutions” vs “just describe”.  
    - Implicit method bias: favour `steps`, `plan`, `diagnose`, `xp`, `experimental`.  
  - Axis-shaped aspects:
    - Intent (`for solving` / `for debugging` / `for project management`), already modelled via static prompts and axes.  
  - Residual goal semantics:
    - A mode-level emphasis: prioritise problem-solving over neutral description when in doubt.

- `sample`  
  - Text: “Generate N diverse responses with explicit numeric probabilities (total ≈1)…; output only the responses and their probabilities.”  
  - Behaviour:
    - **Output contract**: structured multi-sample output with explicit probabilities.  
    - Implicit style: table- or list-like structure; code-like formatting possible.  
    - Implicit method: “sample from distribution rather than just taking the top mode”.  
  - Axis-shaped aspects:
    - Style (structured list/table with probabilities).  
    - Method (sampling / exploration) – potentially a method token or pattern.  
  - Residual goal semantics:
    - A distinct interactive mode: “act as a sampler” rather than a normal single-answer helper.

## Clusters

From the decomposition, `goalModifier` semantics cluster into:

1. **Describe vs solve stance**  
   - `just` vs “normal” (which already tends toward solving for many static prompts).  
   - This is a real **mode/intent** contrast, but much of the “solve” behaviour is already encoded via static prompts, purposes, and methods.

2. **Sampling mode**  
   - `sample`.  
   - This is about a specific **output contract** (“N diverse options with probabilities”) that naturally fits into completeness + method + style.

Unlike directional modifiers (which needed a richer decomposition and surface reduction), the `goalModifier` surface is already small. That makes it a good candidate for further simplification by pushing its semantics into existing axes.

## Decision

We will:

1. **Stop treating `goalModifier` as a first-class axis for new behaviour** and instead:
   - Express “describe vs solve vs sample” semantics primarily via existing axes (static prompts, intent, completeness/scope/method/style) and, where needed, new axis tokens.  
   - Treat the existing `goalModifier` tokens as **legacy shorthands** that should not accumulate new semantics.
2. **Migrate `just` semantics into the method axis**:
   - Introduce a method token (name to be finalised; for this ADR we call it `analysis`) that encodes “describe/analyse only; do not propose solutions”.  
3. **Migrate `sample` semantics into completeness + method + style**:
   - Introduce a completeness token (for example, `samples` or `variants`) that encodes “produce N diverse options with short descriptions and explicit probabilities”, plus recommended method/style patterns.  
4. **Treat `solve` as redundant**:
   - Problem-solving is already the default stance for most action-oriented static prompts; `solve` does not introduce a distinct behaviour that cannot be expressed via static prompts, purposes, and methods.  
   - We will deprecate `solve` in docs and examples, and avoid adding new behaviours under it.
5. **Discourage adding new `goalModifier` entries**:
   - Any future behaviour that looks like a new “goal” should first be expressed via static prompts, intent, or the contract axes; only if it fundamentally cannot fit there should we consider extending the grammar (likely via a dedicated ADR rather than this one).

### Axis-level migration for existing tokens

- `just` – **Descriptive goal → method axis**  
  - Intended meaning:
    - “Describe or analyse only; do not propose changes, actions, or solutions.”  
  - Recommended axis defaults when designing recipes:
    - Intent: `for information` or other non-intervention purposes.  
    - Method: explanatory/structural methods (`structure`, `systemic`, `mapping`, `flow`, `motifs`, `diagnose`) rather than `steps`, `plan`, `xp`, `experimental`.  
- Proposed method axis expression:
  - Add `method=analysis` (or similar) to `methodModifier.talon-list` with:
    - “Important: Describe, analyse, and structure the situation; do not propose specific actions, fixes, or recommendations.”  
  - Example usage:
    - `model describe analysis fog` – descriptive, non-prescriptive overview.  
    - `model describe systemic analysis rog` – systems-thinking analysis only.
  - Recommendation:
    - Prefer `method=analysis` (and similar axis tokens) over `goalModifier=just` in new examples and patterns.

- `solve` – **Problem-solving goal → existing defaults**  
  - Intended meaning:
    - “Aim to produce or refine a solution, fix, or concrete set of next actions.”  
  - Axis / prompt expression:
    - Static prompts: `fix`, `todo`, `product`, `retro`, `risky`, etc. already carry a solving stance.  
    - Intent: `for debugging`, `for deciding`, `for planning`, `for project management`.  
    - Method: `steps`, `plan`, `xp`, `experimental`, `diagnose`.  
  - Recommendation:
    - Treat `solve` as **redundant** for new usage. When you mean “solve”, pick an appropriate static prompt + intent + method combination instead (for example, `fix · steps · ong`).

- `sample` – **Sampling goal → completeness + method + style**  
  - Intended meaning:
    - “Act as a sampler over your own distribution: produce N diverse options with explicit probabilities that approximately sum to 1, avoiding near-duplicates.”  
  - Axis-level expression:
    - Completeness: introduce `completeness=samples` / `variants`:
      - “Important: Provide N diverse, self-contained options with short descriptions and explicit numeric probabilities that approximately sum to 1; avoid near-duplicates.”  
    - Method: use `diverge` (and possibly a future `sampling` method token if needed).  
    - Style: encourage `table` or structured `bullets` for readability.  
  - Example usage:
    - `model describe samples diverge fog` – sample multiple framings with probabilities.  
    - `model describe mapping samples fog` – multiple systems-level options with probabilities.  
  - Recommendation:
    - Prefer expressing sampling behaviour via `completeness=samples` + method/style, rather than relying solely on `goalModifier=sample` in new docs and patterns.

## Consequences

### Positive

- **Clearer axis ownership**:
  - “Describe-only” behaviour lives in the method axis (`analysis`), not in a separate goal axis.  
  - Sampling behaviour lives primarily in completeness + method + style, rather than in `goalModifier`.
- **Less grammar surface area**:
  - New behaviours don’t need new goal modifiers; they can be expressed via static prompts, purposes, and axes.  
  - `solve` is treated as part of the default stance for many prompts rather than a separate spoken token.
- **Easier mental model**:
  - Users can think in terms of:
    - *What*: static prompt + intent.  
    - *How much / where / how / in what shape*: completeness/scope/method/style + directional.  
    - Only legacy flows still rely on `just`/`solve`/`sample` as goal modifiers.

### Negative / trade-offs

- Some existing habits (`model just …`, `model sample …`) will need to be migrated gradually to axis-based forms (for example, `analysis` and `samples` completeness).  
- Until completeness/method lists are extended and wired everywhere, `goalModifier` will remain in the grammar for backwards compatibility, which means the axis migration is a partial, staged change rather than an immediate removal.

## Migration notes and examples

This ADR does not immediately change the `goalModifier` list or grammar in this repo; instead, it:

- Records how `just` and `sample` should be expressed via axes going forward (method/completeness/style), and  
- Treats `solve` as redundant for new usage.  

A few patterns for axis-first usage:

- Purely descriptive analysis (axis-first):
  - `model describe analysis fog` – descriptive, upwards/generalising lens.  
  - `model describe mapping analysis fog` – descriptive system mapping.  
- Explicit problem-solving:
  - `model fix xp ong` – problem-solving stance with `fix` static prompt and `xp` method (no `solve` needed).  
  - `model todo gist checklist ong` – generate and refine a todo list, lean into action.
- Sampling:
  - `model describe samples diverge fog` – propose several framings with probabilities.  
  - `model describe mapping samples fog` – several systems-level framings with probabilities.

In all of these, completeness/scope/method/style and the directional lens carry the semantics; `goalModifier` is treated as legacy sugar rather than the primary contract surface.

## Migration cheat sheet – `goalModifier` → axis recipes

This subsection gives concrete, side‑by‑side mappings from legacy `goalModifier` usage to axis‑first forms, to make migration easier in practice.

- `just` (describe-only):
  - Old:
    - `model just describe fog`
    - `model just describe mapping fog`
  - New (axis-first):
    - `model describe analysis fog`
    - `model describe mapping analysis fog`

- `solve` (problem-solving):
  - Old:
    - `model solve fix xp ong`
    - `model solve todo gist checklist ong`
  - New (axis-first; `solve` implied by prompt + axes):
    - `model fix xp ong`
    - `model todo gist checklist ong`

- `sample` (sampling with probabilities):
  - Old:
    - `model sample product diverge fog`
    - `model sample describe mapping fog`
  - New (axis-first; sampling via completeness + method + style):
    - `model describe samples diverge fog`
    - `model describe mapping samples fog`

These mappings are not exhaustive, but they should cover the most common uses of `just`/`solve`/`sample` and illustrate how to express the same intent using completeness, method, style, and directional axes instead of `goalModifier`.

## Current status in this repo

As of 2025‑12‑05, the following ADR 017 pieces are implemented in `talon-ai-tools`:

- Axis tokens:
  - `GPT/lists/completenessModifier.talon-list`:
    - Includes the `samples` completeness token described here.
  - `GPT/lists/methodModifier.talon-list`:
    - Includes the `analysis` method token described here.
- Tests:
  - `tests/test_static_prompt_docs.py`:
    - `test_new_completeness_and_method_tokens_present` asserts that `samples` and `analysis` exist in the corresponding Talon lists.

Not yet changed:

- The `goalModifier` list file has been removed from this repo, and `goalModifier` is no longer registered or referenced in the `modelPrompt` grammar.  
- README and quick-help surfaces now mention `samples` and `analysis` in cheat sheets and examples; any remaining references to `goalModifier` are purely historical/contextual (for example, in ADRs and migration notes).

Future loops for this ADR should:

- Gradually migrate examples and docs to the axis-first forms shown above, and  
- Treat `goalModifier` as fully deprecated for new usage; any future behavioural changes around mode/intent should be expressed via static prompts, purposes, and axes (completeness/scope/method/style + directional), or via new ADRs if they truly require additional structure.
