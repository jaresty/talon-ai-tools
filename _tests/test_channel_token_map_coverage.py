"""Coverage test: every channel token must carry label, kanji, and routing concept.

A channel token defined in AXIS_KEY_TO_VALUE renders across surfaces (TUI2, help,
grammar export) that read its short label, single-character kanji glyph, and routing
concept. A token present in the value-map but absent from any of these companion maps
renders degraded. This test fails if any channel value-map key lacks an entry in
AXIS_KEY_TO_LABEL, AXIS_KEY_TO_KANJI, or AXIS_KEY_TO_ROUTING_CONCEPT.
"""

import unittest

from lib.axisConfig import (
    AXIS_KEY_TO_VALUE,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_ROUTING_CONCEPT,
)

_CHANNEL = "channel"


class ChannelTokenMapCoverageTests(unittest.TestCase):

    def setUp(self):
        self.tokens = set(AXIS_KEY_TO_VALUE.get(_CHANNEL, {}).keys())

    def test_every_channel_token_has_a_label(self):
        labels = set(AXIS_KEY_TO_LABEL.get(_CHANNEL, {}).keys())
        missing = self.tokens - labels
        self.assertEqual(
            missing, set(), f"channel tokens missing a label: {sorted(missing)}"
        )

    def test_every_channel_token_has_a_kanji(self):
        kanji = set(AXIS_KEY_TO_KANJI.get(_CHANNEL, {}).keys())
        missing = self.tokens - kanji
        self.assertEqual(
            missing, set(), f"channel tokens missing a kanji: {sorted(missing)}"
        )

    def test_every_channel_token_has_a_routing_concept(self):
        routing = set(AXIS_KEY_TO_ROUTING_CONCEPT.get(_CHANNEL, {}).keys())
        missing = self.tokens - routing
        self.assertEqual(
            missing, set(), f"channel tokens missing a routing concept: {sorted(missing)}"
        )


if __name__ == "__main__":
    unittest.main()
