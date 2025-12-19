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

    class HistoryAxisExportTelemetryTests(unittest.TestCase):
        def test_falls_back_to_counts_when_total_missing(self) -> None:
            summary = {
                "total_entries": 5,
                "gating_drop_total": 0,
                "streaming_gating_summary": {
                    "counts": {
                        "streaming_disabled": 2,
                        "rate_limited": 1,
                    },
                    # deliberately omit `total` to exercise fallback behaviour
                },
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                summary_path = tmp_path / "history-validation-summary.json"
                output_path = tmp_path / "telemetry.json"
                summary_path.write_text(json.dumps(summary), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-export-telemetry.py",
                        str(summary_path),
                        "--output",
                        str(output_path),
                        "--top",
                        "1",
                        "--pretty",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"telemetry exporter failed: {result.stdout}\n{result.stderr}",
                )
                payload = json.loads(output_path.read_text(encoding="utf-8"))
                self.assertEqual(payload.get("total_entries"), 5)
                self.assertEqual(payload.get("gating_drop_total"), 3)
                self.assertEqual(
                    payload.get("top_gating_reasons"),
                    [{"reason": "streaming_disabled", "count": 2}],
                )
                self.assertEqual(payload.get("other_gating_drops"), 1)

else:

    class HistoryAxisExportTelemetryTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in Talon runtime")
        def test_placeholder(self) -> None:
            pass
