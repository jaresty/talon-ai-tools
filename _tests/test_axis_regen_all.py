import unittest
from pathlib import Path
import subprocess
import json


class AxisRegenAllTests(unittest.TestCase):
    def test_axis_regen_all_writes_outputs(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        if tmp_dir.exists():
            # Clean out known outputs to ensure the script regenerates them.
            for name in (
                "axisConfig.generated.py",
                "axisConfig.json",
                "axisCatalog.json",
                "readme-axis-lists.md",
                "readme-axis-cheatsheet.md",
                "static-prompt-docs.md",
                "readme-axis-tokens.md",
            ):
                try:
                    (tmp_dir / name).unlink()
                except FileNotFoundError:
                    pass
        subprocess.check_call(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
        )
        outputs = [
            "axisConfig.generated.py",
            "axisConfig.json",
            "axisCatalog.json",
            "readme-axis-lists.md",
            "readme-axis-cheatsheet.md",
            "readme-axis-readme.md",
            "static-prompt-docs.md",
            "static-prompt-readme.md",
            "readme-axis-tokens.md",
        ]
        for name in outputs:
            path = tmp_dir / name
            self.assertTrue(path.exists(), f"{name} not generated")
            self.assertGreater(path.stat().st_size, 0, f"{name} is empty")


class AxisRegenContentTests(unittest.TestCase):
    def test_generated_axis_config_keeps_helper_functions(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        subprocess.check_call(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
        )
        axis_config = (tmp_dir / "axisConfig.generated.py").read_text(encoding="utf-8")
        for marker in ("def axis_key_to_value_map", "def axis_docs_for", "def axis_docs_index"):
            self.assertIn(marker, axis_config, f"{marker} missing from generated axisConfig")

    def test_generated_axis_config_matches_tracked(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        subprocess.check_call(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
        )
        generated = (tmp_dir / "axisConfig.generated.py").read_text(encoding="utf-8")
        tracked = (repo_root / "lib" / "axisConfig.py").read_text(encoding="utf-8")
        self.assertEqual(generated, tracked, "Generated axisConfig drifted from tracked lib/axisConfig.py")

    def test_axis_catalog_json_includes_axes_and_list_tokens(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        subprocess.check_call(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
        )
        catalog = json.loads((tmp_dir / "axisCatalog.json").read_text(encoding="utf-8"))
        self.assertIn("axes", catalog)
        self.assertIn("axis_list_tokens", catalog)
        self.assertIn("static_prompts", catalog)
        self.assertIn("static_prompt_descriptions", catalog)
        self.assertIn("static_prompt_profiles", catalog)
        for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
            self.assertIn(axis, catalog["axes"], f"axis {axis} missing from axes map")
            self.assertIn(axis, catalog["axis_list_tokens"], f"axis {axis} missing from list tokens")
            self.assertTrue(catalog["axis_list_tokens"][axis], f"axis {axis} list tokens empty")
        # Ensure static prompt catalog is populated
        self.assertTrue(catalog["static_prompts"], "static prompt catalog empty")
        self.assertTrue(catalog["static_prompt_descriptions"], "static prompt descriptions empty")
        self.assertTrue(catalog["static_prompt_profiles"], "static prompt profiles empty")
        # Spot check an expected profile is present
        profiled = catalog["static_prompts"].get("profiled", [])
        profile_names = {p.get("name") for p in profiled}
        self.assertIn("describe", profile_names, "static prompt catalog missing 'describe' profile")

    def test_static_prompt_docs_include_required_headings(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_dir = repo_root / "tmp"
        subprocess.check_call(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
        )
        docs = (tmp_dir / "static-prompt-docs.md").read_text(encoding="utf-8")
        self.assertIn("## Static prompt catalog snapshots", docs)
        self.assertIn("## Static prompt catalog details", docs)
        # Guard that snapshots are produced with body content as well.
        self.assertIn("Other static prompts", docs)

    def test_axis_regen_all_runs_catalog_validation(self):
        repo_root = Path(__file__).resolve().parents[1]
        output = subprocess.check_output(
            ["python3", "scripts/tools/axis_regen_all.py"],
            cwd=repo_root,
            text=True,
        )
        self.assertIn("Axis catalog validation passed.", output)
        self.assertTrue(
            (repo_root / "tmp" / "axis-catalog-validate.log").exists(),
            "expected validation log to be written",
        )


if __name__ == "__main__":
    unittest.main()
