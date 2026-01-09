# 0070 – Static prompt task/method separation

## Status
Proposed

## Context
- Static prompts are meant to express the **task/outcome** portion of a recipe, while the contract axes (especially `form` and `method`) carry presentation and procedural instructions (ADR 040, ADR 050).
- A recent audit of `lib/staticPromptConfig.py` identified 73 static prompts; 29 embed detailed "apply this model/analysis" instructions or procedural verbs in their descriptions (for example `math`, `tune`, `bridge`, `constraints`, `effects`, `com b`).
- These blended prompts duplicate method semantics, make it harder to reason about overrides, and dilute the expectation that static prompts describe what to produce rather than how to produce it.
- Duplicate definitions near the end of `staticPromptConfig` (for example `bridge`, `constraints`, `effects`) amplify drift risk when semantics change.

## Decision
- Restrict static prompt definitions to task/outcome descriptions; any procedural guidance ("apply", "outline steps", named analytical frameworks) must live in the method axis or another dedicated axis.
- Immediately refactor the 29 method-shaped static prompts (`how`, `math`, `orthogonal`, `bud`, `boom`, `meld`, `order`, `logic`, `probability`, `recurrence`, `map`, `mod`, `dimension`, `rotation`, `reflection`, `invert`, `graph`, `grove`, `dub`, `drum`, `com b`, `tune`, `melody`, `constraints`, `effects`, `bridge`, plus the duplicated `constraints`, `effects`, `bridge` entries near the file tail) by extracting their procedural aspects into explicit method tokens or method defaults. Static prompt descriptions must describe only the deliverable; retire the static prompt entirely when an axis combination already covers the use case.
- Add repository guardrails (lint/test) that fail when a static prompt description introduces procedural language without matching method defaults, or when a prompt lacks axis defaults but still encodes a method.
- Remove duplicate static prompt entries so the SSOT contains exactly one definition per token before or during the refactor—no phased staging.

## Rationale
- Enforcing the separation keeps the grammar composable: operators can combine a task (static prompt) with any method or form without double-encoding behaviour.
- Moving procedural guidance onto the method axis improves discoverability and validation—guardrails already reason about axis tokens.
- Linting prevents future regressions and documents the contract for contributors.
- Deduplicating entries ensures migrations touch a single source of truth for each prompt.

## Consequences
- Static prompt authors will update or retire roughly thirty prompts so that tasks remain outcome-focused; method axis documentation will expand with the extracted tokens.
- Help hub, CLI grammar exports, and cheat sheets will show clearer boundaries between tasks (static prompts) and methods, reducing operator confusion about "what vs how".
- Guardrail suites gain a new check (run via `make axis-guardrails`) that enforces the task-only rule; contributors will need to satisfy it before merging static prompt changes.
- Downstream tools that relied on the blended prompts may need minor updates to reference the new method tokens, but benefit from more explicit recipes overall.
