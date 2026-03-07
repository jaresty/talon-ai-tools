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

        def test_legacy_persona_flat_dicts_removed_after_migration(self) -> None:
            """ADR-0156 T-10: PERSONA_KEY_TO_USE_WHEN and PERSONA_KEY_TO_GUIDANCE have been
            fully removed. Verify the migration is complete by confirming PersonaMetadataFor
            returns populated metadata for a known token (structured metadata is source of truth)."""
            import talon_user.lib.personaConfig as pc

            # The legacy flat dicts must not exist after full removal.
            self.assertFalse(
                hasattr(pc, "PERSONA_KEY_TO_USE_WHEN"),
                "ADR-0156 T-10: PERSONA_KEY_TO_USE_WHEN must be removed after full migration",
            )
            self.assertFalse(
                hasattr(pc, "PERSONA_KEY_TO_GUIDANCE"),
                "ADR-0156 T-10: PERSONA_KEY_TO_GUIDANCE must be removed after full migration",
            )
            # Verify structured metadata is populated for a known persona token.
            meta_map = pc.persona_token_metadata_map("presets")
            self.assertIn(
                "peer_engineer_explanation",
                meta_map,
                "ADR-0156 T-10: persona_token_metadata_map must return data for known preset",
            )

else:

    class PersonaCatalogTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
