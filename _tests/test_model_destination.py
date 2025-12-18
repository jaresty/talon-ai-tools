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
    from talon import actions, clip
    from talon_user.lib.modelDestination import ModelDestination
    from talon_user.lib import modelDestination as model_destination_module
    from talon_user.lib.modelHelpers import build_request, format_message
    from talon_user.lib.modelPresentation import (
        ResponsePresentation,
        render_for_destination,
    )
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.lib.modelState import GPTState

    class ModelDestinationTests(unittest.TestCase):
        class FakeElement:
            def __init__(self, attrs):
                self._attrs = attrs

            def get(self, name):
                return self._attrs.get(name)

        def setUp(self):
            actions.user.calls.clear()
            clip.set_text(None)
            GPTState.reset_all()
            GPTState.debug_enabled = False

        @patch.object(model_destination_module.ui, "focused_element")
        def test_inside_textarea_accepts_text_entry_role(self, focused_element):
            focused_element.return_value = self.FakeElement({"AXRole": "AXTextEntry"})
            self.assertTrue(ModelDestination().inside_textarea())

        @patch.object(model_destination_module.ui, "focused_element")
        def test_inside_textarea_uses_accessibility_hints(self, focused_element):
            focused_element.return_value = self.FakeElement(
                {"AXRole": "AXGroup", "AXSubrole": "AXSearchField"}
            )
            self.assertTrue(ModelDestination().inside_textarea())

            focused_element.return_value = self.FakeElement(
                {"AXRole": "AXGroup", "AXRoleDescription": "Text Field"}
            )
            self.assertTrue(ModelDestination().inside_textarea())

            focused_element.return_value = self.FakeElement(
                {
                    "AXRole": "AXGroup",
                    "AXSupportsTextSelection": True,
                    "AXValue": "draft note",
                }
            )
            self.assertTrue(ModelDestination().inside_textarea())

            focused_element.return_value = self.FakeElement({"AXRole": "AXButton"})
            self.assertFalse(ModelDestination().inside_textarea())

        @patch.object(model_destination_module.ui, "focused_element")
        def test_inside_textarea_logs_when_debug_enabled(self, focused_element):
            GPTState.debug_enabled = True
            self.addCleanup(lambda: setattr(GPTState, "debug_enabled", False))

            focused_element.return_value = self.FakeElement({"AXRole": "AXTextField"})
            with patch("talon_user.lib.modelDestination.print") as mock_print:
                ModelDestination().inside_textarea()

            mock_print.assert_called()
            message = " ".join(str(arg) for arg in mock_print.call_args.args)
            self.assertIn("inside_textarea=True", message)
            self.assertIn("AXRole='AXTextField'", message)
            self.assertIn("reason=AXRole matches text role", message)

        def test_inside_textarea_fallbacks_with_language_context(self):
            with (
                patch.object(
                    model_destination_module.ui,
                    "focused_element",
                    side_effect=RuntimeError("No element found."),
                ),
                patch.object(
                    model_destination_module.actions.code,
                    "language",
                    return_value="python",
                ),
                patch("talon_user.lib.modelDestination.print") as mock_print,
            ):
                self.assertTrue(ModelDestination().inside_textarea())

            message = " ".join(str(arg) for arg in mock_print.call_args.args)
            self.assertIn("inside_textarea=True", message)
            self.assertIn("fallback via language context 'python'", message)

        def test_inside_textarea_returns_false_when_no_fallback(self):
            with (
                patch.object(
                    model_destination_module.ui,
                    "focused_element",
                    side_effect=RuntimeError("No element found."),
                ),
                patch.object(
                    model_destination_module.actions.code, "language", return_value=""
                ),
                patch.object(
                    model_destination_module.actions.app, "name", return_value="Preview"
                ),
                patch("talon_user.lib.modelDestination.print") as mock_print,
            ):
                self.assertFalse(ModelDestination().inside_textarea())

            message = " ".join(str(arg) for arg in mock_print.call_args.args)
            self.assertIn("inside_textarea=False", message)
            self.assertIn("focused element lookup failed", message)

        @patch("talon_user.lib.modelHelpers.print")
        def test_build_request_logs_textarea_check_when_debug(self, mock_helpers_print):
            GPTState.debug_enabled = True
            self.addCleanup(lambda: setattr(GPTState, "debug_enabled", False))

            build_request(model_destination_module.Above())

            messages = [
                " ".join(str(arg) for arg in call.args)
                for call in mock_helpers_print.call_args_list
            ]
            self.assertTrue(
                any("inside_textarea check" in message for message in messages),
                "Expected build_request to log textarea detection when debug is enabled",
            )

        @patch.object(model_destination_module, "Builder")
        def test_browser_includes_recipe_metadata_from_gpt_state(self, builder_cls):
            # Ensure clean state before configuring recipe fields.
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_static_prompt = "describe"

            result = PromptResult.from_messages([format_message("body line")])

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # The browser destination should prepend a Recipe line, a speakable
            # grammar line, and a tip that references the static prompt.
            paragraph_texts = [
                call.args[0] for call in builder_instance.p.call_args_list
            ]

            self.assertIn(
                "Recipe: describe · full · focus · plain · fog", paragraph_texts
            )
            self.assertIn(
                "Say: model run describe full focus plain fog", paragraph_texts
            )
            self.assertTrue(
                any("model show grammar" in text for text in paragraph_texts),
                "Expected a tip mentioning 'model show grammar'",
            )
            self.assertTrue(
                any("model pattern menu describe" in text for text in paragraph_texts),
                "Expected a tip mentioning 'model pattern menu describe'",
            )

            builder_instance.h2.assert_called_with("Response")

        @patch.object(model_destination_module, "Builder")
        def test_browser_uses_last_axes_when_recipe_empty(self, builder_cls):
            GPTState.reset_all()
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["rigor"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            }
            GPTState.last_static_prompt = "infer"
            GPTState.last_recipe = ""

            result = PromptResult.from_messages([format_message("body line")])
            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            paragraph_texts = [
                call.args[0] for call in builder_instance.p.call_args_list
            ]
            # Recipe should be constructed from last_axes tokens including directional.
            self.assertIn(
                "Recipe: infer · full · bound · rigor · plain · slack · fog",
                paragraph_texts,
            )
            self.assertIn(
                "Say: model run infer full bound rigor plain slack fog", paragraph_texts
            )

        @patch.object(model_destination_module, "Builder")
        def test_browser_includes_meta_section_when_available(self, builder_cls):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_static_prompt = "describe"

            # Simulate a presentation with meta text already split out.
            result = PromptResult.from_messages(
                [format_message("body line\n\n## Model interpretation\nMeta details")]
            )

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # Collect all paragraph calls after Browser.insert.
            paragraph_texts = [
                call.args[0] for call in builder_instance.p.call_args_list
            ]

            # We expect a dedicated Model interpretation section header and the
            # meta content rendered separately from the main body.
            self.assertIn(
                "Model interpretation",
                [call.args[0] for call in builder_instance.h2.call_args_list],
            )
            self.assertTrue(
                any("Meta details" in text for text in paragraph_texts),
                "Expected browser view to include meta interpretation text",
            )
            # The bare heading marker should not appear as its own paragraph.
            self.assertNotIn(
                "Model interpretation",
                paragraph_texts,
                "Model interpretation heading should not be rendered as a body paragraph",
            )

        @patch.object(model_destination_module, "Browser")
        def test_insert_uses_response_presentation(self, browser_cls):
            with (
                patch.object(actions.user, "confirmation_gui_append") as gui_append,
                patch.object(actions.user, "paste") as paste_action,
            ):
                result = PromptResult.from_messages([format_message("answer")])

                ModelDestination().insert(result)

            browser_instance = browser_cls.return_value
            gui_append.assert_called_once()
            self.assertFalse(paste_action.called)
            self.assertFalse(browser_instance.insert.called)
            presentation = gui_append.call_args.args[0]
            self.assertIsInstance(presentation, ResponsePresentation)
            self.assertEqual(presentation.display_text, "answer")

        def test_insert_accepts_prompt_result_like_object(self):
            with patch.object(actions.user, "confirmation_gui_append"):
                inner = PromptResult.from_messages([format_message("legacy")])

                class ForeignPromptResult:
                    def __init__(self, wrapped):
                        self._wrapped = wrapped
                        self.messages = wrapped.messages
                        self.session = wrapped.session

                    def presentation_for(self, destination_kind):  # noqa: ARG002
                        return self._wrapped.presentation_for(destination_kind)

                    def append_thread(self):
                        return self._wrapped.append_thread()

                    @property
                    def text(self):
                        return self._wrapped.text

                ModelDestination().insert(ForeignPromptResult(inner))

        @patch.object(model_destination_module, "Builder")
        def test_browser_renders_bulleted_response_as_list(self, builder_cls):
            # Ensure rich answer rendering recognises simple bullets.
            GPTState.reset_all()
            result = PromptResult.from_messages(
                [
                    format_message(
                        "Intro paragraph.\n\n- First item\n- Second item\n\nConclusion."
                    )
                ]
            )

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # The builder should have been asked to render at least one
            # unordered list for the bullet items.
            self.assertTrue(
                any(call[0] == () for call in builder_instance.ul.call_args_list)
                or builder_instance.ul.call_args_list,
                "Expected Browser to render bullets via Builder.ul",
            )

        def test_presentation_falls_back_to_meta_when_no_answer(self):
            # When only meta content is present, still surface it for paste/display.
            messages = [
                format_message("## Model interpretation\nMeta details only."),
            ]

            presentation = render_for_destination(messages, "paste")

            self.assertEqual(
                presentation.display_text.strip(), messages[0]["text"].strip()
            )
            self.assertEqual(
                presentation.paste_text.strip(), messages[0]["text"].strip()
            )
            # meta_text should remain populated so other surfaces can render it separately.
            self.assertEqual(
                presentation.meta_text.strip(), messages[0]["text"].strip()
            )

        def test_file_destination_writes_markdown_with_response(self):
            from talon import settings as talon_settings  # type: ignore
            import os
            import tempfile

            tmpdir = tempfile.mkdtemp()
            talon_settings.set("user.model_source_save_directory", tmpdir)

            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_static_prompt = "describe"

            result = PromptResult.from_messages([format_message("answer body")])

            before = set(os.listdir(tmpdir))
            dest = model_destination_module.File()
            dest.insert(result)
            after = set(os.listdir(tmpdir))
            new_files = list(after - before)
            self.assertEqual(len(new_files), 1, new_files)
            path = os.path.join(tmpdir, new_files[0])
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("# Response", content)
            self.assertIn("answer body", content)

        def test_file_destination_header_and_slug_use_last_axes_tokens(self):
            from talon import settings as talon_settings  # type: ignore
            import os
            import tempfile

            tmpdir = tempfile.mkdtemp()
            talon_settings.set("user.model_source_save_directory", tmpdir)

            GPTState.reset_all()
            # Seed legacy last_* fields with values that should be overridden
            # by the structured last_axes tokens.
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "gist"
            GPTState.last_scope = "legacy-scope"
            GPTState.last_method = "legacy-method"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor"],
                "form": ["plain"],
                "channel": ["slack"],
            }
            GPTState.last_directional = "fog"

            result = PromptResult.from_messages([format_message("answer body")])

            before = set(os.listdir(tmpdir))
            dest = model_destination_module.File()
            dest.insert(result)
            after = set(os.listdir(tmpdir))
            new_files = list(after - before)
            self.assertEqual(len(new_files), 1, new_files)
            filename = new_files[0]

            # Filename slug should reflect the axis tokens from last_axes
            # rather than the legacy last_* strings.
            self.assertIn("infer-full-bound-edges-rigor-plain-slack-fog", filename)

            path = os.path.join(tmpdir, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Header should include axis tokens derived from last_axes.
            self.assertIn("completeness_tokens: full", content)
            self.assertIn("scope_tokens: bound edges", content)
            self.assertIn("method_tokens: rigor", content)
            self.assertIn("form_tokens: plain", content)
            self.assertIn("channel_tokens: slack", content)
            self.assertIn("directional: fog", content)


else:
    if not TYPE_CHECKING:

        class ModelDestinationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
