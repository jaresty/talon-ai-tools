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
    "ground_complete": "\u2705 Ground complete \u2014 intent achieved: [what the observation shows]",
    "closing_observation": "\U0001f535 Closing observation \u2014 [what the tool-executed observation shows]",
    "write_authorized": "\U0001f535 Write authorized \u2014 rung: [rung name] | artifact type: [type] | file: [path]",
}

# Per-sentinel gate conditions — emitted inline in the sentinel block so the gate
# requirement is visible at the exact point of emission.
_SENTINEL_GATES: dict[str, str] = {
    "ground_entered": "gate: first content emitted in this response; no artifact, code, prose, or reasoning may precede this sentinel — preceding content voids the session",
    "manifest_declared": "gate: rung table produced in current response; rung table precedes this sentinel",
    "exec_observed": "gate: tool call made in the current response immediately before this sentinel; verbatim output in triple-backtick block follows",
    "gap": "gate: exec_observed with non-empty failing output precedes this token in current response; gap text is a currently-false behavioral assertion",
    "hard_stop": "gate: exec_observed showing test suite failure + gap in current cycle; criterion identical to prior cycle criterion for this thread",
    "impl_gate": "gate: exec_observed showing test suite failure + gap in current cycle; valid only at the rung whose artifact type is executable implementation; the verbatim exec_observed output must contain at least one assertion-level failure string (e.g. 'Expected … Received …', 'AssertionError', 'FAILED', specific test name + failure reason) — an exec_observed whose output shows only infrastructure failure, import error, process crash, or a model-described summary of failure does not satisfy this gate; if the suite cannot reach assertions, the implementation artifact for that cycle resolves only the infrastructure gap, and this gate cannot be emitted until a subsequent cycle produces assertion-level failure output",
    "criteria_complete": "gate: exactly one criterion in this rung's artifact; criterion contains no conjunction; formal notation rung label may not be emitted until this sentinel has been emitted",
    "v_complete": "gate: pre-existence check tool call result present; tool call in this response wrote the file to disk",
    "thread_complete": "gate: meta exec_observed after executable implementation shows the gap declared for this thread is no longer present in running behavior",
    "manifest_exhausted": "gate: count of Thread N complete sentinels equals N in Manifest declared",
    "carry_forward": "gate: prior failure name quotable verbatim from a prior exec_observed sentinel",
    "i_formation": "gate: observation of current state complete before manifest",
    "r2_audit": "gate: every criterion encoded in notation; audit section named and separate",
    "ground_complete": "gate: \U0001f535 Closing observation must appear in the current response before this sentinel; meta exec_observed shows no gap between observed running behavior and declared intent; all manifest threads complete",
    "closing_observation": "gate: the tool call immediately before this sentinel must directly invoke the behavior named in the session intent and its output must show that behavior is present; this sentinel must appear after \u2705 Manifest exhausted and before \u2705 Ground complete in the same response; emitting \u2705 Ground complete without a preceding \U0001f535 Closing observation in the current response is a protocol violation",
    "write_authorized": "gate: currently open rung (most recently emitted rung label with no completion sentinel yet) has this file's artifact type in its permitted-tool-calls column; no open rung → gate unsatisfied; artifact type mismatch → gate unsatisfied; the cited artifact type must match the artifact type of the named file as determined by the rung table's artifact-type column — a cited artifact type that does not match the file being written is a fabrication that voids the sentinel and the rung regardless of whether the open rung permits that type; a file write without a preceding \U0001f535 Write authorized voids the write and the rung in which it appears; a \U0001f535 Write authorized whose cited rung is not currently open is a fabrication that voids the write and the rung; this sentinel must appear immediately before the file-write tool call — intervening content between this sentinel and the tool call voids both",
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
        "a model\u2019s prose description of why the automation would fail does not satisfy this principle regardless of accuracy; "
        "the observation of failing state is produced by running the automation immediately after writing it \u2014 "
        "it is part of the verification artifact, not a separate rung; "
        "a reviewer cannot determine from the test file alone what the implementation must do \u2014 "
        "the failure output is required for the verification artifact to satisfy P8. "
        "P6 (Artifact type discipline): executable artifacts may only be changed at a dedicated rung for that artifact type; "
        "a rung that produces artifacts of more than one type is a protocol violation \u2014 each artifact type has exactly one rung; "
        "each protocol sentinel has an artifact type determined by the rung at which it was defined \u2014 "
        "emitting a sentinel outside its defining rung is a type-discipline violation; "
        "the sentinel is void and the rung in which it appears is voided by the cross-type emission; "
        "once a rung\u2019s completion sentinel has been emitted, the artifact type produced at that rung is frozen for the current thread and cycle \u2014 "
        "modifying a frozen artifact at any subsequent rung is a type-discipline violation that voids the rung in which the modification appears; "
        "text artifact types (prose, criteria, formal notation) produce response content only \u2014 they have no file representation; "
        "writing any file to disk during a text-artifact rung is a type-discipline violation regardless of what the rung table\u2019s permitted-tool-calls column says. "
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
        "a single indivisible observable state; "
        "a criterion is a falsifiable behavioral assertion \u2014 given a specific action, a specific observable outcome either occurs or it does not; "
        "a feature name or capability description is not a criterion \u2014 it cannot be directly observed to pass or fail. "
        "P13 (Observation-first, observation-last): a session begins by observing current behavior manually "
        "and declaring what the intent is believed to be; "
        "a session ends by repeating that observation to confirm intent has been met; "
        "declaring completion without a closing observation is a protocol violation; "
        "the opening observation must be tool-executed \u2014 "
        "the intent declaration must be derivable from that tool-executed output; "
        "intent declared without a tool-executed opening observation is an evidential violation under P14. "
        "P14 (Evidential authority): only tool-executed events have evidential standing; "
        "inference, prediction, prior-cycle output, and model-generated descriptions of tool output have none, regardless of accuracy; "
        "a rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript "
        "whose output is of that rung\u2019s artifact type; "
        "a rung gate is not a description of evidence \u2014 it is a blocker: "
        "no completion sentinel for that rung and no label for the subsequent rung may appear "
        "while the gate is unsatisfied; "
        "before emitting a completion sentinel or the next rung label, verify the gate condition is met \u2014 "
        "emitting either before the gate condition is met is a protocol violation that voids the rung; "
        "a completion sentinel is a closing marker \u2014 it appears after the rung\u2019s artifact is complete and its gate condition is verified; "
        "emitting a completion sentinel before the artifact it closes is a protocol violation that voids both the sentinel and the rung; "
        "after a rung label is emitted, the only valid content before the completion sentinel is the rung\u2019s artifact \u2014 "
        "prose commentary, planning text, debugging narration, and content of any other artifact type "
        "between the rung label and its completion sentinel is a protocol violation that voids the rung; "
        "\U0001f534 Execution observed: is only valid when a tool call was made in the current response immediately before it \u2014 "
        "a sentinel emitted without a preceding tool call is a fabrication \u2014 it voids the rung in which it appears "
        "regardless of whether its text resembles tool output; "
        "\u2705 Ground entered must be the first emitted content of any response that begins a ground session \u2014 "
        "any artifact, reasoning, or content of any type produced before \u2705 Ground entered is a pre-entry violation \u2014 "
        "it voids the sentinel and all work that follows in that response. "
        "P15 (Cycle identity): evidence is valid only within the cycle in which it was produced; "
        "a cycle opens when \u2705 Ground entered is emitted for a given thread and closes at Thread N complete or an upward return; "
        "evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate in the current cycle "
        "regardless of type match; "
        "re-emitting \u2705 Ground entered for one thread does not affect the cycle identity of any other thread; "
        "an upward return is valid only when a prior cycle for the current thread exists in the current session \u2014 "
        "a comparison gate requires a prior cycle artifact to compare against; "
        "invoking an upward return in a thread\u2019s first cycle is a protocol violation. "
        "P16 (Provenance): a gate is satisfied only by a tool call made in direct response to the gap declared at the immediately prior rung "
        "in the current cycle; a tool call made for a different purpose, targeting a different gap, or produced in a prior cycle "
        "does not satisfy any gate regardless of type match. "
        "P17 (Derivation chain): each artifact must be derived from the prior rung\u2019s actual content \u2014 "
        "not from the original intent reconstructed from memory; "
        "a skipped rung voids all artifacts below it; "
        "form changes between rungs, intent does not; "
        "divergence from intent is only detectable at the rung where the prior artifact\u2019s specificity was insufficient \u2014 "
        "breaking the chain makes that detection impossible; "
        "an artifact at any rung addresses only the gap declared by the prior rung \u2014 scope does not expand between rungs; "
        "an artifact that addresses behaviors beyond the declared gap is a derivation violation that voids the rung; "
        "an artifact may not retrieve specificity from a rung above its immediate predecessor \u2014 "
        "if a lower rung requires more specificity than the rung above it provides, the remedy is an upward return to that rung, not retrieval from a higher rung. "
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
        "P21 (Upward return): a rung may be returned to and revised at any point during descent if a derivation error is discovered in that rung\u2019s artifact; "
        "the trigger for an upward return must originate at the rung being revised or above it \u2014 "
        "difficulty, failure, or constraint pressure from any lower rung is not a valid trigger; "
        "returning upward because a lower rung\u2019s artifact was hard to produce is a faithfulness violation that voids the revised rung and all rungs below it; "
        "when returning upward, the revised rung must be re-derived from its input rung\u2019s artifact, "
        "and descent resumes from the revised rung downward; "
        "returning to the session observation loop is valid when a tool-executed observation reveals the declared gap is incorrect; "
        "the trigger must be a tool-executed observation \u2014 lower-rung pressure, inference, or prediction does not satisfy this trigger; "
        "when returning to the observation loop, the entire current ladder is void "
        "and a new observation must be made before any new gap may be declared. "
        "P20 (Write authorization): every tool call that writes a file to disk must be immediately preceded by "
        "\U0001f535 Write authorized citing the open rung name, artifact type, and file path; "
        "a file write without a preceding \U0001f535 Write authorized is a protocol violation that voids the rung in which it appears; "
        "a \U0001f535 Write authorized whose cited rung is not currently open, or whose artifact type does not match "
        "the open rung\u2019s permitted-tool-calls column, is a fabrication that voids the write and the rung; "
        "this sentinel exists so that every file write is auditable inline without reconstructing rung state from context. "
        "Ladder derivation rung: before descending, derive the rung table for this session by applying P1\u2013P19 to the declared intent; "
        "produce a table with columns: rung name | artifact type | gate condition (what tool-executed event satisfies the gate) | "
        "void condition (what invalidates the artifact) | faithfulness test (what a reviewer needs from only this artifact to evaluate the next rung) | "
        "permitted tool calls (what file modifications are allowed at this rung; all rungs permit read, observe, and non-modifying run commands; "
        "file modifications are constrained to the artifact type of that rung); "
        "verify the table satisfies P8 minimality \u2014 remove any rung that does not; "
        "descent begins immediately after the table is produced without pausing for confirmation; "
        "\u2705 Manifest declared is the closing sentinel of the ladder derivation rung \u2014 "
        "the required emission order is: rung table, then \u2705 Manifest declared; "
        "a manifest emitted without a preceding rung table is a protocol violation; "
        "the rung table is the gate on all subsequent rung activity. "
        "Session observation loop: observing running behavior means invoking the system directly in a manner that exercises the behavior named in the intent \u2014 "
        "the output must be produced by the behavior itself, not by a test framework asserting properties of it; "
        "the tool call must execute live running code \u2014 reading files, grepping source, "
        "or inspecting static artifacts does not satisfy this requirement regardless of what the output shows; "
        "a test suite run does not satisfy this requirement regardless of whether the tests pass. "
        "Before beginning a ladder descent, observe current running behavior via tool call \u2014 "
        "if the observation reveals a gap between running behavior and declared intent, declare the gap and descend the ladder; "
        "if no gap remains, emit \u2705 Ground complete \u2014 the session ends; "
        "this observation is not a rung in the derived ladder and must not appear in the rung table; "
        "the ladder handles only the declared gap; "
        "after manifest exhaustion, the observation loop recurs to check whether intent is fully achieved; "
        "\u2705 Ground complete may only be emitted as the outcome of the observation loop \u2014 "
        "emitting it outside the observation loop is a protocol violation "
        "regardless of whether \U0001f535 Closing observation is present. "
        "An executable validation artifact is a file whose sole purpose is to assert behavioral properties "
        "of another artifact \u2014 it contains no behavior of its own; "
        "validation files may not be imported by implementation files. "
        "An executable implementation artifact is a file that produces behavior directly \u2014 "
        "it contains no assertions about other artifacts; "
        "implementation files may not contain assertions. "
        "A file that both asserts and implements is a type-discipline violation that voids the rung at which it was written; "
        "classification is determined by file content, not file path or naming convention \u2014 "
        "path and naming are evidence, not authority. "
        "For software behavioral change, the standard ladder for each gap-closing cycle produces: "
        "prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 executable implementation. "
        "A derived ladder that omits any of these rungs for a software behavioral change task must cite which principle makes that rung unnecessary. "
        "The criterion is exercised only when the automated validation suite runs to completion and individual assertions fail; "
        "execution halted before reaching the assertions (by infrastructure failure, import error, or any other cause) does not exercise the criterion \u2014 "
        "the executable-implementation artifact for such a halt resolves only the infrastructure gap (minimum change sufficient to allow the suite to reach the assertions); "
        "the criterion has not been exercised until individual assertions fail in a subsequent cycle. "
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
