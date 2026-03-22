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
        self.assertLess(total, 3000,
            f"GROUND_PARTS_MINIMAL total {total} chars; expected < 3000")

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

    def test_ev_rung_requires_prior_red_run(self):
        self.assertIn("must fail before any implementation edit", self.prompt,
            "Minimal spec must state that validation artifact must fail before any implementation edit")

    def test_preexisting_test_does_not_satisfy_ev_rung(self):
        self.assertIn("pre-existing test that happens to pass does not satisfy", self.prompt,
            "Minimal spec must clarify that pre-existing passing tests do not satisfy the EV rung")

    def test_build_ground_prompt_returns_nonempty(self):
        self.assertGreater(len(self.prompt), 0)


if __name__ == "__main__":
    unittest.main()
