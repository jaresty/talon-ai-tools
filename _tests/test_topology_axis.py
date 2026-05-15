"""Governing tests for ADR-0236: topology axis (solo, witness, audit, relay, blind).

These tests must FAIL before implementation and PASS after.
"""
import unittest
from pathlib import Path

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

_TOPOLOGY_TOKENS = {"solo", "witness", "audit", "relay", "blind", "live"}

if bootstrap is not None:
    from talon_user.lib.axisConfig import (
        AXIS_KEY_TO_VALUE,
        AXIS_KEY_TO_LABEL,
        AXIS_KEY_TO_KANJI,
        AXIS_KEY_TO_ROUTING_CONCEPT,
        AXIS_TOKEN_METADATA,
    )
    from talon_user.lib.talonSettings import _AXIS_PRIORITY

    class TopologyAxisConfigTests(unittest.TestCase):
        def test_T1_axis_key_to_value_has_topology_tokens(self) -> None:
            """topology axis must be present in AXIS_KEY_TO_VALUE with all 5 tokens."""
            self.assertIn("topology", AXIS_KEY_TO_VALUE,
                          "topology axis missing from AXIS_KEY_TO_VALUE")
            tokens = set(AXIS_KEY_TO_VALUE["topology"].keys())
            self.assertEqual(tokens, _TOPOLOGY_TOKENS,
                             f"topology tokens mismatch: got {tokens}")
            for token, value in AXIS_KEY_TO_VALUE["topology"].items():
                self.assertIsInstance(value, str, f"topology.{token} value must be a string")
                self.assertTrue(value.strip(), f"topology.{token} value must be non-empty")

        def test_T2_axis_key_to_label_has_topology_tokens(self) -> None:
            """topology axis must be present in AXIS_KEY_TO_LABEL with all 5 tokens."""
            self.assertIn("topology", AXIS_KEY_TO_LABEL,
                          "topology axis missing from AXIS_KEY_TO_LABEL")
            tokens = set(AXIS_KEY_TO_LABEL["topology"].keys())
            self.assertEqual(tokens, _TOPOLOGY_TOKENS,
                             f"topology labels mismatch: got {tokens}")

        def test_T3_axis_key_to_kanji_has_topology_tokens(self) -> None:
            """topology axis must be present in AXIS_KEY_TO_KANJI with all 5 tokens."""
            self.assertIn("topology", AXIS_KEY_TO_KANJI,
                          "topology axis missing from AXIS_KEY_TO_KANJI")
            topology_kanji = AXIS_KEY_TO_KANJI["topology"]
            if isinstance(topology_kanji, dict):
                tokens = set(topology_kanji.keys())
                self.assertTrue(_TOPOLOGY_TOKENS.issubset(tokens),
                                f"topology kanji missing tokens: {_TOPOLOGY_TOKENS - tokens}")

        def test_T4_axis_key_to_routing_concept_has_topology_tokens(self) -> None:
            """topology axis must be present in AXIS_KEY_TO_ROUTING_CONCEPT with all 5 tokens."""
            self.assertIn("topology", AXIS_KEY_TO_ROUTING_CONCEPT,
                          "topology axis missing from AXIS_KEY_TO_ROUTING_CONCEPT")
            rc = AXIS_KEY_TO_ROUTING_CONCEPT["topology"]
            tokens = set(rc.keys())
            self.assertEqual(tokens, _TOPOLOGY_TOKENS,
                             f"topology routing concept mismatch: got {tokens}")
            for token, phrase in rc.items():
                self.assertTrue(phrase.strip(), f"topology.{token} routing concept must be non-empty")

        def test_T5_axis_token_metadata_has_topology_tokens(self) -> None:
            """topology axis must be present in AXIS_TOKEN_METADATA with all 5 tokens and non-empty heuristics."""
            self.assertIn("topology", AXIS_TOKEN_METADATA,
                          "topology axis missing from AXIS_TOKEN_METADATA")
            meta = AXIS_TOKEN_METADATA["topology"]
            tokens = set(meta.keys())
            self.assertEqual(tokens, _TOPOLOGY_TOKENS,
                             f"topology metadata mismatch: got {tokens}")
            for token, entry in meta.items():
                self.assertIn("heuristics", entry,
                              f"topology.{token} metadata missing heuristics")
                self.assertTrue(entry["heuristics"],
                                f"topology.{token} heuristics must be non-empty list")

        def test_T6_axis_priority_contains_topology(self) -> None:
            """topology must appear in _AXIS_PRIORITY before completeness."""
            self.assertIn("topology", _AXIS_PRIORITY,
                          "topology missing from _AXIS_PRIORITY in talonSettings.py")
            idx_topology = list(_AXIS_PRIORITY).index("topology")
            idx_completeness = list(_AXIS_PRIORITY).index("completeness")
            self.assertLess(idx_topology, idx_completeness,
                            "topology must appear before completeness in _AXIS_PRIORITY")

    class TopologyDefinitionStyleTests(unittest.TestCase):
        _PROHIBITIVE_PHRASES = (
            "do not", "don't", "avoid", "never", "must not", "only present",
            "present only",
        )

        def test_T8_topology_definitions_use_allow_list_phrasing(self) -> None:
            """topology token definitions must not use prohibitive (deny-list) phrasing."""
            definitions = AXIS_KEY_TO_VALUE.get("topology", {})
            offenders: list[str] = []
            for token, defn in definitions.items():
                lower = defn.lower()
                for phrase in self._PROHIBITIVE_PHRASES:
                    if phrase in lower:
                        offenders.append(f"{token!r}: contains {phrase!r}")
            self.assertFalse(
                offenders,
                "Topology definitions must use allow-list phrasing (observable output "
                "properties), not prohibitions:\n" + "\n".join(offenders),
            )

    class TopologyPromptGrammarTests(unittest.TestCase):
        def test_T7_prompt_grammar_axis_loop_includes_topology(self) -> None:
            """promptGrammar.py axis loop must include 'topology'."""
            grammar_src = Path("lib/promptGrammar.py").read_text()
            self.assertIn('"topology"', grammar_src,
                          "topology missing from axis loop in lib/promptGrammar.py")
