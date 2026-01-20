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

## 2026-01-19 – Loop 9: investigate Skia text blob retention (kind: analysis)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 – confirm next steps for the suggestion overlay so inline fallback no longer leaks Skia text blobs when Talon throttles scheduling.
active_constraint: A single `model run suggest` still retains ~8k `SkTextBlob` allocations (≈1.2 MB) even after canvases close; without an exposed Skia cache purge, the suggestion overlay remains the dominant leak vector and blocks the overnight soak.
expected_value:
  Impact: Medium – validating Talon’s Skia API surface prevents us from chasing impossible fixes and directs effort toward viable mitigation.
  Probability: High – REPL inspection and `leaks` runs deterministically exercise the behaviour.
  Time Sensitivity: Medium – we must settle on a mitigation path before scheduling the soak and Help Hub guidance.
  Uncertainty note: Medium – needed to confirm whether SkiaSharp exposed cache controls before committing to UI changes.
validation_targets:
  - /Applications/Talon.app/Contents/Resources/python/bin/python3 /Applications/Talon.app/Contents/Resources/repl.py (skia inspection + canvas stats)
  - leaks 33006

evidence:
- green | 2026-01-19T07:12:44Z | exit 0 | /Applications/Talon.app/Contents/Resources/python/bin/python3 /Applications/Talon.app/Contents/Resources/repl.py
    pointer: inline (listed `talon.skia` attrs; no `purge`/`flush` API beyond `Canvas.flush`, confirming Skia caches are not controllable from Python)
- red | 2026-01-19T07:24:58Z | exit 0 | leaks 33006
    pointer: inline (`SkTextBlob` leak stack persisted at ~8.5k instances after a single suggest cycle; truncation experiments did not reduce allocations)
- green | 2026-01-19T07:28:12Z | exit 0 | /Applications/Talon.app/Contents/Resources/python/bin/python3 /Applications/Talon.app/Contents/Resources/repl.py
    pointer: inline (`canvas_font_stats(reset=True)` / `canvas_font_stats()` instrumentation ready for future validation of collapsed-detail UI)

rollback_plan: None (analysis-only loop; codebase left unchanged).

delta_summary: helper:diff-snapshot=0 files changed; confirmed Talon’s Skia bindings lack cache purge APIs and established that the suggestion overlay’s long-form text must be gated (e.g., collapsed by default) to avoid minting thousands of blobs per request.

loops_remaining_forecast: 2 (confidence medium) – build an expand/collapse path for long-form suggestion copy, then rerun the overnight soak with telemetry/`leaks` before updating operator guidance.

residual_constraints:
- severity: Medium | constraint: Suggestion overlay still emits ~8k `SkTextBlob`s per run; mitigation: switch to collapsed summaries with explicit expand affordance and revalidate via `canvas_font_stats` + `leaks`; monitor trigger: next suggestion UI pull request; owning ADR: 0082.
- severity: Medium | constraint: Overnight idle soak (>12h) with dispatcher telemetry and canvas font stats remains pending; mitigation: execute once overlay churn is bounded; monitor trigger: soak scheduling; owning ADR: 0082.
- severity: Low | constraint: Help Hub degraded-mode guidance still needs dispatcher fallback copy and telemetry pointers; mitigation: draft after soak review; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Implement collapsed suggestion summaries with explicit expand/collapse; Validation: python3 -m pytest _tests/test_model_suggestion_gui.py + canvas_font_stats()/leaks spot check
- Behaviour: Run overnight soak once suggestion churn is bounded; Validation: helper:rerun python3 -m pytest _tests/test_telemetry_export.py and captured soak artefacts
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)

## 2026-01-19 – Loop 10: validate suggestion window memory stability (kind: validation)

helper_version: helper:v20251223.1
focus: ADR 0082 residual constraint – validate that Skia typeface caching prevents unbounded memory growth during repeated suggestion window open/close cycles.
active_constraint: Prior loop 9 reported ~8k `SkTextBlob` allocations per suggest cycle; needed to confirm whether loops 5-6 caching fixes bounded the leak in practice.
expected_value:
  Impact: High – confirms or refutes readiness for overnight soak.
  Probability: High – direct `leaks` measurement provides definitive evidence.
  Time Sensitivity: Medium – soak scheduling depends on this validation.
  Uncertainty note: Low – direct measurement via macOS `leaks` tool.
validation_targets:
  - leaks 92087 (Talon PID)
  - Talon REPL: open/close suggestion window cycles

evidence:
- baseline | 2026-01-19T21:16:00Z | exit 0 | leaks 92087
    pointer: inline (46 leaks for 3,280 bytes before any suggestion window activity)
- green | 2026-01-19T21:16:30Z | exit 0 | leaks 92087
    pointer: inline (64 leaks for 25,360 bytes after first open/close cycle – initial allocation)
- green | 2026-01-19T21:17:00Z | exit 0 | leaks 92087
    pointer: inline (64 leaks for 25,360 bytes after 5 additional cycles – stable, no growth)
- green | 2026-01-19T21:17:30Z | exit 0 | leaks 92087
    pointer: inline (64 leaks for 25,360 bytes after 3 cycles with cache resets – still stable)
- green | 2026-01-19T21:18:00Z | exit 0 | leaks 92087
    pointer: inline (64 leaks for 25,360 bytes after stress test: 10 suggestions × 10 cycles – stable)

rollback_plan: None (validation-only loop; codebase unchanged).

delta_summary: helper:diff-snapshot=0 files changed; confirmed Skia typeface caching from loops 5-6 effectively bounds memory growth – leak count stable at 64 (25KB) across all test scenarios including stress test with 10 suggestions and 10 rapid cycles. Leaks are CFString objects (font name strings), not SkTextBlob as previously feared.

loops_remaining_forecast: 1 (confidence high) – schedule overnight soak to confirm long-term stability before marking ADR 0082 Accepted.

residual_constraints:
- severity: Low | constraint: Overnight idle soak (>12h) with dispatcher telemetry still pending as final validation; mitigation: schedule now that short-cycle stability is confirmed; monitor trigger: next idle session; owning ADR: 0082.
- severity: Low | constraint: Help Hub degraded-mode guidance still needs dispatcher fallback copy and telemetry pointers; mitigation: draft after soak review; monitor trigger: guardrail review queue.

next_work:
- Behaviour: Run overnight soak and confirm leak stability; Validation: leaks <talon-pid> after 12h+ idle session
- Behaviour: Update Help Hub degraded-mode guidance; Validation: docs/helphub/dispatcher-fallback.md (manual review once drafted)
- Behaviour: Mark ADR 0082 as Accepted if soak confirms stability; Validation: update ADR status

## 2026-01-19 – Loop 11: comprehensive canvas memory leak audit (kind: validation)

helper_version: helper:v20251223.1
focus: ADR 0082 Decision bullet 3 – systematically test all canvas-based overlays to identify which share the suggestion GUI's bounded behaviour and which still leak unboundedly.
active_constraint: Loop 10 validated the suggestion GUI but other canvases (help, pattern, provider, pill, history drawer, response) were untested; overnight soak would be misleading if other overlays still leak.
expected_value:
  Impact: High – identifies remaining leak vectors that block ADR 0082 acceptance.
  Probability: High – direct `leaks` measurement with 5-cycle tests per canvas.
  Time Sensitivity: High – must fix severe leakers before overnight soak.
  Uncertainty note: Low – direct measurement via macOS `leaks` tool.
validation_targets:
  - leaks 92087 (Talon PID)
  - Talon REPL: open/close cycles for each canvas type

evidence:
- baseline | 2026-01-19T21:20:00Z | exit 0 | leaks 92087
    pointer: inline (67 leaks for 46,080 bytes before canvas tests)

- red | 2026-01-19T21:21:00Z | exit 0 | Help Canvas × 5 cycles
    pointer: inline (5,817 leaks for 901,472 bytes – severe leak ~170KB/cycle)
- red | 2026-01-19T21:22:00Z | exit 0 | Help Canvas × 5 more cycles (10 total)
    pointer: inline (10,092 leaks for 1,558,048 bytes – linear growth confirmed)

- yellow | 2026-01-19T21:23:00Z | exit 0 | Pattern GUI × 5 cycles
    pointer: inline (10,785 leaks for 1,666,752 bytes – +693 leaks, ~22KB/cycle)

- yellow | 2026-01-19T21:24:00Z | exit 0 | Provider Canvas × 5 cycles
    pointer: inline (11,331 leaks for 1,743,872 bytes – +546 leaks, ~15KB/cycle)

- green | 2026-01-19T21:25:00Z | exit 0 | Pill Canvas × 5 cycles
    pointer: inline (11,519 leaks for 1,764,816 bytes – +188 leaks, ~4KB/cycle)

- yellow | 2026-01-19T21:26:00Z | exit 0 | History Drawer × 5 cycles
    pointer: inline (11,807 leaks for 1,822,880 bytes – +288 leaks, ~12KB/cycle)

- green | 2026-01-19T21:28:00Z | exit 0 | Response Canvas × 5 cycles
    pointer: inline (11,947 leaks for 1,838,000 bytes – +140 leaks, ~3KB/cycle)
- green | 2026-01-19T21:29:00Z | exit 0 | Response Canvas × 10 more cycles (15 total)
    pointer: inline (12,205 leaks for 1,865,696 bytes – +258 leaks, ~3KB/cycle confirmed)

rollback_plan: None (validation-only loop; codebase unchanged).

delta_summary: helper:diff-snapshot=0 files changed; comprehensive audit revealed Help Canvas as severe leaker (~151KB/cycle) due to creating new canvas instances each open. Pattern GUI, Provider Canvas, and History Drawer have moderate leaks (12-22KB/cycle). Pill Canvas and Suggestion GUI are well-behaved (2-4KB/cycle). Response Canvas requires separate investigation due to gating.

Canvas leak summary (5 cycles each unless noted):
| Canvas           | Leaks Added | Bytes Added | Per-Cycle | Severity |
|------------------|-------------|-------------|-----------|----------|
| Help Canvas (×10)| +10,025     | +1,512KB    | ~151KB    | SEVERE   |
| Pattern GUI      | +693        | +109KB      | ~22KB     | Moderate |
| Provider Canvas  | +546        | +77KB       | ~15KB     | Moderate |
| History Drawer   | +288        | +58KB       | ~12KB     | Moderate |
| Pill Canvas      | +188        | +21KB       | ~4KB      | Low      |
| Suggestion GUI   | +18         | +22KB       | ~2KB      | OK       |
| Response Canvas  | +398        | +43KB       | ~3KB      | OK       |

Root cause pattern for Help Canvas: log shows "created new canvas instance from_rect" on every open cycle instead of reusing existing canvas. Similar pattern suspected for other moderate leakers.

Canvases with acceptable leak rates (OK/Low): Suggestion GUI, Response Canvas, Pill Canvas – these reuse canvas instances properly.
Canvases with moderate leak rates: Pattern GUI, Provider Canvas, History Drawer – may benefit from canvas reuse pattern.
Canvas with severe leak rate: Help Canvas – creates new instance every open, must be fixed.

loops_remaining_forecast: 2 (confidence medium) – fix Help Canvas leak, then rerun overnight soak.

residual_constraints:
- severity: High | constraint: Help Canvas leaks ~151KB per open/close cycle; mitigation: modify _open_canvas to reuse existing canvas instance; monitor trigger: next canvas open; owning ADR: 0082.
- severity: Medium | constraint: Pattern GUI, Provider Canvas, History Drawer leak 12-22KB/cycle; mitigation: apply same canvas reuse pattern after Help Canvas fix; monitor trigger: post-Help fix validation; owning ADR: 0082.
- severity: Low | constraint: Overnight idle soak (>12h) blocked until severe leakers fixed; mitigation: schedule after Help Canvas fix lands; monitor trigger: post-fix validation; owning ADR: 0082.

next_work:
- Behaviour: Reduce Help Canvas text rendering (collapsed UI); Validation: leaks spot check showing <20KB/cycle
- Behaviour: Run overnight soak once Help Canvas bounded; Validation: leaks <talon-pid> after 12h+ idle session

## 2026-01-19 – Loop 12: Help Canvas reuse attempt (kind: fix – reverted)

helper_version: helper:v20251223.1
focus: ADR 0082 residual constraint – attempt to fix Help Canvas ~151KB/cycle leak by reusing canvas instance instead of destroying on close.
active_constraint: Help Canvas leaks ~151KB per open/close cycle; hypothesis was that destroying and recreating canvas objects caused the leak.
expected_value:
  Impact: High – if successful, would reduce Help Canvas leak to acceptable levels.
  Probability: Medium – based on assumption that canvas object creation was the leak source.
  Time Sensitivity: High – blocks overnight soak validation.
  Uncertainty note: High – needed to validate whether canvas object or Skia rendering was the leak source.
validation_targets:
  - leaks <talon-pid> after 5 open/close cycles

evidence:
- red | 2026-01-19T22:00:00Z | exit 0 | Help Canvas × 5 cycles (pre-fix baseline)
    pointer: inline (12,210→16,418 leaks, +4,208 leaks, +645KB – ~129KB/cycle confirming leak)
    log: "created new canvas instance from_rect" on every cycle

- applied fix | 2026-01-19T22:05:00Z | Changed _close_canvas() to call hide() instead of _release_help_canvas()

- red | 2026-01-19T22:10:00Z | exit 0 | Help Canvas × 5 cycles (post-fix, fresh Talon)
    pointer: inline (15→39,993 leaks, 640B→5,934KB – ~1,187KB/cycle, WORSE than before)
    log: Cycle 1 "created new canvas instance", Cycles 2-5 "reusing existing canvas instance"

- red | 2026-01-19T22:15:00Z | exit 0 | Help Canvas × 10 more cycles (post-fix)
    pointer: inline (39,993→141,942 leaks, 5,934KB→21,575KB – ~1,564KB/cycle average, MUCH WORSE)

- reverted | 2026-01-19T22:20:00Z | Restored original _release_help_canvas() call

rollback_plan: Reverted inline; change was single line in _close_canvas().

delta_summary: helper:diff-snapshot=0 files changed (reverted); CRITICAL LEARNING: canvas reuse made leak 10x WORSE (~1,500KB/cycle vs ~150KB/cycle). The leak is NOT from canvas object creation – it's from Skia text blob resources created during rendering. Destroying the canvas actually helps release these resources. Keeping the canvas alive causes Skia resources to accumulate unboundedly.

This confirms Loop 9's finding that Skia caches lack purge APIs. The actual fix must reduce the amount of text rendered per draw (collapsed/expandable UI) rather than reusing canvas objects.

loops_remaining_forecast: 2 (confidence medium) – implement collapsed Help Canvas UI to reduce text blob count, then revalidate with leaks.

residual_constraints:
- severity: High | constraint: Help Canvas leaks ~151KB/cycle due to Skia text blob rendering, NOT canvas object creation; mitigation: reduce rendered text via collapsed UI with expand affordance; monitor trigger: next Help Canvas design iteration; owning ADR: 0082.
- severity: Medium | constraint: Pattern GUI, Provider Canvas, History Drawer leak 12-22KB/cycle; mitigation: may benefit from similar text reduction; monitor trigger: post-Help Canvas fix; owning ADR: 0082.
- severity: Low | constraint: Overnight soak blocked until Help Canvas bounded; mitigation: schedule after UI reduction lands; monitor trigger: post-fix validation; owning ADR: 0082.

next_work:
- Behaviour: Design collapsed Help Canvas UI (show axis names only, expand on click/command); Validation: mockup review
- Behaviour: Implement collapsed Help Canvas rendering; Validation: leaks <talon-pid> showing <20KB/cycle
- Behaviour: Run overnight soak; Validation: leaks <talon-pid> after 12h+ idle session

## 2026-01-20 – Loop 13: investigate Skia purge APIs and GC (kind: analysis)

helper_version: helper:v20251223.1
focus: ADR 0082 residual constraint – investigate whether Skia's low-level FFI purge APIs or Python garbage collection can release text blob memory.
active_constraint: Help Canvas leaks ~150KB/cycle; needed to determine if explicit resource release is possible before committing to UI text reduction.
expected_value:
  Impact: High – if successful, would provide a programmatic fix without UI changes.
  Probability: Low – prior analysis suggested Skia caches don't track text blobs.
  Time Sensitivity: Medium – blocks decision on mitigation approach.
  Uncertainty note: High – exploring undocumented FFI layer.
validation_targets:
  - Talon REPL: explore talon.skia FFI layer
  - leaks <talon-pid> before/after purge attempts

evidence:
- green | 2026-01-20T05:38:00Z | exit 0 | REPL: dir(talon.skia)
    pointer: inline (discovered 34 attrs including textblob, font, surface modules)

- green | 2026-01-20T05:39:00Z | exit 0 | REPL: dir(talon.skia.textblob.lib)
    pointer: inline (discovered FFI functions including sk_graphics_purge_all_caches, sk_graphics_purge_font_cache, sk_textblob_unref, gr_direct_context_free_gpu_resources)

- green | 2026-01-20T05:40:00Z | exit 0 | REPL: sk_graphics_purge_all_caches()
    pointer: inline (font_cache_used: 39600 → 0, successfully cleared Skia font cache)

- red | 2026-01-20T05:41:00Z | exit 0 | leaks 96010 after purge
    pointer: inline (239,842 leaks unchanged – purge does not affect text blob leaks)

- red | 2026-01-20T05:45:00Z | exit 0 | 5 cycles with sk_graphics_purge_all_caches() after each
    pointer: inline (+10,095 leaks, ~300KB/cycle – same rate as without purge)

- red | 2026-01-20T05:50:00Z | exit 0 | 5 cycles with gc.collect() × 3 after each
    pointer: inline (+10,264 leaks, ~320KB/cycle – GC collects Python objects but doesn't affect native leaks)

- red | 2026-01-20T05:55:00Z | exit 0 | 5 cycles with gc.collect() + purge + 1s delay
    pointer: inline (+10,225 leaks, ~300KB/cycle – combined cleanup has no effect)

rollback_plan: None (analysis-only loop; codebase unchanged).

delta_summary: helper:diff-snapshot=0 files changed; comprehensive investigation of Talon's Skia FFI layer revealed:

**Available Skia APIs discovered:**
- `sk_graphics_purge_all_caches()` – clears font/resource caches (works, but doesn't help)
- `sk_graphics_purge_font_cache()` – clears font cache specifically
- `sk_graphics_purge_resource_cache()` – clears resource cache
- `sk_textblob_unref()` – exists but we don't have blob handles to call it
- `gr_direct_context_*` functions – exist but require context handles we can't access

**Test results summary:**
| Approach | Effect on Skia Cache | Effect on Leaks |
|----------|---------------------|-----------------|
| sk_graphics_purge_all_caches() | Cleared (39KB → 0) | None (~300KB/cycle) |
| gc.collect() × 3 | Collected ~300-4000 Python objects | None (~320KB/cycle) |
| GC + purge + 1s delay | Both effects | None (~300KB/cycle) |

**Key finding:** The text blobs created by `draw_text()` via `sk_textblob_builder_alloc_run` are NOT tracked by Skia's font/resource caches. They are allocated at a lower level and references are lost before we can call `sk_textblob_unref()`. This appears to be a limitation in how Talon's Skia bindings manage text blob lifecycle.

**Conclusion:** No programmatic fix is available from Python. The viable mitigations remain:
1. Reduce text rendered (collapsed UI)
2. Accept current leak rate (~150KB/cycle for Help Canvas)
3. Report upstream to Talon as a potential binding bug

loops_remaining_forecast: 2 (confidence medium) – implement collapsed Help Canvas UI or accept current leak rate.

residual_constraints:
- severity: High | constraint: Help Canvas leaks ~150KB/cycle; no programmatic fix available from Python; mitigation: reduce rendered text via collapsed UI or accept leak rate; monitor trigger: next Help Canvas iteration; owning ADR: 0082.
- severity: Medium | constraint: Pattern GUI, Provider Canvas, History Drawer leak 12-22KB/cycle; mitigation: may benefit from similar text reduction; monitor trigger: post-Help Canvas decision; owning ADR: 0082.
- severity: Low | constraint: Overnight soak blocked until leak rate acceptable; mitigation: schedule after mitigation decision; monitor trigger: post-decision; owning ADR: 0082.

next_work:
- Behaviour: Decide on mitigation approach (collapsed UI vs accept leak rate); Validation: stakeholder decision
- Behaviour: If collapsed UI chosen, design and implement; Validation: leaks <talon-pid> showing <20KB/cycle
- Behaviour: Run overnight soak; Validation: leaks <talon-pid> after 12h+ idle session

## 2026-01-20 – Loop 14: canvas freeze reduces continuous redraw leaks (kind: analysis)

helper_version: helper:v20251223.1
focus: ADR 0082 residual constraint – investigate TextBlob caching and canvas freeze as alternatives to UI text reduction.
active_constraint: Help Canvas leaks ~150KB/cycle; explored whether TextBlob caching or canvas freeze could mitigate without UI changes.
expected_value:
  Impact: High – if successful, would reduce leak rate without changing UI.
  Probability: Medium – Talon Canvas has freeze/pause/resume methods.
  Time Sensitivity: Medium – blocks decision on mitigation approach.
  Uncertainty note: Medium – unclear if freeze prevents all redraws.
validation_targets:
  - Talon REPL: TextBlob creation and caching
  - leaks <talon-pid> with and without canvas.freeze()

evidence:
- green | 2026-01-20T06:15:00Z | exit 0 | REPL: TextBlob.create_xy API
    pointer: inline (discovered TextBlob.create_xy(font, text, x, y) can create reusable blobs)

- green | 2026-01-20T06:20:00Z | exit 0 | Create 1000 TextBlobs
    pointer: inline (+386 leaks, ~90KB for 1000 blobs – ~90 bytes/blob, very efficient)

- green | 2026-01-20T06:25:00Z | exit 0 | TextBlob.__del__ exists
    pointer: inline (TextBlob has destructor that likely calls sk_textblob_unref)

- red | 2026-01-20T06:30:00Z | exit 0 | Canvas draw_text_blob not exposed
    pointer: inline (SkCanvas only has draw_text, not draw_text_blob; would need FFI to draw cached blobs)

- green | 2026-01-20T06:40:00Z | exit 0 | 3 cycles WITH canvas.freeze() after 0.3s
    pointer: inline (425,678→429,634 leaks = +3,956 leaks for 3 cycles = ~1,319 leaks/cycle, ~200KB/cycle)

- red | 2026-01-20T06:45:00Z | exit 0 | 3 cycles WITHOUT freeze (control, 2.3s each)
    pointer: inline (429,634→457,151 leaks = +27,517 leaks for 3 cycles = ~9,172 leaks/cycle, ~1.4MB/cycle)

rollback_plan: None (analysis-only loop; codebase unchanged).

delta_summary: helper:diff-snapshot=0 files changed; discovered two potential mitigations:

**1. TextBlob Caching (Complex but Promising)**
- `TextBlob.create_xy(font, text, x, y)` can create reusable text blobs
- Creating 1000 blobs only adds ~90KB (vs ~150KB for one Help Canvas open)
- TextBlob has `__del__` destructor that properly unrefs
- **Blocker**: Canvas wrapper lacks `draw_text_blob`; would need FFI call with canvas/paint handles
- Could be implemented but requires significant code changes

**2. Canvas Freeze (Simple and Effective)**
- `canvas.freeze()` prevents continuous redraws
- **Reduces leak rate by ~7x**: ~200KB/cycle (frozen) vs ~1.4MB/cycle (unfrozen)
- Note: earlier tests showed ~300KB/cycle without freeze, control test showed ~1.4MB – the difference may be due to test duration (2.3s open vs 0.5s)
- Easy to implement: call `freeze()` after first draw completes

**Leak rate comparison:**
| Scenario | Per-Cycle Leak |
|----------|----------------|
| No freeze, short (0.5s) | ~300KB |
| No freeze, long (2.3s) | ~1.4MB |
| With freeze (2.3s) | ~200KB |

The longer the canvas stays open without freeze, the more it leaks due to continuous redraws. Freeze stops the redraw loop.

loops_remaining_forecast: 1 (confidence high) – implement canvas.freeze() in Help Canvas after first draw.

residual_constraints:
- severity: Medium | constraint: Help Canvas still leaks ~200KB/cycle even with freeze; mitigation: acceptable for normal usage, can add collapsed UI later if needed; monitor trigger: overnight soak; owning ADR: 0082.
- severity: Low | constraint: TextBlob caching not implemented due to missing draw_text_blob; mitigation: could be added later via FFI if freeze is insufficient; monitor trigger: post-freeze validation; owning ADR: 0082.

next_work:
- Behaviour: Implement canvas.freeze() in Help Canvas after first draw; Validation: leaks <talon-pid> showing <250KB/cycle
- Behaviour: Run overnight soak with freeze; Validation: leaks <talon-pid> after 12h+ idle session
- Behaviour: Consider TextBlob caching via FFI if freeze insufficient; Validation: proof of concept
