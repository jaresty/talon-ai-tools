"""Test: R2 audit section must precede sentinel."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_r2_audit_sentinel_closes_not_constitutes():
    p = _p()
    assert "sentinel closes the audit" in p or "closes the audit" in p or "does not constitute" in p

def test_r2_audit_section_must_precede_sentinel():
    p = _p()
    # The rule about ordering must be present
    assert "before" in p and ("audit section" in p or "audit" in p)
    # Specifically, there should be a rule that the sentinel may not be emitted unless an audit section exists
    assert ("audit section" in p and "before" in p) or "sentinel closes" in p or "sentinel may not be emitted" in p
