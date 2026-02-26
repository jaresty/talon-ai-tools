# ADR 0147: Cross-Axis Composition Semantics — Structured Affinities and Channel-Wins Reframe

**Date:** 2026-02-25
**Status:** Proposed
**Authors:** jaresty

---

## Context

### The current state: incompatibilities as prose notes

When two tokens from different axes combine in ways that produce poor output, the current approach is to document the incompatibility as prose in `AXIS_KEY_TO_GUIDANCE`. For example:

```python
"shellscript": (
    "Shell script output. Avoid with narrative tasks (sim, probe) and "
    "selection tasks (pick, diff, sort) — these don't produce code. "
    "Audience incompatibility: avoid with non-technical audiences "
    "(to-CEO, to-managers, to-stakeholders, to-team)."
)
```

This produces three problems:

**P1 — Structured data masquerading as prose.**
The statement "avoid with sim, probe, pick, diff, sort" is a list of task tokens. The statement "avoid with to-CEO, to-managers" is a list of audience tokens. These are cross-axis relationships that could be represented as data, but they live in a string that only an LLM can interpret. Code cannot use them.

**P2 — No systematic rendering.**
Because the incompatibilities are prose, `help_llm.go` cannot render a "Choosing Channel" section analogous to "Choosing Scope" or "Choosing Form." Each new incompatibility requires manual prose updates in two places: the `AXIS_KEY_TO_GUIDANCE` note and (if added) any hardcoded summary in `help_llm.go`.

**P3 — Grammar enforcement is architecturally blocked.**
`_AXIS_INCOMPATIBILITIES` in `lib/talonSettings.py` is structured as `axis → token → set[incompatible tokens within the same axis]`. It cannot express cross-axis incompatibilities. R41 (grammar-hardening) has been deferred indefinitely because the schema doesn't support it — but that schema could be replaced with the structured data from this ADR.

### The existing precedent: form-as-lens

The grammar already has one cross-axis composition rule defined with explicit semantics rather than incompatibility: the **form-as-lens** rule. When a form token and a channel token are both present and cannot literally compose (e.g., `case` form + `shellscript` channel), the rule is:

> Channel defines output format; form describes conceptual organization within that format. When the form's structural template cannot be expressed in the channel's format, treat the form as a content lens.

This rule is documented in the Reference Key and produces useful output from combinations that would otherwise be incoherent. It is not an incompatibility — it is a defined composition semantic.

### The observation: channel-wins already applies to some task+channel combinations

The Reference Key also documents:

> "When a channel produces a specification artifact (gherkin, codetour, adr), analysis or comparison tasks are reframed as: perform the analysis, then express findings as that artifact type."

So `probe+adr` = probe task + ADR channel → the analysis is expressed as an ADR. `diff+gherkin` = diff task + Gherkin channel → differences expressed as behavioral distinctions. The **channel-wins-reframe** pattern already exists for specification channels.

This pattern is *not* extended to executable channels (shellscript, code) or brevity channels (sync, commit). The shellscript guidance says "avoid" instead of defining what the combination should produce.

### The question from ADR-0085 meta-analysis

ADR-0085 cycles 17–19 found three shellscript grammar gap seeds (531, 560, 588) all scoring 2, all documented in AXIS_KEY_TO_GUIDANCE, all unenforced at grammar level. The meta-analysis surfaced two questions:

1. Should cross-axis affinities be structured data in axisConfig.py rather than prose in guidance notes?
2. Could we define composition semantics that make some "incompatible" combinations produce useful output, rather than just documenting them as errors?

---

## Decision

### Part A: Introduce `CROSS_AXIS_AFFINITIES` in axisConfig.py

Add a structured dict that captures cross-axis affinity and avoidance relationships as data. This replaces the cross-axis incompatibility prose currently embedded in `AXIS_KEY_TO_GUIDANCE` notes.

```python
# lib/axisConfig.py
#
# Cross-axis affinity rules. Structure:
#   axis_a → token_a → axis_b → rule
#
# Rules:
#   "affinity": [tokens] — axis_b tokens that combine well with token_a
#   "avoid": [tokens]    — axis_b tokens that should not be combined with token_a
#   "reframe": {token: description} — axis_b tokens that combine with defined
#                                     composition semantics (see Part B)
#
CROSS_AXIS_AFFINITIES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "channel": {
        "shellscript": {
            "task": {
                "affinity": ["make", "fix", "show", "trans", "pull"],
                "avoid":    ["sim", "probe"],
                "reframe":  {
                    "pick":  "interactive select-menu script for choosing between options",
                    "diff":  "shell script that diffs the two subjects",
                    "sort":  "shell script that filters or orders the items",
                },
            },
            "audience": {
                "avoid": ["to-ceo", "to-managers", "to-stakeholders", "to-team"],
            },
        },
        "adr": {
            "task": {
                "affinity": ["plan", "probe", "make"],
                "avoid":    [],
                "reframe":  {
                    "pull":  "ADR capturing what was extracted and why it matters",
                    "diff":  "ADR recording the comparison and decision rationale",
                    "sort":  "ADR recording the prioritization criteria and outcome",
                    "sim":   "ADR capturing the scenario and its implications",
                },
            },
        },
        "sync": {
            "completeness": {
                "avoid": ["max"],
            },
        },
        "code": {
            "task": {
                "avoid": ["sim", "probe"],
            },
            "audience": {
                "avoid": ["to-ceo", "to-managers", "to-stakeholders", "to-team"],
            },
        },
        "codetour": {
            "task": {
                "affinity": ["make", "fix", "show", "pull"],
                "avoid":    ["sim", "sort", "probe", "diff", "plan"],
            },
            "audience": {
                "avoid": ["to-managers", "to-product-manager", "to-ceo",
                          "to-stakeholders", "to-analyst", "to-designer"],
            },
        },
    },
    "form": {
        "commit": {
            "completeness": {
                "avoid": ["max", "deep"],
            },
        },
    },
}
```

**Scope:** The initial implementation covers the cases identified in ADR-0085 cycles 17–19. Additional entries can be added as new cross-axis patterns are discovered in future shuffle cycles.

### Part B: Define channel-wins-reframe composition semantics

Where a `"reframe"` entry exists in `CROSS_AXIS_AFFINITIES`, the combination is not an incompatibility — it has defined output semantics. The channel wins (output format is fixed); the task becomes a content lens interpreted within the channel's format.

**Reframe rule:** `channel C + task T` with a reframe description `D` → "produce a `C`-format output that `D`."

Examples:
- `shellscript + diff` with reframe "shell script that diffs the two subjects" → produce a shell script implementing or invoking a diff of the subjects
- `adr + pull` with reframe "ADR capturing what was extracted and why it matters" → perform the pull task, express findings as an ADR
- `shellscript + sort` with reframe "shell script that filters or orders the items" → produce a shell script that implements the sort/filter

**Non-reframeable combinations remain "avoid":**
`shellscript + sim` stays "avoid" (not in reframe dict) because simulation is inherently narrative — there is no coherent shell script that "plays out a scenario" in a way that serves the user's intent. `shellscript + probe` similarly — shell scripts produce output, not analysis.

### Part C: Render `CROSS_AXIS_AFFINITIES` in help_llm.go

Add a `renderCrossAxisAffinities(w, grammar)` function that produces a "Choosing Channel" section (and other cross-axis summary sections) from the structured data rather than hardcoded prose.

This replaces the F4 temporary fix (hardcoded "Choosing Channel" in help_llm.go) with a data-driven renderer.

### Part D: Wire into grammar enforcement (replaces R41)

The `CROSS_AXIS_AFFINITIES` dict provides the data needed for cross-axis grammar enforcement. Replace the incomplete `_AXIS_INCOMPATIBILITIES` schema in `lib/talonSettings.py` with a grammar-generation step that reads `CROSS_AXIS_AFFINITIES["channel"]["shellscript"]["task"]["avoid"]` and produces hard blocks in the grammar JSON.

**Note:** Grammar enforcement blocks "avoid" combinations. "Reframe" combinations are NOT blocked — they produce valid output with defined semantics.

---

## Consequences

### Positive

- **P1 resolved**: Cross-axis rules are now machine-readable data. Code can render "Choosing Channel" systematically, generate grammar restrictions, and surface affinities in TUI/SPA tooling.
- **P2 resolved**: `renderCrossAxisAffinities` in `help_llm.go` replaces both the temporary F4 fix and any future manual additions to Go source.
- **P3 resolved**: R41 grammar hardening becomes "populate `CROSS_AXIS_AFFINITIES` and wire the renderer" — the architecture now supports it.
- **Score-2 reduction**: Combinations with reframe semantics (`shellscript+diff`, `shellscript+sort`, `adr+pull`, etc.) may move from score-2 to score-3 or score-4 once the reframe guidance is visible to the LLM.
- **Composability principle extended**: The channel-wins rule now applies uniformly — specification channels, executable channels, and brevity channels all have defined semantics for task combinations.

### Risks and open questions

**R1 — Reframe quality is empirically unknown.**
The reframe descriptions are hypotheses. `shellscript + diff → "shell script that diffs the subjects"` may produce score-4 output for code subjects but score-2 for conceptual subjects. ADR-0085 shuffle validation will be needed after implementation.

**R2 — AXIS_KEY_TO_GUIDANCE prose duplication.**
The structured `CROSS_AXIS_AFFINITIES` data overlaps with existing prose in `AXIS_KEY_TO_GUIDANCE["channel"]["shellscript"]` etc. The prose notes must be updated to reference the structured data (or be auto-generated from it) to avoid contradiction. This is a migration concern, not a blocker.

**R3 — Grammar enforcement for "avoid" changes user experience.**
Currently "avoid" combinations are permitted by grammar and only warned in notes. Hard grammar blocks will reject them outright. This is the intended behavior, but requires user communication (a new release note).

**R4 — Reframe dict coverage is incomplete.**
The initial dict covers cases found in ADR-0085 cycles 17–19. Many other channel+task combinations exist and have not been evaluated. The dict should be treated as growing, not complete.

---

## Implementation Plan

### Phase 1: Data structure (axisConfig.py)

1. Add `CROSS_AXIS_AFFINITIES` dict to `lib/axisConfig.py`
2. Add helper function `get_cross_axis_affinities() → CROSS_AXIS_AFFINITIES`
3. Populate initial entries: shellscript, adr, sync, code, codetour (channel axis) + commit (form axis)
4. Remove cross-axis incompatibility prose from `AXIS_KEY_TO_GUIDANCE` entries that are now covered by the structured dict; keep same-axis and non-structured notes

### Phase 2: Grammar export

1. Add `CrossAxisAffinities` field to grammar JSON (alongside existing `AxisIncompatibilities`)
2. Export from `lib/promptGrammar.py`; read in `grammar.go`
3. `make bar-grammar-update` to regenerate

### Phase 3: help_llm rendering (replaces F4 temporary fix)

1. Add `renderCrossAxisAffinities(w, grammar)` in `help_llm.go`
2. Renders "Choosing Channel" section with affinity/avoid/reframe entries per channel token
3. Renders reframe semantics as composition rules in the Reference Key section
4. Replace the empty `"Grammar-enforced restrictions:"` section (F5) with actual content drawn from the "avoid" entries

### Phase 4: Grammar enforcement (Part D / R41)

1. Update grammar generation to produce hard incompatibility rules from "avoid" entries
2. Update `_AXIS_INCOMPATIBILITIES` in `lib/talonSettings.py` to a cross-axis-capable schema (or deprecate in favour of `CROSS_AXIS_AFFINITIES`)
3. Validate: shuffle cycles should see zero score-2 seeds from newly-blocked combinations

### Phase 5: ADR-0085 validation

1. Re-run seeds 531, 560, 588, 615 against the updated grammar
2. Evaluate reframe combinations (shellscript+diff, shellscript+sort, adr+pull) for quality
3. Update `process-feedback.md` open recommendations table

---

## Deferred

- Extending `CROSS_AXIS_AFFINITIES` to completeness×method affinities (e.g., skim+rigor tension, max+spike) — these are score-3 tensions, not score-2 incompatibilities, and may not warrant grammar enforcement
- Surfacing affinities in TUI2/SPA (would require new UI component to show per-token cross-axis warnings)
- Auto-generating `AXIS_KEY_TO_GUIDANCE` prose from `CROSS_AXIS_AFFINITIES` data (migration work, not architectural blocker)
