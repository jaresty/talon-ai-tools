import unittest

TOPOLOGY = ("audit", "blind", "live", "relay", "solo", "witness")

# The literal text each definition must keep: the observable the token requires.
ANCHORS = {
    "audit": ("before stating", "evidence or premise"),
    "blind": ("assumption block", "by label"),
    "live": ("observation line", "within that paragraph"),
    "relay": ("each named before", "schemas"),
    "solo": ("Required because", "opening sentence"),
    "witness": ("epistemic basis", "before stating any conclusion"),
}


def _definitions():
    from lib.axisConfig import AXIS_KEY_TO_VALUE

    return AXIS_KEY_TO_VALUE["topology"]


class TopologyDefinitionTests(unittest.TestCase):
    def test_no_definition_ends_in_a_deny_list_sentence(self) -> None:
        """Each topology definition states what the output contains, not what fails."""

        defs = _definitions()
        offenders = [t for t in TOPOLOGY if "does not satisfy" in defs[t]]
        self.assertEqual(offenders, [], f"deny-list closers remain in: {offenders}")

    def test_solo_states_its_requirement_affirmatively(self) -> None:
        """solo requires each included step to carry its dependency label; it does not ration steps."""

        text = _definitions()["solo"]
        self.assertNotIn("only when", text)
        self.assertTrue(text.startswith("The response names, in the opening sentence of each intermediate step it includes,"))

    def test_live_places_the_observation_inside_the_paragraph(self) -> None:
        """live puts the observation inside the paragraph, before or alongside the content."""

        text = _definitions()["live"]
        self.assertNotIn("precedes or accompanies", text)
        self.assertIn("before or alongside the task-advancing content", text)

    def test_solo_names_no_other_token(self) -> None:
        """A definition states its own requirement; it does not name a sibling token."""

        text = _definitions()["solo"]
        self.assertNotIn("completeness token", text)
        self.assertIn("Depth of coverage is set independently", text)

    def test_relay_requires_a_label_per_category(self) -> None:
        """relay's five categories each appear under their own label, so presence is checkable."""

        self.assertIn("each appear under their own label", _definitions()["relay"])


    def test_each_definition_keeps_its_observable_anchors(self) -> None:
        """Removing the closing sentence leaves every required artifact in the text."""

        defs = _definitions()
        for token, anchors in ANCHORS.items():
            for anchor in anchors:
                with self.subTest(token=token, anchor=anchor):
                    self.assertIn(anchor, defs[token])


if __name__ == "__main__":
    unittest.main()
