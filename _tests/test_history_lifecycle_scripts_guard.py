import pathlib
import re
import unittest
from typing import Iterable, TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


def _iter_python_files(paths: Iterable[pathlib.Path]) -> Iterable[pathlib.Path]:
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if path.name.startswith("."):
                continue
            yield path


if bootstrap is not None:
    REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
    IMPORT_PATTERN = re.compile(r"^(from|import) .*requestLog")

    class HistoryLifecycleScriptsGuardTests(unittest.TestCase):
        def test_scripts_use_history_lifecycle_facade(self) -> None:
            offenders: list[str] = []
            search_root = REPO_ROOT / "scripts" / "tools"
            for path in _iter_python_files([search_root]):
                relative = path.relative_to(REPO_ROOT)
                text = path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "requestLog" not in stripped:
                        continue
                    if IMPORT_PATTERN.match(stripped):
                        offenders.append(f"{relative}: {stripped}")
                        break
            self.assertFalse(
                offenders,
                msg=(
                    "Direct requestLog imports remain in scripts: "
                    + "; ".join(offenders)
                ),
            )
else:
    if not TYPE_CHECKING:

        class HistoryLifecycleScriptsGuardTests(unittest.TestCase):
            @unittest.skip(
                "historyLifecycle script guard requires bootstrap environment"
            )
            def test_placeholder(self) -> None: ...
