"""Tests for the 'stable' scope token invariant-lens sharpening.

Promotes the latent invariance clause in stable's definition to a named focus and
adds dynamics-phrased heuristics so invariant-framed queries route to stable.
See axisConfig.py stable entry in AXIS_KEY_TO_VALUE and AXIS_TOKEN_METADATA.
"""

import unittest

from lib.axisConfig import AXIS_KEY_TO_VALUE, axis_token_metadata

_STABLE_DEF = AXIS_KEY_TO_VALUE["scope"]["stable"]
_STABLE_META = axis_token_metadata().get("scope", {}).get("stable", {})
_STABLE_HEURISTICS = _STABLE_META.get("heuristics", [])

# The four dynamics-phrased heuristics added to close routing gaps (steps 4/6).
NEW_HEURISTICS = [
    "what is preserved under change",
    "what returns to itself after a disturbance",
    "what stays true as the system changes",
    "what is invariant across states",
]

# Pre-existing heuristics that must survive the edit (property [4] — no regression).
RETAINED_HEURISTICS = [
    "what persists",
    "backward-compatible",
]


class StableInvariantLensTests(unittest.TestCase):
    def test_definition_promotes_invariant_lens(self):
        """property [1]: invariant lens is a named focus in the definition tail."""
        self.assertIn(
            "the properties preserved as the system changes "
            "— what returns to itself after a disturbance",
            _STABLE_DEF,
            "stable definition must promote the invariant lens to a named focus",
        )

    def test_definition_drops_old_trailing_analysis_phrase(self):
        """property [2]: the old downstream-analysis phrasing is removed."""
        self.assertNotIn(
            "analyzing how perturbations affect their continuity",
            _STABLE_DEF,
            "old trailing analysis phrase must be replaced by the named invariant focus",
        )

    def test_new_dynamics_heuristics_present(self):
        """property [3]: all four dynamics-phrased heuristics are added."""
        for phrase in NEW_HEURISTICS:
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase,
                    _STABLE_HEURISTICS,
                    f"stable heuristics must include dynamics phrase: {phrase!r}",
                )

    def test_existing_heuristics_retained(self):
        """property [4]: pre-existing heuristics are not dropped by the edit."""
        for phrase in RETAINED_HEURISTICS:
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase,
                    _STABLE_HEURISTICS,
                    f"pre-existing stable heuristic must be retained: {phrase!r}",
                )


if __name__ == "__main__":
    unittest.main()
