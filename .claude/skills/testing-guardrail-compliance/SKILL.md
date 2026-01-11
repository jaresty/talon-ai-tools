---
name: testing-guardrail-compliance
description: Triggers when work touches property harness guardrails, analytics probes, or hydration telemetry; documents required probe usage and verification steps.
---

# Testing Guardrail Compliance

## Trigger Conditions
- The task updates property harness probes, hydration helpers, or telemetry assertions.
- The task needs guidance on keeping analytics tests compliant without inspecting raw payload shapes.

## Guardrail Priorities
- Harness-owned probes, helpers, and sentinel assertions validate hydration and telemetry outcomes.
- Tests avoid reading vendor payload internals such as `productID` or `shipments[].finalPrice`; focus on computed structures and helper success.
- Coverage checks confirm arrays, rule-component execution, or surfaced harness errors instead of data payload minutiae.

## Documentation Discipline
- When refactoring tests away from analytics payloads, record the reasoning and resulting guardrails in the ADR work-log entry associated with the change.

## Required Test Runs
- After adjusting probes or guard configurations, run the targeted suites listed below to ensure guardrail compliance:
  - `npx vitest run scripts/__tests__/property/property-hydration-coverage.test.ts`
  - Additional focused suites mentioned in the change description when probes expand to new surfaces.

## Failure Handling
- If guardrail suites fail, address probe coverage or scenario hydration gaps before merging.
- When telemetry expectations need updates, align them with computed-state structures rather than vendor payload keys.
