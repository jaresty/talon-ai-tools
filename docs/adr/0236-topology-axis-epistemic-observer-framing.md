# ADR-0236: Topology Axis — Epistemic Observer Framing

**Status:** Proposed
**Date:** 2026-05-12

---

## Context

The existing axis system governs *how* reasoning proceeds (method), *what* is covered
(completeness), *how* it is structured (form), *what medium* it uses (channel), and
*where* it explores (directional). None of these axes govern the assumed evaluability
conditions under which reasoning is produced.

A controlled five-run experiment applied the same architecture design task under five
different observer/evaluability framings (solo / witness / audit / relay / blind). The
architectures produced were identical across runs. The reasoning structure changed
systematically:

- **witness** surfaced hidden engineering assumptions not present in any other run
  (LLM non-determinism as a fragility of event-sourced replay; IPC cost as an
  unvalidated assumption of the modular approach)
- **audit** structured claims as locally defensible statements without narrative
  dependency — a different textual form independent of conclusions
- **relay** uniquely produced handoff artifacts (schemas, tool contracts, event flows)
  absent from all other runs
- **blind** restated all requirements explicitly at the top, unprompted
- The final analysis identified the core pattern: "architectures converge, but the
  shape of reasoning debt changes systematically with observer model"

This axis is distinct from existing ones:

- Not **method**: topology does not specify a reasoning procedure; it specifies the
  assumed scrutiny conditions under which reasoning occurs. Method answers "how do I
  derive this?"; topology answers "what must remain visible while I derive it?"
- Not **completeness**: completeness governs how much is covered; topology governs
  what must be made explicit within that coverage. A system can be fully complete while
  hiding all assumptions.
- Not **form**: form governs information structure; topology governs justification
  obligations independent of structure.

The token names `cross` and `peer` are already taken (`cross` is a method token for
cross-cutting concerns; `peer` is a persona preset for peer-engineer explanation style).
The topology tokens with adversarial-scrutiny and collaborative-handoff semantics are
named `audit` and `relay` instead.

---

## Decision

Add `topology` as a new axis with five tokens, positioned between `task` and
`completeness` in axis priority order.

### Token Definitions

**`solo`** — 独 — "unobserved reasoning"
Assume the reasoning process is not externally inspected during construction. Optimize
for synthesis efficiency and conceptual compression. Do not proactively externalize
intermediate assumptions unless naturally necessary. Assume only the final artifact is
visible.

Use when: early-stage ideation, speculative architecture, naming and metaphor work,
mathematical intuition before formal proof.

**`witness`** — 観 — "inspectable reasoning"
Assume an independent observer is continuously evaluating whether each reasoning
transition is causally and epistemically justified. Surface important assumptions before
relying on them. Avoid silently collapsing uncertainty into conclusions. Assume the
observer may pause at any transition and ask: "Why does this follow from the previous
state?"

Use when: architecture reviews, long-horizon planning, scientific reasoning, any task
where hidden assumption failures have high cost. Expected to be the most generally
useful token.

**`audit`** — 査 — "locally defensible reasoning"
Assume each major reasoning transition may be independently challenged by a skeptical
evaluator. Ensure claims remain locally defensible without relying on later conclusions
for support. Unsupported continuity jumps are treated as failures.

Use when: security analysis, compliance evaluation, formal design reviews, any context
where adversarial challenge is expected or where global narrative cannot substitute for
local proof.

**`relay`** — 継 — "handoff-ready reasoning"
Assume another engineer is jointly tracking the reasoning and may continue it
mid-stream without access to hidden intermediate cognition. Externalize state sufficient
for continuation: surface schemas, contracts, invariants, dependency relationships, and
terminology explicitly.

Use when: engineering handoffs, open-source API design, collaborative architecture,
AI-agent orchestration specs, any task where reasoning state must transfer.

**`blind`** — 暗 — "reconstructable reasoning"
Assume the reasoning artifact will later be replayed by someone without access to
hidden intermediate cognition. Reconstruct key assumptions and constraints explicitly
before relying on them. Avoid implicit contextual carry-forward.

Use when: incident postmortems, reproducible research, long-lived design records,
archival documentation, any context where future readers cannot inherit implicit context.

---

## Tradeoffs

| Token   | Strength                          | Risk                                      |
|---------|-----------------------------------|-------------------------------------------|
| solo    | highest creativity and fluency    | hidden assumptions, hallucinated continuity |
| witness | best default epistemic hygiene    | can slow exploration, increase verbosity  |
| audit   | strongest local validity          | can suppress synthesis, over-fragment     |
| relay   | best handoff artifacts            | over-explains, biases toward maintainability |
| blind   | strongest reconstructability      | verbosity, over-serializes reasoning      |

`witness` is expected to be the most generally useful token and the best default when
epistemic hygiene matters. `solo` is useful as an explicit opt-out of inspectability
pressure when exploration is the primary goal.

---

## Surfaces Requiring Modification

### Python / grammar export pipeline

1. **`lib/axisConfig.py`** (SSOT) — add `topology` entries to:
   - `AXIS_KEY_TO_VALUE` (prompt injection text for each token)
   - `AXIS_KEY_TO_LABEL` (short CLI-facing label)
   - `AXIS_KEY_TO_KANJI` (kanji icon)
   - `AXIS_KEY_TO_ROUTING_CONCEPT` (shortest phrase for token discovery)
   - `AXIS_TOKEN_METADATA` (definition, heuristics[], distinctions[])

2. **`lib/talonSettings.py`** — insert `"topology"` into `_AXIS_PRIORITY` between
   `"completeness"` (or `"task"` if task is handled separately) and `"completeness"`.
   Current order: `completeness, scope, method, form, channel`. New order:
   `topology, completeness, scope, method, form, channel`.

3. **`lib/promptGrammar.py`** — add `"topology"` to the axis loop at line 473 that
   iterates `("completeness", "scope", "method", "form", "channel", "directional")`.

4. **`lib/axisCatalog.py`** — no structural change expected; picks up new axis
   automatically from `axisConfig.py` if the catalog loop covers all axes. Verify.

### Go / CLI

5. **`internal/barcli/help_llm.go`** — multiple sites:
   - Grammar BNF section (lines ~254–259): add `<topology-value>` line
   - `orderedAxes` slices (lines ~410, ~522, ~806, ~849): insert `"topology"` in
     correct position
   - `partnerAxes` slice (line ~1128): add `"topology"`
   - `renderRoutingConceptSection` calls (~1101–1107): add topology routing concept
   - Add a "Choosing Topology" heuristic section explaining when to reach for each token

6. **`internal/barcli/grammar.go`** — verify `topology` axis is loaded from JSON
   automatically through the generic axis loading path; add explicit handling if needed.

7. **`internal/barcli/completion.go`** — verify `axisPriority` from grammar JSON
   propagates correctly to completion ordering; no change expected if driven by JSON.

8. **`internal/barcli/tui_tokens.go`** — verify `topology` axis renders in TUI token
   panel; no change expected if driven by `orderedAxes` from grammar.

### SPA / web

9. **`web/src/routes/+page.svelte`** — add `topology: []` to the `selected` state
   initialization (line ~239) alongside `task`, `completeness`, `scope`, etc.

10. **`web/static/prompt-grammar.json`** — regenerate from `build/prompt-grammar.json`
    after grammar export (`make bar-grammar-update` then `cp build/prompt-grammar.json
    web/static/prompt-grammar.json`). Per existing SPA sync note: missing this step
    silently omits new axis data.

### Talon voice grammar

11. **`GPT/gpt.talon`** — add voice commands for topology if set/reset commands follow
    the pattern of `completeness`, `method`, `channel` (lines ~10–20). Likely:
    ```
    ^{user.model} set topology {user.topologyModifier}$: user.gpt_set_default_topology(topologyModifier)
    ^{user.model} reset topology$: user.gpt_reset_default_topology()
    ```
    Requires corresponding list file and Python action implementations.

12. **Talon list file** — create `topologyModifier.talon-list` (parallel to
    `completenessModifier.talon-list`) enumerating `solo`, `witness`, `audit`,
    `relay`, `blind` as voice-speakable tokens.

### Tests

13. **`internal/barcli/help_llm_test.go`** — update `TestLLMHelp` to include topology
    tokens in validation coverage.

14. **SPA tests** — update any test fixtures that enumerate axes (e.g.,
    `keyboard-navigation.test.ts` F4b/F5b which hardcode `completeness` as the first
    axis after task) to account for `topology` being inserted before `completeness`.

---

## Consequences

- `topology` becomes a first-class axis parallel to `completeness`, `method`, etc.
- `cross` (method) and `peer` (persona preset) are unaffected; no token renames.
- Some existing uses of `method=gate` or `completeness=deep` may be better expressed
  as `topology=witness` — this is a discoverability improvement, not a removal.
- ADR-0113 routing loop should include a topology validation pass after implementation
  to confirm heuristics correctly route observer-framing tasks to topology tokens rather
  than to method or completeness proxies.
