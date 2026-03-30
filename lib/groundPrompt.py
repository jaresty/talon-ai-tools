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
    "impl_intent": "\U0001f535 Intent logged \u2014 file: [path] | target: [assertion name] | evidence: [verbatim red output showing failure]",
    "impl_intent_achieved": "\U0001f535 Intent achieved \u2014 file: [path] | target: [assertion name] | evidence: [verbatim green output showing passing]",
}

# Per-sentinel gate conditions — emitted inline in the sentinel block so the gate
# requirement is visible at the exact point of emission.
_SENTINEL_GATES: dict[str, str] = {
    "ground_entered": "gate: first content emitted in this response; no artifact, code, prose, or reasoning may precede this sentinel — preceding content voids the session",
    "manifest_declared": "gate: rung table produced in current response; rung table precedes this sentinel",
    "exec_observed": "gate: tool call made in the current response immediately before this sentinel; verbatim output in triple-backtick block follows",
    "gap": "gate: exec_observed with non-empty failing output precedes this token in current response; gap text is a currently-false behavioral assertion",
    "hard_stop": "gate: exec_observed showing test suite failure + gap in current cycle; criterion identical to prior cycle criterion for this thread",
    "impl_gate": "gate: exec_observed showing test suite failure + gap in current cycle; valid only at the rung whose artifact type is executable implementation; every assertion in the validation artifact must appear failing in the verbatim exec_observed output (e.g. 'Expected … Received …', 'AssertionError', 'FAILED', specific test name + failure reason) — an exec_observed that shows only some assertions failing, only infrastructure failure, import error, process crash, or a model-described summary of failure does not satisfy this gate; if the suite cannot reach assertions, the implementation artifact for that cycle resolves only the infrastructure gap, and this gate cannot be emitted until a subsequent cycle produces assertion-level failure output for every assertion",
    "criteria_complete": "gate: exactly one criterion in this rung's artifact; criterion contains no conjunction; formal notation rung label may not be emitted until this sentinel has been emitted",
    "v_complete": "gate: pre-existence check tool call result present; tool call in this response wrote the file to disk",
    "thread_complete": "gate: meta exec_observed after executable implementation shows the gap declared for this thread is no longer present in running behavior; every assertion in the validation artifact must appear passing in this exec_observed output",
    "manifest_exhausted": "gate: count of Thread N complete sentinels equals N in Manifest declared",
    "carry_forward": "gate: prior failure name quotable verbatim from a prior exec_observed sentinel",
    "i_formation": "gate: observation of current state complete before manifest",
    "r2_audit": "gate: every criterion encoded in notation; audit section named and separate",
    "ground_complete": "gate: \U0001f535 Closing observation must appear in the current response before this sentinel; meta exec_observed shows no gap between observed running behavior and declared intent; all manifest threads complete",
    "closing_observation": "gate: the tool call immediately before this sentinel must directly invoke the behavior named in the session intent and its output must show that behavior is present; this sentinel must appear after \u2705 Manifest exhausted and before \u2705 Ground complete in the same response; emitting \u2705 Ground complete without a preceding \U0001f535 Closing observation in the current response is a protocol violation",
    "impl_intent": "gate: this sentinel must appear immediately before each file-write tool call to implementation code; the target must be a specific test assertion name and the evidence must be verbatim output from running the validation file showing that test assertion failing in the current state; emitting this sentinel without a preceding exec_observed showing the target test assertion failing voids the intent and the subsequent write; fabrication of red evidence (output that does not come from actual test execution) voids the sentinel and the rung; for backfill cases where tests already pass and cannot be seen red, perturb the implementation (introduce a controlled fault) to observe the test fail, then fix the perturbation",
    "impl_intent_achieved": "gate: this sentinel must appear after each file-write tool call to implementation code; the target test assertion name must match the target from impl_intent and the evidence must be verbatim output from running the validation file showing that test assertion passing in the current state; emitting this sentinel without a matching impl_intent in the same response voids the intent; fabrication of green evidence (output that does not come from actual test execution) voids the sentinel and the rung",
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
        "P1 (Intent primacy): intent exists; all artifacts derive from it; when intent changes, refine affected rungs top-down; completed rungs may not be re-opened except by this mechanism. "
        "P2 (Behavioral change isolation): One rung per artifact type; changes only at dedicated rung; a rung that changes behavior and also produces another artifact type must be split. "
        "P3 (Observable evidence required): Pre/post change states visible through actual tool output; the observation must directly demonstrate the behavior named in the criterion \u2014 infrastructure evidence does not satisfy this unless the criterion explicitly asserts infrastructure state. "
        "P4 (Enforced and persistent): Behavioral changes require a dedicated verification rung; a behavioral change without one is not complete. "
        "P5 (Automation quality verified): Automation must fail before passing; the failure output is part of the verification artifact, not a separate rung; a reviewer cannot determine from the test file alone what the implementation must do \u2014 the failure output is required; the transcript must also contain green-state evidence \u2014 every assertion in the validation artifact must be seen passing after implementation. "
        "P6 (Artifact type discipline): One rung per type; text rungs produce no files; each rung may not be skipped or combined with another; frozen artifacts may not be modified at subsequent rungs; every file write must occur at the dedicated rung for that artifact type. "
        "An executable validation artifact is a file whose sole purpose is to assert behavioral properties of another artifact \u2014 it contains no behavior of its own; it must be invocable by an automated tool; validation files may not be imported by implementation files. "
        "An executable implementation artifact is a file that produces behavior directly \u2014 it contains no assertions about other artifacts; implementation files may not contain assertions. "
        "A file that both asserts and implements is a type-discipline violation that voids the rung; classification is determined by file content, not file path or naming convention \u2014 path and naming are evidence, not authority. "
        "P7 (Upward faithfulness): Lower rungs narrow what upper rungs permit; expanding the permitted space is a faithfulness violation. "
        "P8 (Rung validity test): Human reviewer with only this rung\u2019s artifact can evaluate next rung; ladder is minimal \u2014 remove any rung that does not affect faithfulness evaluation. "
        "P9 (Information density preservation): Each rung encodes same/higher quality than above; a rung that loses information is a protocol violation. "
        "P10 (Three-part completeness): Observation + automation + implementation; all three must be present. "
        "P11 (Immediate lowest-rung observation): Observe at every feasible rung, beginning at the lowest; deferring is a protocol violation. "
        "P12 (Completeness slice): One independently testable behavior per thread per cycle; criterion is a falsifiable behavioral assertion \u2014 a feature name is not a criterion. "
        "P13 (Observation-first, observation-last): Open and close with tool-executed observation of live running code. "
        "Observing running behavior means invoking the system directly in a manner that exercises the behavior named in the intent \u2014 "
        "the output must be produced by the behavior itself, not by a test framework asserting properties of it; "
        "the tool call must execute live running code \u2014 reading files, grepping source, or inspecting static artifacts does not satisfy this requirement regardless of what the output shows; "
        "a test suite run does not satisfy this requirement regardless of whether the tests pass. "
        "The intent declaration must be derivable from the tool-executed opening observation. "
        "\u2705 Ground complete may only be emitted as the outcome of the observation loop \u2014 emitting it outside the loop is a protocol violation regardless of whether \U0001f535 Closing observation is present. "
        "\U0001f535 Closing observation must appear after \u2705 Manifest exhausted and before \u2705 Ground complete; its gate requires a tool call that directly invokes the behavior named in the session intent. "
        "P14 (Evidential authority): Only tool-executed events have standing; evidence scoped to the cycle and gap in which it was produced \u2014 a prior cycle, different thread, or different gap does not satisfy any gate. "
        "A completion sentinel is a closing marker \u2014 emitting it before its artifact is complete voids both; after a rung label is emitted, the only valid content before the completion sentinel is the rung\u2019s artifact. "
        "\U0001f534 Execution observed: is only valid when a tool call was made in the current response immediately before it \u2014 a fabricated sentinel voids the rung. "
        "\u2705 Ground entered must be the first emitted content of any response that begins a ground session \u2014 preceding content voids the sentinel and all work that follows. "
        "The impl_gate requires at least one assertion-level failure string in verbatim exec_observed output \u2014 infrastructure failure, import error, process crash, or model-described summary does not satisfy this gate. "
        "P15 (Derivation chain): Artifacts derive from prior rung\u2019s actual content, not memory; scope does not expand between rungs; a skipped rung voids all artifacts below it. "
        "P16 (Continuous descent): No pausing between rungs; response length is not a valid stop reason; continue from current rung in next response if descent cannot fit in one. "
        "P17 (Thread sequencing): Manifest declares gaps; all rungs for Thread N before N+1; ladder derivation occurs once when ground begins \u2014 not per thread. "
        "P18 (Write authorization): Every file write immediately preceded by \U0001f535 Write authorized citing open rung name, artifact type, and file path; "
        "the cited artifact type must match the artifact type of the named file as determined by the rung table \u2014 a type mismatch voids the write and the rung; "
        "this sentinel exists so that every file write is auditable inline without reconstructing rung state from context. "
        "P19 (Upward return): Return to revise when derivation error discovered at or above the revised rung \u2014 "
        "difficulty, failure, or constraint pressure from any lower rung is not a valid trigger; "
        "returning upward because a lower rung\u2019s artifact was hard to produce is a faithfulness violation that voids the revised rung and all rungs below it; "
        "the trigger for an upward return must originate at the rung being revised or above it; "
        "when returning upward, the revised rung must be re-derived from its input rung\u2019s artifact and descent resumes downward; "
        "the rung label must be re-emitted before any revised artifact content \u2014 "
        "re-entering a rung without re-emitting its label is a protocol violation that voids the revised artifact and all rungs below it. "
        "Returning to the session observation loop is valid when a tool-executed observation reveals the declared gap is incorrect; "
        "the entire current ladder is void on such return; a new observation must be made before any new gap may be declared. "
        "Ladder derivation rung: before descending, before emitting the first rung label, derive the rung table for this session by applying P1\u2013P19 to the declared intent; "
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
        "Session observation loop: before beginning a ladder descent, observe current running behavior via tool call \u2014 "
        "if the observation reveals a gap between running behavior and declared intent, declare the gap and descend the ladder; "
        "if no gap remains, emit \u2705 Ground complete \u2014 the session ends; "
        "this observation is not a rung in the derived ladder and must not appear in the rung table; "
        "the ladder handles only the declared gap; "
        "after manifest exhaustion, the observation loop recurs to check whether intent is fully achieved. "
        "For software behavioral change, the standard ladder for each gap-closing cycle produces: "
        "prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 executable implementation. "
        "A derived ladder that omits any of these rungs for a software behavioral change task must cite which principle makes that rung unnecessary. "
        "The criterion is exercised only when the automated validation suite runs to completion and individual assertions fail; "
        "execution halted before reaching the assertions (by infrastructure failure, import error, or any other cause) does not exercise the criterion \u2014 "
        "the executable-implementation artifact for such a halt resolves only the infrastructure gap (minimum change sufficient to allow the suite to reach the assertions); "
        "the criterion has not been exercised until individual assertions fail in a subsequent cycle. "
        "Outputting a rung label is what begins that rung \u2014 it is not a heading or annotation; "
        "a rung whose label has not been output has not begun; "
        "the rung label must be emitted before any artifact content for that rung \u2014 "
        "producing artifact content before the rung label is a protocol violation that voids that artifact and all rungs below it. "
        "When beginning mid-ladder, locate the highest already-instantiated rung, update it, then descend. "
        + _sentinel_block()
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
