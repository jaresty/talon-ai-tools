# Experiment Log — GPT Suggestion Canonicalisation (EXP-2026-01-07-01)

## Known Facts (Updated)
- `record_suggestions` clears persona hints when axis tokens fail validation, which keeps “Bad persona” suggestions but degrades invalid fields—existing tests codify this behaviour.
- `normalize_intent_token` already maps “For-Deciding!” → “decide” in the base catalog; patched snapshots rely on refreshed orchestrator/persona maps to expose new display labels.
- The test harness must set `PYTEST_CURRENT_TEST="unittest"` so `_suggest_prompt_recipes_core_impl` takes the synchronous code path when the pipeline is mocked; without this flag the JSON payload never reaches the parser.
- Instrumenting the failing test shows `record_suggestions` receives a single canonical entry (`intent_purpose == "vision"`, `intent_preset_key == "vision"`); once the synchronous path is forced, the state records the suggestion correctly.
- Resetting persona caches (`persona_intent_maps_reset` + `reset_persona_intent_orchestrator_cache`) before the suggestion flow does not change the recorded suggestions, confirming that cached maps are not masking the patched snapshot.
- Directly invoking `record_suggestions` with a canonical entry outside the full pipeline can yield `unknown_intent` skips unless the surrounding orchestrator state is fully initialised, highlighting how tightly the canonicalisation depends on the test’s patched snapshot setup.
- `_process_suggest_result` is lexically nested inside `_suggest_prompt_recipes_core_impl` and cannot be patched directly from outside the function; measuring canonicalisation requires instrumentation at the call site.
- Notifications emitted during the display-intent test do not mutate the canonicalised suggestion list; state snapshots before and after notifications match exactly.
- Instrumented runs of display intent and persona-axis tests show `record_suggestions` storing entries exactly as supplied; alias-only canonicalisation occurs upstream where the test substitutes the recorder.

## Open Questions
- None.

## Loop History
### Loop 1 — 2026-01-07
- **Focus question**: Why does `_tests.test_gpt_suggest_validation.test_json_suggestions_accept_snapshot_display_intent` report zero suggestions while manual reproduction succeeds?
- **Hypothesis**: The mocked pipeline leaves `handle.result` as `None`, so `_finish_suggest` never forwards the parsed suggestions to `record_suggestions`.
- **Experiment**: Patch `record_suggestions` during the test run, capture the incoming suggestions, and compare the results before/after forcing synchronous execution.
- **Result**: The patched run showed `record_suggestions` receiving the canonical suggestion (length `1`); the test passed once `PYTEST_CURRENT_TEST` was set to `"unittest"`, disproving the hypothesis and confirming the root cause was the async path.
- **Evidence**: `PYTHONPATH=. python3 -m unittest _tests.test_gpt_suggest_validation.GPTSuggestValidationTests.test_json_suggestions_accept_snapshot_display_intent` (green after env flag); instrumentation captured the canonical entry passed to `record_suggestions`.

### Loop 2 — 2026-01-07
- **Focus question**: Are cached persona maps/orchestrator instances inside the suggestion flow bypassing patched snapshots during tests?
- **Hypothesis**: Resetting persona caches before running the test will not alter the resulting suggestions, proving that cached state is not causing the earlier discrepancy.
- **Experiment**: Wrap the test’s `setUp` to call `persona_intent_maps_reset()` and `reset_persona_intent_orchestrator_cache()`, run the test, and compare the captured suggestions with and without the resets.
- **Result**: Suggestions matched (one canonical entry) in both runs, confirming caches are not the culprit. Hypothesis upheld.
- **Evidence**:
  - With resets: helper script invoking the test produced the same canonical entry.
  - Without resets: control run showed the same canonical entry.

### Loop 3 — 2026-01-07 (Blocked)
- **Focus question**: Do the notification/skip-count paths in `record_suggestions` overwrite canonicalised intent values after they are set?
- **Hypothesis**: Notifications fire after canonical entries are stored and do not mutate the stored suggestions.
- **Experiment**: Attempted to seed `GPTState` with the canonical suggestion from the display-intent test, then re-ran `record_suggestions` with the canonical entry plus a notification-triggering entry, while patching `notify` to capture messages and recording final state.
- **Result**: Blocked. Direct calls to `record_suggestions` with the canonical entry resulted in `unknown_intent` skips because the test’s patched snapshot environment was not active, preventing a meaningful comparison. No evidence that notifications mutate stored suggestions was observed, but the hypothesis remains unverified.
- **Evidence**: Script output showed skip counts (`{'unknown_intent': 1, 'missing_directional': 1}`) and no canonical suggestions recorded.

### Loop 4 — 2026-01-07 (Blocked)
- **Focus question**: Are we still double-applying canonicalisation (helper + `record_suggestions`) in a way that could drop data in other scenarios?
- **Hypothesis**: Instrumenting `_process_suggest_result` to capture the suggestions passed to `record_suggestions` will match the stored state, proving only one canonicalisation step runs.
- **Experiment**: Attempted to monkey patch `_process_suggest_result`; discovered the function is nested inside `_suggest_prompt_recipes_core_impl` and cannot be patched externally.
- **Result**: Blocked. Need an alternative strategy (e.g., instrumentation via wrapper at the call site) for future loops.
- **Evidence**: `PYTHONPATH=. python3 - <<'PY' ...` attempted patch raised `AttributeError: module 'talon_user.GPT.gpt' has no attribute '_process_suggest_result'`.

### Loop 5 — 2026-01-07
- **Focus question**: Do the notification/skip-count paths in `record_suggestions` ever overwrite canonicalised intent values after they are set?
- **Hypothesis**: Notifications operate on the canonical suggestion list without mutating it; capturing state before and after notification calls will confirm this.
- **Experiment**: Patched `talon_user.GPT.gpt.record_suggestions` to wrap the original implementation while logging the input suggestions, stored state, and skip counts; patched both `talon_user.GPT.gpt.notify` and `talon_user.lib.modelHelpers.notify` to record state snapshots when notifications fired. Ran `_tests.test_gpt_suggest_validation.GPTSuggestValidationTests.test_json_suggestions_accept_snapshot_display_intent` under this instrumentation.
- **Result**: Hypothesis confirmed. The canonical suggestion (`intent_purpose == "vision"`) persisted unchanged after notifications, and skip counts remained empty. No additional canonicalisation or mutation occurred post-notification.
- **Evidence**: Instrumentation script (`PYTHONPATH=. python3 - <<'PY' ...`) captured:
  - `records`: one entry showing input suggestions matched stored state.
  - `notifications`: two messages (“opening” and “opened” window) each with the same canonical suggestion snapshot.

### Loop 6 — 2026-01-07
- **Focus question**: Are we still double-applying canonicalisation (helper + `record_suggestions`) in a way that could drop data in other scenarios?
- **Hypothesis**: When `record_suggestions` is supplied with canonical entries from `_suggest_prompt_recipes_core_impl`, the stored state mirrors the inputs.
- **Experiment**: Wrapped `talon_user.GPT.gpt.record_suggestions` with a logging delegate and ran `_tests.test_gpt_suggest_validation.GPTSuggestValidationTests` cases for display intent, alias-only fields, and persona axes under the wrapper.
- **Result**: All tests passed. Display-intent and persona-axis runs logged identical input and stored suggestions, confirming a single canonicalisation step. The alias-only test replaced `record_suggestions` with its own stub, so no delegate logs were captured, but the final stored state matched the test’s expected canonical form.
- **Evidence**: `python3 - <<'PY' ...` (TextTestRunner for the three targeted cases) producing `EVIDENCE::[...]` with per-test logs and final states.

## Focused Question
- None.

## Hypothesis
- Not applicable.

## Next Experiment
- None planned; awaiting new questions.
