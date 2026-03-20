"""Ground method prompt — structured parts (ADR-0171).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

The four parts correspond to the four independently maintainable concerns
identified in ADR-0171. Each part is a self-contained rule block.
"""

# ADR-0171: ground prompt structured parts.
# Edit each part independently; build_ground_prompt() serializes them in canonical order.
GROUND_PARTS: dict[str, str] = {
    "derivation_structure": (
        "I is the declared intent governing the invocation. "
        "I precedes and is not itself an artifact. "
        "Every artifact derives from I through the prior rung — form changes, intent does not. "
        "V is a constraint artifact self-contained to evaluate the next artifact without consulting I. "
        "O is the output evaluated against V. "
        "A rung is complete when and only when its artifact has been produced — "
        "not when it has been listed, planned, or described. "
        "A rung is not achievable when the domain provides no standard artifact type for it; "
        "this must be stated explicitly with justification — convenience, anticipated outcome, "
        "or prior knowledge do not make a rung not achievable. "
        "Completeness governs the depth of each rung's artifact; "
        "it does not affect whether a rung must be produced. "
        "Executable verification is required only for executable artifacts; "
        "prose artifacts do not require execution to be complete. "
        "Formal notation must satisfy R2: every behavioral constraint from the criteria rung "
        "must be re-expressed in the notation \u2014 not just interface shape; "
        "type signatures or schemas that capture structure without encoding invariants "
        "do not satisfy this rung. "
        "For code contexts the ladder instantiates as: "
        "prose (natural language description of intent and constraints) \u2192 "
        "criteria (acceptance conditions as plain statements) \u2192 "
        "formal notation (non-executable specification \u2014 type signatures, schemas, "
        "pseudocode, or contracts with behavioral invariants; may use code syntax but the "
        "artifact cannot be run as written) \u2192 "
        "executable validation (a file artifact invocable by an automated tool \u2014 "
        "go test, pytest, or equivalent \u2014 written to target the declared gap) \u2192 "
        "validation run observation \u2192 "
        "executable implementation \u2192 "
        "observed running behavior."
    ),
    "gate_validity": (
        "A gate is a conversation-state condition: open when and only when the required event "
        "has occurred in this conversation for this thread. "
        "Prior knowledge, anticipation, and model reasoning cannot satisfy any gate regardless of accuracy. "
        "For executable rungs, emit "
        "\U0001F534 Execution observed: [verbatim tool output \u2014 content composed without running the tool is invalid] "
        "then "
        "\U0001F534 Gap: [what the verbatim output reveals] "
        "on their own lines before any implementation artifact. "
        "Before producing implementation code, emit "
        "\U0001F7E2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001F534 Execution observed]. "
        "The quote must be verbatim from the \U0001F534 Execution observed sentinel of this thread; "
        "quoting anticipated output or a prior thread's observation is invalid. "
        "The \U0001F534 sentinel format is reserved exclusively for executable rung gates. "
        "For non-executable rungs, observation appears inline as labeled prose. "
        "No implementation artifact may appear before the \U0001F534 sentinels for the current thread. "
        "When the lowest V is complete, output \u2018\u2705 Validation artifact V complete\u2019 "
        "on its own line before producing O \u2014 this phrase may only appear after the "
        "executable validation rung has been both produced and invoked and the validation run "
        "observation rung has declared a gap."
    ),
    "derivation_discipline": (
        "Gap-locality: the gap gating rung N is the output of executing rung N-1. "
        "No gap from any higher rung, and no element of I directly, "
        "may serve as the gating gap for the current rung. "
        "Minimal scope: the current rung's artifact addresses the declared gap and nothing more. "
        "Implementing beyond the declared gap is a violation \u2014 not a benefit. "
        "Upward revision is always permitted when a gap is observed between prior understanding of I "
        "and something encountered via direct interaction with reality, code, or a stakeholder. "
        "Upward revision must be signposted with: what was observed, which rung is being revised, and why. "
        "It is never permitted to change I without first observing a gap in V that derived it. "
        "Changing I requires revising every artifact derived from it to restore chain consistency "
        "before descent continues."
    ),
    "reconciliation_and_completion": (
        "Intent precedes its representations. "
        "Every artifact that documents the governing intent of this invocation \u2014 "
        "whether produced in this invocation or pre-existing in the codebase \u2014 "
        "must be consistent with I before the invocation closes. "
        "If reconciliation is feasible, return up the chain to prose and rederive. "
        "If not feasible, report as a named process failure: which artifact diverges, "
        "what the divergence is, and why reconciliation could not occur. "
        "The invocation close must include a reconciliation report: "
        "either \u201call representations reconciled\u201d or the list of named failures with reasons. "
        "\u2705 Thread N complete may only appear after observed running behavior for that thread "
        "has been produced and recorded. "
        "\u2705 Manifest exhausted \u2014 N/N threads complete may only appear after all threads "
        "have emitted their completion sentinels and the reconciliation report has been produced."
    ),
}


def build_ground_prompt() -> str:
    """Serialize GROUND_PARTS into the ground method prompt string.

    Joins the four concern blocks in canonical order with a single space separator.
    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return " ".join(GROUND_PARTS[k] for k in GROUND_PARTS)
