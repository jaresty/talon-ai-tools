import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIGNATURE_KEY = "adr-0063-cli-release-signature"

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
            self.env = os.environ.copy()
            self.env["CLI_DELEGATION_STATE"] = str(self.state_path)
            self.env["CLI_DELEGATION_STATE_SNAPSHOT"] = str(self.snapshot_path)
            self.env["CLI_DELEGATION_STATE_DIGEST"] = str(self.digest_path)
            self.env["CLI_DELEGATION_STATE_SIGNATURE"] = str(self.signature_path)
            self.command = [sys.executable, "scripts/tools/check_cli_assets.py"]

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

        def _write_signature(self, recorded: str) -> None:
            self.signature_path.write_text(
                f"{self._signature_for(recorded)}\n", encoding="utf-8"
            )

        def _write_state(self, payload: dict) -> None:
            self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        def _write_snapshot(self, payload: dict) -> None:
            self.snapshot_path.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )

        def _write_matching_manifest(self, payload: dict) -> None:
            digest = self._canonical_digest(payload)
            recorded = f"{digest}  {self.snapshot_path.name}"
            self.digest_path.write_text(f"{recorded}\n", encoding="utf-8")
            self._write_signature(recorded)

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
            self._write_matching_manifest(payload)

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
            self._write_signature(recorded)

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
            self._write_matching_manifest(snapshot_payload)
            self._write_state(runtime_payload)

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("runtime delegation state digest mismatch", result.stderr)

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
            self._write_matching_manifest(payload)
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
            self._write_matching_manifest(payload)
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
            }
            runtime_payload = dict(snapshot_payload)
            runtime_payload["updated_at"] = "2026-01-03T04:00:00Z"
            self._write_snapshot(snapshot_payload)
            self._write_matching_manifest(snapshot_payload)
            self._write_state(runtime_payload)

            result = self._run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("all CLI assets present", result.stdout)
