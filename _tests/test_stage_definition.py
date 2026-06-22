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
        return AXIS_KEY_TO_VALUE["form"]["stage"]

    def _summary() -> str:
        return AXIS_KEY_TO_LABEL.get("form", {}).get("stage", "")

    def _routing_concept() -> str:
        return AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {}).get("stage", "")

    def _heuristics() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("stage", {}).get("heuristics", [])

    def _distinctions() -> list:
        return AXIS_TOKEN_METADATA.get("form", {}).get("stage", {}).get("distinctions", [])

    def _distinction_tokens() -> list:
        return [d["token"] for d in _distinctions()]

    def _distinction_note(token: str) -> str:
        for d in _distinctions():
            if d["token"] == token:
                return d["note"]
        return ""

    class StageDefinitionTests(unittest.TestCase):
        # --- root criterion phrase ---
        def test_stage_named_block_clause(self) -> None:
            """State is a 'named block whose name appears in at least one transition'."""
            self.assertIn(
                "named block whose name appears in at least one transition",
                _defn(),
            )

        def test_stage_transition_separate_artifact(self) -> None:
            """Transition must be 'a separate artifact'."""
            self.assertIn("separate artifact", _defn())

        def test_stage_no_duration_required(self) -> None:
            """Duration/time occupancy clause removed — not a structural requirement."""
            self.assertNotIn("time occupancy", _defn())
            self.assertNotIn("literal value, not a qualitative descriptor", _defn())

        def test_stage_no_labeled_block(self) -> None:
            """'labeled block' replaced by addressable 'named block' clause."""
            self.assertNotIn("labeled block", _defn())

        def test_stage_joint_minimum_gate(self) -> None:
            """At least two state blocks AND at least one transition — jointly stated."""
            self.assertIn("at least one transition", _defn())

        def test_stage_no_any_notation_clause(self) -> None:
            """Medium-agnosticism clause removed (not evaluator-checkable)."""
            self.assertNotIn("Any notation is permitted", _defn())

        def test_stage_no_percentage_position(self) -> None:
            """Animation-domain percentage position format clause removed."""
            self.assertNotIn("percentage position", _defn())

        # --- summary and routing_concept ---
        def test_stage_summary_no_timing(self) -> None:
            """Summary updated — 'timing' removed."""
            self.assertNotIn("timing", _summary())

        def test_stage_summary_has_transition_artifacts(self) -> None:
            """Summary references transition artifacts."""
            self.assertIn("transition", _summary())

        def test_stage_routing_concept_updated(self) -> None:
            """routing_concept updated — no longer 'Temporal state sequence'."""
            self.assertNotEqual("Temporal state sequence", _routing_concept())
            self.assertIn("transition", _routing_concept())

        # --- heuristics ---
        def test_stage_no_animate_this_heuristic(self) -> None:
            """Animation-domain heuristic removed."""
            self.assertNotIn("animate this", _heuristics())

        def test_stage_no_keyframe_heuristic(self) -> None:
            """Animation-domain heuristic removed."""
            self.assertNotIn("keyframe sequence", _heuristics())

        def test_stage_state_machine_heuristic(self) -> None:
            """State-machine heuristic added."""
            self.assertTrue(
                any("state machine" in h for h in _heuristics()),
                "Expected a 'state machine' heuristic",
            )

        def test_stage_lifecycle_heuristic(self) -> None:
            """Lifecycle/phase heuristic added."""
            self.assertTrue(
                any("lifecycle" in h or "life cycle" in h for h in _heuristics()),
                "Expected a lifecycle heuristic",
            )

        # --- distinctions ---
        def test_stage_timeline_distinction_present(self) -> None:
            """timeline distinction present."""
            self.assertIn("timeline", _distinction_tokens())

        def test_stage_distinctions_no_timing_references(self) -> None:
            """All distinction notes updated — no 'timing' or 'duration values' references."""
            for d in _distinctions():
                self.assertNotIn(
                    "timing", d["note"],
                    f"distinction note for '{d['token']}' still contains 'timing'"
                )
                self.assertNotIn(
                    "duration values", d["note"],
                    f"distinction note for '{d['token']}' still contains 'duration values'"
                )

        def test_stage_flow_distinction_names_transition_artifacts(self) -> None:
            """flow distinction explicitly names transition artifacts as differentiator."""
            note = _distinction_note("flow")
            self.assertIn("transition", note, "flow distinction must reference transition artifacts")
