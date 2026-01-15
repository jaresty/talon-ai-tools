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
