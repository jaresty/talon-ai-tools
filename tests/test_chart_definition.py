"""
Falsifiable tests for the 'chart' form token definition.

Definition being implemented:
  'The response is a data visualization in which quantities or categories are
   encoded using position, size, color, or motion — when motion is used, it
   encodes a data variable such as time — with all data values embedded in the
   artifact. Prose labels, legends, and titles within the artifact are permitted
   as navigational aids.'

Tests FAIL when 'chart' is absent from AXIS_KEY_TO_VALUE['form'];
PASS after the token is added.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.axisConfig import AXIS_KEY_TO_VALUE, AXIS_KEY_TO_LABEL, AXIS_KEY_TO_KANJI, AXIS_KEY_TO_ROUTING_CONCEPT, AXIS_TOKEN_METADATA


CHART_DEF = AXIS_KEY_TO_VALUE.get("form", {}).get("chart", "")


def test_chart_key_present():
    assert "chart" in AXIS_KEY_TO_VALUE.get("form", {}), (
        "'chart' key must be present in AXIS_KEY_TO_VALUE['form']"
    )


def test_chart_artifact_commitment():
    assert "is a data visualization" in CHART_DEF, (
        "chart definition must contain 'is a data visualization' (D1/D2: artifact commitment)"
    )


def test_chart_spatial_encoding():
    assert "position, size, color, or motion" in CHART_DEF, (
        "chart definition must contain 'position, size, color, or motion' (A2: spatial encoding dimensions)"
    )


def test_chart_motion_clause():
    assert "encodes a data variable such as time" in CHART_DEF, (
        "chart definition must contain 'encodes a data variable such as time' (A4: motion encodes data)"
    )


def test_chart_embedded_clause():
    assert "all data values embedded in the artifact" in CHART_DEF, (
        "chart definition must contain 'all data values embedded in the artifact' (A5/C1: data embedded)"
    )


def test_chart_navigational_aids_clause():
    assert "Prose labels, legends, and titles" in CHART_DEF, (
        "chart definition must contain 'Prose labels, legends, and titles' (C2: prose as navigational aids)"
    )


def test_chart_label_present():
    label = AXIS_KEY_TO_LABEL.get("form", {})
    assert "chart" in label, (
        "'chart' must be present in AXIS_KEY_TO_LABEL['form']"
    )


def test_chart_kanji_present():
    kanji = AXIS_KEY_TO_KANJI.get("form", {})
    assert "chart" in kanji, (
        "'chart' must be present in AXIS_KEY_TO_KANJI['form']"
    )


def test_chart_routing_concept_present():
    routing = AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {})
    assert "chart" in routing, (
        "'chart' must be present in AXIS_KEY_TO_ROUTING_CONCEPT['form']"
    )


def test_chart_metadata_heuristics_present():
    meta = AXIS_TOKEN_METADATA.get("form", {}).get("chart", {})
    assert "heuristics" in meta and len(meta["heuristics"]) > 0, (
        "AXIS_TOKEN_METADATA['form']['chart'] must have a non-empty heuristics list"
    )
