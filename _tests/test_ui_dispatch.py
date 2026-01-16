import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - unavailable in Talon runtime
    bootstrap = None
else:  # pragma: no cover - exercised only in test harness
    bootstrap()


class UIDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if bootstrap is None:
            raise unittest.SkipTest("Test harness unavailable outside unittest runs")
        from talon_user.lib import uiDispatch as dispatch_module

        cls._ui_dispatch = dispatch_module

    def setUp(self):
        self.ui_dispatch = self.__class__._ui_dispatch
        self.ui_dispatch.cron.after_calls = []
        with self.ui_dispatch._queue_lock:
            self.ui_dispatch._queue.clear()
        self.ui_dispatch._schedule_failed = False
        self.ui_dispatch._fallback_warned = False
        self.ui_dispatch._fallback_next_probe = 0.0
        self.ui_dispatch._draining = False
        with self.ui_dispatch._inline_counts_lock:
            self.ui_dispatch._inline_fallback_counts.clear()
            self.ui_dispatch._inline_fallback_last_timestamp = 0.0
            self.ui_dispatch._inline_fallback_last_wallclock = 0.0
        self.ui_dispatch._fallback_notified = False

    def test_dispatch_uses_cron_after(self):
        called = []

        def fn():
            called.append(True)

        with patch.object(self.ui_dispatch.cron, "after") as after:
            after.side_effect = lambda delay, cb: cb()
            self.ui_dispatch.run_on_ui_thread(fn, delay_ms=15)
            self.ui_dispatch._drain_for_tests()

        self.assertTrue(called)
        self.assertFalse(self.ui_dispatch.ui_dispatch_fallback_active())

    def test_dispatch_falls_back_on_cron_failure(self):
        called = []

        def fn():
            called.append(True)

        with patch.object(
            self.ui_dispatch.cron, "after", side_effect=Exception("boom")
        ) as after:
            self.ui_dispatch.run_on_ui_thread(fn)

        self.assertTrue(called)
        self.assertTrue(self.ui_dispatch.ui_dispatch_fallback_active())
        self.assertEqual(after.call_count, 1)

    def test_inline_mode_probes_after_interval(self):
        called_steps = []

        def make_fn(tag):
            return lambda: called_steps.append(tag)

        fake_time = [0.0]

        def monotonic_stub():
            return fake_time[0]

        with patch.object(self.ui_dispatch.time, "monotonic", monotonic_stub):
            # Initial failure triggers fallback mode and drains inline.
            with patch.object(
                self.ui_dispatch.cron, "after", side_effect=Exception("boom")
            ) as after_fail:
                self.ui_dispatch.run_on_ui_thread(make_fn("fail"))
            self.assertTrue(self.ui_dispatch.ui_dispatch_fallback_active())
            self.assertEqual(after_fail.call_count, 1)

            # Before the probe interval elapses we should not retry cron scheduling.
            with patch.object(self.ui_dispatch.cron, "after") as after_pause:
                self.ui_dispatch.run_on_ui_thread(make_fn("inline"))
            self.assertTrue(self.ui_dispatch.ui_dispatch_fallback_active())
            self.assertFalse(after_pause.called)

            # Advance time beyond probe interval and ensure we attempt to reschedule.
            fake_time[0] = self.ui_dispatch._fallback_next_probe + 0.5
            with patch.object(self.ui_dispatch.cron, "after") as after_recover:
                after_recover.side_effect = lambda delay, cb: cb()
                self.ui_dispatch.run_on_ui_thread(make_fn("probe"))
            self.assertFalse(self.ui_dispatch.ui_dispatch_fallback_active())
            self.assertEqual(after_recover.call_count, 1)

        # Once recovered we should enqueue and schedule via cron again.
        with patch.object(self.ui_dispatch.cron, "after") as after_normal:
            after_normal.side_effect = lambda delay, cb: cb()
            self.ui_dispatch.run_on_ui_thread(make_fn("normal"))
            self.ui_dispatch._drain_for_tests()
        self.assertEqual(after_normal.call_count, 1)
        self.assertEqual(
            called_steps,
            [
                "fail",
                "inline",
                "probe",
                "normal",
            ],
        )

    def test_dispatch_swallows_fn_exceptions(self):
        # Should not raise when fn errors.
        self.ui_dispatch.run_on_ui_thread(
            lambda: (_ for _ in ()).throw(Exception("kaboom"))
        )
        self.ui_dispatch._drain_for_tests()

    def test_inline_stats_tracks_fallback_usage(self):
        fake_monotonic = [10.0]
        fake_wallclock = [1_700_000_000.0]

        def monotonic_stub():
            return fake_monotonic[0]

        def time_stub():
            return fake_wallclock[0]

        with (
            patch.object(self.ui_dispatch, "_notify_inline_fallback") as notify,
            patch.object(self.ui_dispatch.time, "monotonic", monotonic_stub),
            patch.object(self.ui_dispatch.time, "time", time_stub),
            patch.object(
                self.ui_dispatch.cron, "after", side_effect=Exception("boom")
            ) as after_fail,
        ):
            self.ui_dispatch.run_on_ui_thread(lambda: None)

        notify.assert_called_once()
        self.assertTrue(self.ui_dispatch.ui_dispatch_fallback_active())
        self.assertEqual(after_fail.call_count, 1)

        fake_monotonic[0] = 22.5

        stats = self.ui_dispatch.ui_dispatch_inline_stats()
        self.assertEqual(stats["counts"], {"0": 1})
        self.assertEqual(stats["total"], 1)
        self.assertAlmostEqual(stats["last_monotonic"], 10.0)
        self.assertEqual(stats["active"], True)
        self.assertIsNotNone(stats["seconds_since_last"])
        self.assertGreater(stats["seconds_since_last"], 0)
        self.assertEqual(stats["last_wall_time"], "2023-11-14T22:13:20Z")

        reset_stats = self.ui_dispatch.ui_dispatch_inline_stats(reset=True)
        self.assertEqual(reset_stats["counts"], {"0": 1})

        post_reset = self.ui_dispatch.ui_dispatch_inline_stats()
        self.assertEqual(post_reset["counts"], {})
        self.assertEqual(post_reset["total"], 0)
