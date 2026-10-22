import json
import unittest
from pathlib import Path

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    ROOT = Path(__file__).resolve().parents[1]
    GRAMMAR_COPIES = (
        "build/prompt-grammar.json",
        "internal/barcli/embed/prompt-grammar.json",
        "cmd/bar/testdata/grammar.json",
        "web/static/prompt-grammar.json",
    )

    def _grammar_presume(path: str) -> str:
        with (ROOT / path).open(encoding="utf-8") as handle:
            return json.load(handle)["axes"]["definitions"]["method"]["presume"]

    def _carriers() -> dict:
        """Every committed surface that carries the presume description."""
        carriers = {"lib/axisConfig.py": AXIS_KEY_TO_VALUE["method"]["presume"]}
        for path in GRAMMAR_COPIES:
            carriers[path] = _grammar_presume(path)
        return carriers

    class PresumeDefinitionTests(unittest.TestCase):
        def _assert_carried(self, fragment: str) -> None:
            for path, text in _carriers().items():
                with self.subTest(carrier=path):
                    self.assertIn(fragment, text)

        def _assert_absent(self, fragment: str) -> None:
            for path, text in _carriers().items():
                with self.subTest(carrier=path):
                    self.assertNotIn(fragment, text)

        def test_every_carrier_holds_the_same_description(self) -> None:
            carriers = _carriers()
            source = carriers["lib/axisConfig.py"]
            for path, text in carriers.items():
                with self.subTest(carrier=path):
                    self.assertEqual(source, text)

        def test_unstated_rule_is_a_choice(self) -> None:
            self._assert_carried("that no material available to the response states")

        def test_reduced_scope_or_finish_is_not_a_candidate(self) -> None:
            self._assert_carried(
                "reduces the work's scope or finish below what the subject asks for"
            )

        def test_tie_break_takes_the_option_reaching_least(self) -> None:
            self._assert_carried("reach least beyond what the response itself produced")

        def test_dependent_part_names_its_withdrawal(self) -> None:
            self._assert_carried("Withdrawn by: <means>")

        def test_request_in_place_of_a_closing_line_is_unclosed(self) -> None:
            self._assert_carried(
                "a request for approval or clarification raised instead leaves it unclosed"
            )

        def test_old_stop_and_ask_guard_is_gone(self) -> None:
            self._assert_absent(
                "instead of stopping to request approval or clarification"
            )

        def test_old_bare_no_action_clause_is_gone(self) -> None:
            self._assert_absent("and does not act on it")
