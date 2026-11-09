import unittest

TOPOLOGY = ("audit", "blind", "live", "relay", "solo", "witness")

# The literal text each definition must keep: the observable the token requires.
ANCHORS = {
    "audit": ("before stating", "evidence or premise"),
    "blind": ("assumption block", "by label"),
    "live": ("observation line", "within the same paragraph"),
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

    def test_each_definition_keeps_its_observable_anchors(self) -> None:
        """Removing the closing sentence leaves every required artifact in the text."""

        defs = _definitions()
        for token, anchors in ANCHORS.items():
            for anchor in anchors:
                with self.subTest(token=token, anchor=anchor):
                    self.assertIn(anchor, defs[token])


if __name__ == "__main__":
    unittest.main()
