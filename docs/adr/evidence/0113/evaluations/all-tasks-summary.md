# ADR-0113 Cycle 1 — All-Task Coverage Summary

**Date**: 2026-02-13

Columns: Task | Bar command constructed | Fitness | Completeness | Skill | Clarity | Overall | Gap type

| # | Task | Bar command | Fit | Comp | Skill | Clarity | **OA** | Gap |
|---|------|-------------|-----|------|-------|---------|--------|-----|
| T01 | Explain system to non-technical stakeholder | `show full time flow walkthrough` | 4 | 3 | 4 | 4 | **4** | persona-usability |
| T02 | Identify failure modes in a design | `probe full fail adversarial variants` | 5 | 5 | 5 | 5 | **5** | — |
| T03 | Plan refactor / migration | `plan full act flow actions` | 4 | 4 | 4 | 4 | **4** | — |
| T04 | Generate Gherkin BDD criteria | `make full act gherkin` | 5 | 5 | 5 | 5 | **5** | — |
| T05 | Draft Slack message summarising decision | `make gist slack` | 4 | 4 | 4 | 4 | **4** | — |
| T06 | Code review for issues | `check full fail adversarial checklist` | 5 | 4 | 5 | 5 | **5** | — |
| T07 | Cross-cutting concerns in a codebase | `probe full struct motifs systemic` | 3 | 3 | 3 | 3 | **3** | missing-token |
| T08 | Risk summary for release/decision | `probe full fail adversarial checklist`* | 3 | 4 | 3 | 4 | **3** | skill-guidance-wrong |
| T09 | Analyse module dependencies | `probe full struct depends mapping` | 5 | 5 | 5 | 5 | **5** | — |
| T10 | Design API / data model | `make full struct scaffold code`* | 3 | 4 | 3 | 3 | **3** | skill-guidance-wrong |
| T11 | Compare two technical approaches | `diff full thing branch table` | 5 | 5 | 5 | 5 | **5** | — |
| T12 | Evaluate architecture against failure patterns | `probe full fail adversarial checklist`* | 4 | 4 | 3 | 4 | **4** | undiscoverable-token |
| T13 | Write ADR / technical document | `make full struct adr` | 5 | 5 | 5 | 5 | **5** | — |
| T14 | Debug / root cause analysis | `probe full fail diagnose origin checklist` | 5 | 5 | 5 | 5 | **5** | — |
| T15 | Break feature into implementable tasks | `plan full act converge actions` | 5 | 5 | 5 | 5 | **5** | — |
| T16 | Summarise complex content for audience | `show gist mean`* | 3 | 3 | 3 | 3 | **3** | skill-guidance-wrong |
| T17 | Surface hidden assumptions | `probe full assume adversarial checklist` | 5 | 5 | 5 | 5 | **5** | — |
| T18 | Create test plan / identify coverage gaps | `check full good fail checklist`* | 3 | 3 | 3 | 3 | **3** | skill-guidance-wrong |
| T19 | Design system architecture | `make full struct scaffold diagram`* | 3 | 4 | 3 | 3 | **3** | skill-guidance-wrong |
| T20 | Incident postmortem | `probe full fail time origin walkthrough` | 4 | 4 | 4 | 4 | **4** | case-form-conflict |
| T21 | Identify patterns / anti-patterns | `probe full motifs systemic mapping` | 4 | 4 | 4 | 4 | **4** | — |
| T22 | Security threat modelling | `probe full fail adversarial checklist`* | 3 | 3 | 3 | 4 | **3** | undiscoverable-token |
| T23 | Create decision evaluation framework | `make full good branch table` | 5 | 5 | 5 | 5 | **5** | — |
| T24 | Onboarding documentation / walkthrough | `make full time flow walkthrough` | 5 | 5 | 5 | 5 | **5** | — |
| T25 | Identify performance bottlenecks | `probe full fail diagnose checklist` | 4 | 4 | 4 | 4 | **4** | — |
| T26 | Produce prioritised backlog / roadmap | `sort full act prioritize table` | 5 | 5 | 4 | 5 | **5** | — |
| T27 | Translate concept cross-domain | `show full mean analog scaffold` | 5 | 4 | 4 | 5 | **4** | persona-usability |
| T28 | Pre-mortem / inversion exercise | `probe full fail adversarial variants`* | 4 | 4 | 3 | 4 | **4** | skill-guidance-wrong |
| T29 | Deployment checklist | `make full act checklist` | 5 | 5 | 5 | 5 | **5** | — |
| T30 | Multi-turn collaborative brainstorming | `make full cocreate` | 2 | 1 | N/A | 2 | **2** | out-of-scope |

`*` = bar-autopilot would likely select a different (weaker) command than shown; command shown is what autopilot would produce given current skill guidance.

---

## Score Distribution

| Score | Count | Tasks |
|-------|-------|-------|
| 5 | 14 | T02, T04, T06, T09, T11, T13, T14, T15, T17, T23, T24, T26, T29, + |
| 4 | 9 | T01, T03, T05, T12, T20, T21, T25, T27, T28 |
| 3 | 6 | T07, T08, T10, T16, T18, T19, T22 |
| 2 | 1 | T30 |

**Well-covered (score 4-5)**: 23/30 (77%)
**Gapped (score ≤3)**: 7/30 (23%), plus T30 as known out-of-scope

---

## Gap Summary by Type

| Gap type | Count | Tasks |
|----------|-------|-------|
| `skill-guidance-wrong` | 5 | T08, T10, T16, T18, T19 (T28 minor) |
| `undiscoverable-token` | 2 | T12, T22 |
| `missing-token` | 1 | T07 |
| `out-of-scope` | 1 | T30 |
| `persona-usability` | 2 | T01, T27 (tooling, not catalog) |
| `form-conflict` | 1 | T20 (`case` form conflict to investigate) |
