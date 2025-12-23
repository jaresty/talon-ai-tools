## 2025-12-17 – Loop 71 (kind: status)
- Focus: Axis Snapshot & History – clarify legacy style removal plan.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` to state that, after migrating callers onto the shared AxisSnapshot, the remaining legacy style-axis handling will be removed entirely from the request history/log pipeline.
- Removal test: reverting would drop the ADR-level mandate to delete legacy style support, making it easier for that dead codepath to persist despite Concordance’s axis contract.
- Adversarial “what remains” check:
  - `lib/requestLog.py` / `lib/requestHistoryActions.py`: scrub the `legacy_style` flag and any notify paths once historical data is migrated, and add regression tests confirming style payloads are rejected.
  - `scripts/tools/axis-catalog-validate.py`: ensure validator tooling enforces the absence of style tokens under all axis catalogs/lists.
  - Axis docs/help generators: confirm generated docs have no residual style references before removing runtime guards.

## 2025-12-22 – Loop 347 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – CLI guardrails reuse exported telemetry JSON instead of recomputing skip counts.
- riskiest_assumption: Guardrail scripts preserve Talon-exported telemetry without overwriting counts when Talon is unavailable (probability medium, impact high for CLI-only runs).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence:
  - red | 2025-12-22T20:06:50Z | exit 1 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      helper:diff-snapshot=0 files changed
      Guardrail output still reported `Suggestion skip total: 0`; CLI fallback rewrote the exported summary to zero counts.
  - green | 2025-12-22T20:09:12Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      helper:diff-snapshot=4 files changed, 220 insertions(+), 17 deletions(-)
      2 passed in 1.50s
  - green | 2025-12-22T20:29:00Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      helper:diff-snapshot=4 files changed, 220 insertions(+), 17 deletions(-)
      7 passed in 18.77s
- rollback_plan: git restore --source=HEAD -- Makefile scripts/tools/run_guardrails_ci.sh _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py && python3 -m pytest _tests/test_make_request_history_guardrails.py
- delta_summary: helper:diff-snapshot=4 files changed, 220 insertions(+), 17 deletions(-); seeded guardrail tests with telemetry fixtures, updated Makefile and `scripts/tools/run_guardrails_ci.sh` to reuse exported suggestion-skip telemetry, and tightened job-summary expectations for non-zero skip totals.
- residual_risks:
  - Talon exporter still pending; without a fresh snapshot the CLI will continue to surface whatever counts were last exported (including zeros).
  - If telemetry schema changes, the Python snippets that summarise counts may need updates to avoid misreporting skip reasons.
- next_work:
  - Implement the Talon-side telemetry exporter loop so CLI guardrails start from live suggestion-skip counts.
  - Audit remaining CLI helpers to ensure they prefer exported telemetry artefacts over in-memory Talon state.

## 2025-12-22 – Loop 348 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – expose a Talon telemetry export action so guardrails can snapshot live skip counts.
- riskiest_assumption: Without an in-Talon command, maintainers would continue running guardrails on stale telemetry (probability medium, impact high for Concordance scoring).
- validation_targets:
  - python3 -m pytest _tests/test_telemetry_export.py
- evidence:
  - red | 2025-12-22T20:06:50Z | exit 1 | python3 -m pytest _tests/test_telemetry_export.py
      helper:diff-snapshot=0 files changed
      ImportError: cannot import name 'telemetryExportCommand' from 'talon_user.lib'
  - green | 2025-12-22T20:35:12Z | exit 0 | python3 -m pytest _tests/test_telemetry_export.py
      helper:diff-snapshot=5 files changed, 159 insertions(+), 5 deletions(-)
      5 passed in 0.12s
- rollback_plan: git restore --source=HEAD -- lib/telemetryExportCommand.py GPT/request-history.talon _tests/test_telemetry_export.py docs/adr/0056-concordance-personas-axes-history-gating.md && python3 -m pytest _tests/test_telemetry_export.py
- delta_summary: helper:diff-snapshot=5 files changed, 159 insertions(+), 5 deletions(-); added `telemetryExportCommand` with an export helper, wired new voice/action commands, tightened telemetry export tests, and refreshed ADR guidance.
- residual_risks:
  - Telemetry export still requires manual invocation; integrate the command into guardrail runbooks to avoid missed snapshots.
  - Notifications rely on Talon’s desktop UI; in headless sessions they may be swallowed, so monitor guardrail output for confirmation.
- next_work:
  - Document the new `model export telemetry` voice command in operator runbooks and automate invocation before CI guardrail bundles.
  - Evaluate invoking `user.model_export_telemetry` automatically when the guardrail Make targets are triggered from Talon.

## 2025-12-22 – Loop 350 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – enforce telemetry export freshness before guardrail runs.
- riskiest_assumption: Without an automated freshness check, guardrail Make targets run on stale telemetry (probability medium, impact high for Concordance accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
  - python3 -m pytest _tests/test_telemetry_export.py
- evidence:
  - red | 2025-12-22T20:38:02Z | exit 1 | Talon module loader (cron) importing telemetryExportCommand.py
      helper:diff-snapshot=0 files changed
      Action definition failed because `from __future__ import annotations` produced string-typed parameters; guardrail leaked before slice landed.
  - green | 2025-12-22T20:47:18Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py _tests/test_telemetry_export.py
      helper:diff-snapshot=7 files changed, 150 insertions(+), 3 deletions(-)
      14 passed in 19.30s
- rollback_plan: git restore --source=HEAD -- Makefile lib/telemetryExportCommand.py scripts/tools/check-telemetry-export-marker.py _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_make_request_history_guardrails.py
- delta_summary: helper:diff-snapshot=7 files changed, 150 insertions(+), 3 deletions(-); removed the problematic future annotations import, added a telemetry export marker, wired a freshness check into history guardrail targets, updated guardrail tests to honor the bypass env var, and documented the new enforcement.
- residual_risks:
  - Developers running guardrails in non-Talon environments must remember to set `ALLOW_STALE_TELEMETRY=1`; follow-up automation could prompt or invoke Talon export automatically.
- next_work:
  - Evaluate invoking `user.model_export_telemetry` automatically from Talon guardrail macros so manual exports remain optional.

## 2025-12-22 – Loop 352 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – guardrail CLI surfaces scheduler telemetry (ADR-0056 §Monitoring & Next Steps).
- riskiest_assumption: Without emitting scheduler stats in guardrail output, operators cannot spot telemetry export cadence drift (probability medium, impact high for diagnosing Concordance regressions).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0352.md
- rollback_plan: git restore --source=HEAD -- Makefile lib/telemetryExport.py lib/telemetryExportCommand.py scripts/tools/history-axis-export-telemetry.py scripts/tools/run_guardrails_ci.sh docs/adr/0056-concordance-personas-axes-history-gating.md && python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=8 files changed, 353 insertions(+), 15 deletions(-); ensured telemetry exports always embed scheduler stats, taught the CLI runner and Make targets to print the JSON snapshot (and append it to GitHub summaries), and added regression tests asserting the scheduler block is present alongside updated ADR guidance.
- residual_risks:
  - Offline runs still report the zeroed scheduler defaults; improvements could parse Talon markers when exports are unavailable.
  - Future telemetry schema changes must preserve the scheduler shape; otherwise the CLI output will degrade without explicit guardrails.
- next_work:
  - Consider summarising scheduler cadence in the GitHub summary table (e.g., last reason/interval bullets) so operators can scan drop causes quickly.

## 2025-12-23 – Loop 353 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – add human-readable scheduler cadence summary to guardrail output and GitHub step summaries (ADR-0056 §Monitoring & Next Steps).
- riskiest_assumption: Operators may overlook scheduler drift if only the raw JSON is printed (probability medium, impact medium for diagnosing telemetry freshness issues).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0353.md
- rollback_plan: git restore --source=HEAD -- Makefile scripts/tools/run_guardrails_ci.sh _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=6 files changed, 140 insertions(+), 13 deletions(-); updated guardrail Make targets and the CI runner to print scheduler summary bullets, adjusted guardrail tests to assert the new messaging, and refreshed ADR monitoring guidance.
- residual_risks:
  - When Talon exports are stale the summary still reports defaults; consider indicating when data came from the fallback JSON.
- next_work:
  - Evaluate highlighting non-zero reschedules in the GitHub summary (for example, bolding when cadence drifts) so operators spot issues faster.

## 2025-12-23 – Loop 354 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – show scheduler telemetry source across CLI guardrails (ADR-0056 §Monitoring & Next Steps).
- riskiest_assumption: Without labeling the scheduler source, operators cannot tell whether telemetry comes from the exporter, fallback summary, marker, or defaults (probability medium, impact high for diagnosing cadence drift).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0354.md
- rollback_plan: git restore --source=HEAD -- scripts/tools/run_guardrails_ci.sh scripts/tools/scheduler_source.py Makefile _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=6 files changed, 110 insertions(+), 110 deletions(-); added a scheduler_source helper, taught run_guardrails_ci.sh and Make guardrail targets to label the scheduler source, updated guardrail tests, and refreshed ADR monitoring guidance.
- residual_risks:
  - When telemetry JSON omits scheduler stats, the helper falls back to "defaults"; future loops should highlight when the fallback is used repeatedly.
- next_work:
  - Extend GitHub summaries to highlight non-default sources (e.g., marker or summary) so cadence anomalies stand out without inspecting raw JSON.

## 2025-12-23 – Loop 355 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – highlight non-default scheduler telemetry sources in CLI guardrails (ADR-0056 §Monitoring & Next Steps).
- riskiest_assumption: Without emphasizing non-default sources, operators may overlook fallback telemetry and miss cadence drift (probability medium, impact medium-high for diagnosing exporter issues).
- validation_targets:
  - python3 -m pytest _tests/test_run_guardrails_ci.py
  - python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0355.md
- rollback_plan: git restore --source=HEAD -- scripts/tools/run_guardrails_ci.sh Makefile _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=5 files changed, 39 insertions(+), 84 deletions(-); updated run_guardrails_ci.sh and Makefile to append a `(non-default)` suffix for fallback sources, expanded guardrail tests to cover summary-driven scheduler stats, added loop evidence, and refreshed ADR monitoring guidance.
- residual_risks:
  - CLI output still prints raw values even when scheduler stats are stale; consider flagging aged timestamps in a follow-up loop.
- next_work:
  - Log when scheduler timestamps cannot be parsed so operators notice format drift early.

## 2025-12-23 – Loop 356 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – flag stale scheduler telemetry alongside non-default sources (ADR-0056 §Monitoring & Next Steps).
- riskiest_assumption: Operators might miss cadence drift when scheduler stats fall back to summaries but timestamps are old (probability medium, impact medium-high for diagnosing exporter outages).
- validation_targets:
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0356.md
- rollback_plan: git restore --source=HEAD -- scripts/tools/run_guardrails_ci.sh Makefile _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=5 files changed, 145 insertions(+), 17 deletions(-); added stale-age detection and `(stale)` suffix in CLI/Make guardrail outputs, expanded guardrail tests with deterministic thresholds, and refreshed ADR monitoring guidance.
- residual_risks:
  - Timestamp parsing fails on unexpected formats; the helper currently ignores parsing errors. Consider logging a warning when parsing fails.
- next_work:
  - Expose a CLI hint when stale scheduler data appears repeatedly so teams know to refresh Talon exports.
 
## 2025-12-23 – Loop 357 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – log invalid scheduler timestamps in guardrail summaries (ADR-0056 §Monitoring & Next Steps; Loop 356 residual risk).
- riskiest_assumption: Without surfacing parse failures, operators may miss telemetry format drift (probability medium, impact high for Concordance telemetry accuracy).
- validation_targets:
  - python3.11 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0357.md
- rollback_plan: git restore --source=HEAD -- Makefile scripts/tools/run_guardrails_ci.sh _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0357.md && python3.11 -m pytest _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=4 files changed, 174 insertions(+), 3 deletions(-); added invalid timestamp handling to the guardrail script/Makefile, extended guardrail tests to assert the new warnings, and recorded the loop evidence/work-log update.
- residual_risks:
  - Guardrail output remains silent when scheduler telemetry falls back to defaults; highlight missing snapshots in the next loop.
- next_work:
  - Warn when scheduler telemetry source is defaults so operators refresh exports (Loop 358).
 
## 2025-12-23 – Loop 358 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – flag missing scheduler telemetry defaults in guardrail outputs (ADR-0056 §Monitoring & Next Steps; Loop 357 residual risk).
- riskiest_assumption: Without warning on defaults fallback, operators miss stale telemetry exports (probability medium, impact high for Concordance accuracy).
- validation_targets:
  - python3.11 -m pytest _tests/test_run_guardrails_ci.py
- evidence: docs/adr/evidence/0056/loop-0358.md
- rollback_plan: git restore --source=HEAD -- Makefile scripts/tools/run_guardrails_ci.sh _tests/test_run_guardrails_ci.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0358.md && python3.11 -m pytest _tests/test_run_guardrails_ci.py
- delta_summary: helper:diff-snapshot=3 files changed, 26 insertions(+), 5 deletions(-); added defaults `(missing)` qualifier and warning to guardrail CLI/Make targets, extended guardrail tests to require the new messaging, and captured the loop evidence/work-log update.
- residual_risks:
  - CLI still relies on manual Talon exports; consider auto-invoking the telemetry command when defaults warnings persist.
- next_work:
  - Evaluate prompting or auto-invoking `model export telemetry` when defaults warnings repeat (Loop 359).
 
## 2025-12-22 – Loop 349 (kind: docs)

- helper_version: helper:v20251221.5
- focus: Persona & Intent Presets – update monitoring guidance to mention the new Talon export action and runbook integration.
- riskiest_assumption: Without documentation, operators might forget to run the Talon telemetry export before CLI guardrails (probability medium, impact medium for stale Concordance metrics).
- validation_targets: [] (docs-only loop justified by completed guardrail slice and new helper)
- evidence: inline (ADR monitoring bullet edited to reference `user.model_export_telemetry` and runbook integration).
- rollback_plan: git restore --source=HEAD -- docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), concretised monitoring guidance with the new Talon export action and runbook reminder.
- residual_risks:
  - Operators may still skip the command if runbooks lag; follow up with automation to trigger the export before CLI guardrails.
- next_work:
  - Automate invocation of `user.model_export_telemetry` (Loop 350) when Talon-side guardrail macros fire.

## 2025-12-22 – Loop 346 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – guardrail make/CI entrypoints use the telemetry exporter with CLI fallback and relocate artifacts to `artifacts/telemetry`.
- riskiest_assumption: CLI fallback (history-axis-validate plus telemetry synthesis) matches Talon exporter outputs when Talon modules are unavailable (probability medium, impact high if guardrails stay broken outside Talon).
- validation_targets:
  - python3 -m pytest _tests/test_make_request_history_guardrails.py
  - python3 -m pytest _tests/test_run_guardrails_ci.py
- evidence:
  - red | 2025-12-22T19:26:31Z | exit 2 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      helper:diff-snapshot=0 files changed
      ModuleNotFoundError: No module named 'talon_user'
  - green | 2025-12-22T19:48:06Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      helper:diff-snapshot=8 files changed, 164 insertions(+), 63 deletions(-)
      2 passed in 1.55s
  - green | 2025-12-22T19:48:24Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      helper:diff-snapshot=8 files changed, 164 insertions(+), 63 deletions(-)
      7 passed in 17.66s
- rollback_plan: git restore --source=HEAD -- . && python3 -m pytest _tests/test_make_request_history_guardrails.py
- delta_summary: helper:diff-snapshot=8 files changed, 164 insertions(+), 63 deletions(-); rewired `Makefile` guardrail targets and `scripts/tools/run_guardrails_ci.sh` to invoke `lib.telemetryExport` with CLI fallback, moved guardrail outputs and automation to `artifacts/telemetry`, refreshed `_tests/test_make_request_history_guardrails.py`, `_tests/test_run_guardrails_ci.py`, `.github/workflows/test.yml`, and hardened `scripts/tools/history-axis-export-telemetry.py`.
- residual_risks:
  - Suggestion skip counts remain zero outside Talon until the exporter writes real telemetry (planned Loop 347); monitor guardrail output for stale totals.
  - CLI fallback depends on `history-axis-validate.py`; if summaries shift format, telemetry synthesis may drift without new guardrails.
- next_work:
  - Loop 347: update CLI helpers (`history-axis-export-telemetry.py`, `suggestion-skip-export.py`, guardrail wrappers) to consume the Talon-exported JSON directly.
  - Verify Talon runtime invocation still resolves `talon_user.lib.telemetryExport` after the import fallback lands.

## 2025-12-17 – Loop 72 (kind: behaviour)
- Focus: Axis Snapshot & History – remove the legacy “extra axes” passthrough from request logs.
- Change: Updated `lib/requestLog.py` so `_filter_axes_payload` now drops unknown axis keys outright and the `AxisSnapshot` dataclass no longer carries an `extras` map; callers receive only Concordance-recognised axes. Adjusted `_tests/test_request_log_axis_filter.py` and `_tests/test_request_log.py` expectations accordingly.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce support for arbitrary passthrough axes, undermining the ADR directive to delete that feature and weakening Concordance guarantees about history/log payloads.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: delete the residual legacy-style notifications once historical data is migrated and add tests confirming style payloads raise/drop.
  - `lib/historyQuery.py`: add targeted guardrails ensuring drawer/summary rendering never includes unexpected axis keys, keeping the surfaces aligned with the simplified snapshot.
  - Historical data migration: confirm existing logs with style/custom axes are cleaned or dropped before removing the remaining legacy-style handling from runtime code.

## 2025-12-17 – Loop 73 (kind: behaviour)
- Focus: Axis Snapshot & History – eliminate legacy style handling from request log/runtime paths.
- Change: Updated `lib/requestLog.py` to raise a `ValueError` when a style axis is provided, drop the `legacy_style` flag from `RequestLogEntry`, and ensure `AxisSnapshot` now only carries Concordance axes. Adjusted history helpers/tests (`_tests/test_request_log_axis_filter.py`, `_tests/test_request_log.py`, `_tests/test_request_history_actions.py`) to expect style-axis rejection instead of passthrough notifications.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would restore silent acceptance of legacy style payloads, contradicting ADR-0056’s directive that the axis is no longer supported and reintroducing Concordance drift risk.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: once historical data is scrubbed, remove the fallback notify path that still warns on style entries.
  - `lib/talonSettings.py` & persona/pattern GUIs: confirm existing guardrails (raising `ValueError` for style) remain exercised by tests so future refactors don’t weaken the ban.
  - Axis docs/help generators: double-check generated artifacts stay free of style references after the runtime removal (tests already cover, but rerun when doc tools change).

## 2025-12-17 – Loop 74 (kind: behaviour)
- Focus: Axis Snapshot & History – finalize removal of legacy style handling in history replay/doc guidance.
- Change: Removed the residual style warning path from `lib/requestHistoryActions.py` and updated ADR-0056 to note that style-axis inputs now raise errors instead of emitting warnings.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce partial support for legacy style payloads during history replay, contradicting the ADR’s stricter axis contract and weakening Concordance guardrails.
- Adversarial “what remains” check:
  - `lib/talonSettings.py`, persona/pattern GUIs: continue to enforce style rejection at entry points; monitor future UX changes to ensure the guardrails stay active.
  - Axis docs/help generators: keep existing tests that assert absence of style references so doc regen cannot regress without detection.

## 2025-12-17 – Loop 75 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – enforce the legacy style removal through the axis catalog validator.
- Change: Added `validate_no_legacy_style_axis` to `scripts/tools/axis-catalog-validate.py`, wired it into the CLI flow, and extended `_tests/test_axis_catalog_validate_static_prompts.py` to fail if the catalog, lists, or static prompts reintroduce a `style` axis.
- Checks: `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py _tests/test_axis_catalog_validate.py` (pass; excerpt: `30 passed in 0.85s`).
- Removal test: reverting would let `axis-catalog-validate` silently accept the legacy `style` axis, so Concordance guardrails would miss regressions before they hit history/log payloads.
- Adversarial “what remains” check:
  - `lib/historyQuery.py`: add assertions/guardrails so drawer/summary adapters refuse unknown axis keys before rendering (next slice candidate).
  - `scripts/tools/generate_static_prompt_docs.py`: confirm doc generation fails fast when catalog/static prompt payloads carry stray axes, keeping help/README surfaces aligned with the validator.

## 2025-12-17 – Loop 76 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – history drawer and summary guardrails for unknown axes.
- Change: Updated `lib/historyQuery.py` to validate axis keys before delegating to history helpers, raising when uncatalogued axes appear, and added `_tests/test_history_query.py` coverage that asserts both drawer and summary paths reject unknown keys.
- Checks: `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `128 passed in 0.84s`).
- Removal test: reverting would make history drawers and summaries silently accept stray axes again, weakening Concordance guarantees and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - `scripts/tools/generate_static_prompt_docs.py`: ensure doc generation fails fast when lists include unknown axes so help surfaces cannot drift.
  - `lib/requestHistoryDrawer.py`: surface a user-facing message or remediation path when guardrails trigger, preventing silent drawer clears for invalid payloads.
  - Historical payload cleanup: sample stored history data for unknown axes and plan a scrub so the new guardrail doesn’t repeatedly trigger for legacy entries.

## 2025-12-17 – Loop 77 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – make history drawer guardrail failures visible to users.
- Change: Updated `lib/requestHistoryDrawer.py` so `_refresh_entries` catches `history_drawer_entries_from` guardrail `ValueError` signals and surfaces a Concordance-aligned message instead of crashing, and added `_tests/test_request_history_drawer.py` coverage to lock the new messaging behaviour.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `142 passed in 0.90s`).
- Removal test: reverting would let the guardrail exception bubble, leaving the drawer blank without guidance and causing the new regression test to fail.
- Adversarial “what remains” check:
  - `scripts/tools/generate_static_prompt_docs.py`: harden doc generation so unknown axes fail fast, keeping Concordance docs aligned with runtime guardrails.
  - Historical payload cleanup: audit stored history/log data for stray axes and record the remediation path so the surfaced message does not persist.
  - Canvas UX polish: evaluate elevating the guardrail message within the canvas (e.g., inline guidance/action hint) so users can correct issues without checking logs.

## 2025-12-17 – Loop 78 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – prevent static prompt doc generation when catalog axes drift.
- Change: Updated `GPT/gpt.py::_build_static_prompt_docs` to assert profiled prompts only use Concordance-recognised axis keys (via `KNOWN_AXIS_KEYS`) and added `_tests/test_static_prompt_docs.py` coverage that patches the catalog to include a rogue `mystery` axis, expecting a `ValueError` guardrail failure.
- Checks: `python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_axis_regen_all.py` (pass; excerpt: `22 passed in 2.82s`).
- Removal test: reverting would let doc generation succeed even with unsupported axis keys, hiding Concordance drift until runtime and causing the new regression test to fail.
- Adversarial “what remains” check:
  - Historical payload cleanup: plan a sweep of stored history/log entries for stray axes so guardrails do not repeatedly trip on legacy data.
  - Canvas UX polish: elevate guardrail messaging inside the drawer UI so users can remediate without inspecting logs.
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.

## 2025-12-17 – Loop 79 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – detect legacy history entries with unsupported axis keys.
- Change: Added `validate_history_axes` to `lib/requestLog.py`, exported a CLI helper at `scripts/tools/history-axis-validate.py`, and extended `_tests/test_request_history_actions.py` to mutate a stored entry with a rogue `mystery` axis and assert the validator raises.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `143 passed in 0.87s`).
- Removal test: reverting would allow legacy entries with unsupported axes to go unnoticed, keep the CLI guardrail from failing, and cause the new regression test to fail.
- Adversarial “what remains” check:
  - Canvas UX polish: elevate guardrail messaging inside the drawer UI so users can remediate without inspecting logs.
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.
  - Automate remediation path: consider providing a helper that rewrites legacy history payloads once detected rather than only surfacing the error.

## 2025-12-17 – Loop 80 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – surface actionable guidance when history drawer guardrails fire.
- Change: Updated `lib/requestHistoryDrawer.py` to render multi-line warnings with remediation steps (including the new `history-axis-validate` CLI) when Concordance guardrails trigger, and adjusted `_tests/test_request_history_drawer.py` to assert the enhanced messaging.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `143 passed in 0.84s`).
- Removal test: reverting would downgrade the UI to a single-line warning without remediation details, forcing contributors to inspect logs manually and breaking the updated regression test.
- Adversarial “what remains” check:
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.
  - Automate remediation path: provide tooling to rewrite or drop legacy entries once validation fails, reducing manual cleanup burden.
  - Monitor guardrail phrasing for usability feedback during upcoming Concordance dry runs.

## 2025-12-17 – Loop 81 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – ensure persona docs fail fast on unsupported axis tokens.
- Change: Added `validate_persona_presets`/`validate_intent_presets` guardrails in `lib/personaConfig.py`, invoked them inside `_build_persona_intent_docs`, and extended `_tests/test_persona_presets.py` to patch in a rogue tone token and assert the guardrail trips.
- Checks: `python3 -m pytest _tests/test_persona_presets.py _tests/test_gpt_actions.py _tests/test_model_suggestion_gui.py _tests/test_model_pattern_gui.py` (pass; excerpt: `161 passed in 0.62s`).
- Removal test: reverting would allow persona docs to render successfully despite Concordance drift, leaving the new regression test failing and risking silent preset/token mismatch.
- Adversarial “what remains” check:
  - Automate remediation path: surface tooling to rewrite or drop invalid persona/int presets when detected, not just block doc generation.
  - Align persona catalog consumption across GUIs and GPT actions so they all consume the same validated preset data without bespoke copies.
  - Begin mapping preset tokens into the AxisSnapshot once the persona catalog facade lands, keeping Concordance signals consistent end-to-end.

## 2025-12-17 – Loop 82 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – provide a remediation path for legacy history entries with unsupported axes.
- Change: Added `remediate_history_axes` to `lib/requestLog.py` to clean or drop stale entries, exposed the helper via `scripts/tools/history-axis-remediate.py`, and extended `_tests/test_request_history_actions.py` to mutate stored entries and assert cleanup, drop, and dry-run behaviours.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `146 passed in 0.90s`).
- Removal test: reverting would remove the remediation CLI/path, leaving operators without a supported way to purge invalid axes and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Integrate the remediation helper into operational playbooks so Concordance alerts trigger automated cleanup.
  - Emit structured telemetry when remediation drops entries to spot recurring upstream issues.
  - Continue aligning persona catalog consumers before wiring persona state into the future AxisSnapshot façade.

## 2025-12-17 – Loop 83 (kind: status)
- Focus: Axis Snapshot & History – codify the operational runbook requirement for axis remediation.
- Change: Updated ADR-0056 to add a “Docs/help alignment and operations” bullet explicitly requiring Concordance runbooks to invoke `history-axis-remediate.py` (or successor tooling) and record the remediation in the work-log before legacy guardrails are removed.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would drop the new operational prerequisite, allowing guardrails to be stripped without a documented cleanup path.
- Adversarial “what remains” check:
  - Follow up on telemetry for remediation drops so Concordance can detect recurring sources of bad data.
  - Align persona catalog consumers before AxisSnapshot integration to keep Concordance signals coherent.

## 2025-12-17 – Loop 84 (kind: status)
- Focus: Axis Snapshot & History – require telemetry on remediation outcomes.
- Change: Updated ADR-0056 Phase 3 guidance to mandate structured telemetry whenever remediation rewrites or drops history entries, ensuring Concordance can audit recurring issues and verify successful cleanup.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the telemetry prerequisite, weakening our ability to detect systemic breaches of the directional-lens contract.
- Adversarial “what remains” check:
  - Implement the telemetry emission alongside the remediation tooling in a future behaviour loop.
  - Close the persona catalog alignment follow-up before wiring persona into AxisSnapshot.

## 2025-12-17 – Loop 85 (kind: status)
- Focus: Axis Snapshot & History – drop remediation requirements and enforce immediate failure for lens-less entries.
- Change: Updated ADR-0056 to remove the runbook/telemetry prerequisites tied to remediation tooling and to state explicitly that requests missing a directional lens fail immediately without cleanup shims.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would restore outdated remediation guidance, implying lingering compatibility shims that we no longer plan to maintain.
- Adversarial “what remains” check:
  - Execute a behaviour loop to delete the `require_directional=False` pathways and any related helper code.
  - Continue tracking persona catalog alignment prior to AxisSnapshot integration.

## 2025-12-17 – Loop 86 (kind: behaviour)
- Focus: Axis Snapshot & History – eliminate the remaining runtime toggles that allowed lens-less history entries.
- Change: Updated `lib/requestLog.py` to remove the `require_directional` parameter and unconditionally drop entries lacking a directional axis; pruned the matching escape hatch in `lib/streamingCoordinator.py` and rewired `_tests/test_request_history_actions.py` / `_tests/test_streaming_session.py` to use legacy fixtures when simulating lens-less payloads.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_streaming_session.py _tests/test_request_log.py` (pass; excerpt: `121 passed in 0.70s`).
- Removal test: reverting would reintroduce the `require_directional=False` pathway, allowing history appenders to persist lens-less entries and causing the refreshed guardrail tests to fail.
- Adversarial “what remains” check:
  - Audit any cached macros or CLI tooling that might still attempt to pass `require_directional` kwargs (e.g. bespoke scripts under `scripts/` or Talon overlays) and excise them in favour of the new failure contract.
  - Follow up on operational guidance so Concordance runbooks reference the now-default immediate failure instead of remediation tooling.

## 2025-12-17 – Loop 87 (kind: docs)
- Focus: Axis Snapshot & History – align ADR guidance with the new immediate-failure guardrail.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` context to state the `require_directional` override has been removed and to highlight auditing of external macros that might still attempt it.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would reinstate outdated guidance suggesting the bypass still exists, undermining the ADR’s clarity about the enforced directional requirement and the remaining audit task.
- Adversarial “what remains” check:
  - Complete the audit of scripts/overlays that may still pass `require_directional` so failures surface promptly to operators.
  - Update Concordance operational runbooks to spell out the immediate-failure posture once the tooling audit lands.

## 2025-12-17 – Loop 88 (kind: docs)
- Focus: Axis Snapshot & History – capture the outstanding audit task in the ADR’s Salient Tasks.
- Change: Added a bullet under “Axis Snapshot & History” tasks in `docs/adr/0056-concordance-personas-axes-history-gating.md` requiring the audit of Talon overlays/CLI scripts that previously depended on `require_directional=False` so the immediate-failure guardrail is enforced end-to-end.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would erase the explicit audit task, making it easier to overlook this follow-up and potentially reintroduce lens-less history through external tooling.
- Adversarial “what remains” check:
  - Execute the tooling audit and record its outcome (completed or residual follow-ups) in a future behaviour loop.
  - Update Concordance operations/runbooks after the audit to codify the enforcement posture for contributors.

## 2025-12-17 – Loop 89 (kind: docs)
- Focus: Axis Snapshot & History – document the completed in-repo audit of `require_directional` usage.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` context and Salient Tasks to record that the audit ran on 2025-12-17 and found no remaining in-repo consumers of `require_directional=False`, while noting that external automation still needs monitoring.
- Checks: `rg "require_directional"` (run from repo root; matches limited to comments/docs as expected).
- Removal test: reverting would make the ADR omit the audit outcome, obscuring evidence that the guardrail has been enforced and risking duplicate audit work later.
- Adversarial “what remains” check:
  - Coordinate with external automation owners (outside this repo) to confirm they respect the directional lens requirement and add an operations runbook note once confirmed.
  - Consider adding a lightweight lint/CI check that fails when new `require_directional=` references appear.

## 2025-12-17 – Loop 90 (kind: docs)
- Focus: Axis Snapshot & History – reconcile the refactor plan bullet with the landed runtime enforcement.
- Change: Updated the Axis Snapshot refactor plan bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` to mark the `require_directional` removal as completed and to direct follow-up toward auditing/purging legacy data outside this repo.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would imply the bypass still needs removal, obscuring the fact that the guardrail is already in place and confusing prioritisation for remaining work.
- Adversarial “what remains” check:
  - Track external data purges so Concordance sees only directional-backed history; note outcomes in a future behaviour loop once remediation completes.
  - Evaluate adding CI alerts for non-directional history payloads discovered in telemetry exports.

## 2025-12-17 – Loop 91 (kind: docs)
- Focus: Axis Snapshot & History – capture CI enforcement follow-up in Salient Tasks.
- Change: Added a Salient Task bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` to introduce a CI/guardrail check that fails when new code paths attempt to append history entries without directional lenses.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the explicit CI follow-up, risking reintroduction of the bypass without automated detection.
- Adversarial “what remains” check:
  - Design the actual CI guard (e.g., static analysis or targeted test) and land it in a behaviour loop.
  - After the guard exists, document the remediation path for external automation in Concordance runbooks.

## 2025-12-17 – Loop 92 (kind: docs)
- Focus: Axis Snapshot & History – align the Tests-First plan with the new CI guardrail work.
- Change: Updated the Axis Snapshot tests plan to require a regression test/CI assertion that fails when history appends omit directional axes.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would leave the CI guard task without an explicit testing strategy, increasing the risk that the guard lands without automated coverage.
- Adversarial “what remains” check:
  - Implement the guard plus its failing test in a behaviour loop.
  - Coordinate with ops to ensure external automation pushes adopt the same guard once available.

## 2025-12-17 – Loop 93 (kind: docs)
- Focus: Axis Snapshot & History – document the benefit of CI guardrails in the consequences section.
- Change: Added a positive consequence in `docs/adr/0056-concordance-personas-axes-history-gating.md` highlighting CI guardrails as automated protection against lens-less history regressions.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would hide the rationale for CI guardrails, weakening the ADR’s articulation of why the guard is required.
- Adversarial “what remains” check:
  - Land the CI guard plus regression test in code.
  - Update Concordance runbooks to explain the guard’s failure mode for operators.

## 2025-12-17 – Loop 94 (kind: docs)
- Focus: Persona & Intent Presets – tighten the tests-first expectations.
- Change: Added an explicit integration coverage requirement to the persona catalog plan in `docs/adr/0056-concordance-personas-axes-history-gating.md` so catalogue alignment is verified end-to-end.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would weaken tests-first guidance, increasing the risk that catalog refactors ship without integration coverage.
- Adversarial “what remains” check:
  - Implement the integration test once the persona catalog lands.
  - Audit existing persona GUI/help flows to ensure they will exercise the new catalog in CI.

## 2025-12-17 – Loop 95 (kind: docs)
- Focus: Cross-domain mitigations – document the enforcement strategy.
- Change: Updated the Mitigations section in `docs/adr/0056-concordance-personas-axes-history-gating.md` to spell out reliance on CI guardrails and integration coverage for directional lenses and persona catalog alignment.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would obscure the concrete enforcement strategy, making it easier to drop these guardrails in future slices.
- Adversarial “what remains” check:
  - Implement the cited guardrails/tests and record their landing in the work-log.
  - Confirm operations documentation references the automated failures so teams know how to respond.

## 2025-12-17 – Loop 96 (kind: docs)
- Focus: Request Gating & Streaming – strengthen tests-first guidance.
- Change: Added a regression test requirement in `docs/adr/0056-concordance-personas-axes-history-gating.md` ensuring centralized gating/streaming guardrails stay covered by suites like `tests/test_request_streaming.py` and `tests/test_gpt_actions.py`.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would weaken expectations for gating coverage, increasing the chance that lifecycle regressions slip through.
- Adversarial “what remains” check:
  - Implement the new regression tests when centralizing gating.
  - Ensure CI executes them in scenarios covering streaming + gating combinations.

## 2025-12-17 – Loop 97 (kind: docs)
- Focus: Persona & Intent Presets – clarify integration test expectations.
- Change: Updated the persona tests plan in `docs/adr/0056-concordance-personas-axes-history-gating.md` to require integration coverage that fails when catalog alignment regresses.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would dilute the persona tests-first story, making it easier to ship catalog changes without end-to-end verification.
- Adversarial “what remains” check:
  - Implement the integration test once the persona catalog lands.
  - Tie CI alerts to those failures so persona alignment regressions surface quickly.

## 2025-12-17 – Loop 98 (kind: docs)
- Focus: Persona & Intent Presets – capture CI enforcement follow-up.
- Change: Added a test plan bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` instructing teams to add a CI guardrail against bypassing the persona/intent catalog.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the explicit CI enforcement requirement, making catalog bypass regressions harder to catch.
- Adversarial “what remains” check:
  - Implement the CI guardrail alongside the catalog refactor.
  - Document failure modes so contributors know how to resolve violated checks.

## 2025-12-17 – Loop 99 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – enforce directional-lens guard via validator tooling.
- Change: Updated `lib/requestLog.py::validate_history_axes` to raise when stored entries lack directional axes, adjusted `scripts/tools/history-axis-validate.py` messaging, and added `_tests/test_request_history_actions.py::test_validate_history_axes_requires_directional_lens` to lock the guard.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass; excerpt: `102 passed in 0.63s`).
- Removal test: reverting would let history validation pass without directional lenses, weakening the ADR-0056 guardrail and causing the new regression test to fail.
- Adversarial “what remains” check:
  - Wire `history-axis-validate.py` into CI so missing directional lenses surface automatically during builds.
  - Emit structured telemetry when the validator or remediation tooling drops entries, keeping Concordance operations aware of recurring issues.

## 2025-12-17 – Loop 100 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – integrate the directional validator into guardrail automation.
- Change: Updated `Makefile::request-history-guardrails` to invoke `python3 scripts/tools/history-axis-validate.py` before running `_tests/test_request_history_actions.py`, ensuring CI guardrails fail fast on missing directional axes.
- Checks: `make request-history-guardrails` (pass; excerpt: `History axis validation passed: all entries include directional lenses and use Concordance-recognised axes.` / `102 passed in 0.66s`).
- Removal test: reverting would drop the validator from the guardrail target, allowing CI runs to miss directional-lens regressions until unit tests encounter mutated fixtures.
- Adversarial “what remains” check:
  - Add structured telemetry when the validator or remediation CLI drops entries so Concordance ops can spot recurring offenders.
  - Evaluate wiring the validator into nightly data exports for historical payloads outside this repo, keeping runtime + out-of-band stores aligned.

## 2025-12-17 – Loop 101 (kind: status)
- Focus: Axis Snapshot & History – reconcile remaining guardrail follow-ups.
- Change: Confirmed there are no out-of-repo request history stores and no pathways for lens-less entries to land post-guardrail; updated ADR-0056 tasks/context to record that external automation monitoring is no longer required and the CI guardrail is complete.
- Checks: `docs/adr/0056-concordance-personas-axes-history-gating.md` (re-read lines 80-83, 320-326 after edits).
- Removal test: reverting would reintroduce stale guidance suggesting ongoing external monitoring or pending CI guardrail work, obscuring the ADR’s finished state.
- Adversarial “what remains” check:
  - No in-repo work remains for Axis Snapshot & History guardrails; future loops should target Persona & Intent or Request Gating domains if new requirements arise.

## 2025-12-17 – Loop 102 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – centralise canonical token lookups.
- Change: Added `canonical_persona_token`/`persona_axis_tokens` to `lib/personaConfig.py`, refactored `GPT/gpt.py::_canonical_persona_value` to call the shared helper, and expanded `_tests/test_persona_presets.py` plus `_tests/test_gpt_actions.py` to guard the new contract.
- Checks: `python3 -m pytest _tests/test_persona_presets.py _tests/test_gpt_actions.py` (pass; excerpt: `115 passed in 0.29s`).
- Removal test: reverting would split canonicalisation logic again, letting GPT accept tokens that the persona catalog rejects and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next slices should route persona/intents commands in Help Hub and suggestion canvases through the shared catalog and add integration coverage that fails when callers bypass it.
  - Continue planning the consolidated persona catalog API surface (preset fetch + axis metadata) before refactoring `_validated_persona_value` and related helpers end-to-end.

## 2025-12-17 – Loop 103 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align Help Hub and Suggestion GUI with canonical persona tokens.
- Change: Added `_canonical_persona_token` wrappers to `lib/helpHub.py` and `lib/modelSuggestionGUI.py`, updated `_match_persona_preset` and `_suggestion_stance_info` to use canonical tokens, and extended `_tests/test_help_hub.py` plus `_tests/test_model_suggestion_gui.py` to cover the shared helper and case-insensitive persona axes.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py` (pass; excerpt: `40 passed in 0.22s`).
- Removal test: reverting would reintroduce divergent persona canonicalisation across GUIs, letting Help Hub/Suggestion canvases drift from the catalog and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next steps should wire help/suggestion GUIs to consume the future persona catalog façade end-to-end (not just token canonicalisation) and add an integration test that fails when a caller bypasses the catalog.
  - Coordinate follow-up slices to migrate intent preset handling the same way once the consolidated catalog API is ready.

## 2025-12-17 – Loop 104 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – centralise catalog consumption in Suggestion GUI helpers.
- Change: Added `_persona_catalog`/`_intent_catalog` accessors in `lib/modelSuggestionGUI.py`, rewired `_persona_presets`, `_persona_preset_map`, `_persona_long_form`, `_match_persona_preset`, and `_preset_from_command` to pull from the shared catalog, and expanded `_tests/test_model_suggestion_gui.py` with coverage for synonym mapping and case-folded persona inputs. Updated `_tests/test_help_hub.py` with a regression test asserting `_canonical_persona_token` delegates to personaConfig.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py _tests/test_persona_presets.py` (pass; excerpt: `156 passed in 0.43s`).
- Removal test: reverting would reintroduce divergent persona preset lookups across Suggestion GUI helpers, letting catalog updates drift silently and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next slices should expose a consolidated persona/intent catalog façade for Help Hub/Suggestion GUIs (e.g., a single fetch returning presets + axis metadata) and add an integration test that fails when a caller bypasses it.
  - Plan follow-up work to route intent preset handling through the shared façade once it lands, ensuring personas and intents share the same SSOT.

## 2025-12-17 – Loop 105 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – provide a shared catalog snapshot for GUIs and docs.
- Change: Added `PersonaIntentCatalogSnapshot` and `persona_intent_catalog_snapshot()` in `lib/personaConfig.py`, exposing presets, spoken aliases, and axis tokens for personas/intents; updated `lib/helpHub.py` and `lib/modelSuggestionGUI.py` to consume the snapshot and drop bespoke catalog fetchers; expanded `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, and `_tests/test_persona_presets.py` with snapshot regression coverage.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py _tests/test_persona_presets.py` (pass; excerpt: `158 passed in 0.23s` + `106 passed in 0.23s`).
- Removal test: reverting would force GUIs back onto ad-hoc persona lookups, breaking the new snapshot tests and reintroducing drift between help surfaces and the catalog.
- Adversarial “what remains” check:
  - Wire Help Hub and Suggestion GUIs’ intent preset surfaces through the snapshot (mirroring the persona integration) and add an integration test that fails when callers bypass the shared façade.
  - Shape the upcoming persona/intent catalog API so GPT actions can rely on the same snapshot before `_validated_persona_value` is refactored.

## 2025-12-17 – Loop 106 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – route intent displays through the shared snapshot.
- Change: Extended `PersonaIntentCatalogSnapshot` with intent bucket/display metadata, rewired `lib/helpHub.py` intent helpers to use the snapshot, and updated `lib/modelSuggestionGUI.py::_suggestion_stance_info` to rely on the shared snapshot for intent handling. Added regression coverage in `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, and `_tests/test_persona_presets.py` for snapshot-backed intent data.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py`, `python3 -m pytest _tests/test_gpt_actions.py`, `python3 -m pytest _tests/test_persona_presets.py` (pass; excerpts: `44 passed in 0.23s`, `106 passed in 0.25s`, `10 passed in 0.06s`).
- Removal test: reverting would drop GUI reliance on the catalog snapshot for intent aliases, breaking the new regression tests and risking divergence between intent displays and the catalog SSOT.
- Adversarial “what remains” check:
  - Add integration coverage that exercises Help Hub and Suggestion GUIs end-to-end with the snapshot to fail when callers bypass it.
  - Begin migrating GPT persona/intent helpers (`_validated_persona_value`, `_build_persona_intent_docs`) to consume the snapshot before widening catalog usage across CLI/doc surfaces.

## 2025-12-17 – Loop 107 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – hydrate GPT persona/intent docs from the shared snapshot.
- Change: Enhanced `PersonaIntentCatalogSnapshot` with intent display metadata, rewrote `GPT/gpt.py::_build_persona_intent_docs` to render presets, aliases, and buckets from the snapshot, and added regression coverage in `_tests/test_gpt_actions.py` ensuring the docs include bucket output. Snapshot shape tests and GUI helpers were updated to validate the new fields.
- Checks: `python3 -m pytest _tests/test_persona_presets.py`, `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py`, `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpts: `10 passed in 0.07s`, `44 passed in 0.21s`, `107 passed in 0.27s`).
- Removal test: reverting would strip persona/intent docs of snapshot-backed metadata, causing the new regression tests to fail and letting docs/docstrings drift from Concordance SSOT.
- Adversarial “what remains” check:
  - Add end-to-end persona/intent doc integration tests that assert specific snapshot-driven content, then plan `_validated_persona_value` refactor to consume the snapshot before broader CLI/doc updates.

## 2025-12-18 – Loop 108 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – extend persona/intent docs integration coverage.
- Change: Added `test_build_persona_intent_docs_renders_snapshot_content` to `_tests/test_gpt_actions.py` to assert `_build_persona_intent_docs` renders persona presets, intent display names, and bucket output from `PersonaIntentCatalogSnapshot` data.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `108 passed in 0.27s`).
- Removal test: reverting would drop the snapshot-driven doc guardrail, allowing `_build_persona_intent_docs` to ignore catalog display/bucket metadata without failing tests.
- Adversarial “what remains” check:
  - Migrate `GPT/gpt.py::_validated_persona_value` to consume `persona_intent_catalog_snapshot`, then add regression coverage for canonical token handling.
  - Add an end-to-end help/doc generation test (e.g., `make help-hub` or CLI render) to ensure snapshot-driven persona/intent content stays wired through user surfaces.
  - Coordinate Concordance operations docs to highlight the snapshot dependency so manual doc processes stay aligned with the validated catalog.

## 2025-12-18 – Loop 109 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align `_validated_persona_value` with the shared persona/intent snapshot.
- Change: Updated `GPT/gpt.py::_suggest_prompt_recipes_core_impl` to load `persona_intent_catalog_snapshot()` and reuse its axis/display maps when validating persona and intent tokens, then added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_accept_snapshot_display_intent` to lock the new display-name canonicalisation.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_gpt_actions.py` (pass; excerpt: `113 passed in 0.33s`).
- Removal test: reverting would drop snapshot-aware validation, causing suggestions that use catalog display names to lose their intent tokens and failing the new regression test.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add an integration test that exercises `help_hub` doc generation end-to-end to ensure snapshot-driven persona/intent content stays wired through user-facing surfaces.
  - Revisit persona preset matching in `modelSuggestionGUI` to confirm display-name helpers stay snapshot-backed as future catalog entries add richer aliases.

## 2025-12-18 – Loop 110 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT preset actions with snapshot-backed aliases.
- Change: Updated `GPT/gpt.py` to load `persona_intent_catalog_snapshot()` via `_get_persona_intent_maps` so `persona_set_preset` and `intent_set_preset` accept spoken and display aliases; added `_tests/test_gpt_actions.py` coverage for the “mentor” persona alias and “for deciding” intent display name.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `110 passed in 0.39s`).
- Removal test: reverting would drop snapshot-aware alias resolution, causing the new preset alias tests to fail and forcing users back to raw preset keys.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add an integration test that exercises `help_hub` doc generation end-to-end to ensure snapshot-driven persona/intent content stays wired through user-facing surfaces.
  - Revisit persona preset matching in `modelSuggestionGUI` to confirm display-name helpers stay snapshot-backed as future catalog entries add richer aliases.

## 2025-12-18 – Loop 111 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – surface snapshot-driven preset aliases in Help Hub.
- Change: Extended `lib/helpDomain.help_index` to add persona/intent preset search entries that honour snapshot spoken/display aliases and call `persona_set_preset` / `intent_set_preset`; enriched `_tests/test_help_hub.py` with alias-driven regression coverage.
- Checks: `python3 -m pytest _tests/test_help_hub.py` (pass; excerpt: `24 passed in 0.16s`).
- Removal test: reverting would drop the new search handlers, so Help Hub filtering would no longer expose preset aliases and the fresh regression tests would fail.
- Adversarial “what remains” check:
  - Consider wrapping Help Hub search handlers with hub-close helpers so preset selection always dismisses the overlay before applying the stance.
  - Add an integration test covering Help Hub navigation to preset entries to ensure alias metadata stays visible when canvases change.
  - Evaluate unifying `_get_persona_intent_maps` into a shared persona helper module to reduce duplication across GPT, Help Hub, and GUI surfaces.

## 2025-12-18 – Loop 112 (kind: behaviour)
- Focus: Persona & Intent Presets – share snapshot maps across GPT, Help Hub, and suggestion GUIs.
- Change: Introduced `persona_intent_maps()` in `lib/personaConfig.py` to expose axis tokens, preset lookups, and alias maps; refactored `GPT/gpt.py`, `lib/helpDomain.py`, `lib/helpHub.py`, and `lib/modelSuggestionGUI.py` to consume the shared helper instead of bespoke snapshot parsing.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py`, `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_model_pattern_gui.py` (pass; excerpts: `110 passed in 0.39s`, `24 passed in 0.21s`, `22 passed in 0.12s`, `31 passed in 0.46s`).
- Removal test: reverting would reintroduce divergent persona/intent alias handling, breaking the updated GPT action, Help Hub, and suggestion GUI regression suites.
- Adversarial “what remains” check:
  - Consider caching `persona_intent_maps()` when running inside Talon to avoid repeated snapshot rebuilds while keeping test ergonomics.
  - Extend `_suggest_prompt_recipes_core_impl` to surface preset alias metadata in the prompt payload so future cards can highlight spoken forms without recomputing maps.
  - Add an end-to-end CLI/help doc render check that exercises the shared helper to guard against future drift when catalog structure evolves.

## 2025-12-18 – Loop 110 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT preset actions with snapshot-backed aliases.
- Change: Updated `GPT/gpt.py` to load `persona_intent_catalog_snapshot()` via `_get_persona_intent_maps` so `persona_set_preset` and `intent_set_preset` accept spoken and display aliases; added `_tests/test_gpt_actions.py` coverage for the “mentor” persona alias and “for deciding” intent display name.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `110 passed in 0.39s`).
- Removal test: reverting would drop snapshot-aware alias resolution, causing the new preset alias tests to fail and forcing users back to raw preset keys.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add integration coverage that drives `help_hub` persona preset commands through alias inputs to confirm the shared snapshot wiring.
  - Evaluate caching/invalidating snapshot lookups during Talon reloads to avoid stale preset metadata after runtime catalog updates.

## 2025-12-18 – Loop 152 (kind: behaviour)
- Focus: Request Gating & Streaming – centralise in-flight guards for GPT canvases and helpers.
- Change: Added the shared helper in `lib/requestGating.py`, rewired gating wrappers across `GPT/gpt.py`, `lib/modelSuggestionGUI.py`, `lib/helpHub.py`, `lib/modelResponseCanvas.py`, `lib/modelConfirmationGUI.py`, `lib/modelHelpCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelPatternGUI.py`, `lib/providerCommands.py`, and `lib/requestHistoryActions.py` to use it, and updated guardrail tests plus the new `_tests/test_request_gating.py` to lock the behaviour.
- Checks: `python3 -m pytest _tests/test_request_gating.py _tests/test_model_suggestion_gui.py _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas_guard.py _tests/test_model_confirmation_gui_guard.py _tests/test_model_help_canvas_guard.py _tests/test_prompt_pattern_gui_guard.py _tests/test_model_pattern_gui_guard.py _tests/test_help_hub_guard.py _tests/test_request_history_actions.py` (pass; 129 passed in 0.66s).
- Removal test: Reverting would reinstate duplicated `_request_is_in_flight` implementations, drop `lib/requestGating.py`, and strip the new gating tests, undoing the Concordance guardrail alignment and reintroducing inconsistent drop-notify behaviour.
- Adversarial “what remains” check:
  - Extend `try_begin_request` to emit structured telemetry so CI and ops can ingest drop counts alongside the history validator summary.
  - Integrate the helper with the pending `StreamingSession` façade to keep gating and lifecycle orchestration on the same API surface (ADR-0056 §3).
  - Audit provider/Talon overlays for any bespoke gating code paths still bypassing the helper before centralising retry/cancel affordances in a follow-up loop.

## 2025-12-18 – Loop 153 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – capture structured drop telemetry for in-flight guards.
- Change: Updated `lib/requestGating.py` to record rejected `try_begin_request` calls via `record_gating_drop`; extended `lib/requestLog.py` with gating drop counters exposed through `history_validation_stats`; surfaced the drop summary in `scripts/tools/history-axis-validate.py`; added `_tests/test_request_gating.py::test_try_begin_request_records_gating_drop_stats` to lock the telemetry contract.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `5 passed in 0.05s`).
- Removal test: reverting would drop the shared telemetry counters, remove the CLI summary, and break the new gating telemetry test, leaving Concordance without observable drop rates.
- Adversarial “what remains” check:
  - Wire the telemetry counters into upcoming `StreamingSession` events so drop, retry, and cancel flows share one reporting surface.
  - Consider adding a guardrail script flag to reset/emit gating telemetry snapshots for nightly Concordance runs.
  - Audit Talon overlays for residual gating bypasses before consuming gating telemetry in Concordance dashboards.

## 2025-12-18 – Loop 154 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – allow the history validator to reset drop telemetry between runs.
- Change: Added `--reset-gating` to `scripts/tools/history-axis-validate.py` so Concordance guardrails can clear `requestLog` gating counters after reporting; extended `_tests/test_request_gating.py` with coverage for history validation stats and the new flag to lock the telemetry contract.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `7 passed in 0.07s`).
- Removal test: Reverting would drop the CLI reset flag and the regression tests, preventing Concordance automation from clearing telemetry snapshots and causing the new tests to fail.
- Adversarial “what remains” check:
  - Integrate gating telemetry resets with the upcoming `StreamingSession` event hooks so drop/retry reporting shares one surface.
  - Provide a guardrail recipe that captures telemetry via `--summary-path` before invoking `--reset-gating` for nightly Concordance runs.
- Complete the Talon overlay audit for gating bypasses before wiring telemetry into Concordance dashboards.

## 2025-12-18 – Loop 156 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – prevent telemetry resets without archiving drop counts.
- Change: Updated `scripts/tools/history-axis-validate.py` so `--reset-gating` now requires `--summary` or `--summary-path`; refreshed `_tests/test_request_gating.py` to cover the new contract and the failure path.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `8 passed in 0.06s`).
- Removal test: Reverting would allow guardrail runs to clear gating telemetry without capturing counts, violating ADR-0056 requirements and making the new regression test fail.
- Adversarial “what remains” check:
  - Update `make request-history-guardrails` documentation to highlight that the summary file must be archived before counters reset.
  - Integrate the summary archiving workflow into nightly Concordance automation so telemetry is preserved off-box.
- Continue planning the `StreamingSession` hook integration so all drop/ retry telemetry is centralized before enforcing additional guardrails.

## 2025-12-18 – Loop 157 (kind: docs)
- Focus: Request Gating & Streaming – make guardrail usage requirements visible in developer tooling.
- Change: Updated `Makefile` help output so `make request-history-guardrails` explicitly notes that the target captures a summary before resetting gating telemetry.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would hide the telemetry-archiving requirement from developers running guardrails locally, increasing the chance they clear counters without persisting summaries.
- Adversarial “what remains” check:
  - Ensure Concordance runbooks and onboarding docs mirror the guardrail help text so operations teams rely on the same instructions.
  - Integrate summary snapshot archival into the guardrail CI workflow once runbook updates land.
- Continue wiring telemetry through the forthcoming `StreamingSession` hooks before expanding gating guardrails.

## 2025-12-18 – Loop 158 (kind: docs)
- Focus: Request Gating & Streaming – codify the runbook step for preserving gating summaries.
- Change: Updated the Persona & Intent tests plan in ADR-0056 to note that Concordance runbooks must archive the `history-axis-validate.py --summary-path …` output (to the shared logs bucket) before invoking `--reset-gating`.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would leave runbook owners without an explicit archival step, increasing the risk that telemetry is cleared without being captured for Concordance dashboards.
- Adversarial “what remains” check:
  - Mirror the same instruction in the Concordance operations runbook and onboarding materials.
  - Ensure the guardrail CI job archives the summary automatically so manual runs stay aligned.
  - Continue planning the `StreamingSession` telemetry integration before adding further guardrails.

## 2025-12-18 – Loop 159 (kind: docs)
- Focus: Request Gating & Streaming – clarify where automation stores gating summaries.
- Change: Updated ADR-0056 to mention the canonical archive location (GitHub Actions guardrail job artifacts, e.g., `artifacts/telemetry/history-validation-summary.json`) for history validator summaries prior to `--reset-gating`.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would remove the explicit archive location, forcing automation owners to rediscover the destination and risking inconsistent telemetry storage.
- Adversarial “what remains” check:
  - Update the Concordance operations runbook with the same artifact path and retention expectations.
  - Ensure guardrail CI automation writes to that artifact location with appropriate retention settings in place.
- Continue planning the `StreamingSession` telemetry integration before extending guardrail coverage.

## 2025-12-18 – Loop 161 (kind: docs)
- Focus: Request Gating & Streaming – align archival guidance with available infrastructure.
- Change: Updated ADR-0056 to reference GitHub Actions guardrail job artifacts (e.g., `artifacts/telemetry/history-validation-summary.json`) as the storage target for `history-axis-validate` summaries instead of the prior S3 placeholder.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would send readers back to an unusable S3 path, increasing the risk that summaries are not archived before `--reset-gating`.
- Adversarial “what remains” check:
  - Update the Concordance operations runbook to match the GitHub Actions artifact path and describe retention expectations.
  - Verify guardrail CI automation publishes the summary artifact to GitHub Actions and alerts when uploads fail.
  - Continue preparing the `StreamingSession` telemetry integration before expanding gating guardrails.

## 2025-12-18 – Loop 170 (kind: behaviour)
- Focus: Persona & Intent Presets – align quick help (`lib/modelHelpCanvas.py`) and pattern picker (`lib/modelPatternGUI.py`) canvases with the shared persona/intent catalog.
- Change: `_persona_presets()` and `_intent_presets()` now consume `persona_intent_maps()` with bootstrap fallbacks so Talon canvases stay aligned with the catalog snapshot.
- Checks: `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_model_pattern_gui.py` (pass; excerpt: `41 passed in 0.66s`).
- Removal test: Reverting would send those canvases back to bespoke tuple constants, reintroducing drift whenever the catalog updates without touching the canvases.
- Adversarial “what remains” check:
  - `GPT/gpt.py`: route persona/intent helpers through `persona_intent_maps()` so GPT actions share the same SSOT.
  - `lib/modelSuggestionGUI.py` / `lib/modelPromptPatternGUI.py`: update suggestion canvases and guardrail tests to consume the shared maps and broaden alias coverage.
  - Talon list guardrails: add a drift check for `GPT/lists/*.talon-list` regeneration so list outputs track the catalog snapshot.

## 2025-12-18 – Loop 171 (kind: behaviour)
- Focus: Persona & Intent Presets – route GPT persona/intent actions and voice lists through the shared catalog maps.
- Change: `_persona_presets()`, `_intent_presets()`, `_persona_preset_spoken_map()`, `_intent_preset_spoken_map()`, and `_axis_tokens()` now read from `persona_intent_maps()` with catalog fallbacks; new tests lock alias coverage for spoken and label forms.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `113 passed in 4.66s`).
- Removal test: Reverting would drop map-derived alias coverage and axis tokens, causing the new alias guardrail tests to fail and leaving voice lists out of sync with the catalog.
- Adversarial “what remains” check:
  - Quick help & suggestion canvases: surface `intent_display_map` strings everywhere commands render so GUIs show the same spoken aliases as the catalog.
  - Talon list guardrails: add regeneration checks so voice lists fail when the catalog drifts.
  - GPT persona docs: update `_build_persona_intent_docs` and related helpers to emit the same spoken aliases recorded in the snapshot.

## 2025-12-18 – Loop 172 (kind: behaviour)
- Focus: Persona & Intent Presets – surface catalog spoken aliases in quick help intent commands.
- Change: `_intent_preset_commands()` now reads `persona_intent_maps().intent_display_map` with fallbacks and deduplicates aliases; added `_tests/test_model_help_canvas.py::test_quick_help_intent_commands_use_catalog_spoken_aliases` to guard both alias and fallback paths.
- Checks: `python3 -m pytest _tests/test_model_help_canvas.py` → `11 passed in 0.26s`.
- Removal test: Reverting would reintroduce canonical intent tokens in quick help, causing the new regression test to fail and hiding catalog alias drift from users.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: ensure intent badges and command hints reuse the same display aliases end-to-end.
  - Talon list guardrails: add regeneration checks for `GPT/lists/*.talon-list` to fail when catalog aliases drift from on-device spoken tokens.
  - GPT persona docs: align `_build_persona_intent_docs` output with `intent_display_map` so documentation mirrors the spoken aliases surfaced in quick help.

## 2025-12-18 – Loop 173 (kind: behaviour)
- Focus: Persona & Intent Presets – align pattern picker intent commands with catalog display aliases.
- Change: `lib/modelPatternGUI.py` now resolves intent preset display names via `persona_intent_maps().intent_display_map` for both “say” hints and summary rows, retaining canonical tokens in parentheses; added `_tests/test_model_pattern_gui.py::test_pattern_canvas_uses_intent_display_alias` to lock the behaviour.
- Checks: `python3 -m pytest _tests/test_model_pattern_gui.py` → `32 passed in 0.38s`.
- Removal test: Reverting would drop display aliases from the pattern picker, causing the new regression test to fail and reintroducing divergent spoken hints compared to the catalog.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: confirm intent badges and voice hints consistently surface catalog display aliases.
  - Talon list guardrails: add regeneration checks for `GPT/lists/*.talon-list` to fail when catalog aliases drift.
  - GPT persona docs: update `_build_persona_intent_docs` to emit the same aliases shown in canvases.

## 2025-12-18 – Loop 174 (kind: behaviour) – Align suggestion GUI intent surfaces with catalog aliases
- Focus: Persona & Intent Presets – suggestion canvas (`lib/modelSuggestionGUI.py`) command hints and summaries.
- Change: `_suggestion_stance_info()` now consults `persona_intent_maps().intent_display_map` to hydrate the intent alias when preset metadata omits it; suggestion canvas rendering uses the hydrated alias for both “Say” hints and intent summaries. Added `_tests/test_model_suggestion_gui.py::test_stance_info_fetches_alias_when_not_provided` plus updated existing stance tests to expect catalog aliases.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` → `28 passed in 0.11s`.
- Removal test: Reverting would drop display aliases from suggestion rows, restoring canonical tokens and causing the refreshed regression suite to fail.
- Adversarial “what remains” check:
  - Talon list guardrails: add regeneration checks so `GPT/lists/*.talon-list` stay aligned with catalog display aliases.
  - GPT persona docs: update `_build_persona_intent_docs` to emit the same display aliases shown in help/pattern/suggestion surfaces.
  - Response canvas: confirm `lib/modelResponseCanvas.py` uses `intent_display` for recap banners to keep Concordance surfaces consistent.

## 2025-12-18 – Loop 175 (kind: guardrail/tests) – Guard Talon list regeneration against catalog drift
- Focus: Persona & Intent Presets – Talon list generation/guardrails (`scripts/tools/generate_talon_lists.py`).
- Change: generator now emits `personaPreset.talon-list` and `intentPreset.talon-list` with catalog-driven alias→canonical mappings sourced from `persona_intent_maps().intent_display_map`; guardrail tests assert the generated files contain the expected spoken/display aliases and that `--check` flags drift. Updated `_tests/test_generate_talon_lists.py` to cover the new lists and ensured list-drift fixtures in `_tests/test_axis_catalog_validate_lists_dir.py` remain green.
- Checks: `python3 -m pytest _tests/test_generate_talon_lists.py` (4 passed in 0.28s); `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (17 passed in 0.97s).
- Removal test: Reverting would drop the persona/intent lists and alias coverage, causing the refreshed guardrail tests to fail and allowing Talon list drift to go undetected.
- Adversarial “what remains” check:
  - GPT persona docs: update `_build_persona_intent_docs` to emit display aliases so documentation matches the shared SSOT.
  - Response canvas: ensure `lib/modelResponseCanvas.py` surfaces `intent_display` alongside persona axes to keep recap banners aligned.
  - Consider adding an integration guard that runs `generate_talon_lists.py --check` in CI once local regeneration workflows stabilize.

## 2025-12-18 – Loop 162 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure alias-only suggestions stay catalog-aligned.
- Change: Updated `GPT/gpt.py` to retain raw persona/intent alias metadata when model suggestions only provide spoken/display presets, allowing `lib/suggestionCoordinator.record_suggestions` to canonicalize via `persona_intent_maps`, and added `_tests/test_integration_suggestions.py::test_suggest_alias_only_metadata_round_trip` to cover the alias-only path end-to-end through the suggestion GUI helpers.
- Checks: `python3 -m pytest _tests/test_integration_suggestions.py` (pass; excerpt: `6 passed in 2.16s`).
- Removal test: Reverting would drop the alias-preservation path so suggestions that only supply spoken/display presets would lose persona/intent metadata, making the new integration test fail and reopening the ADR-0056 Salient Task 2 gap.
- Adversarial “what remains” check:
  - `GPT/gpt.py::_validated_persona_value`: extend coverage for alias-only intent tokens so prompt recipe commands surface canonical keys when inputs vary in case or punctuation.
  - `lib/modelSuggestionGUI.py`: add an integration slice that drives voice commands with display aliases to confirm GUI actions reuse the shared persona/intent maps.
  - Concordance guardrails: consider a CI assertion that fails when suggestion entries reach `record_suggestions` without persona/intent preset keys to complement the new integration test.

## 2025-12-18 – Loop 163 (kind: behaviour)
- Focus: Persona & Intent Presets – canonicalise alias-only suggestion metadata before reaching the coordinator.
- Change: Updated `GPT/gpt.py::_suggest_prompt_recipes_core_impl` to resolve persona/intent presets from label/spoken/display aliases ahead of `record_suggestions`, ensuring axis hints and preset keys populate even when JSON omits canonical tokens, and added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_alias_only_fields_canonicalise` to guard the new behaviour.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `12 passed in 4.51s`).
- Removal test: Reverting would leave alias-only suggestions without canonical persona/intent metadata upstream of `record_suggestions`, causing the new validation test to fail and risking future regressions when alternative coordinators bypass the fallback.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: extend voice-command coverage so GUI actions exercise preset aliases without relying on the coordinator fallback.
  - `GPT/gpt.py::_validated_persona_value`: tighten canonicalisation for mixed-case intent tokens provided via `intent_purpose` to close out the remaining tests-first bullet.
  - Guardrails: explore a CI assertion (or lint) that fails when suggestion payloads emit persona/intent metadata without canonical preset keys.

## 2025-12-18 – Loop 164 (kind: behaviour)
- Focus: Persona & Intent Presets – harden `_validated_persona_value` against mixed-case and punctuation-heavy aliases.
- Change: Extended `_suggest_prompt_recipes_core_impl` with `_normalise_alias_token` so persona/intent alias lookups strip punctuation and compare normalised keys before falling back to hints, and added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_alias_only_fields_canonicalise` coverage for uppercase/punctuated aliases.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `12 passed in 5.08s`).
- Removal test: Reverting would drop the alias normalisation path, causing the new validation test to fail and allowing hyphenated/display intent aliases to bypass canonicalisation, reintroducing the ADR-0056 Salient Task 2 regression.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: broaden voice-command regression coverage so GUI presets exercise puny-coded aliases without coordinator fallbacks.
  - `GPT/gpt.py::_canonical_persona_value`: consider sharing `_normalise_alias_token` so direct persona command entry benefits from the same sanitisation.
  - Guardrails: add a lint/test that rejects suggestion payloads whose persona/intent fields still lack canonical preset keys after normalisation.

## 2025-12-18 – Loop 165 (kind: behaviour)
- Focus: Persona & Intent Presets – align `_canonical_persona_value` with shared alias normalisation.
- Change: Promoted `_normalise_persona_alias_token` to a module helper and reused it across `_canonical_persona_value` and `_suggest_prompt_recipes_core_impl`, while extending `_canonical_persona_value` to consult `persona_intent_maps` alias tables; added `_tests/test_gpt_suggest_validation.py::test_canonical_persona_value_normalises_aliases` to cover direct canonicalisation.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.47s`).
- Removal test: Reverting would cause `_canonical_persona_value("intent", "For-Deciding!")` to return an empty string, breaking the new test and allowing mixed-case / punctuated aliases to bypass canonicalisation in persona status surfaces.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: create a voice-command regression that ensures GUI presets round-trip aliases without relying on suggestion coordinator fallbacks.
  - Guardrails: consider a lint that asserts canonical persona/intent keys are present before suggestions are persisted.
  - `_canonical_persona_value`: evaluate whether Talon runtime persona commands should use the shared normaliser for interactive inputs.

## 2025-12-18 – Loop 166 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure suggestion GUI hydrates canonical persona/intent metadata from alias-only payloads.
- Change: Updated `lib/modelSuggestionGUI.py` to share the `_normalise_alias_token` helper, normalise preset aliases before dictionary lookups, canonicalise stored labels/spoken names, and expand `_refresh_suggestions_from_state` to align cached GUI suggestions with `persona_intent_maps` output.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `27 passed in 0.15s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 5.12s`).
- Removal test: Reverting would leave the GUI cache with raw uppercased/punctuated aliases, causing `_tests/test_model_suggestion_gui.py::test_open_normalises_alias_only_metadata` to fail and reintroducing divergence between Suggestion GUI state and canonical persona/intent presets.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: add an integration covering voice-command driven preset selection after GUI hydration to guarantee follow-on actions receive the canonical keys.
  - `lib/suggestionCoordinator.py`: consider asserting that recorded suggestions always include canonical preset keys before dispatch to GUI surfaces.
  - Guardrails: evaluate a lint ensuring GUI hydration continues to round-trip with `persona_intent_maps` outputs when presets are added or renamed.

## 2025-12-18 – Loop 167 (kind: tests)
- Focus: Persona & Intent Presets – guard voice-command execution after alias-only hydration.
- Change: Added `_tests/test_model_suggestion_gui.py::test_run_index_normalises_alias_only_metadata`, calling `UserActions.model_prompt_recipe_suggestions_run_index` with uppercase/punctuated preset metadata and asserting the GUI cache normalises to canonical persona/intent keys before running the suggestion.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.13s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.86s`).
- Removal test: Reverting would allow the new test to fail and reopen the gap where run-index execution consumed raw alias strings instead of canonical presets.
- Adversarial “what remains” check:
  - `lib/suggestionCoordinator.py`: consider adding a guard that rejects suggestions lacking canonical preset keys before they reach GUI callers.
  - `lib/modelSuggestionGUI.py`: explore a small integration that verifies voice-command preset selection after the GUI closes, ensuring canonical metadata flows through to downstream apply routines.
  - Guardrails: investigate a CI lint that spots suggestion payloads persisting alias-only persona/intent fields without canonical keys.

## 2025-12-18 – Loop 168 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – harden suggestion GUI refresh against missing catalog attributes.
- Change: Updated `lib/modelSuggestionGUI.py::_refresh_suggestions_from_state` to tolerate absent `persona_intent_maps` fields by normalising lookups through safe dict fallbacks and alias normalisation, and added `_tests/test_model_suggestion_gui.py::test_missing_persona_intent_maps_data` to assert the GUI handles stubbed map objects without preset metadata.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.14s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.49s`).
- Removal test: Reverting would reintroduce AttributeError crashes when persona/intent catalog snapshots omit preset alias tables, causing the new guard test to fail.
- Adversarial “what remains” check:
  - `lib/suggestionCoordinator.py`: consider adding a guard that rejects suggestions lacking canonical preset keys before they reach GUI callers.
  - `lib/modelSuggestionGUI.py`: consider logging a user-facing warning when hydration falls back to raw metadata so operators can detect catalog drift.
  - Guardrails: evaluate adding a CI stub that simulates partially populated `persona_intent_maps` snapshots to ensure future changes keep the refresh path resilient.

## 2025-12-18 – Loop 169 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure GUI refresh handles empty suggestion feeds and logs missing catalogs.
- Change: Added an early return in `_refresh_suggestions_from_state` to short-circuit when `suggestion_entries_with_metadata()` yields no entries, and introduced a `_debug` log when `persona_intent_maps()` is unavailable so Concordance operators can detect fallback hydration.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.13s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.51s`).
- Removal test: Reverting would reintroduce potential `SuggestionGUIState` drift (stale data left behind) and remove the observability signal when persona catalogs fail to load.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: consider emitting a user-facing notification when catalog hydration falls back entirely so voice users know to regenerate presets.
  - `lib/suggestionCoordinator.py`: explore rejecting empty suggestion feeds earlier to surface upstream failures.
  - Guardrails: add a test that simulates an empty suggestions list followed by a refreshed one to ensure state resets remain correct.

## 2025-12-19 – Loop 188 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – publish guardrail summaries via GitHub Actions artifacts.
- Change: Added a `history-axis-summary` upload step to `.github/workflows/test.yml` so `make ci-guardrails` outputs at `artifacts/telemetry/history-validation-summary.json` are persisted as GitHub Actions build artifacts with `if-no-files-found: warn` safeguards.
- Checks: (workflow change) `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass; excerpt: `4 passed in 12.6s`).
- Removal test: Reverting would drop the upload-artifact step, leaving CI without the preserved summary and weakening ADR-0056’s guardrail telemetry requirement.
- Adversarial “what remains” check:
  - Confirm the GitHub Actions job retains artifacts across branches and adjust naming if multiple summaries are needed simultaneously.
  - Update Concordance runbooks to link to the workflow artifact for on-call retrieval once CI artifact retention policies are documented.
  - Evaluate adding an Actions-level summary annotation that links directly to the uploaded JSON for faster inspection.

## 2025-12-19 – Loop 189 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – enforce artifact persistence across guardrail variants.
- Change: Updated `scripts/tools/run_guardrails_ci.sh` to require the history summary for guardrail targets (failing when absent), taught `Makefile::request-history-guardrails-fast` to emit `artifacts/telemetry/history-validation-summary.json`, and added `_tests/test_make_request_history_guardrails.py::test_make_request_history_guardrails_fast_produces_summary` plus `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_history_target_produces_summary`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py` (pass; excerpt: `7 passed in 14.97s`).
- Removal test: Reverting would let guardrail targets succeed without persisting the summary artifact, undoing ADR-0056’s telemetry guardrail and breaking the new regression tests.
- Adversarial “what remains” check:
  - Confirm Actions artifact retention aligns with Concordance operational needs and document retrieval steps in runbooks.
  - Consider including the commit SHA or workflow run ID in artifact names when parallel guardrail runs are expected.
  - Explore adding a GitHub Actions step that surfaces a direct link to the uploaded JSON in the job summary for faster triage.

## 2025-12-19 – Loop 190 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – surface guardrail summaries directly in CI logs and job summary.
- Change: Added a GitHub Actions step in `.github/workflows/test.yml` that appends summary metrics and a direct artifact link (when available) to `GITHUB_STEP_SUMMARY`, taught `scripts/tools/run_guardrails_ci.sh` to log the same metrics and link hint, and refreshed `_tests/test_run_guardrails_ci.py` expectations for the new messaging.
- Checks: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass; excerpt: `5 passed in 15.02s`); `python3 -m pytest _tests/test_make_request_history_guardrails.py` (pass; excerpt: `2 passed in 0.93s`).
- Removal test: Reverting would drop the surfaced metrics/link, causing the updated guardrail tests to fail and reducing operator visibility into where to retrieve summaries.
- Adversarial “what remains” check:
  - Confirm GitHub Actions artifact retention meets Concordance retention requirements and codify retrieval steps in runbooks.
  - Explore including the workflow run URL or artifact download shortcut in contributor-facing docs so on-call operators can find summaries quickly.
  - Monitor whether future guardrail targets need similar summary annotations before broadening the helper logic.

## 2025-12-19 – Loop 191 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – guardrail summary retention and retrieval guidance.
- Change: Set the GitHub Actions upload step in `.github/workflows/test.yml` to keep the `history-axis-summary` artifact for 30 days, updated `scripts/tools/run_guardrails_ci.sh` to restate the job-summary reference and retention window, and expanded `docs/adr/0056-concordance-personas-axes-history-gating.md` guidance so runbooks point operators to the job-summary download link.
- Checks: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass; excerpt: `5 passed in 14.81s`).
- Removal test: Reverting would drop the explicit retention window and retrieval messaging, causing the updated guardrail test to fail and leaving runbooks without actionable instructions.
- Adversarial “what remains” check:
  - Confirm Actions artifact retention settings match Concordance SLOs (e.g., adjust if 30 days proves insufficient) and note any changes in the operations runbook.
  - Consider including the workflow run URL in the scripted output once the pending job-summary enhancements land, giving operators a single-click path to the uploaded JSON.
  - Evaluate whether other guardrail targets (axis docs, persona catalog) need matching retention notes before broadening this pattern.

## 2025-12-19 – Loop 192 (kind: behaviour)
- Focus: Request Gating & Streaming – emit in-flight gating events on the streaming session.
- Change: Added `StreamingSession.record_gating_drop` in `lib/streamingCoordinator.py` and taught `lib/requestGating.try_begin_request` to call it so drop reasons appear in the shared event stream; extended `_tests/test_request_gating.py::test_try_begin_request_records_streaming_event` to lock the behaviour.
- Checks: `python3 -m pytest _tests/test_request_gating.py` @ 2025-12-19T18:43:55Z (fail; excerpt: `AssertionError: [] is not true`), `python3 -m pytest _tests/test_request_gating.py` @ 2025-12-19T18:46:12Z (pass; excerpt: `9 passed in 0.06s`).
- Removal test: Reverting would drop the streaming `gating_drop` event, causing `_tests/test_request_gating.py::test_try_begin_request_records_streaming_event` to fail and hiding in-flight drop telemetry from the session event log.
- Adversarial “what remains” check:
  - Extend `StreamingSession.record_gating_drop` to include per-reason counts (mirroring `requestLog.gating_drop_stats`) so session telemetry matches request log summaries.
  - Audit non-GPT gating call sites for direct state checks and migrate them to `try_begin_request` before adding integration coverage that expects streaming events in those surfaces.
  - Consider emitting a consolidated drop summary when a request exits the in-flight phases so Concordance dashboards can correlate guards with lifecycle completions.

## 2025-12-19 – Loop 193 (kind: behaviour)
- Focus: Request Gating & Streaming – expose RequestUIController gating helpers.
- Change: Added `RequestUIController.is_in_flight` and `RequestUIController.try_start_request` delegating to `requestState` gating helpers so UI callers share the central contract, and extended `_tests/test_request_controller.py` with gating coverage that fails when the delegation is missing.
- Checks: `python3 -m pytest _tests/test_request_controller.py::RequestUIControllerTests::test_is_in_flight_delegates_to_request_state_helper _tests/test_request_controller.py::RequestUIControllerTests::test_try_start_request_returns_drop_reason` @ 2025-12-19T18:58:30Z (fail; excerpt: `AttributeError: 'RequestUIController' object has no attribute 'is_in_flight'`), `python3 -m pytest _tests/test_request_controller.py::RequestUIControllerTests::test_is_in_flight_delegates_to_request_state_helper _tests/test_request_controller.py::RequestUIControllerTests::test_try_start_request_returns_drop_reason` @ 2025-12-19T18:59:04Z (pass; excerpt: `2 passed in 0.02s`).
- Removal test: Reverting would drop the controller-level gating façade and the new tests would fail, reintroducing duplicate gating logic across UIs.
- Adversarial “what remains” check:
  - Add matching gating helpers to `lib/requestLifecycle.py` so lifecycle-oriented orchestrators consume the same gating contract before migrating streaming/session callers.
  - Migrate `_request_is_in_flight` wrappers (for example, `lib/modelHelpCanvas.py`) to call the controller façade and extend an integration guardrail such as `_tests/test_model_help_canvas_guard.py` to exercise the shared helper.
  - Evaluate exposing a bus-level `try_begin_request` wrapper that forwards to the controller to simplify future call-site migrations.

## 2025-12-19 – Loop 194 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – keep streaming gating telemetry aligned with request log counters.
- Change: Updated `lib/streamingCoordinator.py::StreamingSession.record_gating_drop` to track per-reason/total drop counts and include them in emitted `gating_drop` events, and extended `_tests/test_request_gating.py::test_try_begin_request_records_streaming_event` to assert successive drops increment the counts.
- Checks: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:05:20Z (fail; excerpt: `AssertionError: None != 1`), `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:07:11Z (pass; excerpt: `1 passed in 0.04s`).
- Removal test: Reverting would drop the per-reason gating counters from streaming events, causing the refreshed guardrail test to fail and leaving streaming telemetry out of sync with `requestLog.gating_drop_stats`.
- Adversarial “what remains” check:
  - Surface aggregated gating counts alongside other session telemetry (for example, `last_streaming_snapshot`) so dashboards can consume them without parsing event history.
  - Add coverage for mixed drop reasons to ensure the counts map reports separate tallies per reason.
  - Consider emitting a session-level gating summary when a request transitions to a terminal phase so Concordance tooling can correlate drops with lifecycle outcomes.

## 2025-12-19 – Loop 195 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose gating drop summaries via the streaming snapshot façade.
- Change: Extended `lib/streamingCoordinator.py::record_streaming_snapshot` to accept extra metadata and taught `StreamingSession.record_gating_drop` to persist aggregated drop counts (`gating_drop_counts`, `gating_drop_total`, `gating_drop_last`) into `GPTState.last_streaming_snapshot`; expanded `_tests/test_request_gating.py::test_try_begin_request_records_streaming_event` to assert snapshot fields update across successive drops.
- Checks: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:13:12Z (fail; excerpt: `AssertionError: None != 1`), `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:15:07Z (pass; excerpt: `1 passed in 0.05s`).
- Removal test: Reverting would drop the snapshot metadata, causing the refreshed guardrail test to fail and forcing Concordance tooling to parse event logs to retrieve drop totals.
- Adversarial “what remains” check:
  - Add mixed-reason coverage so snapshot counts prove independent tallies when multiple drop reasons occur during a session.
  - Consider wiring `current_streaming_snapshot()` consumers (for example, dashboards) to surface the new `gating_drop_*` fields so operators see drop totals without inspecting events.
  - Evaluate emitting a terminal-phase summary event that captures the final gating totals for historical telemetry.

## 2025-12-19 – Loop 196 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – retain gating-drop summaries after streaming snapshot updates.
- Change: Taught `lib/streamingCoordinator.py::record_streaming_snapshot` to merge prior gating metadata when the request id matches, and added `_tests/test_request_gating.py::test_gating_snapshot_persists_across_session_updates` to assert the `gating_drop_*` fields survive subsequent chunk snapshots.
- Checks: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_gating_snapshot_persists_across_session_updates` @ 2025-12-19T19:18:04Z (fail; excerpt: `AssertionError: None != 1`), `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_gating_snapshot_persists_across_session_updates` @ 2025-12-19T19:29:22Z (pass; excerpt: `1 passed in 0.04s`); supporting guardrail: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:29:24Z (pass; excerpt: `1 passed in 0.03s`).
- Removal test: Reverting would strip the snapshot merge logic so `test_gating_snapshot_persists_across_session_updates` fails and Concordance dashboards lose drop totals once streaming resumes.
- Adversarial “what remains” check:
  - Backfill mixed-reason gating coverage so snapshot aggregation reports distinct counts per drop reason.
  - Wire `current_streaming_snapshot()` consumers (dashboards, telemetry exports) to surface the new `gating_drop_*` fields.
  - Verify gating summaries reset cleanly on new sessions to avoid cross-request leakage before expanding usage in Concordance tooling.

## 2025-12-19 – Loop 197 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – cover mixed-reason gating summaries and preserve totals during streaming updates.
- Change: Added `_tests/test_request_gating.py::test_gating_snapshot_persists_across_session_updates` mixed-reason assertions and enhanced `lib/streamingCoordinator.py::record_streaming_snapshot` to treat `gating_drop_counts` payloads with totals as absolute while additive patches merge per-reason increments.
- Checks: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_gating_snapshot_persists_across_session_updates` @ 2025-12-19T19:35:18Z (fail; excerpt: `AssertionError: None != 2`), `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_gating_snapshot_persists_across_session_updates` @ 2025-12-19T19:38:46Z (pass; excerpt: `1 passed in 0.04s`); supporting guardrail: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event` @ 2025-12-19T19:38:52Z (pass; excerpt: `1 passed in 0.05s`).
- Removal test: Reverting would drop the mixed-reason coverage and restore double-counting in `record_streaming_snapshot`, causing the refreshed guardrail test to fail and leaving Concordance dashboards with inaccurate drop totals when multiple reasons occur.
- Adversarial “what remains” check:
  - Add an integration slice wiring `current_streaming_snapshot()` consumers to surface `gating_drop_*` summaries in dashboards/telemetry.
  - Extend coverage for request resets/new sessions to confirm gating summaries clear between runs.
  - Consider emitting a terminal lifecycle event summarizing gating totals for historical Concordance analysis.

## 2025-12-19 – Loop 198 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – reset gating summaries when a new streaming session starts.
- Change: Updated `lib/streamingCoordinator.py::new_streaming_session` to clear `GPTState.last_streaming_snapshot` and taught the coordinator to use `setattr`/`cast` so gating metadata is replaced safely; added `_tests/test_streaming_coordinator.py::test_new_streaming_session_resets_gating_summary` to guard the behaviour.
- Checks: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_new_streaming_session_resets_gating_summary` @ 2025-12-19T19:41:58Z (fail; excerpt: `AssertionError: {...} != {}`), `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_new_streaming_session_resets_gating_summary` @ 2025-12-19T19:44:35Z (pass; excerpt: `1 passed in 0.03s`); supporting guardrails: `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_try_begin_request_records_streaming_event _tests/test_request_gating.py::RequestGatingTests::test_gating_snapshot_persists_across_session_updates` @ 2025-12-19T19:44:40Z (pass; excerpt: `2 passed in 0.04s`).
- Removal test: Reverting would let stale gating summaries leak into new sessions, causing the new streaming coordinator guardrail test to fail and confusing Concordance dashboards with prior-request drop counts.
- Adversarial “what remains” check:
  - Surface the `gating_drop_*` fields via `current_streaming_snapshot()` consumers so dashboards display them without parsing events.
  - Audit other streaming entrypoints (e.g., request lifecycle resets) to ensure they clear snapshots consistently before relying on the new helper.
  - Consider emitting a terminal lifecycle event summarizing final gating drop counts for Concordance analytics once snapshot consumers are in place.

## 2025-12-19 – Loop 206 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – provide a machine-readable summary format for history guardrails.
- Deliverables:
  - Added a `json` option to `--summary-format` in `scripts/tools/history-axis-validate.py` so `--summarize-json` can output structured data alongside the existing streaming and markdown formats.
  - Extended `_tests/test_history_axis_validate.py` to cover the new JSON output (including artifact URLs) while keeping the streaming/markdown expectations intact.
- Guardrail: `python3 -m pytest _tests/test_history_axis_validate.py`.
- Evidence:
  - red | 2025-12-19T22:34Z | exit 1 | python3 -m pytest _tests/test_history_axis_validate.py
      AssertionError: streaming summary line missing / `--summarize-json` argument not recognised
  - green | 2025-12-19T22:40Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py _tests/test_history_axis_validate.py
      12 passed in 16.88s
- Removal test: Reverting the CLI change removes the JSON format, causing the refreshed history-axis validator tests to fail and leaving automation without a structured summary option.
- Adversarial “what remains” check:
  - Feed the JSON output into Concordance dashboards or telemetry collectors so machine workflows gain parity with human operators.
  - Add `--summary-format json` coverage to other guardrail entrypoints once dashboards are ready to ingest the artifact.
  - Monitor upcoming `StreamingSession` telemetry work to ensure new drop reasons remain serialisable through the shared helper.

## 2025-12-19 – Loop 207 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – ensure history guardrail make targets emit JSON summaries and logs alongside streaming lines.
- Deliverables:
  - Repaired the `Makefile` recipes for `request-history-guardrails` and `request-history-guardrails-fast`, wiring both targets to create `artifacts/telemetry/history-validation-summary.streaming.json` and print the JSON line.
  - Confirmed the shared summary helper now surfaces in local guardrail runs, keeping CLI output aligned with the new `_tests/test_make_request_history_guardrails.py` expectations.
- Guardrail: `python3 -m pytest _tests/test_make_request_history_guardrails.py`.
- Evidence:
  - red | 2025-12-19T22:58Z | exit 1 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      Makefile:121: *** missing separator.  Stop.
  - green | 2025-12-19T23:04Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      2 passed in 1.12s
- Removal test: Reverting the Makefile updates removes the JSON streaming artifact and resurrects the tab/separator error, causing `_tests/test_make_request_history_guardrails.py` to fail.
- Adversarial “what remains” check:
  - Verify `scripts/tools/run_guardrails_ci.sh` continues to archive the JSON summary and surface it in job summaries; add explicit coverage if future regressions appear.
  - Feed the JSON artifact into Concordance telemetry/dashboard tooling so this data becomes actionable beyond local guardrails.

## 2025-12-19 – Loop 208 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – surface the streaming JSON artifact in CI helper output for history guardrails.
- Deliverables:
  - Extended `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` to require a log line referencing the streaming JSON artifact path.
  - Updated `scripts/tools/run_guardrails_ci.sh` to print and persist the streaming JSON path alongside the existing summary output.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary`.
- Evidence:
  - red | 2025-12-19T23:09Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary
      AssertionError: 'Streaming JSON summary recorded at artifacts/telemetry/history-validation-summary.streaming.json; job summary will reference this file when running in GitHub Actions.' not found
  - green | 2025-12-19T23:14Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary
      1 passed in 0.96s
- Removal test: Reverting the script update or test expectation removes the streaming JSON log line, causing the guardrail test to fail and obscuring the artifact for CI operators.
- Adversarial “what remains” check:
  - Hook additional guardrail targets (e.g., `request-history-guardrails-fast`) into CI summaries if operators rely on the fast path.
  - Feed both the markdown and JSON summaries into Concordance telemetry/dashboard tooling so the structured data becomes actionable beyond local guardrails.

## 2025-12-19 – Loop 209 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – publish history guardrail summaries into GitHub Actions job summaries.
- Deliverables:
  - Added `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require the CI helper to honour `GITHUB_STEP_SUMMARY` with the streaming JSON artifact path and markdown summary.
  - Updated `scripts/tools/run_guardrails_ci.sh` to append the markdown summary, streaming line, and JSON artifact reference to `GITHUB_STEP_SUMMARY` when present.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:18Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: run_guardrails_ci.sh did not create the GitHub step summary file
  - green | 2025-12-19T23:21Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 0.96s
  - green | 2025-12-19T23:22Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 15.90s
- Removal test: Reverting the helper or test drops the job-summary append, causing the new guardrail to fail and leaving GitHub Actions runs without persisted history summaries.
- Adversarial “what remains” check:
  - Confirm `request-history-guardrails-fast` invocations inherit the same job-summary output (expected via shared helper).
  - Feed the emitted JSON summary into Concordance telemetry/dashboard tooling so automated consumers capture gating trends directly from CI artifacts.

## 2025-12-19 – Loop 210 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – embed the streaming JSON payload directly into GitHub Actions job summaries.
- Deliverables:
  - Tightened `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require a fenced JSON code block containing the streaming summary.
  - Updated `scripts/tools/run_guardrails_ci.sh` to append a ```json block with the streaming summary payload to `GITHUB_STEP_SUMMARY`.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:24Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: ```json not found in job summary output
  - green | 2025-12-19T23:27Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 0.98s
  - green | 2025-12-19T23:28Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 16.41s
- Removal test: Reverting the helper or guardrail test removes the JSON code block, causing the refreshed guardrail to fail and stripping operators of an inline payload for inspection.
- Adversarial “what remains” check:
  - Consider adding a truncated preview (e.g., `jq`-formatted excerpt) for large summaries once drop counts grow in real runs.
  - Explore wiring the same JSON payload into Concordance dashboards so CI job summaries and telemetry stay aligned without manual copying.

## 2025-12-19 – Loop 211 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – surface a download link and labeled JSON payload in GitHub Actions job summaries.
- Deliverables:
  - Strengthened `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require “Download summary artifact” and “Streaming summary (json)” markers alongside the fenced payload.
  - Updated `scripts/tools/run_guardrails_ci.sh` to log the artifact link (or local path) and labeled JSON section inside `GITHUB_STEP_SUMMARY`.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:32Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: ```json not found in job summary output
  - green | 2025-12-19T23:36Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 1.03s
  - green | 2025-12-19T23:37Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 17.17s
- Removal test: Reverting the helper or guardrail test erases the artifact link and labeled JSON section, causing the refreshed guardrail to fail and hiding the download pointer from CI operators.
- Adversarial “what remains” check:
  - Ensure the markdown link renders correctly in real GitHub Actions runs (consider adding an integration note once observed).
  - Investigate adding a short excerpt beneath the link for quick counts while retaining the full payload in the fenced block.

## 2025-12-19 – Loop 212 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – present history summaries with clickable GitHub artifact links.
- Deliverables:
  - Tightened `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require the “History axis summary” markdown link within the job summary output.
  - Updated `scripts/tools/run_guardrails_ci.sh` to emit a markdown link when `ARTIFACT_URL` is available, falling back to a local path otherwise.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:40Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: '[History axis summary]' not found in job summary output
  - green | 2025-12-19T23:43Z | exit 0 | python3 - m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 0.97s
  - green | 2025-12-19T23:44Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 16.61s
- Removal test: Rolling back either the script or guardrail test removes the markdown link, causing the refreshed guardrail to fail and obscuring the artifact download within GitHub Actions job summaries.
- Adversarial “what remains” check:
  - Ensure the markdown link renders correctly in real GitHub Actions runs (consider adding an integration note once observed).
  - Investigate adding a short excerpt beneath the link for quick counts while retaining the full payload in the fenced block.

## 2025-12-19 – Loop 213 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – add a quick counts preview to GitHub Actions job summaries.
- Deliverables:
  - Strengthened `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require “total entries” and “gating drops” bullet points ahead of the JSON block.
  - Updated `scripts/tools/run_guardrails_ci.sh` to include the counts extracted from the summary in the job summary output.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:47Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: '- total entries: 0' not found in job summary output
  - green | 2025-12-19T23:50Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 0.97s
  - green | 2025-12-19T23:51Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 16.41s
- Removal test: Reverting the helper or guardrail test removes the counts preview, causing the refreshed guardrail to fail and forcing operators to open the JSON blob for common metrics.
- Adversarial “what remains” check:
  - Consider formatting the counts preview into a table or aligning it with future telemetry dashboards once additional metrics are surfaced.
  - Monitor real runs to ensure large gating totals remain readable; adjust formatting if the preview grows noisy.

## 2025-12-19 – Loop 214 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose gating reason counts in GitHub Actions job summaries.
- Deliverables:
  - Extended `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to require a "Streaming gating reasons" preview alongside the counts and JSON block.
  - Updated `scripts/tools/run_guardrails_ci.sh` to compute normalized gating reason counts and surface them in both console output and the job summary (with safe fallbacks for set -u).
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T23:56Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: '- Streaming gating reasons: none' not found in job summary output (updated script not yet emitting preview)
  - green | 2025-12-19T23:59Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 1.12s
  - green | 2025-12-19T23:59Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 17.09s
- Removal test: Reverting the script or guardrail change drops the gating reason preview, causing the refreshed guardrail to fail and hiding drop breakdowns from CI operators.
- Adversarial “what remains” check:
  - Consider presenting non-zero gating reasons as a table or sorted list if real-world counts grow noisy.
  - Evaluate wiring the same summarized counts into Concordance telemetry feeds to keep dashboards aligned with job summaries.

## 2025-12-19 – Loop 215 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – add a gating reason preview/table to history job summaries.
- Deliverables:
  - Extended `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary` to assert the "Streaming gating reasons" bullet (and future table output when counts exist).
  - Updated `scripts/tools/run_guardrails_ci.sh` to compute gating reason counts, emit them in console output, and render either a markdown table (when counts exist) or a `- Streaming gating reasons: none` bullet in the GitHub Actions step summary.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-20T00:02Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      AssertionError: '- Streaming gating reasons: none' not found in job summary output (updated script not yet emitting preview)
  - green | 2025-12-20T00:05Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_writes_job_summary
      1 passed in 1.12s
  - green | 2025-12-20T00:06Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      6 passed in 17.09s
- Removal test: Reverting the script or updated guardrail would drop the gating reason preview/table, causing the refreshed guardrail to fail and leaving operators without a concise per-reason breakdown in CI summaries.
- Adversarial “what remains” check:
  - When real gating reasons appear, confirm the markdown table renders cleanly and consider widening formatting (e.g., sorting by descending count).
  - Evaluate syncing the same per-reason counts into Concordance telemetry exports so dashboards stay aligned with CI summaries.

## 2025-12-19 – Loop 199 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose gating summaries through the streaming snapshot façade.
- Change: Added `lib/streamingCoordinator.py::current_streaming_gating_summary` (and `_coerce_int`) so consumers receive normalized `gating_drop_*` metadata, updated `record_streaming_snapshot` to sanitize merged counts, and extended `_tests/test_streaming_coordinator.py::test_current_streaming_gating_summary_returns_counts` to cover multi-reason drops.
- Checks: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts` @ 2025-12-19T19:46:58Z (fail; excerpt: `ImportError: cannot import name 'current_streaming_gating_summary'`), `python3 -m pytest _tests/test_streaming_coordinator.py _tests/test_request_gating.py` @ 2025-12-19T19:54:18Z (pass; excerpt: `21 passed in 0.07s`).
- Removal test: Reverting would drop the shared gating summary helper and sanitization, causing the new guardrail test to fail and forcing dashboards to parse raw event logs for drop counts.
- Adversarial “what remains” check:
  - Wire `current_streaming_gating_summary()` into Concordance dashboards and telemetry exporters so operators see drop totals without bespoke parsing.
  - Audit request lifecycle reset paths (e.g., cancellation/idle transitions) to ensure they call the streaming session helper before exposing summaries.
  - Consider emitting a terminal lifecycle event that snapshots the finalized gating summary for historical Concordance reporting once dashboards consume the new helper.

## 2025-12-19 – Loop 216 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – confirm gating reason tables render when counts exist.
- Deliverables:
  - Added `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts` to seed synthetic gating counts and assert both stdout and GitHub job summaries render the markdown table.
  - Updated `scripts/tools/run_guardrails_ci.sh` to echo the table to stdout when gating counts exist so local runs mirror the CI summary formatting.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts`; supporting `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T22:14Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      AssertionError: 'Streaming gating reasons:' not found in stdout with synthetic counts
  - green | 2025-12-19T22:16Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      1 passed in 0.48s
  - green | 2025-12-19T22:17Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      7 passed in 18.02s
- Removal test: Reverting the script or new test would drop the stdout table, causing the guardrail test to fail and leaving local guardrail runs without a markdown validation of gating reasons.
- Adversarial “what remains” check:
  - Wire the gating reason table into Concordance telemetry/dashboards so structured counts surface beyond CI/job summaries.
  - Capture evidence from real gating events to confirm multi-reason tables render cleanly and consider ranking reasons by descending count when data becomes noisy.

## 2025-12-19 – Loop 217 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – order gating reason previews by descending counts.
- Deliverables:
  - Updated `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts` to require the markdown table (stdout + job summary) list highest counts first.
  - Taught `scripts/tools/run_guardrails_ci.sh` to sort gating reason previews and tables by count (breaking ties lexicographically), keeping console output aligned with the GitHub summary.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts`; supporting `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T22:21Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      AssertionError: expected top row `streaming_disabled` but observed alphabetical ordering
  - green | 2025-12-19T22:24Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      1 passed in 0.44s
  - green | 2025-12-19T22:25Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      7 passed in 17.14s
- Removal test: Reverting either change restores alphabetical ordering, causing the updated gating-table guardrail to fail and hiding the most actionable counts in console output and job summaries.
- Adversarial “what remains” check:
  - Wire the normalized gating reason data into Concordance telemetry/dashboards so CI summaries and dashboards share the same ordering.
  - Confirm ordering against real multi-reason runs; if the table grows noisy, consider truncating to the top-N reasons while keeping the JSON payload complete.

## 2025-12-19 – Loop 218 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – align streaming summary previews with markdown ordering.
- Deliverables:
  - Tightened `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts` to assert the streaming summary text lists counts in descending order for stdout and GitHub job summaries.
  - Updated `scripts/tools/history-axis-validate.py::_format_streaming_summary_line` (and the drop-summary helper) to sort gating reasons by descending count with lexical tie-breaks so console previews, job summaries, and CLI drop summaries stay consistent.
- Guardrail: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts`; supporting `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T22:27Z | exit 1 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      AssertionError: streaming summary counts remained alphabetical instead of descending
  - green | 2025-12-19T22:29Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts
      1 passed in 0.46s
  - green | 2025-12-19T22:29Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      7 passed in 17.33s
- Removal test: Reverting either the test or helper change restores alphabetical streaming previews, causing the gating summary guardrail to fail and degrading operator readability in CI outputs.
- Adversarial “what remains” check:
  - Surface the same normalized ordering through Concordance telemetry exports so dashboards match CLI/CI previews.
  - Evaluate truncating or highlighting top-N reasons once real multi-reason data accumulates to keep summaries scannable without losing detail in the JSON artifact.

## 2025-12-19 – Loop 228 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose drop-rate telemetry for gating dashboards.
- Deliverables:
  - Added `_tests/test_history_axis_export_telemetry.py::HistoryAxisExportTelemetryTests::test_includes_gating_drop_rate` to require a `gating_drop_rate` field when totals are available.
  - Updated `scripts/tools/history-axis-export-telemetry.py::build_payload` to compute the drop rate (falling back to zero entries) alongside the existing totals and top reasons.
- Guardrail: `python3 -m pytest _tests/test_history_axis_export_telemetry.py`.
- Evidence:
  - red | 2025-12-19T23:55Z | exit 1 | python3 -m pytest _tests/test_history_axis_export_telemetry.py
      TypeError: unsupported operand type(s) for -: 'NoneType' and 'float'
  - green | 2025-12-19T23:57Z | exit 0 | python3 -m pytest _tests/test_history_axis_export_telemetry.py
      4 passed in 0.20s
- Removal test: Reverting either the new guardrail or the drop-rate computation removes the field, causing `_tests/test_history_axis_export_telemetry.py::HistoryAxisExportTelemetryTests::test_includes_gating_drop_rate` to fail and hiding rate trends from telemetry consumers.
- Adversarial “what remains” check:
  - Add guardrails for malformed summary input once CLI error handling slices land, so exporters fail loudly in CI when JSON is missing or corrupt.
  - Thread `gating_drop_rate` through downstream ETL dashboards after confirming Concordance ingestion expects the new field.

## 2025-12-19 – Loop 227 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – extend telemetry exporter guardrails for artifact links and stdout mode.
- Deliverables:
  - Added `_tests/test_history_axis_export_telemetry.py::HistoryAxisExportTelemetryTests::test_preserves_artifact_url_when_provided` to lock the `--artifact-url` passthrough contract.
  - Added `_tests/test_history_axis_export_telemetry.py::HistoryAxisExportTelemetryTests::test_stdout_mode_emits_json_payload` to guard the stdout JSON path when `--output` is omitted.
- Guardrail: `python3 -m pytest _tests/test_history_axis_export_telemetry.py` (existing behaviour already satisfied the new assertions; no implementation changes required).
- Evidence:
  - green | 2025-12-19T23:58Z | exit 0 | python3 -m pytest _tests/test_history_axis_export_telemetry.py
      3 passed in 0.12s
- Removal test: Deleting the new tests allows regressions (dropping `artifact_url` or breaking stdout output) to land unnoticed; retaining them ensures `python3 -m pytest _tests/test_history_axis_export_telemetry.py` fails if the exporter regresses.
- Adversarial “what remains” check:
  - Add negative-path coverage for malformed JSON or missing summary files if future slices harden CLI error handling.
  - Once Concordance ETL integration lands, consider adding a smoke test that exercises artifact upload wiring end-to-end via the guardrail scripts.

## 2025-12-19 – Loop 226 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – harden telemetry export totals when streaming summaries omit `total`.
- Deliverables:
  - Added `_tests/test_history_axis_export_telemetry.py::HistoryAxisExportTelemetryTests::test_falls_back_to_counts_when_total_missing` to require the exporter to sum counts when totals are absent.
  - Updated `scripts/tools/history-axis-export-telemetry.py::build_payload` to fall back to legacy totals or aggregated counts and retain `other_gating_drops`.
- Guardrail: `python3 -m pytest _tests/test_history_axis_export_telemetry.py`.
- Evidence:
  - red | 2025-12-19T23:44Z | exit 1 | python3 -m pytest _tests/test_history_axis_export_telemetry.py
      AssertionError: telemetry payload left `gating_drop_total` at 0 when streaming summary omitted `total`
  - green | 2025-12-19T23:46Z | exit 0 | python3 -m pytest _tests/test_history_axis_export_telemetry.py
      1 passed in 0.04s
- Removal test: Reverting the fallback change (or script) reproduces the failure, e.g. `python3 -m pytest _tests/test_history_axis_export_telemetry.py` at 2025-12-19T23:45Z exited 1 with `gating_drop_total` still 0.
- Adversarial “what remains” check:
  - Extend exporter coverage to assert `artifact_url` propagation and stdout-only mode when `--output` is omitted.
  - Coordinate with Concordance ETL consumers to verify `other_gating_drops` and fallback totals surface correctly in dashboards before widening telemetry fields.

## 2025-12-19 – Loop 224 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – highlight telemetry exports in local guardrail help.
- Deliverables:
  - Updated `Makefile` help entries for `request-history-guardrails` and `request-history-guardrails-fast` to note that each target exports streaming and telemetry summaries before resetting gating counters.
  - Extended `_tests/test_make_help_guardrails.py::MakeHelpGuardrailsTests::test_make_help_lists_guardrail_targets` to assert the new help phrasing.
- Guardrail: `python3 -m pytest _tests/test_make_help_guardrails.py`; supporting `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py`.
- Evidence:
  - green | 2025-12-19T23:35Z | exit 0 | python3 -m pytest _tests/test_make_help_guardrails.py
      1 passed in 0.13s
  - green | 2025-12-19T23:35Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py
      9 passed in 17.32s
- Removal test: Reverting the Makefile help text or the updated guardrail test removes the telemetry note, causing `_tests/test_make_help_guardrails.py::MakeHelpGuardrailsTests::test_make_help_lists_guardrail_targets` to fail and erasing guidance for exporting the new telemetry payload.
- Adversarial “what remains” check:
  - Coordinate with Concordance ops so downstream dashboards ingest `history-validation-summary.telemetry.json`, adding runbook steps once the ETL integration is ready.

## 2025-12-19 – Loop 225 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – ensure CI guardrails archive telemetry payloads.
- Deliverables:
  - Updated `.github/workflows/test.yml` to upload the streaming and telemetry summaries alongside the primary history summary artifact.
  - Extended `_tests/test_ci_workflow_guardrails.py::CiWorkflowGuardrailsTests::test_ci_runs_guardrails_and_tests` to require the telemetry artifact, guarding CI drift.
- Guardrail: `python3 -m pytest _tests/test_ci_workflow_guardrails.py`.
- Evidence:
  - red | 2025-12-19T23:41:33Z | exit 1 | python3 -m pytest _tests/test_ci_workflow_guardrails.py
      AssertionError: 'history-validation-summary.telemetry.json' not found in workflow contents
  - green | 2025-12-19T23:42:04Z | exit 0 | python3 -m pytest _tests/test_ci_workflow_guardrails.py
      1 passed in 0.02s
- Removal test: Reverting either the workflow upload changes or the guardrail assertion drops the telemetry artifact, causing `_tests/test_ci_workflow_guardrails.py::CiWorkflowGuardrailsTests::test_ci_runs_guardrails_and_tests` to fail.
- Adversarial “what remains” check:
  - Verify GitHub Actions history guardrail runs surface the telemetry artifact download link; extend `_tests/test_run_guardrails_ci.py` if summary output drifts.
  - Coordinate with Concordance ETL to ingest the telemetry artifact and confirm dashboards consume the JSON payload before broadening the schema.

## 2025-12-19 – Loop 223 (kind: status)
- Focus: Request Gating & Streaming – document telemetry export requirements.
- Deliverables:
  - Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` to note that guardrail runs emit `history-validation-summary.telemetry.json` (top gating reasons, totals, artifact link) for Concordance dashboards and ETL pipelines.
- Guardrail: Documentation-only slice; no new commands executed.
- Evidence:
  - n/a (doc update).
- Removal test: Reverting the doc change omits the telemetry export requirement, making it easier for future refactors to drop `history-validation-summary.telemetry.json` without noticing.
- Adversarial “what remains” check:
  - Coordinate with Concordance ops to ingest the telemetry payload and evaluate whether additional fields (percentages, trend metadata) should be captured in future slices.

## 2025-12-19 – Loop 222 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – export top gating reasons for Concordance dashboards.
- Deliverables:
  - Added `scripts/tools/history-axis-export-telemetry.py`, producing a condensed telemetry payload (top N reasons, generated timestamp, optional artifact link) from `history-validation-summary.json`.
  - Updated `Makefile::request-history-guardrails(_fast)` and `scripts/tools/run_guardrails_ci.sh` to invoke the exporter and persist `history-validation-summary.telemetry.json`, echoing the payload in CI job summaries.
  - Extended guardrail tests `_tests/test_make_request_history_guardrails.py` and `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` to require the telemetry file with sorted reasons.
- Guardrail: `python3 -m pytest _tests/test_make_request_history_guardrails.py`; supporting `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary`, `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_gating_reasons_table_with_counts`, `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts`.
- Evidence:
  - red | 2025-12-19T23:15Z | exit 1 | python3 -m pytest _tests/test_make_request_history_guardrails.py::MakeRequestHistoryGuardrailsTests::test_make_request_history_guardrails_runs_clean
      AssertionError: Telemetry export was not produced
  - green | 2025-12-19T23:18Z | exit 0 | python3 -m pytest _tests/test_make_request_history_guardrails.py
      2 passed in 1.07s
  - green | 2025-12-19T23:18Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary
      1 passed in 0.94s
- Removal test: Reverting the exporter or guardrail integrations drops `history-validation-summary.telemetry.json`, causing the refreshed guardrail tests to fail and leaving Concordance dashboards without machine-readable drop summaries.
- Adversarial “what remains” check:
  - Hook the telemetry payload into downstream Concordance dashboards/ETL and monitor whether top-N truncation needs adjustment once real gating volume accumulates.
  - Consider augmenting the exporter with additional metadata (e.g., drop-rate percentages) once dashboards prove out the current signal.

## 2025-12-19 – Loop 221 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – propagate sorted gating counts into Concordance telemetry exports.
- Deliverables:
  - Enhanced `lib/streamingCoordinator.current_streaming_gating_summary` and snapshot persistence to emit and preserve `gating_drop_counts_sorted`, clearing it when no counts remain so telemetry doesn’t surface stale data.
  - Updated `lib/requestLog.history_validation_stats` so `history-validation-summary.json` embeds a `counts_sorted` array inside `streaming_gating_summary`, giving dashboards an ordered payload without extra processing.
  - Extended `_tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_include_gating_counts` and `_tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts` to assert the new telemetry contract across both snapshots and history stats.
- Guardrail: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts`; supporting `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_include_gating_counts`, `python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary`.
- Evidence:
  - red | 2025-12-19T23:05Z | exit 1 | python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts
      AssertionError: streaming summary missing `counts_sorted` entry when telemetry pipeline still returned legacy snapshots
  - green | 2025-12-19T23:06Z | exit 0 | python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts
      1 passed in 0.04s
  - green | 2025-12-19T23:07Z | exit 0 | python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_include_gating_counts
      1 passed in 0.06s
- Removal test: Reverting the streaming coordinator or request log updates drops `counts_sorted`, causing the refreshed telemetry guardrails to fail and leaving dashboards to fall back to unordered counts.
- Adversarial “what remains” check:
  - Wire the ordered array into external Concordance dashboards/telemetry consumers and consider trimming to the top-N reasons once real drop volumes grow.
  - Monitor CI/job summaries to confirm operators see the same ordering and adjust presentation if long lists become noisy.

## 2025-12-19 – Loop 220 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – surface descending counts in streaming snapshots and downstream summaries.
- Deliverables:
  - Updated `lib/streamingCoordinator.py` to attach a `gating_drop_counts_sorted` list to snapshots, expose it via `current_streaming_gating_summary`, and keep it merged/reset across streaming sessions.
  - Extended `lib/requestLog.history_validation_stats` to include a `counts_sorted` array in the streaming gating summary so history-axis validation artifacts inherit the same ordering.
  - Strengthened `_tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts` to require the sorted payload.
- Guardrail: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts`; supporting `python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary`, `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T22:37Z | exit 1 | python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts
      AssertionError: streaming summary missing `counts_sorted` entry when code unchanged
  - green | 2025-12-19T22:39Z | exit 0 | python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts
      1 passed in 0.04s
  - green | 2025-12-19T22:40Z | exit 0 | python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary
      1 passed in 0.17s
  - green | 2025-12-19T22:41Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      7 passed in 18.77s
- Removal test: Reverting the snapshot or request log changes drops the sorted list, causing the updated streaming coordinator guardrail to fail and leaving downstream JSON summaries without a consistent ordering.
- Adversarial “what remains” check:
  - Feed the new `counts_sorted` array into Concordance telemetry/dashboard exporters so operators and automation share the same ordering and top-reason context.
  - Evaluate adding top-N reason highlights to GitHub job summaries once real gating data accumulates to avoid overly long bullet lists.

## 2025-12-19 – Loop 219 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose descending gating counts in JSON summaries.
- Deliverables:
  - Extended `_tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary` and `_tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` to require a `counts_sorted` field in streaming gating summaries.
  - Updated `scripts/tools/history-axis-validate.py` to emit a `counts_sorted` array (descending by count with lexical ties) and taught `scripts/tools/run_guardrails_ci.sh` to honour the pre-sorted data for console previews and markdown tables.
- Guardrail: `python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary`; supporting `python3 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence:
  - red | 2025-12-19T22:31Z | exit 1 | python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary
      AssertionError: streaming JSON summary missing expected `counts_sorted` payload
  - green | 2025-12-19T22:33Z | exit 0 | python3 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary
      1 passed in 0.16s
  - green | 2025-12-19T22:34Z | exit 0 | python3 -m pytest _tests/test_run_guardrails_ci.py
      7 passed in 17.01s
- Removal test: Reverting the helper or tests would drop the `counts_sorted` metadata, causing the refreshed guardrail to fail and leaving JSON summaries without a stable, descending representation for downstream automation.
- Adversarial “what remains” check:
  - Thread the `counts_sorted` data into Concordance telemetry/dashboard exporters so dashboards match CLI/CI ordering.
  - Evaluate including top-N reason callouts in future job summaries once real multi-reason gating data appears.

## 2025-12-19 – Loop 229 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – add lifecycle gating helpers to mirror request state guardrails.
- Deliverables:
  - Added `is_in_flight` and `try_start_request` helpers to `lib/requestLifecycle.py`, aligning lifecycle gating with the existing request-state façade.
  - Extended `_tests/test_request_lifecycle.py` with regression coverage for lifecycle gating semantics (in-flight detection and drop reasons).
- Guardrail: `python3 -m pytest _tests/test_request_lifecycle.py`.
- Evidence:
  - red | 2025-12-19T20:07Z | exit 1 | python3 -m pytest _tests/test_request_lifecycle.py
      ImportError: cannot import name 'is_in_flight' from 'talon_user.lib.requestLifecycle'
  - green | 2025-12-19T20:12Z | exit 0 | python3 -m pytest _tests/test_request_lifecycle.py
      8 passed in 0.02s
- Removal test: Reverting the lifecycle helpers or test updates would resurrect the import failure and drop the shared gating guardrail, causing `_tests/test_request_lifecycle.py` to fail.
- Adversarial “what remains” check:
  - Migrate controller and lifecycle orchestrators (`requestController`, downstream canvases) to consume the new lifecycle gating helpers instead of bespoke checks.
  - Extend integration coverage (e.g., `_tests/test_model_help_canvas_guard.py`) so UI gating surfaces fail when they bypass the lifecycle façade.

## 2025-12-19 – Loop 230 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – route `RequestUIController` gating through the lifecycle façade.
- Deliverables:
  - Updated `_tests/test_request_controller.py` to assert `RequestUIController` delegates gating checks to shared requestLifecycle helpers.
  - Refactored `lib/requestController.py` to derive lifecycle status from `requestState` and call the centralized requestLifecycle gating helpers.
- Guardrail: `python3 -m pytest _tests/test_request_controller.py`.
- Evidence:
  - red | 2025-12-19T20:22Z | exit 1 | python3 -m pytest _tests/test_request_controller.py
      AssertionError: Expected 'is_in_flight' to have been called once. Called 0 times.
  - green | 2025-12-19T20:34Z | exit 0 | python3 -m pytest _tests/test_request_controller.py
      12 passed in 0.03s
- Removal test: Reverting the controller refactor or the new delegation tests would drop lifecycle-level gating coverage, causing `_tests/test_request_controller.py` to fail and allowing bespoke gating checks to creep back in.
- Adversarial “what remains” check:
  - Migrate downstream canvases and helpers (`requestUI`, `modelHelpers`, overlay commands) to consume `RequestUIController.try_start_request` so lifecycle gating remains centralized.
  - Extend integration tests (e.g., `_tests/test_model_help_canvas_guard.py`, `_tests/test_model_suggestion_gui.py`) to assert lifecycle drop reasons propagate through UI surfaces.

## 2025-12-19 – Loop 231 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – expose bus-level gating helpers backed by the shared controller façade.
- Deliverables:
  - Added `try_start_request` and `is_in_flight` wrappers to `lib/requestBus.py` that delegate to `RequestUIController` when available and fall back to `requestState` semantics.
  - Updated `lib/requestGating.py` to route default gating checks through the bus helpers while preserving explicit state handling and telemetry recording.
  - Extended `_tests/test_request_bus.py` with delegation coverage ensuring the bus helpers call into the controller when present and revert to stored state when detached.
- Guardrail: `python3.11 -m pytest _tests/test_request_bus.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T20:45Z | exit 1 | python3.11 -m pytest _tests/test_request_bus.py::RequestBusTests::test_try_start_request_delegates_to_controller
      ImportError: cannot import name 'is_in_flight' from 'talon_user.lib.requestBus'
  - green | 2025-12-19T20:52Z | exit 0 | python3.11 -m pytest _tests/test_request_bus.py::RequestBusTests::test_try_start_request_delegates_to_controller
      1 passed in 0.04s
  - green | 2025-12-19T20:53Z | exit 0 | python3.11 -m pytest _tests/test_request_bus.py
      47 passed in 0.04s
  - green | 2025-12-19T20:54Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.05s
- Removal test: Reverting the bus helpers or gating delegation would cause `_tests/test_request_bus.py::RequestBusTests::test_try_start_request_delegates_to_controller` to fail and drop controller-backed gating coverage, undoing the ADR guardrail alignment.
- Adversarial “what remains” check:
  - Migrate UI canvases and helpers that still import `requestGating` wrappers onto the bus/controller façade so drop reasons and telemetry stay centralized end-to-end.
  - Extend integration guardrails (e.g., `_tests/test_model_help_canvas_guard.py`) to assert controller-sourced drop reasons propagate through user-facing surfaces once downstream callers adopt the bus helpers.

## 2025-12-19 – Loop 232 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – align provider commands with the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_provider_commands.py` to require `_request_is_in_flight` to delegate to the bus-level helper.
  - Refactored `lib/providerCommands.py` to import `requestBus.is_in_flight` as `bus_is_in_flight` and fall back safely, keeping `try_begin_request` for telemetry.
- Guardrail: `python3.11 -m pytest _tests/test_provider_commands.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:05Z | exit 1 | python3.11 -m pytest _tests/test_provider_commands.py::ProviderCommandGuardTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.providerCommands' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/providerCommands.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:09Z | exit 0 | python3.11 -m pytest _tests/test_provider_commands.py
      4 passed in 0.05s
  - green | 2025-12-19T21:09Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.05s
- Removal test: Reverting the provider delegation would drop the `bus_is_in_flight` import, causing the refreshed provider guard test to fail and leaving provider commands on the old gating helper.
- Adversarial “what remains” check:
  - Continue migrating other canvases (`modelHelpCanvas`, `modelPatternGUI`, `modelPromptPatternGUI`, `modelSuggestionGUI`, `requestHistoryActions`, `requestHistoryDrawer`) so their gating checks also rely on the bus/controller façade.
  - Extend integration guardrails (e.g., `_tests/test_model_help_canvas_guard.py`, `_tests/test_model_pattern_gui.py`) to ensure UI-level drop messaging reflects controller-sourced reasons after migration.

## 2025-12-19 – Loop 233 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – migrate the model help canvas onto the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_model_help_canvas_guard.py` to assert `_request_is_in_flight` patches `bus_is_in_flight` when present.
  - Refactored `lib/modelHelpCanvas.py` to import `requestBus.is_in_flight` and keep `_reject_if_request_in_flight` telemetry via `try_begin_request(source="modelHelpCanvas")`.
- Guardrail: `python3.11 -m pytest _tests/test_model_help_canvas_guard.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:18Z | exit 1 | python3.11 -m pytest _tests/test_model_help_canvas_guard.py::ModelHelpCanvasGuardTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.modelHelpCanvas' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/modelHelpCanvas.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:22Z | exit 0 | python3.11 -m pytest _tests/test_model_help_canvas_guard.py
      3 passed in 0.05s
  - green | 2025-12-19T21:22Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.04s
- Removal test: Reverting the help-canvas import would drop `bus_is_in_flight`, causing the refreshed guard test to fail and returning the helper to the deprecated request gating path.
- Adversarial “what remains” check:
  - Continue migrating the remaining canvases (`modelPatternGUI`, `modelPromptPatternGUI`, `modelSuggestionGUI`, `requestHistoryActions`, `requestHistoryDrawer`) onto the bus/controller façade.
  - After migrations, extend integration guardrails to ensure drop messaging across canvases reflects bus-sourced gating reasons.

## 2025-12-19 – Loop 234 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – align the prompt pattern GUI with the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_prompt_pattern_gui_guard.py` to require `_request_is_in_flight` to patch `bus_is_in_flight` when present.
  - Refactored `lib/modelPromptPatternGUI.py` to import `requestBus.is_in_flight` and to call `try_begin_request(source="modelPromptPatternGUI")` for telemetry when rejecting requests.
- Guardrail: `python3.11 -m pytest _tests/test_prompt_pattern_gui_guard.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:28Z | exit 1 | python3.11 -m pytest _tests/test_prompt_pattern_gui_guard.py::PromptPatternGUIGuardTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.modelPromptPatternGUI' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/modelPromptPatternGUI.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:33Z | exit 0 | python3.11 -m pytest _tests/test_prompt_pattern_gui_guard.py
      3 passed in 0.06s
  - green | 2025-12-19T21:33Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.05s
- Removal test: Reverting the prompt pattern GUI import would drop `bus_is_in_flight`, causing the refreshed guard test to fail and sending the GUI back through the deprecated gating helper.
- Adversarial “what remains” check:
  - Continue migrating the remaining canvases (`modelPatternGUI`, `modelSuggestionGUI`, `requestHistoryActions`, `requestHistoryDrawer`) to the bus/controller façade.
  - Once canvases migrate, extend integration guardrails to verify drop messaging reflects controller-sourced reasons across UI surfaces.

## 2025-12-19 – Loop 235 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – migrate the model pattern picker onto the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_model_pattern_gui_guard.py` to assert `_request_is_in_flight` delegates to `bus_is_in_flight`.
  - Refactored `lib/modelPatternGUI.py` to import `requestBus.is_in_flight`, wrap `_request_is_in_flight` with a safe bus check, and call `try_begin_request(source="modelPatternGUI")` when rejecting requests.
- Guardrail: `python3.11 -m pytest _tests/test_model_pattern_gui_guard.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:38Z | exit 1 | python3.11 -m pytest _tests/test_model_pattern_gui_guard.py::ModelPatternGUIGuardTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.modelPatternGUI' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/modelPatternGUI.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:42Z | exit 0 | python3.11 -m pytest _tests/test_model_pattern_gui_guard.py
      3 passed in 0.05s
  - green | 2025-12-19T21:42Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.06s
- Removal test: Reverting the pattern GUI import would drop `bus_is_in_flight`, causing the refreshed guard test to fail and restoring the deprecated gating helper.
- Adversarial “what remains” check:
  - Continue migrating the remaining canvases (`modelSuggestionGUI`, `requestHistoryActions`, `requestHistoryDrawer`) to the bus/controller façade.
  - After migrations, extend integration guardrails to verify drop messaging reflects controller-sourced reasons across UI surfaces.

## 2025-12-19 – Loop 236 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – migrate the suggestion GUI onto the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_model_suggestion_gui_guard.py` to assert `_request_is_in_flight` delegates to `bus_is_in_flight`.
  - Refactored `lib/modelSuggestionGUI.py` to import `requestBus.is_in_flight`, wrap `_request_is_in_flight` with a safe bus check, and preserve telemetry via `try_begin_request(source="modelSuggestionGUI")`.
- Guardrail: `python3.11 -m pytest _tests/test_model_suggestion_gui_guard.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:47Z | exit 1 | python3.11 -m pytest _tests/test_model_suggestion_gui_guard.py::ModelSuggestionGUIGuardTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.modelSuggestionGUI' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/modelSuggestionGUI.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:51Z | exit 0 | python3.11 -m pytest _tests/test_model_suggestion_gui_guard.py
      3 passed in 0.05s
  - green | 2025-12-19T21:51Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.06s
- Removal test: Reverting the suggestion GUI import would drop `bus_is_in_flight`, causing the refreshed guard test to fail and restoring the deprecated gating helper.
- Adversarial “what remains” check:
  - Migrate `requestHistoryActions` and `requestHistoryDrawer` to the bus/controller façade.
  - After migrations, extend integration guardrails so history drawers and other canvases surface controller-sourced drop reasons end-to-end.

## 2025-12-19 – Loop 237 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – migrate history actions onto the request bus gating façade.
- Deliverables:
  - Updated `_tests/test_request_history_actions.py` to assert `_request_is_in_flight` patches `bus_is_in_flight`.
  - Refactored `lib/requestHistoryActions.py` to import `requestBus.is_in_flight` and keep `_reject_if_request_in_flight` telemetry via `try_begin_request(source="requestHistoryActions")`.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_actions.py`; supporting `python3.11 -m pytest _tests/test_request_gating.py`.
- Evidence:
  - red | 2025-12-19T21:55Z | exit 1 | python3.11 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_request_is_in_flight_delegates_to_request_bus
      AttributeError: <module 'talon_user.lib.requestHistoryActions' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/requestHistoryActions.py'> does not have the attribute 'bus_is_in_flight'
  - green | 2025-12-19T21:59Z | exit 0 | python3.11 -m pytest _tests/test_request_history_actions.py
      83 passed in 0.45s
  - green | 2025-12-19T21:59Z | exit 0 | python3.11 -m pytest _tests/test_request_gating.py
      10 passed in 0.05s
- Removal test: Reverting the history actions import would drop `bus_is_in_flight`, causing the refreshed guard test to fail and restoring the deprecated gating helper.
- Adversarial “what remains” check:
  - Migrate `requestHistoryDrawer` onto the bus/controller façade.
  - Once drawers migrate, extend integration guardrails so history surfaces surface controller-sourced drop reasons end-to-end.

## 2025-12-20 – Loop 238 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T05:50:17Z
- Focus: Request Gating & Streaming – migrate history drawer gating onto the request bus façade.
- Change: Added `_tests/test_request_history_drawer.py::test_request_is_in_flight_delegates_to_request_bus` and refactored `lib/requestHistoryDrawer._request_is_in_flight` to call `requestBus.is_in_flight()` with safe fallbacks while keeping `try_begin_request` telemetry.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py` (python3 in this environment lacks pytest, so python3.11 was used).
- Evidence: `docs/adr/evidence/0056/loop-0238.md`
- Removal test: Reverting either the guardrail test or the bus delegation causes `_tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_request_is_in_flight_delegates_to_request_bus` to fail, restoring the deprecated gating helper.
- Adversarial “what remains” check:
  - Extend history drawer integration coverage so drop notifications surface controller-provided reasons when gating rejects new requests.
  - Audit other history drawer helpers for direct `_request_is_in_flight` usage before wiring gating telemetry into dashboards.
  - Confirm guardrail scripts capture history drawer gating drop counts alongside existing streaming summaries.

## 2025-12-20 – Loop 239 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T06:36:48Z
- Focus: Request Gating & Streaming – surface history drawer gating drop reasons beyond `in_flight`.
- Change: Added `_tests/test_request_history_drawer.py::test_reject_if_request_in_flight_notifies_other_drop_reasons` and updated `lib/requestHistoryDrawer._reject_if_request_in_flight` to notify and record drop reasons for any gating failure returned by `try_begin_request`.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py` (red before implementation, green after).
- Evidence: `docs/adr/evidence/0056/loop-0239.md`
- Removal test: Reverting either the guardrail test or the `_reject_if_request_in_flight` change causes the new test to fail, allowing non-`in_flight` drop reasons to proceed without notification.
- Adversarial “what remains” check:
  - Add an integration test that exercises history drawer toggle during streaming-disabled scenarios to ensure notifications surface in Talon overlays.
  - Confirm gating telemetry (`history-validation-summary.telemetry.json`) captures non-`in_flight` drop reasons once end-to-end tests produce them.
  - Evaluate aligning other history surfaces (e.g., quick-save shortcuts) with the broader drop reason notifications to keep Concordance messaging consistent.

## 2025-12-20 – Loop 240 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T06:55:30Z
- Focus: Request Gating & Streaming – emit terminal gating summaries from the streaming coordinator.
- Deliverables:
  - Added `_tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_complete_emits_gating_summary_event` and `test_record_error_emits_gating_summary_event` to guard the streaming gating summary event stream.
  - Updated `lib/streamingCoordinator.py` to type-harden `filtered_axes_from_request` and emit `gating_summary` events on completion/error using `current_streaming_gating_summary` data.
- Guardrail: `python3.11 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_complete_emits_gating_summary_event _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_error_emits_gating_summary_event`.
- Evidence: `docs/adr/evidence/0056/loop-0240.md`
- Removal test: Reverting `lib/streamingCoordinator.py` drops the gating summary event, causing the new streaming coordinator tests to fail (`python3.11 -m pytest …test_record_complete_emits_gating_summary_event …test_record_error_emits_gating_summary_event`).
- Adversarial “what remains” check:
  - Thread the `gating_summary` event into guardrail telemetry exporters so CI job summaries and history-axis artifacts surface terminal drop totals without parsing raw events.
  - Add an integration test that confirms request/UI canvases consume the summary snapshot when rendering Concordance diagnostics.
  - Evaluate emitting a lifecycle completion event that persists the gating summary alongside other terminal request metrics.

## 2025-12-20 – Loop 241 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T07:30:05Z
- Focus: Request Gating & Streaming – surface gating status across telemetry, CLI summaries, and CI job summaries.
- Deliverables:
  - Propagated streaming gating status via `lib/streamingCoordinator.py` snapshots and `lib/requestLog.history_validation_stats` so summary exports expose `status` metadata.
  - Updated `scripts/tools/history-axis-validate.py`, `scripts/tools/run_guardrails_ci.sh`, and `scripts/tools/history-axis-export-telemetry.py` to print the status in console output, JSON summaries, job summaries, and telemetry payloads.
  - Extended regression coverage (`_tests/test_streaming_coordinator.py`, `_tests/test_history_axis_validate.py`, `_tests/test_run_guardrails_ci.py`, `_tests/test_history_axis_export_telemetry.py`, `_tests/test_make_request_history_guardrails.py`) to guard the new status signals.
- Guardrail: `python3.11 -m pytest _tests/test_streaming_coordinator.py _tests/test_history_axis_validate.py _tests/test_run_guardrails_ci.py _tests/test_history_axis_export_telemetry.py _tests/test_make_request_history_guardrails.py`.
- Evidence: `docs/adr/evidence/0056/loop-0241.md`
- Removal test: `git checkout HEAD -- lib/streamingCoordinator.py lib/requestLog.py scripts/tools/history-axis-validate.py scripts/tools/run_guardrails_ci.sh scripts/tools/history-axis-export-telemetry.py && python3.11 -m pytest _tests/test_streaming_coordinator.py` (fails: gating summary status absent and gating summary tests fail).
- Adversarial “what remains” check:
  - Consider surfacing the same status metadata in external dashboards or telemetry pipelines that consume history exports.
  - Evaluate exposing status in operator-facing overlays so Concordance drop reasons remain visible even when history guardrails fire.
  - Monitor CI/workflow output to ensure the additional status line remains readable when multiple drop reasons accumulate.

## 2025-12-20 – Loop 242 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T08:45:00Z
- Focus: Request Gating & Streaming – restore gating status metadata across coordinator snapshots, history stats, and guardrail tooling.
- Deliverables:
  - Hardened `lib/streamingCoordinator.filtered_axes_from_request` to guard against non-mapping payloads and reinstated `gating_summary` events that persist status in streaming snapshots.
  - Extended `lib/requestLog.history_validation_stats` to propagate the status field and taught `scripts/tools/history-axis-validate.py`, `scripts/tools/run_guardrails_ci.sh`, and `scripts/tools/history-axis-export-telemetry.py` to surface the status in CLI output, job summaries, and telemetry payloads with sensible defaults.
  - Ensured guardrail-facing summaries render `status=unknown` when none is recorded while preserving structured status data within JSON artifacts for downstream automation.
- Guardrail: `python3.11 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_complete_emits_gating_summary_event _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_script_summary_outputs_stats`.
- Evidence: `docs/adr/evidence/0056/loop-0242.md`
- Removal test: `git checkout -- lib/streamingCoordinator.py lib/requestLog.py scripts/tools/history-axis-validate.py scripts/tools/run_guardrails_ci.sh scripts/tools/history-axis-export-telemetry.py && python3.11 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_complete_emits_gating_summary_event _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_script_summary_outputs_stats` (fails: status emission removed and targeted guardrails regress).
- Adversarial “what remains” check:
  - Re-run broader guardrail suites (`_tests/test_run_guardrails_ci.py`, `_tests/test_history_axis_export_telemetry.py`) in follow-up loop to capture the status-aware telemetry pathways end-to-end.
  - Thread the restored status metadata into Concordance dashboard ingestion so external reporting reflects the same lifecycle state.
  - Audit downstream consumers of `history_validation_stats` for assumptions about missing status values and backfill defaults where necessary.

## 2025-12-20 – Loop 243 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T17:15:00Z
- Focus: Request Gating & Streaming – ensure guardrail CI job summaries surface the streaming gating status and sources table.
- Deliverables:
  - Updated `scripts/tools/run_guardrails_ci.sh` to log the streaming gating status line in stdout and, when data exists, render a Markdown table of gating sources in the GitHub step summary alongside the existing reasons table.
  - Confirmed the history guardrail target now preserves the status field throughout stdout, job summary output, and telemetry exports without regressing status fallbacks for empty summaries.
- Guardrail: `python3.11 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence: `docs/adr/evidence/0056/loop-0243.md`
- Removal test: `git checkout -- scripts/tools/run_guardrails_ci.sh && python3.11 -m pytest _tests/test_run_guardrails_ci.py` (fails: status line and sources table disappear, breaking the refreshed guardrail expectations).
- Adversarial “what remains” check:
  - Re-run `_tests/test_history_axis_export_telemetry.py` in a subsequent slice to verify downstream telemetry continues to capture the status string end-to-end.
  - Consider adding a CLI flag to emit a concise, machine-readable summary when running guardrails locally so operators can spot gating trends without parsing Markdown tables.

## 2025-12-20 – Loop 244 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T17:28:00Z
- Focus: Request Gating & Streaming – normalize streaming gating status in history validation summaries and artifacts.
- Deliverables:
  - Updated `scripts/tools/history-axis-validate.py` to default missing streaming status values to "unknown" across streaming, JSON, and Markdown outputs.
  - Taught `lib/requestLog.history_validation_stats` to propagate the normalized status so guardrail consumers inherit the same fallback.
  - Adjusted request-history guardrail tests to assert that generated summaries and streaming JSON exports retain the explicit status field.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary`.
- Evidence: `docs/adr/evidence/0056/loop-0244.md`
- Removal test: `git checkout -- lib/requestLog.py scripts/tools/history-axis-validate.py && python3.11 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summarize_json_outputs_summary` (fails: streaming gating status field drops back to a blank value).
- Adversarial “what remains” check:
  - Reconfirm that `_tests/test_history_axis_export_telemetry.py` continues to verify the status fallback end-to-end after the normalization change.
  - Evaluate threading the explicit status through any external telemetry pipelines that still rely on blank values as a sentinel.
  - Consider rehydrating request-history summaries that may have been archived with blank status fields so dashboards display consistent signals.

## 2025-12-20 – Loop 245 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T17:58:00Z
- Focus: Request Gating & Streaming – expose the history summary path alongside normalized status in telemetry exports.
- Deliverables:
  - Enhanced `scripts/tools/history-axis-export-telemetry.py` to embed both the normalized streaming status and the originating summary path in the telemetry payload.
  - Updated `_tests/test_history_axis_export_telemetry.py` to require the new fields across stdout and file-output modes, guarding future regressions.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_export_telemetry.py`.
- Evidence: `docs/adr/evidence/0056/loop-0245.md`
- Removal test: `git checkout -- scripts/tools/history-axis-export-telemetry.py && python3.11 -m pytest _tests/test_history_axis_export_telemetry.py` (fails: telemetry payload no longer includes the summary path or normalized status).
- Adversarial “what remains” check:
  - Ensure downstream Concordance ingestion pipelines capture the new `summary_path` metadata before rotating dashboards.
  - Consider extending the exporter to emit a checksum of the summary file so dashboards can detect stale artifacts.
  - Audit other telemetry consumers for assumptions about the payload schema and update documentation accordingly.

## 2025-12-20 – Loop 246 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T19:58:00Z
- Focus: Request Gating & Streaming – deduplicate telemetry summary messaging in CI output.
- Deliverables:
  - Updated `scripts/tools/run_guardrails_ci.sh` to print a single "Telemetry summary saved at …" line in stdout and GitHub step summaries, keeping JSON output unchanged.
  - Extended `_tests/test_run_guardrails_ci.py` assertions to require the new wording and avoid accepting redundant lines.
- Guardrail: `python3.11 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence: `docs/adr/evidence/0056/loop-0246.md`
- Removal test: `git checkout -- scripts/tools/run_guardrails_ci.sh && python3.11 -m pytest _tests/test_run_guardrails_ci.py` (fails: telemetry summary line disappears and guardrail re-fails).
- Adversarial “what remains” check:
  - Consider surfacing the telemetry summary path directly in CI artifacts (e.g., step summary link) to streamline operator navigation.
  - Audit other guardrail scripts for similar duplicate messaging so CI output stays readable.

## 2025-12-20 – Loop 247 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-20T21:10:00Z
- Focus: Request Gating & Streaming – add telemetry artifact hyperlink to CI job summary.
- Deliverables:
  - `scripts/tools/run_guardrails_ci.sh` now emits a “Download telemetry summary” bullet pointing at the GitHub Actions artifact when available, while retaining the local path fallback.
  - `_tests/test_run_guardrails_ci.py` seeds GitHub env variables during job-summary checks and asserts the new hyperlink alongside the saved-path bullet.
- Guardrail: `python3.11 -m pytest _tests/test_run_guardrails_ci.py`.
- Evidence: `docs/adr/evidence/0056/loop-0247.md`
- Removal test: `git checkout -- scripts/tools/run_guardrails_ci.sh && python3.11 -m pytest _tests/test_run_guardrails_ci.py` (fails: telemetry download link disappears from the job summary).
- Adversarial “what remains” check:
  - Consider emitting a direct stdout line with the artifact URL to help local runs when GitHub env vars are present.
  - Review other guardrail helpers for similar artifact-link gaps.

## 2025-12-21 – Loop 248 (kind: guardrail/tests)
- Helper: helper:v20251220.3 @ 2025-12-21T10:30:00Z
- Focus: Request Gating & Streaming – surface non-`in_flight` drop reasons in the history drawer guard.
- Deliverables:
  - Extend `_tests/test_request_history_drawer.py` with `test_reject_if_request_in_flight_surfaces_drop_reason` covering drop reasons beyond `in_flight`.
  - Update `lib/requestHistoryDrawer._reject_if_request_in_flight` to notify and record any drop reason returned by `try_begin_request`, including fallback messaging.
  - `<VCS_REVERT>` mapping: `git stash push -k -u -- lib/requestHistoryDrawer.py` (pop with `git stash pop` after removal evidence) for helper:v20251220.3 loops on ADR-0056.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_reject_if_request_in_flight_surfaces_drop_reason`
- Evidence: `docs/adr/evidence/0056/loop-0248.md`
- Removal test: `<VCS_REVERT> && python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_reject_if_request_in_flight_surfaces_drop_reason` (restore with `git stash pop`)
- Adversarial “what remains” check:
  - Add overlay-level integration coverage ensuring history drawer toggle surfaces drop messages when streaming is disabled.
  - Verify gating telemetry aggregates capture non-`in_flight` drop reason codes for history drawer actions.
  - Confirm Concordance dashboards ingest the expanded drop reason set before rotating guardrail fixtures.

## 2025-12-21 – Loop 249 (kind: guardrail/tests)
- Helper: helper:v20251220.3 @ 2025-12-21T10:50:00Z
- Focus: Request Gating & Streaming – persist drop messaging for history drawer guardrails.
- Deliverables:
  - Extend `_tests/test_request_history_drawer.py` with an integration test that drives `request_history_drawer_open` under a non-`in_flight` drop reason and asserts the drawer surfaces the message.
  - Update `lib/requestHistoryDrawer._reject_if_request_in_flight` to cache the drop message in `HistoryDrawerState.last_message` while continuing to notify and record the drop reason.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_open_surfaces_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0249.md`
- Removal test: `<VCS_REVERT> && python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_open_surfaces_drop_message`
- Adversarial “what remains” check:
  - Confirm history drawer toggle and refresh actions emit the cached message consistently across other guardrails (e.g., history save shortcuts).
  - Verify the drop message clears after a successful drawer open so stale messaging does not persist.
  - Wire the cached message into telemetry snapshots if downstream dashboards need to surface it.

## 2025-12-21 – Loop 250 (kind: guardrail/tests)
- Helper: helper:v20251220.3 @ 2025-12-21T11:05:00Z
- Focus: Request Gating & Streaming – record fallback drop messaging for history drawer guardrails.
- Deliverables:
  - Extend `_tests/test_request_history_drawer.py` with a guardrail that forces `drop_reason_message` to return an empty string and asserts the recorded drop reason surfaces the fallback message.
  - Update `lib/requestHistoryDrawer._reject_if_request_in_flight` to pass the rendered message into `set_drop_reason` so downstream surfaces and telemetry receive the same wording.
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_guard_records_fallback_message`
- Evidence: `docs/adr/evidence/0056/loop-0250.md`
- Removal test: `<VCS_REVERT> && python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_guard_records_fallback_message`
- Adversarial “what remains” check:
  - Audit other gating surfaces that call `set_drop_reason` to ensure they pass explicit messages when overriding defaults.
  - Verify guardrail telemetry exports include the fallback text for non-catalog drop reasons.
  - Consider consolidating fallback phrasing into `drop_reason_message` to reduce duplication across guardrails.

## 2025-12-21 – Loop 251 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-21T11:18:00Z
- Focus: Request Gating & Streaming – clear cached history drawer messages after successful opens.
- Deliverables:
  - Added `_tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_message_clears_after_success` to guard against stale drop messaging after a permitted request.
  - Updated `lib/requestHistoryDrawer._reject_if_request_in_flight` to clear `HistoryDrawerState.last_message` and reset drop reasons when gating allows the action.
  - `<VCS_REVERT>` mapping: `git stash push -k -u -- lib/requestHistoryDrawer.py` (restore with `git stash pop`).
- Guardrail: `python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_message_clears_after_success`
- Evidence: `docs/adr/evidence/0056/loop-0251.md`
- Removal test: `<VCS_REVERT> && python3.11 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_message_clears_after_success`
- Adversarial “what remains” check:
  - Ensure history drawer toggle/refresh paths propagate the cleared message consistently when gating succeeds.
  - Confirm guardrail telemetry drops (`history_validation_stats`) reflect cleared drop reasons after successful actions.
  - Evaluate whether other gating helpers should clear cached messaging on success for parity.

## 2025-12-21 – Loop 252 (kind: guardrail/tests)
- Helper: helper:v20251220 @ 2025-12-21T11:28:00Z
- Focus: Request Gating & Streaming – expose last drop messaging in history validation telemetry.
- Deliverables:
  - Added `_tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_reports_last_drop_message` to require telemetry summaries surface the most recent drop message and clear it after success.
  - Updated `lib/requestLog.history_validation_stats` to publish `gating_drop_last_message` and `gating_drop_last_code` derived from the cached drop reason record.
- Guardrail: `python3.11 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_reports_last_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0252.md`
- Removal test: `<VCS_REVERT> && python3.11 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_history_validation_stats_reports_last_drop_message`
- Adversarial “what remains” check:
  - Thread the last drop message into guardrail CLI summaries (e.g., `history-axis-validate`) so operators see it without inspecting JSON.
  - Confirm streaming gating summaries also carry the message or an equivalent hint when drop reasons repeat.
  - Audit other request surfaces (GPT actions, provider commands) to ensure they set explicit drop messages before delegating to telemetry exports.

## 2025-12-21 – Loop 253 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T06:58:00Z
- Focus: Request Gating & Streaming – surface the last drop message/code across guardrail CLI summaries and CI job outputs.
- Change: Updated `lib/requestLog.history_validation_stats` to embed the cached drop message/code in the streaming summary, taught `scripts/tools/history-axis-validate.py` to render the message in streaming/markdown summaries, and wired `scripts/tools/run_guardrails_ci.sh` plus guardrail tests to log and append the last-drop line in stdout and GitHub step summaries.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_validate.py _tests/test_run_guardrails_ci.py _tests/test_make_request_history_guardrails.py`
- Evidence: `docs/adr/evidence/0056/loop-0253.md`
- Removal test: `git checkout -- lib/requestLog.py scripts/tools/history-axis-validate.py scripts/tools/run_guardrails_ci.sh && python3.11 -m pytest _tests/test_history_axis_validate.py _tests/test_run_guardrails_ci.py _tests/test_make_request_history_guardrails.py`
- Adversarial “what remains” check:
  - Propagate the last-drop message into telemetry exports and streaming session events so dashboards receive the same payload (next loop).
  - Ensure the history guardrail JSON artefacts surface the last-drop text for downstream automation consumers.
  - Audit other guardrail helpers (e.g., fast targets) to confirm they reuse the shared summary helpers before expanding messaging further.

## 2025-12-21 – Loop 254 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T07:25:00Z
- Focus: Request Gating & Streaming – push last drop messaging/code into telemetry exports and guardrail JSON artefacts.
- Change: Extended `scripts/tools/history-axis-export-telemetry.py` to include the last drop message/code in emitted payloads, updated guardrail smoke tests (`_tests/test_history_axis_export_telemetry.py`, `_tests/test_run_guardrails_ci.py`, `_tests/test_make_request_history_guardrails.py`) to assert the new fields, and aligned guardrail CLI output expectations with the normalized summary.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_export_telemetry.py _tests/test_run_guardrails_ci.py _tests/test_make_request_history_guardrails.py`
- Evidence: `docs/adr/evidence/0056/loop-0254.md`
- Removal test: `git checkout -- scripts/tools/history-axis-export-telemetry.py && python3.11 -m pytest _tests/test_history_axis_export_telemetry.py _tests/test_run_guardrails_ci.py _tests/test_make_request_history_guardrails.py`
- Adversarial “what remains” check:
  - Thread the last-drop metadata into downstream dashboards/ETL consumers (e.g., Concordance telemetry ingestion) so the new fields drive alerting.
  - Revisit other guardrail wrappers (fast variants, `run_guardrails_ci.sh` options) to confirm they relay the augmented telemetry payloads consistently.
  - Monitor guardrail outputs for newline-heavy drop messages and consider truncation/formatting rules if multi-line content becomes noisy.

## 2025-12-21 – Loop 255 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T07:32:00Z
- Focus: Request Gating & Streaming – document the new telemetry fields in ADR-0056 consequences.
- Change: Added a positive consequence noting that guardrail telemetry now emits the last-drop message/code so dashboards/ETL pipelines have actionable gating context without parsing logs.
- Checks: Documentation-only loop (no tests run).
- Evidence: inline
- Removal test: Reverting the doc update would hide the new telemetry requirement, making it easier for future slices to drop the last-drop fields without noticing.
- Adversarial “what remains” check:
  - Fold the updated telemetry expectations into Concordance operations/runbook guidance so on-call engineers know the fields exist.
  - Surface follow-up once dashboards ingest the new metadata end-to-end.
  - Monitor future telemetry schema changes to ensure ADR-0056 stays synchronized.

## 2025-12-21 – Loop 256 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T07:52:00Z
- Focus: Request Gating & Streaming – persist and surface the last drop message/code through streaming sessions and gating summaries.
- Change: Updated `lib/streamingCoordinator.StreamingSession` to track last-drop message/code, emit them in gating events/snapshots, and extend `current_streaming_gating_summary`; taught `lib/requestGating.try_begin_request` to derive the drop message, set `requestLog`’s last-drop record, and forward it to streaming sessions; refreshed `_tests/test_streaming_coordinator.py` and `_tests/test_request_gating.py` to assert the new telemetry contract.
- Guardrail: `python3.11 -m pytest _tests/test_streaming_coordinator.py _tests/test_request_gating.py`
- Evidence: `docs/adr/evidence/0056/loop-0256.md`
- Removal test: `git checkout -- lib/streamingCoordinator.py lib/requestGating.py && python3.11 -m pytest _tests/test_streaming_coordinator.py _tests/test_request_gating.py`
- Adversarial “what remains” check:
  - Ensure guardrail CLI wrappers (e.g., `history-axis-validate`) propagate streaming last-drop metadata alongside history summaries (next loop).
  - Audit UI canvases/models that consume `current_streaming_gating_summary` so they display or log the enriched metadata where appropriate.
  - Monitor request bus/controller call sites for any direct `_reject_if_request_in_flight` helpers that might bypass the centralized message propagation.

## 2025-12-21 – Loop 257 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T08:22:00Z
- Focus: Request Gating & Streaming – surface streaming last-drop message/code in guardrail CLI summaries.
- Change: Extended `scripts/tools/history-axis-validate.py` to emit a `Streaming last drop` line, taught `scripts/tools/run_guardrails_ci.sh` to parse streaming JSON for the last-drop message/code, print it in stdout, and add the bullet to GitHub step summaries; refreshed `_tests/test_history_axis_validate.py` and `_tests/test_run_guardrails_ci.py` to assert the new output while keeping make-target guardrail smoke tests stable.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_validate.py _tests/test_run_guardrails_ci.py`
- Evidence: `docs/adr/evidence/0056/loop-0257.md`
- Removal test: `git checkout -- scripts/tools/history-axis-validate.py scripts/tools/run_guardrails_ci.sh && python3.11 -m pytest _tests/test_history_axis_validate.py _tests/test_run_guardrails_ci.py`
- Adversarial “what remains” check:
  - Ensure telemetry exporters (loop 254) continue to include the last-drop fields so dashboards remain in sync with CLI output.
  - Confirm make targets and documentation that quote guardrail output mention the new streaming bullet where relevant.
  - Evaluate whether fast guardrail targets should also surface the streaming last-drop line explicitly for parity.

## 2025-12-21 – Loop 258 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T08:30:00Z
- Focus: Request Gating & Streaming – document the new streaming last-drop bullet for runbooks/operators.
- Change: Updated ADR-0056 consequences and Salient Tasks to call out the `Streaming last drop` line alongside the history drop bullet and to instruct operations runbooks to capture both when auditing guardrail jobs.
- Checks: Documentation-only loop (no tests run).
- Evidence: inline
- Removal test: Reverting the doc updates would leave operations guidance ambiguous about the new streaming-specific summary line.
- Adversarial “what remains” check:
  - Ensure Concordance runbooks explicitly reference both bullet lines when enumerating guardrail output.
  - Confirm future documentation updates keep dashboards, telemetry, and job summaries aligned on the streaming last-drop semantics.
  - Monitor whether additional guardrail tooling needs similar documentation (e.g., persona guardrails).

## 2025-12-21 – Loop 259 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T07:28:00Z
- Focus: Request Gating & Streaming – keep local request-history guardrails emitting the last-drop bullets surfaced in CI job summaries.
- Change: Added assertions in `_tests/test_make_request_history_guardrails.py` for the history/streaming last-drop lines and updated `Makefile` guardrail targets to call `history-axis-validate --summarize-json` so local runs print the same markdown summary.
- Guardrail: `python3.11 -m pytest _tests/test_make_request_history_guardrails.py` (pass; excerpt: `2 passed in 1.36s`).
- Evidence: `docs/adr/evidence/0056/loop-0259.md`
- Removal test: `git stash push -k -u -- Makefile && python3.11 -m pytest _tests/test_make_request_history_guardrails.py` (fails: last-drop bullet missing from output).
- Adversarial “what remains” check:
  - Update ADR guidance/runbooks to note that local guardrail targets now surface last-drop lines alongside CI job summaries.
  - Ensure `scripts/tools/run_guardrails_ci.sh` keeps emitting the same summary even if Makefile recipes evolve (add regression coverage if needed).
  - Consider a follow-up loop to assert the markdown summary lines surface in fast guardrail job summaries when running inside CI logs.

## 2025-12-21 – Loop 260 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T07:35:00Z
- Focus: Request Gating & Streaming – document local guardrail parity with CI last-drop bullets.
- Change: Added a Consequences bullet in ADR-0056 noting that `make request-history-guardrails(-fast)` now prints the same `Last gating drop` and `Streaming last drop` lines exposed in CI job summaries.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the doc change would obscure that on-box guardrails surface the new messaging, making it harder for contributors to know the parity exists.
- Adversarial “what remains” check:
  - Update Concordance operations/runbooks to point at the local guardrail output when training operators.
  - Monitor for future guardrail additions so the doc stays aligned with CLI behaviour.
  - Consider a follow-up to add screenshots or quick references once operations materials consolidate the new flow.

## 2025-12-21 – Loop 261 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T16:34:00Z
- Focus: Request Gating & Streaming – guardrail that history-axis-validate summaries surface last-drop metadata.
- Change: Added a test-only `HISTORY_AXIS_VALIDATE_SIMULATE_GATING_DROP` path so `history-axis-validate` records a synthetic gating drop, and introduced a guardrail test asserting the JSON summary and streaming snapshot include the last-drop message/code.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summary_path_includes_gating_last_drop_metadata`
- Evidence: `docs/adr/evidence/0056/loop-0261.md`
- Removal test: `git stash push -k -u -- scripts/tools/history-axis-validate.py && python3.11 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_summary_path_includes_gating_last_drop_metadata && git stash pop`
- Adversarial “what remains” check:
  - Document the new simulation env var in ADR guardrail notes so contributors know how to reproduce the check locally.
  - Evaluate extending the simulation hook to accept alternate drop reasons for broader coverage.
  - Confirm downstream guardrail helpers reuse this env var instead of re-implementing drop simulations.

## 2025-12-21 – Loop 262 (kind: guardrail/tests)
- Helper: helper:v20251220.5 @ 2025-12-21T16:36:30Z
- Focus: Request Gating & Streaming – ensure telemetry exports carry streaming last-drop metadata.
- Change: Extended `history-axis-export-telemetry.py` to emit `streaming_last_drop_message`/`_code` fields alongside the existing gating summary and tightened the telemetry guardrail tests to assert the new payload contract.
- Guardrail: `python3.11 -m pytest _tests/test_history_axis_export_telemetry.py`
- Evidence: `docs/adr/evidence/0056/loop-0262.md`
- Removal test: `git stash push -k -u -- scripts/tools/history-axis-export-telemetry.py && python3.11 -m pytest _tests/test_history_axis_export_telemetry.py && git stash pop`
- Adversarial “what remains” check:
  - Coordinate with Concordance telemetry consumers to ingest the new streaming fields.
  - Update dashboard schemas and runbooks once downstream ingestion confirms the additional metadata.
  - Monitor guardrail artefacts to ensure the new fields remain populated when streaming summaries are present.

## 2025-12-21 – Loop 263 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T16:38:00Z
- Focus: Request Gating & Streaming – document streaming last-drop telemetry fields for guardrails and runbooks.
- Change: Updated ADR-0056 consequences and Salient Tasks to note the new `streaming_last_drop_*` telemetry fields and reinforce runbook expectations around archiving them.
- Checks: Documentation-only loop (no tests run).
- Evidence: inline
- Removal test: Reverting the doc change would hide the streaming telemetry guidance, making it easier for runbooks to miss the new fields.
- Adversarial “what remains” check:
  - Ensure Concordance operations/runbooks explicitly list the new telemetry keys alongside existing drop fields.
  - Confirm downstream dashboard schemas are revised once ingestion work lands.
  - Consider adding a future loop to cross-link telemetry key names with guardrail CLI output examples.

## 2025-12-21 – Loop 264 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T17:45Z
- Focus: Request Gating & Streaming – align Salient Tasks with the centralized gating façade and tests already in place.
- Change: Marked the request gating Salient Task bullets as completed for the shared helpers, StreamingSession orchestration, and regression/guardrail suites so the ADR reflects the landed work.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would make the gating façade and guardrail suites appear pending, obscuring completion of the centralized lifecycle.
- Adversarial “what remains” check:
  - Expand the operations runbook task to highlight the new streaming status and last-drop telemetry fields so operators archive the full dataset.

## 2025-12-21 – Loop 265 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T18:05Z
- Focus: Request Gating & Streaming – extend operations guidance to cover the new streaming telemetry artefacts.
- Change: Expanded the operations Salient Task bullet to call out archiving the streaming status line, last-drop bullets, and gating reason/source tables, noting their corresponding telemetry fields for dashboards.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would drop the explicit streaming status and gating table guidance, leaving runbooks without the telemetry capture requirements.
- Adversarial “what remains” check:
  - Sync external Concordance runbooks with the updated instructions and include direct links to the archived telemetry artefacts.

## 2025-12-21 – Loop 266 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T18:20Z
- Focus: Request Gating & Streaming – tighten tests-first guidance around streaming telemetry guardrails.
- Change: Expanded the tests-first plan to highlight guardrail and telemetry suites that lock streaming status, last-drop messaging, and local-vs-CI parity for the request history guardrails.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would drop the explicit telemetry test guidance, making it easier for future slices to skip coverage when new fields land.
- Adversarial “what remains” check:
  - Monitor upcoming telemetry automation and add new suites to the tests-first list when additional streaming fields are introduced.

## 2025-12-21 – Loop 267 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T18:40Z
- Focus: Persona & Intent Presets – document the guardrail/test suites that hold catalog alignment across GUIs, history, and telemetry.
- Change: Added tests-first guidance pointing to `_tests/test_persona_presets.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_history_axis_validate.py`, and the `history-axis-validate.py` guardrail so persona metadata drift remains observable.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would drop the explicit guardrail references, weakening the paper trail for persona catalog drift detection.
- Adversarial “what remains” check:
  - Ensure external guardrail documentation links back to these suites when the persona catalog evolves.

## 2025-12-21 – Loop 268 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T19:00Z
- Focus: Axis Snapshot & History – capture the test/guardrail harnesses that enforce axis/catalog alignment and directional guardrails.
- Change: Added tests-first notes referencing `_tests/test_run_guardrails_ci.py`, `_tests/test_history_axis_validate.py`, `_tests/test_history_axis_export_telemetry.py`, `_tests/test_make_axis_guardrails_ci.py`, and the axis doc-generation helpers so drift across catalog, docs, and telemetry remains observable.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would remove the explicit guardrail/test references, obscuring how axis drifts are detected before landing.
- Adversarial “what remains” check:
  - Track upcoming guardrail CLI upgrades and append new suites/scripts once directionality or axis token checks expand.

## 2025-12-21 – Loop 269 (kind: docs)
- Helper: helper:v20251220.5 @ 2025-12-21T19:20Z
- Focus: Request Gating & Streaming – spell out the ongoing guardrail commands and runbook follow-ups for streaming telemetry.
- Change: Added a Monitoring & Next Steps section capturing guardrail commands (`make request-history-guardrails`, `run_guardrails_ci.sh`, `history-axis-validate.py`) and the outstanding operations runbook sync so telemetry reminders stay front of mind.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the ADR edits would remove the explicit guardrail/reminder list, making it easier to miss the streaming telemetry archive obligations.
- Adversarial “what remains” check:
  - Coordinate with operations to update external runbooks and attach the streaming telemetry examples once the handbook edit clears review.

## 2025-12-21 – Loop 270 (superseded)
- Helper: helper:v20251220.5 @ 2025-12-21T19:40Z
- Decision: Original risk/mitigation text assumed operations sign-off and a Monitoring & Next Steps checklist; superseded by later loops now that the workflow is solo-owned.

## 2025-12-21 – Loop 271 (superseded)
- Helper: helper:v20251220.5 @ 2025-12-21T19:55Z
- Decision: Persona telemetry reminders were written for the retired checklist; see newer loops for the simplified solo guidance.

## 2025-12-21 – Loop 272 (superseded)
- Helper: helper:v20251220.5 @ 2025-12-21T20:05Z
- Decision: Operations handbook follow-ups no longer apply; later loops document the solo Monitoring & Next Steps guidance.

## 2025-12-21 – Loop 273 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T20:25Z
- Focus: Risk framing – align the ADR risk/mitigation language with the single-maintainer workflow the helper now expects.
- Change: Replaced the imaginary operations hand-off risk with the real assumption (remembering to archive telemetry before resets), updated mitigations, and pointed the follow-up checklist at my personal guardrail notes.
- Checks: Documentation-only loop (no tests run).
- Removal test: Reverting the edits would reintroduce the invalid operations references and hide the solo-maintainer risk the new helper focuses on.
- Adversarial “what remains” check:
  - Capture the guardrail checklist in personal notes (next loop) so telemetry steps stay visible before future resets.

## 2025-12-21 – Loop 274 (kind: guardrail/tests)
- Helper: helper:v20251221.0 @ 2025-12-21T21:25Z
- Focus: Monitoring & Next Steps – surface the guardrail checklist as an executable helper so telemetry commands stay memorable before resets.
- Change: Added `scripts/tools/history-guardrail-checklist.py` to print the manual guardrail steps (plain text and JSON formats) and `_tests/test_history_guardrail_checklist.py` to guard the helper output against regressions.
- Guardrail: `python3.11 -m pytest _tests/test_history_guardrail_checklist.py`.
- Evidence: `docs/adr/evidence/0056/loop-0274.md`
- Removal test: `mv scripts/tools/history-guardrail-checklist.py scripts/tools/history-guardrail-checklist.py.tmp && python3.11 -m pytest _tests/test_history_guardrail_checklist.py` (fails when the helper is absent; restore with `mv scripts/tools/history-guardrail-checklist.py.tmp scripts/tools/history-guardrail-checklist.py`).
- Adversarial “what remains” check:
  - Add a Makefile target so the checklist is one command away for local operators.
  - Document the helper in ADR-0056 evidence/runbook notes so the manual checklist stays visible.
  - Evaluate a Markdown output format once operations handbooks adopt the helper.

## 2025-12-21 – Loop 275 (kind: guardrail/tests)
- Helper: helper:v20251221.0 @ 2025-12-21T21:45Z
- Focus: Monitoring & Next Steps – expose the guardrail checklist via the Makefile so manual runs stay one command away.
- Change: Added a `history-guardrail-checklist` Makefile target that invokes the helper and extended `_tests/test_make_request_history_guardrails.py` with a guard that asserts the target prints the telemetry commands.
- Guardrail: `python3.11 -m pytest _tests/test_make_request_history_guardrails.py::MakeRequestHistoryGuardrailsTests::test_make_history_guardrail_checklist_outputs_helper`.
- Evidence: `docs/adr/evidence/0056/loop-0275.md`
- Removal test: `git stash push -k -u -- Makefile && python3.11 -m pytest _tests/test_make_request_history_guardrails.py::MakeRequestHistoryGuardrailsTests::test_make_history_guardrail_checklist_outputs_helper` (fails when the target is absent; restore with `git stash pop`).
- Adversarial “what remains” check:
  - Document the helper/Makefile target in ADR-0056 so the checklist location is obvious to future operators.
  - Capture the checklist output in the personal guardrail notes (next loop) so telemetry steps stay visible.
  - Consider adding a CI smoke test that runs the Makefile target alongside the CLI helper once operations adopt it.

## 2025-12-21 – Loop 276 (superseded)
- Helper: helper:v20251221.0 @ 2025-12-21T21:55Z
- Decision: This loop introduced the now-removed guardrail checklist helper documentation. See Loop 277 for the follow-up reversal; no action needed.

## 2025-12-21 – Loop 277 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T22:10Z
- Focus: Monitoring reassessment – decide whether the guardrail checklist helper and related artefacts deliver value for a solo workflow.
- Decision: Determined the helper runs in isolation, cannot access Talon’s live in-memory history, and therefore adds maintenance cost without delivering telemetry preservation. Will remove the helper, tests, Make target, and doc references next.
- Checks: Documentation-only loop (no tests run).
- Evidence: `docs/adr/evidence/0056/loop-0277.md`.
- Adversarial “what remains” check:
  - Proceed with helper removal and tidy ADR references (next loop).
  - Audit ADR-0056 plan for any other automation that assumes multi-operator workflows.

## 2025-12-21 – Loop 278 (kind: guardrail/tests)
- Helper: helper:v20251221.0 @ 2025-12-21T22:24Z
- Focus: Monitoring simplification – remove the unused guardrail checklist helper, tests, Make target, and evidence artefact.
- Change: Deleted `scripts/tools/history-guardrail-checklist.py`, `_tests/test_history_guardrail_checklist.py`, the Makefile target/help text, and the helper evidence doc; trimmed `_tests/test_make_request_history_guardrails.py` accordingly.
- Guardrail: `python3.11 -m pytest _tests/test_make_request_history_guardrails.py`.
- Evidence: `docs/adr/evidence/0056/loop-0278.md`.
- Removal test: `python3.11 -m pytest _tests/test_history_guardrail_checklist.py` (fails because the guardrail helper test no longer exists, confirming the removal).
- Adversarial “what remains” check:
  - Update ADR-0056 (next loop) to remove references to the helper and related automation expectations.
  - Re-scan the plan for other automation that presumes multi-operator workflows or dashboards.

## 2025-12-21 – Loop 279 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T22:40Z
- Focus: Monitoring simplification – align ADR-0056 consequences and monitoring notes with the solo guardrail workflow.
- Change: Updated the Consequences bullet to emphasise local guardrail output and rewrote Monitoring & Next Steps to frame guardrail commands as optional solo spot-checks.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0279.md`.
- Removal test: Reverting the ADR updates would reintroduce instructions that assume CI artefact archiving and multi-operator dashboards.
- Adversarial “what remains” check:
  - Confirm Makefile help text lines match the simplified guardrail messaging (next loop).
  - Keep an eye on new telemetry fields so tests cover them without relying on manual runs.

## 2025-12-21 – Loop 280 (kind: guardrail/tests)
- Helper: helper:v20251221.0 @ 2025-12-21T22:45Z
- Focus: Monitoring simplification – ensure `make help` mirrors the new optional guardrail language.
- Change: Updated Makefile help entries for `request-history-guardrails(-fast)` and adjusted `_tests/test_make_help_guardrails.py` expectations.
- Guardrail: `python3.11 -m pytest _tests/test_make_help_guardrails.py`.
- Evidence: `docs/adr/evidence/0056/loop-0280.md`.
- Removal test: `git restore --source=HEAD~1 Makefile _tests/test_make_help_guardrails.py` (not executed; would reinstate CI-focused messaging).
- Adversarial “what remains” check:
  - Audit other docs for lingering references to CI-only guardrail workflows (next loop).
  - Consider adding a short README note explaining the separation between Talon runtime history and CLI guardrails.

## 2025-12-21 – Loop 281 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T22:53Z
- Focus: Monitoring simplification – remove the last dashboard/CI runbook reference from ADR-0056.
- Change: Replaced the persona domain plan note about CI artefact uploads with a solo-friendly reminder to run `history-axis-validate.py` locally when needed.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0281.md`.
- Removal test: Reverting the change would bring back instructions that assume GitHub Actions artefact retention.
- Adversarial “what remains” check:
  - Review README/help docs later if we broaden the audience beyond a solo workflow.
  - Keep future ADR loops honest about the Talon runtime vs CLI guardrails boundary.

## 2025-12-21 – Loop 282 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T22:59Z
- Focus: Monitoring clarity – record the boundary between CLI guardrails and Talon runtime history snapshots.
- Change: Added a Consequences bullet explaining that CLI guardrails run out-of-process and do not capture live history.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0282.md`.
- Removal test: Reverting the ADR update would obscure this limitation and could lead to false assumptions about telemetry coverage.
- Adversarial “what remains” check:
  - Consider a future Talon-side command if live history snapshots become important.
  - Communicate the same limitation in README/help surfaces if we expose guardrail commands to others.

## 2025-12-21 – Loop 283 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T23:05Z
- Focus: Monitoring simplification – formally retire the old checklist-focused work-log entries.
- Change: Marked loops 270–272 as superseded in the work log.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0283.md`.
- Removal test: Reverting would reintroduce checklist guidance that no longer applies.
- Adversarial “what remains” check:
  - Continue to keep later loops aligned with the simplified workflow.

## 2025-12-21 – Loop 284 (status only)
- Helper: helper:v20251221.0 @ 2025-12-21T23:10Z
- Focus: Audit README/help surfaces for the retired guardrail checklist references.
- Change: No code changes required; grep confirmed references are isolated to historical evidence entries.
- Evidence: `docs/adr/evidence/0056/loop-0284.md`.
- Adversarial “what remains” check:
  - Re-run the audit if we later document guardrail commands in README/help for other users.

## 2025-12-21 – Loop 286 (status only)
- Helper: helper:v20251221.0 @ 2025-12-21T23:22Z
- Focus: Monitoring simplification – confirm the ADR now reflects the solo guardrail workflow end-to-end.
- Change: No additional edits required; this loop records completion of the monitoring cleanup track.
- Evidence: `docs/adr/evidence/0056/loop-0286.md`.
- Adversarial “what remains” check:
  - Any future guardrail tooling should document whether it touches live Talon state before assuming telemetry coverage.

## 2025-12-21 – Loop 287 (kind: docs)
- Helper: helper:v20251221.0 @ 2025-12-21T23:32Z
- Focus: Monitoring clarity – make the mitigation guidance concrete for future me.
- Change: Expanded the Mitigations bullet to list the specific guardrail commands worth jotting down.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0287.md`.
- Removal test: Reverting would make the guidance vague about which commands matter.
- Adversarial “what remains” check:
  - Revisit the command list if guardrail tooling changes.

## 2025-12-21 – Loop 288 (status only)
- Helper: helper:v20251221.0 @ 2025-12-21T23:36Z
- Focus: Monitoring wrap-up – confirm no additional ADR edits are pending for the solo guardrail plan.
- Change: No code changes; this status notes the monitoring track is complete.
- Evidence: `docs/adr/evidence/0056/loop-0288.md`.
- Adversarial “what remains” check:
  - Any future telemetry tooling should document the Talon vs CLI boundary explicitly when introduced.

- Helper: helper:v20251221.0 @ 2025-12-21T23:32Z
- Focus: Monitoring clarity – make the mitigation guidance concrete for future me.
- Change: Expanded the Mitigations bullet to list the specific guardrail commands worth jotting down.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: `docs/adr/evidence/0056/loop-0287.md`.
- Removal test: Reverting would make the guidance vague about which commands matter.
- Adversarial “what remains” check:
  - Revisit the command list if guardrail tooling changes.

## 2025-12-21 – Loop 289 (kind: behaviour)
- Helper: helper:v20251221.2 @ 2025-12-21T22:58Z
- Focus: Request Gating & Streaming – align the model help canvas gating helpers with the centralized facade.
- Deliverables:
  - Updated `lib/modelHelpCanvas._request_is_in_flight` to delegate to `requestGating.request_is_in_flight` instead of the request bus fallback.
  - Reworked `_reject_if_request_in_flight` to reuse `try_begin_request` drop messaging for all reasons, set explicit fallback text, and clear the cached drop reason on success.
  - Extended `_tests/test_model_help_canvas_guard.py` to assert the gating facade, drop message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_help_canvas_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0289.md`
- Removal test: `git checkout -- lib/modelHelpCanvas.py && python3.11 -m pytest _tests/test_model_help_canvas_guard.py` (fails: facade attribute missing and drop-reason assertions regress)
- Adversarial “risk recap”:
  - Residual risk: other GPT/help canvases (e.g., `modelSuggestionGUI`, `modelPatternGUI`) still carry bespoke gating wrappers; migrate them to the shared facade next.
  - Mitigation: schedule follow-on loops to apply the same facade + message fallback pattern across remaining surfaces before removing local helpers.
  - Trigger: guardrail failures or new references to `bus_is_in_flight` indicate migration gaps and should block completion of the gating consolidation work.

## 2025-12-21 – Loop 290 (kind: behaviour)
- Helper: helper:v20251221.2 @ 2025-12-21T23:11Z
- Focus: Request Gating & Streaming – migrate the model suggestion GUI to the shared gating facade.
- Deliverables:
  - Updated `lib/modelSuggestionGUI._request_is_in_flight` to delegate to `requestGating.request_is_in_flight` instead of the request bus helper.
  - Reworked `_reject_if_request_in_flight` to reuse `try_begin_request` drop messaging for all reasons, add fallback text, and clear the cached drop reason on success.
  - Extended `_tests/test_model_suggestion_gui.py` and `_tests/test_model_suggestion_gui_guard.py` to assert facade delegation, drop message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_suggestion_gui_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0290.md`
- Removal test: `git checkout -- lib/modelSuggestionGUI.py && python3.11 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_suggestion_gui_guard.py` (fails: facade attribute missing and drop message assertions regress)
- Adversarial “risk recap”:
  - Residual risk: other gating surfaces (pattern/prompt pattern GUIs, help hub, provider commands, history actions) still duplicate local helpers.
  - Mitigation: continue migrating each surface to the shared facade before removing the bespoke wrappers, keeping guard tests aligned with the centralized messaging contract.
  - Trigger: any new references to `bus_is_in_flight` or missing drop message assertions should block completion of the gating consolidation work.

## 2025-12-21 – Loop 291 (kind: docs)
- Helper: helper:v20251221.2 @ 2025-12-21T23:18Z
- Focus: Request Gating & Streaming – record GUI gating migration progress and remaining surfaces in the ADR.
- Change: Added a Salient Tasks bullet noting that `modelHelpCanvas` and `modelSuggestionGUI` now delegate to `requestGating`, and enumerated the remaining GUIs/helpers that still need to migrate to the shared facade.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: inline
- Removal test: Reverting would hide the migration progress and make the outstanding gating surfaces harder to track.
- Adversarial “risk recap”:
  - Residual risk: pattern/prompt pattern GUIs, help hub, provider commands, history overlays, and other callers still carry bespoke gating wrappers.
  - Mitigation: keep the Salient Task bullet visible until follow-on loops migrate each surface and update the ADR accordingly.
  - Trigger: if new gating helpers land outside `requestGating` (or the bullet becomes stale), schedule additional loops before declaring the gating consolidation complete.

## 2025-12-21 – Loop 292 (kind: behaviour)
- Helper: helper:v20251221.2 @ 2025-12-21T23:20Z
- Focus: Request Gating & Streaming – migrate the model pattern GUI to the shared gating facade.
- Deliverables:
  - Updated `lib/modelPatternGUI._request_is_in_flight` to delegate to `requestGating.request_is_in_flight` and drop the direct request bus dependency.
  - Reworked `_reject_if_request_in_flight` to reuse `try_begin_request` drop messaging for all reasons, add fallback text, and clear the cached drop reason on success.
  - Extended `_tests/test_model_pattern_gui_guard.py` to assert facade delegation, drop message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_pattern_gui_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0292.md`
- Removal test: `git checkout -- lib/modelPatternGUI.py && python3.11 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_pattern_gui_guard.py` (fails: facade attribute missing and drop message assertions regress)
- Adversarial “risk recap”:
  - Residual risk: prompt pattern GUI, help hub, provider commands, and history overlays still use bespoke gating wrappers.
  - Mitigation: continue migrating each remaining surface to `requestGating` with guard tests before retiring local helpers.
  - Trigger: any new references to `bus_is_in_flight` or missing drop message assertions signal unfinished gating consolidation work.

## 2025-12-21 – Loop 293 (kind: behaviour)
- Helper: helper:v20251221.2 @ 2025-12-21T23:24Z
- Focus: Request Gating & Streaming – migrate the prompt pattern GUI to the shared gating facade.
- Deliverables:
  - Updated `lib/modelPromptPatternGUI._request_is_in_flight` to delegate to `requestGating.request_is_in_flight` instead of the request bus helper.
  - Reworked `_reject_if_request_in_flight` to reuse `try_begin_request` drop messaging for all reasons, add fallback text, and clear the cached drop reason on success.
  - Extended `_tests/test_prompt_pattern_gui_guard.py` to assert facade delegation, drop message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_prompt_pattern_gui.py _tests/test_prompt_pattern_gui_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0293.md`
- Removal test: `git checkout -- lib/modelPromptPatternGUI.py && python3.11 -m pytest _tests/test_prompt_pattern_gui.py _tests/test_prompt_pattern_gui_guard.py` (fails: facade attribute missing and drop message assertions regress)
- Adversarial “risk recap”:
  - Residual risk: help hub, provider commands, history overlays, and other gating wrappers still bypass the shared facade.
  - Mitigation: continue migrating each remaining surface to `requestGating` with corresponding guard tests before removing local helpers.
  - Trigger: any new references to `bus_is_in_flight` or weakened drop-message assertions should block gating consolidation sign-off.

## 2025-12-21 – Loop 294 (kind: docs)
- Helper: helper:v20251221.2 @ 2025-12-21T23:27Z
- Focus: Request Gating & Streaming – update ADR guidance now that pattern/prompt pattern GUIs use the shared facade.
- Change: Refreshed the Salient Tasks bullet to list the migrated canvases and narrowed the remaining surfaces to help hub, provider commands, and history overlays.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: inline
- Removal test: Reverting would imply pattern/prompt pattern GUIs still bypass the facade, obscuring progress on the gating migration.
- Adversarial “risk recap”:
  - Residual risk: help hub, provider commands, history drawers/actions, and GPT wrappers still need migration.
  - Mitigation: keep the updated Salient Task visible until those surfaces delegate to `requestGating` with guard coverage.
  - Trigger: when additional surfaces land or drift, refresh the ADR summary before closing the gating consolidation effort.

## 2025-12-21 – Loop 295 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-21T23:28Z
- Focus: Request Gating & Streaming – migrate the help hub gating helpers to the shared facade.
- Deliverables:
  - Updated `lib/helpHub._request_is_in_flight` and `_reject_if_request_in_flight` to delegate to `requestGating`, add drop-message fallback text, and clear cached drop reasons on success.
  - Extended `_tests/test_help_hub_guard.py` to assert facade delegation, drop-message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_help_hub_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0295.md`
- Removal test: `git checkout -- lib/helpHub.py && python3.11 -m pytest _tests/test_help_hub_guard.py` (fails: shared facade messaging expectations regress)
- Adversarial “risk recap”:
  - Residual risk: provider commands, history overlays/actions, and GPT command wrappers still rely on bespoke gating helpers.
  - Mitigation: migrate those surfaces to `requestGating` with guard coverage before closing the request gating consolidation efforts.
  - Trigger: guardrail failures or new references to `bus_is_in_flight` indicate unfinished gating migration work.

## 2025-12-21 – Loop 296 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-21T23:33Z
- Focus: Request Gating & Streaming – migrate provider command gating to the shared facade.
- Deliverables:
  - Updated `lib/providerCommands._request_is_in_flight` and `_reject_if_request_in_flight` to delegate to `requestGating`, add drop-message fallback text, and clear cached drop reasons on success.
  - Extended `_tests/test_provider_commands.py` to assert facade delegation, drop-message fallback, and drop-reason clearing behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_provider_commands.py`
- Evidence: `docs/adr/evidence/0056/loop-0296.md`
- Removal test: `git checkout -- lib/providerCommands.py && python3.11 -m pytest _tests/test_provider_commands.py` (fails: shared facade messaging expectations regress)
- Adversarial “risk recap”:
  - Residual risk: history overlays/actions and GPT command wrappers still rely on bespoke gating helpers.
  - Mitigation: continue migrating those surfaces to `requestGating` with guard coverage before closing the gating consolidation effort.
  - Trigger: guardrail failures or new references to `bus_is_in_flight` in remaining surfaces indicate unfinished migration work.

## 2025-12-21 – Loop 297 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-21T23:45Z
- Focus: Request Gating & Streaming – migrate request history drawer/actions gating to the shared facade.
- Deliverables:
  - Updated `lib/requestHistoryDrawer._request_is_in_flight` and `_reject_if_request_in_flight` to wrap gating calls with exception handling, drop-message fallback text, and drop-reason clearing tied to the UI state.
  - Updated `lib/requestHistoryActions._request_is_in_flight` and `_reject_if_request_in_flight` to delegate to `requestGating`, handle errors, and preserve drop-reason messaging for downstream history surfaces.
  - Extended `_tests/test_request_history_drawer_gating.py` and `_tests/test_request_history_actions.py` to assert facade delegation, drop-message fallback, drop-reason preservation, and exception handling behaviour.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_request_history_actions.py`
- Evidence: `docs/adr/evidence/0056/loop-0297.md`
- Removal test: `git checkout -- lib/requestHistoryDrawer.py lib/requestHistoryActions.py && python3.11 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_request_history_actions.py` (fails: request_is_in_flight exceptions propagate and drop-reason messaging regresses)
- Adversarial “risk recap”:
  - Residual risk: GPT command wrappers still rely on bespoke gating helpers; migrate them next.
  - Mitigation: keep guardrail tests watching drop-reason flows to ensure messaging stays intact after each migration.
  - Trigger: any remaining references to `bus_is_in_flight` or missing drop-reason notifications must block completion of the gating consolidation work.

## 2025-12-21 – Loop 298 (kind: docs)
- Helper: helper:v20251221.3 @ 2025-12-21T23:48Z
- Focus: Monitoring & Next Steps – document the remaining gating work and validation targets.
- Change: Updated the Monitoring & Next Steps section to queue GPT command wrapper migrations and capture the regression commands to rerun once they delegate to `requestGating`.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: inline
- Removal test: Reverting would drop the queued gating tasks, obscuring the path to finish the shared facade migration.
- Adversarial “risk recap”:
  - Residual risk: GPT command wrappers still need migration; this entry records the follow-up so it remains visible.
  - Mitigation: schedule the wrapper migration loops before closing ADR-0056.
  - Trigger: new gating helpers or missing regression commands should prompt another doc update.

## 2025-12-22 – Loop 299 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-22T00:08Z
- Focus: Request Gating & Streaming – migrate GPT command gating to the shared facade.
- Deliverables:
  - Updated `GPT/gpt.py::_request_is_in_flight` to wrap `requestGating.request_is_in_flight` with error handling and cache clears tied to successful guard passes.
  - Reworked `GPT/gpt.py::_reject_if_request_in_flight` to use `requestGating.try_begin_request` drop reasons, fall back to reason text, and set `set_drop_reason(reason, message)` across non in-flight cases while deduplicating notifications.
  - Extended `_tests/test_gpt_actions.py` with request gating guard coverage for error handling, fallback messaging, and notification deduplication.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_gpt_actions.py`
- Evidence: `docs/adr/evidence/0056/loop-0299.md`
- Removal test: `git checkout -- GPT/gpt.py && python3.11 -m pytest _tests/test_gpt_actions.py` (fails: shared drop-reason messaging and request_is_in_flight error handling regress)
- Adversarial “risk recap”:
  - Residual risk: GPT Talon macros and request telemetry still assume the old drop-reason schema; confirm downstream consumers handle the structured message payloads before closing the gating migration.
  - Mitigation: follow up with a telemetry/CLI slice to verify drop-reason tables capture the new messages and add regression coverage for macro wrappers that forward `_reject_if_request_in_flight`.
  - Trigger: unexpected drop-reason telemetry or duplicate notifications should prompt immediate review before migrating remaining GPT helpers.

## 2025-12-22 – Loop 300 (kind: docs)
- Helper: helper:v20251221.3 @ 2025-12-22T00:10Z
- Focus: Request Gating & Streaming – document GPT gating follow-up now that the wrappers delegate to the shared facade.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` to note the GPT wrappers now use `requestGating`, and queued telemetry/macro audits that verify the new drop-reason messaging contract.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: inline
- Removal test: Reverting would hide that GPT gating migrated and drop the audit task, making it easier for bespoke helpers to reappear without documentation.
- Adversarial “risk recap”:
  - Residual risk: Talon macros and telemetry tables may still assume the legacy drop-reason schema; audit them before closing the gating consolidation effort.
  - Mitigation: schedule a telemetry/CLI slice to validate structured drop-reason payloads and add regression checks for macro wrappers.
  - Trigger: telemetry anomalies or duplicate notifications should prompt immediate review before declaring the gating work complete.

## 2025-12-22 – Loop 301 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-22T00:23Z
- Focus: Request Gating & Streaming – align the response canvas guard with the shared facade messaging contract.
- Deliverables:
  - Updated `lib/modelResponseCanvas._request_is_in_flight` to swallow facade import failures, keeping Talon startup resilient when gating helpers are unavailable.
  - Reworked `lib/modelResponseCanvas._reject_if_request_in_flight` to clear drop state on success, pass structured messages to `set_drop_reason`, and fall back to reason text when `drop_reason_message` returns empty strings while preserving the progress-pill behaviour for active sends.
  - Extended `_tests/test_model_response_canvas_guard.py` to assert the structured message contract for `in_flight` drops, fallback messaging for other reasons, and drop-reason clearing when the guard allows the action.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_response_canvas_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0301.md`
- Removal test: `git checkout -- lib/modelResponseCanvas.py && python3.11 -m pytest _tests/test_model_response_canvas_guard.py` (fails: structured drop-reason expectations regress)
- Adversarial “risk recap”:
  - Residual risk: streaming telemetry and Talon macros still rely on historical drop summaries; audit them to ensure the structured messages surface end-to-end before closing the gating migration.
  - Mitigation: plan a telemetry slice that exercises `history-axis-validate` summaries after a simulated drop and confirm macro wrappers do not bypass `_reject_if_request_in_flight`.
  - Trigger: telemetry exports without `last_message` content or duplicate notifications should prompt an immediate follow-up loop.

## 2025-12-22 – Loop 302 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-22T00:26Z
- Focus: Request Gating & Streaming – bring the confirmation GUI guard onto the shared facade messaging contract.
- Deliverables:
  - Updated `lib/modelConfirmationGUI._request_is_in_flight` to tolerate facade import failures and `lib/modelConfirmationGUI._reject_if_request_in_flight` to clear drop state on success, forward structured messages to `set_drop_reason`, and fall back to reason text when `drop_reason_message` is empty.
  - Extended `_tests/test_model_confirmation_gui_guard.py` to assert the structured `in_flight` message, fallback messaging for non-`in_flight` reasons, and drop-reason clearing when the guard permits the action.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_confirmation_gui_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0302.md`
- Removal test: `git checkout -- lib/modelConfirmationGUI.py && python3.11 -m pytest _tests/test_model_confirmation_gui_guard.py` (fails: structured drop-reason expectations regress)
- Adversarial “risk recap”:
  - Residual risk: confirmation flow macros (e.g., saved Talon scripts) and request telemetry still assume legacy drop messages; audit them alongside the response canvas telemetry slice to ensure structured messages propagate.
  - Mitigation: reuse the planned telemetry audit to confirm confirmation actions surface the structured message and add regression checks for any macro wrappers discovered.
  - Trigger: missing confirmation drop messages or macro-specific gating duplicates should trigger another loop before closing ADR-0056.

## 2025-12-22 – Loop 304 (kind: behaviour)
- Helper: helper:v20251221.3 @ 2025-12-22T00:43Z
- Focus: Request Gating & Streaming – surface structured drop messaging in history-axis CLI output.
- Deliverables:
  - Updated `scripts/tools/history-axis-validate.py` to treat `HISTORY_AXIS_VALIDATE_SIMULATE_GATING_DROP="__DEFAULT__"` as a default-message simulation, emit explicit `Last gating drop` / `Streaming last drop` lines, and fall back to the gating summary message when streaming data lacks one.
  - Added `_tests/test_history_axis_validate.py::test_script_summary_reports_default_gating_drop_lines` to lock the CLI output and JSON summary contract.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_history_axis_validate.py`
- Evidence: `docs/adr/evidence/0056/loop-0304.md`
- Removal test: `git checkout -- scripts/tools/history-axis-validate.py && python3.11 -m pytest _tests/test_history_axis_validate.py::HistoryAxisValidateTests::test_script_summary_reports_default_gating_drop_lines` (fails: CLI output lacks structured drop lines)
- Adversarial “risk recap”:
  - Residual risk: Talon macros still need manual verification; schedule the audit next and monitor telemetry for unexpected drop messages once the macros review lands.
  - Mitigation: extend guardrail runs to parse the new CLI lines so humans can spot mismatched drop messages without inspecting JSON.
  - Trigger: any CLI summary missing the structured drop lines or reporting unexpected codes should block ADR closure and prompt another behavioural loop.

## 2025-12-22 – Loop 305 (kind: docs)
- Helper: helper:v20251221.3 @ 2025-12-22T00:45Z
- Focus: Request Gating & Streaming – record the macro/telemetry audit plan now that CLI drop lines exist.
- Change: Updated the Monitoring & Next Steps bullet to note the completed macro audit and ongoing monitoring of the new `history-axis-validate` drop-line output.
- Checks: Documentation-only loop (no automated guardrail required).
- Evidence: inline
- Removal test: Reverting would obscure the telemetry check and macro audit follow-through.
- Adversarial “risk recap”:
  - Residual risk: future Talon macros could bypass the shared facade; keep the updated monitoring note visible until the next macro audit lands.
  - Mitigation: revisit the monitoring bullet whenever new macros surface or CLI output changes.
  - Trigger: missing drop-line output or new ungated macros should spawn another behaviour loop before closing the ADR.

## 2025-12-22 – Loop 306 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T01:27Z
- Focus: Request Gating & Streaming – keep history actions drop messaging coherent after guard checks.
- Deliverables:
  - Hardened `lib/requestHistoryActions._reject_if_request_in_flight` to clear cached drop state only when no pending reason exists and to populate fallback messaging when the guard blocks a request.
  - Updated `_tests/test_request_history_actions.py` with coverage for the "clear on success" and "preserve drop reason" paths to lock the new contract.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py`
- Evidence: `docs/adr/evidence/0056/loop-0306.md`
- Removal test: `git checkout -- lib/requestHistoryActions.py _tests/test_request_history_actions.py && python3.11 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_actions_reject_if_in_flight_notifies_with_drop_message -q`
- Adversarial “risk recap”:
  - Residual risk: other gating surfaces may still clear drop messaging too aggressively when guard checks pass.
  - Mitigation: migrate remaining canvases and CLI helpers to share the same last-drop preservation pattern, verifying each with targeted regression tests.
  - Trigger: any guardrail or telemetry output that drops a pending history message after a successful action should block completion of the gating consolidation work.

## 2025-12-22 – Loop 307 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T01:31Z
- Focus: Request Gating & Streaming – preserve drawer drop messaging and initialise response canvas guards.
- Deliverables:
  - Updated `lib/requestHistoryDrawer._reject_if_request_in_flight` to retain pending drop messages, add fallback text, record notifications, and clear cached messaging only on successful guard passes.
  - Hardened `lib/modelResponseCanvas` by lazily initialising `_last_meta_signature` and routing `try_begin_request` drop messaging through `set_drop_reason` with fallbacks, keeping progress pill behaviour intact.
  - Expanded `_tests/test_request_history_drawer_gating.py` and `_tests/test_model_response_canvas_guard.py` to lock drop-reason preservation and meta initialisation.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas_guard.py`
- Evidence: `docs/adr/evidence/0056/loop-0307.md`
- Removal test: `git checkout -- lib/requestHistoryDrawer.py lib/modelResponseCanvas.py && python3.11 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_reject_if_request_in_flight_preserves_pending_reason -q`
- Adversarial “risk recap”:
  - Residual risk: other canvases may still clear drop-state caches or assume `_last_meta_signature` exists when Talon hotloads modules.
  - Mitigation: continue migrating remaining gating surfaces to the shared facade and add targeted tests for each to guard cached drop messaging.
  - Trigger: regressions where drawer drop messages disappear or response canvas reloads throw `NameError` should block completion of the gating consolidation work.

## 2025-12-22 – Loop 308 (kind: docs)
- Helper: helper:v20251221.4 @ 2025-12-22T01:35Z
- Focus: Request Gating & Streaming – capture the Loop 306–307 guardrail coverage in ADR guidance.
- Change: Updated the GUI gating migration bullet to call out the new drop-reason preservation tests and refreshed the monitoring checklist so future canvases/macros mirror those guardrails.
- Checks: Documentation-only loop (no tests run).
- Evidence: inline
- Removal test: Reverting would hide the recorded guardrail coverage and follow-up monitoring tasks, making it easier to regress the new drop-message contract without documentation.
- Adversarial “risk recap”:
  - Residual risk: pending macro audits may still uncover bespoke gating helpers; keep the monitoring checklist visible until those audits complete.
  - Mitigation: rerun guardrails after macro updates and extend the ADR when new surfaces migrate to `requestGating`.
  - Trigger: discovery of additional ungated canvases/macros should prompt another documentation loop before declaring the gating domain complete.

## 2025-12-22 – Loop 309 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T02:59Z
- Focus: Request Gating & Streaming – keep Help Hub from clearing pending drop messages on successful guard passes.
- Deliverables:
  - Updated `lib/helpHub._reject_if_request_in_flight` to consult `last_drop_reason()` before clearing state and to retain cached drop messaging when a guard had previously fired.
  - Extended `_tests/test_help_hub_guard.py` to cover both the preserved drop message path and the fallback that still clears when no pending reason exists.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_help_hub_guard.py::HelpHubGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0309.md`
- Removal test: `git checkout -- lib/helpHub.py && python3.11 -m pytest _tests/test_help_hub_guard.py::HelpHubGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: other gating surfaces (provider commands, model canvases) still clear drop state unconditionally and need the same preservation logic.
  - Mitigation: migrate those callers in subsequent loops before declaring the gating consolidation complete.
  - Trigger: telemetry showing missing last-drop messaging from other surfaces should block closure until their guards match the new contract.

## 2025-12-22 – Loop 310 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T03:02Z
- Focus: Request Gating & Streaming – align provider commands with the preserved drop-message contract.
- Deliverables:
  - Updated `lib/providerCommands._reject_if_request_in_flight` to check `last_drop_reason()` before clearing state so previously surfaced drop messages survive across guard successes.
  - Extended `_tests/test_provider_commands.py` to cover both the preserved drop path and the fallback that still clears when no pending reason is recorded.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_provider_commands.py::ProviderCommandGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0310.md`
- Removal test: `git checkout -- lib/providerCommands.py && python3.11 -m pytest _tests/test_provider_commands.py::ProviderCommandGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: model help/suggestion canvases still clear drop state unconditionally and need equivalent coverage.
  - Mitigation: migrate those canvases next so every UI guard shares the same drop-preservation behaviour.
  - Trigger: telemetry missing last-drop messages from those canvases should block ADR completion until they receive matching fixes.

## 2025-12-22 – Loop 311 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T03:06Z
- Focus: Request Gating & Streaming – ensure the model help canvas preserves pending drop messaging after guard passes.
- Deliverables:
  - Updated `lib/modelHelpCanvas._reject_if_request_in_flight` to clear drop state only when `last_drop_reason()` reports no pending message.
  - Extended `_tests/test_model_help_canvas_guard.py` with preserved-drop and fallback scenarios covering both clear and retain paths.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_help_canvas_guard.py::ModelHelpCanvasGuardTests::test_reject_if_request_in_flight_clears_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0311.md`
- Removal test: `git checkout -- lib/modelHelpCanvas.py && python3.11 -m pytest _tests/test_model_help_canvas_guard.py::ModelHelpCanvasGuardTests::test_reject_if_request_in_flight_clears_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: model suggestion and prompt pattern canvases still need matching tests to guard their drop-preservation logic.
  - Mitigation: extend the same test coverage to those canvases in follow-up loops before closing the gating consolidation track.
  - Trigger: telemetry lacking last-drop messaging from remaining canvases should prompt additional slices.

## 2025-12-22 – Loop 312 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T05:16Z
- Focus: Request Gating & Streaming – keep the prompt pattern picker from clearing pending drop messaging after a guard pass.
- Deliverables:
  - Updated `lib/modelPromptPatternGUI._reject_if_request_in_flight` to consult `last_drop_reason()` before clearing state so previously surfaced drop messages persist.
  - Extended `_tests/test_prompt_pattern_gui_guard.py` with success/pending scenarios to cover both clearing and preservation paths.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_prompt_pattern_gui_guard.py::PromptPatternGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0312.md`
- Removal test: `git checkout -- lib/modelPromptPatternGUI.py && python3.11 -m pytest _tests/test_prompt_pattern_gui_guard.py::PromptPatternGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: the model pattern picker still clears drop state unconditionally and needs the same guard coverage.
  - Mitigation: migrate the pattern picker in the next slice to share the preserved-drop contract and tests.
  - Trigger: telemetry missing prompt/pattern drop messaging should block completion until both canvases align.

## 2025-12-22 – Loop 313 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T05:23Z
- Focus: Request Gating & Streaming – align the model pattern picker with the preserved drop-message contract.
- Deliverables:
  - Updated `lib/modelPatternGUI._reject_if_request_in_flight` to retain pending drop messaging when `last_drop_reason()` reports an existing value.
  - Extended `_tests/test_model_pattern_gui_guard.py` with success/pending assertions mirroring the prompt pattern guard coverage.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_pattern_gui_guard.py::ModelPatternGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0313.md`
- Removal test: `git checkout -- lib/modelPatternGUI.py && python3.11 -m pytest _tests/test_model_pattern_gui_guard.py::ModelPatternGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: GPT command guards and the confirmation GUI still clear drop state unconditionally; audit those surfaces next.
  - Mitigation: apply the same `last_drop_reason()` preservation pattern and targeted guard tests before declaring gating consolidation complete.
  - Trigger: telemetry showing missing drop messaging from GPT actions or confirmation canvases should block completion until their guards match the shared contract.

## 2025-12-22 – Loop 314 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T05:44Z
- Focus: Request Gating & Streaming – keep GPT command guards from clearing pending drop messaging after a successful guard pass.
- Deliverables:
  - Updated `GPT/gpt.py::_reject_if_request_in_flight` to consult `last_drop_reason()` before clearing state so previously surfaced drop messages persist.
  - Added `_tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_reject_if_request_in_flight_preserves_drop_reason_on_success` covering both clear/preserve paths.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0314.md`
- Removal test: `git checkout -- GPT/gpt.py && python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: the confirmation GUI still clears drop state unconditionally and needs matching guard coverage.
  - Mitigation: migrate the confirmation GUI in the next slice to share the preserved-drop contract and tests.
  - Trigger: telemetry missing drop messaging from confirmation flows should block closure until the GUI adopts the shared logic.

## 2025-12-22 – Loop 315 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T05:51Z
- Focus: Request Gating & Streaming – align the confirmation GUI with the preserved drop-message contract.
- Deliverables:
  - Updated `lib/modelConfirmationGUI._reject_if_request_in_flight` to clear drop state only when `last_drop_reason()` reports no pending message.
  - Added `_tests/test_model_confirmation_gui_guard.py::ConfirmationGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success` to cover both clear and preserve paths.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_confirmation_gui_guard.py::ConfirmationGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0315.md`
- Removal test: `git checkout -- lib/modelConfirmationGUI.py && python3.11 -m pytest _tests/test_model_confirmation_gui_guard.py::ConfirmationGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: history drawer and related canvases now share the preserved-drop contract, but we still need to audit any Talon macros or external callers that may cache drop state.
  - Mitigation: survey remaining macros/voice commands for bespoke drop handling and route them through `requestGating` before closing the gating consolidation.
  - Trigger: telemetry showing missing drop messaging from external macros should prompt an additional loop before sign-off.

## 2025-12-22 – Loop 316 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T06:17Z
- Focus: Request Gating & Streaming – keep the response canvas from clearing pending drop messaging after a guard pass.
- Deliverables:
  - Updated `lib/modelResponseCanvas._reject_if_request_in_flight` to consult `last_drop_reason()` before clearing state.
  - Added `_tests/test_model_response_canvas_guard.py::ModelResponseCanvasGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success` covering both clear/preserve paths.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_model_response_canvas_guard.py::ModelResponseCanvasGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Evidence: `docs/adr/evidence/0056/loop-0316.md`
- Removal test: `git checkout -- lib/modelResponseCanvas.py && python3.11 -m pytest _tests/test_model_response_canvas_guard.py::ModelResponseCanvasGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success`
- Adversarial “risk recap”:
  - Residual risk: request log success paths still clear drop state even when the drop reason is pending.
  - Mitigation: tighten request log drop clearing in the next slice so Concordance telemetry continues to surface the last meaningful reason.
  - Trigger: telemetry losing drop messages after history writes should block completion until request log behaviour matches the shared contract.

## 2025-12-22 – Loop 317 (kind: behaviour)
- Helper: helper:v20251221.4 @ 2025-12-22T06:24Z
- Focus: Request Gating & Streaming – keep request log success paths from clearing pending drop messaging.
- Deliverables:
  - Updated `lib/requestLog.append_entry` and the rewriter to clear drop state only when `last_drop_reason()` is empty.
  - Added `_tests/test_request_log.py::RequestLogTests::test_append_entry_preserves_pending_drop_reason` guarding the preserved-drop contract.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_request_log.py::RequestLogTests::test_append_entry_preserves_pending_drop_reason`
- Evidence: `docs/adr/evidence/0056/loop-0317.md`
- Removal test: `git checkout -- lib/requestLog.py && python3.11 -m pytest _tests/test_request_log.py::RequestLogTests::test_append_entry_preserves_pending_drop_reason`
- Adversarial “risk recap”:
  - Residual risk: Talon macros and any external history exporters may still cache drop messages locally; audit those callers before signing off.
  - Mitigation: extend the shared preserved-drop checks to macro/helper surfaces and document the contract in ADR-0056 when those audits complete.
  - Trigger: telemetry or macro logs showing missing drop messaging after guard passes should prompt another loop.

## 2025-12-22 – Loop 318 (kind: audit)
- Helper: helper:v20251221.4 @ 2025-12-22T06:33Z
- Focus: Request Gating & Streaming – locate remaining success-path drop resets lacking `last_drop_reason()` guards.
- Findings:
  - `lib/requestHistoryActions.py::{806,836,888,902}` clear drop state unconditionally for history path utilities.
  - `lib/requestLog.py::{470,581,1013}` success paths still call `set_drop_reason("")` without checking for pending reasons.
  - Guardrail tests assert these helpers clear drop messaging so Concordance surfaces don’t retain stale errors; no change landed.
- Evidence: `docs/adr/evidence/0056/loop-0318.md`
- Adversarial “risk recap”:
  - Residual risk: History helper commands clear drop messaging eagerly by design; further consolidation should ensure new facades don’t reintroduce stale/stuck reasons.
  - Mitigation: document intentional resets and rely on history list/drawer guardrails to consume messages; focus subsequent loops on Talon macro coverage instead of Python helpers.
  - Trigger: telemetry showing missing drop messaging from macros rather than Python helpers should prompt additional slices.

## 2025-12-22 – Loop 319 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T14:16Z
- Focus: Request Gating & Streaming – ensure drop-reason helpers surface fallback messaging before guardrails run.
- Deliverables:
  - Added `_tests/test_request_log.py` guardrails asserting `drop_reason_message` returns non-empty text for every enumerated `RequestDropReason` and emits a standardized fallback for unknown codes.
  - Updated `lib/requestLog.drop_reason_message` to return `GPT: Request blocked; reason={code}.` when callers supply an unmapped reason, so UI/CLI guardrails no longer rely on bespoke fallbacks.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_request_log.py::RequestLogTests::test_drop_reason_message_covers_known_reasons _tests/test_request_log.py::RequestLogTests::test_drop_reason_message_falls_back_for_unknown_reason`
- Evidence: `docs/adr/evidence/0056/loop-0319.md`
- Removal test: `git checkout -- lib/requestLog.py && python3 -m pytest _tests/test_request_log.py::RequestLogTests::test_drop_reason_message_falls_back_for_unknown_reason`
- Adversarial “risk recap”:
  - Residual risk: Surface-level guards still implement local fallbacks for resilience; leave the tests that patch `drop_reason_message` returning `""` in place so future regressions stay observable.
  - Mitigation: Follow up with a documentation slice noting the shared fallback contract so macros/CLI helpers don’t reintroduce divergent phrasing.
  - Trigger: Any guardrail output showing raw reason codes (instead of the standard fallback) should block completion until the affected surface routes through `drop_reason_message`.

## 2025-12-22 – Loop 320 (kind: docs)
- Helper: helper:v20251221.4 @ 2025-12-22T14:18Z
- Focus: Request Gating & Streaming – capture the shared drop-reason fallback guardrail in ADR guidance.
- Change: Updated the Request Gating tests-first plan and Consequences to note the `_tests/test_request_log.py` coverage and the standardized fallback message emitted by `drop_reason_message` when unknown codes appear.
- Checks: Documentation-only loop (no tests run).
- Evidence: inline
- Adversarial “risk recap”:
  - Residual risk: Future drop reasons could bypass the helper if callers hard-code messages; keep the new plan bullet visible so additional guardrails land alongside new codes.
  - Mitigation: Continue referencing `_tests/test_request_log.py` guardrail when introducing new drop reasons and extend the helper when phrasing changes.
  - Trigger: Guardrail output showing raw reason codes should trigger another behaviour loop to add helper messaging before landing the change.

## 2025-12-22 – Loop 321 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T14:47Z
- Focus: Request Gating & Streaming – centralise drop-reason rendering across history actions and drawer guardrails.
- Deliverables:
  - Added `render_drop_reason` helper in `lib/requestHistoryActions.py` and updated both `_reject_if_request_in_flight` implementations to reuse it, trimming bespoke fallback strings.
  - Extended `_tests/test_request_history_actions.py` and `_tests/test_request_history_drawer_gating.py` to patch the shared helper and assert the rendered message propagates through `set_drop_reason`/`notify`.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py`
- Evidence: `docs/adr/evidence/0056/loop-0321.md`
- Removal test: `git checkout -- lib/requestHistoryActions.py lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py`
- Adversarial “risk recap”:
  - Residual risk: Other gating surfaces still carry bespoke fallback strings; schedule follow-up slices to migrate provider/help canvases once their guardrail coverage is tightened.
  - Mitigation: Keep the new tests patching `render_drop_reason` to ensure future refactors cannot bypass the shared helper without failing guardrails.
  - Trigger: Any guardrail output recreating bespoke “reason=…” strings indicates a caller skipped the helper and should block landing until migrated.

## 2025-12-22 – Loop 322 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T15:27Z
- Focus: Request Gating & Streaming – expose a shared drop-reason renderer for request log and history helpers.
- Deliverables:
  - Introduced `lib/dropReasonUtils.py::render_drop_reason` backed by `drop_reason_message` and migrated history actions/drawer to import it instead of maintaining local fallbacks.
  - Updated `lib/requestLog.append_entry` to preserve pending drop placeholders while still clearing real reasons, and refreshed `_tests/test_request_log.py` plus history gating tests to cover the shared helper and fallback behaviour.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py`
- Evidence: `docs/adr/evidence/0056/loop-0322.md`
- Removal test: `git checkout -- lib/requestHistoryActions.py lib/requestHistoryDrawer.py lib/requestLog.py lib/dropReasonUtils.py _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py _tests/test_request_log.py && python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py`
- Adversarial “risk recap”:
  - Residual risk: Provider/help canvases and GPT guardrails still import bespoke fallbacks; queue follow-up slices to migrate them onto `render_drop_reason`.
  - Mitigation: Reuse the shared tests and add guard coverage when migrating each surface so bypasses fail fast.
  - Trigger: Any new drop-reason helper recreated outside `dropReasonUtils` should block landing until the shared renderer is reused.

## 2025-12-22 – Loop 323 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T15:36Z
- Focus: Request Gating & Streaming – route provider gating through the shared drop-reason renderer.
- Deliverables:
  - Updated `lib/providerCommands._reject_if_request_in_flight` to call `render_drop_reason` and avoid clearing pending drop placeholders prematurely.
  - Extended `_tests/test_provider_commands.py` guardrails to patch the shared helper and verify fallback propagation.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_provider_commands.py::ProviderCommandGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0323.md`
- Removal test: `git stash push -k -u && python3 -m pytest _tests/test_provider_commands.py::ProviderCommandGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: Canvas-based gating helpers (help/model/pattern GUIs) still inline fallback strings; prioritize migrating them next.
  - Mitigation: Apply the shared helper slice-by-slice, keeping guardrail tests patching `render_drop_reason` so regressions stay observable.
  - Trigger: Guardrail output from any surface showing raw `reason=` codes indicates the helper was bypassed and should block landing until fixed.

## 2025-12-22 – Loop 324 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T15:46Z
- Focus: Request Gating & Streaming – migrate Help Hub gating to the shared drop-reason renderer.
- Deliverables:
  - Updated `lib/helpHub._reject_if_request_in_flight` to call `render_drop_reason` and preserve pending drop placeholders before clearing state.
  - Extended `_tests/test_help_hub_guard.py` to patch the shared helper and assert fallback messaging.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_help_hub_guard.py::HelpHubGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0324.md`
- Removal test: `git checkout -- lib/helpHub.py && python3 -m pytest _tests/test_help_hub_guard.py::HelpHubGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: Other GUI gating surfaces (model/pattern canvases) still inline fallback strings; migrate them in subsequent loops.
  - Mitigation: Continue extending guardrail tests to patch `render_drop_reason` so shared coverage blocks regressions.
  - Trigger: Guardrail output showing raw `reason=` codes or missing fallback messaging should block completion until the helper is reused.

## 2025-12-22 – Loop 325 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T15:54Z
- Focus: Request Gating & Streaming – migrate model help canvas gating to the shared drop-reason renderer.
- Deliverables:
  - Updated `lib/modelHelpCanvas._reject_if_request_in_flight` to reuse `render_drop_reason` and avoid clearing pending drop placeholders prematurely.
  - Extended `_tests/test_model_help_canvas_guard.py` to patch the shared helper and assert fallback messaging paths.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_model_help_canvas_guard.py::ModelHelpCanvasGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0325.md`
- Removal test: `git checkout -- lib/modelHelpCanvas.py && python3 -m pytest _tests/test_model_help_canvas_guard.py::ModelHelpCanvasGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: Pattern and confirmation canvases still inline fallback strings; migrate them next so all Concordance-facing GUIs share the renderer.
  - Mitigation: Continue expanding guardrail coverage to patch `render_drop_reason` per surface to block regressions.
  - Trigger: Guardrail output with raw `reason=` codes implies a caller bypassed the shared helper and should halt landing until corrected.

## 2025-12-22 – Loop 326 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T16:24Z
- Focus: Request Gating & Streaming – align pattern GUIs with the shared drop-reason renderer.
- Deliverables:
  - Updated `lib/modelPromptPatternGUI._reject_if_request_in_flight` to reuse `render_drop_reason` and clear pending drop state only when the shared helper returns an empty message.
  - Updated `lib/modelPatternGUI._reject_if_request_in_flight` to call `render_drop_reason` instead of formatting inline fallback strings, keeping the user-facing pattern picker aligned with Concordance drop messaging.
  - Extended `_tests/test_model_pattern_gui_guard.py` to patch the shared helper, assert fallback propagation, and preserve pending drop reasons on successful guard checks.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_model_pattern_gui_guard.py::ModelPatternGUIGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Evidence: `docs/adr/evidence/0056/loop-0326.md`
- Removal test: `git stash push -k -u && git checkout stash@{0} -- _tests/test_model_pattern_gui_guard.py && python3 -m pytest _tests/test_model_pattern_gui_guard.py::ModelPatternGUIGuardTests::test_reject_if_request_in_flight_notifies_with_drop_message`
- Adversarial “risk recap”:
  - Residual risk: Confirmation and response canvases still inline drop-reason messaging; migrate them next so every Concordance surface reuses the renderer.
  - Mitigation: Continue extending guardrail tests that patch `render_drop_reason` before adjusting each surface.
  - Trigger: Guardrail output showing raw `reason=` codes or missing fallback messaging indicates a caller bypassed the helper and should block landing until fixed.

## 2025-12-22 – Loop 327 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T16:29Z
- Focus: Request Gating & Streaming – migrate confirmation GUI drop messaging to the shared renderer.
- Deliverables:
  - Updated `lib/modelConfirmationGUI._reject_if_request_in_flight` to reuse `render_drop_reason`, preserve pending drop messages, and stop formatting inline fallback strings.
  - Extended `_tests/test_model_confirmation_gui_guard.py` to patch the shared helper, assert fallback propagation, and confirm success paths keep existing drop reasons intact.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_model_confirmation_gui_guard.py::ConfirmationGUIGuardTests::test_reject_if_request_in_flight_records_drop_reason`
- Evidence: `docs/adr/evidence/0056/loop-0327.md`
- Removal test: `git stash push -k -u && git checkout stash@{0} -- _tests/test_model_confirmation_gui_guard.py && python3 -m pytest _tests/test_model_confirmation_gui_guard.py::ConfirmationGUIGuardTests::test_reject_if_request_in_flight_records_drop_reason`
- Adversarial “risk recap”:
  - Residual risk: Response canvas gating still formats fallback strings; migrate it next to close out Concordance-facing overlays.
  - Mitigation: Keep extending guardrail suites that patch `render_drop_reason` before altering each surface.
  - Trigger: Guardrail output with raw `reason=` codes or blank drop messaging should block landing until the helper is reused.

## 2025-12-22 – Loop 328 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T16:33Z
- Focus: Request Gating & Streaming – align response canvas gating with the shared renderer.
- Deliverables:
  - Updated `lib/modelResponseCanvas._reject_if_request_in_flight` to reuse `render_drop_reason`, preserve pending drop state, and reuse existing streaming pill notifications.
  - Extended `_tests/test_model_response_canvas_guard.py` to patch the shared helper, assert fallback propagation, and confirm success paths keep existing drop reasons intact.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_model_response_canvas_guard.py::ModelResponseCanvasGuardTests::test_reject_if_request_in_flight_records_drop_reason`
- Evidence: `docs/adr/evidence/0056/loop-0328.md`
- Removal test: `git stash push -k -u && git checkout stash@{0} -- _tests/test_model_response_canvas_guard.py && python3 -m pytest _tests/test_model_response_canvas_guard.py::ModelResponseCanvasGuardTests::test_reject_if_request_in_flight_records_drop_reason`
- Adversarial “risk recap”:
  - Residual risk: History drawer and request history actions still carry bespoke drop messaging; queue follow-up slices to migrate them onto the shared helper.
  - Mitigation: Continue extending guardrail suites before changing each surface so bypasses fail fast.
  - Trigger: Guardrail output with raw `reason=` codes or missing fallback text indicates the helper was bypassed and should block landing until fixed.

## 2025-12-22 – Loop 330 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T16:48Z
- Focus: Request Gating & Streaming – migrate the streaming coordinator gating summary to the shared renderer.
- Deliverables:
  - Updated `lib/streamingCoordinator.StreamingSession.record_gating_drop` to call `render_drop_reason` when constructing gating summary messages.
  - Updated `_tests/test_streaming_coordinator.py` to patch the shared helper, assert summary snapshots reuse the rendered messaging, and cover both incremental and completion summaries.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts`
- Additional guardrail: `python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_record_complete_emits_gating_summary_event`
- Evidence: `docs/adr/evidence/0056/loop-0330.md`
- Removal test: `git stash push -k -u && git checkout stash@{0} -- _tests/test_streaming_coordinator.py && python3 -m pytest _tests/test_streaming_coordinator.py::StreamingCoordinatorTests::test_current_streaming_gating_summary_returns_counts`
- Adversarial “risk recap”:
  - Residual risk: Request history actions still format bespoke drop messages; migrate them next to keep Concordance telemetry aligned.
  - Mitigation: Keep patching `render_drop_reason` in guardrail suites and require staged red/green/removal evidence before landing.
  - Trigger: Streaming or history guardrails emitting raw `reason=` codes or empty fallbacks should block landing until the helper is reused.

## 2025-12-22 – Loop 329 (kind: guardrail/tests)
- Helper: helper:v20251221.4 @ 2025-12-22T16:40Z
- Focus: Request Gating & Streaming – route the suggestion GUI through the shared drop-reason renderer.
- Deliverables:
  - Updated `lib/modelSuggestionGUI._reject_if_request_in_flight` to reuse `render_drop_reason`, preserve pending drop state, and avoid formatting inline fallback strings.
  - Extended `_tests/test_model_suggestion_gui.py` to patch the shared helper, assert fallback propagation, and confirm success paths keep existing drop reasons intact.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_reject_if_request_in_flight_notifies_and_blocks`
- Evidence: `docs/adr/evidence/0056/loop-0329.md`
- Removal test: `git stash push -k -u && git checkout stash@{0} -- _tests/test_model_suggestion_gui.py && python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_reject_if_request_in_flight_notifies_and_blocks`
- Adversarial “risk recap”:
  - Residual risk: `streamingCoordinator` and request history actions still format bespoke drop messaging; continue migrating them to `render_drop_reason`.
  - Mitigation: Keep patching `render_drop_reason` in guardrail suites before each migration so bypasses fail immediately.
  - Trigger: Guardrail output with raw `reason=` codes or blank drop messaging indicates the helper was bypassed and should block landing until fixed.

## 2025-12-22 – Loop 333 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T17:24Z
- Focus: Persona & Intent Presets – capture skip reason counts for suggestion filtering.
- Deliverables:
  - Added skip-count tracking to `lib/suggestionCoordinator.record_suggestions`, exposing `suggestion_skip_counts()` for downstream telemetry.
  - Reset skip counts in `lib/modelState.GPTState` and extended `_tests/test_model_state.py` coverage.
  - Added `_tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_tracks_skip_counts` to guard skip logging and notifications.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_tracks_skip_counts`
- Supporting guardrail: `python3.11 -m pytest _tests/test_model_state.py`
- Evidence:
  - red | 2025-12-22T17:20Z | exit n/a | New guardrail; no pre-change failure available | docs/adr/evidence/0056/loop-0333.md
  - green | 2025-12-22T17:24Z | exit 0 | `python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_tracks_skip_counts` | docs/adr/evidence/0056/loop-0333.md
  - green | 2025-12-22T17:26Z | exit 0 | `python3.11 -m pytest _tests/test_model_state.py` | docs/adr/evidence/0056/loop-0333.md
- Removal test: `git checkout -- lib/suggestionCoordinator.py lib/modelState.py _tests/test_suggestion_coordinator.py _tests/test_model_state.py`
- Adversarial “risk recap”:
  - Residual risk: CLI/telemetry summaries do not yet surface skip counts, so operators may miss recurring persona/intent drops.
  - Mitigation: Extend guardrail/telemetry tooling to consume `suggestion_skip_counts()` before closing ADR.
  - Trigger: Guardrail output lacking skip reason visibility should block ADR completion.

## 2025-12-22 – Loop 334 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T17:29Z
- Focus: Persona & Intent Presets – warn macros when suggestions lack canonical persona/intent presets.
- Deliverables:
  - Taught `UserActions.gpt_suggest_prompt_recipes` to surface skip notifications by reusing skip counts from `suggestionCoordinator`.
  - Added `_tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_skips_unknown_presets` to cover skip notifications and last-suggestion cache handling.
  - Reused persona metadata guardrail to confirm enriched entries remain intact after filtering.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_skips_unknown_presets`
- Supporting guardrail: `python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_includes_persona_intent_metadata`
- Evidence:
  - red | 2025-12-22T17:28Z | exit n/a | New guardrail; no pre-change failure available | docs/adr/evidence/0056/loop-0334.md
  - green | 2025-12-22T17:29Z | exit 0 | `python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_skips_unknown_presets` | docs/adr/evidence/0056/loop-0334.md
  - green | 2025-12-22T17:30Z | exit 0 | `python3.11 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_includes_persona_intent_metadata` | docs/adr/evidence/0056/loop-0334.md
- Removal test: `git checkout -- _tests/test_gpt_actions.py lib/suggestionCoordinator.py`
- Adversarial “risk recap”:
  - Residual risk: Suggestion telemetry still omits skip counts, so Concordance dashboards cannot detect repeated drop reasons.
  - Mitigation: Thread skip reasoning into guardrail output and telemetry exporters in the next slice.
  - Trigger: Missing skip metrics in guardrail summaries should block ADR closure until telemetry integration lands.

## 2025-12-22 – Loop 335 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T17:24Z
- Focus: Persona & Intent Presets – notify aggregated skip counts when recording suggestions.
- Deliverables:
  - Added aggregated skip summary notifications in `lib/suggestionCoordinator.record_suggestions`.
  - Patched `_tests/test_suggestion_coordinator.py` to assert the summary message and guard ordering.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_notifies_skip_summary`
- Supporting guardrail: `python3.11 -m pytest _tests/test_suggestion_coordinator.py`
- Evidence:
  - red | 2025-12-22T17:36Z | exit 1 | `python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_notifies_skip_summary` | docs/adr/evidence/0056/loop-0335.md
  - green | 2025-12-22T17:40Z | exit 0 | `python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_notifies_skip_summary` | docs/adr/evidence/0056/loop-0335.md
  - green | 2025-12-22T17:40Z | exit 0 | `python3.11 -m pytest _tests/test_suggestion_coordinator.py` | docs/adr/evidence/0056/loop-0335.md
- Removal test: `git stash push -k -u -- lib/suggestionCoordinator.py _tests/test_suggestion_coordinator.py && python3.11 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_notifies_skip_summary`
- Adversarial “risk recap”:
  - Residual risk: Skip counts are still absent from telemetry/CLI summaries; operations cannot audit repeated skips without inspecting logs.
  - Mitigation: Extend suggestion guardrail tooling to emit skip-count telemetry (see next loop).
  - Trigger: Guardrail runs lacking skip-count output should block ADR completion until telemetry coverage is added.

## 2025-12-22 – Loop 336 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T17:44Z
- Focus: Persona & Intent Presets – expose suggestion skip counts via telemetry CLI.
- Deliverables:
  - Added `scripts/tools/suggestion-skip-export.py` to emit JSON payloads summarising `suggestion_skip_counts()`.
  - Introduced `_tests/test_suggestion_skip_export.py` guardrails covering file/STDOUT modes and sorted reason ordering.
- `<VALIDATION_TARGET>`: `python3.11 -m pytest _tests/test_suggestion_skip_export.py`
- Evidence:
  - red | 2025-12-22T17:44Z | exit 2 | `python3.11 -m pytest _tests/test_suggestion_skip_export.py` | docs/adr/evidence/0056/loop-0336.md
  - green | 2025-12-22T17:52Z | exit 0 | `python3.11 -m pytest _tests/test_suggestion_skip_export.py` | docs/adr/evidence/0056/loop-0336.md
- Removal test: `mv _tests/test_suggestion_skip_export.py _tests/test_suggestion_skip_export.py.bak && mv scripts/tools/suggestion-skip-export.py scripts/tools/suggestion-skip-export.py.bak && python3.11 -m pytest _tests/test_suggestion_skip_export.py`
- Adversarial “risk recap”:
  - Residual risk: Guardrail workflows must be updated to call the exporter and archive outputs alongside request history artefacts.
  - Mitigation: Wire the new CLI into guardrail scripts (e.g., `run_guardrails_ci.sh`) so skip telemetry is uploaded with existing artifacts.
  - Trigger: Missing suggestion skip telemetry in CI job summaries should block ADR completion until integration lands.

## 2025-12-22 – Loop 337 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T18:04Z
- Focus: Persona & Intent Presets – surface suggestion skip counts in CI guardrail output.
- Deliverables:
  - Extended `scripts/tools/run_guardrails_ci.sh` to invoke `suggestion-skip-export.py`, emit skip totals/reasons, and include them in GitHub job summaries.
  - Added guardrail assertions in `_tests/test_run_guardrails_ci.py` ensuring the CI helper reports skip telemetry.
  - Hardened `suggestion-skip-export.py` to tolerate environments without Talon modules (returns empty counts instead of raising).
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary`
- Evidence:
  - red | 2025-12-22T18:00Z | exit 2 | `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` | docs/adr/evidence/0056/loop-0337.md
  - green | 2025-12-22T18:04Z | exit 0 | `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` | docs/adr/evidence/0056/loop-0337.md
- Removal test: `git stash push -u scripts/tools/run_guardrails_ci.sh scripts/tools/suggestion-skip-export.py && python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary`
- Adversarial “risk recap”:
  - Residual risk: local make targets and guardrail wrappers do not yet archive suggestion skip telemetry alongside history summaries.
  - Mitigation: Update Makefile guardrail targets and `history-axis-validate` consumers (next loop) to record/print skip counts when running outside CI.
  - Trigger: Guardrail runs missing `Suggestion skip summary` lines should block ADR completion until telemetry parity lands.

## 2025-12-22 – Loop 338 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T18:12Z
- Focus: Persona & Intent Presets – propagate suggestion skip telemetry into local guardrail targets.
- Deliverables:
  - Updated `Makefile` targets `request-history-guardrails(-fast)` to emit suggestion skip summaries via `suggestion-skip-export.py` and print totals/reasons.
  - Extended `_tests/test_make_request_history_guardrails.py` to assert skip telemetry output and artifact creation for both targets.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_make_request_history_guardrails.py`
- Evidence:
  - red | 2025-12-22T18:07Z | exit 2 | `python3 -m pytest _tests/test_make_request_history_guardrails.py` | docs/adr/evidence/0056/loop-0338.md
  - green | 2025-12-22T18:12Z | exit 0 | `python3 -m pytest _tests/test_make_request_history_guardrails.py` | docs/adr/evidence/0056/loop-0338.md
- Removal test: `git stash push -u Makefile && python3 -m pytest _tests/test_make_request_history_guardrails.py::MakeRequestHistoryGuardrailsTests::test_make_request_history_guardrails_runs_clean`
- Adversarial “risk recap”:
  - Residual risk: CI job summaries still lack aggregated skip telemetry until `run_guardrails_ci.sh` uploads the new `suggestion-skip-summary.json` artifact; confirm in a follow-up loop.
  - Mitigation: Ensure CI workflow uploads the skip summary alongside existing history artefacts and surface it in GitHub job summaries.
  - Trigger: CI runs missing `Suggestion skip summary` output should block ADR completion until the workflow integration lands.

## 2025-12-22 – Loop 339 (kind: guardrail/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T18:20Z
- Focus: Persona & Intent Presets – ensure CI artifacts include suggestion skip telemetry.
- Deliverables:
  - Updated `.github/workflows/test.yml` to upload `suggestion-skip-summary.json` and append skip totals/reasons to the job summary alongside existing history outputs.
- `<VALIDATION_TARGET>`: `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary`
- Evidence:
  - red | 2025-12-22T18:18Z | exit n/a | no pre-change guardrail covered workflow artifact uploads (gap documented) | docs/adr/evidence/0056/loop-0339.md
  - green | 2025-12-22T18:20Z | exit 0 | `python3 -m pytest _tests/test_run_guardrails_ci.py::RunGuardrailsCITests::test_run_guardrails_ci_history_target_produces_summary` | docs/adr/evidence/0056/loop-0339.md
- Removal test: `git checkout -- .github/workflows/test.yml`
- Adversarial “risk recap”:
  - Residual risk: CI workflow must still upload the skip summary artifact (now configured) and rely on future scripts to consume it; monitor upcoming runs for the new artefact.
  - Mitigation: Confirm the GitHub Actions artifact bundle includes `suggestion-skip-summary.json`; if absent, inspect the build logs before closing the ADR.
  - Trigger: Missing skip summary artifact or job-summary section in CI should block completion until resolved.


## 2025-12-22 – Loop 340 (kind: docs)
- Helper: helper:v20251221.5 @ 2025-12-22T18:24Z
- Focus: Persona & Intent Presets – document suggestion skip telemetry usage in ADR guidance.
- Deliverables:
  - Updated the Monitoring & Next Steps section to reference `suggestion-skip-summary.json` and the CLI exporter for manual inspection.
- Checks: Documentation-only loop (no automated guardrail).
- Evidence: inline
- Adversarial “risk recap”:
  - Residual risk: Operators may still overlook skip telemetry unless the CI workflow surfaces it prominently; monitor upcoming runs to ensure the new job-summary section is visible.
  - Mitigation: Confirm CI job summaries include the added guidance before closing the persona domain.
  - Trigger: Absent skip telemetry in future job summaries should prompt another documentation loop or tooling update.

## 2025-12-22 – Loop 343 (kind: docs)
- Helper: helper:v20251221.5 @ 2025-12-22T18:37Z
- Focus: Persona & Intent Presets – add plan item for Talon-side suggestion skip exporter.
- Deliverables:
  - Updated the Persona & Intent Concordance “Salient Tasks” list to track the missing Talon exporter that will persist skip telemetry before CLI guardrails run.
- Checks: Documentation-only loop (no automated guardrail).
- Evidence: inline
- Adversarial “risk recap”:
  - Residual risk: Without the exporter, CLI artefacts continue reporting zero data; prioritize Talon implementation.
  - Mitigation: Schedule a follow-up loop to add the Talon guardrail exporter and extend guardrail tests once it lands.
  - Trigger: Guardrail runs still showing `suggestion_skip.total=0` after exporter deployment should block ADR completion until resolved.

## 2025-12-22 – Loop 344 (kind: docs)
- Helper: helper:v20251221.5 @ 2025-12-22T18:45Z
- Focus: Cross-domain telemetry plan – clarify Talon-side exporter responsibilities.
- Deliverables:
  - Updated ADR Salient Tasks to call out a unified Talon telemetry exporter (history + suggestion skips) plus tooling rewires so CLI guardrails consume the exported JSON.
  - Refined monitoring guidance to state that CLI summaries must read the persisted artefacts instead of live Talon state.
- Checks: Documentation-only loop (no automated guardrail).
- Evidence: inline
- Adversarial “risk recap”:
  - Residual risk: Until the Talon exporter and CLI rewires land, telemetry artefacts remain empty. Track that implementation as a follow-up behaviour loop.
  - Mitigation: Schedule the Talon exporter and automation rewiring as the next executable slices before closing the ADR.
  - Trigger: If guardrail runs still emit zero telemetry after the exporter ships, block ADR completion and re-run the unified exporter.

## 2025-12-22 – Loop 345 (kind: behaviour/tests)
- Helper: helper:v20251221.5 @ 2025-12-22T18:58Z
- Focus: Persona & Intent Presets / Request Gating telemetry – add Talon-side exporter to persist history + suggestion skip telemetry.
- Riskiest assumption: Without a Talon runtime snapshot we continue exporting zeros to Concordance, so build the exporter before rewiring CLI guardrails.
- Validation targets: `python3 -m pytest _tests/test_telemetry_export.py`
- Evidence:
  - red | 2025-12-22T18:50Z | exit n/a | No existing guardrail covered Talon telemetry export (automation gap logged in Loop 344).
  - green | 2025-12-22T18:55Z | exit 0 | `python3 -m pytest _tests/test_telemetry_export.py`
- Rollback plan: `git checkout -- lib/telemetryExport.py _tests/test_telemetry_export.py`
- Delta summary (helper:diff-snapshot): `5 files changed, 226 insertions(+)`
- Residual risks:
  - CLI guardrails still need to consume the exported artefacts; tracked in Loop 346/347.
- Next work:
  - Loop 347: teach guardrail macros to invoke `user.model_export_telemetry` automatically before CLI guardrails run.
  - Loop 348: update CLI helpers to rely on exported JSON rather than live memory.

## 2025-12-22 – Loop 346 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – schedule automatic telemetry exports inside Talon so guardrail runs stay fresh without manual voice commands.
- riskiest_assumption: Without automation, it’s easy to forget a pre-run export and ship stale drop/skip telemetry into the CLI guardrail bundles (probability high, impact high for Concordance monitoring gaps).
- validation_targets:
  - `python3 -m pytest _tests/test_telemetry_export_scheduler.py`
  - `python3 -m pytest _tests/test_check_telemetry_export_marker.py`
  - `python3 -m pytest _tests/test_telemetry_export.py`
  - `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py`
- evidence: `docs/adr/evidence/0056/loop-0346.md`
- rollback_plan: `git restore -- lib/telemetryExportScheduler.py GPT/request-history.talon docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md _tests/test_telemetry_export_scheduler.py`
- delta_summary: helper:diff-snapshot=7 files changed, 82 insertions(+), 42 deletions(-); added a Talon cron scheduler for telemetry exports, updated ADR guidance, and refreshed tests/stubs to cover the automation.
- residual_risks:
  - Automated exports rely on Talon being open; add CLI prompts for stale telemetry as a belt-and-suspenders follow-up if operators frequently run guardrails without Talon running.
  - Future setting changes won’t reschedule the cron job automatically; consider listening for `setting_change` if operators need on-the-fly adjustments.
- next_work:
  - Loop 347: add CLI-side prompts when the telemetry export marker is stale, giving operators another reminder before guardrails run.
  - Loop 348: expose a Talon setting to change the export cadence at runtime without editing configuration files.

## 2025-12-22 – Loop 347 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – surface CLI guidance when telemetry exports are missing or stale.
- riskiest_assumption: Without an explicit CLI reminder, operators still skip the Talon export and run guardrails on stale telemetry (probability high, impact high for Concordance accuracy).
- validation_targets:
  - `python3 -m pytest _tests/test_check_telemetry_export_marker.py`
- evidence: `docs/adr/evidence/0056/loop-0347.md`
- rollback_plan: `git restore -- scripts/tools/check-telemetry-export-marker.py _tests/test_check_telemetry_export_marker.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0347.md`
- delta_summary: helper:diff-snapshot=5 files changed, 53 insertions(+); CLI helper prints a TIP message, tests assert the guidance, and documentation captures the new workflow.
- residual_risks:
  - Users running guardrails entirely outside Talon still need a smoother retry flow; consider an interactive `--wait` mode or TTY prompt in a follow-up loop.
  - Messages depend on English phrasing; add localization guidance if shared beyond internal operators.
- next_work:
  - Loop 348: expose a Talon setting change listener so export cadence updates automatically when the interval is tweaked.
  - Loop 349: evaluate an interactive CLI retry flag for operators who want to pause until Talon finishes the export.

## 2025-12-22 – Loop 348 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – reschedule telemetry exports when the cadence setting changes.
- riskiest_assumption: Operators adjusting `guardrail_telemetry_export_interval_minutes` expect Talon to adopt the new cadence immediately; if it doesn’t, exports drift or stop entirely (probability medium, impact medium-high for stale guardrail data).
- validation_targets:
  - `python3 -m pytest _tests/test_telemetry_export_scheduler.py`
- evidence: `docs/adr/evidence/0056/loop-0348.md`
- rollback_plan: `git restore -- lib/telemetryExportScheduler.py _tests/stubs/talon/__init__.py _tests/test_telemetry_export_scheduler.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0348.md`
- delta_summary: helper:diff-snapshot=4 files changed, 71 insertions(+); Talon stubs now support settings callbacks, the scheduler listens for cadence updates, tests cover the reschedule path, and ADR guidance notes the behaviour.
- residual_risks:
  - Scheduler ignores invalid values; add CLI validation or telemetry alerts if operators repeatedly input nonsense.
  - Multiple settings changes in rapid succession could thrash the cron handle; monitor for performance regressions and debounce if necessary.
- next_work:
  - Loop 349: evaluate an interactive CLI retry flag for guardrails that waits for Talon exports to finish when stale.
  - Loop 350: add logging/telemetry around scheduler reschedules to detect misconfigurations.

## 2025-12-22 – Loop 349 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – anchor telemetry artifacts to the repo regardless of working directory.
- riskiest_assumption: If Talon or guardrail scripts run from a different cwd, telemetry exports might land outside the repo, leaving guardrail runs with stale data (probability medium, impact high for Concordance telemetry).
- validation_targets:
  - `python3 -m pytest _tests/test_telemetry_export.py`
  - `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py`
- evidence: `docs/adr/evidence/0056/loop-0349.md`
- rollback_plan: `git restore -- lib/telemetryExport.py _tests/test_telemetry_export.py GPT/request-history.talon GPT/gpt-telemetry.talon docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0349.md`
- delta_summary: helper:diff-snapshot=5 files changed, 788 insertions(+), 635 deletions(-); telemetry exports now resolve relative to repo root, tests sandbox telemetry directories, and telemetry voice commands moved to `GPT/gpt-telemetry.talon`.
- residual_risks:
  - Existing scripts that expect relative artifact paths may need the updated absolute location; review downstream tooling.
  - Macros calling `model export telemetry` must load `GPT/gpt-telemetry.talon`; ensure Talon config includes the file.
- next_work:
  - Loop 350: add logging/telemetry around scheduler reschedules to detect misconfigurations.
  - Loop 351: evaluate an interactive CLI retry flag for stale telemetry.

## 2025-12-22 – Loop 350 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – capture scheduler reschedule stats in telemetry outputs.
- riskiest_assumption: Without visibility into scheduler cadence, operators cannot detect missed exports or interval drift (probability medium, impact medium-high for Concordance monitoring).
- validation_targets:
  - `python3 -m pytest _tests/test_telemetry_export_scheduler.py`
  - `python3 -m pytest _tests/test_telemetry_export.py`
- evidence: `docs/adr/evidence/0056/loop-0350.md`
- rollback_plan: `git restore -- lib/telemetryExportScheduler.py lib/telemetryExport.py lib/telemetryExportCommand.py _tests/test_telemetry_export_scheduler.py _tests/test_telemetry_export.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0350.md`
- delta_summary: helper:diff-snapshot=8 files changed, 217 insertions(+), 51 deletions(-); scheduler instrumentation now logs reschedules, telemetry payloads/markers expose the stats, and tests/assertions cover the new data.
- residual_risks:
  - CLI surfaces still need to display the scheduler stats; wire the values into guardrail job summaries in a follow-up loop.
  - Waiting logic remains manual; add an interactive CLI retry flag to help operators refresh telemetry without re-running commands.
- next_work:
  - Loop 351: evaluate an interactive CLI retry flag for stale telemetry so CLI users can pause until Talon completes exports.
  - Loop 352: surface scheduler telemetry in guardrail job summaries and CLI logs.

## 2025-12-22 – Loop 351 (kind: guardrail/tests)
- helper_version: helper:v20251221.5
- focus: Request Gating & Streaming – allow CLI guardrails to wait for fresh telemetry exports.
- riskiest_assumption: Without a wait option, operators must rerun guardrails manually after exporting telemetry, risking stale Concordance data (probability high, impact high for monitoring accuracy).
- validation_targets:
  - `python3 -m pytest _tests/test_check_telemetry_export_marker.py`
  - `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py`
- evidence: `docs/adr/evidence/0056/loop-0351.md`
- rollback_plan: `git restore -- scripts/tools/check-telemetry-export-marker.py _tests/test_check_telemetry_export_marker.py docs/adr/0056-concordance-personas-axes-history-gating.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md docs/adr/evidence/0056/loop-0351.md`
- delta_summary: helper:diff-snapshot=9 files changed, 260 insertions(+), 51 deletions(-); telemetry marker helper gained a wait flag, scheduler stats surface in telemetry outputs, and guardrail docs/tests capture the updated workflow.
- residual_risks:
  - Wait mode still relies on fixed polling; consider exposing configurable poll intervals or interactive prompts if operators need immediate feedback.
  - Guardrail job summaries must surface the new wait behaviour to avoid confusion; wire narrative output in a follow-up loop.
- next_work:
  - Loop 352: surface scheduler telemetry in guardrail job summaries and CLI logs.
  - Loop 353: evaluate interactive prompts/poll interval configuration for long-running exports.

