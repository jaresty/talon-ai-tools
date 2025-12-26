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
    ALLOWED = {
        pathlib.Path("lib/historyLifecycle.py"),
        pathlib.Path("lib/requestLog.py"),
        pathlib.Path("GPT/gpt.py"),
    }
    IMPORT_PATTERN = re.compile(r"^(from|import) .*requestLog")

    class HistoryLifecycleFacadeGuardTests(unittest.TestCase):
        def test_no_direct_requestlog_imports_outside_facade(self) -> None:
            offenders: list[str] = []
            search_roots = [REPO_ROOT / "lib", REPO_ROOT / "GPT"]
            for path in _iter_python_files(search_roots):
                relative = path.relative_to(REPO_ROOT)
                if relative in ALLOWED:
                    continue
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
                    "Direct requestLog imports remain outside historyLifecycle façade: "
                    + "; ".join(offenders)
                ),
            )
else:
    if not TYPE_CHECKING:

        class HistoryLifecycleFacadeGuardTests(unittest.TestCase):
            @unittest.skip("historyLifecycle guard tests require bootstrap environment")
            def test_placeholder(self) -> None: ...
