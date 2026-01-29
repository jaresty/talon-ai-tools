"""
Test that obsolete tokens from ADR 0091/0092 migrations are not present in axisConfig.

This test guards against legacy tokens lingering after migrations. Update OBSOLETE_TOKENS
when future token migrations occur.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import axisConfig


# Tokens removed in ADR 0091/0092 migrations
OBSOLETE_TOKENS = {
    'todo',           # → make (static prompt)
    'focus',          # → struct (scope)
    'system',         # → act (scope)
    'relations',      # → thing (scope)
    'steps',          # → flow (method)
    'announce',       # → bullets (form)
    'coach_junior',   # → teach_junior_dev (persona preset)
}


class TestObsoleteTokens(unittest.TestCase):
    """Verify obsolete tokens don't linger in axisConfig after migrations."""

    def test_no_obsolete_tokens_in_axis_config(self):
        """Verify removed tokens from ADR 0091/0092 are not in AXIS_KEY_TO_VALUE."""
        found_obsolete = []

        for axis_name, tokens in axisConfig.AXIS_KEY_TO_VALUE.items():
            for token in tokens:
                if token in OBSOLETE_TOKENS:
                    found_obsolete.append(f"{axis_name}.{token}")

        self.assertEqual(
            [], found_obsolete,
            f"Obsolete tokens found in axisConfig: {', '.join(found_obsolete)}"
        )


if __name__ == '__main__':
    unittest.main()
