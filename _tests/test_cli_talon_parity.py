import unittest
from pathlib import Path
import io
import json
import hashlib
import platform
import subprocess
import sys
from contextlib import redirect_stderr
from unittest import mock

from talon import actions

import lib.cliDelegation as cliDelegation
import lib.cliHealth as cliHealth
import lib.surfaceGuidance as surfaceGuidance
from lib import historyLifecycle, requestGating
import scripts.tools.install_bar_cli as install_bar_cli
from lib.bootstrapTelemetry import (
    clear_bootstrap_warning_events,
    get_bootstrap_warning_messages,
)


try:
    import bootstrap as bootstrap_module
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None

    def get_bootstrap_warnings(*, clear: bool = False):  # type: ignore[override]
        return []
else:
    bootstrap = getattr(bootstrap_module, "bootstrap", None)
    get_bootstrap_warnings = getattr(
        bootstrap_module,
        "get_bootstrap_warnings",
        lambda *, clear=False: [],
    )
    if callable(bootstrap):
        bootstrap()
    else:
        bootstrap = None

CLI_BINARY = Path("bin/bar")
SCHEMA_BUNDLE = Path("docs/schema/command-surface.json")
PACKAGED_CLI_DIR = Path("artifacts/cli")
SIGNATURE_KEY = "adr-0063-cli-release-signature"


def _target_suffix() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, machine)
    return f"bar-{system}-{arch}"


def _packaged_cli_tarball() -> Path:
    return PACKAGED_CLI_DIR / f"{_target_suffix()}.tar.gz"


def _packaged_cli_manifest(tarball: Path) -> Path:
    return tarball.with_name(f"{tarball.name}.sha256")


def _canonical_snapshot_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _signature_for(message: str) -> str:
    return hashlib.sha256((SIGNATURE_KEY + "\n" + message).encode("utf-8")).hexdigest()


if bootstrap is None:

    class CLITalonParityPlaceholder(unittest.TestCase):
        @unittest.skip("Talon runtime cannot execute CLI parity harness")
        def test_skip_in_talon_runtime(self) -> None:  # pragma: no cover - Talon skip
            pass

else:

    class CLITalonParityTests(unittest.TestCase):
        def test_cli_health_probe_emits_json_status(self) -> None:
            self.assertTrue(
                CLI_BINARY.exists(),
                "CLI binary missing; run loop-0005 to restore bar stub",
            )

            result = subprocess.run(
                [str(CLI_BINARY), "--health"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertIn("version", payload)
            self.assertEqual(
                payload.get("runtime"),
                "go",
                "CLI runtime must report Go binary; stubbed implementation detected",
            )
            self.assertEqual(
                payload.get("executor"),
                "compiled",
                "CLI must run compiled binary rather than go run stub",
            )
            self.assertEqual(
                payload.get("binary_path"),
                "bin/bar.bin",
                "CLI must report compiled binary path relative to repo root",
            )

        def test_schema_bundle_contains_version_marker(self) -> None:
            self.assertTrue(
                SCHEMA_BUNDLE.exists(),
                "Schema bundle missing; run loop-0006 to restore",
            )

            payload = json.loads(SCHEMA_BUNDLE.read_text(encoding="utf-8"))
            self.assertIn("version", payload)
            self.assertIn("commands", payload)

        def test_packaged_cli_assets_present(self) -> None:
            tarball = _packaged_cli_tarball()
            manifest = _packaged_cli_manifest(tarball)

            missing = [str(path) for path in (tarball, manifest) if not path.exists()]
            if missing:
                self.fail(
                    "Packaged CLI artefacts missing; run "
                    "`python3 scripts/tools/package_bar_cli.py --print-paths` to rebuild. "
                    f"Missing: {', '.join(missing)}"
                )

        def test_bootstrap_warning_mentions_rebuild_command(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            tarball = _packaged_cli_tarball()
            manifest = _packaged_cli_manifest(tarball)

            self.assertTrue(
                tarball.exists(),
                "Packaged CLI tarball missing; run `python3 scripts/tools/package_bar_cli.py --print-paths`.",
            )
            self.assertTrue(
                manifest.exists(),
                "Packaged CLI manifest missing; run `python3 scripts/tools/package_bar_cli.py --print-paths`.",
            )

            backup = manifest.read_bytes()
            delegation_state_path = Path("var/cli-telemetry/delegation-state.json")
            disabled_state = None
            restored_state = None
            try:
                manifest.unlink()
            except FileNotFoundError:
                pass
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)
            calls_before = list(actions.user.calls)

            delegation_enabled_after_warning = True
            disable_events = []
            restored_enabled = None
            try:
                buf = io.StringIO()
                with redirect_stderr(buf):
                    bootstrap()
                warning_output = buf.getvalue()
                telemetry_messages = get_bootstrap_warning_messages(clear=False)
                adapter_messages = actions.user.cli_bootstrap_warning_messages()
                warnings = get_bootstrap_warnings(clear=True)
                disable_events = cliDelegation.disable_events()
                delegation_enabled_after_warning = cliDelegation.delegation_enabled()
                if delegation_state_path.exists():
                    disabled_state = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
            finally:
                manifest.write_bytes(backup)
                bootstrap()
                restored_enabled = cliDelegation.delegation_enabled()
                if delegation_state_path.exists():
                    restored_state = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
                clear_bootstrap_warning_events()
                cliDelegation.reset_state()

            new_calls = actions.user.calls[len(calls_before) :]
            # reset added calls to keep other tests isolated
            del actions.user.calls[len(calls_before) :]
            self.assertIn(
                "`python3 scripts/tools/package_bar_cli.py --print-paths`",
                warning_output,
                "Bootstrap warning must direct operators to rebuild packaged CLI",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in warning
                    for warning in warnings
                ),
                "Bootstrap warnings list should include rebuild instructions",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in message
                    for message in telemetry_messages
                ),
                "Bootstrap telemetry should capture rebuild instructions for adapters",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in message
                    for message in adapter_messages
                ),
                "Talon adapters should read bootstrap telemetry via actions.user",
            )
            self.assertIsNotNone(
                disabled_state,
                "Delegation state file should exist when bootstrap disables CLI",
            )
            if disabled_state is not None:
                self.assertFalse(
                    disabled_state.get("enabled", True),
                    "Delegation state should mark CLI as disabled",
                )
                self.assertIn(
                    "package_bar_cli.py",
                    disabled_state.get("reason", ""),
                    "Delegation state should record rebuild instruction reason",
                )
            self.assertFalse(
                delegation_enabled_after_warning,
                "Bootstrap warnings should disable CLI delegation",
            )
            self.assertTrue(
                any(
                    "package_bar_cli.py" in event.get("reason", "")
                    for event in disable_events
                ),
                "CLI delegation disable events should include rebuild instruction reason",
            )
            self.assertIsNotNone(
                restored_state,
                "Delegation state file should exist after bootstrap reinstalls CLI",
            )
            if restored_state is not None:
                self.assertTrue(
                    restored_state.get("enabled", False),
                    "Delegation state should mark CLI as enabled after reinstall",
                )
            self.assertTrue(
                restored_enabled,
                "Successful bootstrap should re-enable CLI delegation",
            )
            self.assertTrue(
                any(
                    call[0] == "notify"
                    and call[1]
                    and "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in call[1][0]
                    for call in new_calls
                ),
                "Bootstrap warning should notify adapters with rebuild instructions",
            )

            delegation_state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

        def test_bootstrap_hydrates_release_snapshot_metadata(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            snapshot_path = PACKAGED_CLI_DIR / "delegation-state.json"
            digest_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256"
            signature_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256.sig"
            runtime_path = Path("var/cli-telemetry/delegation-state.json")

            self.assertTrue(
                snapshot_path.exists(),
                "Delegation snapshot missing; run loop-0032 to rebuild",
            )
            self.assertTrue(
                digest_path.exists(),
                "Delegation snapshot digest missing; run loop-0032 to rebuild",
            )

            snapshot_backup = snapshot_path.read_bytes()
            digest_backup = digest_path.read_bytes()
            if signature_path.exists():
                signature_backup = signature_path.read_bytes()
            else:
                recorded_existing = digest_path.read_text(encoding="utf-8").strip()
                signature_path.write_text(
                    f"{_signature_for(recorded_existing)}\n", encoding="utf-8"
                )
                signature_backup = None
            runtime_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)

            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
                "snapshot_version": "loop-0033-test",
            }
            digest = _canonical_snapshot_digest(snapshot_payload)
            snapshot_path.write_text(
                json.dumps(snapshot_payload, indent=2), encoding="utf-8"
            )
            digest_path.write_text(
                f"{digest}  {snapshot_path.name}\n", encoding="utf-8"
            )
            recorded = f"{digest}  {snapshot_path.name}"
            signature_path.write_text(f"{_signature_for(recorded)}\n", encoding="utf-8")

            try:
                bootstrap()
                self.assertTrue(
                    runtime_path.exists(),
                    "Bootstrap should hydrate runtime delegation snapshot",
                )
                hydrated = json.loads(runtime_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    hydrated.get("snapshot_version"),
                    snapshot_payload["snapshot_version"],
                    "Hydrated state should preserve release snapshot metadata",
                )
                self.assertEqual(
                    hydrated.get("source"),
                    snapshot_payload["source"],
                    "Hydrated state should preserve snapshot source",
                )
                self.assertTrue(
                    hydrated.get("enabled", False),
                    "Hydrated state should mark delegation enabled",
                )
                self.assertEqual(
                    digest,
                    _canonical_snapshot_digest(hydrated),
                    "Hydrated state digest must match release snapshot digest",
                )
            finally:
                snapshot_path.write_bytes(snapshot_backup)
                digest_path.write_bytes(digest_backup)
                if signature_backup is None:
                    signature_path.unlink(missing_ok=True)
                else:
                    signature_path.write_bytes(signature_backup)
                runtime_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)

        def test_bootstrap_fails_on_snapshot_digest_mismatch(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            snapshot_path = PACKAGED_CLI_DIR / "delegation-state.json"
            digest_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256"
            runtime_path = Path("var/cli-telemetry/delegation-state.json")

            self.assertTrue(
                snapshot_path.exists(),
                "Delegation snapshot missing; run loop-0032 to rebuild",
            )
            self.assertTrue(
                digest_path.exists(),
                "Delegation snapshot digest missing; run loop-0032 to rebuild",
            )

            snapshot_backup = snapshot_path.read_bytes()
            digest_backup = digest_path.read_bytes()
            runtime_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)

            bad_digest = "0" * 64
            digest_path.write_text(
                f"{bad_digest}  {snapshot_path.name}\n", encoding="utf-8"
            )

            try:
                with self.assertRaises(install_bar_cli.DelegationSnapshotError):
                    bootstrap()
                warnings = get_bootstrap_warnings(clear=True)
                self.assertTrue(
                    any(
                        "delegation snapshot validation failed" in warning
                        for warning in warnings
                    ),
                    "Bootstrap warning should surface snapshot validation failure",
                )
            finally:
                snapshot_path.write_bytes(snapshot_backup)
                digest_path.write_bytes(digest_backup)
                runtime_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                bootstrap()

        def test_cli_health_probe_trips_delegation_after_failures(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

            failure_result = subprocess.CompletedProcess(
                args=[str(CLI_BINARY), "--health"],
                returncode=1,
                stdout="",
                stderr="probe failed",
            )
            success_result = subprocess.CompletedProcess(
                args=[str(CLI_BINARY), "--health"],
                returncode=0,
                stdout=json.dumps({"status": "ok", "version": "test"}),
                stderr="",
            )

            with mock.patch(
                "lib.cliHealth._run_health_command",
                side_effect=[failure_result, failure_result, failure_result],
            ):
                for _ in range(3):
                    cliHealth.probe_cli_health()

            self.assertFalse(
                cliDelegation.delegation_enabled(),
                "Delegation should disable after repeated health failures",
            )
            self.assertTrue(state_path.exists(), "Delegation state file missing")
            disabled_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(disabled_state.get("failure_count"), 3)
            self.assertFalse(disabled_state.get("enabled", True))
            self.assertIn("failure threshold", disabled_state.get("reason", ""))

            cliDelegation.reset_state()
            with mock.patch(
                "lib.cliHealth._run_health_command", return_value=success_result
            ):
                cliHealth.probe_cli_health()

            restored_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(restored_state.get("enabled", False))
            self.assertEqual(restored_state.get("failure_count"), 0)

            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

        def test_request_gating_blocks_when_cli_unhealthy(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            actions.user.calls.clear()

            for _ in range(3):
                cliDelegation.record_health_failure(
                    "probe failed", source="health_probe"
                )

            with mock.patch(
                "lib.cliHealth.probe_cli_health", return_value=False
            ) as probe:
                allowed, reason = requestGating.try_begin_request(source="parity")

            self.assertFalse(allowed)
            self.assertEqual(reason, "cli_unhealthy")
            probe.assert_called_once()

            message = historyLifecycle.last_drop_reason()
            self.assertIn("CLI delegation disabled", message)
            self.assertIn("failed probes", message)

            actions.user.calls.clear()
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            state_path.unlink(missing_ok=True)

        def test_surface_guard_notifies_cli_failure_details(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            actions.user.calls.clear()

            failure_threshold = cliDelegation.failure_threshold()
            for _ in range(failure_threshold):
                cliDelegation.record_health_failure(
                    "probe failed", source="health_probe"
                )

            failure_count = cliDelegation.failure_count()
            expected_probe_fragment = (
                f"failed probes={failure_count}/{failure_threshold}"
                if failure_threshold
                else f"failed probes={failure_count}"
            )

            with mock.patch("lib.cliHealth.probe_cli_health", return_value=False):
                with mock.patch("lib.surfaceGuidance.notify") as notify:
                    blocked = surfaceGuidance.guard_surface_request(
                        surface="provider_commands",
                        source="parity-cli-failure",
                    )

            self.assertTrue(blocked)
            notify.assert_called()
            message = notify.call_args[0][0]
            self.assertIn("CLI delegation disabled", message)
            self.assertIn(expected_probe_fragment, message)
            self.assertIn("probe failed", message)

            historyLifecycle.set_drop_reason("")
            cliDelegation.reset_state()
            state_path.unlink(missing_ok=True)
