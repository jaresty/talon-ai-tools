# ADR-0113 Loop-5 Task Taxonomy — Realistic User Tasks

**Date:** 2026-02-14  
**Focus:** Realistic user tasks to validate new scope prompt performance  
**Method:** Tasks sampled from actual software engineering workflows (not designed to test scopes)

---

## Task Taxonomy

| # | Task Type | Example | Weight |
|---|---|---|---|
| T110 | Debug why production is slow | "The API latency spiked, find the bottleneck" | 12% |
| T111 | Plan a database migration | "How do we migrate from Postgres to DynamoDB?" | 10% |
| T112 | Review architecture decision | "Should we use Kafka or RabbitMQ?" | 9% |
| T113 | Explain code to new team member | "Walk me through the auth flow" | 8% |
| T114 | Identify security vulnerabilities | "What could an attacker exploit?" | 8% |
| T115 | Write rollout plan | "How do we deploy this without downtime?" | 7% |
| T116 | Refactor legacy code | "Clean up this 500-line function" | 7% |
| T117 | Analyze test failures | "Why do these tests keep flaking?" | 6% |
| T118 | Design API contract | "Define the REST endpoints for this feature" | 6% |
| T119 | Investigate error patterns | "Are we handling errors consistently?" | 5% |
| T120 | Compare implementation options | "Redis vs Memcached for caching?" | 5% |
| T121 | Document system behavior | "How does the retry logic work?" | 4% |
| T122 | Assess technical debt | "How bad is this module?" | 4% |
| T123 | Validate configuration | "Will this config work in prod?" | 4% |
| T124 | Trace request flow | "Follow a request through the system" | 3% |

---

## Sampling Strategy

**Total:** 15 tasks  
**Weighted by:** Frequency + domain diversity  

Coverage across domains:
- Debugging/investigation: 3 tasks (T110, T117, T119)
- Architecture/design: 4 tasks (T112, T118, T120, T122)
- Planning/execution: 3 tasks (T111, T115, T116)
- Explanation/documentation: 2 tasks (T113, T121)
- Security/risk: 2 tasks (T114, T123)
- System understanding: 1 task (T124)

**Goal:** See how the new scope descriptions guide selection for realistic tasks, not test scope distinctions artificially.

---

*Loop-5 realistic task taxonomy for scope prompt validation*
