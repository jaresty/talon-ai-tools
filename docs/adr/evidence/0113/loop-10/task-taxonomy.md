# ADR-0113 Loop-10 Task Taxonomy — Output Channel Discoverability

**Date:** 2026-02-17
**Focus:** Channel token selection by bar-autopilot

---

## Hypothesis

Like form tokens (loop-8), channel tokens may be systematically undiscoverable
unless users name them explicitly. Explicit-name channels (adr, shellscript,
gherkin, jira, slack, svg, html, presenterm) will score 5/5; ambiguous or
tool-specific channels (sync, sketch, plain, remote) will score ≤3/5.

---

## Task Sample (13 tasks, T183–T195)

| # | Task description | Target channel | Explicit name? |
|---|-----------------|----------------|----------------|
| T183 | Write an ADR for choosing PostgreSQL over MongoDB | adr | Yes |
| T184 | Create a Presenterm slide deck for the architecture review | presenterm | Yes |
| T185 | Write a shell script to bootstrap our dev environment | shellscript | Yes |
| T186 | Write Gherkin acceptance criteria for the payment flow | gherkin | Yes |
| T187 | Format this documentation page for Jira | jira | Yes |
| T188 | Create a session plan for tomorrow's design sprint kickoff | sync | No |
| T189 | Create a D2 diagram of our microservices architecture | sketch | Partial |
| T190 | Give me a plain-prose explanation of our auth model, no lists or bullets | plain | Partial |
| T191 | Generate an SVG icon representing data flow between services | svg | Yes |
| T192 | Write a Slack message announcing our v2.0 release | slack | Yes |
| T193 | Help me plan a remote-delivery retrospective for our distributed team | remote | No |
| T194 | Show me the auth module as a VS Code CodeTour for onboarding | codetour | Yes |
| T195 | Write an HTML documentation page for our REST API endpoints | html | Yes |

---

## Domain Coverage

- Code tooling: T185 (shellscript), T194 (codetour), T195 (html)
- Documentation: T183 (adr), T184 (presenterm), T187 (jira), T190 (plain)
- Visual output: T189 (sketch/D2), T191 (svg)
- Collaboration: T188 (sync), T192 (slack), T193 (remote)
- Specification: T186 (gherkin)
