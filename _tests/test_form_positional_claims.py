"""Form definitions scope positional claims to their own structure.

A form describes the structure of the answer's content. A claim about where
something sits in the whole response ("ends with", "opens with", "no text
outside") collides with sections the surrounding prompt adds after the answer,
so each such claim must name the form's own structure as its subject.

Each row is (token, phrase that scopes the claim, phrase that claimed the whole
response). The scoped phrase must be present and the whole-response phrase
absent. Every row must FAIL before its definition is amended and PASS after.

Deliberately not covered: ``template``, a documented whole-response form, and
``direct`` / ``indirect``, which order ideas rather than position output.
"""

import unittest

from lib.axisConfig import AXIS_KEY_TO_VALUE

_ROWS = (
    (
        "storyboard",
        "The storyboard contains no text outside the panel sequence",
        "No text appears outside the panel sequence",
    ),
    (
        "runbook",
        "The procedure opens with 'Operator:",
        "It opens with 'Operator:",
    ),
    (
        "socratic",
        "The questions contain no declarative sentence",
        "This response contains no declarative sentence",
    ),
    (
        "socratic",
        "The questioning ends with an explicit invitation",
        "The response ends with an explicit invitation",
    ),
    (
        "interactive",
        "and its interactive content ends with a prompt",
        "and ends with a prompt",
    ),
    (
        "quiz",
        "the quiz begins with a literal \"Quiz purpose:\" line",
        "the response begins with a literal \"Quiz purpose:\" line",
    ),
    (
        "quiz",
        "then close the quiz with a terminal declaration",
        "then close with a terminal declaration",
    ),
)


class FormPositionalClaimsScopedTests(unittest.TestCase):
    """property [9]"""

    def test_positional_claims_name_the_forms_own_structure(self):
        for token, scoped, whole_response in _ROWS:
            with self.subTest(token=token, scoped=scoped):
                definition = AXIS_KEY_TO_VALUE["form"].get(token, "")
                self.assertIn(scoped, definition)
                self.assertNotIn(whole_response, definition)


if __name__ == "__main__":
    unittest.main()
