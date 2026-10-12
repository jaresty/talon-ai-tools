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

    def test_simulated_contexts_are_closed_blocks(self):
        # token-wide: an in-thread block opens at a header and closes at End:
        self.assertIn("closes at an 'End: <pass N | label>' line", _SHOSHIN)
        self.assertIn("none outside", _SHOSHIN)
        self.assertIn(
            "the next header does not appear until the current block has closed",
            _SHOSHIN,
        )

    def test_block_rule_exempts_real_agents(self):
        # real subagents are bounded by their result block, not by End:
        self.assertIn("a subagent tool-use result block bounds it", _SHOSHIN)

    def test_block_leak_check_is_inside_the_block(self):
        self.assertIn("that block's own leak check", _SHOSHIN)

    def test_reconcile_after_last_end_for_several_blocks(self):
        self.assertIn("after the last End: line", _SHOSHIN)

    def test_inductive_earlier_conclusions_are_inadmissible(self):
        self.assertIn(
            "conclusions of every earlier context are listed as inadmissible",
            _inductive_clause(),
        )

    def test_uniform_subagent_contexts_skip_earlier_conclusions_and_may_run_concurrently(self):
        # an enforced-isolation context never receives other conclusions, so
        # excluding them is vacuous and only forces sequential evaluation
        clause = _inductive_clause()
        self.assertIn(
            "Contexts run as declared in-thread simulations run in sequence", clause
        )
        self.assertIn(
            "a context run by a subagent tool-use block gets none of them", clause
        )
        self.assertIn("such contexts may run concurrently", clause)
        self.assertNotIn("run in sequence, with no exchange", clause)

    def test_stability_claim_is_not_overstated(self):
        # in-thread contexts share a reasoner, so stability shows robustness
        # across the selections tried, not independence from selection itself
        clause = _inductive_clause()
        self.assertIn("evidence it holds across the selections tried", clause)
        self.assertNotIn("evidence of independence from the selection", clause)

    def test_floor_is_three_contexts(self):
        # k-of-N needs a majority/minority split, which N=2 cannot give
        clause = _inductive_clause()
        self.assertIn("N being three or more", clause)
        self.assertNotIn("N being two or more", clause)

    def test_other_shapes_keep_two_or_more(self):
        # the floor change is scoped to inductive only
        self.assertIn("parallel: two or more isolated contexts", _SHOSHIN)
        self.assertIn("dialogue: two or more isolated contexts", _SHOSHIN)

    def test_mode_is_a_required_declaration_on_the_orchestration_line(self):
        # neither mode is a default: the line itself states which one ran
        clause = _inductive_clause()
        self.assertIn(
            "'Orchestration: inductive (N=<n>, [uniform | varied])'", clause
        )
        self.assertNotIn("By default", clause)
        self.assertNotIn("Disposition: varied", clause)

    def test_uniform_is_observable_by_comparison(self):
        self.assertIn("repeat the first context's", _inductive_clause())

    def test_varied_is_observable_by_comparison(self):
        self.assertIn(
            "apart from the earlier-conclusion lines", _inductive_clause()
        )

    def test_each_mode_carries_its_own_purpose(self):
        clause = _inductive_clause()
        self.assertIn("which conclusions recur across repeated runs", clause)
        self.assertIn("however the frames are selected", clause)

    def test_shared_stability_wording_states_the_guarantee(self):
        # the machinery guarantees no reliance on other contexts' conclusions
        self.assertIn(
            "none of which relied on another's conclusions", _inductive_clause()
        )

    def test_clause_names_no_other_token(self):
        # property 5: orthogonality — no sibling token named in the clause
        clause = _inductive_clause()
        for other in ("lateral", "prism", "shift", "chain", "mean", "robust"):
            self.assertNotIn(other, clause)


if __name__ == "__main__":
    unittest.main()
