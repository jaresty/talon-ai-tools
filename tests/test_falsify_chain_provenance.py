"""Tests asserting key literal strings for the returned-object invocation provenance extension.

Each test must FAIL before the edit and PASS after.

Gap: condition (1) of the assertion-target provenance exception requires the identifier
to be directly initialized from the governed symbol. A chain like:
  const routes = governed(deps);
  const response = await routes.request(path, opts);
  expect(response.status, "label").toBe(201);
is blocked because `response` is initialized from `routes.request(...)`, not the governed
symbol directly. The extension permits a chain where each link satisfies conditions (1)-(3)
with the prior link substituting for the governed symbol.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_chain_provenance_label():
    assert "Returned-object invocation provenance" in defn()

def test_chain_provenance_first_link_governed_symbol():
    assert "the first identifier in the chain must have the governed symbol as its outermost non-structural callee" in defn()

def test_chain_provenance_subsequent_link_prior_member():
    assert "each subsequent identifier must have the immediately preceding chain identifier as the outermost non-structural callee of its initializer" in defn()

def test_chain_provenance_conditions_apply_to_each():
    assert "the same no-reassignment and structural-operations constraints from condition (3) apply to each intermediate identifier" in defn()
