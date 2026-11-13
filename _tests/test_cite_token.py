import json
import re
import unittest
from pathlib import Path

from lib.axisConfig import (
    AXIS_KEY_TO_VALUE,
    axis_token_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["method"].get("cite", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["method"].get("cite", "")


def _distinction_note(token: str, other: str) -> str:
    for entry in axis_token_metadata()["method"][token]["distinctions"]:
        if entry["token"] == other:
            return entry["note"]
    return ""


class CiteMethodTokenTests(unittest.TestCase):
    """cite: each claim about what others hold carries a locatable citation."""

    def test_definition_opens_with_the_response(self):
        self.assertTrue(_definition().startswith("The response"))

    def test_definition_ends_each_such_sentence_with_a_citation(self):
        self.assertIn(
            "ending each sentence that states what others hold, do, or have found with a citation",
            _definition(),
        )

    def test_definition_requires_the_source_and_where_it_can_be_found(self):
        self.assertIn("naming the source and where it can be found", _definition())

    def test_definition_requires_the_sources_own_words_when_quoting(self):
        self.assertIn(
            "quoting the source's own words whenever words are attributed to it",
            _definition(),
        )

    def test_definition_limits_the_evidence_base_description(self):
        d = _definition()
        self.assertIn("describing the evidence base", d)
        self.assertIn("only as the cited sources show", d)

    def test_definition_names_no_other_token_or_subject_domain(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in ("objectivity", "pin", "verify"):
            self.assertIsNone(re.search(rf"\b{other}\b", d), other)
        for domain in ("code", "software", "library", "framework", "react"):
            self.assertIsNone(re.search(rf"\b{domain}\b", d), domain)

    def test_cite_and_objectivity_name_each_other_without_claiming_redundancy(self):
        for token, other in (("cite", "objectivity"), ("objectivity", "cite")):
            with self.subTest(token=token):
                note = _distinction_note(token, other)
                self.assertTrue(note, f"{token} must distinguish itself from {other}")
                self.assertNotIn("adds nothing", note)
                self.assertNotIn("redundant", note)

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))


if __name__ == "__main__":
    unittest.main()
