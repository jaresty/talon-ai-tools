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
            """EXECUTION REMINDER must appear before ADDENDUM in format_source_messages output,
            so it gates completion-intent before the task prompt anchors the model's response plan."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            reminder_idx = all_text.find("=== EXECUTION REMINDER ===")
            addendum_idx = all_text.find("=== ADDENDUM (CLARIFICATION) ===")
            self.assertGreater(
                reminder_idx, -1, "EXECUTION REMINDER section must be present"
            )
            self.assertGreater(addendum_idx, -1, "ADDENDUM section must be present")
            self.assertLess(
                reminder_idx,
                addendum_idx,
                "EXECUTION REMINDER must appear before ADDENDUM so it intercepts completion-intent",
            )

        def test_planning_directive_follows_subject(self) -> None:
            """A PLANNING DIRECTIVE must appear after SUBJECT in format_source_messages
            output, providing recency-based resistance to SUBJECT injection attacks while
            requiring explicit planning output from the LLM."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "") for item in messages if isinstance(item, dict)
            )
            subject_idx = all_text.find("=== SUBJECT (CONTEXT) ===")
            planning_directive_idx = all_text.find("=== PLANNING DIRECTIVE ===")
            self.assertGreater(subject_idx, -1, "SUBJECT section must be present")
            self.assertGreater(
                planning_directive_idx,
                -1,
                "PLANNING DIRECTIVE section must be present, got:\n%s" % all_text,
            )
            self.assertGreater(
                planning_directive_idx,
                subject_idx,
                "PLANNING DIRECTIVE must appear after SUBJECT for injection resistance",
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
