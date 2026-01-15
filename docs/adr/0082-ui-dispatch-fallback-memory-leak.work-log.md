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
