from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RequestGatingMacroGuardTests(unittest.TestCase):
    def test_talon_files_avoid_private_gating_helpers(self) -> None:
        banned_tokens = ("_request_is_in_flight", "_reject_if_request_in_flight")
        offenders: list[str] = []
        for path in ROOT.rglob("*.talon"):
            # Only inspect tracked Talon voice command files (skip samples/backups).
            if path.suffix != ".talon":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in banned_tokens:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")
        self.assertFalse(
            offenders,
            "Voice command files should not call private request gating helpers\n"
            + "\n".join(offenders),
        )

    def test_python_wrappers_import_request_gating(self) -> None:
        wrappers = []
        offenders: list[str] = []
        for path in ROOT.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "def _request_is_in_flight" in text:
                wrappers.append(path)
                if "requestGating import request_is_in_flight" not in text:
                    offenders.append(str(path.relative_to(ROOT)))
        # GPT.gpt.py imports from ..lib.requestGating; the pattern above still matches.
        self.assertTrue(
            wrappers,
            "Expected to discover request gating wrappers but none were found",
        )
        self.assertFalse(
            offenders,
            "Wrappers should import request_is_in_flight from lib.requestGating\n"
            + "\n".join(offenders),
        )

    def test_repo_avoids_request_bus_is_in_flight(self) -> None:
        allowlist = {
            Path("lib/requestGating.py"),
            Path("_tests/test_request_bus.py"),
            Path("_tests/test_request_gating_macros.py"),
        }
        offenders: list[str] = []
        for path in ROOT.rglob("*.py"):
            rel_path = path.relative_to(ROOT)
            if (
                path.name == "requestBus.py"
                or "__pycache__" in path.parts
                or rel_path in allowlist
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "requestBus.is_in_flight" in text or "bus_is_in_flight" in text:
                offenders.append(str(rel_path))
        self.assertFalse(
            offenders,
            "Modules should use lib.requestGating instead of requestBus.is_in_flight\n"
            + "\n".join(offenders),
        )
