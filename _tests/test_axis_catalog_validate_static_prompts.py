import importlib.machinery
import types
import unittest
from pathlib import Path
import subprocess


MODULE_PATH = Path("scripts/tools/axis-catalog-validate.py")


def _load_module():
    loader = importlib.machinery.SourceFileLoader("axis_catalog_validate", str(MODULE_PATH))
    module = types.ModuleType(loader.name)
    module.__file__ = str(MODULE_PATH)
    loader.exec_module(module)  # type: ignore
    return module


class AxisCatalogStaticPromptValidationTests(unittest.TestCase):
    def test_missing_static_prompt_sections_fail(self):
        mod = _load_module()
        catalog = {"axes": {}, "axis_list_tokens": {}}
        errors = mod.validate_static_prompt_sections_present(catalog)
        self.assertTrue(errors)
        self.assertIn("static_prompts", " ".join(errors))

    def test_missing_axis_list_tokens_triggers_error(self):
        mod = _load_module()
        catalog = {"axes": {"scope": {"focus": ""}}}  # axis_list_tokens missing
        errors = mod.validate_axis_tokens(catalog)
        self.assertTrue(errors)
        self.assertIn("axis list drift", " ".join(errors))
        errors = mod.validate_axis_tokens({"axis_list_tokens": {"scope": ["focus"]}})  # axes missing
        self.assertTrue(errors)
        self.assertIn("catalog missing axes", " ".join(errors))

    def test_static_prompt_sections_present_and_consistent(self):
        mod = _load_module()
        catalog = {
            "axes": {"scope": {"focus": ""}},
            "axis_list_tokens": {"scope": ["focus"]},
            "static_prompts": {
                "profiled": [
                    {"name": "describe", "axes": {"scope": "focus"}, "description": ""},
                    {"name": "infer", "axes": {"scope": "focus"}, "description": ""},
                ]
            },
            "static_prompt_descriptions": {"describe": "", "infer": ""},
            "static_prompt_profiles": {"describe": {}, "infer": {}},
        }
        # Presence check passes
        self.assertFalse(mod.validate_static_prompt_sections_present(catalog))
        # Static prompt axis alignment passes
        self.assertFalse(mod.validate_static_prompt_axes(catalog))
        # Description alignment passes
        self.assertFalse(mod.validate_static_prompt_descriptions(catalog))
        # Required profile check passes
        self.assertFalse(mod.validate_static_prompt_required_profiles(catalog, required=None))
        # Profile key alignment passes
        self.assertFalse(mod.validate_static_prompt_profile_keys(catalog))

    def test_cli_fails_when_static_prompts_missing(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {},
                "axis_list_tokens": {},
                # Intentionally omit static prompt sections to trigger failure.
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_required_profiles_missing_triggers_error(self):
        mod = _load_module()
        catalog = {
            "axes": {},
            "axis_list_tokens": {},
            "static_prompts": {"profiled": [{"name": "describe", "axes": {}, "description": ""}]},
            "static_prompt_descriptions": {"describe": ""},
            "static_prompt_profiles": {"describe": {}},
        }
        errors = mod.validate_static_prompt_required_profiles(catalog, required=["infer", "describe"])
        self.assertTrue(errors)
        self.assertIn("infer", " ".join(errors))

    def test_profile_key_alignment_drift_detected(self):
        mod = _load_module()
        catalog = {
            "axes": {},
            "axis_list_tokens": {},
            "static_prompts": {"profiled": [{"name": "describe", "axes": {}, "description": ""}]},
            "static_prompt_descriptions": {"describe": ""},
            "static_prompt_profiles": {"describe": {}, "infer": {}},
        }
        errors = mod.validate_static_prompt_profile_keys(catalog)
        self.assertTrue(errors)
        self.assertIn("infer", " ".join(errors))

    def test_descriptions_missing_entry_triggers_error(self):
        mod = _load_module()
        catalog = {
            "axes": {},
            "axis_list_tokens": {},
            "static_prompts": {
                "profiled": [
                    {"name": "describe", "axes": {}, "description": "desc"},
                    {"name": "infer", "axes": {}, "description": "in descr"},
                ]
            },
            "static_prompt_descriptions": {"describe": "desc"},  # infer missing
            "static_prompt_profiles": {"describe": {}, "infer": {}},
        }
        errors = mod.validate_static_prompt_descriptions(catalog)
        self.assertTrue(errors)
        self.assertIn("static_prompt_descriptions missing entry for 'infer'", " ".join(errors))

    def test_descriptions_extra_entry_triggers_error(self):
        mod = _load_module()
        catalog = {
            "axes": {},
            "axis_list_tokens": {},
            "static_prompts": {
                "profiled": [
                    {"name": "describe", "axes": {}, "description": "desc"},
                ]
            },
            "static_prompt_descriptions": {
                "describe": "desc",
                "infer": "should not be here",
            },
            "static_prompt_profiles": {"describe": {}},
        }
        errors = mod.validate_static_prompt_descriptions(catalog)
        self.assertTrue(errors)
        self.assertIn(
            "static_prompt_descriptions contains entry not in static_prompts.profiled: infer",
            " ".join(errors),
        )

    def test_extra_axis_list_tokens_axis_triggers_error(self):
        mod = _load_module()
        catalog = {
            "axes": {"scope": {"focus": ""}},
            "axis_list_tokens": {"scope": ["focus"], "channel": ["slack"]},
        }
        errors = mod.validate_axis_tokens(catalog)
        self.assertTrue(errors)
        self.assertIn(
            "axis_list_tokens contains axes not present in catalog axes: channel",
            " ".join(errors),
        )

    def test_cli_fails_on_extra_axis_list_tokens_axis(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {"scope": {"focus": ""}},
                "axis_list_tokens": {"scope": ["focus"], "channel": ["slack"]},
                "static_prompts": {"profiled": []},
                "static_prompt_descriptions": {},
                "static_prompt_profiles": {},
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_cli_succeeds_on_repo_catalog(self):
        # Integration check: the in-repo catalog validates cleanly with default options.
        rc = subprocess.call(
            ["python3", "scripts/tools/axis-catalog-validate.py", "--skip-list-files"],
            cwd=Path(__file__).resolve().parents[1],
        )
        self.assertEqual(rc, 0)

    def test_cli_fails_when_descriptions_missing(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {"scope": {"focus": ""}},
                "axis_list_tokens": {"scope": ["focus"]},
                "static_prompts": {
                    "profiled": [
                        {"name": "describe", "axes": {"scope": "focus"}, "description": "desc"}
                    ]
                },
                "static_prompt_descriptions": {},
                "static_prompt_profiles": {"describe": {}},
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_cli_fails_when_axis_list_tokens_missing(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {"scope": {"focus": ""}},  # axis_list_tokens missing
                "static_prompts": {"profiled": []},
                "static_prompt_descriptions": {},
                "static_prompt_profiles": {},
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_cli_fails_when_axes_missing(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {},
                "axis_list_tokens": {"scope": ["focus"]},
                "static_prompts": {"profiled": []},
                "static_prompt_descriptions": {},
                "static_prompt_profiles": {},
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_cli_fails_when_profile_keys_drift(self):
        mod = _load_module()
        original_axis_catalog = mod.axis_catalog
        try:
            mod.axis_catalog = lambda lists_dir=None: {  # type: ignore
                "axes": {"scope": {"focus": ""}},
                "axis_list_tokens": {"scope": ["focus"]},
                "static_prompts": {
                    "profiled": [
                        {"name": "describe", "axes": {"scope": "focus"}, "description": "desc"},
                    ]
                },
                "static_prompt_descriptions": {"describe": "desc"},
                "static_prompt_profiles": {"describe": {}, "infer": {}},  # extra profile drift
            }
            import sys

            original_argv = sys.argv
            sys.argv = ["axis-catalog-validate"]
            rc = mod.main()
            self.assertNotEqual(rc, 0)
        finally:
            mod.axis_catalog = original_axis_catalog
            import sys as _sys

            _sys.argv = original_argv

    def test_cli_requires_lists_dir_when_enforcing_list_checks(self):
        # Enforcing list validation without a lists dir should fail fast.
        proc = subprocess.run(
            ["python3", "scripts/tools/axis-catalog-validate.py", "--no-skip-list-files"],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("lists_dir is required", proc.stdout + proc.stderr)

    def test_cli_fails_on_empty_lists_dir(self):
        # Enforcing list validation against an empty lists dir should produce drift errors.
        repo_root = Path(__file__).resolve().parents[1]
        empty_dir = repo_root / "tmp" / "empty-lists-dir"
        empty_dir.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--no-skip-list-files",
                "--lists-dir",
                str(empty_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("list generation drift", proc.stdout + proc.stderr)

    def test_cli_succeeds_when_lists_dir_is_generated(self):
        # Positive path: enforce list checks against freshly generated lists.
        repo_root = Path(__file__).resolve().parents[1]
        lists_dir = repo_root / "tmp" / "generated-lists-dir"
        lists_dir.mkdir(parents=True, exist_ok=True)
        gen = subprocess.run(
            ["python3", "scripts/tools/generate_talon_lists.py", "--out-dir", str(lists_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(gen.returncode, 0, f"list generation failed: {gen.stdout}\n{gen.stderr}")

        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--no-skip-list-files",
                "--lists-dir",
                str(lists_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"validation failed: {proc.stdout}\n{proc.stderr}")

    def test_cli_warns_when_lists_dir_provided_but_skipped(self):
        repo_root = Path(__file__).resolve().parents[1]
        tmp_lists = repo_root / "tmp" / "skip-lists-dir"
        tmp_lists.mkdir(parents=True, exist_ok=True)
        # Skip list checks but still pass lists-dir; expect success with a note.
        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--skip-list-files",
                "--lists-dir",
                str(tmp_lists),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("lists_dir", proc.stdout + proc.stderr)
        self.assertIn("skipped", proc.stdout + proc.stderr)

    def test_cli_verbose_includes_lists_mode_and_counts(self):
        repo_root = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--skip-list-files",
                "--verbose",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        out = proc.stdout + proc.stderr
        self.assertIn("Axis catalog validation passed.", out)
        self.assertIn("lists_validation=skipped", out)
        self.assertIn("Axes=", out)
        self.assertIn("static_prompts=", out)

    def test_cli_detects_list_token_drift(self):
        # Enforcing list validation should fail when list tokens drift from the generator.
        repo_root = Path(__file__).resolve().parents[1]
        lists_dir = repo_root / "tmp" / "drift-lists-dir"
        lists_dir.mkdir(parents=True, exist_ok=True)
        gen = subprocess.run(
            ["python3", "scripts/tools/generate_talon_lists.py", "--out-dir", str(lists_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(gen.returncode, 0, f"list generation failed: {gen.stdout}\n{gen.stderr}")

        # Remove a token from completeness list to simulate drift.
        completeness_path = lists_dir / "completenessModifier.talon-list"
        lines = completeness_path.read_text(encoding="utf-8").splitlines()
        mutated = [line for line in lines if not line.strip().startswith("full:")]
        completeness_path.write_text("\n".join(mutated) + "\n", encoding="utf-8")

        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--no-skip-list-files",
                "--lists-dir",
                str(lists_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("list generation drift", proc.stdout + proc.stderr)

    def test_cli_rejects_non_directory_lists_dir(self):
        repo_root = Path(__file__).resolve().parents[1]
        # Create a file where a directory is expected.
        file_path = repo_root / "tmp" / "lists-file"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("not a directory", encoding="utf-8")

        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--no-skip-list-files",
                "--lists-dir",
                str(file_path),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("lists_dir is not a directory", proc.stdout + proc.stderr)

    def test_cli_detects_missing_list_files(self):
        repo_root = Path(__file__).resolve().parents[1]
        lists_dir = repo_root / "tmp" / "missing-lists-dir"
        if lists_dir.exists():
            for child in lists_dir.iterdir():
                child.unlink()
        else:
            lists_dir.mkdir(parents=True, exist_ok=True)

        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--no-skip-list-files",
                "--lists-dir",
                str(lists_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not found in lists_dir", proc.stdout + proc.stderr)

    def test_cli_warns_when_lists_dir_skipped_without_verbose(self):
        repo_root = Path(__file__).resolve().parents[1]
        lists_dir = repo_root / "tmp" / "skip-note-lists-dir"
        lists_dir.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [
                "python3",
                "scripts/tools/axis-catalog-validate.py",
                "--skip-list-files",
                "--lists-dir",
                str(lists_dir),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        note = proc.stdout + proc.stderr
        self.assertIn("lists_dir", note)
        self.assertIn("skipped", note)


if __name__ == "__main__":
    unittest.main()
