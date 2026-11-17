"""Routing guidance for optimization, feedback-loop and equilibrium tokens.

Each test is one retained property from the grounded request: reciprocal
distinctions for six token pairs, routing heuristics for balance and time, and
polar reading as pursuit and avoidance rather than as system dynamics.
"""

import re
import unittest

from lib.axisConfig import (
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_VALUE,
    AXIS_TOKEN_METADATA,
)

AXIS_OF = {
    "balance": "method",
    "grove": "method",
    "operations": "method",
    "polar": "method",
    "stable": "scope",
    "time": "scope",
    "loop": "form",
    "probability": "method",
    "pulse": "method",
}

# Table cells show the first five heuristics, so appending routing phrases must
# never change them. C0 records the cells as they were before the routing edits.
C0_TABLE_CELLS = {
    "balance": [
        "how do forces balance",
        "what opposing pressures exist",
        "what keeps this in equilibrium",
        "what countervailing forces",
        "how do trade-offs play out",
    ],
    "time": ["step by step", "in order", "over time", "what happens when", "sequence"],
    "probability": [
        "how likely is",
        "what's the probability",
        "expected value",
        "confidence interval",
        "statistical significance",
    ],
    "operations": [
        "throughput",
        "bottleneck analysis",
        "resource allocation",
        "scheduling problem",
        "queuing",
    ],
    "polar": [
        "what attracts and repels",
        "pull toward and push away from",
        "what are the incentives and disincentives",
        "goals and anti-goals",
        "what pulls toward and pushes away",
    ],
}

OPTIMIZE_PHRASE = "what does this service optimize for and what does it sacrifice"


def _meta(token: str) -> dict:
    return AXIS_TOKEN_METADATA[AXIS_OF[token]][token]


def _names(token: str, note: str) -> bool:
    return re.search(rf"\b{re.escape(token)}\b", note) is not None


def _distinguishes(source: str, target: str) -> bool:
    """D(source, target): source carries a note against target that names both."""
    for entry in _meta(source).get("distinctions") or []:
        note = entry.get("note", "")
        if entry.get("token") == target and _names(source, note) and _names(target, note):
            return True
    return False


class ReciprocalDistinctionTests(unittest.TestCase):
    def _assert_pair(self, a: str, b: str) -> None:
        self.assertTrue(_distinguishes(a, b), f"{a} states no distinction against {b}")
        self.assertTrue(_distinguishes(b, a), f"{b} states no distinction against {a}")

    def test_property_01_balance_stable_reciprocal(self):
        self._assert_pair("balance", "stable")

    def test_property_02_balance_grove_reciprocal(self):
        self._assert_pair("balance", "grove")

    def test_property_03_balance_loop_reciprocal(self):
        self._assert_pair("balance", "loop")

    def test_property_04_balance_operations_reciprocal(self):
        self._assert_pair("balance", "operations")

    def test_property_05_polar_stable_reciprocal(self):
        self._assert_pair("polar", "stable")

    def test_property_06_polar_operations_reciprocal(self):
        self._assert_pair("polar", "operations")


class RoutingHeuristicTests(unittest.TestCase):
    def test_property_07_balance_has_oscillation_heuristics(self):
        have = set(_meta("balance").get("heuristics") or [])
        want = {"oscillates", "overshoots", "self-correcting"}
        self.assertTrue(want <= have, f"balance heuristics missing {sorted(want - have)}")

    def test_property_08_time_has_delay_heuristics(self):
        have = set(_meta("time").get("heuristics") or [])
        want = {"delay between cause and effect", "lag"}
        self.assertTrue(want <= have, f"time heuristics missing {sorted(want - have)}")


class PolarReadsAsPursuitAndAvoidanceTests(unittest.TestCase):
    def test_property_09_polar_label_and_routing_concept(self):
        label = AXIS_KEY_TO_LABEL["method"]["polar"]
        concept = AXIS_KEY_TO_ROUTING_CONCEPT["method"]["polar"]
        self.assertEqual(label, "Pursuit and avoidance")
        for stem in ("ttractor", "epeller"):
            self.assertNotIn(stem, concept, f"polar routing concept still says {concept!r}")

    def test_property_10_polar_description_stops_claiming_dynamics(self):
        value = AXIS_KEY_TO_VALUE["method"]["polar"]
        for banned in ("system dynamics", "ttractor", "epeller"):
            self.assertNotIn(banned, value, f"polar description still contains {banned!r}")
        for required in ("pursuit", "avoidance"):
            self.assertIn(required, value, f"polar description lost {required!r}")


class NoiseAndOptimizeRoutingTests(unittest.TestCase):
    def test_property_11_pulse_probability_reciprocal(self):
        self.assertTrue(_distinguishes("pulse", "probability"), "pulse states no distinction against probability")
        self.assertTrue(_distinguishes("probability", "pulse"), "probability states no distinction against pulse")

    def test_property_12_probability_has_noise_heuristics(self):
        have = set(_meta("probability").get("heuristics") or [])
        want = {
            "estimate the underlying value from noisy data",
            "separate signal from noise in measurements",
        }
        self.assertTrue(want <= have, f"probability heuristics missing {sorted(want - have)}")

    def test_property_13_optimize_heuristic_moved_from_polar_to_operations(self):
        self.assertIn(OPTIMIZE_PHRASE, _meta("operations").get("heuristics") or [], "operations lacks the optimize heuristic")
        self.assertNotIn(OPTIMIZE_PHRASE, _meta("polar").get("heuristics") or [], "polar still carries the optimize heuristic")


class TableCellsUnchangedTests(unittest.TestCase):
    def test_property_14_touched_table_cells_unchanged(self):
        for token, before in C0_TABLE_CELLS.items():
            now = (_meta(token).get("heuristics") or [])[:5]
            self.assertEqual(now, before, f"{token} table cell changed: {now}")


if __name__ == "__main__":
    unittest.main()
