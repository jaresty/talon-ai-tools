import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
            self.state_path = Path(self._tmp.name) / "delegation-state.json"
            self.env = os.environ.copy()
            self.env["CLI_DELEGATION_STATE"] = str(self.state_path)
            self.command = [sys.executable, "scripts/tools/check_cli_assets.py"]

        def _run(self) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                env=self.env,
                check=False,
            )

        def test_requires_delegation_state_file(self) -> None:
            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation state", result.stderr)

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
            self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            result = self._run()
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("delegation disabled", result.stderr)

        def test_passes_with_healthy_state(self) -> None:
            payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
            }
            self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            result = self._run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("all CLI assets present", result.stdout)
