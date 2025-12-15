# 053 – Retire the “purpose” axis label; make “intent” the single Why axis

## Status
Proposed

## Context
- Persona/Intent stance is currently split between two labels for the same Why axis: `intent` presets in UX copy and `purpose` tokens/keys in the grammar and SSOT (`PERSONA_KEY_TO_VALUE["purpose"]`, `modelPurpose.talon-list`).
- ADR 015/040/042/051 already frame this axis as **intent (Why)**, while purpose remains as a historical name kept for compatibility and legacy speech captures.
- Maintaining both names forces duplicate docs (persona/intent vs purpose), duplicate status/reset commands, and validation/prompt code paths that normalize between the two even though the token sets are 1–1.
- Users and contributors have to remember whether a given surface says “intent” or “purpose,” and validators must treat them as aliases to avoid regressions, adding churn without semantic benefit.

## Decision
- Make **`intent` the single canonical name** for the Why axis (What we are trying to accomplish).
- **Retire `purpose` as a first-class axis label** across SSOT, docs, UX strings, and status/reset commands; keep a **strict alias** only at the speech/parse boundary for backward compatibility during a deprecation window.
- Keep the current token set and presets exactly as-is (Why semantics remain unchanged); this ADR only collapses naming and surface-level duplication.

## Rationale
- Eliminates duplicated labels and reduces contributor/user confusion about whether “purpose” is distinct from “intent.”
- Aligns grammar, SSOT, presets, and help surfaces with ADR 042’s “persona + intent” framing, avoiding split-brain terminology.
- Simplifies validation and hydration (single axis name), reducing guardrail surface area and future rename churn.

## Migration Plan
1) **SSOT rename:** Rename `purpose` keys/structures in `lib/personaConfig.py` to `intent` (axis table, defaults, presets) while preserving token values; add a temporary alias map so old imports/tests do not break immediately.
2) **List/grammar rename:** Move `GPT/lists/modelPurpose.talon-list` to `modelIntent.talon-list` and update captures/contexts to reference `intent`; add a thin alias capture that maps `purpose` tokens to the intent axis for the deprecation window.
3) **Commands and UX:** Update voice commands, help hub, pattern/suggestions GUIs, and quick-help text to speak “intent” only (status/reset/apply); mark any “purpose” mentions as deprecated copy or remove them.
4) **Validation/tests:** Update validators to expect `intent` as the sole axis name, with explicit tests that reject new “purpose” surface strings while still accepting the alias at the speech boundary until removal. Run `python3 -m pytest`.
5) **Deprecation/remove:** Log/telemetry (if available) any `purpose` alias usage. After the deprecation window, delete the alias capture and any remaining `purpose` strings.

## Consequences
- Clearer mental model: one Why axis called intent; no more intent/purpose split across commands and docs.
- Small migration churn (renames in grammar, SSOT, docs, and tests); mitigated by aliasing and telemetry during rollout.
- Legacy users saying `purpose` continue to work during the alias window; after removal they will need to say `intent <token>` or `model write … for <intent>`.
