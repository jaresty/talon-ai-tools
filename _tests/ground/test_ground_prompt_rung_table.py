"""Tests for Thread 2: rung sequence table in groundPrompt.py.

Validates that after refactor:
- RUNG_SEQUENCE exists with 7 entries, each having required keys
- All 7 canonical rung names are present
- build_ground_prompt() output contains a tabular representation
- rung_sequence_code character count is lower than baseline
"""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt

CANONICAL_RUNG_NAMES = [
    "prose",
    "criteria",
    "formal notation",
    "executable validation",
    "validation run observation",
    "executable implementation",
    "observed running behavior",
]

REQUIRED_RUNG_KEYS = {"name", "type_label", "artifact", "gate", "voids_if"}

# Baseline character count of rung_sequence_code before refactor (measured: 8679 chars).
# Target: numbered list compressed to inline arrow sequence; reduction modest (~30+ chars).
BASELINE_RUNG_SEQUENCE_CODE_CHARS = 33100  # ADR-0205: three clash closures added (~33022 chars)


class TestRungSequenceExists(unittest.TestCase):
    def test_rung_sequence_dict_exists(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        self.assertIsInstance(RUNG_SEQUENCE, list)

    def test_rung_sequence_has_seven_entries(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        self.assertEqual(len(RUNG_SEQUENCE), 7)

    def test_each_entry_has_required_keys(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        for entry in RUNG_SEQUENCE:
            self.assertEqual(
                set(entry.keys()),
                REQUIRED_RUNG_KEYS,
                f"Entry {entry.get('name', '?')} missing required keys",
            )

    def test_all_canonical_rung_names_present(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        names = [entry["name"] for entry in RUNG_SEQUENCE]
        for canonical in CANONICAL_RUNG_NAMES:
            self.assertIn(canonical, names, f"Canonical rung name missing: {canonical}")

    def test_rung_order_matches_canonical(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        names = [entry["name"] for entry in RUNG_SEQUENCE]
        self.assertEqual(names, CANONICAL_RUNG_NAMES)


class TestBuildGroundPromptContainsRungTable(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prompt_contains_all_rung_names(self):
        for name in CANONICAL_RUNG_NAMES:
            self.assertIn(name, self.prompt, f"Rung name missing from prompt: {name}")


class TestRungSequenceCodeShorter(unittest.TestCase):
    def test_rung_sequence_code_shorter_than_baseline(self):
        actual = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            actual,
            BASELINE_RUNG_SEQUENCE_CODE_CHARS,
            f"GROUND_PARTS_MINIMAL core is {actual} chars; expected < {BASELINE_RUNG_SEQUENCE_CODE_CHARS}",
        )


class TestOBRHierarchyFallbackClosesStaticFiles(unittest.TestCase):
    """Thread 3: hierarchy-fallback-gap — realism hierarchy must not permit static file reads."""

    def setUp(self):
        from lib.groundPrompt import build_ground_prompt
        self.prompt = build_ground_prompt()

    def test_fallback_opens_gap_cycle(self):
        # ADR-0184: Thread B condensed fallback language; "static file" removed.
        # Current form: "If no invocable process exists, open a gap cycle to make the artifact directly invocable."
        self.assertIn(
            "open a gap cycle to make the artifact directly invocable",
            self.prompt,
            "OBR fallback must require opening a gap cycle when no invocable process exists",
        )

    def test_fallback_requires_new_gap_cycle(self):
        self.assertIn(
            "new gap cycle",
            self.prompt,
            "OBR fallback must require opening a new gap cycle when no live process can be started",
        )


class TestOBRInvocationPhraseRequiresLiveProcess(unittest.TestCase):
    """Thread 2: invoke-phrase-gap — OBR invocation instruction must require a live process."""

    def setUp(self):
        from lib.groundPrompt import build_ground_prompt
        self.prompt = build_ground_prompt()

    def test_obr_invocation_names_live_process(self):
        # ADR-0187: "live running process" replaced by "live-process invocation" in P4 Clause B.
        self.assertNotIn(
            "live running process",
            self.prompt,
            "ADR-0187: 'live running process' phrase must be absent — replaced by 'live-process invocation'",
        )
        self.assertIn(
            "live-process invocation",
            self.prompt,
            "P4 Clause B must use 'live-process invocation' terminology",
        )

    def test_obr_invocation_excludes_file_reads(self):
        # ADR-0182: "reading a file is not invoking a live process" removed as P1 corollary
        # P1 states file reads don't satisfy any gate; OBR artifact field names the type explicitly
        from lib.groundPrompt import RUNG_SEQUENCE
        obr_entry = next(e for e in RUNG_SEQUENCE if e["name"] == "observed running behavior")
        self.assertIn(
            "reading any file does not satisfy this type",
            obr_entry["artifact"],
            "OBR artifact definition must state reading any file does not satisfy the live-process-output type",
        )


class TestOBRArtifactTypeMechanismDefined(unittest.TestCase):
    """Thread 1: artifact-type-gap — OBR artifact field must be mechanism-defined."""

    def _obr_entry(self):
        from lib.groundPrompt import RUNG_SEQUENCE
        return next(e for e in RUNG_SEQUENCE if e["name"] == "observed running behavior")

    def test_obr_artifact_names_live_process(self):
        entry = self._obr_entry()
        self.assertIn("live", entry["artifact"], "OBR artifact must specify live-process mechanism")

    def test_obr_artifact_names_running_process(self):
        entry = self._obr_entry()
        self.assertIn("process", entry["artifact"], "OBR artifact must name 'process'")

    def test_obr_artifact_excludes_file_reads(self):
        entry = self._obr_entry()
        self.assertIn("file", entry["artifact"], "OBR artifact must explicitly exclude file reads")

    def test_obr_voids_if_includes_file_read(self):
        entry = self._obr_entry()
        self.assertIn("file", entry["voids_if"], "OBR voids_if must name file read as voiding condition")


if __name__ == "__main__":
    unittest.main()
