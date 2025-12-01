# 005 – Orthogonal Prompt Modifiers and Defaults for GPT Talon Commands

- Status: Accepted
- Date: 2025-12-01
- Context: `talon-ai-tools` GPT integration (`model` commands)
- Work-log: `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.work-log.md`

## Context

The current GPT voice command pipeline in `talon-ai-tools` already supports several axes for controlling behavior:

- **Goal / task**: via `staticPrompt` and `goalModifier` (for example, `fix`, `todo`, `product`).
- **Thinking lens**: via `directionalModifier` (for example, `fog`, `fig`, `dig`, `ong`, `rog`, `bog`).
- **System-level style**: via `modelVoice`, `modelTone`, `modelAudience`, `modelPurpose` and their corresponding `model_default_*` settings.
- **Source / destination**: via `modelSource`, `modelDestination`, stacks, and related captures.

However, there are important dimensions of interaction that are not yet explicit or easy to control:

- **Completeness** – how thoroughly to fill in the chosen territory (for example, skim the surface, give the gist, cover all major aspects, or go as exhaustive as is reasonable).
- **Method** – which reasoning approach to use (for example, step-by-step, plan-then-do, or rigorous justification).
- **Scope** – what conceptual territory is in-bounds (for example, only error-handling paths, only this function, only the circulatory system).
- **Output style** – how the result should be expressed (for example, plain prose, bullets, tables, or code only).

Right now, these are either implicit, pushed into ad-hoc phrasing, or partially overlapped with `directionalModifier`. It’s hard to:

- Issue ad-hoc prompts that tweak these axes for a single interaction.
- Configure sticky defaults so that multiple `model` requests share the same completeness/scope/method without repeating the same instructions.
- Express that some static prompts (for example, `fix`, `simple`, `short`, `todo`, `diagram`) carry not just a goal but also an implicit “profile” for completeness, scope, method, and style.
- Experiment safely with new axes without breaking the existing `model` surface.

The idea that’s emerging is: treat these as orthogonal axes, and support both:

- **Modifiers**: per-prompt overrides (“do this one stepwise, sketch only, local scope”).
- **Defaults**: persistent settings that apply when no modifier is given (“I’m in sketch mode for a while”).

## Decision

We will:

1. Introduce explicit, orthogonal modifier axes for:
   - Completeness (`completenessModifier`)
   - Method (`methodModifier`)
   - Scope (`scopeModifier`)
   - (Optional) Output style (`styleModifier`, beyond existing static prompts)

   These will be used in spoken commands to adjust behavior ad hoc on a per-prompt basis.

2. Introduce corresponding default settings for at least completeness and scope (and optionally method/style), analogous to `model_default_voice`, etc. For example:
  - `model_default_completeness`
  - `model_default_scope`
  - `model_default_method`
  - `model_default_style` (if needed)

   These will be applied automatically when a prompt does not specify that modifier axis explicitly.

3. Introduce per-prompt defaults keyed by static prompt, so that each static prompt can define its own “profile” for these axes. For example:
   - `fix` might default to `{ completeness: "solid", scope: "spot" }`.
   - `simple` might default to `{ completeness: "gist", scope: "spot" }`.
   - `todo` might default to `{ completeness: "gist", method: "steps", scope: "block" }`.
   - `diagram` might default to `{ completeness: "gist", scope: "file", style: "code" }`.

   These per-prompt profiles sit conceptually between global defaults and spoken modifiers, and are part of the intended behaviour of this ADR rather than a purely optional extension.

4. Keep `directionalModifier` as a separate, lens-like dimension, distinct from these contract-style axes:
   - It continues to represent thinking stance (abstract/concrete, acting/reflecting, etc.).
   - Over time, we may make it optional, but this ADR does not require that change.

5. Make the combination logic explicit, composable, and non-competing:
   - The pipeline will build the user prompt out of:
     - Goal / static prompt
     - `goalModifier`
     - `directionalModifier` (lens)
     - Zero or more of: `completenessModifier`, `methodModifier`, `scopeModifier`, `styleModifier`
     - System prompt built from `model_default_*` plus any `gpt_set_system_prompt` overrides
   - For each axis, compute a single `effective_<axis>` value per request using strict precedence:
     1. Spoken modifier (if present).
     2. Per-prompt profile value for that axis (if defined).
     3. Global default setting for that axis.
   - Only the `effective_<axis>` value is surfaced to the model for that axis (in system prompt lines and any user-level hints), so profiles and defaults do not compete.

This keeps the current `model` command usable, adds richer control in an incremental way, and supports experimentation without discarding the existing directional lenses.

## Details

### New modifier lists (per-prompt)

For all modifier axes, the design constraint is:

- Single, short words (ideally one or two syllables).
- At most three or four options per axis.
- Expect to speak at most one or two modifiers per command.

Semantics live in the description text, not the spoken word itself. In practice, only a small, “everyday” subset is expected to be used frequently; the rest are advanced and optional.

- `completenessModifier` (examples, from weakest to strongest):
  - `skim:` Very light pass; only touch the most obvious issues or ideas.
  - `gist:` Short but complete answer or summary; cover the main points once.
  - `full:` Thorough for normal use; cover all major aspects, but not every micro-detail.
  - `max:` As exhaustive as reasonable; aim to include essentially everything relevant (advanced; use sparingly).

- `methodModifier` (examples):
  - `steps:` Solve step by step; label each step and explain briefly.
  - `plan:` Give a short plan first, then carry it out.
  - `rigor:` Use disciplined, well-justified reasoning; avoid hand-waving and make uncertainty explicit instead of guessing (method-level constraint, not just a “serious” style flag).

- `scopeModifier` (**optional; conceptual scope rather than text region**):
  - `narrow:` Restrict discussion to a very small slice of the topic.
  - `focus:` Stay tightly on a central theme; avoid tangents and side-quests.
  - `bound:` Stay inside explicit limits; do not introduce material outside them.

- `styleModifier` (optional extra beyond existing prompts):
  - `plain:` Use straightforward, everyday language; minimise jargon.
  - `tight:` Make the answer short and dense; no fluff.
  - `bullets:` Present the main answer as concise bullet points.
  - `table:` Present the main answer as a Markdown table when feasible.
  - `code:` Present the main answer primarily as code or markup, with minimal prose.

These are designed to be short, punchy utterances that can be spoken reliably and concatenated into the prompt text in the same way as existing modifiers.

### Constraint semantics (Task / Completeness / Method / Scope / Style)

A concrete way to understand the four contract-style axes, consistent with the “Task / Constraints” template:

- **Task** – what you want done (for example, “summarise this”, “explain the flow”, “format as TODOs”).
- **Completeness** – how much of the chosen territory must be covered:
  - Think: “how much of the room am I responsible for cleaning or building out?”
  - `skim`/`gist`/`full`/`max` control how thoroughly to fill the fenced area, not how big the area is.
- **Method** – which tool or technique must be used:
  - Think: “which tool do I pick from the pegboard?”
  - `steps`, `plan`, `rigor` constrain how reasoning proceeds (for example, step-by-step vs plan-then-do vs disciplined justification).
- **Scope** – the taped-off area on the floor:
  - Think: “what part of the floor is taped off for this job?”
  - `narrow`, `focus`, `bound` constrain where the model is allowed to work conceptually (for example, “only error-handling”, “only this function”, “bounded to X”).
- **Style** – how the finished bench looks and feels:
  - Think: “how do I leave the workbench?”
  - `plain`, `tight`, `bullets`, `table`, `code` constrain the presentation, not validity.

In short: Scope = the fence; Completeness = how thoroughly you search inside the fence; Method = which tool you use; Style = how the finished output is presented.

### New default settings (persistent)

Add Talon settings analogous to existing ones:

- `model_default_completeness` (string; for example, `"sketch"`, `"full"`)
- `model_default_scope` (string; for example, `"narrow"`, `"focus"`, `"bound"`; recommended default is empty for no implicit scope bias)
- `model_default_method` (string; for example, `"stepwise"` or `"plan then do"`)
- `model_default_style` (optional, if we want default output form separate from static prompts)

These will be:

- Used when building the prompt if the corresponding modifier axis is not present in the spoken command.
- Overridable via a voice command similar to `model write as programmer`, for example:
  - `model set completeness sketch`
  - `model set scope file`
  - `model set method stepwise`

### Completeness axis – current semantics

In the current implementation, completeness behaves as follows:

- **Global default only in system prompt**:
  - `user.model_default_completeness` is surfaced via `GPTSystemPrompt` as `Completeness: <value>`.
  - This is the only default completeness signal; there is no per-static-prompt “bias” implemented in code.
- **User prompt stays plain unless you speak a modifier**:
  - `modelPrompt` does not inject extra completeness hints when no `completenessModifier` is spoken.
  - For example, `model fix fog` composes to `fix` + any goal modifiers + `fog` with no extra completeness text.
- **Spoken modifiers are explicit overrides**:
  - If you say `model fix solid fog`, the `solid` completeness modifier is appended directly into the user prompt string and is treated as the explicit completeness instruction for that request.
  - No additional “use your default completeness” or “bias toward …” phrases are added on top.

### Per-prompt defaults (profiles)

Some static prompts today implicitly bundle goal, completeness, scope, method, and style (for example, `simple` both “simplifies” and tends to produce short output). To make that explicit and controllable, we will introduce per-prompt profiles:

- For each static prompt key `k` (for example, `fix`, `todo`, `diagram`), maintain an optional profile. For illustration:
  - `defaults["todo"] = { method: "steps", style: "bullets" }`
  - `defaults["diagram"] = { style: "code" }`

When a static prompt is present, its profile contributes values to the `effective_<axis>` computation described above:

- If a spoken modifier is present for an axis, it wins.
- Otherwise, if the profile defines a value for that axis, it shadows the global default for that request for that axis.
- Otherwise, the global default is used.

Earlier experiments partially realised the completeness axis in code via a small mapping in `lib/talonSettings.py`, but this has since been removed to avoid competing defaults; future per-prompt profiles should follow the `effective_<axis>` precedence described above.

### How the pieces interact

- Baseline behavior:
  - The system prompt incorporates `model_default_voice`, `model_default_audience`, `model_default_purpose`, `model_default_tone`, and default completeness/method/style (and optionally scope) as brief sentences derived from `user.model_default_*`.
  - Conceptually, `effective_<axis>` values are derived using the precedence rules above; in the current implementation, contract-style axes in the system prompt lines reflect the global defaults, while any per-call overrides are expressed in the user prompt via spoken modifiers and profile hints.
  - If the user just says `model fix`, the response uses the global defaults for all contract-style axes, plus any per-prompt profile for `fix` (for example, `full` completeness) for axes where no spoken modifier is present.

- Per-prompt overrides:
  - If the user says:
    - `model fix skim steps plain`
  - Then:
    - `effective_completeness` = `skim` (overrides any default and any `fix`-specific completeness).
    - `effective_method` = `steps` (overrides default method and any `fix`-specific method).
    - `effective_style` = `plain` (overrides default style and any `fix`-specific style).
    - Directional lens (`fog` and so on) is unchanged unless also specified.

- Directional lenses remain distinct:
  - A command could be:
    - `model refactor full steps fog`
  - Where:
    - `refactor` = goal/static prompt.
    - `full` = completeness.
    - `steps` = method.
    - `fog` = thinking lens (abstract or generalizing overlay).
These examples are illustrative only; the concrete vocabularies and defaults are documented in the “Current Status” and “Next Steps” sections.
## Alternatives Considered

### Use only `directionalModifier` and repurpose it into method/completeness/scope bundles

Each `directionalModifier` entry would encode a mix (for example, “full file stepwise”), rather than adding new axes.

Rejected because:

- It is harder to mix and match (combinatorial explosion of bundled entries).
- It blurs the cognitive lens (fog/fig/dig and so on) with the output contract (completeness, scope, method).
- It is less flexible for future tuning.

### Settings-only approach (no new modifiers)

All behavior changes would be expressed via sticky settings; per-prompt control would stay free-form in natural language.

Rejected because:

- It raises friction for one-off prompts (for example, “sketch this one only”).
- It makes it harder to experiment quickly with different combinations per request.

### Modifiers-only approach (no defaults)

Everything would be controlled ad hoc; there would be no sticky configuration beyond voice, audience, purpose, and tone.

Rejected because:

- Many users want a persistent “mode” (for example, “I’m in sketch mode for an hour”).
- It forces repetition and leads to worse ergonomics for long sessions.

### Replace `directionalModifier` entirely

We could retire fog/fig/dig/ong/rog/bog and reuse the list slot for the new concepts.

Deferred: directional lenses are still valuable for some users, and this ADR aims to add axes orthogonally rather than remove a capability.

## Consequences

### Pros

- Clearer mental model: goal × lens × completeness × method × scope × style.
- Easy to:
  - Fire off ad-hoc nuanced prompts with short spoken phrases.
  - Configure session defaults for completeness, scope, and method, similar to voice and audience.
- Easier experimentation:
  - You can tune or temporarily redefine `completenessModifier`, `scopeModifier`, and `methodModifier` terms without touching the overall shape of the `model` command.
  - You can compare “default sketch plus occasional full” versus “default full plus occasional sketch” just by flipping settings.

### Cons and risks

- More axes create more cognitive overhead for new users.
- The list of modifiers can grow large; documentation and in-editor help (`gpt_help`) must stay clear.
- We need to carefully design default values to avoid confusing behavior when no modifiers are present.
- Implementation complexity increases slightly in `modelPrompt` and system-prompt construction.
- Overuse of scope or method modifiers (for example, stacking many at once, or combining strongly conflicting ones like `max` + `tight`) can lead to ambiguous behaviour; the intended everyday subset is small:
  - Completeness: mostly `skim`, `gist`, `full`.
  - Method: mostly `steps` (and occasionally `plan` / `rigor`).
  - Style: mostly `plain`, `bullets`, `code`.

## Open Questions

- Which axes are most valuable to implement first?
  - Completeness and scope seem highest value; method and style can follow.
- Should `directionalModifier` be made optional in the grammar, or kept required?
  - If made optional, what is the default lens behavior?
- How much of completeness, scope, and method should live in:
  - The system prompt (sticky defaults).
  - Versus the user prompt (ad-hoc modifiers).
- Do we want a “profile” concept (for example, `classic` versus `contract`) to toggle between:
  - Today’s lens-heavy behavior.
  - A more explicit contract-heavy behavior.
  - Any substantial change to these semantics should be proposed via a new ADR rather than silently rewriting this one.

## Next Steps

1. Refine vocabularies for:
   - `completenessModifier`, `scopeModifier`, `methodModifier`, and `styleModifier` (small, opinionated sets).
   - Prioritise the few values you actually use in practice; trim or rename others as experience accumulates.
2. Evolve lists and settings in code, wired into:
   - `lib/talonSettings.py` (lists, captures, settings, optional per-prompt profiles when/if added).
   - System prompt construction (relying on `user.model_default_*` for defaults and spoken modifiers for overrides).
3. Extend tests and tooling:
   - Add further tests for prompt composition and default/override precedence when new behaviours are introduced (for example, per-prompt profiles on additional axes).
   - Ensure new axes remain discoverable and low-friction in day-to-day use (for example, via `gpt_help` and README examples).
4. Dogfood and iterate:
   - Use modifiers in everyday work.
   - Adjust terms and defaults based on actual usage.
5. Optionally, add a temporary “beta profile” or `model beta` command to try alternative interpretations of these axes without disturbing existing `model` behavior, then merge once the design stabilizes.

## Current Status (this repo)

- Completeness, scope, method, and style modifier lists exist under `GPT/lists` and are registered as Talon lists:
  - `completenessModifier` (`skim`, `gist`, `draft`, `solid`)
  - `scopeModifier` (`spot`, `block`, `file`, `tests`)
  - `methodModifier` (`steps`, `plan`, `check`, `alts`)
  - `styleModifier` (`bullets`, `table`, `story`, `code`)
- The `modelPrompt` capture rule accepts these axes as optional modifiers (in the order: completeness, scope, method, style) before the required `directionalModifier`.
- The composed prompt string includes:
  - Base static prompt + goal modifier.
  - Completeness instructions (from spoken modifier only).
  - Scope/method/style instructions when spoken.
  - Directional (lens) instructions.
- Global defaults are available for all contract-style axes via Talon settings:
  - `user.model_default_completeness`, `user.model_default_scope`, `user.model_default_method`, `user.model_default_style`.
- `GPTSystemPrompt` incorporates these defaults and surfaces them as:
  - `Completeness`, `Scope`, `Method`, and `Style` lines in the system prompt array.
- There is currently no per-static-prompt completeness, scope, method, or style profile active in code; all defaults come from the `user.model_default_*` settings plus any spoken modifiers.
- The `gpt_help` command renders help tables for static prompts, directional modifiers, goal modifiers, voice/tone/audience/purpose, and all four new modifier axes.
- Focused tests exist for:
  - `modelPrompt` composition across completeness/scope/method/style.
  - `GPTSystemPrompt` use of the new default axes.

### How to run the relevant tests

- From the repo root, with Python 3 and `pytest` installed, run:
  - `python3 -m pytest -q tests/test_talon_settings_model_prompt.py tests/test_model_types_system_prompt.py`
- These tests:
  - Exercise `modelPrompt` composition for completeness/scope/method/style.
  - Verify that `GPTSystemPrompt` reads the `user.model_default_*` settings for the new axes.

## Practical usage tips

- Start simple:
  - Rely on `user.model_default_completeness` and speak completeness modifiers only when you want something clearly different (for example, `skim` for a quick pass or `solid` for a thorough one).
  - Use at most one or two spoken modifiers per `model` command until the axes feel natural.
- Prefer scope + method as your primary knobs:
  - Scope defaults can stay at `spot` for most day-to-day use; speak `file` only when you truly want file-level reasoning.
  - Method modifiers like `steps` or `plan` are a good default mental model tweak without overloading the prompt.
- Treat style as output formatting, not semantics:
  - Use `bullets` or `table` when you care mainly about how the answer is laid out.
  - Use `code` only when you truly want “code only, no explanation”.
- Use voice commands to shift modes:
  - `model set completeness skim` / `model reset completeness`.
  - `model set scope file` / `model reset scope`.
  - `model set method steps` / `model reset method`.
  - `model set style bullets` / `model reset style`.
