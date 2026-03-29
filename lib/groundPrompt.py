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
    "v_complete": "\u2705 Validation artifact V complete",
    "thread_complete": "\u2705 Thread N complete",
    "manifest_exhausted": "\u2705 Manifest exhausted \u2014 N/N threads complete",
    "carry_forward": "Carry-forward: [list which original failures cover which current tests]",
    "i_formation": "\u2705 I-formation complete",
    "r2_audit": "\u2705 Formal notation R2 audit complete \u2014 N/N criteria encoded",
}


def _sentinel_block() -> str:
    lines = "; ".join(SENTINEL_TEMPLATES.values())
    return "Sentinel formats \u2014 " + lines + "."


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
        "the change must be visible through actual traces \u2014 raw output from tool execution, not descriptions of what the output means. "
        "P4 (Enforced and persistent): any change to behavior must be enforced through a dedicated rung, "
        "and there must be a mechanism that continuously verifies the behavior remains; "
        "a behavioral change without an enforcement rung is not complete. "
        "P5 (Automation quality verified): any automation that enforces behavior must itself be verified by observing it in a failing state "
        "before a passing state; automation that has never been observed to fail provides no evidential guarantee; "
        "static analysis, type checking, and linting do not satisfy this \u2014 the automation must have run and failed. "
        "P6 (Artifact type discipline): executable artifacts may only be changed at a dedicated rung for that artifact type; "
        "a rung that produces artifacts of more than one type is a protocol violation \u2014 each artifact type has exactly one rung. "
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
        "descending without a declared slice is a protocol violation. "
        "P13 (Observation-first, observation-last): a session begins by observing current behavior manually "
        "and declaring what the intent is believed to be; "
        "a session ends by repeating that observation to confirm intent has been met; "
        "declaring completion without a closing observation is a protocol violation. "
        "P14 (Evidential authority): only tool-executed events have evidential standing; "
        "inference, prediction, prior-cycle output, and model-generated descriptions of tool output have none, regardless of accuracy; "
        "a rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript "
        "whose output is of that rung\u2019s artifact type. "
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
        "P18 (Continuous descent): once descent begins, all rung transitions are continuous within the same response "
        "unless the derived ladder specifies a protocol-defined stop at that rung; "
        "pausing between rungs for user confirmation is a protocol violation; "
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
        "descent begins immediately after the table is produced without pausing for confirmation. "
        "For software behavioral change, the standard derivation produces: "
        "prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 validation run observation \u2192 executable implementation \u2192 observed running behavior. "
        "A derived ladder that omits any of these rungs for a software behavioral change task must cite which principle makes that rung unnecessary. "
        + _sentinel_block()
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
