import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GenerateAxisConfigTests(unittest.TestCase):
        def test_axis_config_mapping_matches_generator_output(self) -> None:
            """Guardrail: axisConfig map should match generator's registry view."""

            repo_root = Path(__file__).resolve().parents[1]
            self.assertTrue((repo_root / "lib" / "axisConfig.py").exists(), "Expected lib/axisConfig.py to exist")

            # Import generator and runtime mapping.
            sys_path_was = list(__import__("sys").path)
            try:
                if str(repo_root) not in __import__("sys").path:
                    __import__("sys").path.insert(0, str(repo_root))

                from scripts.tools import generate_axis_config  # type: ignore
                from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

                generated_map = generate_axis_config._axis_mapping()  # type: ignore[attr-defined]
                self.assertDictEqual(
                    generated_map,
                    AXIS_KEY_TO_VALUE,
                    "axisConfig drift detected; regenerate with `make axis-regenerate` to sync to the registry",
                )
            finally:
                __import__("sys").path[:] = sys_path_was

        def test_json_output_matches_axis_config(self) -> None:
            """Guardrail: JSON output stays aligned with axisConfig mapping."""

            repo_root = Path(__file__).resolve().parents[1]
            script = repo_root / "scripts" / "tools" / "generate_axis_config.py"

            result = subprocess.run(
                [sys.executable, str(script), "--json"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    "generate_axis_config --json failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

            from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

            payload = json.loads(result.stdout)
            self.assertDictEqual(
                payload,
                AXIS_KEY_TO_VALUE,
                "JSON output drifted from axisConfig; regen should keep SSOT aligned",
            )
