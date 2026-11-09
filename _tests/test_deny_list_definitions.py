import unittest

# Definitions rewritten to state what the output contains, not what fails (ADR-0241).
# Each batch appends here: (axis, token) -> literal text the definition must keep.
CLEARED = {
    ("method", "own"): (
        "entirely private to the operator",
        "first creating a new artifact",
        "is accessible to others when a single transmission step could share it",
    ),
    ("method", "redact"): (
        "states each category of content being excluded",
        "absent from the rewritten output",
    ),
    ("method", "eliminate"): (
        "marks it surviving",
        "attempts to construct a defeater",
        "eliminated plus surviving equals N",
    ),
    ("scope", "jobs"): (
        "non-negotiable rather than merely convenient",
    ),
    ("form", "quiz"): (
        "A Predict: line satisfies the gate when it appears in a human message turn.",
        "Quiz purpose:",
        "Stopping condition:",
    ),
    ("method", "gate"): (
        "Gate condition:",
        "qualifying prior-executed result",
        "each governed action requires its own gate condition block.",
    ),
    ("method", "prism"): (
        "named before any frame is applied",
        "single structural vantage point",
        "a frame body that enumerates alternative approaches, methods, or investigation paths does not satisfy this requirement",
        "one headed output block per frame, N in total",
    ),
    ("method", "mark"): (
        "## Step N",
        "Governing:",
        "each satisfied by their own named artifacts",
    ),
}


# Where a prohibition carried measured behavior that no affirmative wording reproduced, one
# "does not satisfy" sentence is kept on purpose: (axis, token) -> allowed occurrences.
# prism: frame bodies that list approaches (3 rewordings, 5 runs, all lists; original 2 runs, none).
ALLOWED_DENY_SENTENCES = {("method", "prism"): 1}


def _definition(axis, token):
    from lib.axisConfig import AXIS_KEY_TO_VALUE

    return AXIS_KEY_TO_VALUE[axis][token]


class ClearedDefinitionTests(unittest.TestCase):
    def test_no_cleared_definition_contains_a_deny_list_sentence(self) -> None:
        """A cleared definition states what the response contains; it has no does-not-satisfy sentence."""

        offenders = [
            k
            for k in CLEARED
            if _definition(*k).count("does not satisfy") > ALLOWED_DENY_SENTENCES.get(k, 0)
        ]
        self.assertEqual(offenders, [], f"deny-list sentences remain in: {offenders}")

    def test_each_cleared_definition_keeps_its_anchors(self) -> None:
        """Rewriting keeps the literal text each token's requirement rests on."""

        for key, anchors in CLEARED.items():
            for anchor in anchors:
                with self.subTest(token=key, anchor=anchor):
                    self.assertIn(anchor, _definition(*key))

    def test_each_cleared_definition_opens_with_the_response(self) -> None:
        """The catalog convention: every definition starts 'The response'."""

        for key in CLEARED:
            with self.subTest(token=key):
                self.assertTrue(_definition(*key).startswith("The response"))

    def test_own_states_privacy_affirmatively(self) -> None:
        """own requires every effect to land on private artifacts, not merely forbids shared ones."""

        text = _definition("method", "own")
        self.assertTrue(text.startswith("The response contains only"))
        self.assertIn("An artifact is accessible to others when a single transmission step could share it.", text)

    def test_jobs_names_no_sibling_scope_domain(self) -> None:
        """jobs states its own focus; product features are a sibling scope's domain (distinctions hold the boundary)."""

        text = _definition("scope", "jobs")
        self.assertNotIn("specific product", text)

    def test_quiz_states_the_predict_source_as_a_test(self) -> None:
        """quiz says a satisfying Predict: line appears in a human message turn."""

        text = _definition("form", "quiz")
        self.assertIn("A Predict: line satisfies the gate when it appears in a human message turn.", text)
        self.assertIn("The answer appears in the response turn after a human message containing a Predict: line.", text)


    def test_prism_states_frames_as_one_vantage_point_each(self) -> None:
        """prism keeps the one prohibition that measurably stops frame bodies from listing approaches."""

        text = _definition("method", "prism")
        self.assertIn(
            "a frame body that enumerates alternative approaches, methods, or investigation paths does not satisfy this requirement",
            text,
        )
        self.assertEqual(text.count("does not satisfy"), 1)


    def test_redact_placeholders_are_optional(self) -> None:
        """redact states placeholder markers as optional, not as 'no ... required'."""

        text = _definition("method", "redact")
        self.assertIn("placeholder markers are optional", text)
        self.assertNotIn("no placeholder markers are required", text)


if __name__ == "__main__":
    unittest.main()
