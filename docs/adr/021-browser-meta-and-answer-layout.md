# 021 – Browser Meta and Answer Layout

- Status: Proposed  
- Date: 2025-12-05  
- Context: `talon-ai-tools` GPT integration (`model … to browser`)
- See also:
  - `docs/adr/019-meta-interpretation-channel-and-surfaces.md`
  - `docs/adr/020-richer-meta-interpretation-structure.md`
  - `docs/adr/006-pattern-picker-and-recap.md`

## Context

ADRs 019 and 020 introduce a structured meta channel:

- Responses are split into:
  - A primary **answer** (pasteable).
  - A trailing **meta** section headed by `## Model interpretation`, which may include:
    - Interpretation.
    - Assumptions.
    - Gaps/checks.
    - A “better prompt”.
    - An axis tweak suggestion.
- The meta portion is:
  - Stored as `last_meta`.
  - Exposed via a `meta` source and recap surfaces.
  - Explicitly non-pasteable by default.

The browser destination currently:

- Shows:
  - A heading (`Talon GPT Result`).
  - A prompt recap (recipe, speakable `model …` line, tip).
  - A “Model interpretation” section that simply dumps the meta block as paragraphs.
  - A “Response” section that prints each answer line as a paragraph.
- Treats meta as plain text; headings, labelled sections, and bullets are not rendered as such.

In practice, this leads to:

- **Noisy meta headings** – when the model emits a line like:
  - `## Model interpretation - Interpretation: …`
  the browser shows the raw `##` prefix and a mashed-together heading + sentence.
- **Flattened structure** – bullets and labelled subsections (assumptions, gaps, etc.) appear as long in-line sentences rather than scannable lists.
- **Weak separation between meta and answer** – the “Model interpretation” and “Response” sections have the same visual weight; it’s not obvious which is for inspection vs. which is safe to paste.
- **No strong cue about non-pasteable meta** – nothing in the browser view reminds users that the top section is diagnostic and that only the answer is used by paste destinations.

We want the browser destination to become a **first-class inspection surface**:

- Clear, scannable layout for both meta and answer.
- Strong visual separation between diagnostic meta and pasteable answer.
- Better alignment with the structured meta contract from ADR 020.

## Decision

We will refactor the browser destination layout into three clearly structured sections:

1. **Prompt recap**
   - A compact summary of:
     - Last recipe tokens.
     - The exact `model …` line.
     - A short tip for further exploration (grammar help, pattern menu).

2. **Model interpretation (diagnostic, non-pasteable)**
   - A structured rendering of the meta bundle, when available, with:
     - Interpretation.
     - Assumptions/constraints.
     - Gaps/caveats to verify.
     - Better prompt.
     - Axis tweak suggestion.
   - Rendered with headings and bullet lists where appropriate.
   - Clearly marked as diagnostic and non-pasteable.

3. **Response (primary answer)**
   - A more ergonomic rendering of the answer text:
     - Paragraph-aware.
     - Bullets rendered as bullet lists where feasible.
   - Clearly indicated as the section to read and copy from when pasting manually.

The browser destination will remain **read-only**—it will not change what gets pasted anywhere—but will become a more faithful, ergonomic representation of both meta and answer structure.

## Design

### 1. Section structure and headings

The browser view will use the following HTML structure (via `HTMLBuilder`):

- `h1("Talon GPT Result")`
- `h2("Prompt recap")` (if `GPTState.last_recipe` is present)
  - `p("Recipe: <tokens>")`
  - `p("Say: model …")`
  - `p("Tip: …")`
- `h2("Model interpretation")` (if meta exists)
  - Interpretation paragraph.
  - `h3("Assumptions/constraints")` + bullet list (if any).
  - `h3("Gaps and checks")` + bullet list (if any).
  - `h3("Better prompt")` + a single paragraph.
  - `h3("Axis tweak suggestion")` + one line.
  - A short note, e.g.:
    - `p("Note: This section is diagnostic and is not pasted into documents.")`
- `h2("Response")`
  - Rendered paragraphs and bullet lists derived from the answer text.

### 2. Meta parsing and rendering

We will add a small, **defensive meta parser** that operates on `meta_text`:

- Input: the full meta string, as emitted by the model.
- Output: a simple structure, e.g.:

  ```python
  {
    "interpretation": "…",
    "assumptions": ["…", "…"],
    "gaps": ["…", "…"],
    "better_prompt": "…",
    "suggestion": "Scope=focus",  # or similar
    "raw_lines": [...],  # fallback
  }
  ```

Parsing rules:

- Consider any line starting with `#` (after optional whitespace) to be a **heading marker** and strip the `#` prefix and surrounding whitespace.
- Recognise the following labels (case-insensitive), either at the start of a line or immediately after a heading:
  - `Interpretation:`
  - `Assumptions:` / `Assumptions/constraints:`
  - `Gaps:` / `Gaps/caveats:` / `Gaps/caveats to verify:`
  - `Improved prompt:` / `Better prompt:`
  - `Suggestion:` (captures the rest of the line)
- Treat subsequent `-`-prefixed lines under an “Assumptions” or “Gaps” label as bullets.
- Any unclassified content falls back into:
  - Interpretation (when early in the meta block), or
  - A generic “Additional notes” paragraph.

Rendering rules:

- Interpretation:
  - One or two paragraphs, rendered at the top of the “Model interpretation” section.
- Assumptions / Gaps:
  - When bullets are present, render them via `builder.ul()` for readability.
  - When only a label + inline text exists, render as a simple paragraph.
- Better prompt:
  - Render as a single paragraph (no bullets).
  - Optionally use a monospace or quoted style if we later extend `HTMLBuilder` for that.
- Suggestion:
  - Render the suggestion text as-is, but **do not attempt to interpret it programmatically in this ADR**.
  - If the suggestion clearly matches the `<axis>=<token>` pattern, label it explicitly in the UI (for example, `Axis tweak: scope=focus`).

The parser must be conservative:

- If any structural elements are missing or malformed, fall back to emitting a simple set of paragraphs under “Model interpretation”, as we do today, rather than failing or dropping content.

### 3. Answer rendering

For the primary answer (the content of `presentation.browser_lines`):

- Continue to treat the answer as **pasteable text only**; the browser is purely a view.
- Improve ergonomics by:
  - Grouping contiguous non-empty lines into paragraphs.
  - Recognising simple bullet patterns:
    - Lines starting with `- ` or `* ` (after optional indentation).
  - When a sequence of bullet-style lines occurs:
    - Render them via `builder.ul()` rather than individual paragraphs.
  - Avoid collapsing multiple bullets into a single paragraph; preserve the list semantics when obvious.

This should make long answers with bullet-heavy structure (checklists, step-by-step instructions) much easier to scan and use.

### 4. Visual separation and cues

To reinforce the semantics:

- Meta vs. Answer:
  - Keep them in separate `h2` sections.
  - Add a note under “Model interpretation”, for example:
    - `p("Note: This section is diagnostic and is not pasted into documents; use the Response section below for copy/paste.")`
- Prompt recap vs. Meta:
  - “Prompt recap” is intentionally compact; avoid heavy text there so the user’s eye is drawn to:
    - Interpretation (why the model did what it did).
    - Response (what the user should do).

## Consequences

Positive:

- **Better meta readability**:
  - Interpretation, assumptions, gaps, better prompt, and suggestion are presented in a structured, skimmable way.
- **Clearer answer layout**:
  - Bullets render as bullets, not inline dashes.
  - Paragraphs are grouped sensibly, making longer answers more approachable.
- **Stronger separation of concerns**:
  - Meta is clearly diagnostic and non-pasteable.
  - Answer is the section users copy from when working outside Talon.

Trade-offs:

- **Additional parsing complexity**:
  - The meta parser introduces new logic that must be kept robust against imperfect model outputs.
  - We mitigate this by:
    - Using conservative pattern matching.
    - Falling back to simple paragraph rendering when we cannot confidently structure the meta.
- **Slightly more HTML structure**:
  - The `Browser` destination’s implementation grows to handle sections, lists, and notes.
  - However, this remains contained within `lib/modelDestination.py` and `HTMLBuilder`.

## Next Steps

1. **Implement meta parser and renderer**
   - Add a small helper in `lib/modelDestination.py` (or a nearby module) that:
     - Parses `presentation.meta_text` into a structured dict as described.
     - Renders the “Model interpretation” section with headings and lists.

2. **Improve answer rendering**
   - Extend the answer rendering path in `Browser.insert` to:
     - Use paragraph grouping.
     - Convert simple bullet patterns into `<ul>` lists.

3. **Add tests**
   - Extend `_tests/test_model_destination.py` with cases that:
     - Feed a meta block following the ADR 020 structure and assert:
       - Interpretation, assumptions, gaps, better prompt, and suggestion appear under “Model interpretation”.
       - Bullet-style lines render as list items (via the builder’s `ul` usage).
     - Feed a bullet-heavy response and assert that:
       - The builder’s `ul` helper is invoked for obvious bullet sequences.

4. **Iterate on styling as needed**
   - Once the structure is in place, small ergonomic tweaks (for example, wording of the meta note, number of meta bullets surfaced) can be made without changing the underlying contract.

