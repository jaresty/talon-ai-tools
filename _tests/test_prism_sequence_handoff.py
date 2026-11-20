"""Guardrail: sequences that open a frame step with method:prism run prism in full.

prism requires enumeration and application in one response, so a step hint that
limits the step to enumeration contradicts the token. The application stays
out of the dispatched agents' context through the hand-off instead: each agent
gets its frame's label, Construal and Presupposes lines and the shared facts,
never a 'Reads fact K:' line.
"""

import unittest

from lib.sequenceConfig import SEQUENCES

NARROWING_PHRASES = (
    "enumeration is the only output",
    "Enumeration is the only output",
    "Do not apply any frame yet",
)

HANDOFF_PHRASE = "never any 'Reads fact K:' line"
PREVIEW_PHRASE = "record the difference rather than resolving it toward the preview"


def _prism_frame_sequences():
    for name, seq in SEQUENCES.items():
        steps = seq["steps"]
        for i, step in enumerate(steps):
            if not step.get("token", "").endswith("method:prism"):
                continue
            dispatch = next((s for s in steps[i + 1 :] if s.get("type") == "dispatch"), None)
            if dispatch is None or not dispatch.get("isolation"):
                continue
            # A frame step: the dispatch fans the enumerated frames out to agents.
            # token-rewrite's prism step enumerates test subjects, which are not frames.
            role = step.get("role", "")
            if "enumeration" not in role or "test subject" in role:
                continue
            yield name, i, step, dispatch, steps


class PrismSequenceHandoffTests(unittest.TestCase):
    def test_there_are_prism_frame_sequences(self):
        self.assertGreaterEqual(len(list(_prism_frame_sequences())), 8)

    def test_frame_spike_is_covered(self):
        self.assertIn("frame-spike", [name for name, *_ in _prism_frame_sequences()])

    def test_prism_step_hint_does_not_limit_to_enumeration(self):
        for name, _, step, _, _ in _prism_frame_sequences():
            with self.subTest(sequence=name):
                for phrase in NARROWING_PHRASES:
                    self.assertNotIn(phrase, step["prompt_hint"])

    def test_dispatch_hands_off_frames_without_readings(self):
        for name, _, _, dispatch, _ in _prism_frame_sequences():
            with self.subTest(sequence=name):
                self.assertIn(HANDOFF_PHRASE, dispatch["prompt_hint"])

    def test_synthesis_treats_step_one_readings_as_previews(self):
        for name, i, _, dispatch, steps in _prism_frame_sequences():
            with self.subTest(sequence=name):
                after = steps[steps.index(dispatch) + 1 :]
                synth = next(s for s in after if "method:converge" in s.get("token", "") or "method:orbit" in s.get("token", ""))
                self.assertIn(PREVIEW_PHRASE, synth["prompt_hint"])


if __name__ == "__main__":
    unittest.main()
