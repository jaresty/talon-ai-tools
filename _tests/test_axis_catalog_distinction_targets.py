import importlib.util
import re
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    def _load_validator():
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "tools"
            / "axis-catalog-validate.py"
        )
        spec = importlib.util.spec_from_file_location("axis_catalog_validate", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _catalog(distinctions):
        return {
            "axes": {"scope": {"act": "", "jobs": ""}},
            "static_prompts": {"profiled": [{"name": "probe"}], "unprofiled_tokens": []},
            "axis_token_metadata": {"scope": {"act": {"distinctions": distinctions}}},
        }

    class DistinctionTargetTests(unittest.TestCase):
        def test_resolvable_axis_token_target_passes(self) -> None:
            """A distinction naming a registered axis token is accepted."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "jobs"}])
            )
            self.assertEqual(errors, [])

        def test_task_target_passes(self) -> None:
            """A distinction may reference a task, not only an axis token."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "probe"}])
            )
            self.assertEqual(errors, [])

        def test_unknown_target_fails(self) -> None:
            """A distinction pointing at a renamed or removed token is rejected."""

            module = _load_validator()
            errors = module.validate_distinction_targets(
                _catalog([{"note": "x", "token": "resilience"}])
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("references unknown token 'resilience'", errors[0])

        def test_missing_token_field_fails(self) -> None:
            """A distinction with no target at all is rejected."""

            module = _load_validator()
            errors = module.validate_distinction_targets(_catalog([{"note": "x"}]))
            self.assertEqual(len(errors), 1)
            self.assertIn("no 'token' field", errors[0])

        def test_real_catalog_has_no_dangling_targets(self) -> None:
            """Regression: the committed catalog resolves every distinction target."""

            import sys

            root = Path(__file__).resolve().parents[1]
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            from lib.axisCatalog import axis_catalog

            module = _load_validator()
            errors = module.validate_distinction_targets(axis_catalog(lists_dir=None))
            self.assertEqual(errors, [], f"dangling distinction targets: {errors}")


    class DistinctionAttributionTests(unittest.TestCase):
        """Every description clause in a distinction note must be attributable.

        The catalog convention is bilateral: a note names both the owning token
        and the contrasted one, so a reader can tell which description belongs
        to which token. Some notes state one side's description with no subject
        at all ("interacting whole; grove = ..."), leaving the clause dangling —
        the contrast does not parse as a contrast.

        Prose phrasing is fine ("gate blocks action until a condition is met;
        falsify requires ..."); what this guard requires is only that each token
        appear by name somewhere in its own note.
        """

        # Entries that still fail this invariant and need authored contrast text
        # rather than a subject label. Tracked as debt, not exempted silently.
        KNOWN_UNATTRIBUTED: set[tuple[str, str, str]] = set()

        def _metadata(self):
            import sys

            root = Path(__file__).resolve().parents[1]
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            from lib.axisConfig import AXIS_TOKEN_METADATA

            return AXIS_TOKEN_METADATA

        @staticmethod
        def _names(token: str, note: str) -> bool:
            return re.search(rf"\b{re.escape(token)}\b", note) is not None

        def test_every_distinction_note_names_both_tokens(self) -> None:
            """Regression: no distinction note leaves a description clause unattributed."""
            offenders = []
            for axis, tokens in self._metadata().items():
                for slug, meta in tokens.items():
                    for entry in meta.get("distinctions") or []:
                        other = entry.get("token", "")
                        note = entry.get("note", "")
                        if (axis, slug, other) in self.KNOWN_UNATTRIBUTED:
                            continue
                        missing = [
                            name
                            for name in (slug, other)
                            if not self._names(name, note)
                        ]
                        if missing:
                            offenders.append(
                                f"[{axis}] {slug} vs {other}: note never names "
                                f"{', '.join(repr(m) for m in missing)} — {note[:90]!r}"
                            )
            self.assertEqual(
                offenders,
                [],
                "distinction notes with an unattributable description clause:\n"
                + "\n".join(offenders),
            )

        def test_known_unattributed_entries_still_exist(self) -> None:
            """The debt list must not outlive the entries it excuses."""
            metadata = self._metadata()
            for axis, slug, other in sorted(self.KNOWN_UNATTRIBUTED):
                entries = metadata.get(axis, {}).get(slug, {}).get("distinctions") or []
                notes = [e.get("note", "") for e in entries if e.get("token") == other]
                self.assertTrue(
                    notes,
                    f"KNOWN_UNATTRIBUTED names {axis}/{slug} vs {other}, which no "
                    "longer exists — drop it from the list",
                )
                still_broken = any(
                    not (self._names(slug, n) and self._names(other, n)) for n in notes
                )
                self.assertTrue(
                    still_broken,
                    f"{axis}/{slug} vs {other} now names both tokens — remove it "
                    "from KNOWN_UNATTRIBUTED so the guard covers it",
                )


if __name__ == "__main__":
    unittest.main()
