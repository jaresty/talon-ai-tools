"""Tests for the hollow token definition in axisConfig.py.

BD-CLASSIFY: hollow definition must require per-clause classification (governs behavior vs
describes meaning) before applying the root criterion, closing the escape route where
'each clause' is audited universally including concept-description clauses.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_hollow_definition_requires_per_clause_classification():
    """BD-CLASSIFY: definition must name per-clause classification before applying root criterion."""
    defn = AXIS_KEY_TO_VALUE["method"]["hollow"]
    assert "governs model behavior" in defn, (
        "hollow definition must require classifying each clause as governing behavior "
        "before applying the root criterion"
    )


def test_hollow_definition_names_concept_description_exclusion():
    """BD-CLASSIFY: definition must name concept-description clauses as excluded from hollow audit."""
    defn = AXIS_KEY_TO_VALUE["method"]["hollow"]
    assert "concept-description" in defn, (
        "hollow definition must name concept-description clauses as excluded "
        "so standalone hollow runs pre-filter correctly"
    )
