import os
import unittest


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern=None) -> unittest.TestSuite:
    """Forward unittest discovery to the ``_tests`` package."""
    if pattern is None:
        pattern = "test*.py"

    top_dir = os.path.dirname(os.path.dirname(__file__))
    start_dir = os.path.join(top_dir, "_tests")
    return loader.discover(start_dir=start_dir, pattern=pattern, top_level_dir=top_dir)
