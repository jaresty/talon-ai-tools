import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    # Fragments that name another scope token's domain. A scope description states
    # what its own token focuses on; boundaries with siblings live in distinctions.
    FORBIDDEN_FRAGMENTS = {
        "act": ["suppressing", "perspective-shifting"],
        "authority": ["impersonal structure", "equilibrium dynamics"],
        "cross": ["without primarily analyzing", "recurring structural form"],
        "fail": ["overall quality", "preferred outcomes"],
        "good": ["rather than defining one", "shifting perspective"],
        "mean": [
            "stakeholder perspective",
            "judging quality",
            "prescribing action",
            "required premises",
            "prior to evaluation",
        ],
        "motifs": ["without analyzing their internal topology", "boundary-spanning"],
        "relations": ["rather than the entities themselves", "Entity properties"],
        "struct": ["without emphasizing repetition", "boundary-spanning propagation"],
        "thing": ["without emphasizing", "evaluation, or perspective"],
        "time": ["rather than static structure", "immediate action"],
        "view": ["stakeholder", "evaluating outcomes", "prescribing action"],
    }

    # The token's own focus must survive the removal.
    OWN_FOCUS_ANCHORS = {
        "act": "work to be performed",
        "authority": "how their choices influence results",
        "cross": "become distributed across partitions",
        "fail": "failure modes",
        "good": "assuming a framing for what counts as success",
        "mean": "theoretical role",
        "motifs": "isomorphic patterns",
        "relations": "primary object of study",
        "struct": "internal topology of units",
        "thing": "and what is excluded",
        "time": "temporal dynamics",
        "view": "making that viewpoint explicit",
    }

    # Boundaries that used to live inside descriptions. Each pair must be present
    # in both directions so a chooser starting from either token sees it.
    MOVED_BOUNDARIES = [
        ("act", "mean"),
        ("act", "good"),
        ("act", "struct"),
        ("act", "view"),
        ("mean", "assume"),
        ("mean", "view"),
        ("thing", "relations"),
        ("thing", "good"),
        ("thing", "view"),
        ("time", "struct"),
        ("time", "good"),
        ("time", "act"),
        ("view", "good"),
        ("authority", "struct"),
        ("authority", "stable"),
        ("struct", "motifs"),
    ]

    class ScopeDescriptionsStateOwnDomainTests(unittest.TestCase):
        def test_descriptions_do_not_name_a_sibling_domain(self) -> None:
            from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

            scope = AXIS_KEY_TO_VALUE["scope"]
            for token, fragments in FORBIDDEN_FRAGMENTS.items():
                for fragment in fragments:
                    with self.subTest(token=token, fragment=fragment):
                        self.assertNotIn(fragment, scope[token])

        def test_descriptions_keep_their_own_focus(self) -> None:
            from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

            scope = AXIS_KEY_TO_VALUE["scope"]
            for token, anchor in OWN_FOCUS_ANCHORS.items():
                with self.subTest(token=token):
                    self.assertIn(anchor, scope[token])

        def test_view_label_is_positional_not_stakeholder(self) -> None:
            from talon_user.lib.axisConfig import AXIS_KEY_TO_LABEL

            self.assertEqual(AXIS_KEY_TO_LABEL["scope"]["view"], "Positional perspective")

        def test_moved_boundaries_exist_in_both_directions(self) -> None:
            from talon_user.lib.axisConfig import AXIS_TOKEN_METADATA

            scope = AXIS_TOKEN_METADATA["scope"]
            for a, b in MOVED_BOUNDARIES:
                for src, dst in ((a, b), (b, a)):
                    with self.subTest(src=src, dst=dst):
                        entries = {
                            d["token"]: d["note"]
                            for d in scope[src].get("distinctions", [])
                        }
                        self.assertIn(dst, entries)
                        note = entries[dst]
                        self.assertIn(f"{src} = ", note)
                        self.assertIn(f"; {dst} = ", note)
