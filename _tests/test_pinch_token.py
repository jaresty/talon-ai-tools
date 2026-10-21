import unittest

from lib.axisConfig import (
    AXIS_KEY_TO_CATEGORY,
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_VALUE,
    axis_token_metadata,
)


class PinchMethodTokenTests(unittest.TestCase):
    """pinch: a margin per constraint, then the binding one."""

    def _definition(self) -> str:
        return AXIS_KEY_TO_VALUE["method"]["pinch"]

    def test_pinch_registered_on_every_method_table(self):
        for table in (
            AXIS_KEY_TO_VALUE,
            AXIS_KEY_TO_LABEL,
            AXIS_KEY_TO_KANJI,
            AXIS_KEY_TO_CATEGORY,
            AXIS_KEY_TO_ROUTING_CONCEPT,
        ):
            self.assertIn("pinch", table["method"])

    def test_definition_opens_with_the_response(self):
        self.assertTrue(self._definition().startswith("The response"))

    def test_definition_requires_constraints_named_before_assessment(self):
        self.assertIn("before assessing any of them", self._definition())

    def test_definition_requires_margin_line_per_constraint(self):
        self.assertIn("Margin: <constraint>", self._definition())

    def test_definition_marks_unknown_margins_instead_of_ranking_them(self):
        d = self._definition()
        self.assertIn("Margin unknown: <constraint>", d)
        self.assertIn("is not ranked", d)

    def test_definition_names_the_binding_constraint(self):
        d = self._definition()
        self.assertIn("Binding: <constraint>", d)
        self.assertIn("Binding: none ranked", d)

    def test_definition_is_domain_agnostic_and_names_no_other_token(self):
        d = self._definition().lower()
        for other in ("operations", "lever", "boom", "release", "capacity", "latency"):
            self.assertNotIn(other, d)

    def test_metadata_has_distinctions_and_heuristics(self):
        meta = axis_token_metadata()["method"]["pinch"]
        self.assertTrue(meta["heuristics"])
        distinct = {d["token"] for d in meta["distinctions"]}
        self.assertTrue({"operations", "lever", "boom", "release"} <= distinct)


if __name__ == "__main__":
    unittest.main()
