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
        "listed before any frame is applied",
        "enumerating N named cognitive frames",
        "numbered list of the shared facts of the subject",
        "'Construal:' followed by a sentence whose grammatical subject is the subject's own noun phrase",
        "'Presupposes:' naming the roles present under that frame, what each expects, and what normally happens next",
        "'Reads fact K:'",
        "reads it differently from every other frame's",
        "one headed output block per frame, N in total",
    ),
    ("channel", "zettel"): (
        "Each note body must contain exactly one claim",
        "each constituent claim becomes its own note, and one entry note carries the cross-cutting part",
        "(2) the returned ID must appear as the literal argument to the next command;",
        "nn bulk-link: skipped",
        "(5) run `nn bulk-link` once more with the entry note's ID and every claim note's ID as literal arguments",
    ),
    ("method", "shoshin"): (
        "emits no invocations and is compliant",
        "any delegation tool-use block must appear at a later transcript position than the disposition lines it enforces",
        "Every item entering an isolated context",
        "A response in which a point meets the trigger emits an invocation whose disposition lines establish that its frame set was chosen rather than inherited.",
    ),
    ("method", "falsify"): (
        "'Overreach: not found' is a claim that no such reduction exists, so it is valid only after an attempted reduction",
        "completeness is read from the matching of each enumerated Assertion line to its outcome line",
        "coverage is complete exactly when every enumerated Assertion line has a matching outcome line",
        "a verdict is valid only when it cites a qualifying result record",
        "Gate 1 ends with an 'Overreach: found — <modification or path>', 'Overreach: not found', or 'Overreach: untested — observation unavailable' line, which appears in the transcript before 'Coverage:'.",
        "an assertion carrying an 'Unwitnessed: assertion \"<verbatim assertion>\" — observation unavailable' line is open and takes 'Coverage: incomplete — observation unavailable'",
    ),
    ("method", "mark"): (
        "## Step N",
        "Governing:",
        "each satisfied by their own named artifacts",
    ),
}


# Where a prohibition carried measured behavior that no affirmative wording reproduced, one
# "does not satisfy" sentence may be kept on purpose: (axis, token) -> allowed occurrences.
# Empty now: prism's was the one case, and it was removed once a wording that names a
# transcript-observable (sentence openings) reproduced it (ADR-0241).
ALLOWED_DENY_SENTENCES = {}


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


    def test_prism_frames_are_cognitive_frames_with_observable_lines(self) -> None:
        """prism: a frame construes the subject, brings unstated background, and reads shared facts its own way."""

        text = _definition("method", "prism")
        self.assertIn(
            "a cognitive frame is a way of construing the subject that fixes what it is taken to be, what unstated background it brings, and how the same facts read under it",
            text,
        )
        self.assertIn("one 'Reads fact K:' line per shared fact K", text)
        self.assertNotIn("naming the background the frame supplies without it being stated", text)
        self.assertNotIn("Foregrounds", text)
        self.assertNotIn("opens with a noun phrase", text)
        self.assertNotIn("does not satisfy", text)

    def test_redact_placeholders_are_optional(self) -> None:
        """redact states placeholder markers as optional, not as 'no ... required'."""

        text = _definition("method", "redact")
        self.assertIn("placeholder markers are optional", text)
        self.assertNotIn("no placeholder markers are required", text)


if __name__ == "__main__":
    unittest.main()
