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
        return AXIS_KEY_TO_VALUE.get("form", {}).get("tween", "")

    def _label() -> str:
        return AXIS_KEY_TO_LABEL.get("form", {}).get("tween", "")

    def _routing_concept() -> str:
        return AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {}).get("tween", "")

    def _heuristics() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("tween", {}).get("heuristics", [])

    def _distinctions() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("tween", {}).get("distinctions", [])

    def _distinction_tokens() -> list:
        return [d["token"] for d in _distinctions()]

    def _distinction_note(token: str) -> str:
        for d in _distinctions():
            if d["token"] == token:
                return d["note"]
        return ""

    class TweenDefinitionTests(unittest.TestCase):

        # --- key presence ---
        def test_tween_key_present(self) -> None:
            self.assertIn("tween", AXIS_KEY_TO_VALUE.get("form", {}))

        # --- root criterion phrases ---
        def test_tween_animation_specification(self) -> None:
            self.assertIn("animation specification", _defn())

        def test_tween_progress_position_clause(self) -> None:
            self.assertIn("progress position", _defn())

        def test_tween_percentage_or_named_waypoint(self) -> None:
            self.assertIn("percentage or named waypoint", _defn())

        def test_tween_property_and_value(self) -> None:
            self.assertIn("a property, and its value", _defn())

        def test_tween_curve_token_clause(self) -> None:
            self.assertIn("curve token", _defn())

        def test_tween_curve_token_word_or_hyphenated(self) -> None:
            self.assertIn("word or hyphenated phrase", _defn())

        def test_tween_minimum_gate(self) -> None:
            self.assertIn("At least two keyframes and one curve token", _defn())

        # --- label ---
        def test_tween_label_present(self) -> None:
            self.assertTrue(len(_label()) > 0)

        def test_tween_label_references_keyframe(self) -> None:
            self.assertIn("keyframe", _label().lower())

        # --- routing concept ---
        def test_tween_routing_concept_present(self) -> None:
            self.assertTrue(len(_routing_concept()) > 0)

        def test_tween_routing_concept_references_animation(self) -> None:
            self.assertIn("animation", _routing_concept().lower())

        # --- heuristics ---
        def test_tween_heuristics_present(self) -> None:
            self.assertTrue(len(_heuristics()) >= 5)

        def test_tween_animate_heuristic(self) -> None:
            self.assertTrue(any("animate" in h for h in _heuristics()))

        def test_tween_keyframe_heuristic(self) -> None:
            self.assertTrue(any("keyframe" in h for h in _heuristics()))

        # --- distinctions ---
        def test_tween_stage_distinction_present(self) -> None:
            self.assertIn("stage", _distinction_tokens())

        def test_tween_timeline_distinction_present(self) -> None:
            self.assertIn("timeline", _distinction_tokens())

        def test_tween_stage_distinction_names_progress(self) -> None:
            note = _distinction_note("stage")
            self.assertIn("progress", note)

        def test_tween_timeline_distinction_names_time(self) -> None:
            note = _distinction_note("timeline")
            self.assertTrue(
                "time" in note or "clock" in note or "temporal" in note,
                "timeline distinction must reference time-based positioning"
            )
