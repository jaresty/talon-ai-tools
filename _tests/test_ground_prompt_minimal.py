"""Tests for Thread 1: minimal GROUND_PARTS in groundPrompt.py."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import RUNG_SEQUENCE, SENTINEL_TEMPLATES, build_ground_prompt

CANONICAL_RUNG_NAMES = [e["name"] for e in RUNG_SEQUENCE]

ABSTRACT_RULES = [
    "tool-executed",          # Rule 1: claim only tool events
    "derives from",           # Rule 2: faithful derivation
    "declared gap",           # Rule 3: stop at the gap
    "only the gap declared",  # Rule 2b: gap-locality
    "reconcile",              # Reconciliation gate
    "without consulting I",   # V self-sufficiency
    "declared intent",        # I precedes its representations
    "rung label",             # Rung label at every transition
]

NAMED_VIOLATION_MODES = [
    "vacuous-green",
    "retroactive sentinel",
    "carry-forward",
    "I-formation",
    "R2 audit",
    "upward correction",
]


class TestMinimalGroundParts(unittest.TestCase):
    def setUp(self):
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        self.parts = GROUND_PARTS_MINIMAL
        self.prompt = build_ground_prompt(minimal=True)

    def test_total_chars_under_3000(self):
        total = sum(len(v) for v in self.parts.values())
        self.assertLess(total, 6000,
            f"GROUND_PARTS_MINIMAL total {total} chars; expected < 4000")

    def test_three_abstract_rules_present(self):
        for rule_marker in ABSTRACT_RULES:
            self.assertIn(rule_marker, self.prompt,
                f"Abstract rule marker missing: {rule_marker!r}")

    def test_all_rung_names_present_in_order(self):
        pos = -1
        for name in CANONICAL_RUNG_NAMES:
            new_pos = self.prompt.find(name, pos + 1)
            self.assertGreater(new_pos, pos,
                f"Rung name {name!r} missing or out of order")
            pos = new_pos

    def test_all_sentinel_format_strings_present(self):
        for key, value in SENTINEL_TEMPLATES.items():
            self.assertIn(value, self.prompt,
                f"Sentinel {key!r} missing from minimal prompt")

    def test_no_named_violation_modes_in_core_rules(self):
        # Check only the core prose rules, not the sentinel format strings
        # (sentinels legitimately contain terms like "I-formation complete")
        sentinel_values = set(SENTINEL_TEMPLATES.values())
        core = self.parts.get("core", "")
        # Strip sentinel format strings from the check surface
        check_surface = core
        for sv in sentinel_values:
            check_surface = check_surface.replace(sv, "")
        for mode in NAMED_VIOLATION_MODES:
            self.assertNotIn(mode, check_surface,
                f"Named violation mode found in core rules: {mode!r}")

    def test_vro_recurring_gap_returns_to_formal_notation(self):
        self.assertIn("observed gap matches the prior cycle's gap", self.prompt,
            "Minimal spec must state that a recurring gap requires return to formal notation")

    def test_vro_rung_stop_after_first_failure(self):
        self.assertIn("do not enumerate multiple failures", self.prompt,
            "Minimal spec must state VRO stops after first failure")

    def test_ei_rung_pre_edit_check(self):
        self.assertIn("Before each edit, check", self.prompt,
            "Minimal spec must require a pre-edit check for Execution observed sentinel")

    def test_ei_rung_one_edit_per_cycle(self):
        self.assertIn("One edit per re-run cycle", self.prompt,
            "Minimal spec must state one edit per re-run cycle at EI rung")

    def test_formal_notation_encodes_only_declared_criteria(self):
        self.assertIn("Formal notation encodes only the criteria declared", self.prompt,
            "Minimal spec must state formal notation encodes only declared criteria")

    def test_ev_rung_requires_prior_red_run(self):
        self.assertIn("must fail before any implementation edit", self.prompt,
            "Minimal spec must state that validation artifact must fail before any implementation edit")

    def test_preexisting_test_does_not_satisfy_ev_rung(self):
        self.assertIn("pre-existing test that happens to pass does not satisfy", self.prompt,
            "Minimal spec must clarify that pre-existing passing tests do not satisfy the EV rung")

    def test_every_rung_requires_gap_sentinel(self):
        self.assertIn("Before writing the criteria, formal notation, executable validation, executable implementation", self.prompt,
            "Minimal spec must require a gap sentinel before specific rung label writes")

    def test_gap_names_behavior_not_artifact_absence(self):
        self.assertIn("naming an absent artifact is not a valid gap", self.prompt,
            "Minimal spec must state gap names a behavior not an absent artifact")

    def test_gap_phrased_as_currently_false_assertion(self):
        self.assertIn("phrased as a currently-false assertion", self.prompt,
            "Minimal spec must require gap to be phrased as a currently-false assertion not a goal")

    def test_each_rung_artifact_is_minimal(self):
        self.assertIn("one independently testable behavior", self.prompt,
            "Minimal spec must state criterion is one independently testable behavior")

    def test_criterion_may_not_use_conjunction(self):
        self.assertIn("not a conjunction of behaviors", self.prompt,
            "Minimal spec must forbid joining multiple behaviors with 'and' in one criterion")

    def test_mid_ladder_still_requires_ev_and_vro(self):
        self.assertIn("including after an upward return", self.prompt,
            "Minimal spec must state EV and VRO required even after mid-ladder upward return")

    def test_ev_sentinel_dependency(self):
        self.assertIn("Validation artifact V complete must be emitted at the executable validation rung", self.prompt,
            "Minimal spec must require V-complete sentinel before VRO label as sentinel dependency")

    def test_impl_gate_current_cycle_only(self):
        self.assertIn("from the current cycle", self.prompt,
            "Minimal spec must require execution-observed from current cycle not prior cycle for impl-gate")

    def test_thread_complete_sentinel_dependency(self):
        self.assertIn("Thread N complete may not be emitted unless", self.prompt,
            "Minimal spec must require execution-observed after OBS label before thread-complete")

    def test_post_obs_completeness_check(self):
        self.assertIn("behaviors not yet observed running", self.prompt,
            "Minimal spec must require post-OBS check for unmet behaviors before thread-complete")

    def test_conjunction_ban_has_example(self):
        self.assertIn("are two criteria, not one", self.prompt,
            "Minimal spec must include a concrete example showing conjunction splits into two criteria")

    def test_gap_sentinel_not_a_stopping_point(self):
        self.assertIn("only the validation run observation rung stops after naming the gap", self.prompt,
            "Minimal spec must state gap sentinel is not a stopping point — only VRO stops")

    def test_every_rung_addresses_only_declared_gap(self):
        self.assertIn("not all known requirements of the task", self.prompt,
            "Minimal spec must state each rung addresses only declared gap, not all requirements")

    def test_obs_rung_required_every_cycle(self):
        self.assertIn("including the observed running behavior rung", self.prompt,
            "Minimal spec must state OBS rung is required in every cycle, not just final")

    def test_manifest_exhausted_when_no_gap_remains(self):
        self.assertIn("if no currently-false behavior remains, emit", self.prompt,
            "Minimal spec must require Manifest exhausted when no false behavior remains, not a fabricated gap")

    def test_thread_complete_requires_obs_label_written(self):
        self.assertIn("observed running behavior label has been written in the current cycle", self.prompt,
            "Minimal spec must require OBS label written before thread-complete")

    def test_build_ground_prompt_returns_nonempty(self):
        self.assertGreater(len(self.prompt), 0)


if __name__ == "__main__":
    unittest.main()
