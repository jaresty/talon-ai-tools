"""Python-layer tests for sequenceConfig.py (gate layer boundary requirement).

These tests assert structural entities owned by the Python layer — SEQUENCES dict,
validate_sequences(), example field, new sequence names — independently of the Go
grammar pipeline. A bug in sequenceConfig.py must fail here before reaching Go.
"""
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if TYPE_CHECKING:
    from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences


class TestSequenceConfigStructure(unittest.TestCase):

    def setUp(self):
        from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences
        self.sequences = SEQUENCES
        self.validate = validate_sequences

    # Behavior: SEQUENCES is non-empty
    def test_sequences_non_empty(self):
        self.assertGreater(len(self.sequences), 0, "SEQUENCES must be non-empty")

    # Behavior: each sequence has a non-empty description
    def test_all_sequences_have_description(self):
        for name, seq in self.sequences.items():
            self.assertIsInstance(seq.get("description"), str, f"{name}: description must be a string")
            self.assertTrue(seq["description"], f"{name}: description must be non-empty")

    # Behavior: each sequence has a non-empty example
    def test_all_sequences_have_example(self):
        for name, seq in self.sequences.items():
            self.assertIsInstance(seq.get("example"), str, f"{name}: example must be a string")
            self.assertTrue(seq["example"], f"{name}: example must be non-empty")

    # Behavior: each sequence has a valid mode
    def test_all_sequences_have_valid_mode(self):
        valid_modes = {"autonomous", "linear", "cycle"}
        for name, seq in self.sequences.items():
            self.assertIn(seq.get("mode"), valid_modes, f"{name}: mode must be one of {valid_modes}")

    # Behavior: each sequence has ≥2 steps
    def test_all_sequences_have_at_least_two_steps(self):
        for name, seq in self.sequences.items():
            steps = seq.get("steps", [])
            self.assertGreaterEqual(len(steps), 2, f"{name}: must have ≥2 steps")

    # Behavior: each prompt step has token and role; dispatch steps have role only
    def test_all_steps_have_token_and_role(self):
        for name, seq in self.sequences.items():
            for i, step in enumerate(seq.get("steps", [])):
                self.assertIsInstance(step.get("role"), str, f"{name} step {i}: role must be a string")
                self.assertTrue(step["role"], f"{name} step {i}: role must be non-empty")
                if step.get("type") not in ("dispatch", "action"):
                    self.assertIsInstance(step.get("token"), str, f"{name} step {i}: token must be a string")
                    self.assertTrue(step["token"], f"{name} step {i}: token must be non-empty")

    # Behavior: three new sequences exist
    def test_gather_and_synthesize_exists(self):
        self.assertIn("gather-and-synthesize", self.sequences)

    def test_plan_and_retrospect_exists(self):
        self.assertIn("plan-and-retrospect", self.sequences)

    def test_simulate_and_review_exists(self):
        self.assertIn("simulate-and-review", self.sequences)

    # Behavior: validate_sequences returns no errors for current SEQUENCES
    def test_validate_sequences_passes(self):
        errors = self.validate(self.sequences, known_tokens=set())
        self.assertEqual(errors, [], f"validate_sequences reported errors: {errors}")

    # Behavior: linear/cycle sequences have at least one step with requires_user_input or during_dispatch
    # A dispatch step with during_dispatch is structurally equivalent to requires_user_input:
    # the user engages with the during_dispatch task while agents run, which is the pause.
    def test_interactive_sequences_have_pause_step(self):
        for name, seq in self.sequences.items():
            if seq.get("mode") in ("linear", "cycle"):
                has_pause = any(
                    step.get("requires_user_input") or step.get("during_dispatch")
                    for step in seq.get("steps", [])
                )
                self.assertTrue(has_pause, f"{name} (mode={seq['mode']}): must have at least one step with requires_user_input=True or during_dispatch")


    # Behavior: dispatch steps are allowed to omit token field
    def test_dispatch_steps_do_not_require_token(self):
        for name, seq in self.sequences.items():
            for i, step in enumerate(seq.get("steps", [])):
                if step.get("type") == "dispatch":
                    self.assertNotIn("token", step, f"{name} step {i}: dispatch step must not have a token field")
                    self.assertIn("fan_out", step, f"{name} step {i}: dispatch step must have fan_out")
                    self.assertIn("join", step, f"{name} step {i}: dispatch step must have join")

    # Behavior: validate_sequences rejects dispatch steps missing fan_out or join
    def test_validate_sequences_rejects_dispatch_without_fan_out_join(self):
        bad_seq = {
            "bad": {
                "description": "test",
                "example": "test",
                "mode": "autonomous",
                "steps": [
                    {"token": "task:make", "role": "first"},
                    {"type": "dispatch", "role": "second"},  # missing fan_out and join
                ],
            }
        }
        errors = self.validate(bad_seq, known_tokens={"task:make"})
        self.assertTrue(any("fan_out" in e or "join" in e for e in errors),
                        f"Expected error about missing fan_out/join, got: {errors}")

    # Behavior: token-rewrite sequence exists
    def test_token_rewrite_exists(self):
        self.assertIn("token-rewrite", self.sequences, "token-rewrite sequence must exist")

    # Behavior: token-rewrite has a dispatch step for parallel behavioral verification
    def test_token_rewrite_has_dispatch_step(self):
        seq = self.sequences.get("token-rewrite")
        self.assertIsNotNone(seq, "token-rewrite sequence must exist")
        dispatch_steps = [s for s in seq["steps"] if s.get("type") == "dispatch"]
        self.assertGreater(len(dispatch_steps), 0, "token-rewrite must have a dispatch step for parallel behavioral verification")

    # Behavior: frame-eval has a dispatch step
    def test_parallel_eval_has_dispatch_step(self):
        seq = self.sequences.get("frame-eval")
        self.assertIsNotNone(seq, "frame-eval sequence must exist")
        dispatch_steps = [s for s in seq["steps"] if s.get("type") == "dispatch"]
        self.assertGreater(len(dispatch_steps), 0, "frame-eval must have at least one dispatch step")

    # Behavior: contradiction-scan sequence exists
    def test_contradiction_scan_exists(self):
        self.assertIn("contradiction-scan", self.sequences, "contradiction-scan sequence must exist")

    # Behavior: contradiction-scan has at least 3 steps (decompose, surface, recommend)
    def test_contradiction_scan_has_three_steps(self):
        seq = self.sequences.get("contradiction-scan")
        self.assertIsNotNone(seq, "contradiction-scan sequence must exist")
        self.assertGreaterEqual(len(seq.get("steps", [])), 3, "contradiction-scan must have at least 3 steps")

    # Behavior: cycle-mode sequences have a non-empty stop_when predicate
    def test_cycle_sequences_have_stop_when(self):
        for name, seq in self.sequences.items():
            if seq.get("mode") == "cycle":
                self.assertIsInstance(seq.get("stop_when"), str, f"{name}: stop_when must be a string")
                self.assertTrue(seq["stop_when"], f"{name}: stop_when must be non-empty")


    def _frame_explore_prism_prompt_hint(self) -> str:
        seq = self.sequences.get("frame-explore")
        self.assertIsNotNone(seq, "frame-explore sequence must exist")
        prism_step = seq["steps"][0]
        return prism_step.get("prompt_hint", "")

    # Behavior: frame-explore prism states goal condition must be a coverage criterion
    def test_frame_explore_prism_states_coverage_criterion(self):
        hint = self._frame_explore_prism_prompt_hint()
        self.assertIn("coverage criterion", hint,
                      "'coverage criterion' not found in frame-explore prism prompt_hint")

    # Behavior: frame-explore prism requires Goal condition: heading label
    def test_frame_explore_prism_requires_goal_condition_heading(self):
        hint = self._frame_explore_prism_prompt_hint()
        self.assertIn("Goal condition:", hint,
                      "'Goal condition:' not found in frame-explore prism prompt_hint")

    # Behavior: frame-explore prism requires enumerable set of cases
    def test_frame_explore_prism_requires_enumerable_set(self):
        hint = self._frame_explore_prism_prompt_hint()
        self.assertIn("enumerable set of cases", hint,
                      "'enumerable set of cases' not found in frame-explore prism prompt_hint")

    # Behavior: frame-explore prism names conditional statement as invalid
    def test_frame_explore_prism_rejects_conditional(self):
        hint = self._frame_explore_prism_prompt_hint()
        self.assertIn("A conditional statement", hint,
                      "'A conditional statement' not found in frame-explore prism prompt_hint")

    def _frame_explore_vet_prompt_hint(self) -> str:
        seq = self.sequences.get("frame-explore")
        self.assertIsNotNone(seq, "frame-explore sequence must exist")
        dispatch_step = seq["steps"][1]
        vet_step = dispatch_step["inner"]["steps"][2]
        return vet_step.get("prompt_hint", "")

    def _frame_debug_vet_prompt_hint(self) -> str:
        seq = self.sequences.get("frame-debug")
        self.assertIsNotNone(seq, "frame-debug sequence must exist")
        dispatch_step = seq["steps"][1]
        vet_step = dispatch_step["inner"]["steps"][2]
        return vet_step.get("prompt_hint", "")

    # Behavior: frame-explore vet names allowed tool call type for live execution
    def test_frame_explore_vet_names_allowed_tool_call_type(self):
        hint = self._frame_explore_vet_prompt_hint()
        self.assertIn("a Bash tool call executing a command (live execution) satisfies this step", hint,
                      "'a Bash tool call executing a command (live execution) satisfies this step' not found in frame-explore vet prompt_hint")

    # Behavior: frame-explore vet names denied tool call type for file reads
    def test_frame_explore_vet_names_denied_tool_call_type(self):
        hint = self._frame_explore_vet_prompt_hint()
        self.assertIn("a Read tool call or a Bash call using", hint,
                      "'a Read tool call or a Bash call using' not found in frame-explore vet prompt_hint")

    # Behavior: frame-explore vet declares file-read evidence invalid
    def test_frame_explore_vet_declares_file_read_evidence_invalid(self):
        hint = self._frame_explore_vet_prompt_hint()
        self.assertIn("If the probe step used only file reads, the evidence is invalid", hint,
                      "'If the probe step used only file reads, the evidence is invalid' not found in frame-explore vet prompt_hint")

    # Behavior: frame-debug vet names allowed tool call type for live execution
    def test_frame_debug_vet_names_allowed_tool_call_type(self):
        hint = self._frame_debug_vet_prompt_hint()
        self.assertIn("a Bash tool call executing a command (live execution) satisfies this step", hint,
                      "'a Bash tool call executing a command (live execution) satisfies this step' not found in frame-debug vet prompt_hint")

    # Behavior: frame-debug vet names denied tool call type for file reads
    def test_frame_debug_vet_names_denied_tool_call_type(self):
        hint = self._frame_debug_vet_prompt_hint()
        self.assertIn("a Read tool call or a Bash call using", hint,
                      "'a Read tool call or a Bash call using' not found in frame-debug vet prompt_hint")

    # Behavior: frame-debug vet declares file-read evidence invalid
    def test_frame_debug_vet_declares_file_read_evidence_invalid(self):
        hint = self._frame_debug_vet_prompt_hint()
        self.assertIn("If the probe step used only file reads, the evidence is invalid", hint,
                      "'If the probe step used only file reads, the evidence is invalid' not found in frame-debug vet prompt_hint")


if __name__ == "__main__":
    unittest.main()
