import types


def test_request_history_toggle_calls_common_closers(monkeypatch):
    import talon_user.lib.requestHistoryDrawer as mod

    calls = []

    def fake_close_common(actions_obj, exclude=None, extra=None):
        calls.append(
            {"actions": actions_obj, "exclude": set(exclude or ()), "extra": tuple(extra or ())}
        )

    # Stub close helper and inflight guard.
    monkeypatch.setattr(mod, "close_common_overlays", fake_close_common)
    monkeypatch.setattr(mod, "_request_is_in_flight", lambda: False)

    # Stub history refresh and entries to avoid talon dependencies.
    def fake_refresh_entries():
        mod.HistoryDrawerState.entries = [("id", "text")]
        mod.HistoryDrawerState.selected_index = 0

    monkeypatch.setattr(mod, "_refresh_entries", fake_refresh_entries)

    # Dummy actions/user and canvas.
    class DummyCanvas:
        def show(self):
            calls.append("show")

        def hide(self):
            calls.append("hide")

    monkeypatch.setattr(mod, "actions", types.SimpleNamespace(user=types.SimpleNamespace()))
    monkeypatch.setattr(mod, "_history_canvas", DummyCanvas())
    monkeypatch.setattr(mod, "_ensure_canvas", lambda: mod._history_canvas)

    # Open via action to ensure lifecycle helper runs.
    mod.UserActions.request_history_drawer_open()
    close_calls = [c for c in calls if isinstance(c, dict)]
    assert close_calls, "expected close_common_overlays call"
    assert mod.HistoryDrawerState.showing is True
    assert "show" in calls
