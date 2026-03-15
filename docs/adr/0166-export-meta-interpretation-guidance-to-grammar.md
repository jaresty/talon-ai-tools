# ADR-0166: Export META_INTERPRETATION_GUIDANCE to Grammar JSON

**Status**: Proposed
**Date**: 2026-03-15

---

## Context

`lib/metaPromptConfig.py` defines three meta-instruction strings:

| Constant | Purpose | Already in grammar JSON? |
|---|---|---|
| `PROMPT_REFERENCE_KEY` | Structured token interpretation key | ✅ Yes (`reference_key`) |
| `EXECUTION_REMINDER` | Post-constraint execution directive | ✅ Yes (`execution_reminder`) |
| `META_INTERPRETATION_GUIDANCE` | Instructs the LLM to append a `## Model interpretation` meta section | ❌ No |

`META_INTERPRETATION_GUIDANCE` is injected into the system prompt by the Python-side Talon runner (`lib/talonSettings.py`, `lib/modelTypes.py`), but it is **not** exported into `build/prompt-grammar.json`. As a result:

- The **SPA** (`web/src/lib/renderPrompt.ts`) cannot include it in the copied/rendered prompt.
- The **CLI** (`bar build`) cannot append it to the system prompt it produces.

This means prompts produced by the SPA and CLI are missing the meta-interpretation instruction that Python-side Talon prompts include, creating a cross-surface inconsistency.

## Decision

Export `META_INTERPRETATION_GUIDANCE` as a new top-level field `meta_interpretation_guidance` in `prompt-grammar.json`, parallel to `reference_key` and `execution_reminder`.

Wire it into:
1. **`lib/promptGrammar.py`** — add to the grammar payload (same pattern as `reference_key` / `execution_reminder`)
2. **`grammar.go`** — add `MetaInterpretationGuidance string` field to `PromptGrammar` struct and populate in `LoadGrammar`
3. **`web/src/lib/grammar.ts`** — add `meta_interpretation_guidance: string` to the `Grammar` type
4. **`web/src/lib/renderPrompt.ts`** — append it to the system prompt (after `execution_reminder`, as the final system section), matching the Python pattern in `modelTypes.py`
5. **CLI `bar build`** — emit it in the system prompt output (Go side, after execution_reminder)

## Consequences

- Prompts from all three surfaces (Talon/Python, SPA, CLI) will include consistent meta-interpretation guidance.
- The `META_INTERPRETATION_GUIDANCE` string remains SSOT in `lib/metaPromptConfig.py`; all surfaces read it from the grammar export.
- SPA and CLI test fixtures that construct `Grammar` objects need a `meta_interpretation_guidance: ''` field added (same pattern as the prior `reference_key` / `execution_reminder` additions).
