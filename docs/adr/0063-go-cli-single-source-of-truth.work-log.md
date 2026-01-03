# ADR-0063 Work Log — helper:v20251223.1

## Open Behaviours
- [Implementation Guardrails → Delivery posture] Replace stubbed CLI delegation with real binary | `python3 - <<'PY'
import pathlib, sys
bin_path = pathlib.Path('bin/bar.bin')
if bin_path.exists():
    bin_path.unlink()
import bootstrap
bootstrap.bootstrap()
if bin_path.exists():
    sys.exit(0)
raise SystemExit('bootstrap did not install CLI binary')
PY` | status: in_progress — loop-0026 persists delegation disable state and CLI wrapper gating; next slice wires adapter health counters to delegation backoffs.
- [Implementation Guardrails → Delivery posture] Release checksum manifest hardening | `scripts/tools/check_cli_assets.py` | status: in_progress — loop-0016 added tarball + checksum verification; next slice adds signature enforcement and CI upload contract.

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
