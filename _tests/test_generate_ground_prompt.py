"""Thread 2 validation: generate_axis_config.py emits correct ground value and import."""
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.tools.generate_axis_config as gen_module
from scripts.tools.generate_axis_config import render_axis_config
from lib.groundPrompt import build_ground_prompt


def test_generated_output_contains_groundprompt_import():
    # The generator inlines the ground value; it does not emit the import in its output.
    # What we actually want to verify is that the generator *uses* build_ground_prompt
    # to compute the ground value (so the SSOT flows correctly). Check the generator source.
    source = inspect.getsource(gen_module)
    assert "from lib.groundPrompt import build_ground_prompt" in source or \
           "from talon_user.lib.groundPrompt import build_ground_prompt" in source or \
           "build_ground_prompt" in source, (
        "Generator script must reference build_ground_prompt from lib.groundPrompt "
        "so that the ground token value flows from the SSOT"
    )


def test_generated_ground_value_matches_builder():
    output = render_axis_config()
    # ADR-0174: minimal spec is the current default; matches generate_axis_config.py minimal=True
    expected = build_ground_prompt()
    # pformat may wrap long strings into implicit concat segments; evaluate the
    # generated code to get the actual runtime value rather than raw text search.
    ns: dict = {}
    try:
        exec(compile(output, "<generated>", "exec"), ns)
    except Exception as e:
        raise AssertionError(f"Generated axisConfig.py failed to exec: {e}") from e
    actual = ns.get("AXIS_KEY_TO_VALUE", {}).get("method", {}).get("ground", "")
    assert actual == expected, (
        f"AXIS_KEY_TO_VALUE['method']['ground'] != build_ground_prompt()\n"
        f"  actual[:80]:   {actual[:80]!r}\n"
        f"  expected[:80]: {expected[:80]!r}"
    )
