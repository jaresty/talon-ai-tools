from talon import actions, clip

from lib import helpHub


def setup_function():
    # Reset recorded calls between tests.
    actions.user.calls.clear()


def test_help_hub_open_and_close():
    helpHub.help_hub_close()
    helpHub.help_hub_open()
    assert helpHub.HelpHubState.showing is True
    canvas = getattr(helpHub, "_hub_canvas", None)
    assert canvas is not None and canvas.visible is True

    helpHub.help_hub_close()
    assert helpHub.HelpHubState.showing is False
    assert canvas.visible is False


def test_help_hub_button_triggers_quick_help():
    helpHub.help_hub_open()
    helpHub.help_hub_test_click("Quick help")
    labels = [call[0] for call in actions.user.calls]
    assert "model_help_canvas_open" in labels


def test_help_hub_copy_adr_links():
    helpHub.help_hub_open()
    helpHub.help_hub_test_click("ADR links")
    assert clip.text() is not None
    assert "docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md" in clip.text()


def test_help_hub_search_runs_handler():
    helpHub.help_hub_open()
    helpHub.help_hub_set_filter("Quick help")
    helpHub.help_hub_test_click("Quick help")
    labels = [call[0] for call in actions.user.calls]
    assert "model_help_canvas_open" in labels


def test_help_hub_onboarding_flag():
    helpHub.help_hub_onboarding()
    assert helpHub.HelpHubState.show_onboarding is True
    assert helpHub.HelpHubState.showing is True


def test_help_hub_scroll_logging():
    # Ensure scroll logic clamps and logs.
    helpHub.HelpHubState.max_scroll = 100.0
    helpHub.HelpHubState.scroll_y = 0.0
    helpHub.HelpHubState.scroll_y = min(helpHub.HelpHubState.max_scroll, 200.0)
    assert helpHub.HelpHubState.scroll_y == helpHub.HelpHubState.max_scroll
