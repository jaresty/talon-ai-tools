import unittest
import subprocess
from pathlib import Path
import json


class MakeAxisGuardrailsCiTests(unittest.TestCase):
    def test_make_axis_guardrails_ci_runs_regen(self):
        repo_root = Path(__file__).resolve().parents[1]
        subprocess.check_call(["make", "axis-guardrails-ci"], cwd=repo_root)
        # Spot-check regen outputs exist after the target runs.
        tmp = repo_root / "tmp"
        self.assertTrue((tmp / "axisConfig.generated.py").exists())
        self.assertTrue((tmp / "axisConfig.json").exists())
        catalog_path = tmp / "axisCatalog.json"
        self.assertTrue(catalog_path.exists())
        self.assertTrue((tmp / "readme-axis-lists.md").exists())
        self.assertTrue((tmp / "static-prompt-docs.md").exists())
        # Validate catalog carries static prompts and list tokens.
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertIn("static_prompts", catalog)
        profiled = catalog["static_prompts"].get("profiled", [])
        self.assertTrue(profiled, "static_prompts.profiled should not be empty")
        self.assertIn("describe", {p.get("name") for p in profiled})
        self.assertTrue(catalog.get("axis_list_tokens", {}))


if __name__ == "__main__":
    unittest.main()
