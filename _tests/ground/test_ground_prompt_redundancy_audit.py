"""Tests for ground prompt redundancy audit (ADR-0178: GROUND_PARTS removed; minimal is the only version)."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt

SENTINEL_SUBSTRINGS_MUST_REMAIN = [
    "Execution observed:",
    "Implementation gate cleared",
    "Validation artifact V complete",
    "Manifest exhausted",
    "Carry-forward:",
]

RUNG_NAMES_MUST_REMAIN = [
    "prose",
    "criteria",
    "formal notation",
    "executable validation",
    "validation run observation",
    "executable implementation",
    "observed running behavior",
]

CANDIDATE_A = "retroactive sentinels do not open gates"
CANDIDATE_C = "tool output that appeared before its sentinel is uncovered"


class TestEmphasisOnlyRepetitionsRemoved(unittest.TestCase):
    def test_candidate_a_not_duplicated(self):
        prose = GROUND_PARTS_MINIMAL["core"]
        count = prose.count(CANDIDATE_A)
        self.assertLessEqual(
            count,
            1,
            f"Candidate A appears {count} times; emphasis-only restatement should be reduced to \u22641",
        )

    def test_candidate_c_not_duplicated(self):
        prose = GROUND_PARTS_MINIMAL["core"]
        count = prose.count(CANDIDATE_C)
        self.assertLessEqual(
            count,
            1,
            f"Candidate C appears {count} times; emphasis-only restatement should be reduced to \u22641",
        )


class TestOutputIntegrityAfterAudit(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_all_sentinel_substrings_present(self):
        for s in SENTINEL_SUBSTRINGS_MUST_REMAIN:
            self.assertIn(s, self.prompt, f"Sentinel substring missing: {s}")

    def test_all_rung_names_present(self):
        for name in RUNG_NAMES_MUST_REMAIN:
            self.assertIn(name, self.prompt, f"Rung name missing: {name}")


class TestTotalCharCountDoesNotGrow(unittest.TestCase):
    def test_total_ground_parts_minimal_chars_does_not_exceed_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        # ADR-0178: baseline after D1-D7 applied to minimal
        BASELINE = 33300  # ADR-0212: EV import-check gate added (~169 chars)
        self.assertLessEqual(
            current,
            BASELINE,
            f"GROUND_PARTS_MINIMAL core chars {current} exceeds baseline {BASELINE}",
        )


if __name__ == "__main__":
    unittest.main()
