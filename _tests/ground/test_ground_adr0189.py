"""Tests for ADR-0189: D1 predicate closure + artifact type taxonomy."""

from lib.groundPrompt import build_ground_prompt, RUNG_SEQUENCE


def _p() -> str:
    return build_ground_prompt()


# ── Thread 1: D1 predicate closure ────────────────────────────────────────────

def test_d1_structural_definition_present():
    # D1 closure: "or similar" replaced by a structural definition of the category.
    assert "any finite verb where the subject is the system" in _p()


def test_d1_or_similar_absent():
    # The vague "or similar" is replaced by the principled structural definition.
    assert "or similar" not in _p()


def test_d1_existing_verbs_present():
    p = _p()
    for verb in ["fetches", "renders", "validates", "authenticates", "loads", "saves"]:
        assert verb in p, f"existing verb '{verb}' must remain in closed list"


# ── Thread 2: artifact type taxonomy ──────────────────────────────────────────

def test_type_taxonomy_rung_sequence_has_type_label():
    for rung in RUNG_SEQUENCE:
        assert "type_label" in rung, f"rung '{rung['name']}' must have a type_label field"


def test_type_taxonomy_labels_are_unique():
    labels = [r["type_label"] for r in RUNG_SEQUENCE]
    assert len(labels) == len(set(labels)), "each rung must have a unique type_label"


def test_type_taxonomy_section_in_prompt():
    # ADR-0214: "Artifact type classification" header removed; type definitions folded into rung table
    # and OBR sequence section. The header itself was derivable boilerplate.
    assert "Artifact type classification" not in _p(), \
        "ADR-0214: taxonomy header must be absent; type definitions now in rung table"


def test_type_taxonomy_all_labels_named_in_prompt():
    p = _p()
    for rung in RUNG_SEQUENCE:
        assert rung["type_label"] in p, f"type_label '{rung['type_label']}' must appear in prompt"
