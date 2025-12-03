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
- Express that some static prompts (for example, `fix`, `todo`, `diagram`) carry not just a goal but also an implicit “profile” for completeness, scope, method, and style.
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

2. Introduce corresponding default settings for all four axes, analogous to `model_default_voice`, etc. For example:
  - `model_default_completeness`
  - `model_default_scope`
  - `model_default_method`
  - `model_default_style` (if needed)

   These will be applied automatically when a prompt does not specify that modifier axis explicitly.

3. Introduce a single, per-static-prompt configuration map keyed by canonical static prompt names. Each entry configures:
   - A human-readable description for the `Task:` line (for example, “Reformat this into proper Gherkin using Jira markup; output only the reformatted Gherkin with no surrounding explanation.”).
   - Optional defaults for any of the four contract-style axes (completeness, method, scope, style). For example:
     - `fix` might configure `{ description: "...", completeness: "full", scope: "narrow" }`.
     - `todo` might configure `{ description: "...", completeness: "gist", method: "steps", scope: "focus", style: "bullets" }`.
     - `diagram` might configure `{ description: "...", completeness: "gist", scope: "focus", style: "code" }`.

   This per-prompt configuration map sits conceptually between global defaults and spoken modifiers, and is part of the intended behaviour of this ADR rather than a purely optional extension.

4. Keep `directionalModifier` as a separate, lens-like dimension, distinct from these contract-style axes:
   - It continues to represent thinking stance (abstract/concrete, acting/reflecting, etc.).
   - Over time, we may make it optional, but this ADR does not require that change.

5. Make the combination logic explicit, composable, and non-competing:
   - The pipeline will build the user prompt out of:
     - Goal / static prompt (a short, canonical key expanded into a richer description for the model).
     - `goalModifier`
     - `directionalModifier` (lens)
     - Zero or more of: `completenessModifier`, `methodModifier`, `scopeModifier`, `styleModifier`
     - System prompt built from `model_default_*` plus any `gpt_set_system_prompt` overrides
   - For each axis, compute a single `effective_<axis>` value per request using strict precedence:
     1. Spoken modifier (if present).
     2. Per-prompt profile value for that axis (if defined).
     3. Global default setting for that axis.
   - The effective axis values are surfaced to the model via `GPTSystemPrompt` lines (`Completeness`, `Scope`, `Method`, `Style`), while the user-level prompt shows the static prompt’s canonical key expanded into a human-readable description (for example, “gherkin” → “Reformat this into proper Gherkin using Jira markup; output only the reformatted Gherkin with no surrounding explanation.”).

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
  - `rewrite:` Rewrite or refactor while preserving the original intent; treat this as a mostly mechanical transform.
  - `diagnose:` Look for likely causes of problems first; narrow down hypotheses before proposing fixes.

- `scopeModifier` (**conceptual scope rather than text region**):
  - `narrow:` Restrict discussion to a very small slice of the topic within the voice-selected target.
  - `focus:` Stay tightly on a central theme within the target; avoid tangents and side-quests.
  - `bound:` Stay inside explicit limits inferred from or stated in the prompt; do not introduce material outside them.
  - `edges:` Emphasise edge cases, errors, and unusual conditions around the subject.

- `styleModifier`:
  - `plain:` Use straightforward, everyday language; minimise jargon.
  - `tight:` Make the answer short and dense; no fluff.
  - `bullets:` Present the main answer as concise bullet points.
  - `table:` Present the main answer as a Markdown table when feasible.
  - `code:` Present the main answer primarily as code or markup, with minimal prose.

These values are designed to be short, punchy utterances that can be spoken reliably and combined with static prompts and directional lenses.

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

#### Examples: using completeness and scope together

Concrete examples from the “Task / Constraints” pattern help keep completeness and scope distinct:

- Software documentation:
  - Scope: “only the error-handling paths in the checkout flow”.
  - Completeness: from “mention a couple of major paths” (skim) up to “list every error-handling path that exists” (full).
- Debugging:
  - Scope: “investigate only `renderPage()`”.
  - Completeness: from “highlight a few likely issues” (skim) up to “walk every branch, mutation, side effect, and external call” (full).
- Conceptual study (for example, biology):
  - Scope: “only the circulatory system”.
  - Completeness: from “big idea of how it works” (gist) up to “cover every relevant component and regulation mechanism” (full).

These examples are meant as intuition pumps: scope picks the fenced area; completeness decides how densely you fill it.

#### Constraint categories and example adjectives

In practice, natural-language adjectives tend to fall into four functional “layers” that line up with these axes, even when the concrete spoken tokens in `GPT/lists` are different:

- **Style constraints** – tone, brevity, and density:
  - Words like `light`, `simple`, `small`, `compact`, `moderate` mostly affect how something is said, not what is allowed to be said (they are cousins of `plain`, `tight`, and the style-related static prompts).
- **Scope constraints** – territory and boundaries:
  - Words like `narrow`, `focused`, `targeted`, `bounded`, `comprehensive` decide what area is in‑bounds, conceptually relative to whatever text or object the voice command already targeted (for example, “within this function”, “within this error-handling path”, “within this snippet”).
- **Method constraints** – reasoning approach:
  - Words like `rigorous`, `deep` change how the model thinks and structures the answer (similar in spirit to spoken method modifiers like `steps` and `plan` when they are used as method flags).
- **Completeness constraints** – inclusion requirements:
  - Words like `detailed`, `thorough`, `exhaustive` say how much of the relevant domain must appear (they occupy the same end of the axis as `full`/`max` versus `skim`/`gist`).

These adjectives are not all wired in as spoken `*Modifier` values; they are a conceptual vocabulary for understanding how different free‑form instructions map onto the four contract-style axes and onto the existing concrete lists.

Some adjectives can straddle layers (for example, “detailed” can be style or completeness; “focused” can be scope or method). When in doubt, the higher-impact interpretation wins: “detailed” is treated as completeness before style; “focused” is treated as scope before method; “rigorous” is treated as method before style.

#### Constraint dominance and conflict resolution

When multiple constraint words are present in a single prompt (whether spoken modifiers, free‑form adjectives, or both), the effective behaviour is guided by how much each word shrinks the space of valid outputs. Empirically:

- **Completeness dominates**:
  - High‑completeness terms (“full”, “max”, or natural‑language cousins like `exhaustive` / `thorough` / `detailed`) override brevity and most style/method nudges.
  - For example, “simple but exhaustive” means exhaustive coverage, expressed as simply as possible.
- **Method overrides style, competes with scope**:
  - Method terms (`steps`, `plan`, `rigor`/`rigorous`, `deep`) reshape internal reasoning and outweigh style terms like `simple` or `light`.
  - With hard scope (for example, “bounded and deep”), the resolution is “deep reasoning inside the boundary”.
- **Hard scope dominates style and soft scope**:
  - Hard scope terms (`bound`/`bounded`, “only X”, “exclude Y`) dominate style terms; softer scope words like “focused” or “narrow” sit below explicit bounds.
  - Relational scope terms (for example, `relations`) narrow the territory further to how elements connect (“only relationships and interaction patterns among these parts”).
  - For example, “simple but bounded” means stay inside the boundary; simplicity only affects wording.
- **Style never wins on its own**:
  - Style terms (`plain`, `tight`, `bullets`, or free‑form adjectives like `simple`, `small`, `compact`, `light`, `moderate`) only shape presentation; they yield whenever they clash with scope, method, or completeness requirements.

A useful mental “tie‑breaker ladder” for mixed adjectives is to think in terms of axes, not specific spellings:

> completeness axis (for example, `full` / `max` / “exhaustive`)  
> > method axis (for example, `steps` / `plan` / “rigorous” / “deep` / `filter` / `prioritize` / `cluster`)  
> > hard scope axis (for example, “bounded to X” or “only within this selection”)  
> > style axis (for example, `plain` / `tight` / `bullets` / “simple` / `compact` / `checklist`).

This ladder is descriptive, not prescriptive: it does not change the `effective_<axis>` precedence rules earlier in this ADR, but it captures how layered constraints typically behave when interpreted by the model and is intended as a guide when designing new spoken modifiers, per-prompt profiles, or static prompts.

### New default settings (persistent)

Add Talon settings analogous to existing ones:

- `model_default_completeness` (string; for example, `"skim"`, `"gist"`, `"full"`, `"max"`)
- `model_default_scope` (string; for example, `"narrow"`, `"focus"`, `"bound"`, `"relations"`; recommended default is empty for no implicit scope bias)
- `model_default_method` (string; for example, `"steps"`, `"plan"`, `"filter"`, `"prioritize"`, or `"cluster"`)
- `model_default_style` (string; for example, `"plain"`, `"bullets"`, `"code"`, `"checklist"`)

These will be:

- Used by `GPTSystemPrompt` when no effective per-request value is supplied.
- Overridable via voice commands similar to `model write as programmer`, for example:
  - `model set completeness skim`
  - `model set scope narrow`
  - `model set method steps`
  - `model set style bullets`

### How the pieces interact

- Baseline behavior:
  - The system prompt incorporates `model_default_voice`, `model_default_audience`, `model_default_purpose`, `model_default_tone`, and the four contract-style axes (completeness, scope, method, style). For each axis, `modelPrompt` computes an effective value (spoken modifier > per-prompt profile > `user.model_default_*`) and writes it into `GPTState.system_prompt` before the request is built.
  - `modelPrompt` also builds a user-level `Task / Constraints` schema. The `Task` line contains the static prompt plus any goal modifier; the `Constraints` block contains any spoken modifiers and, where present, short per-prompt profile hints for completeness, scope, method, and style. Pure global defaults need not be repeated here, since they are already reflected in the system prompt lines.
  - If the user just says `model fix fog`, the response uses the effective axes in the system prompt (`Completeness: full`, `Scope: narrow`, and so on, based on the `fix` profile and global defaults), plus the profile-level completeness/scope hints for `fix` in the user prompt’s `Constraints` block. The directional lens (`fog`) is appended after the schema.

- Per-prompt overrides:
  - If the user says:
    - `model fix skim steps plain fog`
  - Then:
    - The `Task` line is still `fix` + any goal modifiers.
    - The `Constraints` block contains explicit lines for:
      - `Completeness: skim`
      - `Method: steps`
      - `Style: plain`
    - Any profile values for those axes are suppressed for that call; the directional lens (`fog`) remains a separate instruction appended after the schema.

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

The core design for ADR 005 is implemented and stable in this repo. Remaining work is optional refinement rather than required behaviour change. Useful future directions include:

1. Refine modifier vocabularies in practice:
   - Focus on the small subset you actually speak day to day (for example, `skim`/`gist`/`full`, `steps`, `plain`/`bullets`/`code`).
   - Trim, rename, or deprecate rarely used values over time to keep lists discoverable.
2. Evolve optional per-static-prompt profiles:
   - Add or tweak axis defaults in `STATIC_PROMPT_CONFIG` only where a prompt’s intent clearly implies a particular completeness/scope/method/style bias.
   - Keep to the precedence rules (`spoken > profile > user.model_default_*`) and avoid surprising hidden defaults.
3. Extend tests and tooling as new behaviours are introduced:
   - When adding new profiles or axes, expand focused tests for `modelPrompt` composition and default/override precedence.
   - Keep `gpt_help` and `GPT/readme.md` examples in sync with any vocabulary or profile changes.
4. Explore profile or mode experiments:
   - Optionally introduce a temporary “beta profile” or `model beta` command to trial alternative interpretations of these axes without disturbing the main `model` behaviour, promoting successful patterns into the primary flow once they stabilise.

## Current Status (this repo)

- Completeness, scope, method, and style modifier lists exist under `GPT/lists` and are registered as Talon lists:
  - `completenessModifier` (`skim`, `gist`, `full`, `max`, `minimal`, `deep`)
  - `scopeModifier` (`narrow`, `focus`, `bound`, `edges`)
  - `methodModifier` (`steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`)
  - `styleModifier` (`plain`, `tight`, `bullets`, `table`, `code`, `checklist`)
- The `modelPrompt` capture rule accepts these axes as optional modifiers (in the order: completeness, scope, method, style) before the required `directionalModifier`.
- `modelPrompt`:
  - Computes effective completeness/scope/method/style per request (spoken modifier > per-static-prompt profile > `user.model_default_*`).
  - Writes these effective values into `GPTState.system_prompt` so `GPTSystemPrompt.format_as_array()` exposes them as `Completeness`, `Scope`, `Method`, and `Style` lines.
  - Returns a `Task / Constraints` schema as the user prompt, with the static prompt and goal on the `Task` line and any spoken/profile constraints listed under `Constraints:`.
- A single per-static-prompt configuration map is active in code (`STATIC_PROMPT_CONFIG` in `lib/staticPromptConfig.py`, consumed by `lib/talonSettings.py`). For selected prompts, it configures both description and axis defaults. For example:
  - `fix` configures `{ description: "...", completeness: "full", scope: "narrow" }`.
  - `todo` configures `{ description: "...", completeness: "gist", method: "steps", style: "checklist", scope: "focus" }`.
  - `bridge` configures `{ description: "...", completeness: "full", method: "steps", scope: "focus" }`.
  - `diagram` configures `{ description: "...", completeness: "gist", scope: "focus", style: "code" }`.
  - `HTML` configures `{ description: "...", completeness: "full", scope: "bound", style: "code" }`.
  - `gherkin` configures `{ description: "...", completeness: "full", scope: "bound", style: "code" }`.
  - `shell` configures `{ description: "...", completeness: "full", scope: "bound", style: "code" }`.
  - `commit` configures `{ description: "...", completeness: "gist", scope: "bound", style: "plain" }`.
  - `ADR` configures `{ description: "...", completeness: "full", method: "rigor", scope: "focus", style: "plain" }`.
- The `gpt_help` command renders help tables for static prompts, directional modifiers, goal modifiers, voice/tone/audience/purpose, and all four new modifier axes.
- Focused tests exist for:
  - `modelPrompt` composition across completeness/scope/method/style.
  - `GPTSystemPrompt` use of the new contract-style axes and Talon defaults.

### How to run the relevant tests

- From the repo root, with Python 3 and `pytest` installed, run:
  - `python3 -m pytest -q tests/test_talon_settings_model_prompt.py tests/test_model_types_system_prompt.py`
- These tests:
  - Exercise `modelPrompt` composition for completeness/scope/method/style.
  - Verify that `GPTSystemPrompt` reads the `user.model_default_*` settings for the new axes.

## Practical usage tips

## Practical usage tips

- Start simple:
  - Rely on `user.model_default_completeness` and speak completeness modifiers only when you want something clearly different (for example, `skim` for a quick pass or `full` for a thorough one).
  - Use at most one or two spoken modifiers per `model` command until the axes feel natural.
- Prefer scope + method as your primary knobs:
  - Keep `model_default_scope` empty for most day-to-day use so scope stays tied to whatever you selected or targeted with the voice command; speak conceptual scopes like `narrow`, `focus`, or `bound` only when you want to tighten or harden that conceptual territory.
  - Method modifiers like `steps` or `plan` are a good default mental model tweak without overloading the prompt.
- Treat style as output formatting, not semantics:
  - Use `bullets` or `table` when you care mainly about how the answer is laid out.
  - Use `code` only when you truly want “code only, no explanation”.
- Use voice commands to shift modes:
  - `model set completeness skim` / `model reset completeness`.
  - `model set scope narrow` / `model reset scope`.
  - `model set method steps` / `model reset method`.
  - `model set style bullets` / `model reset style`.
 - When using overloaded adjectives in free‑form prompts, prefer explicit typing to reduce ambiguity:
   - For example, use a mini‑spec:
     - `Task: …`
     - `Constraints:`
     - `  Completeness: thorough`
     - `  Method: rigorous`
     - `  Scope: bounded to X`
     - `  Style: simple`
   - Or prefix lines like `Scope: focused on error-handling only`, `Method: deep analysis`, `Style: compact`. This makes it obvious which contract-style axis each word is meant to affect.
