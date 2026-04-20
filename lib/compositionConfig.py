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
            "ground + gate: the intent of this combination is that every behavior is governed "
            "by an assertion — meaning the behavior cannot regress without a test automatically "
            "detecting it. Producing passing tests that happen to exist alongside the "
            "implementation does not satisfy this intent; the tests must structurally enforce "
            "the behavior. Everything that follows derives from that intent. Gate's principle "
            "is a required constraint on whatever enforcement process ground derives — any "
            "process that permits behavior without a verified assertion violates gate regardless "
            "of how ground frames it. Ground's derivation must satisfy gate; gate's principle "
            "is not optional within ground's scope. "
            "Additionally, during ground's completion check, each assertion must have a "
            "correlated FAIL artifact in the transcript — evidence that the assertion would "
            "detect a regression in the behavior it governs. The check for each assertion is: "
            "does a correlated FAIL artifact already exist in the transcript for this assertion? "
            "If yes — the adversarial check is satisfied; do not re-perturb. If no — produce "
            "that evidence now by any means that generates a correlated FAIL (perturbation is "
            "the standard method; any approach that produces a FAIL traceable to the governed "
            "behavior is valid). A passing-tests run without correlated FAIL artifacts in the "
            "transcript is not an adversarial check — it establishes consistency between the "
            "behavior and its tests, not that the tests govern the behavior. Self-assessed "
            "certainty ('I am confident this would catch a regression') does not substitute "
            "for a FAIL artifact — the artifact is the evidence; the assessment is not."
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
            "gate + chain: the FAIL tool result produced by gate's Phase 2 perturbation is "
            "the chain predecessor for the implementation step that makes that assertion pass. "
            "An implementation step's correctness criterion is: change the system from the "
            "observed wrong state to the correct state. The wrong state is only defined by "
            "observing the perturbation FAIL output — without that observation, the correctness "
            "criterion is undefined. Chain requires every step to reproduce its predecessor's "
            "actual output before proceeding, because the step's reasoning must be anchored to "
            "what was actually observed. The agent derives from this that implementation is not "
            "merely prohibited before the FAIL artifact exists — it is undefined. A step cannot "
            "be anchored to a predecessor that has not been produced; proceeding requires "
            "fabricating the predecessor, and fabrication is not reproduction regardless of "
            "whether the fabricated content is plausible. "
            "Note: classification and derivation steps are not implementation steps and are "
            "not governed by this rule."
        ),
    },
    {
        "name": "atomic+ground",
        "tokens": ["atomic", "ground"],
        "prose": (
            "atomic + ground: exhausting the governing artifact's failures is necessary but "
            "not sufficient for completion. When the artifact reports no failures, ground's "
            "completion check is still required — return to the original stated intent and "
            "produce visible evidence for each item. Declaring done before the completion "
            "check is a violation. "
            "When all four tokens ground/gate/atomic/chain are co-present, each token's rules "
            "operate at a different level of abstraction: ground governs the task process as a "
            "whole, gate governs what must exist before each step begins, atomic governs the "
            "scope of each step, and chain governs continuity between steps. They do not "
            "conflict — violations at one level are independent of the others."
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
    {
        "name": "mint+root",
        "tokens": ["mint", "root"],
        "prose": (
            "mint + root: the generative model mint constructs must itself be root-compliant — "
            "there may be only one canonical generative structure for each domain under analysis. "
            "mint requires that generative assumptions be made explicit and conclusions follow as "
            "direct products; root requires that each proposition have a single authoritative "
            "locus with no unresolved parallel accounts. Together: constructing two independent "
            "generative models for the same phenomenon and deriving from both is a violation — "
            "the generative layer is not exempt from root's single-source requirement. Multiple "
            "structural models must be unified into one, or their dependency relationship must be "
            "made explicit before either is used as a generative basis."
        ),
    },
    {
        "name": "ground+gate+atomic+chain",
        "tokens": ["ground", "gate", "atomic", "chain"],
        "prose": (
            "ground + gate + atomic + chain (multi-layer work): the protocol's ordering "
            "constraint applies within each branch of the dependency structure, not across "
            "independent branches — layers sharing an upstream dependency can proceed in "
            "parallel once that dependency satisfies its assertions. When asserting layer "
            "boundaries, structural impossibility (the assertion cannot be written) and "
            "pressure to stop early (a high-quality intermediate creates a false sense of "
            "completion) are distinct failure modes with different causes; they are not "
            "resolved by the same intervention."
        ),
    },
]


__all__ = ["COMPOSITIONS"]
