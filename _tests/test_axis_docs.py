import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import axisConfig, axisMappings

    class AxisDocsTests(unittest.TestCase):
        def test_axis_docs_for_matches_axis_docs_map_across_axes(self) -> None:
            axes = ["completeness", "scope", "method", "style"]
            for axis in axes:
                with self.subTest(axis=axis):
                    docs = axisConfig.axis_docs_for(axis)
                    mapping = axisMappings.axis_docs_map(axis)

                    self.assertTrue(docs)
                    keys = {doc.key for doc in docs}
                    self.assertEqual(keys, set(mapping.keys()))
                    for doc in docs:
                        self.assertEqual(doc.description, mapping[doc.key])

        def test_axis_docs_index_includes_expected_axes(self) -> None:
            index = axisConfig.axis_docs_index()
            # At minimum, the core Concordance axes should be present.
            for axis in ("completeness", "scope", "method", "style"):
                with self.subTest(axis=axis):
                    self.assertIn(axis, index)
                    docs = index[axis]
                    mapping = axisMappings.axis_docs_map(axis)
                    self.assertTrue(docs)
                    keys = {doc.key for doc in docs}
                    self.assertEqual(keys, set(mapping.keys()))
                    for doc in docs:
                        self.assertEqual(doc.description, mapping[doc.key])

        def test_axis_docs_default_group_and_flags_are_empty(self) -> None:
            docs = axisConfig.axis_docs_for("completeness")
            self.assertTrue(docs)
            for doc in docs:
                with self.subTest(key=doc.key):
                    self.assertIsNone(doc.group)
                    self.assertEqual(doc.flags, frozenset())


else:
    if not TYPE_CHECKING:

        class AxisDocsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
