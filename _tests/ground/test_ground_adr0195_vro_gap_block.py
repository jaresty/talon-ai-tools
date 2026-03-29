from lib.groundPrompt import build_ground_prompt

def _p(): return build_ground_prompt()

def test_gap_may_not_be_emitted_after_vro_harness():
    p = _p()
    # ADR-0215: compact routing table blocks 🔴 Gap: for all harness error types
    assert "block \U0001f534 Gap:" in p or "\U0001f534 Gap: may not be emitted" in p

def test_ei_rung_label_only_after_vro_harness_missing_file():
    p = _p()
    # ADR-0215: compact routing table routes missing-implementation-file → EI directly
    idx = p.find("missing-implementation-file")
    assert idx != -1, "Compact routing table must name missing-implementation-file"
    window = p[idx:idx+100]
    assert "EI" in window, "missing-implementation-file must route to EI"
