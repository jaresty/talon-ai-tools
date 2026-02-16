# ADR-0113 Loop-6 Task Taxonomy — Token Guidance Validation

**Date:** 2026-02-15  
**Focus:** Validate newly added token guidance (ADR-0128)  
**Method:** Tasks designed to test probe/pull, show/pull, make/check, scaffold guidance

---

## Task Taxonomy

| # | Task Type | Example | Weight | Targets Guidance |
|---|---|---|---|---|
| T130 | Summarise technical spec | "Summarize this RFC for the team" | 12% | show → pull |
| T131 | List security risks | "What are the security risks in this codebase?" | 10% | probe → pull |
| T132 | Create test plan | "Write a test plan for the login feature" | 9% | make vs check |
| T133 | Identify test gaps | "What test coverage is missing?" | 8% | check vs make |
| T134 | Explain architecture to exec | "Explain our system to the CEO" | 8% | scaffold conflict? |
| T135 | Design new feature | "Design the payments API" | 7% | scaffold conflict? |
| T136 | Extract key decisions | "Pull out the main decisions from this ADR" | 7% | pull guidance |
| T137 | Risk assessment | "How risky is this migration?" | 6% | probe vs pull |
| T138 | Generate options | "What are our deployment options?" | 6% | probe |
| T139 | Document patterns | "Document the error handling patterns" | 5% | show vs pull |
| T140 | Review code quality | "What's the quality of this module?" | 5% | check |
| T141 | Compare tools | "Redis vs S3 for session storage?" | 4% | diff |
| T142 | Explain to junior | "Explain closures to a junior dev" | 3% | scaffold |

---

## Sampling

**Total:** 13 tasks  
**Focus:** Validate token guidance changes

- Extraction tasks (should use pull): T130, T131, T136, T137 (4)
- Test tasks (make vs check): T132, T133 (2)
- Scaffold conflict tests: T134, T135 (2)
- Standard tasks: T138, T139, T140, T141, T142 (5)
