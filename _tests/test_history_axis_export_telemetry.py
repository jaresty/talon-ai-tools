import json
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
                "gating_drop_last_message": "Streaming disabled guardrail",
                "gating_drop_last_code": "streaming_disabled",
                "streaming_gating_summary": {
                    "counts": {
                        "streaming_disabled": 2,
                        "rate_limited": 1,
                    },
                    "sources": {
                        "modelHelpCanvas": 2,
                        "providerCommands": 1,
                    },
                    "last": {"reason": "streaming_disabled", "reason_count": 2},
                    "last_message": "Streaming disabled guardrail",
                    "last_code": "streaming_disabled",
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
                self.assertEqual(
                    payload.get("top_gating_sources"),
                    [{"source": "modelHelpCanvas", "count": 2}],
                )
                self.assertEqual(payload.get("other_gating_source_drops"), 1)
                self.assertEqual(payload.get("streaming_status"), "unknown")
                self.assertEqual(payload.get("summary_path"), str(summary_path))
                self.assertEqual(
                    payload.get("last_drop_message"), "Streaming disabled guardrail"
                )
                self.assertEqual(payload.get("last_drop_code"), "streaming_disabled")
                self.assertEqual(
                    payload.get("streaming_last_drop_message"),
                    "Streaming disabled guardrail",
                )
                self.assertEqual(
                    payload.get("streaming_last_drop_code"), "streaming_disabled"
                )

        def test_preserves_artifact_url_when_provided(self) -> None:
            summary = {
                "total_entries": 2,
                "streaming_gating_summary": {
                    "total": 2,
                    "counts_sorted": [
                        {"reason": "streaming_disabled", "count": 1},
                        {"reason": "rate_limited", "count": 1},
                    ],
                },
            }
            artifact_url = "https://example.com/artifacts/42"

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
                        "--artifact-url",
                        artifact_url,
                        "--top",
                        "1",
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
                self.assertEqual(payload.get("gating_drop_total"), 2)
                self.assertEqual(payload.get("artifact_url"), artifact_url)
                self.assertEqual(
                    payload.get("top_gating_reasons"),
                    [{"reason": "streaming_disabled", "count": 1}],
                )
                self.assertEqual(payload.get("other_gating_drops"), 1)
                self.assertEqual(payload.get("top_gating_sources"), [])
                self.assertFalse(payload.get("other_gating_source_drops"))
                self.assertEqual(payload.get("streaming_status"), "unknown")
                self.assertEqual(payload.get("summary_path"), str(summary_path))
                self.assertEqual(payload.get("last_drop_message"), "none")
                self.assertIsNone(payload.get("last_drop_code"))
                self.assertEqual(payload.get("streaming_last_drop_message"), "none")
                self.assertIsNone(payload.get("streaming_last_drop_code"))

        def test_stdout_mode_emits_json_payload(self) -> None:
            summary = {
                "total_entries": 1,
                "streaming_gating_summary": {
                    "total": 1,
                    "counts": {"rate_limited": 1},
                },
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                summary_path = Path(tmpdir) / "history-validation-summary.json"
                summary_path.write_text(json.dumps(summary), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-export-telemetry.py",
                        str(summary_path),
                        "--top",
                        "5",
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
                self.assertIn("gating_drop_total", result.stdout, msg=result.stdout)
                payload = json.loads(result.stdout)
                self.assertEqual(payload.get("total_entries"), 1)
                self.assertEqual(payload.get("gating_drop_total"), 1)
                self.assertEqual(
                    payload.get("top_gating_reasons"),
                    [{"reason": "rate_limited", "count": 1}],
                )
                self.assertEqual(payload.get("top_gating_sources"), [])
                self.assertEqual(payload.get("streaming_status"), "unknown")
                self.assertEqual(payload.get("summary_path"), str(summary_path))
                self.assertEqual(payload.get("last_drop_message"), "none")
                self.assertIsNone(payload.get("last_drop_code"))
                self.assertEqual(payload.get("streaming_last_drop_message"), "none")
                self.assertIsNone(payload.get("streaming_last_drop_code"))

        def test_includes_gating_drop_rate(self) -> None:
            summary = {
                "total_entries": 10,
                "streaming_gating_summary": {
                    "total": 3,
                    "counts_sorted": [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
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
                        "5",
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
                self.assertEqual(payload.get("gating_drop_total"), 3)
                self.assertAlmostEqual(payload.get("gating_drop_rate"), 0.3, places=4)
                self.assertEqual(payload.get("top_gating_sources"), [])
                self.assertEqual(payload.get("streaming_status"), "unknown")
                self.assertEqual(payload.get("summary_path"), str(summary_path))
                self.assertEqual(payload.get("last_drop_message"), "none")
                self.assertIsNone(payload.get("last_drop_code"))

else:

    class HistoryAxisExportTelemetryTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in Talon runtime")
        def test_placeholder(self) -> None:
            pass
