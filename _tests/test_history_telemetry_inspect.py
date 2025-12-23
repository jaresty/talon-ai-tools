import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - Talon runtime fallback
    bootstrap = None
else:  # pragma: no cover - import side-effects only
    bootstrap()

if bootstrap is not None and not TYPE_CHECKING:

    class HistoryTelemetryInspectTests(unittest.TestCase):
        def test_inspect_outputs_guardrail_target(self) -> None:
            telemetry = {
                "guardrail_target": "request-history-guardrails-fast",
                "summary_path": "/tmp/history-validation-summary.json",
                "total_entries": 7,
                "gating_drop_total": 3,
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                telemetry_path = tmp_path / "history-validation-summary.telemetry.json"
                telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-telemetry-inspect.py",
                        str(telemetry_path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"history-telemetry-inspect failed: {result.stdout}\n{result.stderr}",
                )
                self.assertIn(
                    "guardrail_target: request-history-guardrails-fast",
                    result.stdout,
                )


if __name__ == "__main__":  # pragma: no cover - CLI entry
    unittest.main()
