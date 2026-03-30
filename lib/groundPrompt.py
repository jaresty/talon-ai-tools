"""Ground method prompt — structured parts (ADR-0217).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0217: generative ladder — 19 principles replace the fixed rung enumeration.
The model derives its own rung table from the principles on each session.
"""

# Canonical sentinel format strings — SSOT for all format literals used in sentinel_rules.
# Each value is the exact text the model must emit; keys are reference names used in prose.
SENTINEL_TEMPLATES: dict[str, str] = {
    "ground_entered": "\u2705 Ground entered \u2014 prose rung begins",
    "manifest_declared": "\u2705 Manifest declared \u2014 N threads: [numbered list of behavioral gaps]",
    "exec_observed": "\U0001f534 Execution observed: [verbatim tool output \u2014 triple-backtick delimited, complete, nothing omitted]",
    "gap": "\U0001f534 Gap: [what the verbatim output reveals]",
    "hard_stop": "\U0001f6d1 HARD STOP \u2014 upward return to criteria rung",
    "impl_gate": "\U0001f7e2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001f534 Execution observed]",
    "criteria_complete": "\u2705 Criteria complete \u2014 1 criterion: [gap-name]",
    "v_complete": "\u2705 Validation artifact V complete",
    "thread_complete": "\u2705 Thread N complete",
    "manifest_exhausted": "\u2705 Manifest exhausted \u2014 N/N threads complete",
    "carry_forward": "Carry-forward: [list which original failures cover which current tests]",
    "i_formation": "\u2705 I-formation complete",
    "r2_audit": "\u2705 Formal notation R2 audit complete \u2014 N/N criteria encoded",
}

# Per-sentinel gate conditions — emitted inline in the sentinel block so the gate
# requirement is visible at the exact point of emission.
_SENTINEL_GATES: dict[str, str] = {
    "ground_entered": "gate: first token after user invokes ground",
    "manifest_declared": "gate: rung table produced in current response; rung table precedes this sentinel",
    "exec_observed": "gate: tool call made in the current response immediately before this sentinel; verbatim output in triple-backtick block follows",
    "gap": "gate: exec_observed with non-empty failing output precedes this token in current response; gap text is a currently-false behavioral assertion",
    "hard_stop": "gate: exec_observed + gap at VRO rung in current cycle; criterion identical to prior cycle criterion for this thread",
    "impl_gate": "gate: exec_observed + gap at VRO rung in current cycle; valid only at the EI rung",
    "criteria_complete": "gate: exactly one criterion in this rung's artifact; criterion contains no conjunction; formal notation rung label may not be emitted until this sentinel has been emitted",
    "v_complete": "gate: test file written via tool call in current response; pre-existence check tool call result present",
    "thread_complete": "gate: OBR exec_observed directly demonstrating criterion in current cycle; passing test suite run after OBR tool call; valid only at OBR rung",
    "manifest_exhausted": "gate: count of Thread N complete sentinels equals N in Manifest declared",
    "carry_forward": "gate: prior failure name quotable verbatim from a prior exec_observed sentinel",
    "i_formation": "gate: observation of current state complete before manifest",
    "r2_audit": "gate: every criterion encoded in notation; audit section named and separate",
}


def _sentinel_block() -> str:
    entries = []
    for key, fmt in SENTINEL_TEMPLATES.items():
        gate = _SENTINEL_GATES.get(key, "")
        entries.append(f"{fmt} [{gate}]" if gate else fmt)
    return "Sentinel formats \u2014 " + "; ".join(entries) + "."


GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        "This protocol exists because a model\u2019s description of completed work is indistinguishable from actually completing it \u2014 "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "P1 (Intent primacy): intent exists; everything produced in a session is derivative of that intent; "
        "whenever new information changes the understanding of intent, every rung whose definition has changed must be refined "
        "starting with the highest affected rung and propagating downward; "
        "completed rungs may not be re-opened except by this mechanism. "
        "P2 (Behavioral change isolation): any change to behavior may only be made at a dedicated rung; "
        "no rung may produce a behavioral change as a side effect of another rung\u2019s artifact; "
        "a rung that changes behavior and also changes another artifact type is a protocol violation \u2014 split into separate rungs. "
        "P3 (Observable evidence required): any change to behavior must be observed in both its pre-change (absent/failing) state "
        "and its post-change (present/passing) state; "
        "the change must be visible through actual traces \u2014 raw output from tool execution, not descriptions of what the output means; "
        "the observation must directly demonstrate the behavior named in the criterion for the current cycle \u2014 "
        "infrastructure evidence (server liveness, process start, HTTP 200 from a root route) "
        "does not satisfy P3 unless the criterion explicitly asserts infrastructure state. "
        "P4 (Enforced and persistent): any change to behavior must be enforced through a dedicated rung, "
        "and there must be a mechanism that continuously verifies the behavior remains; "
        "a behavioral change without an enforcement rung is not complete. "
        "P5 (Automation quality verified): any automation that enforces behavior must be an artifact invocable by an automated tool "
        "and must itself be verified by observing it in a failing state before a passing state; "
        "automation that has never been observed to fail provides no evidential guarantee; "
        "static analysis, type checking, and linting do not satisfy this \u2014 the automation must have run and failed; "
        "\u201crun and failed\u201d means a tool call invoking the automation appears in the current-cycle transcript "
        "and its verbatim output shows failure \u2014 "
        "a model\u2019s prose description of why the automation would fail does not satisfy this principle regardless of accuracy. "
        "P6 (Artifact type discipline): executable artifacts may only be changed at a dedicated rung for that artifact type; "
        "a rung that produces artifacts of more than one type is a protocol violation \u2014 each artifact type has exactly one rung; "
        "each protocol sentinel has an artifact type determined by the rung at which it was defined \u2014 "
        "emitting a sentinel outside its defining rung is a type-discipline violation; "
        "the sentinel is void and the rung in which it appears is voided by the cross-type emission. "
        "P7 (Upward faithfulness): any artifact at any rung must be faithful to the rung above it; "
        "the space of valid implementations permitted by a lower rung may only be equal to or smaller than the space permitted by the rung above it; "
        "expanding the permitted space is a faithfulness violation; tool execution at any rung is permitted. "
        "P8 (Rung validity test): a rung is valid if and only if a human reviewer, given only that rung\u2019s artifact and no other context, "
        "can determine whether the next rung\u2019s artifact is faithful to the intent without consulting any prior rung; "
        "a rung that fails this test is narration, not a rung; "
        "the ladder must be minimal \u2014 removing any rung must leave some faithfulness evaluation impossible without consulting prior rungs; "
        "a rung that can be removed without loss must be removed. "
        "P9 (Information density preservation): each rung must encode the same or higher quality of information as the rung above it \u2014 "
        "sufficient to represent the intent as fully as possible in its artifact type; "
        "a rung whose artifact loses information present in the rung above it is a protocol violation. "
        "P10 (Three-part completeness): a session is complete only when it has produced: "
        "(a) a manual observation confirming the behavior is present, "
        "(b) automation that verifies the behavior is consistently maintained, "
        "and (c) for behavior-change sessions, an artifact that directly implements the change; all three must be present. "
        "P11 (Immediate lowest-rung observation): whenever a behavioral change is made that would be visible at a higher rung, "
        "it must be observed immediately at the lowest rung that allows observation of that change; "
        "deferring observation to a higher rung when a lower rung could have surfaced it first is a protocol violation. "
        "P12 (Completeness slice): after declaring intent, a slice of behavior is chosen to carry through the ladder; "
        "the slice must be declared explicitly before descent begins; "
        "descending without a declared slice is a protocol violation; "
        "the slice is exactly one independently testable behavior per thread per cycle \u2014 "
        "a criteria artifact asserting more than one behavior is a conjunction and is a protocol violation; "
        "a criterion containing the word \u201cand\u201d is presumptively a conjunction unless both halves jointly constitute "
        "a single indivisible observable state. "
        "P13 (Observation-first, observation-last): a session begins by observing current behavior manually "
        "and declaring what the intent is believed to be; "
        "a session ends by repeating that observation to confirm intent has been met; "
        "declaring completion without a closing observation is a protocol violation. "
        "P14 (Evidential authority): only tool-executed events have evidential standing; "
        "inference, prediction, prior-cycle output, and model-generated descriptions of tool output have none, regardless of accuracy; "
        "a rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript "
        "whose output is of that rung\u2019s artifact type; "
        "a rung gate is not a description of evidence \u2014 it is a blocker: "
        "no completion sentinel for that rung and no label for the subsequent rung may appear "
        "while the gate is unsatisfied; "
        "before emitting a completion sentinel or the next rung label, verify the gate condition is met \u2014 "
        "emitting either before the gate condition is met is a protocol violation that voids the rung; "
        "\U0001f534 Execution observed: is only valid when a tool call was made in the current response immediately before it \u2014 "
        "a sentinel emitted without a preceding tool call is a fabrication \u2014 it voids the rung in which it appears "
        "regardless of whether its text resembles tool output. "
        "P15 (Cycle identity): evidence is valid only within the cycle in which it was produced; "
        "a cycle opens at the prose rung emission for a given thread and closes at Thread N complete or an upward return; "
        "evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate in the current cycle "
        "regardless of type match; "
        "prose re-emission for one thread does not affect the cycle identity of any other thread. "
        "P16 (Provenance): a gate is satisfied only by a tool call made in direct response to the gap declared at the immediately prior rung "
        "in the current cycle; a tool call made for a different purpose, targeting a different gap, or produced in a prior cycle "
        "does not satisfy any gate regardless of type match. "
        "P17 (Derivation chain): each artifact must be derived from the prior rung\u2019s actual content \u2014 "
        "not from the original intent reconstructed from memory; "
        "a skipped rung voids all artifacts below it; "
        "form changes between rungs, intent does not; "
        "divergence from intent is only detectable at the rung where the prior artifact\u2019s specificity was insufficient \u2014 "
        "breaking the chain makes that detection impossible. "
        "P18 (Continuous descent): once descent begins, advance through every feasible rung without pausing for user confirmation; "
        "each rung may not be skipped or combined with another; "
        "all rung transitions are continuous within the same response "
        "unless the derived ladder specifies a protocol-defined stop at that rung; "
        "response length is never a valid reason to stop between rungs \u2014 "
        "if the full descent cannot fit in one response, continue from the current rung in the next response "
        "without re-emitting completed rungs. "
        "P19 (Thread sequencing): when multiple behavioral gaps are declared, they form a manifest; "
        "each gap is a thread; all rungs for Thread N must complete before any content for Thread N+1 may appear; "
        "threads not declared in the manifest may not be created mid-session; "
        "a thread is complete only when all its rungs have fired in the current cycle and a completion sentinel has been emitted. "
        "Ladder derivation rung: before descending, derive the rung table for this session by applying P1\u2013P19 to the declared intent; "
        "produce a table with columns: rung name | artifact type | gate condition (what tool-executed event satisfies the gate) | "
        "void condition (what invalidates the artifact) | faithfulness test (what a reviewer needs from only this artifact to evaluate the next rung); "
        "verify the table satisfies P8 minimality \u2014 remove any rung that does not; "
        "descent begins immediately after the table is produced without pausing for confirmation; "
        "\u2705 Manifest declared is blocked until the rung table artifact has been produced in the current response \u2014 "
        "a manifest emitted without a preceding rung table is a protocol violation; "
        "the rung table is the gate on all subsequent rung activity. "
        "For software behavioral change, the standard derivation produces: "
        "prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 validation run observation \u2192 executable implementation \u2192 observed running behavior. "
        "A derived ladder that omits any of these rungs for a software behavioral change task must cite which principle makes that rung unnecessary. "
        "Outputting a rung label is what begins that rung \u2014 it is not a heading or annotation; "
        "a rung whose label has not been output has not begun. "
        "When beginning mid-ladder, locate the highest already-instantiated rung, update it, then descend. "
        + _sentinel_block()
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
