"""
Tests that the Python path aligns with Go's ADDENDUM (CLARIFICATION) section.

Phase 3 of ADR 0082: the `format_source_messages()` function should render
the prompt parameter under the heading `=== ADDENDUM (CLARIFICATION) ===`
(matching Go's sectionAddendum constant), and PROMPT_REFERENCE_KEY should
document that section so LLMs know how to interpret it.
"""

import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelSource import ModelSource, format_source_messages
    from talon_user.lib.metaPromptConfig import PROMPT_REFERENCE_KEY

    class _SimpleSource(ModelSource):
        """Minimal source that returns a fixed text item."""

        def get_text(self) -> str:
            return "subject content"

    class AddendumAlignmentTests(unittest.TestCase):
        def test_format_source_messages_uses_addendum_heading(self) -> None:
            """format_source_messages should render ADDENDUM heading, not '# Prompt'."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            self.assertIn(
                "=== ADDENDUM (CLARIFICATION) ===",
                all_text,
                "format_source_messages must use ADDENDUM heading to match Go CLI",
            )
            self.assertNotIn(
                "# Prompt",
                all_text,
                "format_source_messages must not use legacy '# Prompt' heading",
            )

        def test_execution_reminder_precedes_addendum(self) -> None:
            """ADDENDUM (CLARIFICATION) must appear before REQUEST (CONTEXT) in format_source_messages output,
            so the task clarification intercepts the model's response plan before context anchors it."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            addendum_idx = all_text.find("=== ADDENDUM (CLARIFICATION) ===")
            request_idx = all_text.find("=== REQUEST (CONTEXT) ===")
            self.assertGreater(
                addendum_idx, -1, "ADDENDUM (CLARIFICATION) section must be present"
            )
            self.assertGreater(request_idx, -1, "REQUEST (CONTEXT) section must be present")
            self.assertLess(
                addendum_idx,
                request_idx,
                "ADDENDUM (CLARIFICATION) must appear before REQUEST (CONTEXT)",
            )

        def test_format_source_messages_uses_request_heading(self) -> None:
            """format_source_messages should render REQUEST heading, not SUBJECT."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            self.assertIn(
                "=== REQUEST",
                all_text,
                "format_source_messages must use REQUEST heading (renamed from SUBJECT)",
            )
            self.assertNotIn(
                "=== SUBJECT",
                all_text,
                "format_source_messages must not use SUBJECT heading after rename to REQUEST",
            )

        def test_format_source_messages_uses_format_heading(self) -> None:
            """format_source_messages should render FORMAT heading, not PLANNING DIRECTIVE."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            self.assertIn(
                "=== FORMAT",
                all_text,
                "format_source_messages must use FORMAT heading (renamed from PLANNING DIRECTIVE)",
            )
            self.assertNotIn(
                "=== PLANNING DIRECTIVE",
                all_text,
                "format_source_messages must not use PLANNING DIRECTIVE heading after rename to FORMAT",
            )

        def test_format_follows_request(self) -> None:
            """FORMAT must appear after REQUEST in format_source_messages output."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            request_idx = all_text.find("=== REQUEST")
            format_idx = all_text.find("=== FORMAT")
            self.assertGreater(request_idx, -1, "REQUEST section must be present")
            self.assertGreater(
                format_idx,
                -1,
                "FORMAT section must be present, got:\n%s" % all_text,
            )
            self.assertGreater(
                format_idx,
                request_idx,
                "FORMAT must appear after REQUEST for injection resistance",
            )

        def test_prompt_reference_key_process_method_no_substitution(self) -> None:
            """prompt_reference_key_as_text() must state process method steps cannot be replaced."""
            from talon_user.lib.metaPromptConfig import prompt_reference_key_as_text

            text = prompt_reference_key_as_text()
            self.assertIn(
                "steps of a process method may not be replaced",
                text,
                "prompt_reference_key_as_text() must close the substitution loophole for process methods",
            )

        def test_prompt_reference_key_process_method_imperative_check(self) -> None:
            """prompt_reference_key_as_text() must include imperative check for process methods."""
            from talon_user.lib.metaPromptConfig import prompt_reference_key_as_text

            text = prompt_reference_key_as_text()
            self.assertIn(
                "Produce that output now before reading files, searching code, or planning",
                text,
                "prompt_reference_key_as_text() Method bullet must include imperative check for process methods",
            )

        def test_prompt_reference_key_documents_addendum_section(self) -> None:
            """PROMPT_REFERENCE_KEY must describe the ADDENDUM section."""
            self.assertIn(
                "addendum",
                PROMPT_REFERENCE_KEY,
                "PROMPT_REFERENCE_KEY must document the ADDENDUM section",
            )
            self.assertIn(
                "clarification",
                PROMPT_REFERENCE_KEY["addendum"].lower(),
                "PROMPT_REFERENCE_KEY ADDENDUM entry should mention 'clarification'",
            )

        def test_meta_interpretation_guidance_suggestion_gate_requires_definition(
            self,
        ) -> None:
            """META_INTERPRETATION_GUIDANCE must require reading a token definition, not name-recognition."""
            from talon_user.lib.metaPromptConfig import META_INTERPRETATION_GUIDANCE

            self.assertIn(
                "definition",
                META_INTERPRETATION_GUIDANCE.lower(),
                "META_INTERPRETATION_GUIDANCE Suggestion gate must require reading the token's definition",
            )

        def test_meta_interpretation_guidance_suggestion_gate_requires_heuristics(
            self,
        ) -> None:
            """META_INTERPRETATION_GUIDANCE must prefer heuristics over name-recognition."""
            from talon_user.lib.metaPromptConfig import META_INTERPRETATION_GUIDANCE

            self.assertIn(
                "heuristic",
                META_INTERPRETATION_GUIDANCE.lower(),
                "META_INTERPRETATION_GUIDANCE Suggestion gate must reference heuristics",
            )

        def test_meta_interpretation_guidance_suggestion_gate_requires_distinctions(
            self,
        ) -> None:
            """META_INTERPRETATION_GUIDANCE must require checking distinctions."""
            from talon_user.lib.metaPromptConfig import META_INTERPRETATION_GUIDANCE

            self.assertIn(
                "distinction",
                META_INTERPRETATION_GUIDANCE.lower(),
                "META_INTERPRETATION_GUIDANCE Suggestion gate must reference distinctions",
            )

else:
    if not TYPE_CHECKING:

        class AddendumAlignmentTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass


if __name__ == "__main__":
    unittest.main()
