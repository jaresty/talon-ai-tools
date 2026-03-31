"""Test for conflicts in groundPrompt.py identified by bar orbit/clash analysis.

These tests verify that conflicting instructions are resolved:
1. P18 mentions write_authorized but it was removed
2. P13 vs impl_intent consistency on test evidence
3. v_complete and impl_intent working together
4. impl_intent should reference rung table for artifact type
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import (
    GROUND_PARTS_MINIMAL,
    _SENTINEL_GATES,
    SENTINEL_TEMPLATES,
    build_ground_prompt,
)


def test_p18_no_longer_mentions_write_authorized():
    """P18 should not mention write_authorized since we replaced it with impl_intent."""
    prompt = build_ground_prompt()

    # P18 section should not mention write_authorized or Write authorized
    # Find P18 section (either "P18 (" or "Write authorization")
    p18_idx = prompt.lower().find("p18 (")
    if p18_idx == -1:
        p18_idx = prompt.lower().find("write authorization")

    # Find P19 to get end of P18 section
    p19_idx = prompt.lower().find("p19 (")
    if p19_idx == -1:
        p19_idx = len(prompt)

    p18_section = prompt[p18_idx:p19_idx]
    assert "write authorized" not in p18_section.lower(), (
        f"P18 should not mention Write authorized - it was replaced by impl_intent. Found: {p18_section[:200]}"
    )


def test_impl_intent_distinguishes_from_p13_observation():
    """impl_intent should clearly distinguish test validation from P13 behavioral observation.

    P13: observation of running behavior (invoking system directly)
    impl_intent: test validation evidence (running test file)
    These should be clearly distinguished in the gate text.
    """
    impl_intent_gate = _SENTINEL_GATES.get("impl_intent", "")

    # impl_intent should mention validation file to distinguish from P13 observation
    assert "validation file" in impl_intent_gate.lower(), (
        "impl_intent should specify validation file to distinguish from P13 behavioral observation"
    )


def test_v_complete_and_impl_intent_both_require_tool_calls():
    """v_complete and impl_intent should both require tool calls before their sentinels."""
    v_complete_gate = _SENTINEL_GATES.get("v_complete", "")
    impl_intent_gate = _SENTINEL_GATES.get("impl_intent", "")

    # Both should require preceding tool calls
    assert "tool call" in v_complete_gate.lower(), (
        "v_complete gate should require tool call"
    )
    assert (
        "tool call" in impl_intent_gate.lower()
        or "file-write" in impl_intent_gate.lower()
    ), "impl_intent gate should require tool call or file-write"


def test_impl_intent_references_rung_table_for_artifact_type():
    """impl_intent should reference rung table as authority for artifact type determination.

    Just like the old write_authorized had: "cited artifact type must match the artifact type
    of the named file as determined by the rung table"
    """
    impl_intent_gate = _SENTINEL_GATES.get("impl_intent", "")

    # Should reference rung table as authority for artifact type matching
    # Need "rung table" specifically, not just "current rung"
    assert "rung table" in impl_intent_gate.lower(), (
        "impl_intent gate should reference rung table for artifact type authority"
    )


def test_v_complete_must_come_after_file_write():
    """v_complete must be emitted AFTER the file write tool call, not before.

    The issue is model emitting v_complete before writing the file.
    Gate should clearly require file write TOOL CALL before v_complete sentinel.
    """
    v_complete_gate = _SENTINEL_GATES.get("v_complete", "")

    # Gate should require tool call that WRITES the file, not just "file written"
    assert (
        "tool call" in v_complete_gate.lower() and "wrote" in v_complete_gate.lower()
    ), (
        "v_complete gate should require a tool call that writes the file before the sentinel"
    )


def test_impl_intent_required_regardless_of_v_complete():
    """impl_intent is required for every file edit, regardless of v_complete.

    v_complete marks the rung complete, but impl_intent is still required
    for each file edit. These are separate requirements.
    """
    impl_intent_gate = _SENTINEL_GATES.get("impl_intent", "")

    # impl_intent should be required for every file write, period
    assert "every file-write" in impl_intent_gate.lower(), (
        "impl_intent should be required for every file-write, regardless of other sentinels"
    )


def test_file_edit_discipline_principle_early():
    """There should be a principle about file edit discipline early in the protocol (within P1-P6).

    File edit discipline is fundamental - it should appear early, not buried in later principles.
    In collapsed P1-P6, P4 covers file edit protocol.
    """
    core = GROUND_PARTS_MINIMAL["core"]

    # P4 covers file edit discipline
    p4_pos = core.lower().find("p4")
    p6_pos = core.lower().find("p6")

    # Should have P4 for file edit discipline
    assert p4_pos != -1, "Should have P4 principle for file edit discipline"

    # P4 should come before P6
    assert p4_pos < p6_pos, "P4 (file edit protocol) should come before P6"
