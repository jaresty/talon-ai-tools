import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpCanvas import (
        HelpCanvasState,
        HelpGUIState,
        UserActions,
        _ensure_canvas,
        register_draw_handler,
        unregister_draw_handler,
        _default_draw_quick_help,
        Rect,
        _group_directional_keys,
        _intent_presets,
        _intent_preset_commands,
        _intent_spoken_buckets,
        _normalize_intent,
    )
    from talon_user.lib.staticPromptConfig import static_prompt_settings_catalog

    class ModelHelpCanvasTests(unittest.TestCase):
        def setUp(self) -> None:
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            HelpCanvasState.showing = False

        def test_open_and_close_toggle_canvas_and_reset_state(self) -> None:
            # Initially hidden.
            self.assertFalse(HelpCanvasState.showing)

            # First call opens the canvas and resets state.
            UserActions.model_help_canvas_open()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

            # Second call closes and resets.
            UserActions.model_help_canvas_open()
            self.assertFalse(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_explicit_close_hides_canvas_and_resets_state(self) -> None:
            HelpGUIState.section = "scope"
            HelpGUIState.static_prompt = "fix"
            HelpCanvasState.showing = True

            UserActions.model_help_canvas_close()

            self.assertFalse(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_open_for_static_prompt_sets_focus_prompt(self) -> None:
            self.assertIsNone(HelpGUIState.static_prompt)

            UserActions.model_help_canvas_open_for_static_prompt("todo")

            self.assertTrue(HelpGUIState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertEqual(HelpGUIState.static_prompt, "todo")

        def test_directional_grid_uses_only_core_lenses(self) -> None:
            """Primary directional grid should surface only core lenses (no composites)."""
            groups = _group_directional_keys()
            all_tokens = {token for lst in groups.values() for token in lst}
            self.assertTrue(
                all(
                    token in {"fog", "fig", "dig", "rog", "bog", "ong", "jog"}
                    for token in all_tokens
                )
            )

        def test_open_for_last_recipe_resets_static_prompt(self) -> None:
            HelpGUIState.static_prompt = "fix"

            UserActions.model_help_canvas_open_for_last_recipe()

            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_axis_specific_openers_set_section(self) -> None:
            UserActions.model_help_canvas_open_completeness()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "completeness")
            self.assertIsNone(HelpGUIState.static_prompt)

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_scope()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "scope")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_method()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "method")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_form()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "form")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_channel()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "channel")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_directional()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "directional")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_examples()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "examples")

        def test_custom_draw_handler_invoked_on_open(self) -> None:
            calls: list[object] = []

            def _handler(c) -> None:
                calls.append(c)

            register_draw_handler(_handler)
            try:
                UserActions.model_help_canvas_open()
                self.assertGreaterEqual(len(calls), 1)
            finally:
                unregister_draw_handler(_handler)

        def test_key_handler_registered_on_canvas(self) -> None:
            canvas_obj = _ensure_canvas()
            # In the test stub, the canvas exposes a `_callbacks` dict; in real
            # Talon this attribute may not exist, so guard accordingly.
            callbacks = getattr(canvas_obj, "_callbacks", None)
            if callbacks is None:
                self.skipTest("Canvas stub does not expose _callbacks")
            self.assertIn("key", callbacks)

        def test_static_prompt_focus_uses_settings_catalog(self) -> None:
            """Quick-help static prompt focus should render settings catalog data."""
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = "todo"

            catalog = static_prompt_settings_catalog()
            entry = catalog.get("todo")
            self.assertIsNotNone(
                entry,
                "Expected 'todo' in static prompt settings catalog",
            )
            description = entry["description"]
            axes = entry["axes"]

            class StubCanvas:
                def __init__(self) -> None:
                    self.rect = Rect(0, 0, 800, 600)
                    self.drawn: list[str] = []

                def draw_text(self, text, x, y) -> None:  # type: ignore[override]
                    self.drawn.append(str(text))

            canvas = StubCanvas()
            _default_draw_quick_help(canvas)

            self.assertIn("Static prompt focus: todo", canvas.drawn)
            if description:
                self.assertIn(description, canvas.drawn)
            if axes:
                self.assertIn("Profile axes:", canvas.drawn)

        def test_quick_help_surfaces_form_channel_defaults_and_directional_requirement(
            self,
        ) -> None:
            """Quick help should remind users about form/channel singleton defaults and required directional lens."""

            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None

            class StubCanvas:
                def __init__(self) -> None:
                    self.rect = Rect(0, 0, 800, 600)
                    self.drawn: list[str] = []

                def draw_text(self, text, x, y) -> None:  # type: ignore[override]
                    self.drawn.append(str(text))

            canvas = StubCanvas()
            _default_draw_quick_help(canvas)

            hint = [
                line
                for line in canvas.drawn
                if "Form/channel are optional singletons" in line
                and "Always include one directional lens" in line
            ]
            self.assertTrue(
                hint,
                "Expected quick help directional reminder",
            )

        def test_intent_presets_use_persona_orchestrator(self) -> None:
            orchestrator_intent = SimpleNamespace(
                key="decide",
                label="Decide (orchestrator)",
                intent="decide",
            )
            orchestrator = SimpleNamespace(
                intent_presets={"decide": orchestrator_intent}
            )
            legacy_intent = SimpleNamespace(
                key="legacy", label="Legacy", intent="legacy"
            )
            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas._get_persona_orchestrator",
                        return_value=orchestrator,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas._get_persona_orchestrator",
                            return_value=orchestrator,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                legacy_maps = SimpleNamespace(intent_presets={"legacy": legacy_intent})
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas.persona_intent_maps",
                        return_value=legacy_maps,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas.persona_intent_maps",
                            return_value=legacy_maps,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                presets = _intent_presets()
            self.assertEqual(presets, (orchestrator_intent,))

        def test_intent_spoken_buckets_use_persona_orchestrator(self) -> None:
            orchestrator_intent = SimpleNamespace(
                key="decide",
                label="Decide (orchestrator)",
                intent="decide",
            )
            orchestrator = SimpleNamespace(
                intent_presets={"decide": orchestrator_intent},
                intent_display_map={"decide": "Decide display"},
            )
            bucket_snapshot = SimpleNamespace(
                intent_buckets={"task": ["decide"]},
                intent_display_map={"decide": "Snapshot display"},
            )
            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas._get_persona_orchestrator",
                        return_value=orchestrator,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas._get_persona_orchestrator",
                            return_value=orchestrator,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas.personaCatalog.get_persona_intent_catalog",
                        return_value=bucket_snapshot,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas.personaCatalog.get_persona_intent_catalog",
                            return_value=bucket_snapshot,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas.persona_intent_maps",
                        side_effect=RuntimeError("legacy maps unavailable"),
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas.persona_intent_maps",
                            side_effect=RuntimeError("legacy maps unavailable"),
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                buckets = _intent_spoken_buckets()
            self.assertEqual(buckets, {"task": ["Decide (orchestrator)"]})

        def test_normalize_intent_uses_persona_orchestrator(self) -> None:
            orchestrator = SimpleNamespace(
                canonical_intent_key=lambda alias: "decide"
                if (alias or "").strip()
                else "",
            )
            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas._get_persona_orchestrator",
                        return_value=orchestrator,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas._get_persona_orchestrator",
                            return_value=orchestrator,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas.personaConfig.normalize_intent_token",
                        side_effect=RuntimeError(
                            "legacy normalize should not be called"
                        ),
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas.personaConfig.normalize_intent_token",
                            side_effect=RuntimeError(
                                "legacy normalize should not be called"
                            ),
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                result = _normalize_intent("Decide display")
            self.assertEqual(result, "decide")

        def test_intent_preset_commands_use_orchestrator_display_map(self) -> None:
            orchestrator_intent = SimpleNamespace(
                key="decide",
                label="Legacy label",
                intent="decide",
            )
            orchestrator = SimpleNamespace(
                intent_presets={"decide": orchestrator_intent},
                intent_display_map={"decide": "Decide Display"},
                canonical_intent_key=lambda alias: "decide" if alias else "",
            )
            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas._get_persona_orchestrator",
                        return_value=orchestrator,
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas._get_persona_orchestrator",
                            return_value=orchestrator,
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                stack.enter_context(
                    patch(
                        "talon_user.lib.modelHelpCanvas.persona_intent_maps",
                        side_effect=RuntimeError("legacy maps unavailable"),
                    )
                )
                try:
                    stack.enter_context(
                        patch(
                            "lib.modelHelpCanvas.persona_intent_maps",
                            side_effect=RuntimeError("legacy maps unavailable"),
                        )
                    )
                except (ModuleNotFoundError, AttributeError):
                    pass
                commands = _intent_preset_commands()
            self.assertIn("decide display", commands)

        def test_quick_help_intent_commands_use_catalog_spoken_aliases(self) -> None:
            from types import SimpleNamespace

            from talon_user.lib.personaConfig import IntentPreset
            from talon_user.lib import modelHelpCanvas as help_module

            preset = IntentPreset(key="decide", label="Decide", intent="decide")
            maps = SimpleNamespace(
                intent_presets={"decide": preset},
                intent_display_map={"decide": "Decide"},
            )

            with patch(
                "talon_user.lib.modelHelpCanvas.persona_intent_maps",
                return_value=maps,
            ):
                commands = help_module._intent_preset_commands()

            self.assertIn("decide", commands)
            self.assertNotIn("for deciding", commands)

            maps_no_display = SimpleNamespace(
                intent_presets={"decide": preset},
                intent_display_map={},
            )

            with patch(
                "talon_user.lib.modelHelpCanvas.persona_intent_maps",
                return_value=maps_no_display,
            ):
                commands = help_module._intent_preset_commands()

            self.assertIn("decide", commands)


else:
    if not TYPE_CHECKING:

        class ModelHelpCanvasTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
