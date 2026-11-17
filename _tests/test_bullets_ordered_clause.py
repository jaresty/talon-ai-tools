"""The bullets form token numbers its items when their order carries meaning."""

import unittest

from lib.axisConfig import axis_key_to_value_map

_BULLETS = axis_key_to_value_map("form")["bullets"]


class BulletsOrderedClauseTests(unittest.TestCase):
    def test_states_numbering_condition(self):
        self.assertIn("numbered", _BULLETS)
        self.assertIn("order carries meaning", _BULLETS)

    def test_keeps_original_concern(self):
        self.assertIn("concise bullet points, avoiding long paragraphs", _BULLETS)

    def test_references_no_other_token(self):
        for token in axis_key_to_value_map("method"):
            self.assertNotIn(f"`{token}`", _BULLETS)
            self.assertNotIn(f" {token} token", _BULLETS)


if __name__ == "__main__":
    unittest.main()
