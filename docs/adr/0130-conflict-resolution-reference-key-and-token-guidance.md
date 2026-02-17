# ADR 0130: Conflict Resolution via Reference Key and Token Guidance

## Status

Accepted

## Context

ADR-0085 Cycle 7 (seeds 0121-0140, 2026-02-16) found a 40% problematic rate (up from 15% in Cycle 6), driven by two recurring patterns:

1. **Prose-form + exclusive-code-channel conflicts** — forms with structural templates that cannot be rendered in the selected channel format (`log`+`svg`, `spike`+`codetour`, `case`+`gherkin`, `story`+`gherkin`). Scored 1-2. Channel takes precedence per the existing reference key rule, but the rule doesn't say what to do with the form when channel wins — the LLM either ignores the form or produces a broken hybrid.

2. **Specification channels + analysis tasks** — channels that produce specification artifacts (`gherkin`, `codetour`) paired with analysis or comparison tasks (`probe`, `diff`, `check`, `sort`). Scored 1-2. The combination is not incoherent in principle — the analysis could produce findings, which the channel could format as specifications — but the current reference key provides no guidance on this reframing.

Previous cycles applied pair-level documentation fixes (R8, R14 — prose-form conflict lists; ADR-0105 D2 — codetour/gherkin task-affinity). These help at selection time but don't improve execution quality when conflicts do occur, and they don't cover novel combinations not yet documented.

### Why not documentation-only?

Documentation guidance (descriptions, `AXIS_KEY_TO_GUIDANCE` fields, help_llm.go) addresses selection quality — it prevents users from choosing problematic combinations. But:

- The shuffle generates combinations without reading documentation
- Users make mistakes regardless of warnings
- Novel conflict pairs will always arise faster than documentation can enumerate them

A general rule in the reference key handles conflicts gracefully at execution time, for any combination — including ones not yet documented. Documentation guidance and reference key rules are complementary:

- **Reference key**: resolves conflicts that do occur
- **Documentation**: reduces the frequency of conflicts occurring

---

## Decision

### Layer 1: Reference Key Changes (`lib/metaPromptConfig.py`)

Two general rules added to `PROMPT_REFERENCE_KEY`.

#### Rule 1: Form-as-Content-Lens

Extends the existing "channel > form" precedence rule. Current text:

> When form and channel tokens are both present, the channel defines the output format and the form describes the conceptual organization within that format.

Proposed addition:

> When the form's structural template cannot be expressed in the channel's format (e.g., a prose log in SVG, a question-document as a CodeTour JSON), treat the form as a **content lens**: it shapes the informational character of the response — what to emphasize and how to organize ideas — rather than the literal output structure.

**Effect:** Instead of producing a broken hybrid or silently discarding the form, the LLM demotes the form to a content-type hint. Examples:
- `log` + `svg`: SVG output that emphasizes temporal, incremental, annotated information
- `spike` + `codetour`: CodeTour steps organized around questions and learning goals rather than code explanations
- `case` + `gherkin`: Gherkin scenarios following an evidence-to-conclusion arc

**Why this is general:** Any prose form paired with any exclusive-code channel is handled by the same rule without needing to enumerate pairs.

#### Rule 2: Specification Channels Reframe Analysis Tasks

New precedence bullet:

> When a channel produces a specification artifact (gherkin, codetour, adr), analysis or comparison tasks are reframed as: perform the analysis, then express findings as that artifact type. `probe`+`gherkin` = Gherkin scenarios that specify the structural properties or assumptions the analysis revealed. `diff`+`gherkin` = Gherkin scenarios expressing differences as behavioral distinctions. `diff`+`codetour` = CodeTour steps walking through the differences.

**Effect:** Transforms combinations that currently score 2 (incoherent) into a specific, interpretable output pattern. The analysis task provides the substance; the specification channel provides the artifact form.

**Why this is general:** Covers `probe`/`diff`/`check`/`sort` with `gherkin`/`codetour`/`adr` without enumerating every pair.

---

### Layer 2: Token Documentation Guidance (`lib/axisConfig.py`, `internal/barcli/help_llm.go`)

Warns at selection time, complementing the reference key's execution-time resolution.

#### R17 — Prose-form channel conflict documentation

Add `AXIS_KEY_TO_GUIDANCE` entries and description notes for:

| Token | Axis | Conflict | Evidence |
|-------|------|----------|----------|
| `log` | form | svg, diagram, codetour, gherkin, shellscript, html | seed_0126 (score 1) |
| `spike` | form | codetour, shellscript, svg, html, diagram, gherkin | seed_0123 (score 2) |
| `case` | form | gherkin, codetour, shellscript, svg, html, diagram | seed_0133 (score 1) |
| `story` | form | gherkin (already in description; surface as warning) | seed_0122 (score 2) |

These extend the documented prose-form conflict list from R14 (`questions`, `recipe`).

Add all four to `bar help llm` § Composition Rules § Prose-form conflicts list.

#### R18 — Gherkin task-affinity guidance

Strengthen `AXIS_KEY_TO_GUIDANCE` for `gherkin` to reflect the Layer 1 reframing:

> "Outputs only Gherkin Given/When/Then syntax. Primary use: `make` tasks creating acceptance tests or feature specifications. With analysis tasks (probe, diff, check, sort), output is reframed as Gherkin scenarios that specify the analyzed properties — the analysis becomes evidence; scenarios express what should be true given that evidence. Avoid with prose-structure forms (story, case, log, questions, recipe)."

Update `bar help llm` § Incompatibilities § Channel task-affinity.

#### R19 — Codetour audience-affinity guidance

Add to `AXIS_KEY_TO_GUIDANCE` for `codetour`:

> "Produces a VS Code CodeTour JSON file for interactive code walkthroughs in VS Code. Requires a developer audience. Avoid with: manager, PM, executive, CEO, stakeholder, analyst, designer audiences — these roles do not use VS Code CodeTour files."

Evidence: seed_0132 (fix+codetour+to managers, score 2). The reference key cannot resolve this — the artifact is technically produced correctly; the problem is audience-appropriateness, a user-selection concern.

#### R20 — Commit form depth-conflict guidance

Add to `AXIS_KEY_TO_GUIDANCE` for `commit`:

> "Produces a conventional commit message (type: scope header + optional body). Commit messages are brief — avoid `deep` or `max` completeness and complex directionals (fip rog, fly rog, bog, fog). Best with `gist` or `minimal` completeness."

Evidence: seed_0121 (make+deep+commit+fip rog, score 3). Not incoherent — `commit` wins cleanly; `deep` and `fip rog` are wasted tokens. Reference key cannot help here because execution is technically correct; the issue is wasted tokens from a user-selection error.

#### R21 — Skim + complex directional depth-tension guidance

Add to `AXIS_KEY_TO_GUIDANCE` for `skim` (and consider `minimal`):

> "Quick-pass constraint. Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog) that require structural depth and sustained examination. Use with simple directionals (jog, rog) or none."

Evidence: seed_0138 (sort+skim+bog, score 2). The reference key has no principled basis to choose between contradictory depth signals — both constraints are valid. Prevention at selection time is the right intervention.

---

### Files to Change

| File | Changes |
|------|---------|
| `internal/barcli/render.go` | Extend Form bullet (R17 Layer 1); add specification-channel precedence bullet (R18 Layer 1) — **CLI prompts use this version** |
| `lib/metaPromptConfig.py` | Same changes as render.go — Python/API path uses this version; must stay in sync |
| `lib/axisConfig.py` | Add `AXIS_KEY_TO_GUIDANCE` entries for log, spike, case, story, gherkin, codetour, commit, skim |
| `internal/barcli/help_llm.go` | Update § Composition Rules § Prose-form conflicts; update § Incompatibilities § Channel task-affinity |
| `internal/barcli/embed/prompt-grammar.json` | Regenerate after axisConfig changes |

---

## Consequences

### Positive

- **Reference key rules are general**: cover novel combination types not yet documented, reducing the need to enumerate pairs in future cycles
- **Two-layer approach is complementary**: documentation reduces selection errors; reference key handles errors that occur anyway
- **Execution quality improves for existing failures**: combinations that currently score 1-2 (log+svg, probe+gherkin) become interpretable outputs rather than broken hybrids
- **Specification-channel reframing opens creative combinations**: probe+gherkin, diff+codetour become valid patterns, not just failures to avoid
- **Documentation catches what reference key can't**: audience mismatches (R19), wasted tokens (R20), depth contradictions (R21) are prevented at selection time

### Tradeoffs

- **Content-lens demotion is lossy**: when a form degrades to a content hint, users may not realize the form's structural template wasn't applied. The output is coherent but different from what a user explicitly requesting `log` form might expect.
- **Specification reframing may surprise users**: a user selecting `probe`+`gherkin` for conceptual analysis may not expect Gherkin scenario output. The reframing is principled but not obvious.
- **Some conflicts remain unresolvable**: `shellscript`+`presenterm`, audience mismatches (R19), and depth contradictions (R21) cannot be resolved by reference key rules — documentation guidance is the only intervention.

### Risks

- **LLM compliance**: reference key additions are instructions to the LLM; adherence depends on model behavior. The content-lens demotion and specification reframing rules are new patterns that may not be followed consistently across models or temperatures.
- **Overgeneralization**: the specification-channel reframing rule covers `adr` channel + any analysis task. `probe`+`adr` may produce valid ADRs, but the results should be validated in Cycle 8 before treating the pattern as established.

### Validation

Run ADR-0085 Cycle 8 after applying these changes:
- Re-evaluate seeds that exhibited conflicts in Cycle 7 (0122, 0123, 0126, 0127, 0133) against the new reference key
- Generate 20 fresh seeds with specific attention to form/channel and gherkin/task combinations
- Target: conflict rate ≤10%, average score ≥3.7

---

## Amendments

### Amendment 1: help_llm.go § Incompatibilities cleanup

During implementation review, the § Incompatibilities section of `help_llm.go` was found to contain four blocks of per-token guidance that duplicate `AXIS_KEY_TO_GUIDANCE` (rendered in the same document's "Token Guidance" section) or `PersonaGuidance` (available in the TUI):

| Block removed | Reason |
|---|---|
| Line 667: "Similarly, form tokens `code`, `html`, and `shellscript` are output-exclusive" | Misclassification — these are channel tokens, already covered by the preceding sentence "all channel tokens are output-exclusive" |
| Task-affinity restrictions (`codetour`, `gherkin`, `code`/`html`/`shellscript`, `adr`) | All per-token notes already exist in `AXIS_KEY_TO_GUIDANCE["channel"]` (or moved there — see below) |
| Prose-output-form conflicts (`log`, `spike`, `case`, `story`, `faq`, `recipe`, `questions`) | All already in `AXIS_KEY_TO_GUIDANCE["form"]`, rendered in the "Token Guidance" section |
| Tone/channel register conflicts (`formally`) | Already in `PersonaGuidance["tone"]["formally"]` in `lib/personaConfig.py`, shown in TUI at selection time |

The `adr` channel guidance was not yet in `AXIS_KEY_TO_GUIDANCE` — it was moved there from the removed block:

> "Task-affinity for decision-making tasks (`plan`, `probe`, `make`). The ADR format (Context, Decision, Consequences) is a decision artifact — it does not accommodate tasks that produce non-decision outputs. Avoid with `sort` (sorted list), `pull` (extraction), `diff` (comparison), or `sim` (scenario playback)."

**Files changed:** `lib/axisConfig.py` (add `adr` to `AXIS_KEY_TO_GUIDANCE["channel"]`), `internal/barcli/help_llm.go` (remove four blocks), regenerate grammar.

---

## Evidence

- `docs/adr/evidence/0085/evaluations-seeds-0121-0140.md`
- `docs/adr/evidence/0085/recommendations-seeds-0121-0140.yaml`
