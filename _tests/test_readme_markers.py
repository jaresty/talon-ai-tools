import unittest
from pathlib import Path


class ReadmeMarkersTests(unittest.TestCase):
    def test_axis_markers_present(self):
        readme = Path("GPT/readme.md").read_text(encoding="utf-8")
        self.assertIn("Completeness (`completenessModifier`):", readme)
        self.assertIn("  - Additional form/channel notes:", readme)

    def test_static_prompt_markers_present(self):
        readme = Path("GPT/readme.md").read_text(encoding="utf-8")
        self.assertIn("## Static prompt catalog snapshots", readme)
        self.assertIn("## Static prompt catalog details", readme)


if __name__ == "__main__":
    unittest.main()
