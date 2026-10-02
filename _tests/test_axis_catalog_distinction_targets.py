import importlib.util
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    def _load_validator():
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "tools"
            / "axis-catalog-validate.py"
        )
        spec = importlib.util.spec_from_file_location("axis_catalog_validate", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _catalog(distinctions):
        return {
            "axes": {"scope": {"act": "", "jobs": ""}},
            "static_prompts": {"profiled": [{"name": "probe"}], "unprofiled_tokens": []},
            "axis_token_metadata": {"scope": {"act": {"distinctions": distinctions}}},
        }

    class DistinctionTargetTests(unittest.TestCase):
        def test_resolvable_axis_token_target_passes(self) -> None:
            """A distinction naming a registered axis token is accepted."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "jobs"}])
            )
            self.assertEqual(errors, [])

        def test_task_target_passes(self) -> None:
            """A distinction may reference a task, not only an axis token."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "probe"}])
            )
            self.assertEqual(errors, [])

        def test_unknown_target_fails(self) -> None:
            """A distinction pointing at a renamed or removed token is rejected."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "resilience"}])
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("references unknown token 'resilience'", errors[0])

        def test_missing_token_field_fails(self) -> None:
            """A distinction with no target at all is rejected."""

            module = _load_validator()
            errors = module.validate_distinction_targets(_catalog([{"note": "x"}]))
            self.assertEqual(len(errors), 1)
            self.assertIn("no 'token' field", errors[0])

        def test_real_catalog_has_no_dangling_targets(self) -> None:
            """Regression: the committed catalog resolves every distinction target."""

            import sys

            root = Path(__file__).resolve().parents[1]
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            from lib.axisCatalog import axis_catalog

            module = _load_validator()
            errors = module.validate_distinction_targets(axis_catalog(lists_dir=None))
            self.assertEqual(errors, [], f"dangling distinction targets: {errors}")


if __name__ == "__main__":
    unittest.main()
