"""Definitions scope positional claims to their own output.

A token describes the structure of the answer's content. A claim about where
something sits in the whole response ("ends with", "opens with", "no text
outside", "closing lines") collides with sections the surrounding prompt adds
after the answer, so each such claim must name the token's own output as its
subject.

Each row is (axis, token, phrase that scopes the claim, phrase that claimed the
whole response). The scoped phrase must be present and the whole-response
phrase absent. Every row must FAIL before its definition is amended and PASS
after.

Deliberately not covered: ``template``, a documented whole-response form;
``direct`` / ``indirect``, which order ideas rather than position output; and
tokens whose positional claims already name a step or block (``solo``,
``chain``, ``gate``, ``blind``). Channels own the output format and are a
different layer.
"""

import unittest

from lib.axisConfig import AXIS_KEY_TO_VALUE

_FORM_ROWS = (
    (
        "form",
        "storyboard",
        "The storyboard contains no text outside the panel sequence",
        "No text appears outside the panel sequence",
    ),
    (
        "form",
        "runbook",
        "The procedure opens with 'Operator:",
        "It opens with 'Operator:",
    ),
    (
        "form",
        "socratic",
        "The questions contain no declarative sentence",
        "This response contains no declarative sentence",
    ),
    (
        "form",
        "socratic",
        "The questioning ends with an explicit invitation",
        "The response ends with an explicit invitation",
    ),
    (
        "form",
        "interactive",
        "and its interactive content ends with a prompt",
        "and ends with a prompt",
    ),
    (
        "form",
        "quiz",
        "the quiz begins with a literal \"Quiz purpose:\" line",
        "the response begins with a literal \"Quiz purpose:\" line",
    ),
    (
        "form",
        "quiz",
        "then close the quiz with a terminal declaration",
        "then close with a terminal declaration",
    ),
)

_CLOSING_ROWS = (
    (
        "completeness",
        "fixpoint",
        "the pass output ends 'Unprocessed: no finite inventory'",
        "the response ends 'Unprocessed: no finite inventory'",
    ),
    (
        "completeness",
        "fixpoint",
        "The last line of the pass output is 'Fixpoint reached",
        "The last line is 'Fixpoint reached",
    ),
    (
        "completeness",
        "mirror",
        "The comparison ends with 'Not checked:",
        "It ends with 'Not checked:",
    ),
    (
        "method",
        "eliminate",
        "The elimination closes with either 'exhaustive:'",
        "The response closes with either 'exhaustive:'",
    ),
    (
        "method",
        "lazy",
        "The final lines of the step sequence list each choice still pending",
        "The closing lines list each choice still pending",
    ),
    (
        "method",
        "norm",
        "The final line of the classification states 'Unwarranted departures:",
        "The closing line states 'Unwarranted departures:",
    ),
    (
        "method",
        "pilot",
        "The final lines of the step sequence state each result that changed the order",
        "The closing lines state each result that changed the order",
    ),
)


def _check(case: unittest.TestCase, rows) -> None:
    for axis, token, scoped, whole_response in rows:
        with case.subTest(axis=axis, token=token, scoped=scoped):
            definition = AXIS_KEY_TO_VALUE[axis].get(token, "")
            case.assertIn(scoped, definition)
            case.assertNotIn(whole_response, definition)


class FormPositionalClaimsScopedTests(unittest.TestCase):
    """property [9]"""

    def test_form_claims_name_the_forms_own_structure(self):
        _check(self, _FORM_ROWS)


class ClosingClaimsScopedTests(unittest.TestCase):
    """property [10]"""

    def test_closing_claims_name_the_tokens_own_output(self):
        _check(self, _CLOSING_ROWS)


if __name__ == "__main__":
    unittest.main()
