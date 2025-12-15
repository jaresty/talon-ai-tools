import types


def test_help_hub_open_calls_common_closers(monkeypatch):
    import talon_user.lib.helpHub as mod

    calls = []

    def fake_close_common(actions_obj, exclude=None, extra=None):
        calls.append({"actions": actions_obj, "exclude": set(exclude or ()), "extra": tuple(extra or ())})

    monkeypatch.setattr(mod, "close_common_overlays", fake_close_common)
    monkeypatch.setattr(mod, "_request_is_in_flight", lambda: False)

    class DummyActions:
        user = types.SimpleNamespace()

    monkeypatch.setattr(mod, "actions", DummyActions())
    monkeypatch.setattr(mod, "_ensure_canvas", lambda: None)
    monkeypatch.setattr(mod, "HelpHubState", types.SimpleNamespace(showing=False, scroll_y=0.0))
    monkeypatch.setattr(mod, "_build_buttons", lambda: [])
    monkeypatch.setattr(mod, "_build_search_index", lambda: None)
    monkeypatch.setattr(mod, "_recompute_search_results", lambda: None)
    monkeypatch.setattr(mod, "_copy_cheat_sheet", lambda: None)
    monkeypatch.setattr(mod, "_log", lambda *_: None)
    monkeypatch.setattr(mod, "_hub_key_handler", object())
    monkeypatch.setattr(mod, "_global_key_handler_registered", False)
    monkeypatch.setattr(mod, "_tap_key_handler_registered", False)
    monkeypatch.setattr(mod, "tap", types.SimpleNamespace(register=lambda *args, **kwargs: None, KEY=1, HOOK=2))
    monkeypatch.setattr(mod, "_hub_canvas", types.SimpleNamespace(move=lambda *a, **k: None, register=lambda *a, **k: None))

    mod.help_hub_open()

    close_calls = [c for c in calls if isinstance(c, dict)]
    assert close_calls, "expected close_common_overlays call"
    # Ensure help hub is marked showing.
    assert mod.HelpHubState.showing is True
