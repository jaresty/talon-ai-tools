"""Content tests for the shoshin inductive orchestration clause.

Asserts the inductive clause properties in the SSOT description string:
- the Orchestration enumeration admits inductive (property 1)
- N is declared in the Orchestration line (property 2)
- Reconcile reports Stable:/Unstable: lines; 'Stable: none' is valid (property 3)
- no exchange between contexts; isolation rule covers inductive (property 4)
- the clause names no other token (property 5)
"""

import unittest

from lib.axisConfig import axis_key_to_value_map

_SHOSHIN = axis_key_to_value_map("method")["shoshin"]


def _inductive_clause():
    start = _SHOSHIN.index("- inductive:")
    end = _SHOSHIN.index("Isolation mode", start)
    return _SHOSHIN[start:end]


class ShoshinInductiveTests(unittest.TestCase):
    def test_orchestration_enumeration_admits_inductive(self):
        # property 1
        self.assertIn(
            "[in-thread | delegate | parallel | dialogue | inductive]", _SHOSHIN
        )

    def test_shape_count_is_five(self):
        # property 1: the stated shape count matches the enumeration
        self.assertIn("one of five named shapes", _SHOSHIN)

    def test_n_is_declared_in_orchestration_line(self):
        # property 2
        self.assertIn("Orchestration: inductive (N=", _SHOSHIN)

    def test_reconcile_reports_stable_and_unstable(self):
        # property 3
        clause = _inductive_clause()
        self.assertIn("Stable:", clause)
        self.assertIn("Unstable:", clause)

    def test_empty_stable_set_is_valid(self):
        # property 3
        self.assertIn("Stable: none", _inductive_clause())

    def test_no_exchange_between_contexts(self):
        # property 4
        self.assertIn("no exchange", _inductive_clause())

    def test_isolation_rule_covers_inductive(self):
        # property 4: enforced vs declared-simulation resolution applies
        self.assertIn(
            "Isolation mode (parallel, dialogue and inductive)", _SHOSHIN
        )

    def test_parallel_states_when_it_is_chosen(self):
        # parallel's own focus: differences between contexts are the finding
        start = _SHOSHIN.index("- parallel:")
        end = _SHOSHIN.index("- dialogue:", start)
        self.assertIn(
            "Chosen when the differences between the contexts' conclusions are "
            "themselves the finding.",
            _SHOSHIN[start:end],
        )

    def test_clause_names_no_other_token(self):
        # property 5: orthogonality — no sibling token named in the clause
        clause = _inductive_clause()
        for other in ("lateral", "prism", "shift", "chain", "mean", "robust"):
            self.assertNotIn(other, clause)


if __name__ == "__main__":
    unittest.main()
