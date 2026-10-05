"""
Falsifiable tests for the 'as insider' voice token definition.

as insider: constrains the response's word choice to the terms of art established
in the subject's own field, resolving which field from the subject at render time
rather than naming any field in the definition.

Tests FAIL before 'as insider' is added to personaConfig.py; PASS after.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.personaConfig import (
    PERSONA_KEY_TO_VALUE,
    PERSONA_KEY_TO_LABEL,
    PERSONA_KEY_TO_ROUTING_CONCEPT,
    PERSONA_KEY_TO_KANJI,
    PERSONA_TOKEN_METADATA,
)

TOKEN = "as insider"

INSIDER_DEF = PERSONA_KEY_TO_VALUE.get("voice", {}).get(TOKEN, "")
INSIDER_META = PERSONA_TOKEN_METADATA.get("voice", {}).get(TOKEN, {})
INSIDER_META_DEF = INSIDER_META.get("definition", "")


# property [1]: the token is defined at every site the lookup commands read.

def test_insider_present_in_all_five_maps():
    missing = [
        name
        for name, mapping in (
            ("PERSONA_KEY_TO_VALUE", PERSONA_KEY_TO_VALUE),
            ("PERSONA_KEY_TO_LABEL", PERSONA_KEY_TO_LABEL),
            ("PERSONA_KEY_TO_ROUTING_CONCEPT", PERSONA_KEY_TO_ROUTING_CONCEPT),
            ("PERSONA_KEY_TO_KANJI", PERSONA_KEY_TO_KANJI),
            ("PERSONA_TOKEN_METADATA", PERSONA_TOKEN_METADATA),
        )
        if TOKEN not in mapping.get("voice", {})
    ]
    assert not missing, (
        f"'{TOKEN}' must be present in the voice axis of every persona map; "
        f"missing from: {', '.join(missing)}"
    )


def test_insider_metadata_has_definition_and_heuristics():
    assert INSIDER_META_DEF, f"'{TOKEN}' metadata must carry a definition"
    assert INSIDER_META.get("heuristics"), (
        f"'{TOKEN}' metadata must carry heuristics so bar lookup can reach it"
    )


# property [3]: the field referent is resolved from the subject at render time,
# which requires an emitted naming string -- otherwise nothing in the transcript
# distinguishes resolution from a generic register default.

def test_insider_requires_emitting_the_resolved_terms():
    text = INSIDER_META_DEF.lower()
    assert "write" in text or "name" in text or "list" in text, (
        f"'{TOKEN}' definition must instruct the response to emit the resolved "
        "terms; without an emitted naming string, compliance is unaddressable"
    )


def test_insider_resolves_referent_from_the_subject():
    text = INSIDER_META_DEF.lower()
    assert "subject" in text, (
        f"'{TOKEN}' definition must resolve its referent from the subject, "
        "the way 'as wild' does, rather than from a fixed name"
    )


# property [2]: the definition is domain-agnostic (protocol 20260716164822-9216).
# A definition naming a specific field would restrict the subjects the token
# composes with, because the definition is the instruction being carried out.

def test_insider_definition_names_no_specific_domain():
    assert INSIDER_META_DEF, (
        f"'{TOKEN}' must have a definition before it can be checked for "
        "domain-agnosticism; an empty definition is vacuously agnostic"
    )
    text = INSIDER_META_DEF.lower()
    named_domains = [
        "software", "engineering", "medical", "medicine", "legal", "law",
        "finance", "financial", "scientific", "academic", "technical",
        "programming", "code", "business",
    ]
    found = [d for d in named_domains if d in text]
    assert not found, (
        f"'{TOKEN}' definition must name no specific domain "
        f"(protocol 20260716164822-9216); found: {', '.join(found)}"
    )


def test_insider_definition_is_not_a_simplification_instruction():
    assert INSIDER_META_DEF, (
        f"'{TOKEN}' must have a definition before its direction can be checked"
    )
    text = INSIDER_META_DEF.lower()
    # A simplification instruction makes the everyday register the target. This
    # token makes it the thing displaced, so an everyday-register phrase is only
    # admissible as the object of a displacing construction.
    displacing = ("in place of", "instead of", "rather than", "not the")
    for phrase in ("plain language", "simple words", "avoid jargon", "everyday"):
        if phrase not in text:
            continue
        before = text.split(phrase)[0]
        assert any(d in before for d in displacing), (
            f"'{TOKEN}' constrains word choice toward the field's terms; "
            f"'{phrase}' appears without a preceding displacing construction, "
            "so it reads as the target register rather than the displaced one"
        )


# property [6]: distinguished from the vocabulary-adjacent voice tokens, so the
# orthogonality boundary is checkable (protocol 20260715194839-8169).

def test_insider_distinguished_from_vocabulary_neighbours():
    required = {"as plainspeak", "as technical writer", "as wild"}
    present = {d.get("token") for d in INSIDER_META.get("distinctions", [])}
    missing = required - present
    assert not missing, (
        f"'{TOKEN}' must carry a distinction against each vocabulary-adjacent "
        f"voice token; missing: {', '.join(sorted(missing))}"
    )


def test_insider_distinction_notes_are_nonempty():
    distinctions = INSIDER_META.get("distinctions", [])
    assert distinctions, (
        f"'{TOKEN}' must carry distinctions before their notes can be checked; "
        "an empty list has vacuously non-empty notes"
    )
    for d in distinctions:
        assert d.get("note"), (
            f"'{TOKEN}' distinction against '{d.get('token')}' must carry a note"
        )
