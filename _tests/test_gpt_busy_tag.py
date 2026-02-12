"""Specifying validation for gpt_busy Talon tag lifecycle
(ADR-035, ADR-0080 Workstream 3)."""

import types
import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.requestBus import (
        emit_begin_send,
        emit_complete,
        emit_fail,
        emit_cancel,
        emit_reset,
    )

    class GptBusyTagTests(unittest.TestCase):
        def setUp(self):
            import talon_user.lib.gptBusyTag as busy_tag
            self._busy_tag = busy_tag
            self._orig_ctx = busy_tag.ctx
            busy_tag.ctx = types.SimpleNamespace(tags=[])

        def tearDown(self):
            self._busy_tag.ctx = self._orig_ctx

        def test_sending_phase_sets_busy_tag(self) -> None:
            """update() with SENDING phase must add user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.update(RequestState(phase=RequestPhase.SENDING))
            self.assertIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_streaming_phase_sets_busy_tag(self) -> None:
            """update() with STREAMING phase must add user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.update(RequestState(phase=RequestPhase.STREAMING))
            self.assertIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_done_phase_clears_busy_tag(self) -> None:
            """update() with DONE phase must remove user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.ctx.tags = ["user.gpt_busy"]
            self._busy_tag.update(RequestState(phase=RequestPhase.DONE))
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_idle_phase_clears_busy_tag(self) -> None:
            """update() with IDLE phase must remove user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.ctx.tags = ["user.gpt_busy"]
            self._busy_tag.update(RequestState(phase=RequestPhase.IDLE))
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_error_phase_clears_busy_tag(self) -> None:
            """update() with ERROR phase must remove user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.ctx.tags = ["user.gpt_busy"]
            self._busy_tag.update(RequestState(phase=RequestPhase.ERROR))
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_cancelled_phase_clears_busy_tag(self) -> None:
            """update() with CANCELLED phase must remove user.gpt_busy."""
            from talon_user.lib.historyLifecycle import RequestPhase, RequestState
            self._busy_tag.ctx.tags = ["user.gpt_busy"]
            self._busy_tag.update(RequestState(phase=RequestPhase.CANCELLED))
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_bus_begin_send_sets_busy_tag(self) -> None:
            """Integration: bus emit_begin_send must set user.gpt_busy via state change."""
            from talon_user.lib import requestUI
            with patch.object(requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()):
                requestUI.register_default_request_ui()
                emit_begin_send("rid-busy-send")
            self.assertIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_bus_complete_clears_busy_tag(self) -> None:
            """Integration: bus emit_complete must clear user.gpt_busy via state change."""
            from talon_user.lib import requestUI
            with patch.object(requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()):
                requestUI.register_default_request_ui()
                emit_begin_send("rid-busy-done")
            self.assertIn("user.gpt_busy", self._busy_tag.ctx.tags)
            with patch.object(requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()):
                emit_complete("rid-busy-done")
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

        def test_bus_fail_clears_busy_tag(self) -> None:
            """Integration: bus emit_fail must clear user.gpt_busy via state change."""
            from talon_user.lib import requestUI
            with patch.object(requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()):
                requestUI.register_default_request_ui()
                emit_begin_send("rid-busy-fail")
            with patch.object(requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()):
                emit_fail("boom", request_id="rid-busy-fail")
            self.assertNotIn("user.gpt_busy", self._busy_tag.ctx.tags)

else:
    if not TYPE_CHECKING:

        class GptBusyTagTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
