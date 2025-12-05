import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelSource import Meta
    from talon_user.lib.modelState import GPTState

    class MetaSourceTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()

        def test_meta_source_returns_last_meta_when_present(self) -> None:
            GPTState.last_meta = "Model interpretation: parsed as refactor request"

            source = Meta()
            self.assertEqual(source.get_text(), GPTState.last_meta)

        def test_meta_source_raises_when_no_meta_available(self) -> None:
            GPTState.last_meta = ""

            source = Meta()
            with self.assertRaises(Exception):
                source.get_text()

else:
    if not TYPE_CHECKING:
        class MetaSourceTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
