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
            "ground + gate: gate's principle is a required constraint on whatever enforcement "
            "process ground derives — any process that permits behavior without a verified "
            "assertion violates gate regardless of how ground frames it. Ground's derivation "
            "must satisfy gate; gate's principle is not optional within ground's scope."
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
            "gate + chain: gate requires a FAIL observation per assertion before any "
            "implementation step proceeds; chain requires each implementation step reproduce "
            "its predecessor's actual output verbatim. Derive what these two requirements "
            "together demand of any step that involves test behavior — including what "
            "constitutes a valid predecessor, what the coverage table must contain, and what "
            "makes a coverage table entry a violation. The derivation must be visible. "
            "Note: derivation blocks produced by the planning directive are not implementation "
            "steps and are not governed by this rule."
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
