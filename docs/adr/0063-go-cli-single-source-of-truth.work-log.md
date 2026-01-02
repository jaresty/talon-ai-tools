# ADR-0063 Work Log — helper:v20251223.1

## Open Behaviours
- [Implementation Guardrails → Delivery posture] Replace stubbed CLI delegation with real binary | `python3 - <<'PY'\nimport pathlib, sys\nbin_path = pathlib.Path('bin/bar.bin')\nif bin_path.exists():\n    bin_path.unlink()\nimport bootstrap\nbootstrap.bootstrap()\nif bin_path.exists():\n    sys.exit(0)\nraise SystemExit('bootstrap did not install CLI binary')\nPY` | status: in_progress — loop-0018 wires bootstrap to install the packaged CLI; next slice integrates Talon adapters to surface installer failures.
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
- loop-0018 — wired bootstrap to install the packaged CLI binary before delegation; validation: `python3 - <<'PY'\nimport pathlib, sys\nbin_path = pathlib.Path('bin/bar.bin')\nif bin_path.exists():\n    bin_path.unlink()\nimport bootstrap\nbootstrap.bootstrap()\nif bin_path.exists():\n    sys.exit(0)\nraise SystemExit('bootstrap did not install CLI binary')\nPY`; evidence: `docs/adr/evidence/0063/loop-0018.md`.
