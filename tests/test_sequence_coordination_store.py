"""Tests for frame-work coordination store encoding in sequenceConfig.py.
Each test FAILS against the old encoding and PASSES after the edit.
"""
import sys

from lib.sequenceConfig import SEQUENCES

seq = SEQUENCES["frame-work"]
step1 = seq["steps"][0]
dispatch = seq["steps"][1]
scope_claim = dispatch["inner"]["steps"][0]

def test_namespace_not_json_file():
    """BD1: step 1 must not prescribe a single shared JSON file."""
    assert "temp JSON file" not in step1["prompt_hint"], \
        "step1 prompt_hint still contains 'temp JSON file' (old encoding)"

def test_namespace_directory_present():
    """BD1: step 1 must name a namespace directory."""
    assert "namespace" in step1["prompt_hint"], \
        "step1 prompt_hint missing 'namespace' (new encoding)"

def test_per_frame_path_derivation():
    """BD2: step 1 must name per-frame path derivation from frame name."""
    hint = step1["prompt_hint"]
    assert "frame name" in hint or "per-frame path" in hint, \
        "step1 prompt_hint missing per-frame path derivation rule"

def test_format_freedom():
    """BD5: dispatch prompt_hint must name format as agent's choice."""
    hint = dispatch["prompt_hint"]
    assert "format" in hint and "agent" in hint, \
        "dispatch prompt_hint missing format freedom clause"

def test_claim_before_edit_gate():
    """BD4: scope claim must require claim before any file-modifying call."""
    hint = scope_claim["prompt_hint"]
    assert "Before any file-modifying" in hint, \
        "scope claim prompt_hint missing claim-before-edit gate"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
