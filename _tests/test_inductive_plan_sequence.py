"""Guard for the inductive-plan sequence in sequenceConfig.py.

One test per retained property; each test name is the assertion identity.
"""
import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


class TestInductivePlanSequence(unittest.TestCase):

    def setUp(self):
        from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences
        self.sequences = SEQUENCES
        self.validate = validate_sequences

    def entry(self):
        return self.sequences["inductive-plan"]

    def test_property_1_key_present(self):
        self.assertIn("inductive-plan", self.sequences)

    def test_property_2_replicate_dispatch_of_five(self):
        s = self.entry()["steps"][0]
        self.assertEqual(s.get("type"), "dispatch")
        self.assertEqual(s.get("fan_out"), "replicate")
        self.assertEqual(s.get("join"), "all")
        self.assertIs(s.get("isolation"), True)
        self.assertEqual(s.get("during_dispatch"), "show form:quiz")
        self.assertIn("exactly 5 agents", s.get("prompt_hint", ""))

    def test_property_3_induction_threshold_and_divergence(self):
        s = self.entry()["steps"][2]
        self.assertEqual(s.get("role"), "induction")
        self.assertIn("3 of 5", s.get("prompt_hint", ""))
        self.assertIn("divergence", s.get("prompt_hint", ""))

    def test_property_4_well_formed_entry(self):
        e = self.entry()
        errors = self.validate({"inductive-plan": e}, known_tokens=set())
        self.assertEqual(errors, [], f"validate_sequences reported errors: {errors}")
        self.assertEqual(e.get("mode"), "linear")
        self.assertNotEqual(e.get("heuristics"), [])
        self.assertTrue(e.get("heuristics"))
        self.assertTrue(e.get("example"))

    def test_property_5_step_structure(self):
        steps = self.entry()["steps"]
        self.assertEqual(
            [s["role"] for s in steps],
            ["independent plan sampling", "plan collection", "induction", "knowledge transfer"],
        )
        self.assertEqual(
            [s.get("token") for s in steps],
            [None, "task:show", "task:plan method:converge", "show form:quiz"],
        )
        self.assertIs(steps[3].get("optional"), True)


if __name__ == "__main__":
    unittest.main()
