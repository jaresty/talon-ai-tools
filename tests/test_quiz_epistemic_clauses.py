"""Tests asserting four epistemic clauses added to the quiz form token.

Each test must FAIL before the edit and PASS after.

Gap: quiz token defines procedural gates (Predict:, Hook:, etc.) but lacks
epistemic constraints on what constitutes a valid question. Four principles
must be added before the procedural gates:
1. Source material grounding — unsupported questions are invention not retrieval
2. Derived-framework guardrail — facilitator models are not domain knowledge
3. Information-gain gate — value by consequence, not enumeration position
4. LLM-augmented relevance (conditional) — recognizing vs unaided production
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["form"]["quiz"]


def test_quiz_source_material():
    assert "does not constitute retrieval demand" in defn()


def test_quiz_derived_framework():
    assert "facilitator-created model is not domain knowledge" in defn()


def test_quiz_information_gain():
    assert "not its position in an enumeration" in defn()


def test_quiz_llm_conditional():
    assert "when LLM assistance will be available in the target context" in defn()
