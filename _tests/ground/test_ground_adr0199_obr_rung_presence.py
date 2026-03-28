"""Thread N complete blocked when OBR rung label absent from transcript (ADR-0199 Thread 1)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRRungPresenceGate(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_thread_complete_requires_obr_rung_label_in_transcript(self):
        # The protocol must state that the OBR rung label must appear in the
        # transcript for the current thread before Thread N complete fires.
        self.assertIn(
            "OBR rung label must appear in the transcript",
            self.prompt,
            "Protocol must require OBR rung label to appear in transcript before Thread N complete",
        )

    def test_obr_absence_is_protocol_violation_not_voiding(self):
        # Absence of OBR rung label is a protocol violation, not a void condition.
        # The void conditions handle OBR firing with invalid output; this handles OBR never firing.
        self.assertIn(
            "absence is a protocol violation",
            self.prompt,
            "Protocol must distinguish OBR absence (protocol violation) from OBR voiding",
        )


if __name__ == "__main__":
    unittest.main()
