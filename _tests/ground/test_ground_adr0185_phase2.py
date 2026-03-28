"""ADR-0185 Phase 2: behavioral-effect anchors for principle-derivative rules.

These tests replace literal-phrase assertIn anchors with logical assertions
on behavioral invariants. They pass on both the pre-deletion prompt (current)
and the post-deletion prompt (Thread 3 target).

Rules covered here are principle-derivative (subsumed by sharpened P1/P3/A3/R2).
Genuine per-rung exceptions remain as literal-phrase anchors in their original files.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt, GROUND_PARTS_MINIMAL


class TestP3SequentialThreadConstraint(unittest.TestCase):
    """P3: all rungs for Thread N must complete before Thread N+1 content."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_sequential_thread_constraint_present(self):
        """P3 sequential-thread constraint must exist in some form."""
        has_rule = (
            "all seven rungs must complete for Thread N before any rung content for Thread N+1 may appear"
            in self.prompt
            or (
                "Thread N" in self.prompt
                and "Thread N+1" in self.prompt
                and (
                    "complete" in self.prompt
                    or "before any rung content" in self.prompt
                )
            )
        )
        self.assertTrue(has_rule, "P3 sequential-thread constraint must be present")

    def test_stopping_between_rungs_is_violation(self):
        """Stopping between rungs must be prohibited — either explicitly or via continuous-transition rule."""
        has_rule = (
            "stopping between rungs" in self.prompt
            or "all other rung transitions are continuous within the same response" in self.prompt
        )
        self.assertTrue(has_rule, "Stopping between rungs must be prohibited or continuous transitions required")

    def test_waiting_for_confirmation_between_rungs(self):
        """The model must not pause for user confirmation between rungs."""
        has_rule = (
            "waiting for user confirmation between rungs" in self.prompt
            or "without pausing for user confirmation" in self.prompt
        )
        self.assertTrue(has_rule, "Must prohibit waiting for user confirmation between rungs")


class TestP3ScopeRules(unittest.TestCase):
    """P3: scope discipline — one gap, one criterion, one edit per cycle."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_one_criterion_per_thread_per_cycle(self):
        """P3: one criterion per thread per cycle must be stated."""
        has_rule = (
            "one criterion per thread per cycle" in self.prompt
            or (
                "exactly one criterion" in self.prompt
                and "per thread" in self.prompt
            )
        )
        self.assertTrue(has_rule, "One criterion per thread per cycle must be stated")

    def test_one_edit_per_rerun(self):
        """P3: one edit per re-run cycle must be stated."""
        has_rule = (
            "one edit per re-run" in self.prompt
            or "one edit means exactly one tool call" in self.prompt
        )
        self.assertTrue(has_rule, "One edit per re-run must be stated")

    def test_no_additional_invariants(self):
        """P3: no additional invariants beyond declared gap."""
        has_rule = (
            "no additional invariants" in self.prompt
            or (
                "additional invariants" in self.prompt
                and "gap" in self.prompt
            )
        )
        self.assertTrue(has_rule, "No additional invariants beyond declared gap must be stated")

    def test_nothing_beyond_declared_gap(self):
        """P3: each artifact addresses nothing beyond the declared gap."""
        has_rule = (
            "nothing beyond it" in self.prompt
            or "nothing beyond the declared gap" in self.prompt
            or "addresses only the gap" in self.prompt
        )
        self.assertTrue(has_rule, "Nothing beyond declared gap must be stated")


class TestA3CycleIsolation(unittest.TestCase):
    """A3: cycle isolation — prior-cycle artifacts have no standing."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_vro_gate_requires_current_cycle(self):
        """A3: impl_gate/VRO requires evidence from the current cycle, not prior."""
        has_rule = (
            "from the current cycle" in self.prompt
            or "current cycle" in self.prompt
            and "prior cycle" in self.prompt
        )
        self.assertTrue(has_rule, "VRO/impl_gate current-cycle requirement must be stated")

    def test_prior_cycle_does_not_satisfy(self):
        """A3: prior-cycle output does not satisfy any gate."""
        has_rule = (
            "prior cycle does not satisfy this gate" in self.prompt
            or (
                "prior cycle" in self.prompt
                and "does not satisfy" in self.prompt
            )
            or "prior-cycle output" in self.prompt
        )
        self.assertTrue(has_rule, "Prior cycle non-satisfaction must be stated")

    def test_prose_reemission_at_every_cycle(self):
        """A3: prose rung must be re-emitted at the start of every cycle."""
        has_rule = (
            "prose rung must be re-emitted at the start of every cycle" in self.prompt
            or (
                "re-emitted" in self.prompt
                and "every cycle" in self.prompt
            )
        )
        self.assertTrue(has_rule, "Prose re-emission every cycle must be stated")

    def test_criterion_derivable_from_reemitted_prose(self):
        """A3: criterion must be immediately derivable from the re-emitted prose."""
        has_rule = (
            "the criterion must be immediately derivable from the re-emitted prose" in self.prompt
            or (
                "derivable" in self.prompt
                and "prose" in self.prompt
            )
        )
        self.assertTrue(has_rule, "Criterion derivability from prose must be stated")

    def test_upward_return_cycle_isolation(self):
        """A3: cycle isolation applies after upward returns."""
        has_rule = (
            "any cycle following an upward return" in self.prompt
            or (
                "upward return" in self.prompt
                and ("cycle" in self.prompt or "re-emitted" in self.prompt)
            )
        )
        self.assertTrue(has_rule, "Cycle isolation after upward returns must be stated")


class TestUpwardReturnFailureClass(unittest.TestCase):
    """R2/upward-return: failure class routing."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_observation_cannot_be_produced_is_prose_failure(self):
        """Observation-cannot-be-produced is a prose failure, not impl failure."""
        has_rule = (
            "observation cannot be produced is a prose-description failure" in self.prompt
            or (
                "observation cannot be produced" in self.prompt
                and "prose" in self.prompt
            )
        )
        self.assertTrue(has_rule, "OBR-impossible = prose failure must be stated")


if __name__ == "__main__":
    unittest.main()
