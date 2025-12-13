import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisCatalog import static_prompt_catalog
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    class StaticPromptAxisTokenTests(unittest.TestCase):
        def test_profiled_prompt_axes_use_valid_axis_tokens(self) -> None:
            """Guardrail: profiled static prompts must only reference known axis tokens.

            This ties STATIC_PROMPT_CONFIG profiles (via static_prompt_catalog) back to
            axisConfig.AXIS_KEY_TO_VALUE so axis semantics stay aligned across the
            catalog and axis configuration (ADR-0045 Axis & Static Prompt domain).
            """

            catalog = static_prompt_catalog()
            axis_map = AXIS_KEY_TO_VALUE

            for entry in catalog.get("profiled", []):
                axes = entry.get("axes", {}) or {}
                for axis_name, value in axes.items():
                    # Focus this guardrail on axes whose tokens are expected
                    # to come directly from axisConfig; completeness hints may
                    # intentionally use looser language for now.
                    if axis_name not in {"scope", "method", "form", "channel", "directional"}:
                        continue

                    # Axis must exist in axisConfig.
                    self.assertIn(
                        axis_name,
                        axis_map,
                        f"Unknown axis {axis_name!r} in static prompt profile {entry['name']!r}",
                    )
                    # Normalise to a list of tokens for checking.
                    if isinstance(value, list):
                        tokens = [str(v) for v in value]
                    else:
                        tokens = [str(value)] if value else []
                    for token in tokens:
                        self.assertIn(
                            token,
                            axis_map[axis_name],
                            f"Unknown {axis_name} token {token!r} in static prompt profile {entry['name']!r}",
                        )
else:
    if not TYPE_CHECKING:

        class StaticPromptAxisTokenTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
