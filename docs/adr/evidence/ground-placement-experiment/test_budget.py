"""Tests for the expense tracker."""
import pytest
from budget import Tracker


class TestBasicTracking:
    def test_total_empty_category_is_zero(self):
        t = Tracker()
        assert t.total("food") == 0.0

    def test_add_single_expense(self):
        t = Tracker()
        t.add("food", 12.50)
        assert t.total("food") == 12.50

    def test_add_multiple_expenses_same_category(self):
        t = Tracker()
        t.add("food", 10.00)
        t.add("food", 5.50)
        assert t.total("food") == 15.50

    def test_categories_independent(self):
        t = Tracker()
        t.add("food", 20.00)
        t.add("transport", 8.00)
        assert t.total("food") == 20.00
        assert t.total("transport") == 8.00

    def test_categories_lists_all(self):
        t = Tracker()
        t.add("food", 10.00)
        t.add("transport", 5.00)
        assert set(t.categories()) == {"food", "transport"}

    def test_report_returns_totals_by_category(self):
        t = Tracker()
        t.add("food", 30.00)
        t.add("food", 10.00)
        t.add("transport", 15.00)
        assert t.report() == {"food": 40.00, "transport": 15.00}

    def test_empty_tracker_report(self):
        t = Tracker()
        assert t.report() == {}
