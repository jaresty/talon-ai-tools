"""Content tests for the shoshin dialogue clause (per-context Terminal redesign).

Asserts the v4 dialogue clause properties in the SSOT description string:
- per-context Terminal (Ground property 1)
- four-label set including withdrawn (property 2)
- withdrawn carries a referent (property 3)
- agreement not required (property 4)
- participant-set completeness invariant (property 5)
"""

import unittest

from lib.axisConfig import axis_key_to_value_map

_SHOSHIN = axis_key_to_value_map("method")["shoshin"]


class ShoshinDialogueTerminationTests(unittest.TestCase):
    """The dialogue sub-clause governs multi-context (N>=2) termination per-context."""

    def test_participant_set_is_defined_from_message_fields(self):
        # property 5: participant set derived from Message from/to labels
        self.assertIn("participant set", _SHOSHIN)

    def test_termination_is_per_context(self):
        # property 1: every participant context owns its own Terminal line
        self.assertIn("Termination is per-context", _SHOSHIN)

    def test_four_terminal_labels_including_withdrawn(self):
        # property 2: converged | deadlock | divergence | withdrawn
        self.assertIn(
            "converged | deadlock | divergence | withdrawn", _SHOSHIN
        )

    def test_withdrawn_names_what_it_declines(self):
        # property 3: withdrawn carries a positive referent, not bare absence
        self.assertIn("withdrawn: no claim on", _SHOSHIN)

    def test_agreement_not_required_across_contexts(self):
        # property 4: labels of different contexts need not match
        self.assertIn("need not match", _SHOSHIN)

    def test_completeness_invariant_over_participant_set(self):
        # property 5: complete iff every participant label owns a Terminal
        self.assertIn("Termination check", _SHOSHIN)


if __name__ == "__main__":
    unittest.main()
