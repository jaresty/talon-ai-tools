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
