# ADR 0147: Cross-Axis Composition Semantics — Structured Guidance for All Channel+Task Combinations

**Date:** 2026-02-25
**Status:** Proposed
**Authors:** jaresty

---

## Context

### The current state: selective incompatibility prose

When two tokens from different axes combine in ways that produce poor output, the current approach is to document this in `AXIS_KEY_TO_GUIDANCE` prose:

```python
"shellscript": (
    "Shell script output. Avoid with narrative tasks (sim, probe) and "
    "selection tasks (pick, diff, sort) — these don't produce code. "
    "Audience incompatibility: avoid with non-technical audiences "
    "(to-CEO, to-managers, to-stakeholders, to-team)."
)
```

This has two problems:

**P1 — Structured data masquerading as prose.**
"Avoid with sim, probe, pick, diff, sort" is a list of task tokens. "Avoid with to-CEO, to-managers" is a list of audience tokens. These are cross-axis relationships that could be represented as data, but they live in a string that only an LLM can interpret at runtime. Code cannot use them to render systematic guidance or validate entries.

**P2 — Only the bad cases are documented; the good ones aren't.**
The prose says what to avoid, but not what `shellscript` *does* when combined with the tasks it does work well with (make, fix, show, trans, pull). There's no systematic statement of what any channel+task pair produces. Users learn what's broken but not what to aim for.

### The existing precedent: defined composition semantics

The grammar already documents combinations with explicit *what it produces* language rather than avoidance:

- **form-as-lens rule**: When form and channel can't literally compose, the form becomes a content lens. The rule says what the combination *produces* — it doesn't block it.
- **Specification channel reframe** (Reference Key): "`probe+adr` = probe task expressed as an ADR. `diff+gherkin` = differences expressed as behavioral distinctions." Channel wins; task becomes a content lens. Again: defines the output, doesn't block the input.

The pattern is consistent: define what the combination produces. This works for specification channels (adr, gherkin, codetour) but isn't extended to executable channels (shellscript, code) or brevity channels (sync, commit). Those just say "avoid."

### The question from ADR-0085 meta-analysis

ADR-0085 cycles 17–19 found three shellscript grammar gap seeds all scoring 2 because no guidance told the LLM what to produce. The meta-analysis surfaced:

1. Should cross-axis relationships be structured data in axisConfig.py rather than ad-hoc prose?
2. Could we define what *every* channel+task combination produces — including the currently-discouraged ones — so the LLM always has guidance rather than just a list of things to avoid?

---

## Decision

### Core principle: define what every combination produces

No combinations are blocked. The goal is to give the LLM a complete composition map: for any channel+task pair, there is a defined output description. Some descriptions will say "this produces a useful X"; others will say "this tends to produce low-quality output because Y; prefer Z instead." Both are more useful than silence or a bare "avoid."

This extends the existing channel-wins-reframe pattern uniformly across all channels.

### Part A: Introduce `CROSS_AXIS_COMPOSITION` in axisConfig.py

Add a structured dict that captures cross-axis composition semantics as data. The structure uses two keys per axis pair:

- `"natural"` — tokens that combine with the channel and reliably produce good output without the LLM needing explicit instruction about what to produce. When in doubt, use `reframe` with a positive description; promote to `natural` after ADR-0085 validation confirms consistent score-4.
- `"reframe"` — a dict of `{token: description}` giving the output semantics when the combination is not natural. Descriptions may be positive ("produces X") or cautionary ("tends to produce poor output because Y; prefer Z instead")

```python
# lib/axisConfig.py
#
# Cross-axis composition semantics. Structure:
#   axis_a → token_a → axis_b → {"natural": [...], "reframe": {token: description}}
#
# "natural": token_b combinations that work with token_a without any special
#            interpretation. Listed for completeness and for "Choosing Channel"
#            rendering; the LLM produces normal output.
#
# "reframe": token_b combinations where the LLM should interpret token_b as a
#            content lens within token_a's format. The description says what the
#            combination should produce. Descriptions may be positive or cautionary.
#            No combination is blocked — these are guidance, not restrictions.
#
CROSS_AXIS_COMPOSITION: Dict[str, Dict[str, Dict[str, Any]]] = {
    "channel": {
        "shellscript": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull"],
                "reframe": {
                    "pick":  "interactive select-menu script (e.g. bash select) for choosing between options",
                    "diff":  "shell script that diffs or compares the two subjects",
                    "sort":  "shell script that filters or orders the items",
                    "sim":   "a script nominally about the scenario — tends to produce thin output "
                             "since simulation is inherently narrative; consider remote or no channel instead",
                    "probe": "a diagnostic script checking the subject — valid for narrow system-probe "
                             "use cases; tends to miss the analytical depth a prose channel provides",
                    "check": "a shell script that validates or asserts the conditions",
                    "plan":  "a shell script that sets up the plan as executable steps",
                },
            },
            "audience": {
                "natural": ["to-programmer", "to-principal-engineer", "to-junior-engineer",
                            "to-platform-team", "to-llm"],
                "reframe": {
                    "to-ceo":          "shell output to a non-technical audience — tends to be inaccessible; consider plain or presenterm instead",
                    "to-managers":     "shell output to a non-technical audience — tends to be inaccessible; consider plain or sync instead",
                    "to-stakeholders": "shell output to a non-technical audience — tends to be inaccessible; consider plain or presenterm instead",
                    "to-team":         "shell output to a mixed audience — accessible only to technical members; consider plain instead",
                },
            },
        },
        "adr": {
            "task": {
                "natural": ["plan", "probe", "make"],
                "reframe": {
                    "pull":  "ADR capturing what was extracted and the decision context around it",
                    "diff":  "ADR recording the comparison and the decision rationale it supports",
                    "sort":  "ADR recording the prioritization criteria and outcome",
                    "sim":   "ADR capturing the scenario explored and its architectural implications",
                    "check": "ADR recording what was evaluated, findings, and decision",
                    "pick":  "ADR recording the options considered and the final selection rationale",
                    "fix":   "ADR recording what was changed, why, and the trade-offs accepted",
                    "show":  "ADR framing what was demonstrated and what it implies for the architecture",
                },
            },
        },
        "sync": {
            "completeness": {
                "natural": ["full", "minimal", "gist"],
                "reframe": {
                    "max":  "exhaustive session plan — tends to be unusable; session plans require "
                            "practical brevity; max completeness treats omissions as errors and "
                            "produces overloaded agendas; use full or minimal instead",
                    "deep": "deep-dive session plan — workable but risks running long; ensure time-boxing",
                    "skim": "light-pass session plan — valid for quick standups or check-ins",
                },
            },
        },
        "code": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull", "check"],
                "reframe": {
                    "sim":   "code that nominally represents the simulation — tends to produce "
                             "thin placeholder code since simulation is narrative; consider remote or no channel",
                    "probe": "code that inspects or queries the subject — valid for narrow introspection "
                             "use cases; tends to miss the analytical depth prose provides",
                    "diff":  "code that implements a comparison of the subjects",
                    "sort":  "code that sorts or filters the items",
                    "pick":  "code that implements the selection logic",
                    "plan":  "code skeleton or scaffolding for the plan steps",
                },
            },
            "audience": {
                "natural": ["to-programmer", "to-principal-engineer", "to-junior-engineer",
                            "to-platform-team", "to-llm"],
                "reframe": {
                    "to-ceo":          "code output to a non-technical audience — inaccessible; use plain or presenterm instead",
                    "to-managers":     "code output to a non-technical audience — inaccessible; use plain instead",
                    "to-stakeholders": "code output to a non-technical audience — inaccessible; use plain or presenterm instead",
                    "to-team":         "code output to a mixed audience — accessible only to technical members",
                },
            },
        },
        "codetour": {
            "task": {
                "natural": ["make", "fix", "show", "pull"],
                "reframe": {
                    "sim":   "CodeTour nominally about a scenario — no code subject to navigate; tends to be incoherent",
                    "sort":  "CodeTour nominally about sorted items — no navigable code; tends to be incoherent",
                    "probe": "CodeTour that navigates relevant code locations to support the analysis",
                    "diff":  "CodeTour walking through the two subjects side-by-side in code",
                    "plan":  "CodeTour outlining planned code locations — valid for architecture planning",
                    "check": "CodeTour walking through the code locations being evaluated",
                    "pick":  "CodeTour comparing code implementations of the options",
                },
            },
        },
        "gherkin": {
            "task": {
                "natural": ["make", "check"],
                "reframe": {
                    "probe":  "Gherkin scenarios specifying the structural properties the analysis revealed",
                    "diff":   "Gherkin scenarios expressing differences as behavioral distinctions",
                    "sort":   "Gherkin scenarios capturing the sorted items as ordered acceptance criteria",
                    "pick":   "Gherkin scenarios expressing the selection criteria as behavioral tests",
                    "pull":   "Gherkin scenarios capturing the extracted content as behavioral specifications",
                    "sim":    "Gherkin scenarios walking through the simulation as Given/When/Then steps",
                    "plan":   "Gherkin scenarios expressing planned behavior as acceptance criteria",
                    "show":   "Gherkin scenarios demonstrating the subject's behavior",
                    "fix":    "Gherkin scenarios specifying what the fix must satisfy",
                    "trans":  "Gherkin scenarios specifying the transformation as behavioral contracts",
                },
            },
        },
    },
    "form": {
        "commit": {
            "completeness": {
                "natural": ["gist", "minimal"],
                "reframe": {
                    "max":   "commit message with exhaustive detail — the format has no room for depth; "
                             "tends to produce truncated or overloaded commit messages; use gist or minimal",
                    "deep":  "commit message with deep analysis — same constraint as max; use gist or minimal",
                    "full":  "commit message with full coverage — workable but may feel verbose for the format",
                    "skim":  "commit message with only the most obvious change noted — may omit important context",
                    "narrow": "commit message restricted to one aspect — valid for focused commits",
                },
            },
        },
    },
}
```

### Part B: Render `CROSS_AXIS_COMPOSITION` in help_llm.go

Add a `renderCrossAxisComposition(w, grammar)` function that produces two things in a single Go change:

1. **"Choosing Channel" section** — for each channel, lists the natural task combinations and notes the reframe semantics for others
2. **Universal channel-wins-reframe rule in Reference Key** — replaces the current selective documentation (only gherkin/codetour/adr) with a universally stated rule, plus per-channel reframe examples pulled from the data:

> "When a channel token is combined with any task: the channel defines output format; the task becomes a content lens within that format. For all channel+task combinations, `CROSS_AXIS_COMPOSITION` defines the output description. If no natural combination exists for a given task, the reframe description tells the LLM what to produce or warns that the combination tends to produce low-quality output."

When new channel+task entries are added to `CROSS_AXIS_COMPOSITION`, the rendered output updates automatically — no Go changes required.

---

## Consequences

### Positive

- **P1 resolved**: Cross-axis relationships are machine-readable data. Code can render "Choosing Channel" systematically and validate entries against the token catalog.
- **P2 resolved**: Every channel+task pair has defined output semantics. The LLM no longer silently mishandles undocumented combinations.
- **Composability principle unified**: The channel-wins-reframe pattern now applies to all channels, not just specification artifact channels. The Reference Key states the rule once; `CROSS_AXIS_COMPOSITION` provides the per-combination output descriptions.
- **Score-2 reduction**: Combinations with useful reframe semantics (`shellscript+diff`, `shellscript+sort`, `adr+pull`, `gherkin+sim`, etc.) may improve from score-2 to score-3 or score-4 once the LLM has guidance on what to produce.
- **Cautionary reframes**: Combinations like `shellscript+sim` now produce defined (poor) output with an explanation and a better-path suggestion, rather than producing undefined output silently.
- **Growing dict**: New channel+task observations from ADR-0085 shuffle cycles can be added as `reframe` entries without Go changes.

### Risks and open questions

**R1 — Reframe quality is empirically unknown.**
Reframe descriptions are hypotheses. `shellscript+diff → "shell script that diffs the subjects"` may produce score-4 for code subjects but score-2 for conceptual subjects. ADR-0085 shuffle validation is needed post-implementation.

**R2 — AXIS_KEY_TO_GUIDANCE prose duplication.**
`CROSS_AXIS_COMPOSITION` overlaps with existing prose in `AXIS_KEY_TO_GUIDANCE["channel"]["shellscript"]` etc. The prose notes should be updated to reference the structured data (or removed where the structured data is the SSOT) to avoid contradiction. Migration concern, not a blocker.

**R3 — Coverage is intentionally incomplete at first.**
The initial dict covers channels identified in ADR-0085 cycles 17–19. Many channel+task combinations are not yet listed. Unlisted combinations fall back to existing behavior (no special reframe). The dict is additive.

**R4 — No grammar enforcement.**
All combinations remain permitted by the grammar. The `CROSS_AXIS_COMPOSITION` data is guidance-only. If grammar enforcement is desired in the future, this data structure is the natural place to derive it from — but that is explicitly deferred and not part of this ADR.

---

## Implementation Plan

### Phase 1: Data structure (axisConfig.py)

1. Add `CROSS_AXIS_COMPOSITION` dict to `lib/axisConfig.py`
2. Add helper function `get_cross_axis_composition(axis: str, token: str) → dict`
3. Populate initial entries (shellscript, adr, sync, code, codetour, gherkin for channel axis; commit for form axis)
4. Leave `AXIS_KEY_TO_GUIDANCE` prose unchanged — migration of overlapping cross-axis notes is deferred to Phase 5 audit

### Phase 2: Grammar export

1. Add `CrossAxisComposition` field to grammar JSON
2. Export from `lib/promptGrammar.py`; read in `grammar.go`
3. `make bar-grammar-update` to regenerate

### Phase 3: help_llm rendering (replaces F4)

1. Add `renderCrossAxisComposition(w, grammar)` in `help_llm.go`
2. Renders "Choosing Channel" section from natural+reframe data per channel
3. Renders universal channel-wins-reframe rule in Reference Key, replacing the current selective gherkin/codetour/adr-only statement
4. "Grammar-enforced restrictions" section already handled by F5 fix — no further change needed

### Phase 4: ADR-0085 validation

1. Re-run seeds 531, 560, 588, 615 against the updated grammar
2. Evaluate reframe combinations for quality (shellscript+diff, shellscript+sort, adr+pull, gherkin+sim)
3. Update `process-feedback.md` open recommendations table

### Phase 5: Metadata migration audit (post-implementation)

Once `CROSS_AXIS_COMPOSITION` is live and validated, audit existing token metadata for content that should migrate to the new structure:

```
bar build probe full domains split --addendum "Audit token metadata for cross-axis content that belongs in CROSS_AXIS_COMPOSITION rather than per-token prose"
```

Evaluate the following sources:
- `AXIS_KEY_TO_GUIDANCE` prose in `lib/axisConfig.py` — entries like shellscript, code, adr, codetour, gherkin, sync, commit that contain cross-axis avoidance notes (these are the prime migration candidates per R2)
- `AXIS_KEY_TO_USE_WHEN` entries that contain cross-axis heuristics rather than token-selection guidance
- `_STATIC_PROMPT_GUIDANCE` and `_STATIC_PROMPT_USE_WHEN` in `lib/staticPromptConfig.py` — task token notes that reference channel or form incompatibilities
- Static help text in `help_llm.go` — sections that document cross-axis behavior inline rather than rendering from data

For each candidate: determine whether it is (a) pure cross-axis composition data → migrate to `CROSS_AXIS_COMPOSITION`, (b) same-axis guidance → keep in place, or (c) general usage pattern → belongs in `help_llm.go` heuristics sections.

---

## Deferred

- Grammar enforcement for cross-axis combinations — explicitly out of scope for this ADR; the data structure would support it if desired
- Extending `CROSS_AXIS_COMPOSITION` to completeness×method tensions (skim+rigor, max+spike) — score-3 tensions, lower priority
- Surfacing reframe descriptions in TUI2/SPA (would require new UI component)
- Auto-generating `AXIS_KEY_TO_GUIDANCE` prose from `CROSS_AXIS_COMPOSITION` (migration work)
