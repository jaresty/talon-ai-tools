"""Tests for ADR-0215: Ground prompt second-half reduction.

Three changes to GROUND_PARTS_MINIMAL["core"]:
1. VRO harness error routing: three verbose clauses → compact routing table (~350→~130 chars)
2. Criteria A2 restatement: removed (~200 chars)
3. Criteria batch-collect restatement: removed (~250 chars)
4. OBR rationalization: compressed to why-sentence (~100→~80 chars)
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0215VerboseClausesAbsent(unittest.TestCase):
    """Thread 1: verbose harness error routing prose is replaced by compact table."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_missing_impl_verbose_clause_absent(self):
        self.assertNotIn(
            "Gap: and \U0001f7e2 Implementation gate cleared may not be emitted after a harness error",
            self.core,
            "ADR-0215: verbose missing-impl clause must be absent",
        )

    def test_test_file_error_verbose_clause_absent(self):
        self.assertNotIn(
            "same block rule applies; the only valid next token is a tool call that repairs the test file",
            self.core,
            "ADR-0215: verbose test-file-error clause must be absent",
        )

    def test_test_interaction_verbose_clause_absent(self):
        self.assertNotIn(
            "the tests loaded and ran but could not interact with the component under test",
            self.core,
            "ADR-0215: verbose test-interaction-failure clause must be absent",
        )


class TestADR0215CompactRoutingTablePresent(unittest.TestCase):
    """Thread 2: compact routing table is present with all three routes."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_compact_routing_table_header_present(self):
        self.assertIn(
            "Harness error routing",
            self.core,
            "ADR-0215: compact routing table header must be present",
        )

    def test_missing_impl_route_present(self):
        self.assertIn(
            "missing-implementation-file \u2192 EI directly",
            self.core,
            "ADR-0215: missing-implementation-file → EI route must be present",
        )

    def test_test_file_error_route_present(self):
        self.assertIn(
            "test-file-error",
            self.core,
            "ADR-0215: test-file-error route must be present",
        )
        idx = self.core.find("test-file-error")
        window = self.core[idx:idx+100]
        self.assertIn("EV repair", window, "ADR-0215: test-file-error must route to EV repair")

    def test_test_interaction_route_present(self):
        self.assertIn(
            "test-interaction-failure",
            self.core,
            "ADR-0215: test-interaction-failure route must be present",
        )
        idx = self.core.find("test-interaction-failure")
        window = self.core[idx:idx+100]
        self.assertIn("EV repair", window, "ADR-0215: test-interaction-failure must route to EV repair")

    def test_all_three_block_gap_and_impl_gate(self):
        self.assertIn(
            "all three block",
            self.core,
            "ADR-0215: compact table must state all three block Gap: and impl_gate",
        )


class TestADR0215A2RestatementAbsent(unittest.TestCase):
    """Thread 3: A2 type-context restatement at criteria rung is removed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_a2_forward_gate_prose_absent(self):
        self.assertNotIn(
            "after the criterion is written, the only valid next token is the formal notation rung label",
            self.core,
            "ADR-0215: A2 forward gate prose must be absent",
        )

    def test_content_type_context_prose_absent(self):
        self.assertNotIn(
            "each rung label opens a content-type context",
            self.core,
            "ADR-0215: content-type context prose must be absent",
        )

    def test_type_violation_prose_absent(self):
        self.assertNotIn(
            "type violation under A2",
            self.core,
            "ADR-0215: per-rung A2 type violation prose must be absent",
        )


class TestADR0215BatchCollectAbsent(unittest.TestCase):
    """Thread 4: batch-collect thread-sequencing restatement is removed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_per_thread_label_prose_absent(self):
        self.assertNotIn(
            "criteria rung label is per-thread",
            self.core,
            "ADR-0215: per-thread criteria label prose must be absent",
        )

    def test_batch_collect_prose_absent(self):
        self.assertNotIn(
            "batch-collecting criteria for multiple threads under one criteria label",
            self.core,
            "ADR-0215: batch-collect prose must be absent",
        )


class TestADR0215OBRWhySentence(unittest.TestCase):
    """Thread 5: OBR rationalization compressed to why-sentence."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_old_obr_enumeration_absent(self):
        self.assertNotIn(
            "none of the following satisfies the OBR gate",
            self.core,
            "ADR-0215: verbose OBR enumeration must be absent",
        )

    def test_new_obr_why_sentence_present(self):
        self.assertIn(
            "prior evidence",
            self.core,
            "ADR-0215: OBR why-sentence must name prior evidence",
        )
        self.assertIn(
            "only a live-process invocation in the current cycle does",
            self.core,
            "ADR-0215: OBR why-sentence must name live-process invocation as the only satisfier",
        )


class TestADR0215CharCountReduced(unittest.TestCase):
    """Thread 6: char-count — changes reduce core string length."""

    def test_char_count_below_adr0214_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        ADR0214_BASELINE = 32090  # measured after ADR-0214
        self.assertLess(
            current,
            ADR0214_BASELINE,
            f"ADR-0215: core string ({current} chars) must be shorter than ADR-0214 baseline ({ADR0214_BASELINE})",
        )


if __name__ == "__main__":
    unittest.main()
