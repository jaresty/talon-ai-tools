import unittest
import subprocess
from pathlib import Path
import json


class MakeAxisRegenAllTests(unittest.TestCase):
    def test_make_axis_regenerate_all(self):
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["make", "axis-regenerate-all"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                "make axis-regenerate-all failed:\n"
                f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        # Ensure snapshots exist in tmp/
        tmp = repo_root / "tmp"
        for name in (
            "axisConfig.generated.py",
            "axisConfig.json",
            "axisCatalog.json",
            "readme-axis-lists.md",
            "readme-axis-cheatsheet.md",
            "readme-axis-readme.md",
            "static-prompt-docs.md",
            "static-prompt-readme.md",
            "readme-axis-tokens.md",
        ):
            path = tmp / name
            self.assertTrue(path.exists(), f"{name} not generated")
            self.assertGreater(path.stat().st_size, 0, f"{name} is empty")
        self.assertIn("Axis catalog validation passed.", result.stdout)
        self.assertTrue(
            (tmp / "axis-catalog-validate.log").exists(),
            "axis-catalog-validate.log not written by axis-regenerate-all",
        )
        # Spot-check catalog contents for static prompts and list tokens.
        catalog = json.loads((tmp / "axisCatalog.json").read_text(encoding="utf-8"))
        self.assertIn("static_prompts", catalog)
        profiled = catalog["static_prompts"].get("profiled", [])
        self.assertTrue(profiled, "static_prompts.profiled should not be empty")
        self.assertIn("describe", {p.get("name") for p in profiled})
        self.assertIn("axis_list_tokens", catalog)
        self.assertTrue(catalog["axis_list_tokens"].get("scope"))


if __name__ == "__main__":
    unittest.main()
