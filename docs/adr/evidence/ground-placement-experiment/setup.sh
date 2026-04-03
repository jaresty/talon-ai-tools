#!/usr/bin/env bash
# Setup script for ground protocol experiments.
# Creates isolated directories for each experiment with identical starter files.
# Usage: bash setup.sh

set -e

EXPERIMENTS=(exp1 exp2 exp3)

BUDGET_PY='"""Simple expense tracker."""


class Tracker:
    def __init__(self):
        self._spending: dict[str, list[float]] = {}

    def add(self, category: str, amount: float) -> None:
        if category not in self._spending:
            self._spending[category] = []
        self._spending[category].append(amount)

    def total(self, category: str) -> float:
        return sum(self._spending.get(category, []))

    def categories(self) -> list[str]:
        return list(self._spending.keys())

    def report(self) -> dict[str, float]:
        return {cat: self.total(cat) for cat in self.categories()}
'

TEST_BUDGET_PY='"""Tests for the expense tracker."""
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
'

BASE="/tmp/ground-experiment"

for exp in "${EXPERIMENTS[@]}"; do
    dir="$BASE/$exp"
    mkdir -p "$dir"
    echo "$BUDGET_PY" > "$dir/budget.py"
    echo "$TEST_BUDGET_PY" > "$dir/test_budget.py"
    echo "Created $dir"
done

echo ""
echo "Verifying all tests pass in each directory..."
for exp in "${EXPERIMENTS[@]}"; do
    dir="$BASE/$exp"
    result=$(python3 -m pytest "$dir/test_budget.py" -q 2>&1)
    if echo "$result" | grep -q "7 passed"; then
        echo "  $exp: OK (7 passed)"
    else
        echo "  $exp: FAIL"
        echo "$result"
    fi
done

echo ""
echo "Render experiment prompts:"
echo "  Exp 2: bash render_exp2.sh > $BASE/exp2/prompt.txt"
echo "  Exp 3: bash render_exp3.sh > $BASE/exp3/prompt.txt"
