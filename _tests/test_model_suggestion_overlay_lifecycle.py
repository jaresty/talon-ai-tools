import types


def test_suggestion_open_calls_common_closers(monkeypatch):
    import talon_user.lib.modelSuggestionGUI as mod

    calls = []

    def fake_close_common(actions_obj, exclude=None, extra=None):
        calls.append({"actions": actions_obj, "exclude": set(exclude or ()), "extra": tuple(extra or ())})

    # Patch lifecycle helper and inflight guard.
    monkeypatch.setattr(mod, "close_common_overlays", fake_close_common)
    monkeypatch.setattr(mod, "_reject_if_request_in_flight", lambda: False)

    # Stub suggestion state and refresh.
    suggestions = [{"prompt": "p", "description": "d"}]
    monkeypatch.setattr(mod, "SuggestionGUIState", types.SimpleNamespace(suggestions=suggestions))

    def fake_refresh():
        mod.SuggestionGUIState.suggestions = suggestions

    monkeypatch.setattr(mod, "_refresh_suggestions_from_state", fake_refresh)

    # Dummy actions/user and canvas.
    class DummyActions:
        user = types.SimpleNamespace()
        app = types.SimpleNamespace(notify=lambda msg: calls.append(("notify", msg)))

    class DummyCanvas:
        def show(self):
            calls.append("show")

        def hide(self):
            calls.append("hide")

    monkeypatch.setattr(mod, "actions", DummyActions())
    monkeypatch.setattr(mod, "_suggestion_canvas", DummyCanvas())
    monkeypatch.setattr(mod, "_ensure_suggestion_canvas", lambda: mod._suggestion_canvas)
    monkeypatch.setattr(mod, "ctx", types.SimpleNamespace(tags=[]))

    mod.UserActions.model_prompt_recipe_suggestions_gui_open()

    close_calls = [c for c in calls if isinstance(c, dict)]
    assert close_calls, "expected close_common_overlays call"
    assert mod.ctx.tags == ["user.model_suggestion_window_open"]
    assert "show" in calls
