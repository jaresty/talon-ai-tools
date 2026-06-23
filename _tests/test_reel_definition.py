import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import (
        AXIS_KEY_TO_VALUE,
        AXIS_KEY_TO_LABEL,
        AXIS_KEY_TO_ROUTING_CONCEPT,
        AXIS_TOKEN_METADATA,
    )

    def _defn() -> str:
        return AXIS_KEY_TO_VALUE.get("form", {}).get("reel", "")

    def _label() -> str:
        return AXIS_KEY_TO_LABEL.get("form", {}).get("reel", "")

    def _routing_concept() -> str:
        return AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {}).get("reel", "")

    def _heuristics() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("reel", {}).get("heuristics", [])

    def _distinctions() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("reel", {}).get("distinctions", [])

    def _distinction_tokens() -> list:
        return [d["token"] for d in _distinctions()]

    def _distinction_note(token: str) -> str:
        for d in _distinctions():
            if d["token"] == token:
                return d["note"]
        return ""

    class ReelDefinitionTests(unittest.TestCase):

        # --- key presence ---
        def test_reel_key_present(self) -> None:
            self.assertIn("reel", AXIS_KEY_TO_VALUE.get("form", {}))

        # --- root criterion phrases ---
        def test_reel_animated_scene_specification(self) -> None:
            self.assertIn("animated scene specification", _defn())

        def test_reel_scene_record_ordinal(self) -> None:
            self.assertIn("ordinal", _defn())

        def test_reel_scene_record_duration_format(self) -> None:
            self.assertIn("a number and time unit such as 2s or 400ms", _defn())

        def test_reel_narrative_label_final_field(self) -> None:
            self.assertIn("narrative label as the final field", _defn())

        def test_reel_motion_entry_element_identifier(self) -> None:
            self.assertIn("element identifier", _defn())

        def test_reel_motion_entry_states(self) -> None:
            self.assertIn("absent, entering, holding, or exiting", _defn())

        def test_reel_curve_token_entering_or_exiting(self) -> None:
            self.assertIn("when entering or exiting, a curve token", _defn())

        def test_reel_minimum_one_motion_entry_per_scene(self) -> None:
            self.assertIn("at least one motion entry", _defn())

        def test_reel_minimum_gate(self) -> None:
            self.assertIn("At least two scene records must be present", _defn())

        # --- label ---
        def test_reel_label_present(self) -> None:
            self.assertTrue(len(_label()) > 0)

        def test_reel_label_references_scene(self) -> None:
            self.assertIn("scene", _label().lower())

        def test_reel_label_references_motion(self) -> None:
            self.assertIn("motion", _label().lower())

        # --- routing concept ---
        def test_reel_routing_concept_present(self) -> None:
            self.assertTrue(len(_routing_concept()) > 0)

        def test_reel_routing_concept_references_animated(self) -> None:
            self.assertIn("animated", _routing_concept().lower())

        # --- heuristics ---
        def test_reel_heuristics_present(self) -> None:
            self.assertTrue(len(_heuristics()) >= 5)

        def test_reel_intro_heuristic(self) -> None:
            self.assertTrue(any("introduc" in h or "intro" in h for h in _heuristics()))

        def test_reel_animated_heuristic(self) -> None:
            self.assertTrue(any("animat" in h for h in _heuristics()))

        # --- distinctions ---
        def test_reel_slides_distinction_present(self) -> None:
            self.assertIn("slides", _distinction_tokens())

        def test_reel_stage_distinction_present(self) -> None:
            self.assertIn("stage", _distinction_tokens())

        def test_reel_timeline_distinction_present(self) -> None:
            self.assertIn("timeline", _distinction_tokens())

        def test_reel_slides_distinction_references_motion(self) -> None:
            note = _distinction_note("slides")
            self.assertTrue(
                "motion" in note or "timing" in note or "animat" in note,
                "slides distinction must reference motion or timing absence"
            )
