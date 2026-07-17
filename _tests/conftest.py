"""Skip tests that require the Talon runtime when talon is not importable."""
import importlib.util
import sys


def pytest_runtest_setup(item):
    # If talon is not importable, skip any test file that imports from it.
    if importlib.util.find_spec("talon") is None:
        source = item.fspath.read_text(encoding="utf-8")
        if "from talon import" in source or "import talon\n" in source:
            import pytest
            pytest.skip("talon runtime not available")
