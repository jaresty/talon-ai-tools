# 020 – Richer Meta Interpretation Structure

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT integration (`model` commands), building on ADR 019
- See also:
  - `docs/adr/019-meta-interpretation-channel-and-surfaces.md`
  - `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
  - `docs/adr/006-pattern-picker-and-recap.md`

## Context

ADR 019 introduces a **meta-interpretation channel**:

- `last_meta` stores a trailing explanation of how the model interpreted the request.
- `split_answer_and_meta` splits main answer vs. meta based on a trailing `## Model interpretation` heading.
- A `Meta` model source and recap surfaces (confirmation GUI, quick help, browser) expose this interpretation without polluting paste text.

Today, the meta content is largely **unstructured free text**. In practice, several recurring questions come up after a response:

- *“What assumptions did the model make?”*
- *“What should I double-check or adapt?”*
- *“How could I phrase this better next time?”*
- *“Given this grammar, what axis tweak would you recommend?”*

Right now, users have to infer these from the answer (or from ad-hoc meta the system prompt might ask for), and there is no standard format that:

- Keeps the main answer clean.
- Provides a compact, structured set of **post-hoc diagnostics**.
- Fits naturally with the existing axis/recipe grammar.

We want the meta channel to carry a **small, structured bundle of diagnostics** that can be:

- Skimmed quickly by humans.
- Optionally parsed or reused in future iterations.
- Kept out of paste destinations by default.

## Decision

We will extend the meta channel into a **structured interpretation bundle** with standard subsections, all still treated as non-pasteable metadata:

1. **Model interpretation (required)**
   - Short plaintext explanation of how the model understood the request and chose its approach.
   - Already present conceptually via ADR 019’s `## Model interpretation` block.

2. **Assumptions (optional)**
   - 2–4 short bullets capturing key assumptions and inferred constraints.

3. **Gaps and checks (optional)**
   - 1–3 bullets listing:
     - Major gaps in information.
     - Concrete things the user should double-check or adapt.

4. **Better prompt (optional but encouraged)**
   - A single, improved version of the user’s request, in one or two sentences.
   - Expressed as a direct prompt the user could reuse next time.

5. **Axis tweak suggestion (optional)**
   - A compact recommendation for how to adjust the recipe next time, expressed in the same axis token language as the rest of the system, for example:
     - `Suggestion: completeness=gist`
     - `Suggestion: scope=focus`
     - `Suggestion: style=bullets`

All of these live **inside the meta section** and must not change paste behaviour:

- The main answer continues to be what is pasted and threaded.
- The meta bundle is visible via recap surfaces and routable via the `meta` source.

## Design

### 1. Meta section structure

We will standardise on a **single meta block** anchored by the existing heading:

- After the main answer, the model emits:

  - `## Model interpretation`  
    *(short paragraph)*
  - `### Assumptions`  
    `- …`  
    `- …`  
  - `### Gaps and checks`  
    `- …`  
    `- …`  
  - `### Better prompt`  
    *(one improved prompt sentence or two)*  
  - `### Axis tweak suggestion`  
    `Suggestion: <axis>=<token>`

Notes:

- All subsections after `## Model interpretation` are **optional**; the model should emit them when they are helpful, but the client must tolerate their absence.
- The existing splitter continues to detect the meta block by the first heading containing “interpretation”; everything that follows, including `### …` subheadings, remains part of `meta_text`.
- Recap surfaces remain conservative:
  - Confirmation GUI and quick help show only the interpretation preview (first line) to avoid clutter.
  - Browser and `meta` source surfaces can show the full structured meta.

### 2. System prompt guidance

We will update the **default system prompt** to:

1. Reiterate the main-answer requirements:
   - Output just the response to the request as the primary answer.
   - Avoid markdown in the main answer unless explicitly requested (except where style/method axes intentionally demand it).
2. Add explicit instructions for the meta bundle:
   - After the main answer, append a structured meta section beginning with `## Model interpretation`.
   - Within that section:
     - Briefly explain how you interpreted the request and why you chose your approach.
     - List key assumptions and constraints as short bullets.
     - Call out major gaps/caveats and up to three things the user should verify.
     - Propose one improved version of the original prompt.
     - Optionally suggest a single axis tweak in `Suggestion: <axis>=<token>` form.

This prompt lives in configuration (`user.model_system_prompt` default) so advanced users can opt out, but the **recommended** behaviour for this repo is to include the structured meta section.

### 3. Surfaces and parsing

No new parsing logic is required:

- `split_answer_and_meta` already:
  - Treats everything before the `## Model interpretation` heading as the main answer.
  - Treats the heading and all subsequent content as meta.
- Recap surfaces:
  - Continue to show only:
    - `Meta:` preview (confirmation GUI).
    - “Model interpretation” preview (quick help).
    - A full “Model interpretation” section (browser).
  - These previews do not need to know about the subheadings; they simply show the beginning of the meta block.

Optional future work (outside this ADR) might:

- Parse `Suggestion: <axis>=<token>` for tighter axis-aware helpers.
- Extract the “Better prompt” for reuse by a dedicated command.

## Consequences

Positive:

- **Richer diagnostics without polluting pastes**
  - Users get a compact bundle of:
    - Interpretation.
    - Assumptions and gaps.
    - Better prompt.
    - Optional axis tweak suggestion.
  - All live in meta-only space, never in `paste_text`.

- **Better iteration affordances**
  - The “Better prompt” and axis tweak suggestion give users:
    - A clear, reusable prompt they can refine.
    - A concrete axis token they can try next (`model again gist fog`, etc.).

- **Aligned with existing grammar**
  - The axis suggestion uses the same token language as ADR 005/006/009:
    - Makes it easy to map meta recommendations back into recipe tokens.

Trade-offs:

- **Longer responses** – Including diagnostics increases token count. The timeout guidance and existing “concise” framing should keep this manageable, but some users may wish to trim meta in their own system prompt.
- **Prompt complexity** – The default system prompt becomes more complex. We mitigate this by:
  - Keeping the main-answer instructions distinct from the meta bundle.
  - Making all sub-sections after “Model interpretation” optional.

## Next Steps

1. **Update default system prompt**
   - Extend `user.model_system_prompt`’s default in `lib/talonSettings.py` to:
     - Keep main-answer constraints.
     - Add explicit instructions for the `## Model interpretation` meta block and its subsections.
   - Keep the wording concise and robust enough to handle non-LLM backends.

2. **Document the richer meta structure**
   - Update `GPT/readme.md` “Meta interpretation channel (ADR 019)” to:
     - Describe the new subsections (Assumptions, Gaps and checks, Better prompt, Axis tweak suggestion).
     - Make it clear they all live inside the meta block and are not pasted.

3. **(Optional) Add light tests**
   - Given that the structure is enforced via prompts, not parsing:
     - No direct parsing changes are required for this ADR.
     - It may still be useful to add a small “contract” test that asserts:
       - The default `model_system_prompt` string mentions `## Model interpretation`.
       - It instructs the model to include assumptions/gaps/better prompt/axis suggestion in that section.

