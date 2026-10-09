import re
import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    TOKEN = "as end user"
    # Same-axis neighbours the voice must be told apart from, in both directions.
    VOICE_NEIGHBOURS = ["as junior engineer", "as PM", "as designer", "as plainspeak"]
    # Software-shaped words that would narrow the voice to one kind of subject.
    DOMAIN_WORDS = [
        "software", "code", "app", "api", "feature", "interface", "developer",
        "engineer", "product", "customer", "sponsor", "stakeholder",
    ]

    class AsEndUserDefinitionTests(unittest.TestCase):
        def _persona(self):
            from talon_user.lib import personaConfig as P

            return P

        def _meta(self) -> dict:
            return self._persona().PERSONA_TOKEN_METADATA["voice"].get(TOKEN, {})

        def _description(self) -> str:
            return self._persona().PERSONA_KEY_TO_VALUE["voice"].get(TOKEN, "")

        def test_token_is_defined_at_every_persona_site(self) -> None:
            P = self._persona()
            for name in (
                "PERSONA_KEY_TO_VALUE",
                "PERSONA_KEY_TO_LABEL",
                "PERSONA_KEY_TO_ROUTING_CONCEPT",
                "PERSONA_KEY_TO_KANJI",
                "PERSONA_TOKEN_METADATA",
            ):
                with self.subTest(site=name):
                    self.assertIn(TOKEN, getattr(P, name)["voice"])

        def test_description_names_the_recipient_stance(self) -> None:
            text = self._description()
            self.assertTrue(text.startswith("The response speaks in the first person as"))
            self.assertIn("receives the outcome without having made it", text)
            self.assertIn("what they are trying to get done", text)
            self.assertIn("the terms they would use", text)

        def test_description_is_domain_agnostic(self) -> None:
            text = self._description().lower()
            for word in DOMAIN_WORDS:
                with self.subTest(word=word):
                    self.assertIsNone(re.search(rf"\b{re.escape(word)}\b", text))

        def test_description_names_no_other_persona_token(self) -> None:
            P = self._persona()
            text = self._description().lower()
            others = []
            for axis in ("voice", "audience"):
                for key in P.PERSONA_KEY_TO_VALUE[axis]:
                    if key == TOKEN:
                        continue
                    phrase = key.split(" ", 1)[1].lower()
                    if len(phrase) >= 4:
                        others.append(phrase)
            for phrase in others:
                with self.subTest(phrase=phrase):
                    self.assertIsNone(re.search(rf"\b{re.escape(phrase)}\b", text))

        def test_metadata_definition_carries_the_same_stance(self) -> None:
            definition = self._meta().get("definition", "")
            self.assertIn("receives the outcome without having made it", definition)

        def test_heuristics_do_not_collide_with_view(self) -> None:
            from talon_user.lib.axisConfig import AXIS_TOKEN_METADATA

            mine = self._meta().get("heuristics", [])
            self.assertGreaterEqual(len(mine), 5)
            theirs = set(AXIS_TOKEN_METADATA["scope"]["view"]["heuristics"])
            self.assertEqual(set(mine) & theirs, set())

        def test_kanji_is_unique(self) -> None:
            P = self._persona()
            kanji = P.PERSONA_KEY_TO_KANJI["voice"].get(TOKEN)
            self.assertEqual(kanji, "用")
            owners = [
                (axis, key)
                for axis, m in P.PERSONA_KEY_TO_KANJI.items()
                for key, value in m.items()
                if value == kanji
            ]
            self.assertEqual(owners, [("voice", TOKEN)])

        def test_neighbour_distinctions_exist_in_both_directions(self) -> None:
            P = self._persona()
            for other in VOICE_NEIGHBOURS:
                for src, dst in ((TOKEN, other), (other, TOKEN)):
                    with self.subTest(src=src, dst=dst):
                        entries = {
                            d["token"]: d["note"]
                            for d in P.PERSONA_TOKEN_METADATA["voice"].get(src, {}).get(
                                "distinctions", []
                            )
                        }
                        self.assertIn(dst, entries)
                        self.assertIn(f"{src} = ", entries[dst])
                        self.assertIn(f"; {dst} = ", entries[dst])

        def test_end_user_points_at_view(self) -> None:
            # One direction only: the axis catalog validator accepts distinction
            # targets that are axis tokens or tasks, so a scope token such as view
            # cannot point at a persona token. The pointer therefore lives on the
            # persona side, and the heuristics test keeps the two from colliding.
            mine = {d["token"]: d["note"] for d in self._meta().get("distinctions", [])}
            self.assertIn("view", mine)
            self.assertIn(f"{TOKEN} = ", mine["view"])
            self.assertIn("; view = ", mine["view"])
            # The contrast is who the speaker is and whether the position is held
            # as one among others, which a probe showed is where the two differ.
            self.assertIn("resolved from the subject", mine["view"])
            self.assertIn("named in the request", mine["view"])
            self.assertIn("one among others", mine["view"])
