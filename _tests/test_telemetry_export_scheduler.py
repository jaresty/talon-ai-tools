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
        module = importlib.import_module("talon_user.lib.telemetryExportScheduler")
        module._reset_for_tests()
        return module

    def test_ready_event_schedules_and_exports(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 15)
        scheduler = self._load_scheduler()
        app.trigger("ready")

        self.assertGreaterEqual(len(actions.user.calls), 1)
        self.assertEqual(
            actions.user.calls[0], ("model_export_telemetry", (False,), {})
        )
        self.assertTrue(cron.interval_calls)
        interval_spec, _ = cron.interval_calls[0]
        self.assertEqual(interval_spec, "15m")

        stats = scheduler.get_scheduler_stats()
        self.assertEqual(stats["reschedule_count"], 1)
        self.assertEqual(stats["last_interval_minutes"], 15)
        self.assertEqual(stats["last_reason"], "enabled")

    def test_disable_interval_skips_export(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 0)
        scheduler = self._load_scheduler()
        app.trigger("ready")

        self.assertEqual(actions.user.calls, [])
        self.assertEqual(cron.interval_calls, [])
        stats = scheduler.get_scheduler_stats()
        self.assertEqual(stats["reschedule_count"], 0)

    def test_setting_change_reschedules_interval(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 10)
        scheduler = self._load_scheduler()
        app.trigger("ready")

        self.assertTrue(cron.interval_calls)
        self.assertEqual(cron.interval_calls[0][0], "10m")
        actions.user.calls.clear()

        stats = scheduler.get_scheduler_stats()
        self.assertEqual(stats["reschedule_count"], 1)
        self.assertEqual(stats["last_interval_minutes"], 10)
        self.assertEqual(stats["last_reason"], "enabled")

        settings.set("user.guardrail_telemetry_export_interval_minutes", 5)
        self.assertEqual(len(cron.interval_calls), 1)
        self.assertEqual(cron.interval_calls[0][0], "5m")
        self.assertEqual(actions.user.calls, [])

        stats = scheduler.get_scheduler_stats()
        self.assertEqual(stats["reschedule_count"], 2)
        self.assertEqual(stats["last_interval_minutes"], 5)
        self.assertEqual(stats["last_reason"], "updated")

    def test_disabling_after_enable_records_stats(self) -> None:
        settings.set("user.guardrail_telemetry_export_interval_minutes", 20)
        scheduler = self._load_scheduler()
        app.trigger("ready")
        settings.set("user.guardrail_telemetry_export_interval_minutes", 0)

        stats = scheduler.get_scheduler_stats()
        self.assertEqual(stats["reschedule_count"], 2)
        self.assertIsNone(stats["last_interval_minutes"])
        self.assertEqual(stats["last_reason"], "disabled")
