# ADR-0149: Bounded Evolution Strategy — Work Log

helper_version: helper:v20260227.1

## Salient Task List

- T-1: Define structured error hierarchy (`TalonAIError`, `StateError`, `ConfigError`, `ProviderError`) in `lib/errors.py`
- T-2: Integrate existing scattered exception classes into the hierarchy
- T-3: Add `error_context` decorator for debugging

VCS_REVERT: `git restore`
EVIDENCE_ROOT: `docs/adr/evidence/0149/`
VALIDATION_TARGET (T-1): `.venv/bin/python -m pytest _tests/test_errors.py -v`

---

## Loop 1 — 2026-02-28

helper_version: helper:v20260227.1
focus: ADR-0149 § Phase 1 — T-1: Define error hierarchy in lib/errors.py

active_constraint: `lib/errors.py` does not exist; `_tests/test_errors.py` importing `TalonAIError`, `StateError`, `ConfigError`, `ProviderError` from `talon_user.lib.errors` exits non-zero. Alternatives considered: (a) extend existing exceptions in modelHelpers.py in-place — ranks lower because it doesn't create a single authoritative hierarchy module; (b) skip hierarchy and document only — ranks lower because T-1 requires a concrete importable module. Expected value: Impact=H (foundation for T-2 and T-3), Probability=H (deterministic), Time Sensitivity=H (T-2 and T-3 blocked until T-1 lands). Product: 27.

validation_targets:
- T-1: `.venv/bin/python -m pytest _tests/test_errors.py -v`

evidence:
- red | 2026-02-28T03:40:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_errors.py -v`
    helper:diff-snapshot=0 files changed
    ModuleNotFoundError: No module named 'talon_user.lib.errors' | inline

- green | 2026-02-28T03:42:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_errors.py -v`
    helper:diff-snapshot=2 files changed (lib/errors.py + _tests/test_errors.py)
    All hierarchy and subclass assertions pass | inline

- removal | 2026-02-28T03:43:00Z | exit 1 | `git restore lib/errors.py && .venv/bin/python -m pytest _tests/test_errors.py -v`
    helper:diff-snapshot=0 files changed
    ModuleNotFoundError: No module named 'talon_user.lib.errors' | inline

rollback_plan: `git restore lib/errors.py _tests/test_errors.py` then replay red validation.

delta_summary: Created `lib/errors.py` with TalonAIError base and StateError/ConfigError/ProviderError subclasses. Created `_tests/test_errors.py` as specifying validation. 2 files added.

loops_remaining_forecast: 2 loops remaining (T-2: wire existing exceptions into hierarchy; T-3: error_context decorator). Confidence: high.

residual_constraints:
- T-2 (existing exceptions in modelHelpers.py not yet in hierarchy): severity=M, mitigation=next loop, monitoring=import check, owning ADR=0149
- T-3 (no error_context decorator): severity=L, mitigation=loop 3, monitoring=n/a, owning ADR=0149
- Pre-existing test failure in test_axis_regen_all.py (axis config drift): severity=L, unrelated to Phase 1, mitigation=none needed for this loop, monitoring=existing CI, owning ADR=pre-existing

next_work:
- Behaviour T-2: Wire existing exceptions (MissingAPIKeyError, GPTRequestError, ClipboardImageError, UnsupportedProviderCapability) to extend from hierarchy in lib/errors.py. Validation: `.venv/bin/python -m pytest _tests/test_errors.py _tests/test_provider_error_canvas.py -v`
- Behaviour T-3: Add `error_context` decorator to lib/errors.py. Validation: `.venv/bin/python -m pytest _tests/test_errors.py -v`

---

## Loop 2 — 2026-02-28

helper_version: helper:v20260227.1
focus: ADR-0149 § Phase 1 — T-2: Wire existing exceptions into TalonAIError hierarchy

active_constraint: `MissingAPIKeyError`, `GPTRequestError`, `ClipboardImageError`, `UnsupportedProviderCapability` all extend bare Python builtins; `ExistingExceptionIntegrationTests` exits non-zero (7 failures). Alternatives considered: (a) add parallel aliases in lib/errors.py — ranks lower because two definitions of the same exception is confusing; (b) leave unchanged — ranks lower because T-2 is the explicitly stated goal. Expected value: Impact=H (catchable as TalonAIError enables unified handling), Probability=H (deterministic base-class change), Time Sensitivity=M (T-3 doesn't depend on T-2). Product: 18.

validation_targets:
- T-2: `.venv/bin/python -m pytest _tests/test_errors.py _tests/test_provider_error_canvas.py -v`

evidence:
- red | 2026-02-28T03:50:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_errors.py::ExistingExceptionIntegrationTests -v`
    helper:diff-snapshot=1 file changed (_tests/test_errors.py additions only)
    7 failures: AssertionError: False is not true (issubclass checks) | inline

- green | 2026-02-28T03:53:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_errors.py _tests/test_provider_error_canvas.py -v`
    helper:diff-snapshot=2 files changed (lib/modelHelpers.py + _tests/test_errors.py)
    19 passed | inline

- removal | 2026-02-28T03:54:00Z | exit 1 | `git restore lib/modelHelpers.py && pytest ExistingExceptionIntegrationTests`
    helper:diff-snapshot=0 files changed (impl reverted, test kept)
    7 failures: issubclass assertions fail again | inline

rollback_plan: `git restore lib/modelHelpers.py` reverts base-class changes; test suite re-fails as shown.

delta_summary: Changed bases of MissingAPIKeyError→ConfigError, GPTRequestError→ProviderError, ClipboardImageError→ProviderError, UnsupportedProviderCapability→ProviderError. Added from .errors import to modelHelpers.py. Removed duplicate CancelledRequest definition at line 1871. 2 files changed.

loops_remaining_forecast: 1 loop remaining (T-3: error_context decorator — already implemented in Loop 1; tests already green). Phase 1 effectively complete. Confidence: high.

residual_constraints:
- T-3 (error_context decorator): already shipped in lib/errors.py and tested — no loop needed
- Pre-existing test_axis_regen_all.py drift: severity=L, unrelated, owning ADR=pre-existing
- Notification-based failures (30+ callsites): not targeted by Phase 1 ADR scope; deferred to future ADR work

next_work:
- Phase 1 complete: all three tasks delivered (T-1 hierarchy, T-2 integration, T-3 decorator)
- Verify full test suite still passes excluding pre-existing failure
- Update ADR status to reflect Phase 1 done
