# ADR-0161: Compare Mode and Algebraic Prompt Composition

## Status
Accepted — Stage 1 implemented

## Context

The backlog carries a "token variation comparison" feature: given a base command and a set of token
variants on one axis, generate a prompt that shows how the response changes across variants. This
surfaces what a token actually *does* rather than relying on its description alone.

Two initial approaches were noted:
- **Approach A** — single prompt asking the LLM to respond N times, once per variant, labeled
- **Approach B** — N independent `bar build` prompts run in parallel, outputs side by side

During design exploration, the scope expanded: the useful comparison unit is not always a single
axis value but a *complete configuration* — a full set of tokens across multiple axes. For example:

- "diagnostic lens" = `diagnose fail` vs "structural lens" = `mapping cross`
- `gist bullets` vs `full walkthrough`
- Two personas against the same subject

Once the comparison unit is a full configuration, comma-separated single-axis syntax (`method=a,b,c`)
is insufficient. A compositional grammar is needed.

## Problem Statement

1. There is no way to express "compare these two token configurations against this subject" in a
   single `bar build` invocation.
2. Adding a `bar compare` subcommand handles single-axis variation but doesn't generalise to
   multi-axis configuration comparison.
3. The bar grammar is currently a flat ordered token list with no grouping or operator semantics.
   Extending it to support comparison requires defining what "group" and "compare" mean in the
   grammar.
4. The ADR-0113 eval loop currently constructs comparison prompts manually. A structured compare
   mode would automate this and make token iteration faster.

## Design

### Stage 1 — Single-axis compare via comma syntax (MVP)

Extend `bar build` to accept comma-separated values on exactly one axis:

```
bar build make method=diagnose,mapping "subject"
```

Semantics: generate an Approach A prompt with N labeled sections, one per variant. The prompt
instructs the LLM to respond to the subject N times, each time applying the named token.

Each section includes the token's `definition` and key `heuristics[]` from the grammar as context,
so the LLM has the token's actual meaning — not just its name.

**Constraints:**
- Exactly one axis may carry multiple comma-separated values
- All other axes must be single-valued (normal `bar build` behaviour)
- `--parallel` flag (deferred to Stage 2) would switch to Approach B

**Prompt template structure (Approach A):**

```
You will respond to the subject below multiple times, once per token variant listed.
For each variant, apply only that token's framing and label your response clearly.

## Variant: method=diagnose
Definition: [from grammar]
Heuristics: [from grammar]
---
[Your response here]

## Variant: method=mapping
Definition: [from grammar]
Heuristics: [from grammar]
---
[Your response here]

## Subject
[subject text]
```

### Stage 2 — Multi-configuration compare via grouping syntax

Allow comparison of complete configurations using bracket grouping:

```
bar build make [diagnose fail] | [mapping cross] "subject"
```

Or equivalently in a more explicit form:

```
bar build make {diagnose fail} or {mapping cross} "subject"
```

Semantics: each `[...]` or `{...}` group defines a complete token configuration. The `|` / `or`
operator means "compare these configurations". The base tokens outside any group apply to all
configurations (here, `make` applies to both).

**Open questions for Stage 2:**
- Syntax: brackets `[...]`, braces `{...}`, or an explicit `--group` flag?
- Operator: `|` (terse, shell-conflicting), `or` (readable), `--compare` flag?
- How many configurations can be compared? (2 is the clear case; N adds output length fast)
- Should intra-group tokens follow the same ordering rules as `bar build`?
- What does `and` mean? Currently multiple method tokens are already implicitly ANDed.
  An explicit `and` operator may be redundant or could mean "run sequentially" (pipeline).

### Stage 3 — Pipeline / sequential composition (deferred, speculative)

```
bar build probe diagnose "subject" | bar build fix "output of step 1"
```

Sequential composition where the output of one bar prompt is the subject of the next.
This is architecturally different (requires a runner) and is out of scope for Stage 1–2.

## Decision

- **Stage 1 is accepted**: implement comma-separated single-axis compare in `bar build`.
  New flag `--compare` or auto-detected from comma syntax; Approach A prompt template;
  definitions + heuristics embedded per variant.
- **Stage 2 is deferred**: the grouping syntax needs more design before implementation.
  The open questions above must be resolved in a follow-up ADR or addendum.
- **`bar compare` subcommand is rejected**: keeping compare inside `bar build` is cleaner
  and positions the feature as a grammar extension rather than a separate tool.
- **Approach B (parallel prompts) is deferred**: requires a prompt runner that doesn't exist.

## Stage Feasibility Notes

**Stage 1 → Stage 2**: The prompt generation code (labeled sections, definition/heuristics
embedding) reuses directly. However, the parsing models are different: Stage 1 stays within
the existing flat token list (detect comma, split one axis). Stage 2 requires genuine
group/expression parsing (bracket delimiters, operator tokens, multiple sub-configurations).
Stage 1 does not pave the way for Stage 2 at the parser level. Stage 2 should be validated
against real usage of Stage 1 before building — if single-axis compare proves sufficient in
practice, Stage 2 may never be needed.

**Stage 2 → Stage 3**: Architecturally unrelated. Stage 2 is still prompt generation (one
output string). Stage 3 requires an LLM runner to receive and pipe responses.

**Stage 3 may already be solved**: Shell piping handles this today if the user has an LLM
runner: `bar build probe diagnose "subject" | llm | bar build fix --input -`. Bar already
reads from stdin via `--input -`. Stage 3 may require zero bar changes.

## Consequences

- `bar build` gains a new parsing branch: `DetectCompare` pre-scans tokens for comma-separated
  axis values before the normal `Build` call.
- Grammar accessors `AxisDescription` and `AxisTokenHeuristics` (already exist) are used
  directly in the compare prompt template — no grammar changes needed.
- Stage 2 grouping syntax is a meaningful parser change; deferring it avoids premature
  commitment to a syntax that may not be ergonomic.
- The ADR-0113 eval loop can use Stage 1 immediately: `bar build probe method=a,b,c "task"`
  generates a structured comparison prompt for any token set.
- Stage 1 implemented in `internal/barcli/compare.go`; 11 tests in `compare_test.go`.
