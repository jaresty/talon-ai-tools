from lib.groundPrompt import build_ground_prompt

def _p(): return build_ground_prompt()

def test_gap_may_not_be_emitted_after_vro_harness():
    p = _p()
    # The explicit prohibition must use the exact phrase pattern to be unambiguous
    assert (
        "🔴 Gap: may not be emitted" in p and "harness" in p
        or "harness error" in p and "VRO" in p and "🔴 Gap: may not" in p
    )

def test_ei_rung_label_only_after_vro_harness_missing_file():
    p = _p()
    # Must say EI rung label is the only valid next token after VRO harness (missing file)
    idx = p.find("missing implementation file")
    assert idx != -1
    window = p[idx:idx+300]
    assert "EI rung label" in window or "executable implementation" in window.lower()
