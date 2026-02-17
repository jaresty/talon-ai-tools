# ADR-0113 Loop-8 Task Taxonomy — Specialist Form Token Coverage

**Date:** 2026-02-17
**Focus:** Validate specialist/exotic form tokens — whether bar-autopilot surfaces them correctly
**Method:** Tasks designed to naturally trigger specific form tokens; evaluate selection and output

---

## Motivation

Loops 1-7 covered: baseline gaps, scope/method tokens, guidance (ADR-0128), directionals, personas.
Specialist form tokens have never been systematically evaluated for discoverability or fitness.

The form token catalog includes many specialist tokens with non-obvious use cases:
`wardley`, `wasinawa`, `spike`, `cocreate`, `ladder`, `taxonomy`, `facilitate`, `recipe`,
`socratic`, `merge`, `codetour`, `quiz`, `visual`, `cards`.

Key question: does bar-autopilot surface these tokens for the tasks they were designed for,
or does it default to safer/more common forms (checklist, walkthrough, bullets, variants)?

---

## Task Taxonomy

| # | Task Type | Example | Weight | Target Form |
|---|-----------|---------|--------|-------------|
| T170 | Competitive landscape Wardley map | "Map our product's components on a Wardley evolution axis" | 6% | wardley |
| T171 | Post-incident reflection | "We just shipped code that slowed queries by 300%. Reflect on what happened." | 7% | wasinawa |
| T172 | Technology investigation spike | "Should we adopt GraphQL for our API? Frame this as a research spike." | 5% | spike |
| T173 | Iterative collaborative design | "Help me work through the API design incrementally with decision points" | 5% | cocreate |
| T174 | Abstraction-ladder diagnosis | "Help me understand this performance issue by stepping up and down abstraction levels" | 4% | ladder |
| T175 | Error type classification | "Classify all the types of errors that can occur in our payment service" | 5% | taxonomy |
| T176 | Technical retrospective facilitation | "Plan and facilitate a retrospective on our Q4 deployment failures" | 5% | facilitate |
| T177 | Process as recipe | "Document how to set up our dev environment in a recipe format with a custom mini-language" | 3% | recipe |
| T178 | Learn via Socratic questioning | "Help me understand event sourcing through questions, not explanation" | 4% | socratic |
| T179 | Merge multiple documents | "Combine these three architecture docs into a single coherent specification" | 4% | merge |
| T180 | VS Code CodeTour creation | "Create a CodeTour for our authentication flow" | 3% | codetour (channel) |
| T181 | Quiz-based knowledge check | "Test my understanding of CQRS through a quiz" | 3% | quiz |
| T182 | Abstract visual layout | "Show the relationship between microservices as an abstract visual layout" | 4% | visual |

---

## Sampling Strategy

All 13 tasks evaluated (small corpus, specialist focus).
Each task run through bar-autopilot to assess whether the correct form token is selected.
Evaluation asks: did the skill surface the specialist token, or fall back to a generic form?

---

## Coverage Focus

The central hypothesis: bar-autopilot defaults to generic forms (checklist, walkthrough, bullets,
variants, table) when specialist forms are more appropriate. If confirmed, this reveals a
skill guidance gap: specialist forms need clearer usage patterns or heuristics in bar help llm.

The secondary question: when specialist forms ARE selected, does the resulting prompt actually
serve the task well? (Some specialist tokens may be under-described.)
