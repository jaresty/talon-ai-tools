import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import talon_user.lib.telemetryExport as telemetry_module
from talon_user.lib import requestLog
from talon_user.lib import telemetryExportScheduler as scheduler
from talon_user.lib.modelState import GPTState
from talon_user.lib.telemetryExport import snapshot_telemetry


class TelemetryExportTests(unittest.TestCase):
    def setUp(self) -> None:
        requestLog.clear_history()
        requestLog.consume_gating_drop_stats()
        GPTState.last_suggest_skip_counts = {}
        scheduler._reset_for_tests()

    def tearDown(self) -> None:
        requestLog.clear_history()
        requestLog.consume_gating_drop_stats()
        GPTState.last_suggest_skip_counts = {}
        scheduler._reset_for_tests()

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
            self.assertIn("scheduler", telemetry_data)
            scheduler_payload = telemetry_data["scheduler"]
            self.assertIsInstance(scheduler_payload, dict)
            self.assertIn("reschedule_count", scheduler_payload)

            skip_data = json.loads(skip_path.read_text())
            self.assertEqual(skip_data.get("total_skipped"), 3)
            reasons = skip_data.get("reason_counts")
            self.assertIsInstance(reasons, list)
            self.assertEqual(len(reasons), 2)

            self.assertEqual(requestLog.gating_drop_stats(), {})

    def test_snapshot_telemetry_delegates_to_history_lifecycle(self) -> None:
        lifecycle_stats = {
            "total_entries": 0,
            "gating_drop_total": 0,
            "gating_drop_last_message": "",
            "gating_drop_last_code": "",
            "streaming_gating_summary": {},
        }

        with (
            patch.object(
                telemetry_module, "historyLifecycle", create=True
            ) as lifecycle,
            patch.object(telemetry_module, "requestLog", create=True) as requestlog,
        ):
            lifecycle.history_validation_stats.return_value = dict(lifecycle_stats)
            lifecycle.consume_gating_drop_stats.return_value = {}
            requestlog.history_validation_stats.side_effect = AssertionError(
                "telemetryExport should use historyLifecycle"
            )
            requestlog.consume_gating_drop_stats.side_effect = AssertionError(
                "telemetryExport should use historyLifecycle"
            )

            with tempfile.TemporaryDirectory() as tmpdir:
                snapshot_telemetry(output_dir=tmpdir, reset_gating=True)

        lifecycle.history_validation_stats.assert_called_once_with()
        lifecycle.consume_gating_drop_stats.assert_called_once_with()


class TelemetryExportCommandTests(unittest.TestCase):
    def test_export_model_telemetry_notifies_success(self) -> None:
        from talon_user.lib import telemetryExportCommand as command

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            fake_result = {
                "history": temp_path / "history.json",
                "streaming": temp_path / "history.streaming.json",
                "telemetry": temp_path / "history.telemetry.json",
                "suggestion_skip": temp_path / "suggestion.json",
            }
            for path in fake_result.values():
                path.write_text("{}", encoding="utf-8")

            with (
                patch.object(telemetry_module, "DEFAULT_OUTPUT_DIR", temp_path),
                patch.object(command, "DEFAULT_OUTPUT_DIR", temp_path),
            ):
                with (
                    patch.object(
                        command, "snapshot_telemetry", return_value=fake_result
                    ) as snapshot,
                    patch.object(command.app, "notify") as notify,
                ):
                    result = command.export_model_telemetry(
                        reset_gating=True, notify_user=True
                    )

                    snapshot.assert_called_once_with(
                        output_dir=temp_path,
                        reset_gating=True,
                        top_n=command.DEFAULT_TOP_N,
                    )
                    notify.assert_called_once()
                    message = notify.call_args.args[0]
                    self.assertIn("reset", message)
                    self.assertEqual(result, fake_result)

                    marker_path = temp_path / "talon-export-marker.json"
                    self.assertTrue(marker_path.exists())
                    marker_payload = json.loads(marker_path.read_text(encoding="utf-8"))
                    self.assertTrue(marker_payload.get("reset_gating"))
                    self.assertIn("scheduler", marker_payload)

    def test_export_model_telemetry_handles_reset(self) -> None:
        from talon_user.lib import telemetryExportCommand as command

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            with (
                patch.object(telemetry_module, "DEFAULT_OUTPUT_DIR", temp_path),
                patch.object(command, "DEFAULT_OUTPUT_DIR", temp_path),
            ):
                with (
                    patch.object(
                        command, "snapshot_telemetry", return_value={}
                    ) as snapshot,
                    patch.object(command.app, "notify") as notify,
                    patch.object(scheduler, "get_scheduler_stats", return_value=None),
                ):
                    command.export_model_telemetry(reset_gating=False, notify_user=True)

        snapshot.assert_called_once_with(
            output_dir=temp_path,
            reset_gating=False,
            top_n=command.DEFAULT_TOP_N,
        )
        notify.assert_called_once()
        self.assertNotIn("reset", notify.call_args.args[0])

    def test_export_model_telemetry_notifies_failure(self) -> None:
        from talon_user.lib import telemetryExportCommand as command

        exc = RuntimeError("boom")
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            with (
                patch.object(telemetry_module, "DEFAULT_OUTPUT_DIR", temp_path),
                patch.object(command, "DEFAULT_OUTPUT_DIR", temp_path),
            ):
                with (
                    patch.object(command, "snapshot_telemetry", side_effect=exc),
                    patch.object(command.app, "notify") as notify,
                    patch.object(scheduler, "get_scheduler_stats", return_value=None),
                ):
                    with self.assertRaises(RuntimeError):
                        command.export_model_telemetry(
                            reset_gating=False, notify_user=True
                        )

        notify.assert_called_once()
        self.assertIn("failed", notify.call_args.args[0])

    def test_action_invokes_helper(self) -> None:
        from talon_user.lib import telemetryExportCommand as command

        with patch.object(command, "export_model_telemetry") as export:
            export.return_value = {}
            command.UserActions.model_export_telemetry()
        export.assert_called_once_with(reset_gating=True, notify_user=True)

        with patch.object(command, "export_model_telemetry") as export_false:
            export_false.return_value = {}
            command.UserActions.model_export_telemetry(False)
        export_false.assert_called_once_with(reset_gating=False, notify_user=True)

    def test_default_output_dir_is_repo_root(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expected = repo_root / "artifacts" / "telemetry"
        self.assertEqual(telemetry_module.DEFAULT_OUTPUT_DIR, expected)
        self.assertTrue(telemetry_module.DEFAULT_OUTPUT_DIR.is_absolute())

    def test_export_model_telemetry_respects_default_directory(self) -> None:
        from talon_user.lib import telemetryExportCommand as command

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            with (
                patch.object(telemetry_module, "DEFAULT_OUTPUT_DIR", temp_path),
                patch.object(command, "DEFAULT_OUTPUT_DIR", temp_path),
                patch.object(scheduler, "get_scheduler_stats", return_value=None),
            ):
                result = command.export_model_telemetry(
                    reset_gating=False, notify_user=False
                )

                for path in result.values():
                    self.assertTrue(path.is_absolute())
                    self.assertTrue(str(path).startswith(str(temp_path)))
                    self.assertTrue(path.exists())

                marker_path = temp_path / "talon-export-marker.json"
                self.assertTrue(marker_path.exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
