import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    def _form() -> dict:
        return AXIS_KEY_TO_VALUE["form"]

    def _defn() -> str:
        return _form()["reference"]

    class ReferenceDefinitionTests(unittest.TestCase):
        # property [1]: cheatsheet renamed to reference
        def test_key_renamed_to_reference(self) -> None:
            self.assertIn("reference", _form())
            self.assertNotIn("cheatsheet", _form())

        # property [2a]: no single-line mandate remains
        def test_no_single_line_mandate(self) -> None:
            self.assertNotIn("single line", _defn())

        # property [2b]: labeled retrievability is required
        def test_labeled_retrievability(self) -> None:
            defn = _defn()
            self.assertIn("label", defn)
            self.assertIn("retriev", defn)
