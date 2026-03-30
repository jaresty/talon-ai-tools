"""Tests for ADR-0240: every assertIn in ground ADR tests has a red-state counterpart.

T1 red-state-detection: every phrase assertion in a ground ADR test must
   demonstrate both green (phrase present) and red (phrase absent) states via
   assertDetects helper; raw assertIn without red-state counterpart is
   insufficient.
"""
import importlib
import inspect
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase


class TestThread1_RedStateDetection(unittest.TestCase):
    """Base class and assertDetects helper exist and behave correctly."""

    def test_base_class_exists(self):
        from _tests.ground import ground_test_base
        self.assertTrue(hasattr(ground_test_base, "GroundADRTestBase"))

    def test_assert_detects_passes_when_phrase_present(self):
        class _T(GroundADRTestBase):
            pass
        t = _T()
        t.maxDiff = None
        # Should not raise
        t.assertDetects("hello", "say hello world")

    def test_assert_detects_fails_when_phrase_absent(self):
        class _T(GroundADRTestBase):
            pass
        t = _T()
        with self.assertRaises(AssertionError):
            t.assertDetects("hello", "say goodbye world")

    def test_assert_detects_red_state_catches_removal(self):
        """Red-state check: assertDetects would catch if phrase were removed."""
        class _T(GroundADRTestBase):
            pass
        t = _T()
        phrase = "unique-sentinel-xyz"
        text_with = f"some text {phrase} more text"
        text_without = text_with.replace(phrase, "\x00")
        # Green: present
        t.assertDetects(phrase, text_with)
        # Red: absent triggers failure
        with self.assertRaises(AssertionError):
            t.assertDetects(phrase, text_without)


if __name__ == "__main__":
    unittest.main()
