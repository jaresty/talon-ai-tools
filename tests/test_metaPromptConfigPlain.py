"""Tests for the plain web variant of the meta-prompt scaffolding.

The plain variant keeps a lightweight, checkable token-application record while
dropping features that read as reasoning-extraction templates: a pre-answer
derivation span, counterfactual self-reasoning, span-control rules, and
foreign-language framing in the prose.
"""
import re

FIELDS = (
    "PREAMBLE",
    "AXIS_INTERACTION",
    "PLANNING_DIRECTIVE",
    "SUBJECT_FRAMING",
    "META_INTERPRETATION_GUIDANCE",
)
CJK = re.compile(r"[぀-ヿ一-鿿]")


def _plain():
    from lib import metaPromptConfigPlain

    return metaPromptConfigPlain


def test_plain_module_exposes_same_names_as_standard():
    plain = _plain()
    for name in FIELDS + ("PROMPT_REFERENCE_KEY",):
        assert hasattr(plain, name), f"missing {name}"
    from lib.metaPromptConfig import PROMPT_REFERENCE_KEY as std

    assert set(plain.PROMPT_REFERENCE_KEY) == set(std)
    assert set(plain.PROMPT_REFERENCE_KEY["constraints_axes"]) == set(std["constraints_axes"])


def test_plain_directive_keeps_checkable_record_after_the_answer():
    d = _plain().PLANNING_DIRECTIVE
    assert "## Token application" in d
    assert "Token derivations:" not in d
    assert "Derived stance complete" not in d
    assert "before task content" not in d.lower()


def test_plain_directive_record_is_checkable_against_the_response():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "quote" in d, "each token line must cite a phrase from the response"


def test_plain_text_has_no_counterfactual_or_span_control_clauses():
    plain = _plain()
    for name in FIELDS:
        text = getattr(plain, name)
        assert not re.search(r"without \[", text), name
        assert "tool call result" not in text.lower() or name == "META_INTERPRETATION_GUIDANCE", name
        assert "re-derive" not in text.lower(), name
        assert "verbatim and authoritative" not in text.lower(), name


def test_plain_prose_has_no_cjk():
    plain = _plain()
    for name in FIELDS:
        assert not CJK.search(getattr(plain, name)), name


def test_plain_directive_is_shorter_than_standard():
    from lib.metaPromptConfig import PLANNING_DIRECTIVE as std

    assert len(_plain().PLANNING_DIRECTIVE) < len(std)


def test_plain_directive_requires_exact_quotes_for_every_token_including_method():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "copied exactly" in d, "quotes must be copied exactly, not paraphrased"
    assert "one line for each token" in d
    assert "do not join" in d, "separate lines must not be stitched into one quote"
    assert "method token" in d and "steps:" in d


def test_plain_token_loading_is_a_light_lookup_instruction():
    plain = _plain()
    assert hasattr(plain, "TOKEN_LOADING"), "plain module must define TOKEN_LOADING"
    text = plain.TOKEN_LOADING
    assert "bar help token" in text
    assert "Remaining (not loaded)" in text, "batch-continuation marker must stay"
    assert "Loaded:" not in text and "does not satisfy" not in text
    assert "invalidates the run" not in text
    assert not CJK.search(text)
    assert len(text) < 1200


def test_plain_composition_loading_is_a_light_lookup_instruction():
    plain = _plain()
    assert hasattr(plain, "COMPOSITION_LOADING"), "plain module must define COMPOSITION_LOADING"
    text = plain.COMPOSITION_LOADING
    assert "bar help composition" in text
    assert "Remaining (not loaded)" in text
    assert "Composition active:" not in text and "Loaded:" not in text
    assert "does not satisfy" not in text
    assert not CJK.search(text)
    assert len(text) < 1000


SEQUENCE_KEYS = (
    "mode_autonomous",
    "mode_linear",
    "mode_cycle",
    "opening",
    "build_gate",
    "action_step",
)
FLAGGED_PHRASES = ("does not satisfy", "invalidates the run", "Sequence Derivation", "satisfies this gate")


def test_plain_sequence_text_has_expected_keys_and_no_gate_ceremony():
    seq = _plain().SEQUENCE
    assert set(SEQUENCE_KEYS) <= set(seq), "missing sequence keys"
    for key in SEQUENCE_KEYS:
        value = seq[key]
        parts = value if isinstance(value, list) else [value]
        assert parts and all(isinstance(p, str) and p.strip() for p in parts), key
        for part in parts:
            for phrase in FLAGGED_PHRASES:
                assert phrase not in part, f"{key} contains {phrase!r}"
            assert not CJK.search(part), key


def test_plain_sequence_keeps_the_functional_markers():
    seq = _plain().SEQUENCE
    assert "Step N complete." in seq["mode_autonomous"]
    assert "Agents complete:" in seq["mode_autonomous"]
    assert any("bar build" in line for line in seq["build_gate"])
    assert "Sequence:" in seq["opening"] and "extra step" in seq["opening"]


DISPATCH_KEYS = (
    "header",
    "preflight",
    "orchestrator_only",
    "fan_out_enumerate",
    "fan_out_replicate",
    "isolation_true",
    "isolation_false",
    "start",
    "start_during",
    "agent_task",
    "agent_task_inner",
    "join_all",
    "join_first",
    "join_merge",
    "after",
    "cycle_intro",
    "cycle_check",
    "inner_action",
)
DISPATCH_FLAGGED = FLAGGED_PHRASES + ("DISPATCH GATE", "An evaluator", "evaluator determines", "dispatch protocol — required")


def test_plain_dispatch_text_has_expected_keys_and_no_gate_ceremony():
    dispatch = _plain().SEQUENCE.get("dispatch", {})
    assert set(DISPATCH_KEYS) <= set(dispatch), "missing dispatch keys"
    for key in DISPATCH_KEYS:
        value = dispatch[key]
        parts = value if isinstance(value, list) else [value]
        assert parts and all(isinstance(p, str) and p.strip() for p in parts), key
        for part in parts:
            for phrase in DISPATCH_FLAGGED:
                assert phrase not in part, f"dispatch.{key} contains {phrase!r}"
            assert not CJK.search(part), key


def test_plain_dispatch_keeps_functional_requirements():
    d = _plain().SEQUENCE.get("dispatch", {})
    joined = " ".join(
        p for v in d.values() for p in (v if isinstance(v, list) else [v])
    )
    for marker in (
        "## Agent Configuration",
        "subagent_type: general-purpose",
        "Dispatching N agents:",
        "run_in_background: true",
        "## Derivation",
        "shoshin",
        "bar build",
    ):
        assert marker in joined, f"plain dispatch text lost {marker!r}"
    assert "{cmd}" in d.get("start_during", ""), "during-dispatch command placeholder"
    assert "{ctx}" in d.get("isolation_true", ""), "isolation context placeholder"
    assert "{tok}" in d.get("cycle_check", ""), "cycle last-token placeholder"


def test_plain_directive_gives_form_tokens_something_to_quote():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "form" in d and "first line" in d, "form tokens must quote the first line of the structure they shaped"


def test_plain_directive_method_steps_are_a_separate_line_with_fixed_shape():
    d = _plain().PLANNING_DIRECTIVE
    assert "Steps:" in d, "method steps line must have a fixed 'Steps:' shape"
    assert "->" in d, "steps are listed with arrows in order of appearance"


def test_plain_directive_method_quote_is_any_exact_line_not_the_first_step():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "first step it called for" not in d, "forcing 'the first step' pushes the model to stitch text together"
    assert "any line" in d or "one line" in d, "method quote is one exact line where the method shows"


def test_plain_directive_steps_line_is_required_and_separate():
    d = _plain().PLANNING_DIRECTIVE
    assert "own line" in d, "Steps: must be its own line, not appended to the token line"
    assert "never join" in d.lower() or "not on the token line" in d.lower()
