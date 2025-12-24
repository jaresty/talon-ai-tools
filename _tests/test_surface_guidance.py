import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.surfaceGuidance import guard_surface_request
else:  # pragma: no cover - Talon runtime shim
    GPTState = None  # type: ignore[assignment]
    guard_surface_request = None  # type: ignore[assignment]

if guard_surface_request is None:  # pragma: no cover - Talon runtime shim

    def _unavailable_guard(*_args, **_kwargs):
        raise RuntimeError("surfaceGuidance unavailable in Talon runtime")

    guard_surface_request = _unavailable_guard  # type: ignore[assignment]


@unittest.skipIf(bootstrap is None, "Tests disabled inside Talon runtime")
class SurfaceGuidanceTests(unittest.TestCase):
    def setUp(self) -> None:
        if hasattr(GPTState, "suppress_overlay_inflight_guard"):
            delattr(GPTState, "suppress_overlay_inflight_guard")

    def tearDown(self) -> None:
        if hasattr(GPTState, "suppress_overlay_inflight_guard"):
            delattr(GPTState, "suppress_overlay_inflight_guard")

    def test_guard_clears_drop_reason_when_allowed(self) -> None:
        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(True, ""),
            ) as try_begin,
            patch("talon_user.lib.surfaceGuidance.last_drop_reason", return_value=""),
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_drop,
        ):
            blocked = guard_surface_request(
                surface="suggestion", source="modelSuggestionGUI"
            )  # type: ignore[misc]
        try_begin.assert_called_once_with(source="modelSuggestionGUI")
        set_drop.assert_called_once_with("")
        self.assertFalse(blocked)

    def test_guard_blocks_and_notifies_when_inflight(self) -> None:
        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(False, "in_flight"),
            ) as try_begin,
            patch(
                "talon_user.lib.surfaceGuidance.render_drop_reason",
                return_value="busy",
            ) as render_reason,
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_drop,
            patch("talon_user.lib.surfaceGuidance.notify") as notify,
        ):
            blocked = guard_surface_request(
                surface="suggestion", source="modelSuggestionGUI"
            )  # type: ignore[misc]
        try_begin.assert_called_once_with(source="modelSuggestionGUI")
        render_reason.assert_called_once_with("in_flight")
        set_drop.assert_called_once_with("in_flight", "busy")
        notify.assert_called_once_with("busy")
        self.assertTrue(blocked)

    def test_guard_honours_suppression_flag(self) -> None:
        setattr(GPTState, "suppress_overlay_inflight_guard", True)
        with patch("talon_user.lib.surfaceGuidance.try_begin_request") as try_begin:
            blocked = guard_surface_request(
                surface="suggestion",
                source="modelSuggestionGUI",
                suppress_attr="suppress_overlay_inflight_guard",
            )  # type: ignore[misc]
        try_begin.assert_not_called()
        self.assertFalse(blocked)
