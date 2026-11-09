import importlib.util
import sys
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

    def _real_catalog():
        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from lib.axisCatalog import axis_catalog

        return axis_catalog(lists_dir=None)

    class UniqueTokenNameTests(unittest.TestCase):
        def test_name_on_two_axes_fails(self) -> None:
            """A token name registered on two axes is rejected."""

            module = _load_validator()
            errors = module.validate_token_names_unique_across_axes(
                {"axes": {"scope": {"act": ""}, "method": {"act": ""}}}
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("'act'", errors[0])
            self.assertIn("method", errors[0])
            self.assertIn("scope", errors[0])

        def test_distinct_names_pass(self) -> None:
            """Names unique across axes are accepted."""

            module = _load_validator()
            errors = module.validate_token_names_unique_across_axes(
                {"axes": {"scope": {"act": ""}, "method": {"abduce": ""}}}
            )
            self.assertEqual(errors, [])

    class DistinctionPresenceTests(unittest.TestCase):
        def _catalog(self, payload):
            return {
                "axes": {"scope": {"act": ""}},
                "axis_token_metadata": {"scope": {"act": payload}},
            }

        def test_token_without_distinctions_fails(self) -> None:
            """A token that states no distinction against any neighbour is rejected."""

            module = _load_validator()
            errors = module.validate_distinctions_present(
                self._catalog({"distinctions": []})
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("'act'", errors[0])

        def test_token_with_distinction_passes(self) -> None:
            """A token with at least one distinction is accepted."""

            module = _load_validator()
            errors = module.validate_distinctions_present(
                self._catalog({"distinctions": [{"note": "x", "token": "jobs"}]})
            )
            self.assertEqual(errors, [])

        def test_null_directional_is_exempt(self) -> None:
            """jog is the null directional and needs no distinction."""

            module = _load_validator()
            errors = module.validate_distinctions_present(
                {
                    "axes": {"directional": {"jog": ""}},
                    "axis_token_metadata": {
                        "directional": {"jog": {"distinctions": []}}
                    },
                }
            )
            self.assertEqual(errors, [])

    class SameAxisIncompatibilityTests(unittest.TestCase):
        AXES = {"scope": {"act": "", "jobs": ""}, "method": {"abduce": ""}}

        def test_cross_axis_conflict_fails(self) -> None:
            """axis_incompatibilities is same-axis only; a cross-axis pair is rejected."""

            module = _load_validator()
            errors = module.validate_incompatibilities_same_axis(
                {"scope": {"act": ["abduce"]}}, self.AXES
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("'abduce'", errors[0])

        def test_same_axis_conflict_passes(self) -> None:
            """A conflict between two tokens of one axis is accepted."""

            module = _load_validator()
            errors = module.validate_incompatibilities_same_axis(
                {"scope": {"act": ["jobs"]}}, self.AXES
            )
            self.assertEqual(errors, [])

    # Pairs authored when the A2 gap was closed (ADR-0241). Each is stated from both
    # tokens' side so a chooser starting from either one sees the seam.
    AUTHORED_PAIRS = [
        ("channel", "html", "svg"),
        ("channel", "html", "code"),
        ("channel", "svg", "diagram"),
        ("channel", "svg", "sketch"),
        ("channel", "code", "shellscript"),
        ("channel", "code", "notebook"),
        ("channel", "shellscript", "demo"),
        ("channel", "notebook", "codetour"),
        ("channel", "gherkin", "jira"),
        ("channel", "jira", "slack"),
        ("channel", "slack", "github"),
        ("channel", "adr", "ledger"),
        ("channel", "adr", "skill"),
        ("channel", "adr", "agent"),
        ("channel", "plain", "aloud"),
        ("channel", "plain", "demo"),
        ("channel", "plain", "tight"),
        ("channel", "remote", "sync"),
        ("form", "dialogue", "ibis"),
        ("form", "dialogue", "storyboard"),
        ("form", "wardley", "timeline"),
        ("form", "wardley", "chart"),
        ("method", "own", "redact"),
        ("method", "own", "bound"),
        ("method", "adversarial", "unknowns"),
    ]

    class AuthoredDistinctionPairTests(unittest.TestCase):
        def test_authored_pairs_are_stated_from_both_sides(self) -> None:
            """Each authored pair is declared on both tokens."""

            metadata = _real_catalog().get("axis_token_metadata", {})
            axes = _real_catalog().get("axes", {})

            def targets(token):
                found = set()
                for axis_name, tokens in metadata.items():
                    for d in ((tokens or {}).get(token, {}) or {}).get("distinctions", []):
                        found.add(d.get("token"))
                return found

            missing = []
            for _axis, a, b in AUTHORED_PAIRS:
                if b not in targets(a):
                    missing.append(f"{a} -> {b}")
                if a not in targets(b):
                    missing.append(f"{b} -> {a}")
            self.assertEqual(missing, [], f"one-sided or missing: {missing}")

        def test_authored_notes_use_affirmative_wording(self) -> None:
            """A distinction contrasts what each token does; it is not a prohibition."""

            metadata = _real_catalog().get("axis_token_metadata", {})
            pairs = {(a, b) for _x, a, b in AUTHORED_PAIRS}
            pairs |= {(b, a) for _x, a, b in AUTHORED_PAIRS}
            bad = []
            for tokens in metadata.values():
                for token, payload in (tokens or {}).items():
                    for d in (payload or {}).get("distinctions", []):
                        if (token, d.get("token")) in pairs and any(
                            w in d["note"].lower()
                            for w in (" not ", " never ", " no ", "without", "does not", "cannot")
                        ):
                            bad.append((token, d["token"]))
            self.assertEqual(bad, [], f"prohibition wording in: {bad}")


    class DirectionalCompoundTests(unittest.TestCase):
        def _catalog(self, token, targets):
            return {
                "axes": {"directional": {token: ""}},
                "axis_token_metadata": {
                    "directional": {
                        token: {"distinctions": [{"note": "x", "token": t} for t in targets]}
                    }
                },
            }

        def test_compound_naming_both_parts_passes(self) -> None:
            """A compound whose distinctions name its vertical and horizontal parts is accepted."""

            module = _load_validator()
            errors = module.validate_directional_compounds_name_their_parts(
                self._catalog("fly bog", ["fog", "bog"])
            )
            self.assertEqual(errors, [])

        def test_compound_missing_a_part_fails(self) -> None:
            """A compound that omits one component is rejected."""

            module = _load_validator()
            errors = module.validate_directional_compounds_name_their_parts(
                self._catalog("fly bog", ["fog"])
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("'fly bog'", errors[0])

        def test_compound_naming_a_wrong_part_fails(self) -> None:
            """A compound whose distinction targets the wrong vertical pole is rejected."""

            module = _load_validator()
            errors = module.validate_directional_compounds_name_their_parts(
                self._catalog("dip ong", ["fog", "ong"])
            )
            self.assertEqual(len(errors), 1)

        def test_simple_token_is_ignored(self) -> None:
            """A single-pole token is not a compound and needs no component check."""

            module = _load_validator()
            errors = module.validate_directional_compounds_name_their_parts(
                self._catalog("dig", ["fog"])
            )
            self.assertEqual(errors, [])

        def test_real_catalog_compounds_name_their_parts(self) -> None:
            """Regression: every committed directional compound names its two parts."""

            module = _load_validator()
            errors = module.validate_directional_compounds_name_their_parts(
                _real_catalog()
            )
            self.assertEqual(errors, [], f"compound drift: {errors}")

    class NullDirectionalTests(unittest.TestCase):
        def test_jog_label_describes_the_null_orientation(self) -> None:
            """jog's label and routing concept state its definition: no directional push."""

            catalog = _real_catalog()
            label = catalog["axis_labels"]["directional"]["jog"].lower()
            routing = catalog["axis_routing_concept"]["directional"]["jog"].lower()
            for text in (label, routing):
                self.assertNotIn("clarification", text)
                self.assertTrue(
                    any(w in text for w in ("direction", "orientation", "compass")),
                    f"jog text does not describe orientation: {text!r}",
                )

    class SoftCapTableTests(unittest.TestCase):
        def _talon_settings(self):
            try:
                from bootstrap import bootstrap

                bootstrap()
                from talon_user.lib import talonSettings
            except Exception as exc:  # pragma: no cover - environment dependent
                self.skipTest(f"talonSettings not importable here: {exc}")
            return talonSettings

        def test_single_valued_axes_are_in_the_cap_table(self) -> None:
            """topology and completeness are single-valued, and the table says so."""

            caps = self._talon_settings().axis_soft_caps()
            self.assertEqual(caps.get("topology"), 1)
            self.assertEqual(caps.get("completeness"), 1)

        def test_existing_caps_are_unchanged(self) -> None:
            """The caps that were already declared keep their values."""

            caps = self._talon_settings().axis_soft_caps()
            for axis, value in {
                "scope": 2,
                "method": 5,
                "form": 1,
                "channel": 3,
                "directional": 1,
            }.items():
                self.assertEqual(caps.get(axis), value, axis)

        def test_canonicalise_keeps_the_latest_single_valued_token(self) -> None:
            """A second topology or completeness token replaces the first."""

            settings = self._talon_settings()
            self.assertEqual(
                settings._canonicalise_axis_tokens("topology", ["witness", "audit"]),
                ["audit"],
            )
            self.assertEqual(
                settings._canonicalise_axis_tokens("completeness", ["full", "deep"]),
                ["deep"],
            )

    class ReciprocalDistinctionTests(unittest.TestCase):
        def _catalog(self, edges, axes=None, tasks=()):
            axes = axes or {"scope": {"act": "", "jobs": ""}}
            meta = {}
            for axis_name, tokens in axes.items():
                meta[axis_name] = {t: {"distinctions": []} for t in tokens}
            for axis_name, src, dst in edges:
                meta[axis_name][src]["distinctions"].append({"note": "x", "token": dst})
            return {
                "axes": axes,
                "axis_token_metadata": meta,
                "static_prompts": {"profiled": [{"name": t} for t in tasks]},
            }

        def test_one_way_distinction_fails(self) -> None:
            """A distinction stated on one token only is rejected."""

            module = _load_validator()
            errors = module.validate_distinctions_reciprocal(
                self._catalog([("scope", "act", "jobs")])
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("'act'", errors[0])
            self.assertIn("'jobs'", errors[0])

        def test_mirrored_pair_passes(self) -> None:
            """A pair stated from both sides is accepted."""

            module = _load_validator()
            errors = module.validate_distinctions_reciprocal(
                self._catalog([("scope", "act", "jobs"), ("scope", "jobs", "act")])
            )
            self.assertEqual(errors, [])

        def test_task_target_is_exempt(self) -> None:
            """A distinction against a task has no reverse entry to require."""

            module = _load_validator()
            errors = module.validate_distinctions_reciprocal(
                self._catalog([("scope", "act", "probe")], tasks=("probe",))
            )
            self.assertEqual(errors, [])

        def test_directional_compound_to_part_is_exempt(self) -> None:
            """A compound names its parts; the parts do not list every compound."""

            module = _load_validator()
            axes = {"directional": {"fly ong": "", "fog": "", "ong": ""}}
            errors = module.validate_distinctions_reciprocal(
                self._catalog(
                    [("directional", "fly ong", "fog"), ("directional", "fly ong", "ong")],
                    axes=axes,
                )
            )
            self.assertEqual(errors, [])

        def test_real_catalog_distinctions_are_reciprocal(self) -> None:
            """Regression: every committed token-to-token distinction is stated both ways."""

            module = _load_validator()
            errors = module.validate_distinctions_reciprocal(_real_catalog())
            self.assertEqual(errors, [], f"{len(errors)} one-way distinctions: {errors[:5]}")

    class RealCatalogDesignRuleTests(unittest.TestCase):
        def test_real_catalog_satisfies_design_rules(self) -> None:
            """Regression: the committed catalog satisfies A1, A2 and A5."""

            module = _load_validator()
            catalog = _real_catalog()
            errors = (
                module.validate_token_names_unique_across_axes(catalog)
                + module.validate_distinctions_present(catalog)
            )
            self.assertEqual(errors, [], f"design-rule violations: {errors}")

        def test_real_incompatibilities_are_same_axis(self) -> None:
            """Regression: no cross-axis pair is registered in axis_incompatibilities.

            Checked here, not in the CLI, because reading the hierarchy imports
            lib.talonSettings, which the CLI's interpreter cannot always load.
            """

            try:
                from bootstrap import bootstrap

                bootstrap()
                from talon_user.lib.talonSettings import axis_incompatibilities
            except Exception as exc:  # pragma: no cover - environment dependent
                self.skipTest(f"talonSettings not importable here: {exc}")
            module = _load_validator()
            errors = module.validate_incompatibilities_same_axis(
                axis_incompatibilities(), _real_catalog().get("axes", {})
            )
            self.assertEqual(errors, [], f"cross-axis incompatibilities: {errors}")

        def test_main_runs_the_design_rules(self) -> None:
            """main() wires the catalog-only validators into the CLI run."""

            source = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "axis-catalog-validate.py"
            ).read_text()
            for name in (
                "validate_token_names_unique_across_axes",
                "validate_distinctions_present",
                "validate_directional_compounds_name_their_parts",
                "validate_distinctions_reciprocal",
            ):
                self.assertIn(f"{name}(", source.split("def main()")[1])
