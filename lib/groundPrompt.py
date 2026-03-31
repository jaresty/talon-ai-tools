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
    "impl_intent": "\U0001f535 Intent logged \u2014 id: [unique id] | file: [path] | target: [assertion name] | evidence: [verbatim red output showing failure]",
    "impl_intent_achieved": "\U0001f535 Intent achieved \u2014 id: [unique id] | file: [path] | target: [assertion name] | evidence: [verbatim green output showing passing]",
    "protocol_derived": "\U0001f7e2 Protocol derived",
    "ladder_derived": "\U0001f7e2 Ladder derived",
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
    "v_complete": "gate: this sentinel may only be emitted after a tool call in this response has written the validation file to disk; emitting this sentinel without a preceding tool call that wrote the file is a fabrication that voids the sentinel and the rung; the tool call output must show the file was successfully written",
    "thread_complete": "gate: meta exec_observed after executable implementation shows the gap declared for this thread is no longer present in running behavior; every assertion in the validation artifact must appear passing in this exec_observed output",
    "manifest_exhausted": "gate: count of Thread N complete sentinels equals N in Manifest declared",
    "carry_forward": "gate: prior failure name quotable verbatim from a prior exec_observed sentinel",
    "i_formation": "gate: observation of current state complete before manifest",
    "r2_audit": "gate: every criterion encoded in notation; audit section named and separate",
    "ground_complete": "gate: \U0001f535 Closing observation must appear in the current response before this sentinel; meta exec_observed shows no gap between observed running behavior and declared intent; all manifest threads complete",
    "closing_observation": "gate: the tool call immediately before this sentinel must directly invoke the behavior named in the session intent and its output must show that behavior is present; this sentinel must appear after \u2705 Manifest exhausted and before \u2705 Ground complete in the same response; emitting \u2705 Ground complete without a preceding \U0001f535 Closing observation in the current response is a protocol violation",
    "impl_intent": "gate: this sentinel must appear immediately before every file-write tool call at every rung; include a unique id for this edit that will be matched by impl_intent_achieved; every file edit requires impl_intent + impl_intent_achieved pair - editing any file without this pair is a protocol violation; the artifact type is determined by the rung table - the file must be of the artifact type permitted at the current rung as determined by the rung table; if a file of a different artifact type needs editing, emit an upward return to the appropriate rung first; the target must be a specific test assertion name and the evidence must be verbatim output from running the validation file showing that test assertion failing in the current state; emitting this sentinel without a preceding exec_observed showing the target test assertion failing voids the intent and the subsequent write; fabrication of red evidence (output that does not come from actual test execution) voids the sentinel and the rung; for backfill cases where tests already pass and cannot be seen red, perturb the implementation (introduce a controlled fault) to observe the test fail, then fix the perturbation",
    "impl_intent_achieved": "gate: this sentinel must appear immediately after a tool call in this response that runs the test or validation file to show the target test assertion passing; the unique id must match the id from impl_intent in this response, the target test assertion name must match the target from impl_intent and the evidence must be verbatim output from running the test or validation file showing that test assertion passing in the current state; emitting this sentinel without a preceding tool call that runs the test or validation file is fabrication that voids the sentinel and the rung; emitting this sentinel without a matching impl_intent in the same response voids the intent; fabrication of green evidence (output that does not come from actual test execution) voids the sentinel and the rung; each file-write requires its own impl_intent + impl_intent_achieved pair with matching unique ids - the pair must repeat for every edit; skipping the pair for subsequent edits is a protocol violation",
    "protocol_derived": "gate: derived protocol rules cited P1-P6 must precede this sentinel; must be emitted before ladder derivation",
    "ladder_derived": "gate: rung table must precede this sentinel; must be emitted after protocol derived and before descending",
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
        "P1 (Intent primacy): intent is an abstract goal outside the system, not an artifact; without intent, no way to evaluate artifacts; intent anchors all downstream decisions; all artifacts derive from it. "
        "P2 (One artifact per type): mixing artifact types creates ambiguity about what each rung produces; each artifact type has exactly one rung. "
        "P3 (Observable evidence required): a model's description is indistinguishable from completion; every claim requires tool execution showing reality; pre/post change states visible through actual traces. "
        "P4 (File edit protocol): to prevent bypassing protocol requirements; every file edit follows protocol rules; only EV rung edits validation files, only EI rung edits implementation files; impl_intent + impl_intent_achieved pair required for each edit. "
        "P5 (Derivation chain): memory is unreliable; artifacts derive from prior rung's actual content, not memory; scope does not expand. "
        "P6 (Thread sequencing): to maintain coherent gap closure; minimal complete vertical slice — one independently testable behavior per thread per cycle; manifest declares gaps; all rungs for Thread N before N+1; ladder derivation occurs once at session start. "
        "Protocol derivation: before ladder derivation, derive the complete protocol rules by applying P1-P6 — "
        "derive: Session observation loop (when to observe vs descend, what observation means vs does NOT mean), "
        "ladder derivation format (table columns, columns meaning), "
        "rung-specific behaviors (when to emit each sentinel, gate blocks sentinel emission until gate satisfied), "
        "evidence chain (every assertion must go red then green; show red output before implementing, show green output after implementing; describing what you would do is not evidence; every assertion and its red→green transition must appear in the log for independent verification), "
        "rung transitions (emit rung label when beginning each rung; emit completion sentinel when finishing each rung; emit rung label when returning upward to a prior rung; you are at rung N until you emit completion sentinel for rung N or return upward), "
        "rung completion order (each rung must produce its artifact before emitting completion sentinel; sequential descent through prose → criteria → formal notation → validation → implementation; skipping a rung is a protocol violation), "
        "P5 implies sequential descent (since each artifact derives from prior artifact per P5, you must produce them in order — treating the ladder as a planning document rather than strict sequence violates derivation), "
        "ladder is strict execution sequence (emit rung label, produce artifact, emit completion sentinel — repeat for each rung in order; you may return upward freely, but only when higher rung artifact is discovered to be malformed — NOT to make lower rung implementation easier; difficulty, failure, or constraint pressure at a lower rung is not a valid upward return trigger), "
        "observation loop returns to start (after manifest exhausted, return to observation loop to verify gap is closed; re-observe running behavior; if gap still exists, descend ladder again; if gap is closed, emit Ground complete), "
        "observation loop corollary (if opening observation shows no gap exists, emit Ground complete immediately — no ladder descent needed), "
        "upward return conditions (what triggers return, what does NOT trigger return and why excluded), "
        "evidential scoping (evidence is scoped to current cycle and gap, not prior cycles), "
        "scope preservation (scope does not expand between rungs), "
        "derivation reasoning (explain WHY each rule follows from P1-P6, not just WHAT the rule is); "
        "each derived rule must cite its source principle(s) from P1-P6; rules that cannot be derived are protocol violations; "
        "emit Protocol derived after deriving all rules; "
        "emit Ladder derived after producing the rung table; "
        "ground complete may only be emitted as the outcome of the observation loop — emitting it outside the loop is a protocol violation. "
        "Rung validity test: a rung is valid iff a human reviewer with only that rung's artifact can evaluate the next rung. "
        "Standard ladder for software behavioral change: prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 executable implementation — each rung must be completed in this order; emit the rung label before producing its artifact; emit completion sentinel after artifact is produced and gate is satisfied. "
        "EV rung: edits only validation files. EI rung: edits only implementation files. "
        "An executable validation artifact is a file whose sole purpose is to assert behavioral properties of another artifact \u2014 it contains no behavior of its own; it must be invocable by an automated tool; validation files may not be imported by implementation files. "
        "An executable implementation artifact is a file that produces behavior directly \u2014 it contains no assertions about other artifacts; implementation files may not contain assertions. "
        "A file that both asserts and implements is a type-discipline violation that voids the rung; classification is determined by file content, not file path or naming convention \u2014 path and naming are evidence, not authority. "
        + _sentinel_block()
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
