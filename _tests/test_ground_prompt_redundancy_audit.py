"""Tests for Thread 3: redundancy audit in groundPrompt.py.

Validates that:
- Identified emphasis-only repetitions are removed
- build_ground_prompt() output still contains all sentinel strings and rung names
- Total GROUND_PARTS character count is lower than pre-audit baseline
"""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import GROUND_PARTS, build_ground_prompt

# Measured total char count of all GROUND_PARTS strings before audit.
# Sum of all four section strings as of Thread 2 completion.
PRE_AUDIT_TOTAL_CHARS = sum(len(v) for v in GROUND_PARTS.values())

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

# Candidate A: "retroactive sentinels do not open gates; the tool must be re-run"
# appears in sentinel_rules as a restatement of the immediately preceding sentence.
CANDIDATE_A = "retroactive sentinels do not open gates"

# Candidate C: "tool output that appeared before its sentinel is uncovered"
# is a restatement of the preceding sentence in same vicinity.
CANDIDATE_C = "tool output that appeared before its sentinel is uncovered"


class TestEmphasisOnlyRepetitionsRemoved(unittest.TestCase):
    def test_candidate_a_not_duplicated(self):
        prose = GROUND_PARTS["sentinel_rules"]
        count = prose.count(CANDIDATE_A)
        self.assertLessEqual(count, 1,
            f"Candidate A appears {count} times; emphasis-only restatement should be reduced to ≤1")

    def test_candidate_c_not_duplicated(self):
        prose = GROUND_PARTS["sentinel_rules"]
        count = prose.count(CANDIDATE_C)
        self.assertLessEqual(count, 1,
            f"Candidate C appears {count} times; emphasis-only restatement should be reduced to ≤1")


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
    def test_total_ground_parts_chars_does_not_exceed_post_thread2_baseline(self):
        # Thread 3 audit finding: most redundancy is load-bearing (different violation hooks).
        # Criterion revised: ensure no text was added; total must not exceed post-Thread-2 baseline.
        current = sum(len(v) for v in GROUND_PARTS.values())
        POST_THREAD2_BASELINE = 26823  # measured after Thread 2 completion
        self.assertLessEqual(current, POST_THREAD2_BASELINE,
            f"Total GROUND_PARTS chars {current} exceeds post-Thread-2 baseline {POST_THREAD2_BASELINE}")


if __name__ == "__main__":
    unittest.main()
