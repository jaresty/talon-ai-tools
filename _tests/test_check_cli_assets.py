import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIGNATURE_KEY = "adr-0063-cli-release-signature"

try:
    from talon_user.lib.requestLog import drop_reason_message
except Exception:  # pragma: no cover - Talon runtime fallback
    drop_reason_message = None

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is None:  # pragma: no cover - Talon runtime shim

    class CheckCliAssetsPlaceholder(unittest.TestCase):
        @unittest.skip("CLI asset guard unavailable inside Talon runtime")
        def test_placeholder(self) -> None:
            pass

else:

    class CheckCliAssetsTests(unittest.TestCase):
        def setUp(self) -> None:
            self._tmp = tempfile.TemporaryDirectory()
            self.addCleanup(self._tmp.cleanup)
            base = Path(self._tmp.name)
            self.runtime_dir = base / "runtime"
            self.runtime_dir.mkdir()
            self.release_dir = base / "release"
            self.release_dir.mkdir()
            self.state_path = self.runtime_dir / "delegation-state.json"
            self.snapshot_path = self.release_dir / "delegation-state.json"
            self.digest_path = self.release_dir / "delegation-state.json.sha256"
            self.signature_path = self.release_dir / "delegation-state.json.sha256.sig"
            self.metadata_path = self.release_dir / "signatures.json"
            self.telemetry_path = self.release_dir / "signature-telemetry.json"
            self.env = os.environ.copy()
            self.env["CLI_DELEGATION_STATE"] = str(self.state_path)
            self.env["CLI_DELEGATION_STATE_SNAPSHOT"] = str(self.snapshot_path)
            self.env["CLI_DELEGATION_STATE_DIGEST"] = str(self.digest_path)
            self.env["CLI_DELEGATION_STATE_SIGNATURE"] = str(self.signature_path)
            self.env["CLI_SIGNATURE_METADATA"] = str(self.metadata_path)
            self.env["CLI_SIGNATURE_TELEMETRY"] = str(self.telemetry_path)
            self.env["CLI_RELEASE_SIGNING_KEY"] = SIGNATURE_KEY
            self.env["CLI_RELEASE_SIGNING_KEY_ID"] = "test-key"
            self.command = [sys.executable, "scripts/tools/check_cli_assets.py"]
            self._tarball_manifest_path = self._tarball_manifest()
            self._tarball_signature_path = self._tarball_signature()
            if self._tarball_signature_path.exists():
                original_signature = self._tarball_signature_path.read_bytes()

                def _restore_tarball_signature() -> None:
                    self._tarball_signature_path.write_bytes(original_signature)

                self.addCleanup(_restore_tarball_signature)
            self.addCleanup(lambda: self.metadata_path.unlink(missing_ok=True))
            self.addCleanup(lambda: self.telemetry_path.unlink(missing_ok=True))
            self._write_tarball_signature()

        def _run(self) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                env=self.env,
                check=False,
            )

        def _canonical_digest(self, payload: dict) -> str:
            canonical = dict(payload)
            canonical["updated_at"] = None
            return hashlib.sha256(
                json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest()

        def _signature_for(self, message: str) -> str:
            return hashlib.sha256(
                (SIGNATURE_KEY + "\n" + message).encode("utf-8")
            ).hexdigest()

        def _write_signature(self, recorded: str) -> str:
            signature = self._signature_for(recorded)
            self.signature_path.write_text(f"{signature}\n", encoding="utf-8")
            return signature

        def _write_state(self, payload: dict) -> None:
            self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        def _write_snapshot(self, payload: dict) -> None:
            self.snapshot_path.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )

        def _write_matching_manifest(self, payload: dict) -> tuple[str, str]:
            digest = self._canonical_digest(payload)
            recorded = f"{digest}  {self.snapshot_path.name}"
            self.digest_path.write_text(f"{recorded}\n", encoding="utf-8")
            signature = self._write_signature(recorded)
            return recorded, signature

        def _recovery_snapshot(self, payload: dict) -> dict:
            snapshot: dict[str, object] = {"enabled": bool(payload.get("enabled"))}
            code = str(payload.get("recovery_code") or "").strip()
            details = str(payload.get("recovery_details") or "").strip()
            if code:
                snapshot["code"] = code
            if details:
                snapshot["details"] = details
            effective_code = code or "cli_ready"
            prompt = "CLI delegation ready."
            if drop_reason_message is not None:
                try:
                    prompt = drop_reason_message(effective_code)  # type: ignore[arg-type]
                except Exception:
                    prompt = "CLI delegation ready."
            if details and effective_code in {
                "cli_recovered",
                "cli_signature_recovered",
            }:
                prompt = f"{prompt} (previous: {details})"
            snapshot["prompt"] = prompt
            return snapshot

        def _tarball_manifest(self) -> Path:
            system = platform.system().lower()
            machine = platform.machine().lower()
            arch_map = {
                "x86_64": "amd64",
                "amd64": "amd64",
                "arm64": "arm64",
                "aarch64": "arm64",
            }
            arch = arch_map.get(machine, machine)
            return Path(f"artifacts/cli/bar-{system}-{arch}.tar.gz.sha256")

        def _tarball_signature(self) -> Path:
            return self._tarball_manifest().with_suffix(".sha256.sig")

        def _tarball_recorded(self) -> str:
            manifest = self._tarball_manifest()
            return manifest.read_text(encoding="utf-8").strip()

        def _write_metadata(
            self, snapshot_recorded: str, snapshot_signature: str
        ) -> None:
            tarball_recorded = self._tarball_recorded()
            tarball_signature = (
                self._tarball_signature_path.read_text(encoding="utf-8").strip()
                if self._tarball_signature_path.exists()
                else ""
            )
            recovery_snapshot = None
            if self.snapshot_path.exists():
                try:
                    snapshot_payload = json.loads(
                        self.snapshot_path.read_text(encoding="utf-8")
                    )
                except Exception:
                    snapshot_payload = None
                if isinstance(snapshot_payload, dict):
                    recovery_snapshot = self._recovery_snapshot(snapshot_payload)
            metadata = {
                "signing_key_id": self.env["CLI_RELEASE_SIGNING_KEY_ID"],
                "tarball_manifest": {
                    "recorded": tarball_recorded,
                    "signature": tarball_signature,
                },
                "delegation_snapshot": {
                    "recorded": snapshot_recorded,
                    "signature": snapshot_signature,
                },
            }
            if recovery_snapshot is not None:
                metadata["cli_recovery_snapshot"] = recovery_snapshot
            self.metadata_path.write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )

        def _read_telemetry(self) -> dict:
            self.assertTrue(self.telemetry_path.exists(), "Telemetry file missing")
            return json.loads(self.telemetry_path.read_text(encoding="utf-8"))

        def _write_tarball_signature(self) -> str:
            recorded = self._tarball_recorded()
            signature = self._signature_for(recorded)
            self._tarball_signature_path.write_text(f"{signature}\n", encoding="utf-8")
            return signature

        def test_requires_delegation_state_file(self) -> None:
            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation state", result.stderr)

        def test_requires_delegation_state_snapshot(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self.digest_path.write_text(
                f"{self._canonical_digest(payload)}  {self.snapshot_path.name}\n",
                encoding="utf-8",
            )

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation state snapshot", result.stderr)

        def test_requires_delegation_state_digest(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self._write_snapshot(payload)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation state digest", result.stderr)

        def test_requires_enabled_state(self) -> None:
            payload = {
                "enabled": False,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": "probe failed; reached failure threshold 3",
                "source": "health_probe",
                "events": [
                    {
                        "reason": "probe failed; reached failure threshold 3",
                        "source": "health_probe",
                        "timestamp": "2026-01-03T00:00:00Z",
                    }
                ],
                "failure_count": 3,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self._write_snapshot(payload)
            recorded, signature = self._write_matching_manifest(payload)
            self._write_metadata(recorded, signature)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation disabled", result.stderr)

        def test_snapshot_digest_mismatch(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self._write_snapshot(payload)
            recorded = f"{'0' * 64}  {self.snapshot_path.name}"
            self.digest_path.write_text(f"{recorded}\n", encoding="utf-8")
            signature = self._write_signature(recorded)
            self._write_metadata(recorded, signature)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("snapshot digest mismatch", result.stderr)

        def test_fails_on_runtime_digest_mismatch(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            runtime_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T04:10:00Z",
                "reason": "manual override",
                "source": "health_probe",
                "events": [
                    {
                        "reason": "manual override",
                        "source": "operator",
                        "timestamp": "2026-01-03T04:10:00Z",
                    }
                ],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self._write_state(runtime_payload)
            self._write_metadata(recorded, signature)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("runtime delegation state digest mismatch", result.stderr)

        def test_requires_tarball_signature(self) -> None:
            manifest = self._tarball_manifest()
            signature = self._tarball_signature()
            recorded = self._tarball_recorded()
            original_signature = signature.read_bytes() if signature.exists() else None
            try:
                if signature.exists():
                    signature.unlink()
                result = self._run()
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertIn("tarball manifest signature", result.stderr)
            finally:
                if original_signature is not None:
                    signature.write_bytes(original_signature)
                else:
                    signature.write_text(
                        f"{self._signature_for(recorded)}\n", encoding="utf-8"
                    )

        def test_tarball_signature_mismatch(self) -> None:
            manifest = self._tarball_manifest()
            signature = self._tarball_signature()
            recorded = self._tarball_recorded()
            original_signature = signature.read_bytes() if signature.exists() else None
            try:
                signature.write_text("0" * 64 + "\n", encoding="utf-8")
                result = self._run()
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertIn("tarball manifest signature mismatch", result.stderr)
            finally:
                if original_signature is not None:
                    signature.write_bytes(original_signature)
                else:
                    signature.write_text(
                        f"{self._signature_for(recorded)}\n", encoding="utf-8"
                    )

        def test_requires_delegation_state_signature(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self._write_snapshot(payload)
            recorded, signature = self._write_matching_manifest(payload)
            self._write_metadata(recorded, signature)
            self.signature_path.unlink()

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("signature", result.stderr)

        def test_snapshot_signature_mismatch(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(payload)
            self._write_snapshot(payload)
            recorded, signature = self._write_matching_manifest(payload)
            self._write_metadata(recorded, signature)
            self.signature_path.write_text("0" * 64 + "\n", encoding="utf-8")

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("signature mismatch", result.stderr)

        def test_passes_with_healthy_state(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
                "recovery_code": "cli_signature_recovered",
                "recovery_details": "signature telemetry mismatch detected during bootstrap",
            }
            runtime_payload = dict(snapshot_payload)
            runtime_payload["updated_at"] = "2026-01-03T04:00:00Z"
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self._write_state(runtime_payload)
            self._write_metadata(recorded, signature)

            result = self._run()
            self.assertEqual(result.returncode, 0, result.stderr)
            stdout = result.stdout
            self.assertIn("all CLI assets present", stdout)
            self.assertIn(
                f"cli_tarball={self._tarball_manifest_path.with_suffix('')}", stdout
            )
            self.assertIn(f"cli_manifest={self._tarball_manifest_path}", stdout)
            self.assertIn(f"cli_signatures={self.metadata_path}", stdout)

            telemetry: dict = self._read_telemetry()
            self.assertEqual("green", telemetry["status"])
            self.assertEqual(
                self.env["CLI_RELEASE_SIGNING_KEY_ID"], telemetry["signing_key_id"]
            )
            self.assertEqual(
                telemetry["tarball_manifest"]["recorded"],
                self._tarball_recorded(),
            )
            self.assertEqual(
                telemetry["tarball_manifest"]["signature"],
                self._tarball_signature_path.read_text(encoding="utf-8").strip(),
            )
            self.assertEqual(
                telemetry["delegation_snapshot"]["recorded"],
                recorded,
            )
            self.assertEqual(
                telemetry["delegation_snapshot"]["signature"],
                signature,
            )
            recovery = telemetry.get("cli_recovery_snapshot")
            self.assertIsInstance(recovery, dict)
            recovery = dict(recovery or {})
            self.assertEqual(recovery.get("code"), "cli_signature_recovered")
            self.assertTrue(recovery.get("enabled"))
            self.assertIn(
                "signature telemetry mismatch detected during bootstrap",
                recovery.get("prompt", ""),
            )

            self.assertEqual(telemetry["delegation_snapshot"]["recorded"], recorded)
            self.assertEqual(telemetry["delegation_snapshot"]["signature"], signature)
            self.assertNotIn("previous", telemetry)
            self.assertFalse(telemetry.get("issues"))

        def test_signature_telemetry_mismatch_blocks_guard(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self._write_state(dict(snapshot_payload))
            self._write_metadata(recorded, signature)

            tarball_recorded = self._tarball_recorded()
            tarball_signature = self._tarball_signature_path.read_text(
                encoding="utf-8"
            ).strip()
            stale_payload = {
                "status": "green",
                "generated_at": "2026-01-03T00:00:00Z",
                "signing_key_id": "stale-key",
                "tarball_manifest": {
                    "recorded": tarball_recorded,
                    "signature": tarball_signature,
                },
                "delegation_snapshot": {
                    "recorded": recorded,
                    "signature": signature,
                },
            }
            self.telemetry_path.write_text(
                json.dumps(stale_payload, indent=2) + "\n", encoding="utf-8"
            )

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("signature telemetry signing_key_id mismatch", result.stderr)

            telemetry: dict = self._read_telemetry()
            self.assertEqual("red", telemetry["status"])
            self.assertEqual(
                self.env["CLI_RELEASE_SIGNING_KEY_ID"], telemetry["signing_key_id"]
            )
            issues = telemetry.get("issues") or []
            self.assertIn("signature telemetry signing_key_id mismatch", issues)
            previous = telemetry.get("previous")
            self.assertIsInstance(previous, dict)
            assert isinstance(previous, dict)
            self.assertEqual(previous["signing_key_id"], "stale-key")

        def test_requires_signature_metadata(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(dict(snapshot_payload))
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self.metadata_path.unlink(missing_ok=True)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("signature metadata", result.stderr)

        def test_signature_metadata_mismatch(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(dict(snapshot_payload))
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self._write_metadata(recorded, signature)
            # Corrupt metadata signature
            metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            metadata["tarball_manifest"]["signature"] = "0" * 64
            self.metadata_path.write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "signature metadata tarball signature mismatch", result.stderr
            )

        def test_signature_metadata_key_id_mismatch(self) -> None:
            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self._write_state(dict(snapshot_payload))
            self._write_snapshot(snapshot_payload)
            recorded, signature = self._write_matching_manifest(snapshot_payload)
            self._write_metadata(recorded, signature)
            metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            metadata["signing_key_id"] = "unexpected-key"
            self.metadata_path.write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("signing_key_id mismatch", result.stderr)
