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
        "Every artifact derives from I through the prior rung \u2014 form changes, intent does not. "
        "V is a constraint artifact self-contained to evaluate the next artifact without consulting I. "
        "O is the output evaluated against V. "
        "Three rules govern every thread. "
        "R1 (I is fixed): every artifact derives from I through faithful derivation of the prior rung \u2014 "
        "the form changes, the intent does not. "
        "R2 (rung criterion): an artifact is a rung iff upward-faithful (derived from the prior rung "
        "without adding unstated constraints) and downward-sufficient (self-contained to evaluate the "
        "next artifact without consulting I); domain phases are not downward-sufficient \u2014 writing tests "
        "for 'API layer' requires knowing what the API must do, which comes from I, not the phase name. "
        "R3 (observation terminates): every thread descends to observed running behavior; only "
        "tool-executed output with a declared gap satisfies the execution gate; skipped tests are not observations. "
        "A rung is complete when and only when its artifact has been produced \u2014 "
        "not when it has been listed, planned, or described. "
        "A rung is not achievable when the domain provides no standard artifact type for it; "
        "this must be stated explicitly with justification \u2014 convenience, anticipated outcome, "
        "or prior knowledge do not make a rung not achievable. "
        "ground is a Process method \u2014 the task governs the character of each rung's output "
        "but not the process structure; the manifest, rung sequence, and execution gates are "
        "mandatory regardless of which task or other tokens are combined with ground; "
        "completeness governs rung depth, not rung existence. "
        "Executable verification is required only for executable artifacts; "
        "prose artifacts do not require execution to be complete. "
        "Formal notation must satisfy R2: every behavioral constraint from the criteria rung "
        "must be re-expressed in the notation \u2014 not just interface shape; "
        "type signatures or schemas that capture structure without encoding invariants "
        "do not satisfy this rung. "
        "Boundary: the manifest is the first and only output before the manifest-complete sentinel \u2014 "
        "no rung work, planning text, or content of any kind may appear before it; "
        "observation of existing code or running behavior sufficient to establish I is permitted "
        "before the manifest when I cannot be declared from context alone \u2014 "
        "this is I-formation, not rung work; exploration beyond what is needed to declare I "
        "belongs as the first rung of the manifest, not pre-manifest. "
        "Foundational constraint: a symbol is not the state it represents \u2014 "
        "a rung label during execution marks the point where the artifact begins \u2014 "
        "it is not a section heading for planning, description, or exploration about the rung; "
        "no content other than the artifact itself may appear between a rung label and the artifact it precedes. "
        "Eagerness to implement is the primary failure mode \u2014 "
        "an implementation produced without passing validation is invalid and will be discarded; "
        "the shortest path to a valid implementation is strict rung adherence, not shortcuts; "
        "every skipped rung produces output that must be thrown away. "
        "When beginning mid-ladder, first locate the highest already-instantiated rung "
        "and update it to reflect the intended change, then descend. "
        "Traversal (R5): depth-first by thread; within a thread, advance through every feasible rung; "
        "stopping mid-thread is only permitted when the next rung is not achievable. "
        "For code contexts, each rung in this sequence may not be skipped or combined with another \u2014 "
        "the executable implementation rung is blocked until the validation run observation rung "
        "has declared a gap. "
        "R4 instantiates as: "
        "prose (natural language description of intent and constraints) \u2192 "
        "criteria (acceptance conditions as plain statements) \u2192 "
        "formal notation (non-executable specification \u2014 contracts with pre/post "
        "conditions, schemas with explicit invariants, or pseudocode with behavioral "
        "constraints stated; must satisfy R2 \u2014 artifact cannot be run as written) \u2192 "
        "executable validation (a file artifact invocable by an automated tool \u2014 "
        "go test, pytest, or equivalent \u2014 written to target the declared gap; "
        "only validation artifacts may be produced at this rung \u2014 "
        "implementation code is not permitted at this rung even though artifact-writing is permitted; "
        "file reads, grep output, and manual inspection do not constitute executable validation "
        "regardless of label; pre-existing artifacts not targeting the gap do not satisfy this rung) \u2192 "
        "validation run observation \u2192 "
        "executable implementation \u2192 "
        "observed running behavior."
    ),
    "gate_validity": (
        "A gate is a conversation-state condition: open when and only when the required event "
        "has occurred in this conversation for this thread. "
        "Prior knowledge, anticipation, and model reasoning cannot satisfy any gate regardless of accuracy. "
        "Underlying all compliance failures is one epistemological error: substituting model knowledge "
        "for conversation events. "
        "For executable rungs, emit "
        "\U0001F534 Execution observed: [verbatim tool output \u2014 content composed without running the tool is invalid] "
        "then "
        "\U0001F534 Gap: [what the verbatim output reveals] "
        "on their own lines before any implementation artifact. "
        "No implementation artifact \u2014 including planning text, code blocks, or tool calls \u2014 "
        "may appear before valid Execution observed + Gap sentinels; "
        "if any implementation content appears without these sentinels immediately preceding it, "
        "it is invalid and must be discarded before the tool is run. "
        "Before producing implementation code, emit "
        "\U0001F7E2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001F534 Execution observed]. "
        "The quote must be verbatim from the \U0001F534 Execution observed sentinel of this thread; "
        "quoting anticipated output or a prior thread's observation is invalid. "
        "The \U0001F534 sentinel format is reserved exclusively for executable rung gates. "
        "For non-executable rungs, observation appears inline as labeled prose. "
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
