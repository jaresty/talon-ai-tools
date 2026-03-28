"""Validation tests for ADR-0184: declarative conciseness rewrites to groundPrompt.py.

Four threads:
  A: exec_observed verbatim paragraph condensed
  B: OBR invocation enumeration condensed
  C: criteria falsifying-condition sentence condensed (partial — conjunctions untouched)
  D: Thread N complete preconditions unified into gate list
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


def _core():
    return GROUND_PARTS_MINIMAL["core"]


# ---------------------------------------------------------------------------
# Thread A — exec_observed verbatim paragraph
# ---------------------------------------------------------------------------

class TestAExecObservedVerbatim(unittest.TestCase):
    """A: verbose prohibited-forms enumeration removed; invariant 'verbatim, nothing omitted' remains."""

    def test_a_verbose_enumeration_removed(self):
        self.assertNotIn(
            "prose descriptions, inline summaries",
            _core(),
            "A: verbose prohibited-forms list must be removed — 'verbatim, nothing omitted' covers them",
        )

    def test_a_elision_markers_removed(self):
        self.assertNotIn(
            "elision markers",
            _core(),
            "A: elision markers example list must be removed — implied by 'nothing omitted'",
        )

    def test_a_verbatim_invariant_survives(self):
        self.assertIn(
            "no paraphrasing",
            _core(),
            "A: verbatim/no-paraphrasing invariant must survive the condensation",
        )

    def test_a_triple_backtick_survives(self):
        self.assertIn(
            "triple-backtick",
            _core(),
            "A: triple-backtick delimiter requirement must survive",
        )

    def test_a_preceding_tool_call_anchor(self):
        # Replaces old L1 anchor: "tool call must exist in the current response before"
        self.assertIn(
            "preceding tool call",
            _core(),
            "A: condensed paragraph must require a preceding tool call (replaces L1 anchor)",
        )

    def test_a_void_clause_survives(self):
        # Replaces old N5 anchor: "no delimited block"
        # Condensed form uses "void" near the block requirement
        self.assertIn(
            "voids the sentinel",
            _core(),
            "A: condensed paragraph must state deviations void the sentinel (replaces N5 anchor)",
        )


# ---------------------------------------------------------------------------
# Thread B — OBR invocation enumeration
# ---------------------------------------------------------------------------

class TestBOBRInvocation(unittest.TestCase):
    """B: per-artifact-type enumeration removed; live-process invariant + critical carveouts survive."""

    def test_b_web_ui_branch_removed(self):
        self.assertNotIn(
            "for a web UI, start the dev server and emit",
            _core(),
            "B: web-UI enumeration branch must be removed — live-process invariant covers it",
        )

    def test_b_cli_branch_removed(self):
        self.assertNotIn(
            "for a CLI, invoke it directly and emit its output",
            _core(),
            "B: CLI enumeration branch must be removed — live-process invariant covers it",
        )

    def test_b_live_process_invariant_survives(self):
        # ADR-0187: "live running process" prose deleted; concept now in P4 Clause B as "live-process invocation".
        self.assertIn(
            "live-process invocation",
            _core(),
            "B: live-process invocation must appear in P4 OBR sequence (ADR-0187: replaces 'live running process' prose)",
        )

    def test_b_file_read_exclusion_survives(self):
        # ADR-0187: "A file read never satisfies" prose deleted (duplicate of rung table void condition).
        # Behavioral guarantee carried by OBR rung table voids_if: "file read used as evidence".
        self.assertIn(
            "file read used as evidence",
            _core(),
            "B: file-read exclusion must be present in OBR rung table void condition",
        )

    def test_b_renderToStaticMarkup_survives(self):
        # N2 regression guard — specific failure mode: LLM used test renderer instead of live process
        self.assertIn(
            "renderToStaticMarkup",
            _core(),
            "B: renderToStaticMarkup must survive (N2 regression guard — documented failure mode)",
        )

    def test_b_provenance_statement_survives(self):
        # N1 regression guard — ADR-0187: "provenance statement does not replace" prose deleted.
        # Guarantee now carried by P4 Clause B: provenance statement (step 2) and live-process invocation (step 3) are both in the binding sequence.
        prompt = _core()
        prov_pos = prompt.find("provenance statement")
        lp_pos = prompt.find("live-process invocation")
        assert prov_pos != -1, "B: provenance statement must appear in P4 OBR sequence"
        assert lp_pos != -1, "B: live-process invocation must appear in P4 OBR sequence"
        assert prov_pos < lp_pos, "B: provenance statement (step 2) must precede live-process invocation (step 3) — N1 regression guard"


# ---------------------------------------------------------------------------
# Thread C — criteria falsifying-condition and manifest-quote sentences (partial)
# ---------------------------------------------------------------------------

class TestCCriteriaPartial(unittest.TestCase):
    """C: falsifying-condition sentence condensed; conjunction sentences with split-before-continuing untouched."""

    def test_c_content_gate_survives(self):
        self.assertIn(
            "content gate, not a self-check",
            _core(),
            "C: 'content gate, not a self-check' must survive in condensed form",
        )

    def test_c_conjunction_split_explicit_untouched(self):
        # Regression guard — must NOT be condensed
        self.assertIn(
            "it is a conjunction \u2014 split before continuing",
            _core(),
            "C: explicit conjunction 'split before continuing' must be untouched (regression guard)",
        )

    def test_c_conjunction_split_implicit_untouched(self):
        # Regression guard — must NOT be condensed
        self.assertIn(
            "data source is a conjunction \u2014 split before continuing",
            _core(),
            "C: implicit conjunction 'split before continuing' must be untouched (regression guard)",
        )

    def test_c_falsifying_no_implementation_internals_survives(self):
        self.assertIn(
            "no implementation internals",
            _core(),
            "C: condensed falsifying-condition sentence must state 'no implementation internals'",
        )


# ---------------------------------------------------------------------------
# Thread D — Thread N complete gate list
# ---------------------------------------------------------------------------

class TestDThreadNCompleteGateList(unittest.TestCase):
    """D: ADR-0187: gate list preamble and conditions (1)-(4) deleted (derivable from P4 Clause A+B); condition (5) kept."""

    def test_d_gate_list_opener_deleted(self):
        # ADR-0187: preamble "Thread N complete may not be emitted unless" deleted — derivable from P4 Clause A.
        self.assertNotIn(
            "Thread N complete may not be emitted unless",
            _core(),
            "D: gate list opener must be absent (ADR-0187: derivable from P4 Clause A sequence binding)",
        )

    def test_d_tool_call_in_transcript_anchor_deleted(self):
        # ADR-0187: condition (1) deleted — derivable from P4 Clause B step (3) live-process invocation.
        self.assertNotIn(
            "a tool call exists in the transcript after the observed running behavior label",
            _core(),
            "D: condition (1) must be absent (ADR-0187: derivable from P4 Clause B step 3)",
        )

    def test_d_obs_label_written_anchor_deleted(self):
        # ADR-0187: condition (2) deleted — derivable from P4 Clause A sequence binding.
        self.assertNotIn(
            "observed running behavior label has been written after the most recent",
            _core(),
            "D: condition (2) must be absent (ADR-0187: derivable from P4 Clause A)",
        )

    def test_d_suite_next_action_anchor_survives(self):
        # E6 regression guard phrase — condition (5) kept (genuine content gate, no principle path).
        self.assertIn(
            "only valid next action if no such result exists is the tool call that runs the suite",
            _core(),
            "D: suite next-action gate must survive (condition 5, kept per ADR-0187)",
        )

    def test_d_non_empty_verbatim_anchor_deleted(self):
        # ADR-0187: condition (3) deleted — derivable from P4 Clause A + exec_observed sentinel definition.
        self.assertNotIn(
            "non-empty verbatim output appears in the transcript after the observed running behavior label",
            _core(),
            "D: condition (3) must be absent (ADR-0187: derivable from P4 Clause A + sentinel def)",
        )

    def test_d_p4_sequence_binding_present(self):
        # P4 Clause A now carries the behavioral guarantee that formerly required the gate list.
        self.assertIn(
            "no completion sentinel for the rung may be emitted until the full sequence has been executed in order",
            _core(),
            "D: P4 Clause A sequence binding must be present to carry the deleted gate list guarantees",
        )


if __name__ == "__main__":
    unittest.main()
