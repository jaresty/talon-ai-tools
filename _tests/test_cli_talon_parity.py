import unittest
from pathlib import Path
import io
import json
import platform
import subprocess
import sys
from contextlib import redirect_stderr
from unittest import mock

from talon import actions

import lib.cliDelegation as cliDelegation
import lib.cliHealth as cliHealth
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
