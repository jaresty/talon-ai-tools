# ADR-0227: Pairwise token compositions.
#
# Each composition defines prompt text injected into the COMPOSITION RULES section
# when all tokens in its set are co-present in a bar build command.
# Compositions are pairwise — each activates independently for partial combinations.

from typing import Any

COMPOSITIONS: list[dict[str, Any]] = [
    {
        "name": "ground+gate",
        "tokens": ["ground", "gate"],
        "prose": (
            "ground + gate: the enforcement process derived by ground must include "
            "assertion-before-behavior as its first step. No behavior may be produced before "
            "a governing assertion exists and has been verified to fail when the behavior is "
            "absent. This is not an additional constraint on top of ground's derivation — it "
            "is the required first rung of any enforcement process ground produces when gate governs."
        ),
    },
    {
        "name": "gate+atomic",
        "tokens": ["gate", "atomic"],
        "prose": (
            "gate + atomic: the governing output is the artifact output (failure message, "
            "compile error, test result) produced by the governing artifact that opens the "
            "current implementation step. When no governing output exists for the current "
            "behavior, the scope of the current step is undefined — the governing artifact "
            "has not been written yet. Test absence is an explicit open gap that blocks "
            "implementation; the required action is to write and run the assertion, not to "
            "proceed without one."
        ),
    },
    {
        "name": "gate+chain",
        "tokens": ["gate", "chain"],
        "prose": (
            "gate + chain: for implementation steps, the governing output is the only valid "
            "predecessor artifact. A prior implementation artifact, compile result, or prose "
            "description does not satisfy chain's reproduction requirement for an "
            "implementation step — only a reproduced governing output does."
        ),
    },
    {
        "name": "atomic+ground",
        "tokens": ["atomic", "ground"],
        "prose": (
            "atomic + ground: exhausting the governing artifact's failures is necessary but "
            "not sufficient for completion. When the artifact reports no failures, the "
            "required next step is ground's completion check — return to the original stated "
            "intent and produce visible evidence for each item. Declaring done before the "
            "completion check is a violation. "
            "When all four tokens ground/gate/atomic/chain are co-present, the dependency "
            "order is: ground (frame and close) → gate (assertion coverage) → atomic (step "
            "scope) → chain (step continuity). Each token's rules operate at a different "
            "level; they do not conflict."
        ),
    },
    {
        "name": "calc+chain",
        "tokens": ["calc", "chain"],
        "prose": (
            "calc + chain: each executable step's output must be reproduced verbatim before "
            "the next step may constrain its conclusions. calc requires that conclusions be "
            "constrained by the actual outputs of formal steps; chain requires that each step "
            "reproduce its predecessor's actual output before proceeding. Together: quoting "
            "a calculation result is not sufficient — the exact output of each step must "
            "appear in the response before the reasoning that depends on it."
        ),
    },
]


__all__ = ["COMPOSITIONS"]
