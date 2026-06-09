import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    def _defn() -> str:
        return AXIS_KEY_TO_VALUE["form"]["cheatsheet"]

    class CheatsheetDefinitionTests(unittest.TestCase):
        def test_root_criterion_phrase(self) -> None:
            self.assertIn("each entry is a single line", _defn())

        def test_exactly_one_delimiter_allow_list(self) -> None:
            self.assertIn("followed by exactly one", _defn())

        def test_entry_adjacency_allow_list(self) -> None:
            self.assertIn(
                "Each entry line is immediately followed by the next entry line or a heading",
                _defn(),
            )

        def test_heading_identification(self) -> None:
            self.assertIn("a heading is a line containing no", _defn())
