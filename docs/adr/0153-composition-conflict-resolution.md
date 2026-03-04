# ADR-0153 – Composition Conflict Resolution

Status: Draft
Date: 2026-03-04
Owners: Architecture Review

## Context

Token descriptions in `lib/axisConfig.py` are clean after ADR-0152. The
remaining quality problem is structural: certain token combinations produce
rendered prompts where two CONSTRAINTS bullets make incompatible demands on the
same dimension of the response (depth, range, breadth). The model receives no
declared resolution and must reconcile the conflict itself — inconsistently.

Two interference patterns were identified via spill analysis of prompts
rendered for tokens that carry cautionary entries in `CROSS_AXIS_COMPOSITION`:

**Pattern A — Default completeness conflicts with format-constrained form
tokens.**

`bar build make commit` renders:

```
- Completeness (full 全): The response provides a thorough answer for normal
  use, covering all major aspects without needing every micro-detail.
- Form (commit 提): The response structures ideas as a conventional commit
  message with a short type or scope line and an optional concise body.
```

`full` is the system default when no completeness token is specified. `commit`
format is structurally incapable of satisfying `full` coverage. Every `make
commit` prompt already contains this contradiction before `max` or `deep` are
involved — yet the existing cautionary entries in `CROSS_AXIS_COMPOSITION` only
flag `max` and `deep`, not `full`. The default creates the conflict silently.

**Pattern B — Brevity completeness tokens conflict with depth-requiring
directional tokens.**

`bar build make gist fig` renders two independent bullets: gist instructs
"touch main points once without exploring every detail"; fig instructs "span
both abstract/general and concrete/specific dimensions." Spanning both
dimensions requires the depth that gist prohibits. The CONSTRAINTS section
presents them as orthogonal guardrails; they are not. The model resolves the
contradiction ad hoc, producing score-3 output that neither constraint
intended.

The same interference occurs with `skim + fog`, `gist + bog`, and the full
matrix of brevity completeness tokens (`gist`, `skim`) × spectrum directionals
(`fig`, `bog`, `fog`, and all nine compound directionals).

## Problem

The CROSS_AXIS_COMPOSITION cautionary entries correctly identify these
combinations as problematic and surface warnings in the TUI at selection time.
However, they have no effect on the rendered prompt. The model that executes
the prompt receives no information about the conflict or its resolution. The
fix must act at render time, not just at selection time.

Two separate mechanisms are required because the two patterns have different
root causes:

- Pattern A is caused by the default completeness being semantically
  incompatible with certain form tokens. The fix is at default-injection time.
- Pattern B is caused by two explicitly chosen tokens being incompatible. The
  fix is at constraint-rendering time.

## Decision

**Phase 1 — Default completeness override for format-constrained form tokens
(T-1)**

Add a `default_completeness` field to the form token metadata structure in
`lib/axisConfig.py`. Form tokens that are structurally brevity-constrained
declare their preferred default. `commit` declares `gist`. The render pipeline
(`internal/barcli/render.go` or the equivalent Go build path) checks this
field when selecting the default completeness: if the active form token
declares a `default_completeness` and the user has not specified a completeness
token, inject the declared default instead of `full`.

Scope: `commit` is the only form token that needs this for now. Other
brevity-constrained form tokens (`bug`, `checklist`) should be evaluated but
are not blocked on this ADR.

Validation: `bar build make commit` renders `gist` completeness, not `full`.
`bar build make gist commit` still renders `gist` (user-specified, unchanged).
`bar build make full commit` still renders `full` (user-specified, unchanged).
Grammar export and tests pass.

**Phase 2 — Conflict resolution note injected into rendered prompts (T-2)**

Extend `CROSS_AXIS_COMPOSITION` cautionary entries with an optional
`render_note` field. When bar renders a prompt and detects a cautionary pair,
it appends the `render_note` beneath the conflicting constraint bullet as an
indented subordinate line. The note declares which constraint governs when they
conflict.

Example rendered output for `make gist fig`:

```
- Completeness (gist 略): The response offers a short but complete answer or
  summary that touches the main points once without exploring every detail.
  ↳ Conflict: gist constrains depth — brevity governs over directional range.
- Directional (fig 抽): The response modifies the task to span both abstract
  and concrete dimensions...
```

The `render_note` field is optional: existing cautionary entries without it
render unchanged. New entries for the brevity × spectrum-directional matrix
must be added with `render_note` values as part of this task.

Validation: prompts for `gist + fig`, `gist + bog`, `skim + fog`, and a
representative compound directional render the conflict note. Prompts for
non-cautionary pairs render unchanged. Grammar export and tests pass.

## Salient Tasks

- **T-1** — Add `default_completeness` to form token metadata; implement
  override in render pipeline; `commit` declares `gist`
- **T-2** — Add `render_note` field to `CROSS_AXIS_COMPOSITION` cautionary
  entries; implement render-time injection; populate `render_note` for brevity
  × spectrum-directional matrix (`gist`/`skim` × `fig`, `bog`, `fog`, and nine
  compound directionals)

## Risks

| Risk | Mitigation |
|------|------------|
| `default_completeness` override surprises users who expect `full` from `make commit` | TUI should show the effective completeness token when an override is active; surfaced at selection time |
| `render_note` adds visual noise to prompts for combinations users intentionally chose | Note is a single indented line, subordinate to the constraint; not a warning block |
| `render_note` text goes stale as token descriptions evolve | `render_note` is co-located with the cautionary entry it annotates; update is part of the same diff as any description change |
| Phase 1 changes `bar build make commit` default — breaks existing tests that snapshot that prompt | Grammar export tests must be updated as part of T-1 |

## Metadata

Analyzed: 2026-03-04
Method: Spill analysis of rendered prompt output for cautionary-cluster tokens
Scope: `internal/barcli/render.go` default injection + CROSS_AXIS_COMPOSITION
  render_note field + `lib/axisConfig.py` form token metadata
