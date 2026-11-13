import json
import re
import unittest
from pathlib import Path

from lib.axisConfig import (
    AXIS_KEY_TO_CATEGORY,
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
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
RECIPROCAL_AXIS = {"norm": "method", "mirror": "completeness", "winnow": "method"}
RECIPROCAL_TOKENS = tuple(RECIPROCAL_AXIS)
OTHER_TOKENS = ("norm", "mirror", "winnow", "induce", "falsify", "diff", "gap")


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["method"].get("earn", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["method"].get("earn", "")


class EarnMethodTokenTests(unittest.TestCase):
    """earn: classify each difference from a reference as warranted or unwarranted."""

    def test_earn_registered_on_every_method_table(self):
        for table in (
            AXIS_KEY_TO_VALUE,
            AXIS_KEY_TO_LABEL,
            AXIS_KEY_TO_KANJI,
            AXIS_KEY_TO_CATEGORY,
            AXIS_KEY_TO_ROUTING_CONCEPT,
        ):
            self.assertIn("earn", table["method"])

    def test_definition_opens_with_the_response(self):
        self.assertTrue(_definition().startswith("The response"))

    def test_definition_separates_subject_reason_from_classification(self):
        d = _definition()
        self.assertIn("'Difference: <what differs>'", d)
        self.assertIn("'Subject's reason:", d)
        self.assertIn("'none stated'", d)
        self.assertIn("'Classification: <warranted or unwarranted>", d)
        self.assertNotIn("Reason: <why the reference does not serve the purpose here>", d)

    def test_definition_classifies_warranted_or_unwarranted(self):
        d = _definition()
        self.assertIn("warranted when", d)
        self.assertIn("unwarranted when", d)
        self.assertIn("Unwarranted differences: <count>", d)

    def test_definition_names_no_other_token_or_subject_domain(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in OTHER_TOKENS:
            self.assertIsNone(re.search(rf"\b{other}\b", d), other)
        for domain in ("code", "software", "library", "framework", "react"):
            self.assertIsNone(re.search(rf"\b{domain}\b", d), domain)

    def test_metadata_has_heuristics_and_distinctions(self):
        meta = axis_token_metadata()["method"].get("earn", {})
        self.assertTrue(meta.get("heuristics"))
        distinct = {d["token"] for d in meta.get("distinctions", [])}
        self.assertTrue(set(RECIPROCAL_TOKENS) <= distinct)

    def test_each_neighbour_names_earn_in_its_distinctions(self):
        for token in RECIPROCAL_TOKENS:
            with self.subTest(token=token):
                axis = RECIPROCAL_AXIS[token]
                distinct = {
                    d["token"]
                    for d in axis_token_metadata()[axis][token]["distinctions"]
                }
                self.assertIn("earn", distinct)

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))

    def test_norm_description_is_unchanged(self):
        d = AXIS_KEY_TO_VALUE["method"]["norm"]
        self.assertTrue(
            d.startswith(
                "The response names the purpose the subject serves and the established practice"
            )
        )
        self.assertTrue(d.endswith("'Unwarranted departures: <count>'."))


if __name__ == "__main__":
    unittest.main()
