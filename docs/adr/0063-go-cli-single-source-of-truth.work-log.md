# ADR-0063 Work Log — helper:v20251223.1

## Open Behaviours
- [Implementation Guardrails → Delivery posture] Replace stubbed CLI delegation with real binary | `python3 -m pytest _tests/test_cli_talon_parity.py` | status: in_progress — loop-0066 automates CLI_GO_COMMAND guidance, regenerates delegation state/metadata during bootstrap, replaces the provider overlay with log output, and keeps auto-packaging green. loop-0069 replays CLI delegate streaming events through the Talon request bus so canvases/history stay in sync; loop-0070 promotes fixture-driven transcript streaming, propagates meta/history updates, and keeps Talon adapters green while we prepare real provider wiring; loop-0071 embeds canonical CLI transcript fixtures and removes ad-hoc environment overrides so Talon adapters consume packaged transcripts by default; loop-0072 synthesises live transcripts from request payloads so the CLI produces dynamic streaming output without relying on packaged fixtures; loop-0073 aligns CLI stream events with provider-style deltas and exposes usage metrics for Talon parity tests; loop-0074 feeds recorded provider transcripts through the CLI delegate so parity asserts captured usage and meta before live provider wiring ships. Upcoming loops: design provider transport interface + fixture recorder with automated redaction, gate live transport behind feature flags with dual-path evidence, and enforce SLO/telemetry before Talon delegates to networked providers.
- [Implementation Guardrails → Delivery posture] Release checksum manifest hardening | `python3 scripts/tools/check_cli_assets.py` | status: in_progress — loop-0059 enforces single-entry manifests; CI artefact evidence deferred until merge readiness.

## Completed Loops
- loop-0001 — tightened loop compliance statements and removed adhoc helper; evidence: `docs/adr/evidence/0063/loop-0001.md`.
- loop-0002 — scaffolded parity harness stub and captured red/green; evidence: `docs/adr/evidence/0063/loop-0002.md`.
- loop-0003 — documented CLI blocker and recorded `./bin/bar --health` absence; evidence: `docs/adr/evidence/0063/loop-0003.md`.
- loop-0004 — added schema asset check helper capturing bundle blocker; evidence: `docs/adr/evidence/0063/loop-0004.md`.
- loop-0005 — introduced JSON health payload stub for `bar`; evidence: `docs/adr/evidence/0063/loop-0005.md`.
- loop-0006 — supplied schema stub and made asset check green; evidence: `docs/adr/evidence/0063/loop-0006.md`.
- loop-0007 — enforced JSON health probe contract in tests and CLI; evidence: `docs/adr/evidence/0063/loop-0007.md`.
- loop-0008 — recorded telemetry SLO blocker and helper; evidence: `docs/adr/evidence/0063/loop-0008.md`.
- loop-0009 — queued next behaviours and linked validation targets; evidence: `docs/adr/evidence/0063/loop-0009.md`.
- loop-0010 — added sibling work-log tracker and guardrail; evidence: `docs/adr/evidence/0063/loop-0010.md`.
- loop-0011 — linked ADR body to work-log according to helper; evidence: `docs/adr/evidence/0063/loop-0011.md`.
- loop-0012 — recorded telemetry metrics and turned SLO checker green; evidence: `docs/adr/evidence/0063/loop-0012.md`.
- loop-0013 — migrated bar health probe to Go runtime and enforced parity sentinel; evidence: `docs/adr/evidence/0063/loop-0013.md`.
- loop-0014 — required compiled Go binary and executor sentinel for parity; evidence: `docs/adr/evidence/0063/loop-0014.md`.
- loop-0015 — surfaced compiled binary path in health payload and asset guard; evidence: `docs/adr/evidence/0063/loop-0015.md`.
- loop-0016 — updated [Implementation Guardrails → Delivery posture] Completed Loops; packaged bar CLI tarball with checksum manifest; validation: `python3 scripts/tools/check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0016.md`.
- loop-0017 — installed packaged CLI binary before delegation and updated bin wrapper fallback; validation: `python3 scripts/tools/install_bar_cli.py --quiet`; evidence: `docs/adr/evidence/0063/loop-0017.md`.
- loop-0018 — wired bootstrap to install the packaged CLI binary before delegation; validation: `python3 - <<'PY'
import pathlib, sys
bin_path = pathlib.Path('bin/bar.bin')
if bin_path.exists():
    bin_path.unlink()
import bootstrap
bootstrap.bootstrap()
if bin_path.exists():
    sys.exit(0)
raise SystemExit('bootstrap did not install CLI binary')
PY`; evidence: `docs/adr/evidence/0063/loop-0018.md`.
- loop-0019 — surfaced bootstrap installer failures with explicit warnings; validation: `python3 - <<'PY'
import pathlib, sys, io
from contextlib import redirect_stderr
manifest = pathlib.Path('artifacts/cli/bar-darwin-arm64.tar.gz.sha256')
backup = manifest.read_bytes()
manifest.unlink()
import bootstrap
buf = io.StringIO()
with redirect_stderr(buf):
    bootstrap.bootstrap()
manifest.write_bytes(backup)
print(buf.getvalue())
PY`; evidence: `docs/adr/evidence/0063/loop-0019.md`.
- loop-0020 — made bootstrap warnings actionable with rebuild instructions; validation: `python3 - <<'PY'
import pathlib, sys, io
from contextlib import redirect_stderr
manifest = pathlib.Path('artifacts/cli/bar-darwin-arm64.tar.gz.sha256')
backup = manifest.read_bytes()
manifest.unlink()
import bootstrap
buf = io.StringIO()
with redirect_stderr(buf):
    bootstrap.bootstrap()
manifest.write_bytes(backup)
output = buf.getvalue()
print(output)
PY`; evidence: `docs/adr/evidence/0063/loop-0020.md`.
- loop-0021 — enforced parity guardrail for packaged CLI artefacts; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0021.md`.
- loop-0022 — gated parity on bootstrap rebuilding instructions; validation: `python3 -m pytest _tests/test_cli_talon_parity.py::CLITalonParityTests::test_bootstrap_warning_mentions_rebuild_command`; evidence: `docs/adr/evidence/0063/loop-0022.md`.
- loop-0024 — routed bootstrap warnings through telemetry actions and parity assertions; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0024.md`.
- loop-0025 — disabled delegation on bootstrap telemetry warnings and re-enabled after successful install; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0025.md`.
- loop-0026 — persisted delegation disable telemetry and added CLI wrapper guard; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0026.md`.
- loop-0027 — enforced CLI health probe gating with failure threshold persistence and parity assertions; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0027.md`.
- loop-0028 — blocked request gating when CLI delegation is unhealthy and recorded drop telemetry; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0028.md`.
- loop-0029 — surfaced CLI disable telemetry in guard/backoff notifications and extended parity tests; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0029.md`.
- loop-0030 — piped delegation disable telemetry into provider registry/status canvases and parity gating; validation: `python3 -m pytest _tests/test_provider_commands.py`; evidence: `docs/adr/evidence/0063/loop-0030.md`.
- loop-0031 — enforced release guardrails by requiring delegation state snapshots in `check_cli_assets`; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0031.md`.
- loop-0032 — wired delegation snapshot digests into release guard rails; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0032.md`.
- loop-0033 — hydrated release snapshot metadata through bootstrap install path; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0033.md`.
- loop-0034 — blocked bootstrap fallback when snapshot digest drifts; validation: `python3 - <<'PY'
import pathlib, sys
bin_path = pathlib.Path('bin/bar.bin')
if bin_path.exists():
    bin_path.unlink()
import bootstrap
bootstrap.bootstrap()
if bin_path.exists():
    sys.exit(0)
raise SystemExit('bootstrap did not install CLI binary')
PY`; evidence: `docs/adr/evidence/0063/loop-0034.md`.
- loop-0035 — enforced signature verification across bootstrap and release guardrails; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0035.md`.
- loop-0036 — required tarball manifest signatures before parity guardrails; validation: `python3 scripts/tools/check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0036.md`.
- loop-0037 — sourced release signing key from environment and enforced CI overrides; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0037.md`.
- loop-0038 — kept release metadata consistent across bootstrap reinstall and guard rails; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0038.md`.
- loop-0039 — published signature metadata artefact paths for release guardrails; validation: `python3 scripts/tools/check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0039.md`.
- loop-0040 — emitted signing key telemetry and guarded stale metadata; validation: `python3 scripts/tools/check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0040.md`.
- loop-0041 — enforced signature telemetry fallback in bootstrap and parity harness; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0041.md`.
- loop-0042 — propagated signature telemetry mismatch into adapter UX and gating; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0042.md`.
- loop-0043 — surfaced telemetry recovery prompts via CLI delegation readiness and provider canvases; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0043.md`.
- loop-0044 — threaded CLI recovery metadata through history telemetry exports, inspection tooling, and parity regression guards; validation: `python3 -m pytest _tests/test_history_axis_validate.py _tests/test_history_axis_export_telemetry.py _tests/test_history_telemetry_inspect.py` and `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0044.md`.
- loop-0045 — integrated CLI recovery snapshot into release telemetry guardrails and packaging metadata; validation: `python3 -m pytest _tests/test_check_cli_assets.py` and `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0045.md`.
- loop-0046 — propagated CLI recovery snapshot into skip dashboards and telemetry exports; validation: `python3 -m pytest _tests/test_suggestion_skip_export.py _tests/test_history_axis_export_telemetry.py _tests/test_telemetry_export.py`; evidence: `docs/adr/evidence/0063/loop-0046.md`.
- loop-0047 — enforced recovery snapshot parity in checksum telemetry drift guard; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0047.md`.
- loop-0048 — exposed signature telemetry artefact path for CI consumption; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0048.md`.
- loop-0049 — retried packaging automatically when recovery snapshot drift is detected; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0049.md`.
- loop-0050 — exported refreshed signature telemetry bundles for CI uploads; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0050.md`.
- loop-0051 — integrated recovery snapshot drift remediation into Talon parity UX; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0051.md`.
- loop-0052 — documented signature telemetry export workflow for release operators; validation: _documentation-only_; evidence: `docs/adr/evidence/0063/loop-0052.md`.
- loop-0053 — wired CI artifact uploads for signature telemetry bundle; validation: _workflow-only_; evidence: `docs/adr/evidence/0063/loop-0053.md`.
- loop-0054 — recorded telemetry export output from `python3 scripts/tools/check_cli_assets.py --repackage-on-recovery-drift`; validation: `python3 scripts/tools/check_cli_assets.py --repackage-on-recovery-drift`; evidence: `docs/adr/evidence/0063/loop-0054.md`.
- loop-0055 — ensured CI workflow runs `check_cli_assets.py --repackage-on-recovery-drift` before uploading telemetry bundle; validation: _workflow-only_; evidence: `docs/adr/evidence/0063/loop-0055.md`.
- loop-0056 — hydrated runtime delegation state from packaged snapshot before guard checks; validation: `python3 scripts/tools/check_cli_assets.py --repackage-on-recovery-drift`; evidence: `docs/adr/evidence/0063/loop-0056.md`.
- loop-0057 — added guardrail test coverage for delegation state hydration; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0057.md`.
- loop-0058 — required tarball manifests to record the packaged filename and added guard coverage; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0058.md`.
- loop-0059 — rejected multi-entry tarball manifest files and added regression tests; validation: `python3 -m pytest _tests/test_check_cli_assets.py`; evidence: `docs/adr/evidence/0063/loop-0059.md`.
- loop-0060 — exposed CLI schema export command and parity test coverage; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0060.md`.
- loop-0061 — introduced CLI delegate stub and parity invocation helper; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0061.md`.
- loop-0062 — wrapped CLI delegate with lifecycle helper and parity coverage; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0062.md`.
- loop-0063 — implemented CLI delegate execution path with echo response and parity failure guard; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0063.md`.
- loop-0064 — surfaced CLI delegate responses through history entries and response canvas refresh; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0064.md`.
- loop-0065 — auto-generated CLI signature metadata during bootstrap, added parity coverage, and kept Talon imports green; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0065.md`.
- loop-0066 — provided CLI_GO_COMMAND fallback guidance, auto-packaged Go artefacts when available, and extended parity coverage for missing Go binaries; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0066.md`.
- loop-0067 — replaced provider overlay canvases with log-based status output, updated guard tests, and documented the UX mitigation; validation: `python3 -m pytest _tests/test_provider_commands.py`, `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0067.md`.
- loop-0068 — throttled bootstrap warnings and marked delegation ready after auto-recovery; validation: `python3 -m pytest _tests/test_provider_commands.py`, `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0068.md`.
- loop-0069 — replayed CLI delegate events into the Talon request bus, enriched CLI responses with chunk metadata, and extended parity coverage; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0069.md`.
- loop-0070 — streamed recorded CLI transcripts via fixture-driven delegate responses, surfaced meta/history alignment in Talon adapters, and kept parity tests green; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0070.md`.
- loop-0071 — embedded canonical CLI transcript fixtures, added delegate fixture key routing, and removed environment overrides from parity tests; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0071.md`.
- loop-0072 — synthesised streaming transcripts directly from delegate payloads, replacing baked fixtures so parity now exercises dynamic content; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0072.md`.
- loop-0073 — emitted provider-style streaming deltas with usage metrics and updated parity to assert the new shape; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0073.md`.
- loop-0074 — fed recorded provider transcripts through the CLI delegate, embedded the recorded transcript store, and refreshed parity assertions to match the captured usage; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0074.md`.
- loop-0075 — executed external provider command flows via `BAR_PROVIDER_COMMAND`, extended parity coverage, and surfaced shell-out error handling; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0075.md`.
- loop-0076 — gated provider command execution behind `BAR_PROVIDER_COMMAND_MODE`, added parity coverage for the disabled path, and rebuilt CLI binary; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0076.md`.
- loop-0077 — kept fixtures-only CLI mode from shelling out and added parity coverage to confirm recorded transcripts stream without invoking the provider command; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0077.md`.
- loop-0078 — enforced fixtures-only missing transcript errors with parity coverage and CLI exit codes; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0078.md`.
- loop-0079 — added HTTP provider transport with environment-gated endpoint and parity coverage verifying success/failure paths; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0079.md`.
- loop-0080 — recorded HTTP fallback metadata when endpoint is missing or unreachable and added parity coverage; validation: `python3 -m pytest _tests/test_cli_talon_parity.py`; evidence: `docs/adr/evidence/0063/loop-0080.md`.
