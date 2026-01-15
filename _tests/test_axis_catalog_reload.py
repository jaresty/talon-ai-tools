import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from unittest import mock

    from talon_user.lib import axisCatalog

    class AxisCatalogReloadTests(unittest.TestCase):
        def setUp(self) -> None:
            self._orig_cache = axisCatalog._axis_config_cache
            self._orig_source = axisCatalog._axis_config_source
            self._orig_mtime = axisCatalog._axis_config_mtime

            axisCatalog._axis_config_cache = None
            axisCatalog._axis_config_source = None
            axisCatalog._axis_config_mtime = None

        def tearDown(self) -> None:
            axisCatalog._axis_config_cache = self._orig_cache
            axisCatalog._axis_config_source = self._orig_source
            axisCatalog._axis_config_mtime = self._orig_mtime

        def test_reload_runs_only_when_module_changes(self) -> None:
            with mock.patch.object(
                axisCatalog,
                "reload",
                wraps=axisCatalog.reload,
            ) as mock_reload:
                axisCatalog._axis_config_map()
                first_calls = mock_reload.call_count
                self.assertGreaterEqual(first_calls, 1)

                axisCatalog._axis_config_map()
                self.assertEqual(mock_reload.call_count, first_calls)

                axisCatalog._axis_config_mtime = -1.0
                axisCatalog._axis_config_map()
                self.assertEqual(mock_reload.call_count, first_calls + 1)

else:
    if not TYPE_CHECKING:

        class AxisCatalogReloadTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
