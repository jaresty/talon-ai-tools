import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib import axisMappings, personaConfig

    class AxisFamilyTokenGuardrailTests(unittest.TestCase):
        def test_persona_docs_do_not_contain_contract_shaped_words(self) -> None:
            # Words that strongly suggest containers or output formats rather than
            # social framing or interaction-level intent. If these show up in
            # persona/intent docs, they probably belong on style/method instead.
            banned = {
                "table",
                "diagram",
                "jira",
                "slack",
                "checklist",
                "gherkin",
                "code",
                "shellscript",
                "html",
                "cards",
            }

            for axis, mapping in personaConfig.PERSONA_KEY_TO_VALUE.items():
                with self.subTest(axis=axis):
                    for key, description in mapping.items():
                        lower = description.lower()
                        for word in banned:
                            self.assertNotIn(
                                word,
                                lower,
                                msg=(
                                    f"Persona/intent axis {axis!r} token {key!r} description "
                                    f"contains contract-shaped word {word!r}: {description!r}"
                                ),
                            )

        def test_contract_docs_do_not_contain_persona_shaped_words(self) -> None:
            # Words that suggest audience roles or experience levels rather than
            # coverage, territory, reasoning, or containers.
            banned = {
                "executive",
                "ceo",
                "junior",
                "novice",
                "manager",
            }

            for axis in ("completeness", "scope", "method", "form", "channel"):
                mapping = axisMappings.axis_docs_map(axis)
                with self.subTest(axis=axis):
                    for key, description in mapping.items():
                        lower = description.lower()
                        for word in banned:
                            self.assertNotIn(
                                word,
                                lower,
                                msg=(
                                    f"Contract axis {axis!r} token {key!r} description contains "
                                    f"persona-shaped word {word!r}: {description!r}"
                                ),
                            )


else:
    if not TYPE_CHECKING:

        class AxisFamilyTokenGuardrailTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
