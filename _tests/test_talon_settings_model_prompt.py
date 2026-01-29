import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.axisMappings import axis_key_to_value_map_for
    from talon_user.lib.staticPromptConfig import (
        STATIC_PROMPT_CONFIG,
        get_static_prompt_axes,
        static_prompt_settings_catalog,
    )
    import talon_user.lib.talonSettings as talon_settings
    from talon_user.lib.talonSettings import (
        applyPromptConfiguration,
        modelPrompt,
        pleasePromptConfiguration,
    )
    from talon_user.lib.modelState import GPTState

    class ModelPromptModifiersTests(unittest.TestCase):
        def setUp(self) -> None:
            # Ensure GPTState starts clean for tests that rely on derived axes.
            if bootstrap is not None:
                GPTState.reset_all()
                settings.set("user.model_default_completeness", "full")
                settings.set("user.model_default_scope", "")
                settings.set("user.model_default_method", "")
                settings.set("user.model_default_form", "")
                settings.set("user.model_default_channel", "")

        def test_no_modifiers_uses_static_prompt_profile_when_present(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # With no explicit axis modifiers, we should get a Task / Constraints
            # schema with a profile-driven completeness/scope hint.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn(
                "The response changes the form or presentation of given content while keeping its intended meaning.",
                result,
            )
            # Profile for "fix" includes completeness.
            self.assertIn("Completeness:", result)
            # Directional lens is pushed into the system prompt instead of the task text.
            self.assertEqual(GPTState.system_prompt.directional, "DIR")
            self.assertNotIn("\nDIR", result)

        def test_explicit_completeness_modifier_is_used_as_is(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Explicit completeness should appear under the Completeness line.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn("Completeness: COMP", result)
            self.assertEqual(GPTState.system_prompt.directional, "DIR")

        def test_scope_method_form_channel_modifiers_appended_in_order(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                scopeModifier="SCOPE",
                methodModifier="METHOD",
                formModifier="FORM",
                channelModifier="CHAN",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Check that all constraint lines are present under the schema.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn("Completeness: COMP", result)
            self.assertIn("Scope: SCOPE", result)
            self.assertIn("Method: METHOD", result)
            self.assertIn("Form: FORM", result)
            self.assertIn("Channel: CHAN", result)
            self.assertEqual(GPTState.system_prompt.directional, "DIR")

        def test_constraint_block_hydrates_axis_tokens(self):
            """Constraints should display hydrated axis descriptions while state stays tokenised."""
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="struct",
                methodModifier="flow",
                formModifier="bullets",
                channelModifier="jira",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            completeness_desc = axis_key_to_value_map_for("completeness").get(
                "skim", "skim"
            )
            scope_desc = axis_key_to_value_map_for("scope").get(
                "struct", "struct"
            )
            method_desc = axis_key_to_value_map_for("method").get("flow", "flow")
            form_desc = axis_key_to_value_map_for("form").get("bullets", "bullets")
            channel_desc = axis_key_to_value_map_for("channel").get("jira", "jira")

            self.assertIn(f"Completeness: {completeness_desc}", result)
            self.assertIn(f"Scope: {scope_desc}", result)
            self.assertIn(f"Method: {method_desc}", result)
            self.assertIn(f"Form: {form_desc}", result)
            self.assertIn(f"Channel: {channel_desc}", result)

        def test_missing_scope_method_form_channel_do_not_add_text(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                # scope/method/form/channel omitted on intent; profiles may add hints,
                # but we should not see the test sentinel tokens.
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            self.assertIn("Task:", result)
            self.assertIn("Completeness: COMP", result)
            # No literal sentinel tokens should appear for scope/method/form/channel.
            self.assertNotIn("SCOPE", result)
            self.assertNotIn("METHOD", result)
            self.assertNotIn("FORM", result)
            self.assertNotIn("CHAN", result)
            self.assertEqual(GPTState.system_prompt.directional, "DIR")

        def test_model_prompt_updates_system_prompt_axes(self):
            # Start from known defaults.
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_form", "")
            settings.set("user.model_default_channel", "")
            GPTState.reset_all()

            # Spoken modifiers should win over profiles and defaults.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="struct",
                methodModifier="flow",
                formModifier="bullets",
                channelModifier="adr",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.scope, "struct")
            self.assertEqual(GPTState.system_prompt.method, "flow")
            self.assertEqual(GPTState.system_prompt.form, "bullets")
            self.assertEqual(GPTState.system_prompt.channel, "adr")

        def test_model_prompt_uses_profiles_for_system_axes_when_unset(self):
            # Defaults are present but profile should shape the effective axes
            # when no spoken modifier is given.
            # "fix" has a profile for completeness only.
            m = SimpleNamespace(
                staticPrompt="fix",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "full")
            # No other axes are profiled, so they should be empty
            self.assertEqual(GPTState.system_prompt.scope, "")
            self.assertEqual(GPTState.system_prompt.method, "")
            self.assertEqual(GPTState.system_prompt.form, "")
            self.assertEqual(GPTState.system_prompt.channel, "")

        def test_directional_moves_to_system_prompt_and_hydrates(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                directionalModifier="fog",
            )

            result = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.directional, "fog")
            self.assertEqual(GPTState.last_directional, "fog")

            # The task text should not append the directional lens directly.
            self.assertNotIn("\nfog", result)

            # System prompt should hydrate the directional lens when present.
            directional_desc = axis_key_to_value_map_for("directional").get(
                "fog", "fog"
            )
            self.assertTrue(
                any(
                    line.startswith("Directional: ") and directional_desc in line
                    for line in GPTState.system_prompt.format_as_array()
                )
            )

        def test_prefixed_token_reassigns_to_highest_priority_axis(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                # Intentionally mis-placed axis token with explicit prefix.
                formModifier="Completeness:skim",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Completeness should capture the prefixed token; form should stay empty.
            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.form, "")
            self.assertIn("Completeness:", result)
            self.assertNotIn("Form:", result.split("Constraints:", 1)[-1])

        def test_axis_map_recovers_method_token_from_wrong_axis(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                # "flow" belongs to method; provide it under form to test reassignment.
                formModifier="flow",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # The method axis should capture the token; form should remain empty.
            self.assertEqual(GPTState.system_prompt.method, "flow")
            self.assertEqual(GPTState.system_prompt.form, "")

        def test_last_recipe_uses_resolved_axes(self):
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_form", "")
            settings.set("user.model_default_channel", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="infer",
                completenessModifier="full",
                # Misfile a method token under form.
                formModifier="flow",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # Method absorbs the token; form remains empty; recipe reflects resolved axes.
            self.assertEqual(GPTState.system_prompt.method, "flow")
            self.assertEqual(GPTState.system_prompt.form, "")
            self.assertEqual(GPTState.last_recipe, "infer · full · flow")

        def test_profile_axes_are_propagated_to_system_prompt(self) -> None:
            """Guardrail: profile axes should be reflected in GPTState.last_axes.

            For every profiled static prompt that defines scope/method axes,
            calling modelPrompt with only that staticPrompt (and a directional
            lens) should populate GPTState.last_axes with those axis tokens,
            subject to the usual axisConfig filtering and hierarchy rules.
            """

            from types import SimpleNamespace as _NS

            for name, _profile in STATIC_PROMPT_CONFIG.items():
                axes = get_static_prompt_axes(name)
                # Skip prompts with no profile axes.
                if not axes:
                    continue
                has_profile_axes = any(axis in axes for axis in ("scope", "method"))
                if not has_profile_axes:
                    continue

                with self.subTest(static_prompt=name):
                    GPTState.reset_all()
                    m = _NS(staticPrompt=name, directionalModifier="DIR")
                    _ = modelPrompt(m)

                    last_axes = GPTState.last_axes

                    for axis in ("scope", "method"):
                        configured = axes.get(axis)
                        if not configured:
                            continue
                        if isinstance(configured, list):
                            expected_tokens = [
                                str(v).strip() for v in configured if str(v).strip()
                            ]
                        else:
                            token = str(configured).strip()
                            expected_tokens = [token] if token else []

                        actual_tokens = last_axes.get(axis, [])
                        for token in expected_tokens:
                            self.assertIn(
                                token,
                                actual_tokens,
                                f"Static prompt {name!r} axis {axis!r} token {token!r} "
                                "not reflected in GPTState.last_axes",
                            )

        def test_ambiguous_token_uses_priority_order(self):
            """When a token is valid for multiple axes, the hierarchy should pick the higher-priority axis."""
            from talon_user.lib import axisMappings

            scope_map = axisMappings.AXIS_VALUE_TO_KEY_MAPS["scope"]
            method_map = axisMappings.AXIS_VALUE_TO_KEY_MAPS["method"]
            original_scope = scope_map.get("ambig")
            original_method = method_map.get("ambig")
            try:
                scope_map["ambig"] = "ambig"
                method_map["ambig"] = "ambig"

                m = SimpleNamespace(
                    staticPrompt="fix",
                    completenessModifier="full",
                    scopeModifier="ambig",
                    methodModifier="",
                    directionalModifier="DIR",
                )

                _ = modelPrompt(m)

                # Scope outranks method in the axis hierarchy, so the ambiguous token should land on scope.
                self.assertEqual(
                    GPTState.system_prompt.scope,
                    "ambig",
                    "Ambiguous token should resolve to the higher-priority scope axis",
                )
                self.assertEqual(
                    GPTState.system_prompt.method,
                    "",
                    "Method axis should remain empty when scope captures the token",
                )
            finally:
                if original_scope is None:
                    scope_map.pop("ambig", None)
                else:
                    scope_map["ambig"] = original_scope
                if original_method is None:
                    method_map.pop("ambig", None)
                else:
                    method_map["ambig"] = original_method

        def test_clear_all_resets_last_recipe_and_response(self):
            # Exercise the lifecycle: after a prompt, clear_all should drop
            # last_response/last_recipe so recap helpers don't show stale data.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="narrow",
                methodModifier="steps",
                formModifier="bullets",
                channelModifier="slack",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertNotEqual(GPTState.last_recipe, "")

            GPTState.clear_all()

            self.assertEqual(GPTState.last_recipe, "")
            self.assertEqual(GPTState.last_response, "")
            self.assertEqual(GPTState.last_meta, "")
            self.assertEqual(GPTState.last_directional, "")
            self.assertEqual(GPTState.last_static_prompt, "")
            self.assertEqual(GPTState.last_completeness, "")
            self.assertEqual(GPTState.last_scope, "")
            self.assertEqual(GPTState.last_method, "")
            self.assertEqual(GPTState.last_form, "")
            self.assertEqual(GPTState.last_channel, "")

        def test_model_prompt_updates_last_recipe_with_spoken_modifiers(self):
            # Spoken modifiers should be reflected in the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="struct",
                methodModifier="flow",
                formModifier="bullets",
                channelModifier="adr",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(
                GPTState.last_recipe,
                "fix · skim · struct · flow · bullets · adr",
            )
            self.assertEqual(GPTState.last_static_prompt, "fix")
            self.assertEqual(GPTState.last_completeness, "skim")
            self.assertEqual(GPTState.last_scope, "struct")
            self.assertEqual(GPTState.last_method, "flow")
            self.assertEqual(GPTState.last_form, "bullets")
            self.assertEqual(GPTState.last_channel, "adr")
            # Directional is stored as the short token when known; in this test
            # we use a sentinel "DIR" that is not in the Talon list, so it
            # should be preserved as-is.
            self.assertEqual(GPTState.last_directional, "DIR")

        def test_model_prompt_handles_multi_tag_scope_from_list(self):
            """Multi-tag scope from scopeModifier_list should be preserved and canonicalised."""
            # Start from known defaults.
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            GPTState.reset_all()

            # Simulate a Talon match object that exposes multiple scope
            # modifiers via the *_list attribute. Other axes remain single.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier_list=["struct", "time"],
                methodModifier="flow",
                formModifier="bullets",
                channelModifier="adr",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # System prompt should see the raw, spoken scope description.
            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.scope, "struct time")
            self.assertEqual(GPTState.system_prompt.method, "flow")
            self.assertEqual(GPTState.system_prompt.form, "bullets")
            self.assertEqual(GPTState.system_prompt.channel, "adr")

            # last_scope should reflect a canonicalised set of scope tokens.
            self.assertNotEqual(GPTState.last_scope, "")
            scope_tokens = GPTState.last_scope.split()
            self.assertEqual(set(scope_tokens), {"struct", "time"})

            # last_recipe should include a multi-token scope segment.
            self.assertIn("fix · skim", GPTState.last_recipe)
            self.assertIn("flow", GPTState.last_recipe)
            # The exact order of scope tokens is canonicalised; assert by set.
            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            scope_part = recipe_parts[2]
            self.assertEqual(set(scope_part.split()), {"struct", "time"})

        def test_model_prompt_enforces_scope_soft_cap_from_list(self):
            """Over-cap multi-tag scope from scopeModifier_list should respect the soft cap."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            GPTState.reset_all()

            # Provide three distinct scope modifiers even though the soft cap
            # for scope is 2; the canonicaliser should enforce the cap.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier_list=["struct", "time", "act"],
                methodModifier="flow",
                formModifier="bullets",
                channelModifier="adr",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # System prompt should see the capped, most recent scope tokens.
            self.assertEqual(GPTState.system_prompt.scope, "time act")

            # last_scope should include at most 2 tokens drawn from the input set.
            scope_tokens = GPTState.last_scope.split()
            self.assertLessEqual(len(scope_tokens), 2)
            self.assertTrue(set(scope_tokens).issubset({"time", "act"}))

            # last_recipe should reflect the capped, canonicalised scope tokens.
            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            # static, completeness, scope, method, form, channel
            scope_part = recipe_parts[2]
            scope_part_tokens = scope_part.split()
            self.assertLessEqual(len(scope_part_tokens), 2)
            self.assertTrue(
                set(scope_part_tokens).issubset({"struct", "time", "act"})
            )

        def test_model_prompt_handles_multi_tag_method_from_list(self):
            """Multi-tag method from methodModifier_list should be preserved and canonicalised."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="struct",
                methodModifier_list=["analysis", "flow"],
                formModifier="bullets",
                channelModifier="adr",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.method, "analysis flow")
            self.assertNotEqual(GPTState.last_method, "")
            method_tokens = GPTState.last_method.split()
            self.assertEqual(set(method_tokens), {"analysis", "flow"})

            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            # static, completeness, scope, method, form, channel
            method_part = recipe_parts[3]
            self.assertEqual(set(method_part.split()), {"analysis", "flow"})

        def test_model_prompt_rejects_legacy_style_modifier(self):
            """Guardrail: legacy styleModifier should fail fast post form/channel split."""
            m = SimpleNamespace(
                staticPrompt="fix",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            with self.assertRaises(ValueError) as ctx:
                modelPrompt(m)
            self.assertIn("use form/channel instead", str(ctx.exception))

        def test_apply_prompt_configuration_rejects_legacy_style_modifier(self):
            """Guardrail: applyPromptConfiguration should reject legacy style tokens."""
            m = SimpleNamespace(
                modelPrompt="describe",
                styleModifier="plain",
                directionalModifier="fog",
            )

            with patch.object(talon_settings, "notify") as notify_mock:
                with self.assertRaises(ValueError):
                    applyPromptConfiguration(m)

            notify_mock.assert_called_once()

        def test_please_prompt_configuration_rejects_legacy_style_modifier(self):
            """Guardrail: pleasePromptConfiguration should reject legacy style tokens."""
            m = SimpleNamespace(
                pleasePrompt="describe",
                styleModifier="plain",
            )

            with patch.object(talon_settings, "notify") as notify_mock:
                with self.assertRaises(ValueError):
                    pleasePromptConfiguration(m)

            notify_mock.assert_called_once()

        def test_spoken_axis_caps_scope_method_form_channel(self):
            """Spoken axis values should respect caps (scope≤2, method≤3, form=1, channel=1)."""
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier_list=["struct", "time", "act"],
                methodModifier_list=["analysis", "flow", "rigor", "diagnose"],
                formModifier_list=["bullets", "table"],
                channelModifier_list=["adr", "slack"],
                directionalModifier="fog",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.scope, "time act")
            self.assertEqual(GPTState.system_prompt.method, "flow rigor diagnose")
            self.assertEqual(GPTState.system_prompt.form, "table")
            self.assertEqual(GPTState.system_prompt.channel, "slack")
            scope_tokens = GPTState.last_scope.split()
            method_tokens = GPTState.last_method.split()
            self.assertLessEqual(len(scope_tokens), 2)
            self.assertLessEqual(len(method_tokens), 3)
            self.assertEqual(GPTState.last_form, "table")
            self.assertEqual(GPTState.last_channel, "slack")

        def test_model_prompt_handles_multi_tag_form_from_list(self):
            """Form list should respect singleton cap and keep the most recent token."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="ticket",
                completenessModifier="full",
                scopeModifier="actions",
                methodModifier="structure",
                formModifier_list=["bullets", "table"],
                channelModifier="slack",
                directionalModifier="fog",
            )

            _ = modelPrompt(m)

            # Form/channel should be singletons; last token wins for form list inputs.
            self.assertEqual(GPTState.system_prompt.form, "table")
            self.assertEqual(GPTState.last_form, "table")
            self.assertEqual(GPTState.last_channel, "slack")

            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            # Recipe should contain table (form) and slack (channel)
            self.assertIn("table", recipe_parts)
            self.assertIn("slack", recipe_parts)

        def test_model_prompt_enforces_channel_soft_cap_from_list(self):
            """Channel list should respect singleton cap and keep the most recent token."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="ticket",
                completenessModifier="full",
                scopeModifier="actions",
                methodModifier="structure",
                channelModifier_list=["slack", "jira", "remote"],
                directionalModifier="fog",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.channel, "remote")
            self.assertEqual(GPTState.last_channel, "remote")

            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            self.assertEqual(recipe_parts[-1], "remote")

        def test_model_prompt_updates_last_recipe_with_profile_axes(self):
            # When no spoken modifiers are provided, the per-prompt profile for
            # "fix" should drive the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="fix",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # fix profile only has completeness=full, using model default from setUp
            self.assertEqual(
                GPTState.last_recipe,
                "fix · full",
            )
            self.assertEqual(GPTState.last_static_prompt, "fix")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_scope, "")
            self.assertEqual(GPTState.last_method, "")
            self.assertEqual(GPTState.last_form, "")
            self.assertEqual(GPTState.last_directional, "DIR")

        def test_model_prompt_uses_profiles_for_filter_style_prompts(self):
            # Filter-style prompts like "relevant" no longer have axis profiles.
            m = SimpleNamespace(
                staticPrompt="relevant",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # No profile exists for relevant, using model default from setUp
            self.assertEqual(GPTState.system_prompt.completeness, "full")
            self.assertEqual(GPTState.system_prompt.scope, "")
            self.assertEqual(GPTState.system_prompt.method, "")

        def test_model_prompt_uses_struct_scope_for_dependency_prompts(self):
            # Relationship-style prompts like "dependency" no longer have a
            # scope profile, so scope should be empty unless explicitly set.
            m = SimpleNamespace(
                staticPrompt="dependency",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # No profile exists for dependency, so scope should be empty
            self.assertEqual(GPTState.system_prompt.scope, "")

        def test_static_prompt_settings_catalog_axes_align_with_model_prompt(self):
            """Static prompt settings catalog axes should match GPTState.last_axes when no spoken modifiers are present.

            This guards cross-surface consistency between the Axis & Static Prompt
            catalog facade and the Talon settings modelPrompt path for all
            profiled static prompts that define axis hints.
            """

            catalog = static_prompt_settings_catalog()

            for name, entry in catalog.items():
                axes = entry.get("axes", {}) or {}
                # Skip prompts with no profile axes.
                has_profile_axes = any(
                    axis in axes and axes.get(axis)
                    for axis in ("scope", "method", "completeness")
                )
                if not has_profile_axes:
                    continue

                with self.subTest(static_prompt=name):
                    GPTState.reset_all()
                    m = SimpleNamespace(staticPrompt=name, directionalModifier="DIR")
                    _ = modelPrompt(m)

                    last_axes = GPTState.last_axes or {}

                    for axis in ("scope", "method", "completeness"):
                        configured = axes.get(axis)
                        if not configured:
                            continue
                        if isinstance(configured, list):
                            expected_tokens = [
                                str(v).strip() for v in configured if str(v).strip()
                            ]
                        else:
                            token = str(configured).strip()
                            expected_tokens = [token] if token else []

                        actual_tokens = last_axes.get(axis, []) or []

                        for token in expected_tokens:
                            self.assertIn(
                                token,
                                actual_tokens,
                                f"Static prompt {name!r} axis {axis!r} token {token!r} "
                                "not reflected in GPTState.last_axes via settings catalog",
                            )

else:
    if not TYPE_CHECKING:

        class ModelPromptModifiersTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
