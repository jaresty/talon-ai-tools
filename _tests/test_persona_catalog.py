import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class PersonaCatalogTests(unittest.TestCase):
        def test_persona_catalog_snapshot_contains_expected_presets(self) -> None:
            from talon_user.lib.personaCatalog import get_persona_intent_catalog

            snapshot = get_persona_intent_catalog()

            peer = snapshot.persona_presets.get("peer_engineer_explanation")
            self.assertIsNotNone(peer, "Expected peer engineer persona preset")
            if peer is not None:
                self.assertEqual(peer.spoken, "peer")
                self.assertEqual(peer.voice, "as programmer")
                self.assertEqual(peer.audience, "to programmer")

            self.assertEqual(
                snapshot.persona_spoken_map.get("mentor"),
                "teach_junior_dev",
                "Expected mentor spoken alias to map to teach_junior_dev",
            )

        def test_persona_catalog_snapshot_exposes_axis_tokens_and_intent_display(
            self,
        ) -> None:
            from talon_user.lib.personaCatalog import get_persona_intent_catalog

            snapshot = get_persona_intent_catalog()

            voice_tokens = snapshot.persona_axis_tokens.get("voice") or []
            self.assertIn("as teacher", voice_tokens)
            self.assertIn("as programmer", voice_tokens)

            intent_tokens = snapshot.intent_axis_tokens.get("intent") or []
            self.assertIn("teach", intent_tokens)
            self.assertIn("inform", intent_tokens)

            intent_display_map = snapshot.intent_display_map
            self.assertEqual(intent_display_map.get("teach"), "Teach / explain")
            self.assertEqual(intent_display_map.get("inform"), "Inform")

else:

    class PersonaCatalogTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
