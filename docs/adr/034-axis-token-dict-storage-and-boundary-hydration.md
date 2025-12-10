# 034 – Axis Token Dict Storage and Boundary Hydration

- Status: Accepted  
- Date: 2025-12-09  
- Context: ADR 030 moved us toward token-only state with hydration at a single boundary, but the current shape still serialises axes as ad-hoc strings (`"plan xp"`), and overrides can arrive hydrated. We want a stricter, testable contract: store axes as token lists (per axis) in state/history, and hydrate only when emitting system-facing text.  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 018 – Axis Modifier Decomposition into Pure Elements  
  - 026 – Axis Multiplicity for Scope/Method/Style  
  - 030 – Axis Token Storage and Hydration Boundary  
  - 032 – Completeness/Method/Scope/Style Meta-Spec  

---

## Decision

- **Authoritative storage = tokens only, per-axis lists.**  
  `GPTState` (and history/log entries) keep axes as a dict of axis → list[str] tokens (for example, `{scope: ["narrow"], method: ["rigor", "xp"], style: []}`). `last_recipe` and recap strings are derived views, not the source of truth.

- **Hydration only at the model boundary.**  
  When building the system prompt / constraints, map tokens → hydrated descriptions via in-memory dicts. Never persist hydrated strings in state/history.

- **All ingress mapped to tokens.**  
  Spoken/profile/default/override values are immediately run through the value→key maps (`_map_axis_tokens`) into token lists before touching state. “Again”/history replays operate on token lists only.

- **History/log persistence is token-based.**  
  Append history with token dicts plus a compact token-string view for display; on read, restore the token dict into `GPTState` and re-derive recap strings.

- **Surface contract:**  
  - State/history: token lists per axis.  
  - Recap/grammar strings: token-joined views derived from lists.  
  - Hydrated descriptions: only in system prompt / constraint text / UX that is explicitly for humans.

## Consequences

Positive:
- Eliminates hydrated leakage into state/recap; replays and “again” stay deterministic and token-only.
- Clear contract for readers/writers; easier to test and refactor.
- Simpler merging/replacement semantics on token lists (no string splitting).

Negative / mitigations:
- Requires refactors to introduce axis-token dicts and migrate writers/readers.  
- History format change needs a migration shim; mitigate by dual-writing old `recipe` string + new token dict and preferring the dict on read until the old field can be dropped.

## Implementation Notes / Steps

1) **State shape:** add `GPTState.last_axes = {"completeness": [token], "scope": [...], "method": [...], "style": [...]}` (directional stays scalar token). Keep `last_recipe` as derived for UI/grammar.
2) **Writers/surfaces to update:**  
   - `modelPrompt` (main entry), `modelPatternGUI`, `modelPromptPatternGUI`, `modelSuggestionGUI` → write `last_axes` tokens, derive `last_recipe` for recap/grammar.  
   - “again” (`gpt_rerun_last_recipe` + with-source variant) → operate on token lists; overrides replace per-axis lists; re-derive `last_recipe`.  
   - History append/replay, request log → persist token dict + legacy string; replay restores `last_axes`.  
   - Settings/defaults (system prompt persona/axes) → write tokens into `last_axes` defaults.  
   - Recap/destination surfaces (response canvas, confirmation GUI, help/pattern/suggestion canvases) → read token lists; display joins; never store hydrated text.  
   - System prompt/constraints → only place that hydrates tokens → descriptions.
3) **Hydration boundary:** system prompt / constraint builders take `last_axes` (or current request axes) and hydrate via maps; no other hydrators remain.
4) **History/logs:** append token dicts; when reading history, restore `last_axes` and re-derive `last_recipe`. Keep writing the legacy `recipe` string during transition.
5) **Tests:** add coverage that state/history stay token-only, replays don’t re-hydrate, and hydrations only happen in system prompt construction.

---

## Current Status (2025-12-10)

- Token-only storage is implemented end-to-end: `GPTState.last_axes` is the SSOT, history/log dual-write token dicts, and recaps/again/history use token dicts (legacy strings only for display fallback).
- Hydration boundary enforced: system prompt/constraints hydrate via `axisConfig` (token→description); ingress filters hydrated/unknown tokens, and Talon lists are token:token with `axisConfig` as SSOT.
- Guardrails/tests: history ingest and rerun filter hydrated/unknown tokens; recaps prefer tokens; token-vs-list parity test ensures Talon lists match `axisConfig`.
- All ADR tasks for this repo are complete and test-backed; any further status changes would be maintenance only.
