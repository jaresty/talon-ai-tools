"""OBR why-sentence must name dev server as valid OBR artifact for UI components (ADR-0199 Thread 7)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRUIWhySentence(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_why_sentence_names_dev_server_for_ui(self):
        self.assertIn(
            "dev server",
            self.prompt,
            "Type taxonomy must name the dev server as the OBR invocable artifact for UI components",
        )

    def test_obr_why_sentence_distinguishes_test_renderer(self):
        self.assertIn(
            "test renderer",
            self.prompt,
            "Type taxonomy must distinguish test renderer (VRO-type) from dev server (OBR-type)",
        )

    def test_obr_why_sentence_names_ui_component(self):
        self.assertIn(
            "UI component",
            self.prompt,
            "Type taxonomy must explicitly reference UI components when explaining OBR invocation",
        )


if __name__ == "__main__":
    unittest.main()
