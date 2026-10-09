import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class ToStakeholdersDefinitionTests(unittest.TestCase):
        """The audience token 'to stakeholders' is defined by the makeup of the
        group (different roles), not by impact/risk vocabulary owned by its siblings."""

        def _prompt_text(self) -> str:
            from talon_user.lib.personaConfig import PERSONA_KEY_TO_VALUE

            return PERSONA_KEY_TO_VALUE["audience"]["to stakeholders"]

        def _routing_definition(self) -> str:
            from talon_user.lib.personaConfig import PERSONA_TOKEN_METADATA

            return PERSONA_TOKEN_METADATA["audience"]["to stakeholders"]["definition"]

        def test_prompt_text_names_the_mixed_group(self) -> None:
            self.assertIn("members hold different roles", self._prompt_text())

        def test_prompt_text_denies_shared_role_vocabulary(self) -> None:
            self.assertIn(
                "does not assume any one role's vocabulary or concerns are shared by every reader",
                self._prompt_text(),
            )

        def test_prompt_text_makes_each_reader_able_to_locate_their_part(self) -> None:
            self.assertIn("locate what bears on them", self._prompt_text())

        def test_prompt_text_names_the_decision_asked(self) -> None:
            self.assertIn("any decision being asked of them", self._prompt_text())

        def test_prompt_text_does_not_borrow_sibling_vocabulary(self) -> None:
            text = self._prompt_text().lower()
            self.assertNotIn("impact", text)
            self.assertNotIn("risk", text)

        def test_routing_definition_carries_the_same_trait(self) -> None:
            self.assertIn("different roles", self._routing_definition())
