# ADR-0113 — Gap Catalog (Cycle 1)

**Date**: 2026-02-13
**Tasks evaluated**: 30 (T01–T30)
**Tasks with gaps (score ≤3)**: 7 (T07, T08, T10, T16, T18, T19, T22) + T30 (out-of-scope)
**Additional findings**: 2 supplementary tooling/compat issues (SF-01, SF-02)

---

## Gap Type 1: Missing Token

### G-01 — No scope token for cross-cutting concerns

**Tasks**: T07
**Axis**: scope
**Severity**: High (5% of tasks; unique structural lens with no substitute)

No scope token specifically foregrounds concerns that span module boundaries
(logging, auth, error handling, observability, caching). `struct` covers structural
arrangements, `motifs` covers recurring patterns — together they approximate the concept
but neither precisely targets the horizontal-cut nature of cross-cutting concerns.

The user question "where are observability concerns handled, and how consistently?" has no
single token combination that directly expresses "focus on cross-boundary concerns and their
consistency."

**Proposed token**: `cross` (scope axis)
> The response focuses on concerns that span multiple modules or components — patterns
> applied repeatedly across the codebase (logging, error handling, authentication,
> observability, caching) — examining their consistency, distribution, and coupling
> characteristics. Use when the question is about where a concern lives across the system,
> not just within one place.

---

## Gap Type 2: Undiscoverable Token

### G-02 — `inversion` not surfaced for architecture evaluation against failure patterns

**Tasks**: T12
**Axis**: method
**Severity**: Medium (4% of tasks; affects architectural reviews specifically)

The `inversion` method ("beginning from undesirable or catastrophic outcomes, asking what
would produce or amplify them, then working backward") is precisely suited for evaluating
architectures against named failure patterns. But the skill heuristics only list it under
"Root cause analysis" diagnostics, not under architecture evaluation. Bar-autopilot routes
this task to `adversarial` from the Risk Assessment usage pattern, missing the richer
backward-reasoning approach that `inversion` provides.

**Recommended fix**: Add to `inversion` method description:
> Well-suited for architecture evaluation: starting from known failure modes (cascade
> failure, split-brain, thundering herd, data loss scenarios) and asking which design
> choices create or amplify them. Use when the failure patterns are named and the
> question is whether the architecture protects against them.

### G-03 — `actors` method not surfaced for security threat modelling

**Tasks**: T22
**Axis**: method
**Severity**: Medium (2% of tasks; affects all security threat modelling work)

The `actors` method ("focusing on the entities involved — who they are, what motivates
them, and how their roles and goals interact") directly maps to the threat-actor dimension
of security threat modelling. But the method description doesn't mention security or threat
actors as a use case. Bar-autopilot routes threat modelling to `probe+fail+adversarial`,
which finds weaknesses without reasoning about who would exploit them.

**Recommended fix**: Add to `actors` method description:
> Well-suited for security threat modelling: identifying threat actors (external attackers,
> insiders, automated bots, compromised dependencies), their motivations (data theft,
> service disruption, privilege escalation), and how their capabilities interact with system
> attack surfaces. Use alongside 'adversarial' for a complete threat model.

---

## Gap Type 3: Skill Guidance Wrong

### G-04 — Risk extraction routed to probe instead of pull

**Tasks**: T08
**Axis**: task selection
**Severity**: Medium (5% of tasks; affects all "what are the risks?" requests)

The "Risk Assessment" usage pattern uses `probe` for all risk tasks. But "produce a risk
summary" is extraction (`pull`), not open-ended analysis (`probe`). The distinction:
`pull` = extract a targeted subset; `probe` = analyze broadly and surface implications.

A risk checklist is a targeted subset — it should be `pull+fail+risks`, not `probe+fail+adversarial`.

**Recommended fix**: Split the Risk Assessment usage pattern into two subtypes:
- Risk extraction: `pull + fail + risks checklist` (for "what are the risks?", "risk summary")
- Risk analysis: `probe + fail + adversarial` (for "how risky is this?", "assess risk posture")

### G-05 — `scaffold` form wrongly selected for design artifact tasks

**Tasks**: T10, T19
**Axis**: form selection
**Severity**: High (8% of tasks; affects all API/schema/architecture design requests)

The form heuristic "Building understanding → scaffold" fires for design tasks, even though
`scaffold` is explicitly for learning-oriented explanation (first principles, gradual introduction,
analogies for a student-level audience). When the task is `make` and the output is a design
artifact (code, diagram), `scaffold` creates a conflicting prompt: the LLM is instructed to
both produce an artifact (make) and explain it from first principles (scaffold).

The correct behavior: when `make+code` or `make+diagram`, omit form tokens unless the user
explicitly wants an accompanied explanation.

**Recommended fix**: Add to form selection heuristics:
> Do not apply `scaffold` when `make` task produces a design artifact.
> `scaffold` is for explanation (show/probe); not for artifact production (make).
> When task=make with code/diagram/adr channel: omit form tokens.

### G-06 — Summarisation routed to show instead of pull

**Tasks**: T16
**Axis**: task selection
**Severity**: Medium (3% of tasks; affects summarisation of documents/RFCs/specs)

Bar-autopilot routes summarisation to `show` (explain or describe) because summarisation
feels like explanation. But summarisation is extraction: given a long document (SUBJECT),
pull out a shorter version. `pull+gist+mean` more precisely instructs the LLM to extract
the conceptual core from the source material.

The key heuristic: if a long SUBJECT document is being compressed → `pull`; if a concept
is being explained without a specific long source → `show`.

**Recommended fix**: Add to Usage Patterns:
> Summarisation / Extraction: `bar build pull gist [scope]`
> Use pull when the task is to compress a long source document into a shorter form.
> Heuristic: if SUBJECT is a long document to be compressed, prefer pull over show.

### G-07 — Test plan/coverage tasks need disambiguation by intent

**Tasks**: T18
**Axis**: task selection (create vs evaluate)
**Severity**: Medium (3% of tasks; affects testing-related tasks)

"Create a test plan" and "identify coverage gaps" are different operations:
- Gap analysis: `check + good + fail checklist` (evaluate existing against criteria)
- Plan creation: `make + act + fail checklist` (produce a test plan artifact)

Bar-autopilot routes both to check-based quality evaluation because "testing" is associated
with checking. The distinction: is the user evaluating something that exists, or creating
something new?

**Recommended fix**: Add disambiguation to Usage Patterns for testing tasks:
> Test coverage gap analysis: `check full good fail checklist`
> Test plan creation: `make full act fail checklist`
> Heuristic: "what's missing?" = check; "write/create a plan" = make.

### G-08 (minor) — Pre-mortem / inversion exercise lacks usage pattern

**Tasks**: T28
**Axis**: method discoverability
**Severity**: Low (1% of tasks; but inversion is underutilised generally)

The pre-mortem technique ("assume the project has failed — what went wrong?") is a
well-known planning tool with no dedicated usage pattern in bar help llm. Bar-autopilot
routes to `adversarial` instead of the more precise `inversion`, which is designed
exactly for backward-from-catastrophe reasoning.

**Recommended fix**: Add a "Pre-mortem / Inversion" usage pattern:
> Pattern: `bar build probe full fail inversion variants`
> Use when assuming failure and working backward to identify causes.

---

## Gap Type 4: Out of Scope

### G-09 — Multi-turn brainstorming

**Tasks**: T30
**Severity**: Documented boundary

Bar produces single-turn structured prompts. Real-time stateful collaborative brainstorming
requires multi-turn interaction that bar's grammar cannot represent. The `cocreate` form is
the closest approximation.

**Recommended fix**: Add scope note to `bar help llm`:
> Bar produces single-turn structured prompts. It does not model multi-turn interactive
> sessions. Use `cocreate` form for responses structured to invite iteration, then
> continue the conversation manually.

---

## Tooling / Compatibility Issues (Not Catalog Gaps)

### SF-01 — Persona token slug format inconsistency

Audience tokens reject slug format in key=value syntax (`audience=to-product-manager` fails;
requires `to product manager` with spaces or shorthand before static token which hangs).
This prevents bar-autopilot from reliably applying audience persona.

**Action**: Fix slug normalization for persona token key=value syntax.

### SF-02 — `case` form hangs with `fail+time+origin` combination

`bar build probe full fail time origin case` hangs. Substituting `walkthrough` for `case`
works. The incompatibility is undocumented and the failure mode is a hang rather than a clean error.

**Action**: Investigate grammar incompatibility rules for `case` form; fix to fail cleanly with error message.
