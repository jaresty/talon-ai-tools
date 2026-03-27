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
            "nothing omitted",
            _core(),
            "A: 'nothing omitted' invariant must survive the condensation",
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
        self.assertIn(
            "live running process",
            _core(),
            "B: live-running-process invariant must survive",
        )

    def test_b_file_read_exclusion_survives(self):
        self.assertIn(
            "A file read never satisfies",
            _core(),
            "B: file-read exclusion must survive as a concise declarative statement",
        )

    def test_b_renderToStaticMarkup_survives(self):
        # N2 regression guard — specific failure mode: LLM used test renderer instead of live process
        self.assertIn(
            "renderToStaticMarkup",
            _core(),
            "B: renderToStaticMarkup must survive (N2 regression guard — documented failure mode)",
        )

    def test_b_provenance_statement_survives(self):
        # N1 regression guard
        self.assertIn(
            "provenance statement does not replace",
            _core(),
            "B: provenance statement clause must survive (N1 regression guard)",
        )


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
    """D: five scattered Thread-N-complete precondition sentences replaced by unified gate list."""

    def test_d_gate_list_opener_survives(self):
        self.assertIn(
            "Thread N complete may not be emitted unless",
            _core(),
            "D: gate list must open with 'Thread N complete may not be emitted unless'",
        )

    def test_d_tool_call_in_transcript_anchor_survives(self):
        self.assertIn(
            "a tool call exists in the transcript after the observed running behavior label",
            _core(),
            "D: tool-call-in-transcript precondition must survive in gate list",
        )

    def test_d_obs_label_written_anchor_survives(self):
        self.assertIn(
            "observed running behavior label has been written after the most recent",
            _core(),
            "D: OBS-label-written precondition must survive in gate list",
        )

    def test_d_suite_next_action_anchor_survives(self):
        # E6 regression guard phrase
        self.assertIn(
            "only valid next action if no such result exists is the tool call that runs the suite",
            _core(),
            "D: suite next-action gate must survive in gate list (E6 anchor)",
        )

    def test_d_non_empty_verbatim_anchor_survives(self):
        self.assertIn(
            "non-empty verbatim output appears in the transcript after the observed running behavior label",
            _core(),
            "D: non-empty verbatim output precondition must survive in gate list",
        )

    def test_d_scattered_repetition_removed(self):
        # Old form repeated "✅ Thread N complete may not be emitted unless" 5 separate times
        # Unified gate list should have it once as opener + items
        count = _core().count("Thread N complete may not be emitted unless")
        self.assertEqual(
            count, 1,
            f"D: 'Thread N complete may not be emitted unless' should appear exactly once as gate-list opener, found {count}",
        )


if __name__ == "__main__":
    unittest.main()
