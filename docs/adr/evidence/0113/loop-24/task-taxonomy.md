# Loop-24 Task Taxonomy: Voice/Persona Axis Discoverability

**Date:** 2026-02-24
**Focus:** Does bar-autopilot correctly surface voice=, tone=, and audience= tokens?
**Hypothesis:** voice= and tone= tokens are systematically undiscoverable because the "Choosing Persona"
heuristic in help_llm.go only covers audience= tokens and presets — it says nothing about when to use
voice= (speaker identity) or tone= (emotional register) tokens.

## Background

Loop-22 added "Choosing Persona" heuristic and loop-23 validated it at 4.9/5. But that heuristic
covers only *audience routing* — non-technical audiences, presets, and explicit audience= tokens.
The voice= axis (11 tokens) and tone= axis (5 tokens) are absent from any heuristic guidance.

## Task Corpus (15 tasks)

### Group A: Voice Tokens (speaker identity matters)

| # | Task description | Expected persona |
|---|-----------------|-----------------|
| T01 | "Write a user story for the CSV export feature" (from PM perspective) | voice=as-pm |
| T02 | "Give feedback on this UI mockup as a designer would" | voice=as-designer |
| T03 | "Teach me about dependency injection" | voice=as-teacher |
| T04 | "Create a retrospective agenda for the team" (as facilitator) | voice=as-facilitator |
| T05 | "Review this PR from a senior engineer's perspective" | voice=as-principal-engineer |

### Group B: Audience Tokens (target reader matters — heuristic should handle)

| # | Task description | Expected persona |
|---|-----------------|-----------------|
| T06 | "Summarize this tech debt for the CEO" | audience=to-ceo |
| T07 | "Explain this API to a junior developer" | audience=to-junior-engineer |
| T08 | "Present this architecture decision to stakeholders" | audience=to-stakeholders |
| T09 | "Write a status update to our product manager about the delay" | audience=to-product-manager |
| T10 | "Communicate this release to the whole team" | audience=to-team |

### Group C: Tone Tokens (emotional register matters)

| # | Task description | Expected persona |
|---|-----------------|-----------------|
| T11 | "Draft a formal incident report for compliance" | tone=formally |
| T12 | "Send a casual check-in Slack message to the team" | tone=casually |
| T13 | "Give sensitive, supportive feedback on a colleague's code" | tone=gently |

### Group D: No-Persona Controls (persona should NOT be added)

| # | Task description | Expected persona |
|---|-----------------|-----------------|
| T14 | "Analyze the performance bottleneck in this query" | none |
| T15 | "List all the API endpoints in this service" | none |
