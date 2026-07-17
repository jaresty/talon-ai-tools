"""Skip tests that require local environment features not present in CI."""
import importlib.util
import os

import pytest

_IN_CI = os.environ.get("CI") == "true"


def pytest_runtest_setup(item):
    source = item.fspath.read_text(encoding="utf-8")
    # Skip tests that require the Talon runtime when talon is not importable.
    if importlib.util.find_spec("talon") is None:
        if "from talon import" in source or "import talon\n" in source:
            pytest.skip("talon runtime not available")
    # Skip embedding tests in CI — embeddings are only generated locally.
    if _IN_CI and item.fspath.name == "test_embed_tokens.py":
        pytest.skip("embedding tests skipped in CI")
