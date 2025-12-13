import re
import unittest
from typing import TYPE_CHECKING, Dict, List, Set

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import os

    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def _read_axis_keys(filename: str) -> Set[str]:
        path = os.path.join(BASE, "GPT", "lists", filename)
        keys: Set[str] = set()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                    or ":" not in line
                ):
                    continue
                key, _ = line.split(":", 1)
                keys.add(key.strip())
        return keys

    def _read_overlap_mapping() -> Dict[str, str]:
        """Parse tokens and fixed axes from the manual overlap analysis doc."""
        path = os.path.join(BASE, "docs", "adr", "033-axis-overlap-analysis.md")
        mapping: Dict[str, str] = {}
        token_line = re.compile(r"- \*\*(.+?)\*\* .*Decision:\s*\*(\w+)\*", re.IGNORECASE)
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = token_line.match(line.strip())
                if not m:
                    continue
                raw_tokens, axis = m.groups()
                axis_lower = axis.lower()
                # Split composite tokens like "direct/indirect" or "focus/focused".
                for part in re.split(r"[\/]", raw_tokens):
                    token = part.strip().lower()
                    if not token:
                        continue
                    mapping[token] = axis_lower
        return mapping

    class AxisOverlapAlignmentTests(unittest.TestCase):
        def setUp(self) -> None:
            self.axis_keys = {
                "completeness": _read_axis_keys("completenessModifier.talon-list"),
                "scope": _read_axis_keys("scopeModifier.talon-list"),
                "method": _read_axis_keys("methodModifier.talon-list"),
                "form": _read_axis_keys("formModifier.talon-list"),
                "channel": _read_axis_keys("channelModifier.talon-list"),
            }
            self.token_axis_map = _read_overlap_mapping()

        def test_tokens_align_with_manual_axis_decisions(self):
            """Tokens present in axis lists should respect the manual fixed-axis mapping."""
            for token, axis in self.token_axis_map.items():
                present_axes: List[str] = [
                    name for name, keys in self.axis_keys.items() if token in keys
                ]
                if not present_axes:
                    # Token alias not present in lists (e.g., focused vs focus); skip.
                    continue
                if axis == "style":
                    # Style axis has been retired; tokens now live under form/channel.
                    continue
                self.assertEqual(
                    present_axes,
                    [axis],
                    f"Token '{token}' present on axes {present_axes}, expected only {axis}",
                )
else:
    if not TYPE_CHECKING:
        class AxisOverlapAlignmentTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
