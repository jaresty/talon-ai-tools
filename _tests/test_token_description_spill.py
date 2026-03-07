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


try:
    from talon_user.lib.axisConfig import AXIS_TOKEN_METADATA
except ImportError:
    AXIS_TOKEN_METADATA = None  # type: ignore[assignment]


@unittest.skipIf(AXIS_KEY_TO_VALUE is None, "axisConfig not importable in this environment")
class ContextualiseDescriptionSpillTests(unittest.TestCase):
    def setUp(self):
        self.desc = AXIS_KEY_TO_VALUE["form"]["contextualise"]
        meta = (AXIS_TOKEN_METADATA or {}).get("form", {}).get("contextualise", {})
        self.meta_distinction_tokens = [d["token"] for d in meta.get("distinctions", [])]

    def test_no_with_pull_task_coupling_in_description(self):
        """contextualise description must not contain task-pairing conditional."""
        self.assertNotIn(
            "With pull:",
            self.desc,
            "'With pull:' task-pairing found in contextualise description (ADR-0152 T-5)",
        )

    def test_no_with_make_fix_task_coupling_in_description(self):
        """contextualise description must not contain make/fix task-pairing."""
        self.assertNotIn(
            "With make/fix:",
            self.desc,
            "'With make/fix:' task-pairing found in contextualise description (ADR-0152 T-5)",
        )

    def test_pull_task_pairing_migrated_to_use_when(self):
        """contextualise distinctions must reference pull task-pairing (ADR-0152 T-5 / ADR-0155 T-12)."""
        self.assertIn(
            "pull",
            self.meta_distinction_tokens,
            "pull task-pairing not found in contextualise distinctions (ADR-0152 T-5 / ADR-0155 T-12)",
        )

    def test_downstream_model_core_preserved(self):
        """contextualise description must retain its downstream-model core."""
        self.assertIn("downstream model", self.desc)


@unittest.skipIf(AXIS_KEY_TO_VALUE is None, "axisConfig not importable in this environment")
class SocraticDescriptionSpillTests(unittest.TestCase):
    def setUp(self):
        self.desc = AXIS_KEY_TO_VALUE["form"]["socratic"]
        meta = (AXIS_TOKEN_METADATA or {}).get("form", {}).get("socratic", {})
        self.meta_heuristics = meta.get("heuristics", [])

    def test_no_with_sort_plan_task_coupling_in_description(self):
        """socratic description must not contain sort/plan task-pairing conditional."""
        self.assertNotIn(
            "With sort/plan:",
            self.desc,
            "'With sort/plan:' task-pairing found in socratic description (ADR-0152 T-5)",
        )

    def test_no_with_probe_task_coupling_in_description(self):
        """socratic description must not contain probe task-pairing conditional."""
        self.assertNotIn(
            "With probe:",
            self.desc,
            "'With probe:' task-pairing found in socratic description (ADR-0152 T-5)",
        )

    def test_probe_task_pairing_migrated_to_use_when(self):
        """socratic metadata heuristics must reference probe task-pairing (ADR-0152 T-5 / ADR-0155 T-12)."""
        all_heuristics = " ".join(self.meta_heuristics)
        self.assertIn(
            "probe",
            all_heuristics,
            "probe task-pairing not found in socratic heuristics (ADR-0152 T-5 / ADR-0155 T-12)",
        )

    def test_socratic_core_preserved(self):
        """socratic description must retain its question-led Socratic core."""
        self.assertIn("question", self.desc.lower())
        self.assertIn("withholding", self.desc)


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
