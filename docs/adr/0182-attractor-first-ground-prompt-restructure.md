# ADR-0182: Attractor-First Restructure of groundPrompt.py

## Status

Proposed

## Context

`groundPrompt.py` injects approximately 6,000 words of behavioral rules into the model as the `ground` method prompt. An orbit analysis of the prompt text identified three recurring structural attractors — concepts the prompt returns to across eight or more distinct locations each:

**Attractor 1 — Evidential boundary:** What counts as evidence. Tool-executed vs. inferred. Verbatim vs. paraphrased. Live-process output vs. file read. Test runner output vs. live artifact output. This is the load-bearing attractor; all rung gates are downstream of it.

**Attractor 2 — Forward-only discipline:** When advancement is permitted. V-complete before OBR label. Red run before implementation. Manifest before criteria. Thread-complete before next criterion. Carry-forward before modification. The protocol is enforced by token ordering in the transcript, not by intent.

**Attractor 3 — Scope discipline:** Do only what the current gap requires. One criterion per cycle. One edit per re-run. No anticipation of future gaps. No additional invariants. This is R2 (minimal derivation) in action.

These three attractors are currently implicit. No section of the prompt names them. Instead, each enforcement paragraph re-derives a specific manifestation of an attractor in isolation. The result is a prompt that is long because it is enumerative rather than deductive: every known escape route is closed by a separate prohibition, rather than by a stated principle from which the prohibition follows.

The rung-entry gate (ADR-0181) partially addresses this by making A2 operational at each rung boundary, but the underlying structure remains implicit.

## Decision

Restructure the prompt text in `GROUND_PARTS_MINIMAL["core"]` around three explicitly named principles, each derived from the axioms, followed by a compact rung table, followed by protocol mechanics. Enforcement paragraphs that are corollaries of a named principle are removed and replaced by the principle itself being precise enough to make the corollary derivable.

### Three named principles (stated after the axioms, before the rung sequence)

**P1 (Evidential boundary):** A rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript whose output is classified as that rung's artifact type. No other event — inference, file read, test runner output, static analysis, prior-cycle output — satisfies any gate regardless of its content or accuracy.

**P2 (Forward-only discipline):** A rung label may not be emitted until all preconditions for that rung are present in the current-cycle transcript. The precondition list for each rung is the rung table's gate column. No content at a rung is valid before the label. No label is valid before its gate conditions.

**P3 (Scope discipline):** Each rung artifact addresses exactly the gap declared by the prior rung — nothing beyond it. One gap per cycle. One criterion per thread per cycle. One edit per re-run. No anticipation of future gaps, no additional invariants, no coverage beyond the declared gap.

### Restructured prompt shape

1. Axioms (A1–A3, R2) — unchanged
2. Named principles (P1–P3) — new, derived from axioms
3. Rung table — seven rows: name, artifact type, gate condition, void condition
4. Protocol mechanics — cycle isolation, upward-return failure classes, thread counting, carry-forward, sentinel catalog
5. Rung-entry gate — unchanged (ADR-0181)

### Enforcement paragraphs to remove

Any paragraph whose content is a corollary of P1, P2, or P3 and which adds no new information beyond the principle:

- "A file read does not satisfy the OBR gate" → corollary of P1 (file reads produce static-analysis-type output, not live-process-output type)
- "A test runner output does not satisfy OBR" → corollary of P1 (test runner output is validation-run-observation type, not observed-running-behavior type)
- "V-complete may not be emitted before a red run" → corollary of P2 (red run is a gate precondition for V-complete)
- "One edit per re-run" → corollary of P3
- "No enumeration of future gaps before manifest exhausted" → corollary of P3
- "No additional invariants in formal notation" → corollary of P3

Paragraphs that close escape routes not derivable from P1–P3 are retained.

## Consequences

**Positive:**
- Prompt text compresses from ~6,000 words to an estimated ~2,500 words without losing behavioral coverage
- Models can reason from principles to novel failure modes rather than scanning a prohibition list
- New escape routes can be closed by refining a principle rather than appending a new paragraph
- The attractor structure becomes legible, making the prompt easier to audit and maintain

**Negative:**
- Requires careful audit to verify each removed paragraph is genuinely derivable from a named principle and not closing a novel escape route
- Compliance must be re-validated via ADR-0113 loop after restructuring

## Implementation Notes

- Edit `GROUND_PARTS_MINIMAL["core"]` in `lib/groundPrompt.py` directly (it is the SSOT)
- Run `make axis-regenerate-apply` and `cp build/prompt-grammar.json web/static/prompt-grammar.json` after editing
- Run ADR-0113 loop (minimum 5 tasks) to validate compliance before closing this ADR
- Work log should record which paragraphs were removed and which principle makes each removal sound
