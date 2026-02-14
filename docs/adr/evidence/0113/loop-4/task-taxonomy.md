# ADR-0113 Loop-4 Task Taxonomy (Generated via Bar Variants)

**Date:** 2026-02-14  
**Method:** `bar build probe full variants`  
**Addendum:** Enumerate 25-30 realistic task types with probability weights

---

## Generated Task Taxonomy

| # | Task Type | Example | Weight | Domain |
|---|-----------|---------|--------|--------|
| T61 | Debug production issue | "The API is returning 500s, investigate" | 10% | Engineering |
| T62 | Review pull request | "Review this PR for the auth service" | 10% | Engineering |
| T63 | Explain code to new teammate | "Walk me through this module" | 8% | Engineering |
| T64 | Design API endpoint | "Design the user registration endpoint" | 7% | Design |
| T65 | Write unit tests | "Add tests for the payment logic" | 7% | Engineering |
| T66 | Plan feature rollout | "Plan the gradual rollout of v2" | 6% | Planning |
| T67 | Analyze error patterns | "Why do we keep seeing these timeouts?" | 6% | Analysis |
| T68 | Create runbook | "Document the database failover procedure" | 5% | Operations |
| T69 | Refactor legacy code | "Clean up this 5-year-old module" | 5% | Engineering |
| T70 | Write technical specification | "Spec out the caching layer" | 5% | Design |
| T71 | Compare frameworks | "Should we use React or Vue?" | 5% | Decision |
| T72 | Draft incident postmortem | "Write up what happened Friday" | 4% | Communication |
| T73 | Estimate project timeline | "How long will the migration take?" | 4% | Planning |
| T74 | Identify security risks | "Audit the auth flow for vulnerabilities" | 4% | Security |
| T75 | Optimize performance | "The queries are too slow, fix them" | 4% | Engineering |
| T76 | Onboard new engineer | "Create onboarding docs for the backend team" | 3% | Team |
| T77 | Deprecate old API | "Plan the sunset of v1 endpoints" | 3% | Planning |
| T78 | Present to leadership | "Explain tech debt to the CTO" | 3% | Communication |
| T79 | Research new technology | "Evaluate if we should adopt Rust" | 3% | Research |
| T80 | Coordinate cross-team effort | "Align frontend and backend on the API" | 2% | Coordination |
| T81 | Write architecture decision record | "Document why we chose Kafka" | 2% | Documentation |
| T82 | Troubleshoot CI/CD failure | "The build keeps failing on main" | 2% | Engineering |
| T83 | Design experiment | "Test if caching improves latency" | 2% | Research |
| T84 | Create data pipeline | "Build the ETL from logs to warehouse" | 2% | Data |
| T85 | Handle customer escalation | "The client is upset about downtime" | 1% | Support |
| T86 | Mentor junior developer | "Help them understand this algorithm" | 1% | Team |
| T87 | Negotiate technical constraints | "We need 99.99% uptime but have budget limits" | 1% | Decision |
| T88 | Write patent application | "Document our novel caching approach" | 1% | Legal |

---

## Sampling Strategy

**Selected for Loop 4:** 15 tasks weighted by frequency + diversity

| Task | Weight | Rationale |
|------|--------|-----------|
| T61 Debug production | 10% | High-frequency, critical |
| T62 Review PR | 10% | High-frequency |
| T63 Explain code | 8% | Common, tests pedagogical |
| T64 Design API | 7% | Design domain coverage |
| T66 Plan rollout | 6% | Planning + risk |
| T67 Analyze errors | 6% | Analysis domain |
| T70 Write spec | 5% | Documentation + design |
| T71 Compare frameworks | 5% | Tests compare token |
| T74 Security risks | 4% | Security domain |
| T75 Optimize performance | 4% | Performance engineering |
| T77 Deprecate API | 3% | Tests migration concepts |
| T78 Present leadership | 3% | Stakeholder communication |
| T80 Cross-team coord | 2% | Coordination domain |
| T83 Design experiment | 2% | Research domain |
| T85 Customer escalation | 1% | Support edge case |

---

## Loop 4 Focus

**Total tasks:** 15  
**Coverage:** Engineering (6), Planning (2), Analysis (1), Design (2), Security (1), Communication (2), Coordination (1)

**Target:** Maintain mean ≥ 4.5 while testing high-frequency tasks

---

*Generated using bar variants form per ADR-0113 Phase 1*
