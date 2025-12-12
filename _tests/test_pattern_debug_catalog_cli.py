import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class PatternDebugCatalogCliTests(unittest.TestCase):
        def test_pattern_debug_catalog_cli_outputs_json(self) -> None:
            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "pattern-debug-catalog.py"
            result = subprocess.run(
                [sys.executable, str(script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"pattern-debug-catalog failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("[", result.stdout)
            self.assertIn("]", result.stdout)
