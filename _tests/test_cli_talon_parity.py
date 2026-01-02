import unittest
from pathlib import Path

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

CLI_BINARY = Path("bin/talon-cli")
SCHEMA_BUNDLE = Path("docs/schema/command-surface.json")


if bootstrap is None:

    class CLITalonParityPlaceholder(unittest.TestCase):
        @unittest.skip("Talon runtime cannot execute CLI parity harness")
        def test_skip_in_talon_runtime(self) -> None:  # pragma: no cover - Talon skip
            pass

else:

    class CLITalonParityTests(unittest.TestCase):
        def test_cli_binary_missing_records_blocker(self) -> None:
            if not CLI_BINARY.exists():
                self.skipTest(
                    "CLI binary absent; parity harness pending implementation"
                )

        def test_schema_bundle_missing_records_blocker(self) -> None:
            if not SCHEMA_BUNDLE.exists():
                self.skipTest(
                    "Shared command surface schema missing; parity harness pending implementation"
                )
