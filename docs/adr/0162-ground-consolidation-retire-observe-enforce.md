# ADR-0162: Consolidate ground/observe/enforce — Retire observe and enforce

## Status
Accepted

## Context

The method axis has three tokens — `ground`, `observe`, `enforce` — that form a compositional
verification pipeline:

- `ground`: treat governing intent I as fixed; construct falsifiable validation artifact V; produce
  output O satisfying V (protocol: I → V → O)
- `enforce`: express V using the strongest enforceable mechanism available (executable code written
  to files > formal notation > structured criteria > prose)
- `observe`: if V is executable, run it; present empirical evidence E before deriving claims C

These three are often used together, and `observe` already cross-references `ground` explicitly in
its definition ("when ground constraint is also present, V may be executed to obtain E"). However,
because they are separate tokens they consume three of the available method slots in `bar build`,
leaving no room for other methods when the full verification pipeline is needed.

Additionally, a review of the definitions surfaced two design issues:

1. **`enforce` uses maximize semantics, not minimize semantics.** It says "select the strongest
   available mechanism" — but the right pressure is "select the strongest *necessary* mechanism."
   Over-specifying V (e.g. requiring executable tests when a type annotation would close the gap)
   is waste, not rigour.

2. **`observe`'s conditional hookup into `ground` belongs in `ground` itself.** Whether to run V
   depends entirely on whether V is executable — a property of the medium, not a separate operator
   choice. Requiring users to add `observe` as a third token to get execution is friction without
   benefit.

The organizing principle underlying all three tokens is:

> Each validation expression must be necessary based on the strictest feasible gap observed one
> layer closer to the originating expression of intent.

This implies a conditional ladder: escalate only as far as needed to close the observable gap, but
express the chosen layer at maximum strength.

## Design

### Revised `ground` definition

`ground` absorbs the logic of `enforce` and `observe` under a single token:

1. **Declare I**: treat the stated goals, correctness criteria, or explicit constraints as fixed and
   authoritative.
2. **Construct V**: build a falsifiable validation artifact expressing conditions under which I is
   satisfied. V must use the strongest mechanism *necessary* to close the observable gap between I
   and O — not the strongest available in the abstract, but the strongest the current gap demands.
   Strength ordering (strongest to weakest): executable code written to files > formal notation
   encoding constraints > structured criteria with concrete checkable values > prose descriptions.
   Using a weaker mechanism when the gap requires a stronger one violates this constraint. Using a
   stronger mechanism when a weaker one closes the gap is over-specification and should be avoided.
3. **Run V if executable**: if V can be executed in the current medium, the response must run it
   and present the observed evidence before producing O. If V is not executable, constructing and
   presenting V before O is sufficient.
4. **Produce O**: output O must satisfy V. Present the complete V artifact, then the exact phrase
   `Validation artifact V complete` on its own line, then O. Any O appearing before this checkpoint
   violates the constraint.

Iteration is permitted: V₁ → O₁, then V₂ → O₂, each cycle moving one layer closer to I.

### Retire `observe`

`observe`'s behaviour is fully captured by the "run V if executable" sub-step in the revised
`ground`. The independent use of `observe` (prefer running over assuming, outside a ground context)
was a weaker pressure that is better handled by the general instruction to prefer empirical evidence
— it does not require a dedicated token.

### Retire `enforce`

`enforce`'s strength ordering is absorbed into `ground`'s V construction rule, with the important
correction that it now uses minimize-necessary semantics rather than maximize-available semantics.
The checkpoint phrase `Validation mechanism:` is retired; the mechanism is implicit in V's form.

## Decision

- Update `ground` in `AXIS_TOKEN_METADATA` and `AXIS_KEY_TO_VALUE` in `axisConfig.py` to
  incorporate the conditional execution sub-step and the minimal-sufficiency V construction rule.
- Remove `observe` from all axis config dicts (`AXIS_KEY_TO_VALUE`, `AXIS_KEY_TO_LABEL`,
  `AXIS_KEY_TO_KANJI`, `AXIS_KEY_TO_ROUTING_CONCEPT`, `AXIS_KEY_TO_CATEGORY`,
  `AXIS_TOKEN_METADATA`).
- Remove `enforce` from all axis config dicts.
- Update `help_llm.go` to remove hardcoded references to `observe` and `enforce`; update any
  heuristics that reference the three-token pipeline.
- Run `make axis-regenerate-apply` and `go test ./internal/barcli/ -run TestLLMHelp` to validate.

## Consequences

- `ground` becomes a self-contained verification token covering intent declaration, validation
  construction, conditional execution, and output derivation.
- Two method slots are freed when the full verification pipeline is needed, allowing one or two
  additional method tokens in a `bar build` invocation.
- The minimal-sufficiency correction to `enforce` semantics eliminates a subtle design error:
  users were previously encouraged to over-specify validation mechanisms.
- The organizing principle — "strictest feasible gap, one layer closer to intent" — is now
  embedded in a single token rather than split across three.
- Existing prompts that used `ground enforce observe` together will produce equivalent behaviour
  from `ground` alone; prompts that used `observe` or `enforce` independently will need review.
