# ADR 0082 — UI dispatch fallback memory leak work log

## 2026-01-15 – Loop 1: inline dispatcher fallback (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullets 1–4 – keep `run_on_ui_thread` bounded when Talon cron scheduling fails and expose degraded-mode signal for callers/tests.
active_constraint: When Talon rejected `cron.after` the dispatcher logged and abandoned the queue, so background refresh callbacks accumulated unboundedly and memory ballooned; `_tests/test_ui_dispatch.py` reproduced the leak by asserting inline fallback behaviour and failed red against the current implementation.
expected_value:
  Impact: High – prevents multi-GB memory leaks during idle Talon sessions and keeps ADR 029’s main-thread guarantees intact.
  Probability: High – inline draining plus degraded-mode guardrails are directly exercised by the new tests.
  Time Sensitivity: Medium – operators continue to hit runaway memory growth on sleep/idle until the dispatcher is hardened.
  Uncertainty note: Low – change is local to the dispatcher and fully covered by deterministic unit tests.
validation_targets:
  - python3 -m pytest _tests/test_ui_dispatch.py

EVIDENCE
- red | 2026-01-15T20:27:22Z | exit 1 | python3 -m pytest _tests/test_ui_dispatch.py
    helper:diff-snapshot=
      _tests/test_ui_dispatch.py | 137 ++++++++++++++++++++++++++++++++-------------
    pointer: inline (AssertionError: [] is not true; cron failure dropped queued UI work)
- green | 2026-01-15T20:31:02Z | exit 0 | python3 -m pytest _tests/test_ui_dispatch.py
    helper:diff-snapshot=
      _tests/test_ui_dispatch.py | 137 ++++++++++++++++++++++++++++++++-------------
      lib/uiDispatch.py          |  78 +++++++++++++++++++++-----
    pointer: inline (dispatcher drains inline, probes recovery, and exposes degraded-mode flag)
- removal | 2026-01-15T20:28:06Z | exit 1 | git checkout origin/main -- lib/uiDispatch.py && python3 -m pytest _tests/test_ui_dispatch.py
    helper:diff-snapshot=
      _tests/test_ui_dispatch.py | 137 ++++++++++++++++++++++++++++++++-------------
    pointer: inline (reverting dispatcher reintroduces dropped queue and failing assertions)

rollback_plan: git restore --source=HEAD -- lib/uiDispatch.py _tests/test_ui_dispatch.py

delta_summary: helper:diff-snapshot=lib/uiDispatch.py | 78 +++++++++++++++++++++-----; _tests/test_ui_dispatch.py | 137 ++++++++++++++++++++++++++++++++-------------; added inline fallback drain with recovery probes, surfaced `ui_dispatch_fallback_active`, and expanded unit tests to cover failure, degraded, and recovery paths.

loops_remaining_forecast: 1 (confidence medium) – instrument degraded-mode logging/telemetry and document operator guidance once runtime soak confirms stability.

residual_constraints:
- severity: Medium | constraint: Degraded-mode warning only logs to debug; telemetry/alerting is still absent, so operators may miss prolonged fallback sessions. Mitigation: add counter/export in follow-up loop; monitor trigger: next guardrail sweep of Talon runtime logs; owning ADR: 0082.
- severity: Low | constraint: Extended in-Talon soak (overnight) with logging enabled still pending to confirm heap remains bounded. Mitigation: schedule pilot soak once patch lands; monitor trigger: first 12h idle run; owning ADR: 0082.

next_work:
- Behaviour: Wire degraded-mode telemetry/logging and update ADR guidance after soak; Validation: python3 -m pytest _tests/test_ui_dispatch.py

## 2026-01-15 – Loop 2: axis catalog cache (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Context + Implementation Notes – stop axisCatalog reload churn so dispatcher fallback remains bounded during canvas repaints.
active_constraint: Axis catalog reloads on every help canvas draw import `axisConfig` repeatedly, causing Skia resources to accumulate and heap usage to grow even when `_schedule_failed` drains inline; the constraint is red when `python3 -m pytest _tests/test_axis_catalog_reload.py` fails because `_axis_config_cache` is absent.
expected_value:
  Impact: High – removes the lingering memory growth driver that persisted after the dispatcher patch and keeps UI fallback bounded.
  Probability: Medium – caching by module path/mtime is local but depends on Talon loader semantics; the new regression test secures behaviour.
  Time Sensitivity: Medium – operators are still seeing overnight growth today, so eliminating the immediate churn is time-sensitive but not a hard deadline.
  Uncertainty note: Low – the code path is deterministic and covered by the regression harness.
validation_targets:
  - python3 -m pytest _tests/test_axis_catalog_reload.py

evidence:
- red | 2026-01-15T21:22:21Z | exit 1 | python3 -m pytest _tests/test_axis_catalog_reload.py
    helper:diff-snapshot captured in docs/adr/evidence/0082/loop-2.md#helper:diff-snapshot
    pointer: docs/adr/evidence/0082/loop-2.md#red
- green | 2026-01-15T21:22:49Z | exit 0 | python3 -m pytest _tests/test_axis_catalog_reload.py
    helper:diff-snapshot captured in docs/adr/evidence/0082/loop-2.md#helper:diff-snapshot
    pointer: docs/adr/evidence/0082/loop-2.md#green
- removal | 2026-01-15T21:23:03Z | exit 1 | git checkout -- lib/axisCatalog.py && python3 -m pytest _tests/test_axis_catalog_reload.py
    helper:diff-snapshot captured in docs/adr/evidence/0082/loop-2.md#helper:diff-snapshot
    pointer: docs/adr/evidence/0082/loop-2.md#removal

rollback_plan: git restore --source=HEAD -- lib/axisCatalog.py docs/adr/0082-ui-dispatch-fallback-memory-leak.md _tests/test_axis_catalog_reload.py

delta_summary: helper:diff-snapshot=docs/adr/0082-ui-dispatch-fallback-memory-leak.md | context/decision clarified with axisCatalog caching; lib/axisCatalog.py | +64 −13 adds path/mtime cache with lock + probe logic; _tests/test_axis_catalog_reload.py | +56 introduces regression ensuring reloads only occur on file changes.

loops_remaining_forecast: 1 (confidence medium) – wire degraded-mode telemetry counter and soak validation, then update ADR status to Accepted once logs stay bounded overnight.

residual_constraints:
- severity: Medium | constraint: Degraded-mode telemetry/alert still missing, so operators may not notice prolonged fallback; mitigation: add counter + Help Hub surface notice; monitor trigger: next consolidated Talon log review; owning ADR: 0082.
- severity: Low | constraint: Overnight soak (>=12h) with axis cache enabled still pending to confirm heap stability; mitigation: schedule pilot soak; monitor trigger: first overnight session; owning ADR: 0082.

next_work:
- Behaviour: Add telemetry counter + operator guidance for degraded mode; Validation: python3 -m pytest _tests/test_axis_catalog_reload.py && python3 -m pytest _tests/test_ui_dispatch.py
- Behaviour: Run overnight soak and capture memory telemetry; Validation: manual soak log with helper:rerun once data collected

## 2026-01-16 – Loop 3: degraded-mode telemetry (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 residual constraint “Degraded-mode telemetry/alert still missing” – expose dispatcher fallback metrics, surface operator notification, and add regression coverage.
active_constraint: Inline fallback counters were tracked privately and operators had no visibility when Talon cron rejected UI scheduling, so degraded sessions could persist silently and memory regressions were hard to diagnose. `_tests/test_ui_dispatch.py` lacked assertions to guarantee telemetry reset semantics.
expected_value:
  Impact: Medium – operators get immediate notification plus structured counters for guardrails.
  Probability: Medium – changes reuse existing dispatcher scaffolding and add focused unit coverage.
  Time Sensitivity: High – degraded-mode ops remain blind until telemetry lands.
  Uncertainty note: Low – scope is isolated to dispatcher helpers.
validation_targets:
  - python3 -m pytest _tests/test_ui_dispatch.py

evidence:
- blocked | 2026-01-16T08:36:12Z | exit 1 | python3 -m pytest _tests/test_ui_dispatch.py
    pointer: python3.14 environment lacks pytest module; rerun once dependencies restored.

rollback_plan: git restore --source=HEAD -- lib/uiDispatch.py _tests/test_ui_dispatch.py docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=lib/uiDispatch.py | +146 −13 adds operator notification, inline telemetry snapshot helper, and fallback reset plumbing; _tests/test_ui_dispatch.py | +74 −2 resets inline counters in harness and covers `ui_dispatch_inline_stats`; docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md | +24 documents telemetry loop and blocked test run.

loops_remaining_forecast: 1 (confidence medium) – schedule overnight soak once pytest environment restored so telemetry/export paths can be validated end-to-end.

residual_constraints:
- severity: Medium | constraint: Guardrail telemetry export not yet validated; mitigation: rerun `_tests/test_ui_dispatch.py` after pytest restoration and add history telemetry snapshot smoke once environment permits.
- severity: Medium | constraint: Operator guidance still needs Help Hub copy post-soak; mitigation: draft Help Hub notice after telemetry soak completes; monitor trigger: first overnight session using new counters.

next_work:
- Behaviour: Restore pytest environment and rerun `_tests/test_ui_dispatch.py`; Validation: python3 -m pytest _tests/test_ui_dispatch.py
- Behaviour: Capture overnight soak metrics with new telemetry; Validation: manual soak log with helper:rerun once data collected

## 2026-01-17 – Loop 4: export dispatcher fallback stats (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 – add dispatcher degraded-mode telemetry to the guardrail export so operators can spot inline fallback in artifacts.
active_constraint: Telemetry snapshots omitted `ui_dispatch_inline_stats`, leaving `artifacts/telemetry/*.json` blind to degraded dispatcher sessions; `_tests/test_telemetry_export.py` fails when asserting the inline fallback payload.
expected_value:
  Impact: High – guardrail exports now surface dispatcher degradation for operators running manual snapshots.
  Probability: High – wiring the export to reuse the dispatcher stats helper deterministically satisfies the regression test.
  Time Sensitivity: Medium – telemetry exports happen during operations; missing data delays leak detection but is recoverable within the release window.
  Uncertainty note: Low – scope is limited to JSON serialization of existing counters with unit coverage.
validation_targets:
  - python3 -m pytest _tests/test_telemetry_export.py

evidence:
- red | 2026-01-17T22:28:03Z | exit 1 | python3 -m pytest _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-4.md#red
- green | 2026-01-17T22:28:17Z | exit 0 | python3 -m pytest _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-4.md#green
- removal | 2026-01-17T22:28:26Z | exit 1 | git checkout -- lib/telemetryExport.py && python3 -m pytest _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-4.md#removal

rollback_plan: git restore --source=HEAD -- lib/telemetryExport.py _tests/test_telemetry_export.py docs/adr/evidence/0082/loop-4.md docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=docs/adr/evidence/0082/loop-4.md#helper:diff-snapshot; added `_fetch_ui_dispatch_inline_stats()` and exported its payload in `snapshot_telemetry`, extending `_tests/test_telemetry_export.py` to cover the inline fallback artefact; appended stack-logged leaks evidence confirming Skia text blob retention.

loops_remaining_forecast: 1 (confidence medium) – run overnight soak with the new telemetry artefacts and update operator guidance before marking ADR 0082 accepted.

residual_constraints:
- severity: Medium | constraint: Overnight idle soak (>12h) with inline fallback telemetry captured remains pending; mitigation: schedule soak now that exports include dispatcher stats and leak evidence (`docs/adr/evidence/0082/loop-4.md`) points to Talon-held IOSurface tiles and Skia text blobs; monitor trigger: first post-loop overnight session; owning ADR: 0082.
- severity: Low | constraint: Help Hub copy still needs to reference the new dispatcher fallback telemetry counters; mitigation: draft guidance after soak data reviewed; monitor trigger: guardrail review queue.

## 2026-01-17 – Loop 5: cache Skia typefaces and emoji segments (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 – stop dispatcher fallback from leaking Skia text resources by caching typefaces and emoji segment plans in canvas rendering helpers.
active_constraint: Response/help canvases rebuilt Skia typefaces and text runs on every inline drain, causing `sk_textblob_builder_alloc_run` to leak and `_tests/test_canvas_font.py` fails when asserting reuse of dispatcher font resources.
expected_value:
  Impact: High – stabilises UI dispatcher memory footprint during fallback by preventing per-frame Skia allocations.
  Probability: High – caching helpers are exercised directly by updated unit tests and reused across canvases.
  Time Sensitivity: High – leak manifests within a single idle session; shipping caches immediately prevents further runaway sessions.
  Uncertainty note: Medium – assumes SkiaSharp reuses cached typeface objects when reused across draws; telemetry soak will confirm.
validation_targets:
  - python3 -m pytest _tests/test_canvas_font.py

evidence:
- red | 2026-01-17T23:20:11Z | exit 1 | python3 -m pytest _tests/test_canvas_font.py
    pointer: docs/adr/evidence/0082/loop-5.md#red
- green | 2026-01-17T23:20:48Z | exit 0 | python3 -m pytest _tests/test_canvas_font.py
    pointer: docs/adr/evidence/0082/loop-5.md#green
- removal | 2026-01-17T23:21:16Z | exit 1 | git checkout -- lib/canvasFont.py && python3 -m pytest _tests/test_canvas_font.py
    pointer: docs/adr/evidence/0082/loop-5.md#removal

rollback_plan: git restore --source=HEAD -- lib/canvasFont.py _tests/stubs/talon/__init__.py _tests/test_canvas_font.py docs/adr/evidence/0082/loop-5.md docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=docs/adr/evidence/0082/loop-5.md#helper:diff-snapshot; cached Skia typefaces and emoji render plans, added reset helper for tests, extended Talon stubs with instrumentation, and codified caching regressions via `_tests/test_canvas_font.py`.

loops_remaining_forecast: 2 (confidence medium) – validate overnight soak under inline fallback and update degraded-mode operator guidance before closing ADR 0082.

residual_constraints:
- severity: Medium | constraint: Overnight idle soak (>12h) with inline fallback telemetry captured remains pending; mitigation: schedule soak now that dispatcher caches land; monitor trigger: first post-loop overnight session; owning ADR: 0082.
- severity: Low | constraint: Help Hub copy still needs to reference the new dispatcher fallback telemetry counters and caching behaviour; mitigation: draft guidance after soak data reviewed; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Run overnight soak and capture dispatcher telemetry artefacts; Validation: manual soak log with helper:rerun once data collected
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)
- Behaviour: Use telemetry export snapshots to correlate inline fallback with canvas stats; Validation: python3 -m pytest _tests/test_telemetry_export.py && model export telemetry artefact review

## 2026-01-19 – Loop 6: instrument canvas font telemetry (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullets 3–4 – expose dispatcher fallback render activity through canvas font counters so telemetry exports capture Skia churn during inline drains.
active_constraint: Telemetry exports and tests could not observe Skia text cache behaviour; `_tests/test_canvas_font.py` failed once the new stats API was referenced because `canvas_font_stats` and dispatcher wiring were absent.
expected_value:
  Impact: High – operators gain in-session visibility into text rendering churn, enabling quicker detection of fallback-induced leaks.
  Probability: High – adding counters inside `canvasFont` and plumbing them through `ui_dispatch_inline_stats` deterministically satisfies the new regression tests.
  Time Sensitivity: Medium – instrumentation is needed before long-running soaks so data collection isn’t blocked, but one loop delay is tolerable.
  Uncertainty note: Medium – assumes the counters track real-world Skia activity; overnight soak will validate correlation.
validation_targets:
  - python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py

evidence:
- red | 2026-01-19T02:31:13Z | exit 1 | python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-6.md#red
- green | 2026-01-19T02:31:55Z | exit 0 | python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-6.md#green
- removal | 2026-01-19T02:32:30Z | exit 1 | python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py
    pointer: docs/adr/evidence/0082/loop-6.md#removal

rollback_plan: git restore --source=HEAD -- lib/canvasFont.py lib/telemetryExport.py lib/uiDispatch.py _tests/test_canvas_font.py _tests/test_telemetry_export.py docs/adr/evidence/0082/loop-6.md docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=docs/adr/evidence/0082/loop-6.md#helper:diff-snapshot; added `canvas_font_stats()` instrumentation and counters, threaded stats into `ui_dispatch_inline_stats`, exported sanitized payloads in telemetry snapshots, and extended regression tests to assert counter availability.

loops_remaining_forecast: 2 (confidence medium) – run the overnight soak with telemetry counters and update operator guidance before flipping ADR 0082 to Accepted.

residual_constraints:
- severity: Medium | constraint: Overnight idle soak (>12h) with inline fallback telemetry captured remains pending; mitigation: schedule soak now that dispatcher stats are exported; monitor trigger: first post-loop overnight session; owning ADR: 0082.
- severity: Low | constraint: Help Hub copy still needs to reference the new dispatcher fallback telemetry counters and usage guidance; mitigation: draft guidance after soak data reviewed; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Run overnight soak and capture dispatcher telemetry artefacts; Validation: manual soak log with helper:rerun once data collected
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)
- Behaviour: Use telemetry export snapshots to correlate inline fallback with canvas stats; Validation: python3 -m pytest _tests/test_telemetry_export.py && model export telemetry artefact review

## 2026-01-19 – Loop 7: lazily create/destroy pill canvas (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 – ensure the pill dispatcher surface only holds Skia resources while a request is active.
active_constraint: Pill cron warm-up kept the canvas alive and `_tests/test_pill_canvas.py` failed because `hide_pill` never closed the canvas, leaving idle sessions to retain Skia allocations.
expected_value:
  Impact: High – removing cron and releasing canvases immediately prevents background Skia churn when Talon is idle.
  Probability: High – tests cover show/hide flows directly.
  Time Sensitivity: Medium – mitigates rapid idle leaks while leaving time for downstream soak validation.
  Uncertainty note: Medium – will validate with overnight leaks/telemetry run.
validation_targets:
  - python3 -m pytest _tests/test_pill_canvas.py

evidence:
- red | 2026-01-19T04:20:48Z | exit 1 | python3 -m pytest _tests/test_pill_canvas.py
    pointer: docs/adr/evidence/0082/loop-7.md#red
- green | 2026-01-19T04:22:15Z | exit 0 | python3 -m pytest _tests/test_pill_canvas.py
    pointer: docs/adr/evidence/0082/loop-7.md#green
- removal | 2026-01-19T04:23:03Z | exit 1 | python3 -m pytest _tests/test_pill_canvas.py
    pointer: docs/adr/evidence/0082/loop-7.md#removal

rollback_plan: git restore --source=HEAD -- lib/pillCanvas.py _tests/test_pill_canvas.py docs/adr/evidence/0082/loop-7.md docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=docs/adr/evidence/0082/loop-7.md#helper:diff-snapshot; removed cron warm-up, switched `show_pill` to lazy creation, and made `hide_pill` release the canvas immediately.

loops_remaining_forecast: 2 (confidence medium) – run the overnight soak with dispatcher telemetry and update operator guidance before marking ADR 0082 Accepted.

residual_constraints:
- severity: Medium | constraint: Overnight idle soak (>12h) with inline fallback telemetry captured remains pending; mitigation: run soak with the revised pill lifecycle and review telemetry/leaks (`docs/adr/evidence/0082/loop-7.md`); monitor trigger: first post-loop overnight session; owning ADR: 0082.
- severity: Low | constraint: Help Hub copy still needs to reference the new dispatcher fallback telemetry counters and usage guidance; mitigation: draft guidance after soak data reviewed; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Run overnight soak and capture dispatcher telemetry artefacts; Validation: manual soak log with helper:rerun once data collected
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)
- Behaviour: Use telemetry export snapshots to correlate inline fallback with canvas stats; Validation: python3 -m pytest _tests/test_telemetry_export.py && model export telemetry artefact review

## 2026-01-19 – Loop 8: history drawer canvas release ordering (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 & residual constraint “Overnight idle soak” – ensure request history drawer releases its canvas the same way as other overlays so inline fallback doesn’t drop pending hide handlers and the new regression stays green.
active_constraint: `_release_history_canvas` set the module-level reference to `None` before the Talon canvas could invoke `hide`, so `_tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_close_allows_inflight` failed (red) and inline fallback left stale handlers, letting the drawer leak Skia objects across requests.
expected_value:
  Impact: Medium – keeps history drawer lifecycle aligned with other overlays, closing a remaining leak vector before the overnight soak.
  Probability: High – the targeted regression test and overlay suite deterministically cover the new ordering.
  Time Sensitivity: Medium – overnight soak depends on all canvases releasing cleanly; letting this linger would skew telemetry.
  Uncertainty note: Low – change is confined to overlay helpers and validated via unit tests.
validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_close_allows_inflight
  - python3 -m pytest _tests/test_model_response_canvas.py _tests/test_model_help_canvas.py _tests/test_model_suggestion_gui.py _tests/test_model_pattern_gui.py _tests/test_prompt_pattern_gui.py

evidence:
- red | 2026-01-19T05:49:12Z | exit 1 | python3 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_close_allows_inflight
    helper:diff-snapshot=lib/requestHistoryDrawer.py | 11 +++++----
    pointer: inline (hide was never invoked once `_history_canvas` dropped to `None` ahead of the MagicMock handler)
- green | 2026-01-19T05:52:04Z | exit 0 | python3 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_close_allows_inflight
    helper:diff-snapshot=lib/requestHistoryDrawer.py | 11 +++++----
    pointer: inline (hide now runs before the reference is cleared, keeping the test green)
- removal | 2026-01-19T05:53:18Z | exit 1 | python3 -m pytest _tests/test_request_history_drawer.py::RequestHistoryDrawerTests::test_history_drawer_close_allows_inflight
    helper:diff-snapshot=lib/requestHistoryDrawer.py | 11 +++++----
    pointer: inline (reverting to close-first ordering drops hide again and recreates the failure)
- green | 2026-01-19T05:54:26Z | exit 0 | python3 -m pytest _tests/test_model_response_canvas.py _tests/test_model_help_canvas.py _tests/test_model_suggestion_gui.py _tests/test_model_pattern_gui.py _tests/test_prompt_pattern_gui.py
    helper:diff-snapshot=lib/helpHub.py | 22 ++++++++----; lib/modelHelpCanvas.py | 36 +++++++++++-----; lib/modelPatternGUI.py | 27 ++++++++----; lib/modelPromptPatternGUI.py | 23 ++++++----; lib/modelResponseCanvas.py | 42 ++++++++++------; lib/modelSuggestionGUI.py | 52 +++++++++++++-----; lib/providerCanvas.py | 11 +++++-

rollback_plan: git restore --source=HEAD -- lib/helpHub.py lib/modelHelpCanvas.py lib/modelPatternGUI.py lib/modelPromptPatternGUI.py lib/modelResponseCanvas.py lib/modelSuggestionGUI.py lib/providerCanvas.py lib/requestHistoryDrawer.py _tests/test_request_history_drawer.py docs/adr/0082-ui-dispatch-fallback-memory-leak.work-log.md

delta_summary: helper:diff-snapshot=lib/requestHistoryDrawer.py | 33 +++++++++++++++++++++++-----; lib/helpHub.py | 22 +++++++++++++++----; lib/modelHelpCanvas.py | 36 +++++++++++++++++++-----------; lib/modelPatternGUI.py | 27 +++++++++++++++++------; lib/modelPromptPatternGUI.py | 23 ++++++++++++++++----; lib/modelResponseCanvas.py | 42 ++++++++++++++++++++---------------; lib/modelSuggestionGUI.py | 52 ++++++++++++++++++++++++++++++--------------; lib/providerCanvas.py | 11 +++++++++-

loops_remaining_forecast: 2 (confidence medium) – run the overnight soak with the telemetry counters and publish Help Hub guidance before marking ADR 0082 Accepted.

residual_constraints:
- severity: Medium | constraint: Overnight idle soak (>12h) with dispatcher telemetry and canvas font stats remains pending; mitigation: schedule soak now that all canvases share the release helper; monitor trigger: next idle session; owning ADR: 0082.
- severity: Low | constraint: Help Hub degraded-mode guidance still needs the dispatcher fallback copy and telemetry pointers; mitigation: draft after soak review; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Run overnight soak and capture dispatcher telemetry artefacts (`leaks <talon-pid>` plus user.model_export_telemetry()); Validation: helper:rerun python3 -m pytest _tests/test_telemetry_export.py after soak data lands
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)
- Behaviour: Correlate dispatcher inline stats with canvas font counters via telemetry export; Validation: python3 -m pytest _tests/test_telemetry_export.py && user.model_export_telemetry()
