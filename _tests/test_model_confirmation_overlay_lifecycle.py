import types

import pytest


def test_confirmation_close_uses_common_overlay_closer(monkeypatch):
    import talon_user.lib.modelConfirmationGUI as mod

    calls = []

    def fake_close_common(actions_obj, exclude=None, extra=None):
        calls.append(
            {
                "actions": actions_obj,
                "exclude": set(exclude or []),
                "extra": tuple(extra or ()),
            }
        )

    # Patch close_common_overlays to observe calls.
    monkeypatch.setattr(mod, "close_common_overlays", fake_close_common)

    # Provide a minimal actions/user stub.
    class DummyUser:
        def model_response_canvas_close(self):
            calls.append("response_close")

    class DummyActions:
        user = DummyUser()

    monkeypatch.setattr(mod, "actions", DummyActions())

    # Patch confirmation_gui.hide to avoid Talon imgui dependency.
    class DummyConfirmation:
        def hide(self):
            calls.append("hide")

    monkeypatch.setattr(mod, "confirmation_gui", DummyConfirmation())

    # Patch ctx.tags container.
    monkeypatch.setattr(mod, "ctx", types.SimpleNamespace(tags=[]))

    # Patch GPTState with minimal fields used.
    monkeypatch.setattr(
        mod,
        "GPTState",
        types.SimpleNamespace(text_to_confirm="text", thread=[]),
    )

    # Run via action class method.
    mod.UserActions.confirmation_gui_close()

    # Assertions
    assert mod.GPTState.text_to_confirm == ""
    close_calls = [c for c in calls if isinstance(c, dict)]
    assert close_calls, "close_common_overlays should be called"
    assert close_calls[0]["exclude"] == {"confirmation_gui_close"}
    assert isinstance(close_calls[0]["actions"], DummyUser)
    assert "hide" in calls
    # Response close should not be invoked directly; handled via common overlays.
    assert "response_close" not in calls
