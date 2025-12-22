import importlib
import sys
import unittest

from talon import actions, app, cron, settings


class TelemetryExportSchedulerTests(unittest.TestCase):
    def setUp(self) -> None:
        actions.user.calls = []
        actions.app.calls = []
        cron.reset()
        app.reset()
        settings.reset()
        sys.modules.pop("talon_user.lib.telemetryExportScheduler", None)

    def _load_scheduler(self):
        return importlib.import_module("talon_user.lib.telemetryExportScheduler")

    def test_ready_event_schedules_and_exports(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 15)
        self._load_scheduler()
        app.trigger("ready")

        self.assertGreaterEqual(len(actions.user.calls), 1)
        self.assertEqual(
            actions.user.calls[0], ("model_export_telemetry", (False,), {})
        )
        self.assertTrue(cron.interval_calls)
        interval_spec, _ = cron.interval_calls[0]
        self.assertEqual(interval_spec, "15m")

    def test_disable_interval_skips_export(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 0)
        self._load_scheduler()
        app.trigger("ready")

        self.assertEqual(actions.user.calls, [])
        self.assertEqual(cron.interval_calls, [])

    def test_setting_change_reschedules_interval(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 10)
        self._load_scheduler()
        app.trigger("ready")

        self.assertTrue(cron.interval_calls)
        self.assertEqual(cron.interval_calls[0][0], "10m")
        actions.user.calls.clear()

        settings.set("user.guardrail_telemetry_export_interval_minutes", 5)
        self.assertEqual(len(cron.interval_calls), 1)
        self.assertEqual(cron.interval_calls[0][0], "5m")
        self.assertEqual(actions.user.calls, [])
