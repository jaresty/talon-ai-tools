# ADR-0227: Pairwise token compositions.
#
# Each composition defines prompt text injected into the COMPOSITION RULES section
# when all tokens in its set are co-present in a bar build command.
# Compositions are pairwise — each activates independently for partial combinations.

from typing import Any

COMPOSITIONS: list[dict[str, Any]] = [
    {
        "name": "gate+falsify",
        "tokens": ["gate", "falsify"],
        "prose": (
            "gate + falsify: when these two tokens are co-present, the objective condition that "
            "gate requires to be met before proceeding is that a falsifiable artifact satisfying "
            "falsify's criteria exists in the transcript — it has fired against the minimal wrong "
            "state and produced a visible signal. Gate provides the blocking structure; falsify "
            "specifies the evidentiary quality that satisfies it. Together they produce the "
            "discipline previously called 'TDD enforcement': no implementation step may begin "
            "until every governing assertion has been observed to fail against the specific "
            "absent behavior it governs."
        ),
    },
    {
        "name": "ground+falsify",
        "tokens": ["ground", "falsify"],
        "prose": (
            "ground + falsify: the intent of this combination is that every behavior is governed "
            "by a falsifiable artifact — meaning the behavior cannot regress without the artifact "
            "detecting it. Producing passing artifacts that happen to exist alongside the "
            "implementation does not satisfy this intent; each artifact must structurally enforce "
            "its governed behavior. Falsify's criteria are required constraints on whatever "
            "enforcement process ground derives. "
            "During ground's completion check, each assertion must have a correlated artifact-fire "
            "in the transcript — evidence that it would detect a regression. Does a correlated "
            "FAIL artifact already exist for this assertion? If yes — adversarial check satisfied; "
            "do not re-perturb. If no — produce it now. Self-assessed certainty does not substitute "
            "for a visible artifact fire — the artifact is the evidence; the assessment is not."
        ),
    },
    {
        "name": "falsify+atomic",
        "tokens": ["falsify", "atomic"],
        "prose": (
            "falsify + atomic: the governing output is the artifact-fire output (failure message, "
            "visible signal) produced by running the falsifiable artifact against the minimal wrong "
            "state. When no artifact fire exists for the current behavior, the scope of the current "
            "step is undefined — the artifact has not yet been run against the absent behavior. "
            "Artifact absence is an explicit open gap that blocks implementation; the required "
            "action is to produce the artifact fire, not to proceed without one."
        ),
    },
    {
        "name": "falsify+chain",
        "tokens": ["falsify", "chain"],
        "prose": (
            "falsify + chain: the artifact-fire tool result produced by falsify is the chain "
            "predecessor for the implementation step that makes that assertion pass. An "
            "implementation step's correctness criterion is: change the system from the observed "
            "wrong state to the correct state. The wrong state is only defined by observing the "
            "artifact-fire output — without that observation, the correctness criterion is "
            "undefined. Chain requires every step to reproduce its predecessor's actual output "
            "before proceeding. The agent derives that implementation is not merely prohibited "
            "before the artifact fire exists — it is undefined. "
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
            "completion check must be produced as a completed block before any done declaration "
            "opens — the completion check block must end before the done claim appears. "
            "When ground/gate/falsify/atomic/chain are co-present, each token operates at a "
            "different level: ground governs the task process as a whole; gate governs whether "
            "to proceed; falsify governs the evidentiary quality required to proceed; atomic "
            "governs the scope of each step; chain governs continuity between steps. They do "
            "not conflict — violations at one level are independent of the others."
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
        "name": "ground+gate+falsify+atomic+chain",
        "tokens": ["ground", "gate", "falsify", "atomic", "chain"],
        "prose": (
            "ground + gate + falsify + atomic + chain (multi-layer work): ground's first "
            "artifact is a dependency graph that partitions the work into independent branches — "
            "two branches are independent if neither's first step depends on any node in the "
            "other. Each node carries an explicit predecessor/successor contract. This graph "
            "is required before any branch begins. The protocol's ordering constraint applies "
            "within each branch, not across independent branches. Once a shared upstream "
            "dependency satisfies its assertions, independent branches must be executed as "
            "parallel subagent invocations; parallel execution is available if and only if "
            "the execution context supports simultaneous tool calls — if not, name the specific "
            "tool or context property that is absent before proceeding sequentially; a statement "
            "of unavailability without a named absent property does not satisfy this condition. "
            "Each subagent runs "
            "gate+falsify+atomic+chain on its assigned branch; ground is the orchestrating "
            "protocol and its dependency graph is not re-derived within a branch. When "
            "asserting layer boundaries, structural impossibility (the assertion cannot be "
            "written) and pressure to stop early (a high-quality intermediate creates a "
            "false sense of completion) are distinct failure modes with different causes; "
            "they are not resolved by the same intervention."
        ),
    },
]


__all__ = ["COMPOSITIONS"]
