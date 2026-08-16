"""Behavioral tests for the frame-spike sequence in sequenceConfig.py.

frame-spike is a lightweight parallel frame-dispatch pattern: enumerate spike
frames, dispatch one throwaway spike artifact per frame (low rigor — no TDD, no
experiment cycle), then extract learnings across spikes. It is a collaborative
cycle: the user co-creates on the spikes and the loop re-enumerates frames each
round until the user decides to stop.

These tests assert the frame-spike entry's structure independently of the Go
grammar pipeline. They FAIL against a SEQUENCES dict that lacks frame-spike.
"""
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if TYPE_CHECKING:
    from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences


class TestFrameSpikeSequence(unittest.TestCase):

    def setUp(self):
        from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences
        self.sequences = SEQUENCES
        self.validate = validate_sequences

    # property [1]: the key exists
    def test_frame_spike_exists(self):
        self.assertIn("frame-spike", self.sequences,
                      "frame-spike sequence must exist in SEQUENCES")

    # property [2]: validate_sequences reports no errors for the whole dict
    def test_validate_sequences_passes_with_frame_spike(self):
        errors = self.validate(self.sequences, known_tokens=set())
        self.assertEqual(errors, [],
                         f"validate_sequences reported errors: {errors}")

    # property [3]: cycle mode with a non-empty stop_when
    def test_frame_spike_is_cycle_with_stop_when(self):
        seq = self.sequences["frame-spike"]
        self.assertEqual(seq.get("mode"), "cycle",
                         "frame-spike must be a cycle (collaborative spike loop)")
        self.assertIsInstance(seq.get("stop_when"), str,
                              "frame-spike stop_when must be a string")
        self.assertTrue(seq["stop_when"],
                        "frame-spike stop_when must be non-empty")

    # property [4]: at least one step pauses for the user (co-creation)
    def test_frame_spike_has_pause_step(self):
        seq = self.sequences["frame-spike"]
        has_pause = any(
            step.get("requires_user_input") or step.get("during_dispatch")
            for step in seq.get("steps", [])
        )
        self.assertTrue(has_pause,
                        "frame-spike (cycle) must have a step with "
                        "requires_user_input=True or during_dispatch")

    # property [5]: a dispatch step with join="all" fans out the spikes
    def test_frame_spike_dispatch_joins_all(self):
        seq = self.sequences["frame-spike"]
        dispatch_steps = [s for s in seq["steps"] if s.get("type") == "dispatch"]
        self.assertEqual(len(dispatch_steps), 1,
                         "frame-spike must have exactly one dispatch step")
        self.assertEqual(dispatch_steps[0].get("join"), "all",
                         "frame-spike dispatch must join all spike frames "
                         "(complementary directions, not competing)")
        self.assertEqual(dispatch_steps[0].get("fan_out"), "enumerate",
                         "frame-spike dispatch must fan out over enumerated frames")

    # property [5b]: shape is prism -> dispatch -> converge
    def test_frame_spike_shape(self):
        seq = self.sequences["frame-spike"]
        steps = seq["steps"]
        self.assertGreaterEqual(len(steps), 3,
                                "frame-spike must have prism, dispatch, converge steps")
        self.assertIn("method:prism", steps[0].get("token", ""),
                      "frame-spike step 1 must enumerate frames via method:prism")
        self.assertEqual(steps[1].get("type"), "dispatch",
                         "frame-spike step 2 must be the dispatch step")
        self.assertIn("method:converge", steps[-1].get("token", ""),
                      "frame-spike final step must converge via method:converge")

    # property: the throwaway/low-rigor distinction from frame-work is explicit
    def test_frame_spike_names_throwaway_and_low_rigor(self):
        seq = self.sequences["frame-spike"]
        blob = repr(seq).lower()
        self.assertIn("throwaway", blob,
                      "frame-spike must name the throwaway nature of spikes")
        # The dispatch inner must NOT carry the craft/TDD stack that frame-work uses.
        self.assertNotIn("witness ground gate falsify atomic", blob,
                         "frame-spike dispatch must be low-rigor — no TDD craft stack")

    # property: no quiz step (artifact-output sequence, like frame-work)
    def test_frame_spike_has_no_quiz_step(self):
        seq = self.sequences["frame-spike"]
        tokens = " ".join(s.get("token", "") for s in seq["steps"])
        self.assertNotIn("form:quiz", tokens,
                         "frame-spike is artifact-output — no quiz step")

    # property [5a]: the co-creation step carries the elicit+dimension token
    def test_frame_spike_cocreation_step_token(self):
        seq = self.sequences["frame-spike"]
        tokens = [s.get("token") for s in seq["steps"]]
        self.assertIn("make form:elicit method:dimension", tokens,
                      "frame-spike must have a co-creation step surfacing evaluation "
                      "axes (method:dimension) as holder instructions (form:elicit)")

    # property [5b]: that co-creation step pauses for the explorer
    def test_frame_spike_cocreation_step_requires_user_input(self):
        seq = self.sequences["frame-spike"]
        cocreate = [s for s in seq["steps"]
                    if s.get("token") == "make form:elicit method:dimension"]
        self.assertTrue(cocreate,
                        "frame-spike co-creation step must exist")
        self.assertTrue(cocreate[0].get("requires_user_input"),
                        "frame-spike co-creation step must pause for the explorer "
                        "(requires_user_input=True)")

    # property [6]: domain-agnostic
    def test_frame_spike_domain_agnostic(self):
        seq = self.sequences["frame-spike"]
        blob = repr(seq).lower()
        for banned in ("nais", " nn ", "--subject", ".tldraw", "html"):
            self.assertNotIn(banned, blob,
                             f"frame-spike must not contain domain-specific text {banned!r}")


if __name__ == "__main__":
    unittest.main()
