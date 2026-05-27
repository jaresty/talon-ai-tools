# ADR-0227: Pairwise token compositions — application-time behavioral rules.
#
# PURPOSE: These entries govern how the LLM behaves when tokens are *already co-present*
# in a bar build command. They are injected into the COMPOSITION RULES section of the
# prompt at runtime. They are NOT for discovery (use guidebookConfig.py for that).
#
# Discovery layer (token selection guidance): guidebookConfig.py → `bar guide <token>`
# Application layer (co-presence resolution):  this file → injected into COMPOSITION RULES
#
# Each entry answers: "given these tokens are already selected, how should the LLM
# resolve their interaction?" Entries typically cover:
#   - Precedence (one token takes priority over another)
#   - Sequencing (apply one before the other)
#   - Scope restriction (token A applies everywhere except where token B governs)
#
# Compositions are pairwise — each activates independently for partial combinations.

from typing import Any

COMPOSITIONS: list[dict[str, Any]] = [
    {
        "name": "gate+falsify",
        "tokens": ["gate", "falsify"],
        "prose": (
            "gate + falsify: the blocking condition gate requires is that a FAIL satisfying "
            "falsify's validity criteria exists in the transcript — a tool-result block appearing "
            "above the current position whose output names the assertion text that fires on the "
            "absent behavior, names at least one other assertion as passing, and whose triggering "
            "event is established by a quoted string from a prior tool-result block showing both "
            "the artifact and the changed file were invoked by that event. No file-modifying tool "
            "call is permitted until such a tool-result block appears above it in the transcript."
        ),
    },
    {
        "name": "ground+falsify",
        "tokens": ["ground", "falsify"],
        "prose": (
            "ground + falsify: every behavior governed by ground's enforcement process must be "
            "governed by a falsifiable artifact satisfying falsify's validity criteria — meaning "
            "the behavior cannot regress without the artifact detecting it. Producing passing "
            "artifacts that happen to exist alongside the implementation does not satisfy this "
            "requirement; each artifact must have fired against the absent behavior. During "
            "ground's completion check, each governed behavior must have a correlated tool-result "
            "block in the transcript showing the artifact fired against the absent behavior — "
            "self-assessed certainty does not substitute for a visible tool-result block. For each "
            "governed behavior, the completion check must locate a tool-result block in the "
            "transcript whose output contains the assertion text that fires on the absent behavior "
            "as a FAIL string; if none exists, that behavior is a gap and the completion check "
            "must not close until such a tool-result block appears."
        ),
    },
    {
        "name": "gate+atomic",
        "tokens": ["gate", "atomic"],
        "prose": (
            "gate + atomic: gate's blocking condition applies to every file-modifying tool call, "
            "including stub additions. Each file-modifying tool call must be immediately preceded "
            "by a tool-result block whose output contains the name of the function or symbol that "
            "tool call adds or modifies; a tool-result block that does not name that symbol does "
            "not gate that tool call. A Symbols list with more than one entry — where the Symbols "
            "list is the string appearing between 'Symbols:' and 'Lines:' in the pre-edit line — "
            "requires a separate Scope line and separate tool call for each entry."
        ),
    },
    {
        "name": "falsify+atomic",
        "tokens": ["falsify", "atomic"],
        "prose": (
            "falsify + atomic: when this composition rule is active, the pre-edit line required by "
            "atomic gains one additional field: 'Governing artifact: <verbatim FAIL output from "
            "falsify's verification phase>' — this field must appear in the pre-edit line and must "
            "quote verbatim the FAIL output produced by falsify's candidate-check run appearing "
            "above this line in the transcript; a pre-edit line missing this field does not satisfy "
            "atomic's requirement. Additionally, before each file-modifying tool call, produce a "
            "minimal-state declaration naming: the specific behavior being removed, and at least "
            "one other behavior that is present and unchanged in the test state — the "
            "minimal-state declaration is not complete until both items appear in the transcript "
            "above the tool call; if a tool-executed FAIL result shows the same failure with less "
            "than the named behavior removed, the named behavior is not the sole governed cause "
            "and must be rederived. The governing artifact must be run such that the scope text "
            "appears as a line in the tool-result block; a run command whose output does not "
            "contain the scope text as a line does not satisfy this requirement — use the same "
            "command for both pre-edit and post-edit runs."
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
            "atomic + ground: ground's completion check is not permitted to open until a "
            "tool-result block showing zero items in the run result appears above it in the "
            "transcript; the completion check block must end before any done declaration opens. "
            "Satisfying atomic's requirements does not exempt ground's requirements; satisfying "
            "ground's requirements does not exempt atomic's requirements — each applies "
            "independently. Adversarial completion check: treat each distinct file-modifying tool "
            "call as one step. For each step, the completion check must locate a tool-result block "
            "appearing in the transcript at that step's position that shows exactly one "
            "independently testable change — where independently testable means a separate named "
            "test or observable can detect one change while being blind to the other. If no such "
            "tool-result block exists, or if it shows more than one independently testable change, "
            "that step is a gap requiring re-execution as separate tool calls before the "
            "completion check may close."
        ),
    },
    {
        "name": "skim+gate",
        "tokens": ["skim", "gate"],
        "prose": (
            "skim + gate: gate's hard-blocking precision requirement takes precedence over skim's "
            "brevity constraint at every gate condition. The gate condition itself must be stated "
            "fully — naming the specific string or structural property whose presence constitutes "
            "satisfaction — regardless of skim's light-pass instruction. Skim governs all content "
            "outside the gate conditions; within a gate condition, skim does not apply. A gate "
            "condition expressed as a vague summary rather than a named observable property does "
            "not satisfy gate's requirement even when skim is present."
        ),
    },
    {
        "name": "blind+skim",
        "tokens": ["blind", "skim"],
        "prose": (
            "blind + skim: assumption and constraint reconstruction — which blind requires before "
            "any conclusion that depends on prior context — is compressed to one-line headers "
            "rather than full blocks. Each header names the assumption or constraint explicitly "
            "so the conclusion can be traced to it, but elaboration is suppressed. Conclusions "
            "still name their dependency by reference to the header; a conclusion that omits this "
            "reference does not satisfy blind's requirement regardless of skim's brevity instruction."
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
        "name": "variants+adversarial",
        "tokens": ["variants", "adversarial"],
        "prose": (
            "variants + adversarial: each variant must include its primary failure mode "
            "co-located within that variant's block — a failure mode appearing in a "
            "separate section rather than inside the variant it governs does not satisfy "
            "this requirement. The failure mode must name the specific flaw type "
            "(edge case, unstated assumption, architectural brittleness, etc.) and at "
            "least one concrete instance of that type found in the variant. A variant "
            "block without a co-located failure mode is incomplete regardless of whether "
            "adversarial's global failure-category requirement is otherwise met."
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
    {
        "name": "prep+svg",
        "tokens": ["prep", "svg"],
        "prose": (
            "prep + svg: prep form requires rich prose blocks — hypothesis, method, "
            "expected outcomes, evaluation criteria. svg is markup-only with no prose "
            "slot. The structured write-up prep requires has no valid rendering target "
            "inside svg. Same mechanism as ghost+svg and twin+svg: the form demands "
            "prose structure the channel structurally cannot hold. When prep and svg "
            "appear together, the prep write-up must appear as a prose block before "
            "or after the svg artifact."
        ),
    },
    {
        "name": "ghost+svg",
        "tokens": ["ghost", "svg"],
        "prose": (
            "ghost + svg: ghost produces a step-by-step execution trace in prose — "
            "each step names what was done and what result was produced. svg is a "
            "markup-only channel with no prose slot. The trace narrative ghost requires "
            "has nowhere to render in svg. When ghost and svg appear together, the "
            "ghost trace must appear as a separate prose block before the svg artifact; "
            "embedding trace commentary inside svg markup does not satisfy ghost's "
            "requirement for a readable execution narrative."
        ),
    },
    {
        "name": "twin+svg",
        "tokens": ["twin", "svg"],
        "prose": (
            "twin + svg: twin form produces a two-column parallel prose comparison — "
            "each column runs a distinct analytical lens on the same subject. svg is "
            "markup-only with no prose slot for column content. The prose comparison "
            "twin requires has no valid rendering target inside svg. Same mechanism as "
            "ghost+svg: the form demands prose structure that the channel structurally "
            "cannot hold. When twin and svg appear together, the twin comparison must "
            "appear as a prose block before or after the svg artifact."
        ),
    },
    {
        "name": "probe+falsify",
        "tokens": ["probe", "falsify"],
        "prose": (
            "probe + falsify: falsify requires an implementation artifact to precede it — "
            "the artifact must fire against the absent behavior (FAIL) before any "
            "implementation step. probe produces understanding, not an implementation "
            "artifact. There is no implementation step for falsify to gate before. When "
            "probe and falsify appear together, falsify applies only if the probe output "
            "leads to an implementation step within the same response; if the response "
            "is analysis only, falsify has no target and is silently inapplicable."
        ),
    },
    {
        "name": "pick+indirect",
        "tokens": ["pick", "indirect"],
        "prose": (
            "pick + indirect: pick requires an explicit committed selection — the LLM names "
            "one option and commits to it. indirect withholds direct statement, hinting rather "
            "than declaring. These conflict: a token that selects one option cannot "
            "simultaneously decline to state it. Resolution: pick takes precedence — the "
            "selection must be named explicitly. indirect may govern surrounding framing "
            "(context, caveats, approach) but not the selection itself. A response that "
            "hints at a selection without naming it does not satisfy pick."
        ),
    },
    {
        "name": "pick+cocreate",
        "tokens": ["pick", "cocreate"],
        "prose": (
            "pick + cocreate: cocreate scaffolds an open-ended iterative co-creation "
            "process; pick commits to one final answer. These are in mild tension: the "
            "co-creation form implies ongoing iteration and dialogue, while pick asks for "
            "a committed selection. Resolution: structure the cocreate scaffold toward a "
            "decision point — the collaborative process converges to the pick output rather "
            "than remaining open-ended. The final cocreate turn must name the picked option "
            "explicitly. A cocreate scaffold that never commits to a selection does not "
            "satisfy pick."
        ),
    },
    {
        "name": "reset+good",
        "tokens": ["reset", "good"],
        "prose": (
            "reset + good: reset clears state and starts fresh, discarding prior context; "
            "good reinforces what is already working, building on existing strengths. These "
            "operate in opposite directions on the same material — you cannot simultaneously "
            "clear and reinforce. Resolution: treat them as sequential rather than "
            "simultaneous — good identifies what to preserve before reset clears everything "
            "else. The response must name what is being preserved (good) before naming what "
            "is being cleared (reset); a response that resets without first identifying "
            "preserved strengths does not satisfy good."
        ),
    },
]


__all__ = ["COMPOSITIONS"]
