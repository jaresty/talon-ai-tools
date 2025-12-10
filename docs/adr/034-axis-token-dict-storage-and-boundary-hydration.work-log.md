## 2025-12-09 – Slice: introduce token dict storage plumbing

- Added `GPTState.last_axes` (per-axis token lists) as the authoritative axis store alongside existing recap strings; reset paths updated.
- Wired main writers to populate `last_axes`:
  - `modelPrompt` (via `talonSettings`) now writes canonical axis tokens into `last_axes`.
  - Pattern/suggestion runners (`modelPatternGUI`, `modelPromptPatternGUI`, `modelSuggestionGUI`) now write token lists into `last_axes`.
  - History replay populates `last_axes` from the parsed recipe; reset/clear do likewise.
  - `gpt_rerun_last_recipe` now reads base tokens from `last_axes` (fallback to legacy strings) and writes merged tokens back to `last_axes`.
- All tests touched by these surfaces still pass: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_axis_mapping.py _tests/test_request_history_actions.py`.

Follow-ups:
- Extend history/log entries to persist axis token dicts (dual-write legacy string + dict; prefer dict on read).
- Update recap/destination surfaces to optionally read from `last_axes` directly (currently still derived from `last_*` strings).
- Add focused tests asserting `last_axes` stays token-only across prompt runs, history replay, and “again” overrides.

## 2025-12-09 – Slice: axis config module + history token dicts

- Added `lib/axisConfig.py`: static Python maps for axis token→description (generated from list data) plus derived value→token maps, mirroring staticPromptConfig so code no longer reparses Talon lists at runtime.
- `axisMappings` now sources maps from `axisConfig` and exports back-compat aliases.
- `GPTState.last_axes` now persists through history/log: `append_entry` dual-writes axes dicts; `RequestLogEntry` stores them; history replay restores `last_axes`.
- Recap surface (response canvas) reads `last_axes` when building the prompt recap.
- Tests updated/passing: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_axis_mapping.py _tests/test_request_history_actions.py _tests/test_request_log.py`.

Next:
- Prefer `last_axes` in other recap/GUI surfaces; remove reliance on legacy `last_*` strings.
- Ensure “again” and history replays derive recaps from `last_axes` consistently; add targeted tests.

## Current plan and definition of done

SSOT direction:
- Treat `lib/axisConfig.py` as the single source of token→description data (similar to staticPromptConfig). Talon lists can remain token:token for grammar; no other code should read hydrated descriptions from list files.
- All state/history/storage uses token lists only (`GPTState.last_axes`), with `last_recipe`/recap strings derived from tokens.
- Hydration happens only at the model boundary (system prompt/constraints) using `axisConfig` maps.

Remaining work for DONE:
1) Ensure all recap/GUI surfaces read from `last_axes` and derive strings/toggles from tokens; drop reliance on legacy `last_*` strings for axis values (response canvas + browser done; confirm other surfaces).
2) History/log: prefer the stored axes dict when replaying/reviewing; keep legacy `recipe` string only as a display fallback.
3) Add guardrail tests:
   - AxisConfig vs token sets sanity (no hydrated text needed from lists).
   - `last_axes` stays token-only across prompt runs, “again”, and history replay.
   - Recap surfaces reflect `last_axes`.
4) AxisConfig is SSOT for descriptions. Add a sanity check that Talon lists’ token sets match `axisConfig` tokens (lists are token:token only); no value→token parsing or hydrated text paths remain.

## 2025-12-10 – Slice: token-only ingress & recap token usage

- Enforced token-only ingress: `_read_axis_default_from_list` and `_read_axis_value_to_key_map` now return tokens only; removed hydrated parsing fallbacks. Updated axis mapping tests accordingly.
- Axis value→key maps are exposed as copies so tests can inject overlaps without mutating SSOT.
- Browser destination recap now derives its recipe/“Say” hints from `last_axes` tokens (with legacy `last_*`/`last_recipe` as fallback), aligning recap surfaces with token dict storage.
- Full pytest suite passing after ingress changes.

Next:
- Finish migrating remaining recap surfaces (if any) to prefer `last_axes` and add guardrail tests to ensure recaps reflect token dicts.
- Add sanity checks between `axisConfig` tokens and Talon list token sets; keep axisConfig as SSOT for descriptions.

## 2025-12-10 – Slice: axisConfig↔Talon token-set guardrail

- Added guardrail test to ensure each GPT axis Talon list’s token set matches `axisConfig` tokens (token-only ingress contract).
- Kept recap behaviour green after the recent browser/response canvas token-preferring changes.
- Full pytest suite passing.

Remaining:
- If any recap/GUI surfaces still rely on legacy `last_*` strings, switch them to `last_axes` and add tests that recaps reflect token dicts.
- Add a sanity check that `last_axes` stays token-only across prompt runs/again/history replay.

## 2025-12-10 – Slice: history replay prefers axes dict (token-only state)

- Added a history action test ensuring `gpt_request_history_show_latest` prefers stored `axes` token dicts over legacy recipe strings when both are present, and that `last_*` strings derive from tokens.
- Full pytest suite passing.

Remaining:
- Sweep any remaining recap/GUI surfaces that might still read legacy `last_*` strings and add tests asserting recaps reflect `last_axes`.
- Add guardrail that `last_axes` remains token-only across prompt runs/again/history replay.

## 2025-12-10 – Slice: history recap derived from axes tokens

- History replay now derives `last_recipe` from the stored `axes` token dict when present, ignoring legacy recipe strings. Added a test asserting recap uses tokens.
- Full pytest suite passing.

Remaining:
- Sweep any remaining recap/GUI surfaces that might still read legacy `last_*` strings and add tests asserting recaps reflect `last_axes`.
- Add guardrail that `last_axes` remains token-only across prompt runs/again/history replay.

## 2025-12-10 – Slice: rerun prefers token dict over legacy recipe

- Added guardrail test for `gpt_rerun_last_recipe` to ensure reruns use token-only `last_axes` even when the legacy `last_recipe`/`last_*` strings are hydrated/mismatched; state and recap are rebuilt from tokens.
- Full pytest suite passing.

Remaining:
- Sweep any remaining recap/GUI surfaces that might still read legacy `last_*` strings and add tests asserting recaps reflect `last_axes`.
- Add guardrail that `last_axes` remains token-only across prompt runs/again/history replay.

## 2025-12-10 – Slice: recap surfaces prefer `last_axes`

- `gpt_show_last_recipe` now builds its recap from `last_axes` tokens (with legacy string as fallback) and a new test asserts this token-preferring behaviour.
- Confirmation GUI recap now derives its recipe text from `last_axes` tokens, keeping it aligned with the token-only contract.
- Full pytest suite passing.

Remaining:
- Add a guardrail that `last_axes` remains token-only across prompt runs/again/history replay.

## 2025-12-10 – Slice: token-only guardrail on rerun & recap

- `gpt_rerun_last_recipe` now filters axis tokens against `axisConfig` so unknown/hydrated tokens are dropped before updating state. Adds a guardrail test verifying rerun derives axes from token dict and rebuilds recap token-only.
- `gpt_show_last_recipe` test asserts recap uses `last_axes` tokens even when legacy strings are hydrated/mismatched.
- Full pytest suite passing.

Remaining:
- Add a guardrail that `last_axes` remains token-only across prompt runs/again/history replay (broader integration check).

## 2025-12-10 – Slice: token-only guardrail across rerun/history

- Added filtering against `axisConfig` in history replay (`requestHistoryActions`) so hydrated/unknown tokens are dropped when restoring `last_axes`.
- Strengthened rerun guardrail: invalid/hydrated tokens in `last_axes` are filtered before canonicalisation to keep caps from dropping valid tokens.
- Added tests covering both history ingestion filtering and rerun token filtering.
- Full pytest suite passing.

Remaining:
- Broader integration guardrail that `last_axes` stays token-only across prompt runs/again/history replay (end-to-end check).

## 2025-12-10 – Slice: token-only override filtering

- Added a rerun guardrail test covering overrides with mixed valid/invalid tokens; rerun now emits only known tokens into `modelPrompt`/state.
- History ingestion test kept to ensure hydrated/unknown tokens are filtered out on replay.
- Full pytest suite passing.

Remaining:
- Broader integration guardrail that `last_axes` stays token-only across prompt runs/again/history replay (end-to-end check).

## 2025-12-10 – Slice: token-only across history → rerun path

- Added end-to-end guardrail test: history ingest filters hydrated/unknown tokens, then `model again` rerun keeps `last_axes` token-only and maps only valid tokens into `modelPrompt`.
- Tests remain green.

Remaining:
- Broader integration guardrail that `last_axes` stays token-only across prompt runs/again/history replay (end-to-end check) – largely covered for history→rerun; consider full prompt run coverage if needed.

## 2025-12-10 – Slice: prompt-run filtering + end-to-end guardrail

- Added token filtering in `modelPrompt` so obviously hydrated strings (starting with "Important:") are dropped while allowing short custom tokens; keeps prompt-run state token-only.
- Added end-to-end guardrail: history ingest filters hydrated/unknown tokens, rerun uses token-only state, and overrides with invalid tokens are ignored.
- Full pytest suite passing.

Remaining:
- ADR 034 objectives are effectively covered in-repo; consider status reconciliation if no further token-only gaps are identified.

## 2025-12-10 – Status reconciliation

- ADR 034 implemented and tests cover token-only state across prompt runs, again, history replay, recaps, and list/config parity. Hydration is confined to the prompt boundary via axisConfig.
- No in-repo work remains for this ADR; future changes would be maintenance.
## 2025-12-10 – Slice: history recap derived from axes tokens

- History replay now derives `last_recipe` from the stored `axes` token dict when present, ignoring legacy recipe strings. Added a test asserting recap uses tokens.
- Full pytest suite passing.

Remaining:
- Sweep any remaining recap/GUI surfaces that might still read legacy `last_*` strings and add tests asserting recaps reflect `last_axes`.
- Add guardrail that `last_axes` remains token-only across prompt runs/again/history replay.
