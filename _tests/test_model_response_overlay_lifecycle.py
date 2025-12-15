import types

import pytest


def test_response_toggle_calls_common_closers(monkeypatch):
    import talon_user.lib.modelResponseCanvas as mod

    calls = []

    def fake_close_common(actions_obj, exclude=None, extra=None):
        calls.append({"actions": actions_obj, "exclude": set(exclude or ()), "extra": tuple(extra or ())})

    # Patch close_common_overlays to observe calls.
    monkeypatch.setattr(mod, "close_common_overlays", fake_close_common)

    # Stub actions/user with minimal closers to avoid attribute errors.
    class DummyUser:
        def model_response_canvas_close(self):
            calls.append("response_close_direct")

    class DummyActions:
        user = DummyUser()

    monkeypatch.setattr(mod, "actions", DummyActions())

    # Stub canvas creation/show/hide.
    class DummyCanvas:
        def show(self):
            calls.append("show")

        def hide(self):
            calls.append("hide")

    monkeypatch.setattr(mod, "_response_canvas", DummyCanvas())
    monkeypatch.setattr(mod, "_ensure_response_canvas", lambda: mod._response_canvas)

    # Patch guards/state
    monkeypatch.setattr(mod, "_guard_response_canvas", lambda allow_inflight=False: False)
    monkeypatch.setattr(
        mod,
        "ResponseCanvasState",
        types.SimpleNamespace(showing=False, scroll_y=0.0, meta_expanded=False),
    )
    monkeypatch.setattr(
        mod,
        "GPTState",
        types.SimpleNamespace(last_response="resp", text_to_confirm="", thread=[]),
    )
    # State to simulate idle request.
    class DummyState:
        phase = getattr(mod.RequestPhase, "IDLE", None)

    monkeypatch.setattr(mod, "_current_request_state", lambda: DummyState())
    monkeypatch.setattr(mod, "_prefer_canvas_progress", lambda: False)

    # Exercise toggle (should open and call common closers, excluding self).
    mod.UserActions.model_response_canvas_toggle()

    close_calls = [c for c in calls if isinstance(c, dict)]
    assert close_calls, "expected close_common_overlays call"
    assert close_calls[0]["exclude"] == {"model_response_canvas_close"}
    assert "show" in calls
    # Toggle again to close.
    mod.UserActions.model_response_canvas_toggle()
    assert "hide" in calls
