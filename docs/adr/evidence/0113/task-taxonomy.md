# ADR-0113 — Task Taxonomy (Cycle 1)

**Generated via**: `bar build probe full variants` applied as LLM-in-the-loop
**Date**: 2026-02-13
**Method**: Probe analysis of realistic bar use cases; variants form for distinct labelled options with probability weights

---

## Task Taxonomy

| # | Task type | Example phrasing | Domain | Approx. weight |
|---|-----------|-----------------|--------|----------------|
| T01 | Explain a code system or component to a non-technical stakeholder | "explain our auth flow to the PM" | code | 11% |
| T02 | Identify and describe failure modes in a design or implementation | "what could go wrong with this approach?" | analysis | 8% |
| T03 | Plan a refactor or structural migration with constraints | "plan migrating from REST to GraphQL" | planning | 7% |
| T04 | Generate acceptance criteria or BDD scenarios from a feature story | "write Gherkin tests for this user story" | code | 6% |
| T05 | Draft a technical communication for a specific channel/audience | "write a Slack message summarising the release delay" | writing | 6% |
| T06 | Review code for correctness, security, or performance issues | "review this PR for security issues" | code | 6% |
| T07 | Identify cross-cutting concerns (logging, auth, error handling) in a codebase | "where are observability concerns handled inconsistently?" | code | 5% |
| T08 | Produce a risk summary for a release or architectural decision | "what are the risks of deploying this on Friday?" | analysis | 5% |
| T09 | Analyse dependencies between modules or services | "what depends on this module and what breaks if I change it?" | code | 5% |
| T10 | Design a new API, schema, or data model | "design a REST API for the notification service" | design | 5% |
| T11 | Compare two or more technical approaches with tradeoff analysis | "compare Kafka vs SQS for our use case" | analysis | 4% |
| T12 | Evaluate a proposed architecture against known failure patterns | "evaluate this microservices design for split-brain and cascade failure" | analysis | 4% |
| T13 | Write a technical document (ADR, RFC, design doc, runbook) | "write an ADR for choosing Postgres over MongoDB" | writing | 4% |
| T14 | Debug or perform root cause analysis on a failing system or behaviour | "why does the login flow fail intermittently under load?" | code | 4% |
| T15 | Break a feature or epic into implementable tasks | "break down the payment integration into tickets" | planning | 4% |
| T16 | Summarise complex technical content for a specific audience | "summarise this 50-page RFC for the engineering team" | writing | 3% |
| T17 | Surface hidden assumptions in a design or decision | "what assumptions are we making in this architecture?" | analysis | 3% |
| T18 | Create a test plan or identify test coverage gaps | "what tests are missing for this feature?" | code | 3% |
| T19 | Design a system architecture from requirements | "design the high-level architecture for a real-time event pipeline" | design | 3% |
| T20 | Analyse incident or postmortem: root cause, timeline, lessons | "structure the postmortem for last week's outage" | analysis | 2% |
| T21 | Identify patterns and anti-patterns in a codebase | "what patterns or anti-patterns do you see in this module?" | code | 2% |
| T22 | Perform security threat modelling on a component | "threat model the file upload service" | analysis | 2% |
| T23 | Create a decision evaluation framework or scoring criteria | "create criteria to evaluate observability tools" | planning | 2% |
| T24 | Draft onboarding documentation or a technical walkthrough | "write a getting-started guide for our deployment process" | writing | 2% |
| T25 | Identify performance bottlenecks or optimisation opportunities | "profile where the bottlenecks are in this query pipeline" | code | 1% |
| T26 | Produce a prioritised backlog or sequenced roadmap | "prioritise these 15 technical debt items" | planning | 1% |
| T27 | Translate a technical concept across domains or audiences | "explain eventual consistency to someone from a banking background" | writing | 1% |
| T28 | Perform a pre-mortem or inversion exercise on a plan | "assume this project fails — what went wrong?" | analysis | 1% |
| T29 | Create operational or deployment checklists | "create a deployment checklist for this service" | planning | 0.5% |
| T30 | Real-time collaborative brainstorming (multi-turn, stateful) | "let's brainstorm the API design together iteratively" | design | 0.5% |

---

## Sampling Notes

**Corpus for cycle 1**: Selected 25 tasks (T01–T29) proportional to weight; T30 included as known edge case.

**Broad domain coverage**:
- Code: T01, T04, T06, T07, T09, T14, T18, T21, T25
- Analysis: T02, T08, T11, T12, T17, T20, T22, T28
- Writing: T05, T13, T16, T24, T27
- Planning: T03, T15, T23, T26, T29
- Design: T10, T19, T30

**Edge cases included**:
- T07 (cross-cutting concerns — structural lens)
- T28 (pre-mortem / inversion — method-specific task)
- T30 (multi-turn brainstorm — expected out-of-scope)
- T27 (cross-domain translation — audience + explanation)

---

*Phase 1 artifact — feeds Phase 2 skill application*
