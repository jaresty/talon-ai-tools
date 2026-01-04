import unittest
from pathlib import Path
import io
import json
import hashlib
import os
import platform
import subprocess
import sys
from contextlib import redirect_stderr
from datetime import datetime, timezone
from unittest import mock

from talon import actions

SIGNATURE_KEY = "adr-0063-cli-release-signature"
os.environ.setdefault("CLI_RELEASE_SIGNING_KEY", SIGNATURE_KEY)
os.environ.setdefault("CLI_RELEASE_SIGNING_KEY_ID", "local-dev")
os.environ.setdefault("CLI_SIGNATURE_METADATA", "artifacts/cli/signatures.json")
os.environ.setdefault(
    "CLI_SIGNATURE_TELEMETRY", "var/cli-telemetry/signature-metadata.json"
)
os.environ.setdefault(
    "CLI_SIGNATURE_TELEMETRY_EXPORT", "artifacts/cli/signature-telemetry.json"
)

import lib.cliDelegation as cliDelegation
import lib.cliHealth as cliHealth
import lib.providerCommands as providerCommands
import lib.providerRegistry as providerRegistry
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
        def _signature_metadata_path(self) -> Path:
            return PACKAGED_CLI_DIR / "signatures.json"

        def _signature_telemetry_path(self) -> Path:
            return Path(
                os.environ.get(
                    "CLI_SIGNATURE_TELEMETRY",
                    "var/cli-telemetry/signature-metadata.json",
                )
            )

        def _load_signature_metadata(self) -> dict:
            metadata_path = self._signature_metadata_path()
            self.assertTrue(
                metadata_path.exists(),
                "Signature metadata missing; run loop-0039 to rebuild",
            )
            return json.loads(metadata_path.read_text(encoding="utf-8"))

        def _write_signature_telemetry(
            self,
            *,
            signing_key_id: str | None = None,
            status: str = "green",
            issues: list[str] | None = None,
        ) -> dict:
            metadata = self._load_signature_metadata()
            payload = {
                "status": status,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "signing_key_id": signing_key_id
                or metadata.get("signing_key_id")
                or os.environ.get("CLI_RELEASE_SIGNING_KEY_ID", "local-dev"),
                "tarball_manifest": dict(metadata.get("tarball_manifest") or {}),
                "delegation_snapshot": dict(metadata.get("delegation_snapshot") or {}),
            }
            if issues:
                payload["issues"] = list(issues)
            telemetry_path = self._signature_telemetry_path()
            telemetry_path.parent.mkdir(parents=True, exist_ok=True)
            telemetry_path.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            return payload

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

        def test_cli_schema_command_outputs_bundle(self) -> None:
            result = subprocess.run(
                [str(CLI_BINARY), "schema"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = SCHEMA_BUNDLE.read_text(encoding="utf-8").strip()
            self.assertEqual(result.stdout.strip(), expected)

        def test_cli_delegate_stub_response(self) -> None:
            payload = {
                "request_id": "req-123",
                "prompt": {
                    "text": "hello world",
                },
            }
            success, response, error_message = cliDelegation.invoke_cli_delegate(
                payload
            )
            self.assertTrue(success, error_message)
            self.assertEqual(response.get("status"), "not_implemented")
            self.assertEqual(response.get("request_id"), "req-123")
            self.assertIn("stub", (response.get("message") or "").lower())

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
            metadata_path = PACKAGED_CLI_DIR / "signatures.json"
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
            if metadata_path.exists():
                metadata_backup = metadata_path.read_bytes()
            else:
                metadata_backup = None
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
            signature = _signature_for(recorded)
            signature_path.write_text(f"{signature}\n", encoding="utf-8")

            tarball = _packaged_cli_tarball()
            manifest_path = _packaged_cli_manifest(tarball)
            manifest_recorded = manifest_path.read_text(encoding="utf-8").strip()
            manifest_signature_path = manifest_path.with_suffix(
                manifest_path.suffix + ".sig"
            )
            manifest_signature = manifest_signature_path.read_text(
                encoding="utf-8"
            ).strip()
            metadata = {
                "signing_key_id": os.environ.get(
                    "CLI_RELEASE_SIGNING_KEY_ID",
                    "local-dev",
                ),
                "tarball_manifest": {
                    "recorded": manifest_recorded,
                    "signature": manifest_signature,
                },
                "delegation_snapshot": {
                    "recorded": recorded,
                    "signature": signature,
                },
                "cli_recovery_snapshot": {
                    "enabled": snapshot_payload.get("enabled", True),
                    "prompt": historyLifecycle.drop_reason_message("cli_ready"),
                },
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            telemetry_path = self._signature_telemetry_path()
            telemetry_backup = (
                telemetry_path.read_bytes() if telemetry_path.exists() else None
            )
            self._write_signature_telemetry()

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
                if metadata_backup is None:
                    metadata_path.unlink(missing_ok=True)
                else:
                    metadata_path.write_bytes(metadata_backup)
                if telemetry_backup is None:
                    telemetry_path.unlink(missing_ok=True)
                else:
                    telemetry_path.write_bytes(telemetry_backup)
                runtime_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)

        def test_bootstrap_disables_delegation_on_signature_telemetry_mismatch(
            self,
        ) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            telemetry_path = self._signature_telemetry_path()
            telemetry_backup = (
                telemetry_path.read_bytes() if telemetry_path.exists() else None
            )

            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)
            get_bootstrap_warning_messages(clear=True)
            cliDelegation.reset_state()
            actions.user.calls.clear()

            self._write_signature_telemetry(signing_key_id="unexpected-key")

            try:
                with mock.patch(
                    "scripts.tools.install_bar_cli._write_signature_telemetry",
                    return_value=None,
                ):
                    bootstrap()
                self.assertFalse(
                    cliDelegation.delegation_enabled(),
                    "Bootstrap should disable delegation when signing telemetry mismatches",
                )

                allowed, reason = requestGating.try_begin_request(
                    source="signature-telemetry-test"
                )
                self.assertFalse(allowed)
                self.assertEqual(reason, "cli_signature_mismatch")
                drop_message = historyLifecycle.last_drop_reason()
                self.assertIn("signature telemetry mismatch", drop_message)
                export_path = os.environ.get(
                    "CLI_SIGNATURE_TELEMETRY_EXPORT",
                    "artifacts/cli/signature-telemetry.json",
                )
                if export_path:
                    self.assertIn(export_path, drop_message)

                registry = providerRegistry.ProviderRegistry()
                entries = registry.status_entries()
                self.assertTrue(
                    any(
                        entry.get("delegation", {}).get("reason")
                        == "cli_signature_mismatch"
                        and "signature telemetry mismatch"
                        in (entry.get("delegation", {}).get("message") or "")
                        for entry in entries
                    ),
                    "Provider registry should surface signature telemetry mismatch",
                )
                if export_path:
                    self.assertTrue(
                        any(
                            export_path
                            in (entry.get("delegation", {}).get("message") or "")
                            for entry in entries
                        ),
                        "Provider registry message should mention telemetry export path",
                    )

                warnings = get_bootstrap_warning_messages(clear=False)
                self.assertTrue(
                    any(
                        "signature telemetry mismatch" in warning
                        for warning in warnings
                    ),
                    "Bootstrap warnings should mention signature telemetry mismatch",
                )
                if export_path:
                    self.assertTrue(
                        any(export_path in warning for warning in warnings),
                        "Bootstrap warnings should mention telemetry export path",
                    )
                delegation_state_path = Path("var/cli-telemetry/delegation-state.json")
                if delegation_state_path.exists():
                    state_payload = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
                    self.assertFalse(state_payload.get("enabled", True))
            finally:
                if telemetry_backup is None:
                    telemetry_path.unlink(missing_ok=True)
                else:
                    telemetry_path.write_bytes(telemetry_backup)
                cliDelegation.reset_state()
                historyLifecycle.clear_drop_reason()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                get_bootstrap_warning_messages(clear=True)
                actions.user.calls.clear()

        def test_cli_delegation_ready_surfaces_recovery_prompt(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            actions.user.calls.clear()
            historyLifecycle.set_drop_reason(
                "cli_signature_mismatch",
                historyLifecycle.drop_reason_message("cli_signature_mismatch"),
            )

            cliDelegation.disable_delegation(
                "signature telemetry mismatch detected during bootstrap",
                source="bootstrap",
                notify=False,
            )

            registry = providerRegistry.ProviderRegistry()
            entries = registry.status_entries()
            self.assertTrue(
                any(
                    entry.get("delegation", {}).get("reason")
                    == "cli_signature_mismatch"
                    for entry in entries
                ),
                "Provider registry should surface signature mismatch before recovery",
            )

            with mock.patch("lib.providerCommands.show_provider_canvas") as show_canvas:
                cliDelegation.mark_cli_ready(source="parity")
                show_canvas.assert_called_once()
                canvas_args = show_canvas.call_args[0]
                self.assertGreaterEqual(len(canvas_args), 2)
                self.assertIn("Delegation ready", canvas_args[1])

            self.assertTrue(cliDelegation.delegation_enabled())
            reason_code = historyLifecycle.last_drop_reason_code() or "cli_ready"
            self.assertIn(
                reason_code,
                {"cli_ready", "cli_signature_recovered"},
                "Recovered delegation should tag drop reason as cli_ready",
            )

            ready_calls = [
                c for c in actions.user.calls if c[0] == "cli_delegation_ready"
            ]
            self.assertTrue(
                ready_calls,
                "Expected cli_delegation_ready action to be recorded on recovery",
            )
            self.assertEqual(ready_calls[-1][1], ("parity",))

            entries = providerRegistry.ProviderRegistry().status_entries()
            self.assertTrue(
                any(
                    entry.get("delegation", {}).get("reason")
                    == "cli_signature_recovered"
                    for entry in entries
                ),
                "Provider registry should surface signature telemetry recovery",
            )
            recovered_messages = [
                entry.get("delegation", {}).get("message", "")
                for entry in entries
                if entry.get("delegation", {}).get("reason")
                == "cli_signature_recovered"
            ]
            self.assertTrue(
                any(
                    "CLI delegation restored" in message
                    for message in recovered_messages
                ),
                "Recovery message should mention restored delegation",
            )

            actions.user.calls.clear()
            historyLifecycle.set_drop_reason("")
            cliDelegation.reset_state()
            state_path.unlink(missing_ok=True)

        def test_bootstrap_fails_on_snapshot_digest_mismatch(self) -> None:
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
            runtime_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)

            bad_digest = "0" * 64
            digest_path.write_text(
                f"{bad_digest}  {snapshot_path.name}\n", encoding="utf-8"
            )

            try:
                with self.assertRaises(install_bar_cli.ReleaseSignatureError):
                    bootstrap()
                warnings = get_bootstrap_warnings(clear=True)
                self.assertTrue(
                    any(
                        "release signature validation failed" in warning
                        for warning in warnings
                    ),
                    "Bootstrap warning should surface signature validation failure",
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
