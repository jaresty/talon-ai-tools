# 019 – Meta-Interpretation Channel and Surfaces

- Status: Accepted  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT integration (`model` commands)
- See also:
  - `docs/adr/002-prompt-session-and-presentation.md`
  - `docs/adr/006-pattern-picker-and-recap.md`
  - `docs/adr/009-rerun-last-recipe-shorthand.md`

## Context

Many users run with a richer system prompt that asks the model to:

- Produce a **primary answer** (what should actually be pasted / applied), and
- Append a short **meta-interpretation** describing how the model understood the request, what assumptions it made, or how it chose a particular pattern.

Today, this meta-interpretation is:

- Embedded directly in the same text block as the answer.
- Routed identically through all destinations (confirmation GUI, paste, browser, etc.).
- Not addressable as its own “thing” via the `model` source/destination grammar.

This leads to a few problems:

- **Pasting friction** – when you paste, you often get both the answer and the trailing meta commentary, even though you only wanted the answer.
- **Visibility gaps** – the meta is not visible on **recap surfaces** that otherwise help you understand what happened:
  - Confirmation GUI `Recipe:` line.
  - Quick help last-recipe recap.
  - Browser view that already carries recipe / grammar hints.
- **No way to re-route meta** – there is no `meta` model source you can send to another destination on demand (for example, “stick the last interpretation into the thread”, or “open it in the browser for review”).

We want to treat the interpretation as a **first-class meta channel**:

- Separable from the main answer, especially for pasting.
- Visible alongside the last recipe on recap surfaces.
- Addressable via the same `model` source/destination grammar used elsewhere.

## Decision

We will introduce a **meta-interpretation channel** with three main properties:

1. **Answer vs. meta split**
   - When a prompt run completes, we will split the model’s first text response into:
     - `answer_text` – the main content users typically want to paste.
     - `meta_text` – an optional trailing interpretation of the request.
   - The split will be based on a **simple structural heuristic** (for example, a trailing section headed `Model interpretation`, or a dedicated delimiter string) that can be aligned with the system prompt.

2. **First-class state and source**
   - We will add a `GPTState.last_meta` field (and related reset plumbing) that stores the most recent `meta_text`.
   - We will expose a new `Meta` model source so users can **send the meta to any destination** using the existing grammar, e.g.:
     - `model meta to browser`
     - `model meta to context`
     - `model meta to query`

3. **Recap surfaces show meta near the last recipe**
   - The meta-interpretation will be surfaced **close to where we already recap the last recipe**, so users can see:
     - What recipe was run (`staticPrompt · axes · directional`).
     - How the model says it interpreted the request.
   - Concretely:
     - **Confirmation GUI** – show a short “Meta:” line beneath the `Recipe:` line when `last_meta` is present (possibly truncated).
     - **Quick help** – in the “Last recipe” section, add an optional “Model interpretation” snippet when `last_meta` is available.
     - **Browser destination** – add a “Model interpretation” section near the recipe recap, separate from the main response body.

The core rule is:

> **Destinations treat meta as secondary, non-pasteable context by default**, while still making it easy to inspect and route via the `meta` source when desired.

## Design

### 1. State and representation

Extend `GPTState` with a dedicated meta field:

- `last_meta: str` – the most recent meta-interpretation text (empty string when none).

Plumbing:

- Initialise `last_meta` to `""`.
- Reset it to `""` in:
  - `GPTState.clear_all`
  - `GPTState.reset_all`
- Optionally add a lightweight helper:
  - `GPTState.clear_meta()` for explicit meta resets, if needed later.

### 2. Answer / meta splitting

We keep the existing `PromptResult` and `ResponsePresentation` types, but change how we feed them:

1. Introduce a helper (in `promptPipeline` or a nearby utility) to split a raw text response:

   - `split_answer_and_meta(text: str) -> (answer: str, meta: str)`
   - Default behaviour:
     - If no obvious delimiter / heading is present, treat the whole text as `answer` and `meta == ""`.
   - When the system prompt consistently appends a marked meta section (for example, a trailing `## Model interpretation` heading or a `--- META ---` delimiter), we parse that into `meta`.

2. Apply the splitter in the prompt pipeline:

   - After `PromptSession.execute()` returns the first text message, but before we assemble `ResponsePresentation`:
     - Compute `(answer_text, meta_text) = split_answer_and_meta(first_text)`.
     - Store `meta_text` in `GPTState.last_meta`.
     - Use `answer_text` as the **primary content** for destinations that care about what gets pasted.

3. Extend `ResponsePresentation` with an optional meta field:

   - `meta_text: str = ""`
   - For now:
     - `paste_text` should be derived from `answer_text` only.
     - `display_text` and `browser_lines` may continue to include the full combined text or be adjusted case-by-case as surfaces become more meta-aware.

### 3. Meta as a first-class model source

Add a new source type to `modelSource.py`:

- `class Meta(ModelSource):`
  - `get_text` returns `GPTState.last_meta`.
  - On empty meta, either:
    - Notify and raise (like `GPTResponse` when no response exists), or
    - Return an empty string; the former is likely more user-friendly.

Wire it into `create_model_source`:

- Add a `"meta": Meta` entry in the `source_map`.
- As with other sources, tag the instance with `modelSimpleSource = "meta"` for downstream flows.

Expose it via the Talon list:

- In `GPT/lists/modelSource.talon-list`, add:

  - A human-friendly key, for example:
    - `meta: meta`
    - `interpretation: meta`
  - This allows commands like:
    - `model meta to browser`
    - `model meta to context`

This makes meta routable to any existing destination without adding new destination types.

### 4. Recap and UI surfaces

We will treat `last_meta` as a **radar-style complement** to the last-recipe recap:

1. **Confirmation GUI (`lib/modelConfirmationGUI.py`)**
   - Beneath the `Recipe:` line, when `GPTState.last_meta` is non-empty:
     - Show a compact “Meta:” line, e.g.:
       - `Meta: <first N characters of last_meta>…`
     - Consider keeping this inside the existing “advanced actions” / expandable region if vertical space becomes a concern.
   - This keeps the modal as the primary in-flow recap surface for both recipe and interpretation, without polluting the paste text.

2. **Quick help GUI (`lib/modelHelpGUI.py`)**
   - In the “Last recipe” section (when `GPTState.last_recipe` is present and `HelpGUIState.static_prompt` is not set):
     - If `GPTState.last_meta` is non-empty, show:
       - A “Model interpretation” header.
       - A short preview or first line of `last_meta`.
   - This gives a **discoverable, low-churn** place to read the model’s own explanation of what it thought you asked, alongside the exact `model …` line you can repeat.

3. **Browser destination (`lib/modelDestination.Browser`)**
   - We already prepend:
     - A heading (“Talon GPT Result”).
     - A `Recipe:` line and `Say: model …` grammar phrase.
     - A recap tip around `model show grammar` and `model pattern menu`.
   - When `GPTState.last_meta` is non-empty, also include:
     - A “Model interpretation” subheading.
     - The full `last_meta` text, separated clearly from the main response.
   - The main response content continues to be rendered from `presentation.browser_lines` (answer text), so meta remains **visible but logically separate**.

4. **Non-goals (for now)**

- We will not:
  - Persist multiple meta entries across threads / history; only **last-meta** is tracked.
  - Attempt to automatically rewrite arbitrary system prompts to conform to a specific meta delimiter; we will document a recommended structure instead.
  - Introduce separate per-destination toggles for showing/hiding meta; first iteration keeps the UX simple.

## Consequences

Positive:

- **Cleaner pastes** – destinations that rely on `paste_text` use only `answer_text`, avoiding accidental inclusion of meta commentary in user documents.
- **Richer recaps** – the confirmation GUI, quick help, and browser surfaces now give:
  - A concise recipe recap (as before).
  - The model’s own explanation of how it interpreted the request.
- **Composability** – the `meta` source can be combined with any existing destination:
  - Users can quickly ship meta to context, thread, clipboard, browser, etc.

Trade-offs / risks:

- **Heuristic parsing** – unless the system prompt uses a very regular delimiter for the meta section, the splitter may occasionally misclassify content. We can mitigate this by:
  - Documenting a recommended structure for meta sections.
  - Making the parsing rule explicit and conservative.
- **Slightly more state** – `GPTState` grows another field; we must be careful to keep it in sync across resets and thread operations.
- **Incremental UI changes** – each surface (confirmation GUI, quick help, browser) needs small, coordinated tweaks to show meta without overwhelming the UI.

### Current status in this repo

For the `talon-ai-tools` integration, the core ADR objectives are implemented:

- `GPTState.last_meta`, `split_answer_and_meta`, and `ResponsePresentation.meta_text` are in place and wired so that:
  - The main answer (before the meta heading) is what gets pasted and threaded.
  - The trailing interpretation section is treated as non-pasteable meta.
- A `Meta` model source (`model meta …`) exposes `last_meta` to any destination.
- Recap surfaces all show meta alongside the last recipe when available:
  - Confirmation GUI: `Meta: …` preview under the `Recipe:` line.
  - Quick help: “Model interpretation” preview in the “Last recipe” section.
  - Browser: a “Model interpretation” section above the main “Response”.
- A small helper, `model last meta`, surfaces the last interpretation in a notification.

Remaining ideas under “Iterate based on usage” (per-surface toggles, longer-meta affordances, history-aware meta navigation) are explicitly treated as optional future refinements rather than required by this ADR.

## Next Steps

1. **Define and document the meta delimiter**
   - Decide on the preferred delimiter / heading for meta sections (for example, a trailing `## Model interpretation` heading or `--- META ---` block).
   - Update the default system prompt (or docs) to encourage this structure.

2. **Implement state and splitting**
   - Add `GPTState.last_meta` and wire it into `clear_all` / `reset_all`.
   - Implement `split_answer_and_meta` and call it from the prompt pipeline.
   - Extend `ResponsePresentation` to include `meta_text`, and ensure `paste_text` uses only `answer_text`.

3. **Expose the `meta` source**
   - Add the `Meta` model source and wire it into `create_model_source`.
   - Update `GPT/lists/modelSource.talon-list` with a human-friendly key (for example, `meta: meta`).
   - Add focused tests for:
     - Empty vs. non-empty `last_meta`.
     - Error behaviour when `meta` is requested but missing.

4. **Update recap surfaces**
   - Confirmation GUI:
     - Show a concise “Meta:” line when `last_meta` exists.
   - Quick help GUI:
     - Add a “Model interpretation” preview next to the last recipe.
   - Browser destination:
     - Add a “Model interpretation” section using `GPTState.last_meta`.
   - Add tests / snapshots where feasible to keep the behaviour stable.

5. **Iterate based on usage**

   - If meta proves noisy, consider:
     - A toggle to hide/show meta in specific surfaces.
     - Truncation / “Show more” affordances for very long meta sections.
   - If multiple meta entries per thread become useful, consider a future ADR for history-aware meta navigation.
