import json
import tempfile
import unittest
from pathlib import Path

from talon_user.lib import requestLog
from talon_user.lib.modelState import GPTState
from talon_user.lib.telemetryExport import snapshot_telemetry


class TelemetryExportTests(unittest.TestCase):
    def setUp(self) -> None:
        requestLog.clear_history()
        requestLog.consume_gating_drop_stats()
        GPTState.last_suggest_skip_counts = {}

    def tearDown(self) -> None:
        requestLog.clear_history()
        requestLog.consume_gating_drop_stats()
        GPTState.last_suggest_skip_counts = {}

    def test_snapshot_telemetry_writes_expected_files(self) -> None:
        requestLog.append_entry(
            "req-1",
            "prompt",
            "response",
            axes={"directional": ["fog"]},
        )
        requestLog.record_gating_drop("in_flight", source="telemetry-export-test")
        GPTState.last_suggest_skip_counts = {"unknown_persona": 2, "unknown_intent": 1}

        with tempfile.TemporaryDirectory() as tmpdir:
            output = snapshot_telemetry(output_dir=tmpdir, reset_gating=True)

            history_path = Path(output["history"])
            streaming_path = Path(output["streaming"])
            telemetry_path = Path(output["telemetry"])
            skip_path = Path(output["suggestion_skip"])

            self.assertTrue(history_path.exists())
            self.assertTrue(streaming_path.exists())
            self.assertTrue(telemetry_path.exists())
            self.assertTrue(skip_path.exists())

            history_data = json.loads(history_path.read_text())
            self.assertIn("total_entries", history_data)
            self.assertEqual(history_data.get("total_entries"), 1)

            streaming_data = json.loads(streaming_path.read_text())
            self.assertEqual(streaming_data.get("status"), "unknown")

            telemetry_data = json.loads(telemetry_path.read_text())
            self.assertEqual(telemetry_data.get("total_entries"), 1)
            self.assertIn("suggestion_skip", telemetry_data)
            self.assertEqual(telemetry_data.get("suggestion_skip", {}).get("total"), 3)

            skip_data = json.loads(skip_path.read_text())
            self.assertEqual(skip_data.get("total_skipped"), 3)
            reasons = skip_data.get("reason_counts")
            self.assertIsInstance(reasons, list)
            self.assertEqual(len(reasons), 2)

            self.assertEqual(requestLog.gating_drop_stats(), {})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
