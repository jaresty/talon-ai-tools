"""
Test that all examples in `bar help llm` are valid bar commands.

This prevents silent drift where example commands in the LLM reference
become invalid as the grammar evolves.
"""

import subprocess
import re
import unittest


class TestBarHelpLLMExamples(unittest.TestCase):
    """Validate all example commands in bar help llm output."""

    def setUp(self):
        """Extract example commands from bar help llm patterns section."""
        try:
            result = subprocess.run(
                ["go", "run", "./cmd/bar", "help", "llm", "--section", "patterns"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.patterns_output = result.stdout
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to run 'bar help llm --section patterns': {e}")

    def extract_example_commands(self):
        """Extract all example bar build commands from patterns output."""
        # Match code blocks under **Example:** headers
        example_pattern = r'\*\*Example:\*\*\n```bash\n(bar build [^\n]+)\n```'
        matches = re.findall(example_pattern, self.patterns_output)
        return matches

    def test_all_examples_parse(self):
        """Test that all example commands can be parsed by bar."""
        examples = self.extract_example_commands()

        # Ensure we found examples
        self.assertGreater(
            len(examples),
            0,
            "No example commands found in bar help llm output. "
            "Check that patterns section is present.",
        )

        failures = []
        for cmd in examples:
            # Extract tokens from "bar build <tokens>... --subject \"...\""
            # Split on --subject to get just the token part
            if "--subject" not in cmd:
                failures.append(f"Missing --subject in example: {cmd}")
                continue

            token_part = cmd.split("--subject")[0].strip()
            # Remove "bar build" prefix
            if not token_part.startswith("bar build "):
                failures.append(f"Invalid example format: {cmd}")
                continue

            tokens = token_part.replace("bar build ", "").strip().split()

            # Test that bar can parse these tokens
            # We don't need actual subject text for validation
            test_cmd = ["go", "run", "./cmd/bar", "build"] + tokens + ["--subject", "test"]

            try:
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # If it succeeds, the command is valid
            except subprocess.CalledProcessError as e:
                # Check if error is about parsing/tokens vs other issues
                if "unknown" in e.stderr.lower() or "invalid" in e.stderr.lower():
                    failures.append(
                        f"Invalid command: {cmd}\n"
                        f"  Tokens: {tokens}\n"
                        f"  Error: {e.stderr.strip()}"
                    )
            except subprocess.TimeoutExpired:
                failures.append(f"Command timed out: {cmd}")

        # Report all failures together
        if failures:
            self.fail(
                f"Found {len(failures)} invalid example(s) in bar help llm:\n\n"
                + "\n\n".join(failures)
            )

    def test_example_count(self):
        """Test that we have the expected number of examples."""
        examples = self.extract_example_commands()

        # We added 23 patterns in Loop 8, so we should have 23 examples
        self.assertEqual(
            len(examples),
            23,
            f"Expected 23 example commands in patterns section, found {len(examples)}. "
            f"If you added/removed patterns, update this test.",
        )

    def test_patterns_have_framing(self):
        """Test that patterns section includes discovery-focused framing."""
        # Check for key phrases from Loop 9 framing
        self.assertIn(
            "reference material for learning grammar and syntax",
            self.patterns_output,
            "Patterns section missing discovery-focused framing text",
        )
        self.assertIn(
            "LLMs should use their own reasoning",
            self.patterns_output,
            "Patterns section missing instruction for LLMs to use reasoning",
        )
        # Check for the key principle (accounting for markdown bold formatting)
        output_lower = self.patterns_output.lower()
        self.assertIn(
            "how",
            output_lower,
            "Patterns section missing 'how' in key principle",
        )
        self.assertIn(
            "which",
            output_lower,
            "Patterns section missing 'which' in key principle",
        )
        self.assertIn(
            "tokens work together",
            output_lower,
            "Patterns section missing 'tokens work together' phrase",
        )


if __name__ == "__main__":
    unittest.main()
