import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class AxisCatalogValidateListsDirTests(unittest.TestCase):
        def setUp(self) -> None:
            self.repo_root = Path(__file__).resolve().parents[1]
            self.script = self.repo_root / "scripts" / "tools" / "axis-catalog-validate.py"

        def test_validate_with_custom_lists_dir_passes_when_generated(self) -> None:
            """Guardrail: axis-catalog-validate should pass against a generated lists dir."""

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                # Generate clean lists from the catalog into the temp dir.
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(tmp_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(tmp_path), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate should pass with generated lists\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                self.assertIn("Axis catalog validation passed", result.stdout + result.stderr)

        def test_validate_with_custom_lists_dir_flags_drift(self) -> None:
            """Guardrail: axis-catalog-validate should flag drift in a custom lists dir."""

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                # Generate clean lists, then introduce drift.
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(tmp_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                drift_file = tmp_path / "completenessModifier.talon-list"
                drift_file.write_text(
                    drift_file.read_text(encoding="utf-8") + "drift: drift\n",
                    encoding="utf-8",
                )

                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(tmp_path), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                self.assertNotEqual(result.returncode, 0, "Expected drift to cause a non-zero exit")
                self.assertIn("Axis catalog validation failed (errors:", result.stdout + result.stderr)
                self.assertIn("list generation drift", result.stdout + result.stderr)

        def test_validate_verbose_summary(self) -> None:
            """Guardrail: axis-catalog-validate --verbose should emit a summary."""

            result = subprocess.run(
                [sys.executable, str(self.script), "--verbose"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate --verbose failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("Axis catalog validation passed", result.stdout)
            self.assertIn("Axes=", result.stdout)
            self.assertIn("lists_dir=", result.stdout)

        def test_validate_verbose_summary_with_lists_dir_skipped(self) -> None:
            """Guardrail: passing lists-dir while skipping list checks should report the arg as skipped."""

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                result = subprocess.run(
                    [sys.executable, str(self.script), "--verbose", "--lists-dir", str(lists_dir)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate --verbose with lists-dir (skipped) failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                self.assertIn("lists_dir=<skipped>", result.stdout)
                self.assertIn(f"lists_dir_arg={lists_dir}", result.stdout)
                self.assertIn("list validation skipped", result.stdout)

        def test_validate_default_with_lists_dir_skipped_reports_note(self) -> None:
            """Guardrail: default run with lists-dir still skips list checks and emits a note."""

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(lists_dir)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate default run with lists-dir (skipped) failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                combined = result.stdout + result.stderr
                self.assertIn("Axis catalog validation passed", combined)
                self.assertIn("lists_dir=<skipped>", combined)
                self.assertIn("lists_validation=skipped", combined)
                self.assertIn("list validation skipped", combined)

        def test_validate_default_without_lists_dir_stays_minimal(self) -> None:
            """Guardrail: default run without lists-dir should not emit lists_dir details."""

            result = subprocess.run(
                [sys.executable, str(self.script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate default run failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            combined = result.stdout + result.stderr
            self.assertIn("Axis catalog validation passed", combined)
            self.assertNotIn("lists_dir", combined)
            self.assertNotIn("lists_validation", combined)
            self.assertNotIn("Note:", combined)

        def test_validate_verbose_with_lists_dir_enforced_reports_validated(self) -> None:
            """Guardrail: enforcing list checks should report validated lists_dir in verbose output."""

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                # Generate clean lists
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(lists_dir)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                result = subprocess.run(
                    [sys.executable, str(self.script), "--verbose", "--lists-dir", str(lists_dir), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate verbose enforced list checks failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                out = result.stdout + result.stderr
                self.assertIn(f"lists_dir={lists_dir}", out)
                self.assertIn(f"lists_validation=validated@{lists_dir}", out)
                self.assertNotIn("lists_dir=<skipped>", out)
                self.assertNotIn("list validation skipped", out)

        def test_validate_nonverbose_with_lists_dir_enforced_reports_validated(self) -> None:
            """Guardrail: enforcing list checks should report validated lists_dir in non-verbose output."""

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(lists_dir)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(lists_dir), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate enforced list checks failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                out = result.stdout + result.stderr
                self.assertIn("Axes=", out)
                self.assertIn("static_prompts=", out)
                self.assertIn(f"lists_dir={lists_dir}", out)
                self.assertIn(f"lists_validation=validated@{lists_dir}", out)
                self.assertNotIn("lists_dir=<skipped>", out)
                self.assertNotIn("list validation skipped", out)

        def test_validate_nonverbose_with_empty_lists_dir_reports_missing_files(self) -> None:
            """Guardrail: enforcing list checks against an empty lists dir should fail and report missing files."""

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(lists_dir), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                self.assertNotEqual(result.returncode, 0, "Expected empty lists dir to fail validation")
                combined = result.stdout + result.stderr
                self.assertIn("not found in lists_dir", combined)
                self.assertIn("completenessModifier.talon-list", combined)

        def test_validate_missing_lists_dir_fails(self) -> None:
            """Guardrail: axis-catalog-validate should fail if lists dir is missing/empty."""

            with tempfile.TemporaryDirectory() as tmpdir:
                missing_dir = Path(tmpdir) / "empty-lists"
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(missing_dir), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                self.assertNotEqual(result.returncode, 0, "Expected missing lists to cause validation failure")
                self.assertIn("Axis catalog validation failed (errors:", result.stdout + result.stderr)
                self.assertIn("lists_dir not found", result.stdout + result.stderr)
                self.assertIn("--lists-dir", result.stdout + result.stderr)
                self.assertIn("generate_talon_lists.py", result.stdout + result.stderr)

        def test_validate_requires_lists_dir_when_list_checks_forced(self) -> None:
            """Guardrail: enforcing list checks without a lists_dir should fail clearly."""

            result = subprocess.run(
                [sys.executable, str(self.script), "--no-skip-list-files"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            self.assertNotEqual(result.returncode, 0, "Expected missing --lists-dir to cause validation failure")
            combined = result.stdout + result.stderr
            self.assertIn("lists_dir is required", combined)
            self.assertIn("--lists-dir", combined)

        def test_validate_help_includes_lists_dir_and_verbose(self) -> None:
            """Guardrail: CLI help should surface lists-dir and verbose flags."""

            result = subprocess.run(
                [sys.executable, str(self.script), "--help"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            # argparse returns 0 when showing help.
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate --help failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("--lists-dir", result.stdout)
            self.assertIn("--verbose", result.stdout)
            self.assertIn("--skip-list-files", result.stdout)

        def test_validate_error_output_sorted(self) -> None:
            """Guardrail: failure output should be deterministic/sorted."""

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                # Generate clean lists, then introduce both missing and extra tokens.
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(tmp_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                drift_file = tmp_path / "completenessModifier.talon-list"
                original = drift_file.read_text(encoding="utf-8")
                # Remove a token and add an extra to force two drift messages.
                drift_file.write_text(
                    original.replace("full: full\n", ""), encoding="utf-8"
                )
                with drift_file.open("a", encoding="utf-8") as fh:
                    fh.write("extra: extra\n")

                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(tmp_path), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                self.assertNotEqual(result.returncode, 0, "Expected drift to cause a non-zero exit")
                lines = [line.strip() for line in (result.stdout + result.stderr).splitlines() if line.strip().startswith("- ")]
                self.assertGreaterEqual(len(lines), 2, "Expected at least two drift messages for sortedness check")
                self.assertEqual(lines, sorted(lines), "Expected drift messages to be sorted for determinism")

        def test_validate_missing_list_files_reported(self) -> None:
            """Guardrail: missing list files should be reported explicitly."""

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                # Generate only some lists to simulate missing files.
                gen_script = self.repo_root / "scripts" / "tools" / "generate_talon_lists.py"
                gen_result = subprocess.run(
                    [sys.executable, str(gen_script), "--out-dir", str(tmp_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

            # Remove one list file to trigger the missing file path.
            missing_file = tmp_path / "channelModifier.talon-list"
            if not missing_file.exists():
                missing_file.parent.mkdir(parents=True, exist_ok=True)
                missing_file.write_text("list: user.channelModifier\n-\nchannel: channel\n", encoding="utf-8")
            missing_file.unlink()

            result = subprocess.run(
                [sys.executable, str(self.script), "--lists-dir", str(tmp_path), "--no-skip-list-files"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            self.assertNotEqual(result.returncode, 0, "Expected missing list file to cause non-zero exit")
            combined = result.stdout + result.stderr
            self.assertIn("not found in lists_dir", combined)
            self.assertIn("channelModifier.talon-list", combined)
            self.assertIn("generate_talon_lists.py", combined)

        def test_validate_lists_dir_not_directory_fails(self) -> None:
            """Guardrail: axis-catalog-validate should fail when lists_dir is not a directory."""

            with tempfile.NamedTemporaryFile() as tmpfile:
                not_a_dir = Path(tmpfile.name)
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(not_a_dir), "--no-skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                self.assertNotEqual(result.returncode, 0, "Expected non-directory lists_dir to cause failure")
                combined = result.stdout + result.stderr
                self.assertIn("Axis catalog validation failed (errors:", combined)
                self.assertIn("lists_dir is not a directory", combined)
                self.assertIn("--lists-dir", combined)
                self.assertIn("generate_talon_lists.py", combined)

        def test_validate_skip_list_files_allows_missing_dir(self) -> None:
            """Guardrail: --skip-list-files should succeed even when lists_dir is absent."""

            with tempfile.TemporaryDirectory() as tmpdir:
                missing_dir = Path(tmpdir) / "does-not-exist"
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(missing_dir), "--skip-list-files"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate --skip-list-files failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                self.assertIn("Axis catalog validation passed", result.stdout + result.stderr)

        def test_validate_default_skips_missing_dir(self) -> None:
            """Guardrail: default skip-list-files should pass even if lists_dir is missing."""

            with tempfile.TemporaryDirectory() as tmpdir:
                missing_dir = Path(tmpdir) / "does-not-exist"
                result = subprocess.run(
                    [sys.executable, str(self.script), "--lists-dir", str(missing_dir)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.repo_root),
                )
                if result.returncode != 0:
                    self.fail(
                        f"axis-catalog-validate default skip failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                self.assertIn("Axis catalog validation passed", result.stdout + result.stderr)

else:

    class AxisCatalogValidateListsDirTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
