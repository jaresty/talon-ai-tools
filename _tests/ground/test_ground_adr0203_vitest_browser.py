"""ADR-0203 Thread 5: Vitest browser mode produces VRO-type, not OBR-type."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestVitestBrowserModeVROClassification(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_browser_mode_test_runner_produces_vro_type(self):
        self.assertIn(
            "browser mode",
            self.prompt,
            "Protocol must address browser-mode test runners (e.g., Vitest chromium) as VRO-type",
        )

    def test_chromium_test_runner_does_not_satisfy_obr(self):
        self.assertIn(
            "chromium",
            self.prompt,
            "Protocol must explicitly name chromium as a VRO-type producer to close the escape route",
        )


if __name__ == "__main__":
    unittest.main()
