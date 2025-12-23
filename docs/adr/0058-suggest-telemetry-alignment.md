# 0058 – Align suggest telemetry with axis-first stance guardrails

## Status
Accepted

## Context
- `model run suggest` runs use the standard request logging pipeline (`lib/modelHelpers.py:1725` → `lib/streamingCoordinator.py:430` → `lib/requestLog.py:454`), so the Silent destination still attempts to append a history entry. Because the suggest payload lacks a directional axis, the log helper emits a `missing_directional` drop, which is surfaced in the latest telemetry snapshot (`artifacts/telemetry/history-validation-summary.telemetry.json`).
- Manual telemetry exports invoked via `lib/telemetryExportCommand.py:37` default to `reset_gating=False`, so the snapshot preserves legacy gating counters (for example, 18 prior `in_flight` drops) even when the streaming summary reports only current-session drops. This mismatch complicates guardrail triage.
- Suggestion skip reporting in `lib/suggestionCoordinator.py:98` requires persona hints to resolve to a known preset. The current suggest result parser (`GPT/gpt.py:3328`) already normalises axis tokens, but when the model emits a stance without a preset alias we count it as `unknown_persona`, leading to noisy telemetry (4 skips in the latest snapshot).
- The suggest meta-prompt (`GPT/gpt.py:408` onwards) still foregrounds preset tables and mixes preset and axis instructions, encouraging the model to emit preset names that our axis-first workflow no longer prefers (ADR 041). The parser then has to down-convert those presets, increasing failure modes.

## Decision
- Treat suggest runs as **non-history requests**: short-circuit the history append path when `current_destination_kind == "suggest"` so Silent runs do not emit fake history entries or `missing_directional` drops.
- **Reset gating counters by default** for manual telemetry exports (set `reset_gating=True` in `model_export_telemetry` calls and update the command default) so snapshot data reflects only post-export activity unless callers explicitly opt out.
- **Accept axis-aligned persona hints** without requiring preset resolution: adjust `record_suggestions` to treat stance voice/audience/tone tokens as sufficient and only log `unknown_persona` when the tokens fall outside the known axis catalog.
- **Rephrase the suggest meta-prompt** to emphasise raw axis tokens, demote preset tables to optional reference material, and clarify that persona/intent preset fields are optional—aligning model output with the relaxed parser and ADR 041’s stance guidance.

## Rationale
- Suppressing history writes for suggest eliminates false-positive telemetry (`missing_directional`) while keeping real history guardrails intact for other destinations.
- Resetting counters makes manual exports comparable to CI snapshots and prevents stale data from obscuring current issues.
- Allowing axis tokens without preset lookups rewards the desired stance format (raw voice/audience/tone) and reduces spurious skip totals that distract from genuine persona catalog drift.
- Updating the meta-prompt closes the loop: the model is guided toward axis tokens, the parser accepts them, and telemetry reflects meaningful skips or errors.

## Implementation Plan
1. **History bypass:** in `lib/modelHelpers.py` (and any fallback path), detect `suggest` destination runs and skip `append_entry_from_request`; add characterization coverage in `_tests/test_gpt_actions.py` or similar to assert no history append occurs.
2. **Telemetry defaults:** set the default `reset_gating` to `True` in `lib/telemetryExportCommand.py` and ensure callers/tests expecting legacy behaviour pass `reset_gating=False`; refresh `_tests/test_telemetry_export.py` expectations if needed.
3. **Persona skip logic:** update `lib/suggestionCoordinator.py` to validate voice/audience/tone against `axis_registry_tokens("persona")` (or related helpers) and only log `unknown_persona` when the values do not align; expand `_tests/test_suggestion_coordinator.py` to cover axis-only stances.
4. **Meta-prompt refresh:** rewrite the persona/intent sections in `_suggest_prompt_text` (`GPT/gpt.py`) to (a) present axis token lists first, (b) mark preset fields as optional examples, and (c) clarify stance expectations; adjust suggest parser tests (`_tests/test_gpt_actions.py`) for new phrasing if assertions depend on the prompt text.

## Execution Checklist
- `lib/modelHelpers.py`
- `lib/telemetryExportCommand.py`
- `lib/suggestionCoordinator.py`
- `GPT/gpt.py`
- `_tests/test_gpt_actions.py`
- `_tests/test_suggestion_coordinator.py`
- `_tests/test_telemetry_export.py`

## Definition of Done
- `python3 -m pytest`
- Telemetry export invoked without arguments resets gating counters (verified via `artifacts/telemetry/talon-export-marker.json`).
- `model run suggest` followed by history export produces no `missing_directional` drops and zero `unknown_persona` skips when the model emits valid axis tokens.

## Verification
- Pending: execute `python3 -m pytest` after implementing the changes above.

## Consequences
- Manual telemetry exports reflect only recent gating events, making regressions easier to spot.
- Suggest skip telemetry aligns with axis-first stances, reducing noisy alerts while still catching genuinely unknown personas.
- Suggest guardrails stay focused on contract completeness (directional lenses) instead of logging artefacts from Silent destinations.

## Risks and Mitigations
- **Silent history bypass hides real issues:** add targeted tests ensuring non-suggest destinations still log history entries; log a debug message when bypassing for traceability.
- **Reset default surprises automation:** document the new behaviour in guardrail tooling and allow `reset_gating=False` overrides; update scripts under `scripts/tools/` if they relied on cumulative counters.
- **Meta-prompt edits drift from ADR 041:** review the rewritten prompt with ADR 041 authors and rerun suggest acceptance tests to confirm stance/Why lines remain clear.
- **Relaxed persona validation misses catalog drift:** retain optional debug logging when axis tokens fail to canonicalise so telemetry can still highlight invalid tokens.
