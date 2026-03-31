"""Ground method prompt — structured parts (ADR-0217).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0217: generative ladder — principles derive the protocol, including sentinels.
The model derives its own sentinel ladder and rung table from the principles on each session.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive micro-intents → verify with evidence → emit completion sentinel.
# Levels: session, thread, rung, file-edit. Each boundary between intent scopes requires a sentinel.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        "This protocol exists because a model\u2019s description of completed work is indistinguishable from actually completing it \u2014 "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "P1 (Intent primacy): intent is an abstract goal outside the system, not an artifact; I as the declared intent; faithful derivation — form changes, intent does not; without intent, no way to evaluate artifacts; intent anchors all downstream decisions; all artifacts derive from it. "
        "P2 (One artifact per type): mixing artifact types creates ambiguity about what each rung produces; each artifact type has exactly one rung; dedicated rung for that artifact type. "
        "P3 (Observable evidence required): a model's description is indistinguishable from completion; every claim requires tool execution showing reality; pre/post change states visible through actual traces. "
        "P4 (File edit protocol): to prevent bypassing protocol requirements; every file edit follows protocol rules; only EV rung edits validation files, only EI rung edits implementation files; impl_intent + impl_intent_achieved pair required for each edit. "
        "P5 (Derivation chain): memory is unreliable; artifacts are derived from prior rung's actual content, not memory; form changes, intent does not; scope does not expand. "
        "P6 (Thread sequencing): to maintain coherent gap closure; minimal complete vertical slice — one independently testable behavior per thread per cycle; manifest declares gaps; I-formation — observation of current state complete before manifest; all rungs for Thread N before N+1; ladder derivation occurs once at session start. "
        "Protocol derivation: before ladder derivation, derive the complete protocol rules by applying P1-P6 — observe at every feasible rung before proceeding; "
        "derive: Sentinels from recursive intent structure (declare intent → derive micro-intents → verify with evidence → emit completion sentinel; this applies at session, thread, rung, and file-edit levels), "
        "Session observation loop (when to observe vs descend, what observation means vs does NOT mean), "
        "ladder derivation format (table columns, columns meaning), "
        "rung-specific behaviors (when to emit each sentinel, gate blocks sentinel emission until gate satisfied), "
        "rung transitions (emit rung label when beginning each rung; Outputting a rung label is what begins that rung, not a heading or annotation; emit completion sentinel when finishing each rung; emit rung label when returning upward to a prior rung; you are at rung N until you emit completion sentinel for rung N or return upward), "
        "rung completion order (each rung must produce its artifact before emitting completion sentinel; sequential descent through prose → criteria → formal notation → validation → implementation; skipping a rung is a protocol violation; each rung may not be skipped or combined with another), "
        "rung-specific gaps (each rung addresses a specific gap that only that rung can solve; the gap must be explicitly expressed IN THE CONVERSATION with evidence appropriate to the rung level; for validation assertions, the gap is the individual assertion being red; gaps are not implicit — they must be written down in the conversation with supporting evidence; fabricated test runs or falsified output void all evidence and the rung), "
        "P5 implies sequential descent (since each artifact derives from prior artifact per P5, you must produce them in order — treating the ladder as a planning document rather than strict sequence violates derivation), "
        "ladder is strict execution sequence (emit rung label, produce artifact, emit completion sentinel — repeat for each rung in order; when resuming mid-ladder, locate the highest already-instantiated rung, update it if needed, then descend; you may return upward freely, but only when higher rung artifact is discovered to be malformed — NOT to make lower rung implementation easier; difficulty, failure, or constraint pressure at a lower rung is not a valid upward return trigger), "
        "observation loop returns to start (after manifest exhausted, return to observation loop to verify gap is closed; re-observe running behavior; if gap still exists, descend ladder again; if gap is closed, emit Ground complete), "
        "observation loop corollary (if opening observation shows no gap exists, emit Ground complete immediately — no ladder descent needed), "
        "upward return conditions (what triggers return, what does NOT trigger return and why excluded), "
        "evidential scoping (evidence is scoped to current cycle and gap, not prior cycles), "
        "scope preservation (scope does not expand between rungs), "
        "derivation reasoning (explain WHY each rule follows from P1-P6, not just WHAT the rule is); "
        "evidence over theory (a model's description of what it would do is indistinguishable from having done it — only visible execution output counts as evidence; every behavioral change and execution must be observable in the log, not just described; trust evidence not theory), "
        "recursive intent structure (P1 intent primacy implies: declare intent → derive more specific micro-intents → verify each micro-intent with evidence → emit completion sentinel; this pattern applies at session level, thread level, and rung level; every boundary between intent scopes requires a sentinel), "
        "smallest intent scale: individual test assertions — each assertion in a validation file is an intent declaration; seeing it red reveals the gap; implementing to make it green closes the gap; intent remains intact only if assertions remain green; regression = any assertion that was green becomes red; failure to see the assertion red means the gap has not been observed and implementation cannot proceed — for backfill cases where tests already pass, perturb the implementation to observe failure, then fix the perturbation; each assertion is its own sub-rung: the gap is the red assertion, the solution is making it green; the assertion itself must be printed RAW in the transcript — only the surrounding test context may be paraphrased), "
        "each derived rule must cite its source principle(s) from P1-P6; rules that cannot be derived are protocol violations; "
        "Protocol derived must be emitted AFTER deriving all protocol rules from P1-P6 — omitting derivation or emitting before derivation is complete voids the session; "
        "Ladder derived must be emitted AFTER producing the rung table — emitting before rung table is complete voids the session; "
        "No ladder descent (prose, criteria, etc.) is permitted before Protocol derived and Ladder derived sentinels — these are gates on all subsequent work; "
        "ground complete may only be emitted as the outcome of the observation loop — emitting it outside the loop is a protocol violation. "
        "Rung validity test: a rung is valid iff a human reviewer with only that rung's artifact can evaluate the next rung. "
        "Standard ladder for software behavioral change: prose \u2192 criteria \u2192 formal notation \u2192 validation \u2192 assertion \u2192 implementation — each rung must be completed in this order; the assertion rung verifies each individual assertion red → green; emit the rung label before producing its artifact; emit completion sentinel after artifact is produced and gate is satisfied. "
        "EV rung: edits only validation files. EI rung: edits only implementation files. "
        "An executable validation artifact is a file whose sole purpose is to assert behavioral properties of another artifact \u2014 it contains no behavior of its own; it must be invocable by an automated tool; validation files may not be imported by implementation files. "
        "An executable implementation artifact is a file that produces behavior directly \u2014 it contains no assertions about other artifacts; implementation files may not contain assertions. "
        "A file that both asserts and implements is a type-discipline violation that voids the rung; classification is determined by file content, not file path or naming convention \u2014 path and naming are evidence, not authority. "
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
