"""Tests for token-rewrite sequence structure in sequenceConfig.py.

BD-INSERT: new drift+gap+clash diagnostic step inserted between abduce and mint+reify+hollow.
BD-REWRITE: step 2 token changed from mint+gap+hollow to mint+reify+hollow.
"""

from lib.sequenceConfig import SEQUENCES


def _token_rewrite_steps():
    return SEQUENCES["token-rewrite"]["steps"]


def test_token_rewrite_sequence_drift_gap_clash_step_present():
    """BD-INSERT: 'show mean drift gap chain clash' must appear in the token-rewrite steps."""
    tokens = [s.get("token", "") for s in _token_rewrite_steps()]
    assert "show mean drift gap chain clash" in tokens


def test_token_rewrite_sequence_drift_gap_clash_precedes_mint_reify_align_hollow():
    """BD-INSERT: drift+gap+chain+clash step must appear before mint+reify+align+enforce+hollow step."""
    tokens = [s.get("token", "") for s in _token_rewrite_steps()]
    assert tokens.index("show mean drift gap chain clash") < tokens.index("show mean mint reify align enforce hollow")


def test_token_rewrite_sequence_mint_reify_align_hollow_replaces_mint_gap_hollow():
    """BD-REWRITE: 'show mean mint reify align enforce hollow' present, old forms absent."""
    tokens = [s.get("token", "") for s in _token_rewrite_steps()]
    assert "show mean mint reify align enforce hollow" in tokens
    assert "show mean mint gap hollow" not in tokens
    assert "show mean mint reify align hollow" not in tokens


def test_token_rewrite_sequence_drift_step_includes_chain():
    """BD-CHAIN: 'show mean drift gap chain clash' must appear; 'show mean drift gap clash' (without chain) must not."""
    tokens = [s.get("token", "") for s in _token_rewrite_steps()]
    assert "show mean drift gap chain clash" in tokens
    assert "show mean drift gap clash" not in tokens


def test_token_rewrite_sequence_mint_step_includes_enforce():
    """BD-ENFORCE: 'show mean mint reify align enforce hollow' must appear; old form without enforce must not."""
    tokens = [s.get("token", "") for s in _token_rewrite_steps()]
    assert "show mean mint reify align enforce hollow" in tokens
    assert "show mean mint reify align hollow" not in tokens
