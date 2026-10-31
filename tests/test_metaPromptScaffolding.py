"""Tests for the meta-prompt scaffolding (lib/metaPromptConfig.py).

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
    from lib import metaPromptConfig

    return metaPromptConfig


def test_scaffolding_module_exposes_the_expected_names():
    scaffolding = _plain()
    for name in FIELDS + ("PROMPT_REFERENCE_KEY", "TOKEN_LOADING", "COMPOSITION_LOADING", "SEQUENCE"):
        assert hasattr(scaffolding, name), f"missing {name}"
    assert {"task", "addendum", "constraints", "constraints_axes", "persona", "subject"} <= set(scaffolding.PROMPT_REFERENCE_KEY)


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


def test_plain_directive_requires_exact_quotes_for_every_token_including_method():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "copied exactly" in d, "quotes must be copied exactly, not paraphrased"
    assert "one line for each token" in d
    assert "do not join" in d, "separate lines must not be stitched into one quote"
    assert "method token" in d


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


def test_plain_directive_method_quote_is_any_exact_line_not_the_first_step():
    d = _plain().PLANNING_DIRECTIVE.lower()
    assert "first step it called for" not in d, "forcing 'the first step' pushes the model to stitch text together"
    assert "any line" in d or "one line" in d, "method quote is one exact line where the method shows"


def test_plain_directive_has_no_steps_line():
    d = _plain().PLANNING_DIRECTIVE
    assert "Steps:" not in d and "->" not in d, "the Steps line was dropped: haiku omitted it in most runs"
    assert "for a method token, quote any line" in d.lower(), "the method quote rule stays"


def test_plain_token_loading_puts_lookups_before_any_other_tool_call():
    text = _plain().TOKEN_LOADING
    low = text.lower()
    assert "before any other tool call" in low, "lookups must precede every other tool call"
    assert "whatever the call is for" in low, "the ordering must not depend on which kind of call it is"
    for software_term in ("reading files", "searching code", "running commands"):
        assert software_term not in low, f"domain-specific term {software_term!r} in a gate clause"
    assert "no need to look it up again" not in low, "the skip-if-visible escape lets agents skip the lookups"
    assert "invalidates" not in low and "does not satisfy" not in low


def test_plain_composition_loading_puts_lookups_before_any_other_tool_call():
    text = _plain().COMPOSITION_LOADING
    low = text.lower()
    assert "before any other tool call" in low
    assert "bar help composition" in text and "Remaining (not loaded)" in text


GATE_PHRASES = ("does not satisfy", "An evaluator", "evaluator determines")


def _all_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _all_strings(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from _all_strings(v)


def test_plain_sequence_rewrites_remove_every_gate_clause_from_sequence_hints():
    from lib.sequenceConfig import SEQUENCES

    rewrites = _plain().SEQUENCE.get("rewrites", [])
    assert rewrites, "plain.sequence.rewrites must exist"
    texts = list(_all_strings(SEQUENCES))
    for old, new in rewrites:
        assert any(old in t for t in texts), f"rewrite source no longer found in sequenceConfig: {old[:60]!r}"
        for phrase in GATE_PHRASES:
            assert phrase not in new, f"rewrite still contains {phrase!r}: {new[:60]!r}"
    remaining = []
    for t in texts:
        for old, new in rewrites:
            t = t.replace(old, new)
        remaining += [p for p in GATE_PHRASES if p in t]
    assert not remaining, f"gate clauses left after rewrites: {sorted(set(remaining))}"


def test_during_dispatch_text_restores_the_interruption_contract():
    start = _plain().SEQUENCE["dispatch"]["start_during"]
    low = start.lower()
    assert "instruction" in low and "carry it out" in low, "the during-dispatch bar build output is that task's instruction"
    assert "not user messages" in low, "agent results are not user messages"
    assert "own stop condition" in low, "the task runs until its own stop condition"
    assert "after the question" in low, "a step that asks the user is complete only after a user message follows"
    assert "do not quote" in low, "agent results are not quoted until the task is finished"
    assert "{cmd}" in start


def test_directional_policy_is_not_stated_on_universal_surfaces():
    scaffolding = _plain()
    assert "directional" not in scaffolding.META_INTERPRETATION_GUIDANCE.lower(), "token-specific rule on a universal surface"
    for text in (scaffolding.PROMPT_REFERENCE_KEY["constraints_axes"]["directional"], scaffolding._AXIS_FULL_TEXT["directional"]):
        low = text.lower()
        assert "applies globally and implicitly" in low or "applies globally" in low
        assert "do not name" not in low and "name or label" not in low and "do not describe, name" not in low
