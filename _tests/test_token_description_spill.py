"""Specifying validation for ADR-0152 T-1 and T-2: token description spill reduction.

Asserts that policy/ethics language has been removed from `verify` and that
methodological prescription has been removed from `balance`.  These tests are
intentionally narrow — each assertion targets the exact phrase that constitutes
spill, so failure uniquely identifies the unremoved content.
"""
import unittest
from typing import TYPE_CHECKING

try:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE
except ImportError:
    AXIS_KEY_TO_VALUE = None  # type: ignore[assignment]


@unittest.skipIf(AXIS_KEY_TO_VALUE is None, "axisConfig not importable in this environment")
class VerifyDescriptionSpillTests(unittest.TestCase):
    def setUp(self):
        self.desc = AXIS_KEY_TO_VALUE["method"]["verify"]

    def test_no_authority_transfer_language(self):
        """verify must not contain policy language about authority transfer."""
        self.assertNotIn(
            "transfer authority",
            self.desc,
            "Policy phrase 'transfer authority' found in verify description (ADR-0152 T-1)",
        )

    def test_no_human_oversight_language(self):
        """verify must not contain AI-safety framing about human oversight."""
        self.assertNotIn(
            "human oversight",
            self.desc,
            "Policy phrase 'human oversight' found in verify description (ADR-0152 T-1)",
        )

    def test_no_trust_beyond_model_language(self):
        """verify must not contain the trust-beyond-model phrase."""
        self.assertNotIn(
            "trust beyond the model",
            self.desc,
            "Policy phrase 'trust beyond the model' found in verify description (ADR-0152 T-1)",
        )

    def test_falsification_core_preserved(self):
        """The falsification core of verify must be retained after trim."""
        self.assertIn(
            "falsification pressure",
            self.desc,
            "Core falsification language missing from verify description",
        )
        self.assertIn(
            "causal chain integrity",
            self.desc,
            "Core causal chain language missing from verify description",
        )


@unittest.skipIf(AXIS_KEY_TO_VALUE is None, "axisConfig not importable in this environment")
class BalanceDescriptionSpillTests(unittest.TestCase):
    def setUp(self):
        self.desc = AXIS_KEY_TO_VALUE["method"]["balance"]

    def test_no_perturbation_dynamics_prescription(self):
        """balance must not specify perturbation dynamics methodology."""
        self.assertNotIn(
            "restoring or destabilizing dynamics",
            self.desc,
            "Methodology prescription 'restoring or destabilizing dynamics' found in balance (ADR-0152 T-2)",
        )

    def test_no_stable_configuration_prescription(self):
        """balance must not prescribe what to do with every stable configuration."""
        self.assertNotIn(
            "No configuration may be treated as stable",
            self.desc,
            "Methodology prescription 'No configuration may be treated as stable' found in balance (ADR-0152 T-2)",
        )

    def test_balancing_forces_core_preserved(self):
        """The balancing-forces core of balance must be retained after trim."""
        self.assertIn(
            "balancing forces",
            self.desc,
            "Core 'balancing forces' language missing from balance description",
        )
