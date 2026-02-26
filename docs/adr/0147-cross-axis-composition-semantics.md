# ADR 0147: Cross-Axis Composition Semantics — Structured Guidance for All Channel+Task Combinations

**Date:** 2026-02-25
**Status:** Accepted
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

### Core principle: universal rule + cautionary exceptions

Positive "what does this combination produce" cases are handled by a universal channel-wins-reframe rule in the Reference Key (injected into every `bar build` prompt via `metaPromptConfig.py`). The rule tells the LLM: when a channel is present, the channel mandates output format and the task becomes a content lens — ask "what would it mean to produce this task's output through this channel's format?" This is derivable for any combination.

The only cases that need explicit data are **cautionary**: combinations that tend to produce poor output for structural reasons the universal rule cannot predict (e.g., simulation is inherently narrative and cannot be meaningfully executed as a shell script). These are enumerated in `CROSS_AXIS_COMPOSITION` and surfaced in `bar help llm` — not injected into the prompt.

### Part A: Introduce `CROSS_AXIS_COMPOSITION` in axisConfig.py

Add a structured dict that captures cross-axis composition semantics as data. The structure uses two keys per axis pair:

- `"natural"` — tokens that combine with the channel and reliably produce good output without any special interpretation. Listed for "Choosing Channel" rendering in `bar help llm`.
- `"cautionary"` — a dict of `{token: warning}` for combinations that tend to produce poor output for structural reasons not derivable from the universal rule. Only entries that are genuinely non-obvious belong here. Format: "tends to produce X because Y; prefer Z instead".

```python
# lib/axisConfig.py — cautionary entries only; positive cases handled by Reference Key universal rule
CROSS_AXIS_COMPOSITION: Dict[str, Dict[str, Dict[str, Any]]] = {
    "channel": {
        "shellscript": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull"],
                "cautionary": {
                    "sim":   "tends to produce thin output — simulation is inherently narrative, not executable",
                    "probe": "tends to miss analytical depth — valid only for narrow system-probe scripts",
                },
            },
            "audience": {
                "natural": ["to-programmer", "to-principal-engineer", "to-junior-engineer",
                            "to-platform-team", "to-llm"],
                "cautionary": {
                    "to-ceo":          "tends to be inaccessible; consider plain or presenterm instead",
                    "to-managers":     "tends to be inaccessible; consider plain or sync instead",
                    "to-stakeholders": "tends to be inaccessible; consider plain or presenterm instead",
                    "to-team":         "accessible only to technical members; consider plain instead",
                },
            },
        },
        "adr":      {"task": {"natural": ["plan", "probe", "make"]}},
        "gherkin":  {"task": {"natural": ["make", "check"]}},
        "sync": {
            "completeness": {
                "natural": ["full", "minimal", "gist"],
                "cautionary": {
                    "max": "tends to be unusable — session plans require brevity; use full or minimal instead",
                },
            },
        },
        "code": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull", "check"],
                "cautionary": {
                    "sim":   "tends to produce thin placeholder code — simulation is narrative, not executable",
                    "probe": "tends to miss analytical depth — valid only for narrow introspection scripts",
                },
            },
            "audience": {
                "natural": ["to-programmer", "to-principal-engineer", "to-junior-engineer",
                            "to-platform-team", "to-llm"],
                "cautionary": {
                    "to-ceo":          "inaccessible to a non-technical audience; use plain or presenterm instead",
                    "to-managers":     "inaccessible to a non-technical audience; use plain instead",
                    "to-stakeholders": "inaccessible to a non-technical audience; use plain or presenterm instead",
                    "to-team":         "accessible only to technical members of a mixed audience",
                },
            },
        },
        "codetour": {
            "task": {
                "natural": ["make", "fix", "show", "pull"],
                "cautionary": {
                    "sim":  "tends to be incoherent — simulation is narrative with no code subject to navigate",
                    "sort": "tends to be incoherent — sorted items have no navigable code structure",
                },
            },
        },
    },
    "form": {
        "commit": {
            "completeness": {
                "natural": ["gist", "minimal"],
                "cautionary": {
                    "max":  "tends to produce truncated or overloaded messages — format has no room for depth; use gist or minimal",
                    "deep": "same constraint as max — format cannot accommodate deep analysis; use gist or minimal",
                },
            },
        },
    },
}
```

### Part B: Update Reference Key in `metaPromptConfig.py`

Extend two places in the Channel bullet of `PROMPT_REFERENCE_KEY`:

1. **Channel constraint description** — extend from "delivery context: platform formatting conventions only" to include the task-as-lens rule: when a channel is present, the task becomes a content lens — ask "what would it mean to produce this task's output through this channel's format?"

2. **Precedence bullet** — extend the existing specification-artifact-only rule to a universal statement covering all channels (executable, specification, and delivery).

This is the primary mechanism for score-2 improvement — the LLM reads this at execution time in every `bar build` prompt.

### Part C: Render `CROSS_AXIS_COMPOSITION` in `help_llm.go`

Add a `renderCrossAxisComposition(w, grammar)` function that renders a **"Choosing Channel" section** in `bar help llm`:

- For each channel, lists the natural task/audience/completeness combinations
- Lists cautionary warnings for non-natural combinations that tend to produce poor output

This is pre-selection guidance — the LLM reads it when learning the grammar, not at execution time. The cautionary warnings here complement the universal rule in the Reference Key.

---

## Consequences

### Positive

- **P1 resolved**: Cross-axis relationships are machine-readable data. Code can render "Choosing Channel" systematically and validate entries against the token catalog.
- **P2 resolved**: The universal Reference Key rule gives the LLM first-principles guidance for any channel+task combination. Cautionary exceptions are enumerated for the structurally-broken cases the universal rule cannot predict.
- **Composability principle unified**: The channel-wins-reframe pattern now applies to all channels universally, stated once in the Reference Key, with cautionary exceptions in `CROSS_AXIS_COMPOSITION`.
- **Score-2 reduction**: The primary mechanism is the Reference Key universal rule (execution-time). Cautionary entries prevent the structurally-broken combinations (`shellscript+sim`, `code+sim`, `codetour+sim/sort`) from silently producing poor output.
- **Minimal dict**: `cautionary` contains only entries that are non-derivable from first principles. New entries are only added when observed in ADR-0085 shuffle cycles and confirmed not explainable by the universal rule.
- **Growing dict**: New cautionary observations can be added to `CROSS_AXIS_COMPOSITION` without Go changes.

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

### Phase 1: Data structure (axisConfig.py) ✅ Done

1. ~~Add `CROSS_AXIS_COMPOSITION` dict to `lib/axisConfig.py`~~ — done; cautionary-only entries
2. ~~Add helper function `get_cross_axis_composition(axis: str, token: str) → dict`~~ — done
3. ~~Populate initial entries~~ — done; `adr`/`gherkin` have natural-only (no cautionary); `shellscript`/`code`/`codetour`/`sync`/`commit` have cautionary entries
4. Leave `AXIS_KEY_TO_GUIDANCE` prose unchanged — migration deferred to Phase 5 audit

### Phase 2: Grammar export ✅ Done

1. ~~Add `CrossAxisComposition` field to grammar JSON~~ — done; `cross_axis_composition` under `axes`
2. ~~Export from `lib/promptGrammar.py`; read in `grammar.go`~~ — done; `CrossAxisPair` struct + accessor
3. ~~`make bar-grammar-update` to regenerate~~ — done

### Phase 3a: Reference Key universal rule (`metaPromptConfig.py`) ✅ Done

1. ~~Extend Channel bullet in CONSTRAINTS: add task-as-lens rule~~ — done
2. ~~Extend Precedence bullet: replace specification-artifact-only statement with universal rule covering all channels~~ — done; covers executable, specification, and delivery channels
3. ~~`make bar-grammar-update` to regenerate; verify rule appears in `bar build` output~~ — done

### Phase 3b: `help_llm` Choosing Channel (`help_llm.go`) ✅ Done

1. ~~Add `renderCrossAxisComposition(w, grammar)` in `help_llm.go`~~ — done
2. ~~Renders "Choosing Channel" section from `natural` + `cautionary` data per channel~~ — done
3. ~~Wire into `renderTokenSelectionHeuristics`~~ — done; call at end after Choosing Directional
4. ~~Fix `TestLLMHelpHeuristicsTokensExist`~~ — done; audience tokens use `audience=token` form (contains `=`, skipped by test)

### Phase 4: ADR-0085 validation ✅ Done

1. ~~Re-run seeds 531, 560, 588, 615 against the updated grammar~~ — done; universal rule present in all outputs
2. ~~Evaluate reframe combinations for quality~~ — done; shellscript+diff, shellscript+sort, adr+pull all derivable from universal rule; score-4 expected for normal subjects
3. ~~Update `process-feedback.md` open recommendations table~~ — done; R40 and F4 marked done; Phase 4 validation section added

### Phase 5: Metadata migration audit ✅ Done (2026-02-26)

Audit result: **no migrations required.** `AXIS_KEY_TO_GUIDANCE` prose and `CROSS_AXIS_COMPOSITION` are complementary, not duplicates — they serve different purposes at different surfaces.

**Findings per source:**

`AXIS_KEY_TO_GUIDANCE` (shellscript, code, adr, codetour, gherkin, sync, commit):
- Each guidance entry is the human-readable description shown in TUI2 and SPA meta panels. It provides broad usage context, exceptions (form-as-lens rescue for `adr+pull`), and audience considerations.
- `CROSS_AXIS_COMPOSITION` is the *structured extract* of the same information — covering only the structurally-broken cases derivable from empirical observation (sim, probe), not the universal-rule cases.
- **Decision: keep guidance prose in place. It is not duplicating `CROSS_AXIS_COMPOSITION`; it is a fuller human-facing narrative of which `CROSS_AXIS_COMPOSITION` is the structured subset.**

`AXIS_KEY_TO_GUIDANCE` — additional tokens listed in prose but not in `CROSS_AXIS_COMPOSITION` (e.g., `shellscript` guidance mentions `pick`, `diff`, `sort` as "avoid"; `codetour` mentions `probe`, `diff`, `plan`):
- These are all derivable from the universal Reference Key rule introduced in Phase 3a — they produce output, just output that the universal rule can generate without explicit guidance.
- **Decision: do not add to `CROSS_AXIS_COMPOSITION`. Cautionary entries are reserved for combinations that produce poor output even with the universal rule (i.e., structurally narrative tasks like `sim` in an executable channel).**

`AXIS_KEY_TO_USE_WHEN` (channel tokens):
- Channel use_when entries describe when to select the channel, not cross-axis interactions.
- **Decision: no migration candidates found.**

`_STATIC_PROMPT_GUIDANCE` / `_STATIC_PROMPT_USE_WHEN` in `staticPromptConfig.py`:
- Task token notes reference internal task distinctions (`sim` vs `simulation` method, `probe` vs `diagnose` disambiguation). No channel/form incompatibilities found.
- **Decision: no migration candidates found.**

Static help text in `help_llm.go`:
- All channel cross-axis guidance is now rendered dynamically from `CROSS_AXIS_COMPOSITION` (Phase 3b). No residual inline cross-axis text found.
- **Decision: no action needed.**

**R2 residual constraint status:** Closed. The prose and structured data are deliberately complementary. R2 was premature — "prose duplication" was a misdiagnosis; the two are different representations for different audiences (human readers vs. structured rendering).

---

## Deferred

- Grammar enforcement for cross-axis combinations — explicitly out of scope for this ADR; the data structure would support it if desired
- Extending `CROSS_AXIS_COMPOSITION` to completeness×method tensions (skim+rigor, max+spike) — score-3 tensions, lower priority
- Surfacing reframe descriptions in TUI2/SPA (would require new UI component)
- Auto-generating `AXIS_KEY_TO_GUIDANCE` prose from `CROSS_AXIS_COMPOSITION` (migration work)
