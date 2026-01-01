# 053 – Retire the “purpose” axis label; make “intent” the single Why axis

## Status
Accepted

## Context
- Persona/Intent stance is currently split between two labels for the same Why axis: `intent` presets in UX copy and `purpose` tokens/keys in the grammar and SSOT (`PERSONA_KEY_TO_VALUE["purpose"]`, the axis catalog entry, and the runtime Talon list historically surfaced as `modelPurpose`).
- Persona/Intent metadata is now exposed via `get_persona_intent_orchestrator()` (backed by `lib.personaConfig`), so renaming the SSOT requires updating the façade rather than touching surfaces directly.
- ADR 015/040/042/051 already frame this axis as **intent (Why)**, while purpose remains as a historical name kept for compatibility.
- Maintaining both names forces duplicate docs (persona/intent vs purpose), duplicate status/reset commands, and validation/prompt code paths that normalize between the two even though the token sets are 1–1.
- Users and contributors have to remember whether a given surface says “intent” or “purpose,” adding churn without semantic benefit.

## Decision
- Make **`intent` the single canonical name** for the Why axis (What we are trying to accomplish).
- **Retire `purpose` entirely** across SSOT, grammar, docs, UX strings, suggest meta-prompt/handling, and status/reset commands; do not keep aliases.
- Keep the current token set and presets exactly as-is (Why semantics remain unchanged); this ADR only collapses naming and surface-level duplication.

## Rationale
- Eliminates duplicated labels and reduces contributor/user confusion about whether “purpose” is distinct from “intent.”
- Aligns grammar, SSOT, presets, and help surfaces with ADR 042’s “persona + intent” framing, avoiding split-brain terminology.
- Simplifies validation and hydration (single axis name), reducing guardrail surface area and future rename churn.

## Migration Plan
1) **SSOT/catalog rename (risky first):** Rename `purpose` keys/structures in `lib/personaConfig.py` and `axis_catalog` to `intent` (axis table, defaults, presets) while preserving token values; remove purpose aliasing/shims, and refresh `get_persona_intent_orchestrator()` so downstream consumers pick up the new naming.
2) **Grammar/runtime list rename:** Rename the runtime Talon list (per ADR 052’s catalog-driven population) from `modelPurpose` to `modelIntent` and update captures/contexts to reference `intent`; if the optional list generator/export exists, ensure it emits `modelIntent` naming. Remove purpose captures/contexts instead of aliasing.
3) **Suggest pipeline:** Update suggest meta-prompt, parsing, and stance validation to accept only `intent` naming; adjust tests to reject any `purpose` strings.
4) **Commands/UX surfaces:** Update voice commands, status/reset flows, help hub, pattern/suggestions GUIs, and quick-help copy to “intent” only; remove the separate purpose section. `model write …` sets voice/audience/tone; intent is set via `intent <token>` or presets.
5) **Validation/guardrails:** Refresh axis/suggestion/help tests for intent-only naming and run `python3 -m pytest` (plus guardrail targets if configured).

## Execution checklist (repo touchpoints)
- SSOT/catalog: `lib/personaConfig.py`, `lib/axis_catalog.py` intent axis tables/defaults/presets; remove purpose symbols entirely and ensure `get_persona_intent_orchestrator()` reflects the updated naming.
- Grammar/runtime lists: Talon list wiring for the intent axis (runtime-populated list name swap to `modelIntent`); remove any purpose captures/contexts.
- Suggest pipeline: meta-prompt strings and stance parsing/validation in `GPT/gpt.py` (or adjacent parser/validator modules) to accept only intent naming.
- Commands/UX: voice commands/status/reset flows and help surfaces (help hub, pattern/suggestions GUI, quick help) to render and speak “intent” only.
- Tests/guardrails: update axis/help/suggestion guardrail tests and run `python3 -m pytest` (plus guardrail targets if configured) to enforce intent-only naming.

## Definition of done (checks)
- `python3 -m pytest`
- `make guardrails` (or `make axis-guardrails`/`axis-guardrails-ci` if `guardrails` is unavailable)
- Manual: intent status/reset voice commands and suggestion GUI show “intent” only (no “purpose”) and accept intent tokens without purpose tokens.
- Manual: `model write …` sets voice/audience/tone and does not demand an intent token.

## Verification
- 2026-01-09: `python3 -m pytest` (pass).

## Consequences
- Clearer mental model: one Why axis called intent; no more intent/purpose split across commands and docs.
- Small migration churn (renames in grammar, SSOT, docs, and tests); no backward-compatibility layer to maintain.
- Users must say `intent <token>` (or presets) to set Why; `model write …` covers voice/audience/tone without requiring an intent token.

## Open tasks
- (done) SSOT/catalog rename landed with tests updated.
- (done) Grammar/runtime list rename and capture removal completed.
- (done) Suggest meta-prompt/stance validation migrated to intent-only.
- (done) Commands/UX copy and status/reset flows updated to intent-only.
- (done) Guardrail/tests refreshed (including suggest/help/axis) and `python3 -m pytest` green.
- (done) Add preset surfacing for all intent tokens (intent presets reflect the intent list; quick help shows all intent tokens, not just preset keys).
- (done) Rename legacy purpose/intent tokens to single-word keys for speaking surfaces; reuse existing intent preset names where available and choose new, easy-to-say single words for any added intents.

## Risks and mitigations
- Missed purpose references in help/GUI copy: run guardrail/help tests and manual spot-checks; search for “purpose” strings in UI resources.
- Suggest pipeline still emitting/validating purpose: update meta-prompt and stance validator; add a regression test that rejects purpose tokens.
- Talon list/grammar rename drift: ensure runtime list name (`modelIntent`) matches captures and catalog; run `make guardrails` and targeted Talon grammar validation if available.
- User confusion during cutover: surface intent-only wording in quick help/status; remove purpose sections entirely to avoid mixed signals.
