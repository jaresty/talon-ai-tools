"""
Falsifiable tests for the 'orient' intent token definition.

orient: frames why a group is forming in a way easy to understand for a newcomer —
explains the subject's reason for existing and who it serves, without assuming
prior context, history, or familiarity.

Tests FAIL before orient is added to personaConfig.py; PASS after.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.personaConfig import PERSONA_KEY_TO_VALUE


ORIENT_DEF = PERSONA_KEY_TO_VALUE.get("intent", {}).get("orient", "")


def test_orient_intent_key_present():
    assert "orient" in PERSONA_KEY_TO_VALUE.get("intent", {}), (
        "'orient' key must be present in PERSONA_KEY_TO_VALUE['intent']"
    )


def test_orient_definition_mentions_newcomer():
    assert "first time" in ORIENT_DEF or "newcomer" in ORIENT_DEF or "new to" in ORIENT_DEF, (
        "orient definition must address a newcomer or first-time audience"
    )


def test_orient_definition_mentions_purpose():
    assert "reason for existing" in ORIENT_DEF or "why" in ORIENT_DEF or "purpose" in ORIENT_DEF, (
        "orient definition must frame the subject's purpose or reason for existing"
    )


def test_orient_definition_is_domain_agnostic():
    domain_nouns = ["team", "company", "organization", "product", "project", "group"]
    for noun in domain_nouns:
        assert noun not in ORIENT_DEF, (
            f"orient definition must be domain-agnostic — found domain noun '{noun}'"
        )
