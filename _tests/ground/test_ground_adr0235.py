"""Tests for ADR-0235: executable validation and implementation artifact type definitions.

T1 artifact-type-definitions: executable validation defined as asserting behavioral
   properties with no behavior of its own; executable implementation defined as
   producing behavior with no assertions; overlap is a type-discipline violation;
   classification determined by content not path.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ArtifactTypeDefinitions(GroundADRTestBase):
    """Executable validation and implementation types are mutually exclusive by definition."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_validation_defined_as_asserting_properties(self):
        self.assertIn(
            "executable validation artifact is a file whose sole purpose is to assert behavioral properties",
            self.core,
        )

    def test_validation_contains_no_behavior_of_its_own(self):
        self.assertIn(
            "contains no behavior of its own",
            self.core,
        )

    def test_validation_files_not_imported_by_implementation(self):
        self.assertIn(
            "validation files may not be imported by implementation files",
            self.core,
        )

    def test_implementation_defined_as_producing_behavior(self):
        self.assertIn(
            "executable implementation artifact is a file that produces behavior directly",
            self.core,
        )

    def test_implementation_contains_no_assertions(self):
        self.assertIn(
            "implementation files may not contain assertions",
            self.core,
        )

    def test_overlap_is_type_discipline_violation(self):
        self.assertIn(
            "file that both asserts and implements is a type-discipline violation",
            self.core,
        )

    def test_classification_by_content_not_path(self):
        self.assertIn(
            "classification is determined by file content, not file path or naming convention",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "executable validation artifact is a file whose sole purpose is to assert behavioral properties",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
