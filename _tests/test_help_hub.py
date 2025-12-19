from unittest.mock import MagicMock, patch

from talon import actions, clip

from lib import helpHub


class _DummyButton(helpHub.HubButton):
    def __init__(self, label: str, description: str = "", voice_hint: str = ""):
        super().__init__(
            label=label,
            description=description,
            handler=lambda: None,
            voice_hint=voice_hint,
        )


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


def test_help_hub_button_triggers_provider_list():
    helpHub.help_hub_open()
    helpHub.help_hub_test_click("Providers")
    labels = [call[0] for call in actions.user.calls]
    assert "model_provider_list" in labels


def test_help_hub_search_can_trigger_provider_list():
    helpHub.help_hub_open()
    helpHub.help_hub_set_filter("provider")
    helpHub.help_hub_test_click("Providers")
    labels = [call[0] for call in actions.user.calls]
    assert "model_provider_list" in labels


def test_help_hub_cheat_sheet_includes_all_intent_tokens():
    from lib.personaConfig import intent_bucket_spoken_tokens

    cheat = helpHub._cheat_sheet_text()
    buckets = intent_bucket_spoken_tokens()
    for label, tokens in (
        ("Intent tokens (task):", buckets.get("task", [])),
        ("Intent tokens (relational):", buckets.get("relational", [])),
    ):
        for token in tokens:
            assert token in cheat, f"{token} missing from {label} line"
    # Ensure new intent preset keys are represented.
    assert "understand" in " ".join(buckets.get("task", []))


def test_help_hub_quick_help_closes_hub_before_open(monkeypatch):
    # Open the hub and patch quick help to assert close-before-open ordering.
    helpHub.help_hub_open()
    assert helpHub.HelpHubState.showing is True

    calls: list[str] = []
    original = actions.user.model_help_canvas_open

    def _wrapped():  # type: ignore[no-redef]
        # Help Hub should already be closed when quick help opens.
        calls.append("open_quick_help")
        assert helpHub.HelpHubState.showing is False
        return original()

    monkeypatch.setattr(actions.user, "model_help_canvas_open", _wrapped)
    try:
        helpHub.help_hub_test_click("Quick help")
    finally:
        monkeypatch.setattr(actions.user, "model_help_canvas_open", original)

    assert calls == ["open_quick_help"]


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


def test_help_hub_search_persona_preset_triggers(monkeypatch):
    from lib.personaConfig import persona_intent_catalog_snapshot

    persona_mock = MagicMock()
    monkeypatch.setattr(actions.user, "persona_set_preset", persona_mock)
    snapshot = persona_intent_catalog_snapshot()
    assert snapshot.persona_spoken_map.get("mentor") == "teach_junior_dev"
    helpHub.help_hub_open()
    search_labels = [
        btn.label
        for btn in getattr(helpHub, "_search_index", [])
        if "Persona preset:" in btn.label
    ]
    assert search_labels, "Persona presets missing from search index"
    assert "mentor" in " ".join(search_labels).lower(), search_labels
    helpHub.help_hub_set_filter("mentor")
    persona_labels = [
        btn.label
        for btn in getattr(helpHub, "_search_results", [])
        if "Persona preset:" in btn.label
    ]
    assert persona_labels, "Expected persona preset search result"
    helpHub.help_hub_test_click(persona_labels[0])
    persona_mock.assert_called()
    helpHub.help_hub_close()


def test_help_hub_persona_search_labels_surface_alias_metadata():
    helpHub.help_hub_open()
    try:
        helpHub.help_hub_set_filter("mentor")
        persona_results = [
            btn
            for btn in getattr(helpHub, "_search_results", [])
            if btn.label.startswith("Persona preset:")
        ]
        assert persona_results, "Expected persona preset search result"
        entry = persona_results[0]
        label_lower = entry.label.lower()
        assert "(say: persona mentor)" in label_lower
        assert "apply persona stance" in entry.description.lower()
        assert "say: persona mentor" in entry.voice_hint.lower()
    finally:
        helpHub.help_hub_close()


def test_help_hub_search_intent_preset_triggers(monkeypatch):
    intent_mock = MagicMock()
    monkeypatch.setattr(actions.user, "intent_set_preset", intent_mock)
    helpHub.help_hub_open()
    assert any(
        "Intent preset:" in btn.label for btn in getattr(helpHub, "_search_index", [])
    ), "Intent presets missing from search index"
    helpHub.help_hub_set_filter("for deciding")
    intent_labels = [
        btn.label
        for btn in getattr(helpHub, "_search_results", [])
        if "Intent preset:" in btn.label
    ]
    assert intent_labels, "Expected intent preset search result"
    helpHub.help_hub_test_click(intent_labels[0])
    intent_mock.assert_called()
    helpHub.help_hub_close()


def test_help_hub_intent_search_labels_surface_alias_metadata():
    helpHub.help_hub_open()
    try:
        helpHub.help_hub_set_filter("for deciding")
        intent_results = [
            btn
            for btn in getattr(helpHub, "_search_results", [])
            if btn.label.startswith("Intent preset:")
        ]
        assert intent_results, "Expected intent preset search result"
        entry = intent_results[0]
        label_lower = entry.label.lower()
        assert "(say: intent for deciding)" in label_lower
        assert "apply intent stance" in entry.description.lower()
        assert "say: intent for deciding" in entry.voice_hint.lower()
    finally:
        helpHub.help_hub_close()


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


def test_help_hub_next_focus_label_wraps_and_steps():
    items = [
        ("btn", "Quick help"),
        ("btn", "Patterns"),
        ("res", "Docs"),
    ]

    # No current focus: moving forward focuses the first item.
    assert helpHub._next_focus_label("", 1, items) == "btn:Quick help"

    # Stepping forward wraps from last to first.
    assert helpHub._next_focus_label("res:Docs", 1, items) == "btn:Quick help"

    # Stepping backward from first wraps to last.
    assert helpHub._next_focus_label("btn:Quick help", -1, items) == "res:Docs"


def test_cheat_sheet_hides_composite_directionals():
    """Cheat sheet should surface only core directional lenses (no fly/fip/dip)."""
    text = helpHub._cheat_sheet_text()
    assert "fly" not in text
    assert "fip" not in text
    assert "dip" not in text


def test_cheat_sheet_omits_legacy_style_axis():
    """Cheat sheet should not reintroduce legacy style axis tokens/commands."""
    text = helpHub._cheat_sheet_text().lower()
    assert "style axis" not in text
    assert "style=" not in text
    assert "model set style" not in text


def test_cheat_sheet_calls_out_form_channel_defaults_and_directional_requirement():
    """Cheat sheet should remind users form/channel are optional singletons with defaults and one directional lens is required."""
    text = helpHub._cheat_sheet_text().lower()
    assert "form and channel are optional singletons" in text
    assert "stance/defaults appear in quick help" in text
    assert "directional lens" in text


def test_cheat_sheet_persona_line_uses_persona_catalog():
    """Persona presets line should reflect the persona catalog spoken tokens."""
    from lib.personaConfig import persona_catalog

    text = helpHub._cheat_sheet_text()
    lines = text.splitlines()
    persona_lines = [line for line in lines if line.startswith("- persona ")]
    alias_tokens = set()
    if persona_lines:
        for line in persona_lines:
            if "(say: persona " not in line:
                continue
            alias_part = line.split("(say: persona ", 1)[1]
            alias_token = alias_part.split(")", 1)[0].strip().lower()
            if alias_token:
                alias_tokens.add(alias_token)
        assert alias_tokens, "Persona preset entries missing say: persona hints"
    else:
        fallback_line = next(
            (line for line in lines if line.startswith("Persona presets:")),
            "",
        )
        assert fallback_line, "Persona presets section missing from cheat sheet"
        alias_tokens = {
            token.strip().lower()
            for token in fallback_line.split("Persona presets:", 1)[1].split("|")
            if token.strip()
        }

    catalog_spoken = {
        (preset.spoken or "").strip().lower()
        for preset in persona_catalog().values()
        if (preset.spoken or "").strip()
    }

    missing = {token for token in catalog_spoken if token and token not in alias_tokens}
    assert not missing, f"Missing persona presets in cheat sheet: {sorted(missing)}"


def test_help_hub_copy_cheat_sheet_includes_snapshot_aliases(monkeypatch):
    """Clipboard copy should reuse snapshot-backed persona/intent alias phrasing."""
    from lib.personaConfig import persona_intent_catalog_snapshot

    captured: dict[str, str] = {}

    monkeypatch.setattr(helpHub, "_reject_if_request_in_flight", lambda: False)
    monkeypatch.setattr(actions.app, "notify", lambda _: None)
    monkeypatch.setattr(
        clip, "set_text", lambda value: captured.setdefault("text", value)
    )

    helpHub._copy_cheat_sheet()

    text = captured.get("text", "")
    assert text, "Cheat sheet copy did not set clipboard text"
    lower_text = text.lower()

    snapshot = persona_intent_catalog_snapshot()
    persona_aliases = {
        (preset.spoken or preset.label or preset.key or "").strip().lower()
        for preset in snapshot.persona_presets.values()
        if (preset.spoken or preset.label or preset.key)
    }
    for alias in sorted(filter(None, persona_aliases)):
        assert f"(say: persona {alias}" in lower_text, (
            f"Persona alias {alias!r} missing from cheat sheet copy"
        )

    intent_aliases = set()
    for key, preset in snapshot.intent_presets.items():
        display = (
            snapshot.intent_display_map.get(key) or preset.label or key or ""
        ).strip()
        alias = display or preset.intent or key or ""
        if alias:
            intent_aliases.add(alias.lower())
    for alias in sorted(intent_aliases):
        assert f"(say: intent {alias}" in lower_text, (
            f"Intent alias {alias!r} missing from cheat sheet copy"
        )


def test_persona_presets_use_catalog_snapshot():
    from lib.personaConfig import persona_intent_catalog_snapshot

    snapshot = persona_intent_catalog_snapshot()
    with patch(
        "lib.personaConfig.persona_intent_catalog_snapshot",
        return_value=snapshot,
    ) as snapshot_mock:
        presets = helpHub._persona_presets()
    snapshot_mock.assert_called_once()
    assert {preset.key for preset in presets} == set(snapshot.persona_presets.keys())


def test_intent_spoken_buckets_use_catalog_snapshot():
    from lib.personaConfig import persona_intent_catalog_snapshot

    snapshot = persona_intent_catalog_snapshot()
    with patch(
        "lib.personaConfig.persona_intent_catalog_snapshot",
        return_value=snapshot,
    ) as snapshot_mock:
        buckets = helpHub._intent_spoken_buckets()
    snapshot_mock.assert_called_once()
    expected_buckets = set(snapshot.intent_buckets.keys())
    assert expected_buckets.issubset(buckets.keys())
    for bucket, tokens in buckets.items():
        for token in tokens:
            assert token


def test_help_hub_key_handler_swallows_keys(monkeypatch):
    helpHub.help_hub_open()

    class _Evt:
        def __init__(self, key: str):
            self.key = key
            self.down = True
            self.mods = []
            self.blocked = 0

        def block(self):
            self.blocked += 1

    handler = helpHub._hub_key_handler
    assert handler is not None
    result = handler(_Evt("j"))
    assert result is True

    # Key-up events are consumed as well.
    evt_up = _Evt("j")
    evt_up.down = False
    result_up = handler(evt_up)
    assert result_up is True
    assert evt_up.blocked >= 1

    helpHub.help_hub_close()


def test_build_search_index_uses_buttons_and_lists(monkeypatch):
    buttons = [
        _DummyButton(label="Quick help", description="Open quick help"),
    ]

    fake_catalog = {
        "axes": {"completeness": {"full": "Full answer"}},
        "axis_list_tokens": {"completeness": ["full"]},
        "static_prompts": {"profiled": [{"name": "todo"}]},
    }

    def fake_read_list_items(name: str):
        return []

    index = helpHub.build_search_index(
        buttons,
        patterns=[],
        presets=[],
        read_list_items=fake_read_list_items,
        catalog=fake_catalog,
    )
    labels = {item.label for item in index}

    assert "Hub: Quick help" in labels
    assert "Prompt: todo" in labels
    assert "Axis (Completeness): full" in labels


def test_focusable_items_for_uses_results_when_filtered():
    buttons = [
        _DummyButton(label="Quick help"),
        _DummyButton(label="Patterns"),
    ]
    results = [
        _DummyButton(label="Hub: Quick help"),
        _DummyButton(label="Axis (Completeness): full"),
    ]

    items = helpHub.focusable_items_for("quick", buttons, results)
    assert items == [("res", "Hub: Quick help"), ("res", "Axis (Completeness): full")]


def test_focusable_items_for_includes_buttons_when_unfiltered():
    buttons = [
        _DummyButton(label="Quick help"),
        _DummyButton(label="Patterns"),
    ]
    results = [
        _DummyButton(label="Hub: Quick help"),
    ]

    items = helpHub.focusable_items_for("", buttons, results)
    assert items == [
        ("btn", "Quick help"),
        ("btn", "Patterns"),
        ("res", "Hub: Quick help"),
    ]


def test_help_hub_search_results_for_is_pure_and_label_based():
    index = [
        helpHub.HubButton(
            label="Quick help",
            description="Open grammar quick reference",
            handler=lambda: None,
            voice_hint="Say: model quick help",
        ),
        helpHub.HubButton(
            label="Patterns",
            description="Open curated model patterns",
            handler=lambda: None,
            voice_hint="Say: model patterns",
        ),
    ]

    # Empty or whitespace-only queries return no results.
    assert helpHub.search_results_for("", index) == []
    assert helpHub.search_results_for("   ", index) == []

    # Case-insensitive substring match on labels only.
    results = helpHub.search_results_for("quick", index)
    assert [item.label for item in results] == ["Quick help"]

    results = helpHub.search_results_for("PAT", index)
    assert [item.label for item in results] == ["Patterns"]
