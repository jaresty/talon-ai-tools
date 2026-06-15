import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_topology_definitions_exist():
    assert "topology" in AXIS_KEY_TO_VALUE
    tokens = AXIS_KEY_TO_VALUE["topology"]
    assert set(tokens.keys()) == {"witness", "audit", "blind", "relay", "solo", "live"}


def test_solo_definition_is_epistemic_stance_only():
    solo_def = AXIS_KEY_TO_VALUE["topology"]["solo"]
    assert "compression" not in solo_def.lower(), (
        f"solo definition contains 'compression' — solo must describe epistemic stance only, "
        f"not output depth or compression: {solo_def!r}"
    )
    assert "synthesis efficiency" not in solo_def.lower(), (
        f"solo definition contains 'synthesis efficiency' — solo must describe epistemic stance only: {solo_def!r}"
    )
    assert "intermediate step" in solo_def.lower() or "reasoning state" in solo_def.lower() or "unobserved" in solo_def.lower(), (
        f"solo definition must describe what intermediate steps or reasoning state is externalized: {solo_def!r}"
    )


def test_audit_structural_unit_and_artifact():
    audit_def = AXIS_KEY_TO_VALUE["topology"]["audit"]
    assert "paragraph or step" in audit_def, (
        f"audit definition must name the structural unit 'paragraph or step': {audit_def!r}"
    )
    assert "before stating any conclusion" in audit_def, (
        f"audit definition must name the ordering constraint (before stating any conclusion): {audit_def!r}"
    )


def test_blind_assumption_block_and_label():
    blind_def = AXIS_KEY_TO_VALUE["topology"]["blind"]
    assert "assumption block" in blind_def, (
        f"blind definition must name the structural form 'assumption block': {blind_def!r}"
    )
    assert "names the specific assumption block it draws from, by label" in blind_def, (
        f"blind definition must require conclusions to name the assumption block by label: {blind_def!r}"
    )


def test_live_observation_line_and_label():
    live_def = AXIS_KEY_TO_VALUE["topology"]["live"]
    assert "observation line" in live_def, (
        f"live definition must name the structural form 'observation line': {live_def!r}"
    )
    assert "sentence beginning with a label such as" in live_def, (
        f"live definition must name the label form (e.g. Noticing:): {live_def!r}"
    )


def test_relay_named_before_section():
    relay_def = AXIS_KEY_TO_VALUE["topology"]["relay"]
    assert "each named before the section that depends on them" in relay_def, (
        f"relay definition must require items to be named before the section that depends on them: {relay_def!r}"
    )


def test_solo_dependency_label_form():
    solo_def = AXIS_KEY_TO_VALUE["topology"]["solo"]
    assert "Required because" in solo_def, (
        f"solo definition must include the dependency label form 'Required because': {solo_def!r}"
    )


def test_witness_structural_unit_and_basis():
    witness_def = AXIS_KEY_TO_VALUE["topology"]["witness"]
    assert "paragraph or numbered step" in witness_def, (
        f"witness definition must name the structural unit 'paragraph or numbered step': {witness_def!r}"
    )
    assert "causal or epistemic basis for that assumption" in witness_def, (
        f"witness definition must require naming the causal or epistemic basis: {witness_def!r}"
    )


def test_topology_definitions_no_intent_qualifiers():
    intent_qualifiers = {"important", "major", "key", "sufficient", "essential", "structurally"}
    tokens = AXIS_KEY_TO_VALUE["topology"]
    for token, definition in tokens.items():
        words = set(definition.lower().split())
        found = intent_qualifiers & words
        assert not found, (
            f"topology/{token} contains intent-qualifier word(s) {found!r} "
            f"that require evaluator judgment to assess compliance"
        )
