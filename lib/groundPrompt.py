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
        "This protocol exists because a model's description of completed work is indistinguishable from actually completing it — "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "P1 (Intent primacy): intent is an abstract goal outside the system, not an artifact; I as the declared intent; faithful derivation — form changes, intent does not; without intent, no way to evaluate artifacts; intent anchors all downstream decisions; all artifacts derive from it. "
        "P2 (One artifact per type): mixing artifact types creates ambiguity about what each rung produces; each artifact type has exactly one rung; dedicated rung for that artifact type. "
        "P3 (Observable evidence required): a model's description is indistinguishable from completion; every claim requires tool execution showing reality; pre/post change states visible through actual traces. "
        "P4 (File edit protocol): to prevent bypassing protocol requirements; every file edit follows protocol rules; only EV rung edits validation files, only EI rung edits implementation files; impl_intent + impl_intent_achieved pair required for each edit. "
        "P5 (Derivation chain): memory is unreliable; artifacts are derived from prior rung's actual content, not memory; form changes, intent does not; scope does not expand. "
        "P6 (Thread sequencing): to maintain coherent gap closure; minimal complete vertical slice — one independently testable behavior per thread per cycle; manifest declares gaps; I-formation — observation of current state complete before manifest; all rungs for Thread N before N+1; ladder derivation occurs once at session start. "
        "Protocol derivation: before ladder derivation, derive the complete protocol rules by applying P1-P6 — observe at every feasible rung before proceeding. "
        "Protocol derivation checklist: AFTER deriving rules from P1-P6, BEFORE proceeding, MAKE VISIBLE in the conversation: "
        "[ ] How to handle files: what creates at validation, what edits at assertion/implementation — what GOES WRONG if you create files at wrong rung: audit trail breaks, protocol unverifiable; RULE: validation creates ALL stubs, assertion adds assertions to existing test files, implementation edits existing stub files only, NO new files after validation "
        "[ ] How to handle the ladder: what each rung does and when to move to next — what GOES WRONG if you skip rungs: gaps lost, completion becomes false claim; RULE: one rung at a time, complete before next "
        "[ ] How to verify gap closure: when to check and emit completion — what GOES WRONG if you emit 'complete' with gaps remaining: fool yourself, contradictions invisible; RULE: only emit 'complete' after upward scan confirms no gaps, look for 'but still' or 'needs' as contradiction signals "
        "[ ] Gap cycle: derive from P1,P3,P5 — why one gap at a time; what GOES WRONG if you batch: no clear red→green signal; RULE: one gap at a time, assertion→implement→verify→complete→next gap "
        "[ ] Validation before assertion: derive from P3,P5 — why validation tests must pass (scripts run, stubs exist) before assertion rung: assertion rung failures must be due to actual gaps, not infrastructure issues; RULE: validation tests must pass before moving to assertion rung "
        "[ ] Three-step completion: derive from P2,P3 — why validation→assertion→implementation requires THREE distinct rungs, not two; what GOES WRONG if you combine: cannot verify that infrastructure works before adding new failing assertions; RULE: (1) validation rung: create stubs that make tests PASS, (2) assertion rung: add NEW assertions that FAIL against stubs, (3) implementation rung: implement to make assertions PASS; the pass→fail→pass cycle proves each step works; skipping assertion rung means you never prove stubs were sufficient first "
        "[ ] Implementation edits only: derive from P2,P4 — why only stub implementation files at implementation rung, not test files; what GOES WRONG if you edit test files at implementation: rung responsibilities mix, test changes obscure what implementation actually satisfies, derivation chain breaks; RULE: implementation rung ONLY edits stub implementation files (the file being implemented) — NEVER edit test files during implementation; if tests need adjustment, that was a gap in the assertion rung "
        "[ ] Executable rungs only: derive from P1,P2,P6 — why only validation, assertion, implementation rungs may create or edit executable files; what GOES WRONG if you create files in prose/criteria/formal rungs: you skip rung-specific gates, breaks derivation chain, creates untraceable artifacts; RULE: only EV, EA, EI rungs create or edit files — prose (analysis only), criteria (requirements only), formal notation (specification only) produce mental artifacts, not files "
        "[ ] Smallest intent at executable level: derive from P1,P3 — the smallest unit of intent is the individual failing assertion, not the test file; each assertion is its own intent declaration; regression = assertion that was green becomes red; RULE: implement one assertion at a time, not batch of assertions "
        "[ ] File edit declarations: derive from P4 — what to declare before edits; RULE: before any edit, declare 'no new files' at assertion/implementation rungs "
        "[ ] Evidence: derive from P3 — what evidence for completion sentinels; RULE: cite specific assertion that was red "
        "[ ] File manifest: derive from P4,P6 — why validation must list files created; RULE: validation rung lists every file before creating it "
        "[ ] Upward scan: derive from P5,P6 — how to verify all criteria addressed; RULE: after implementation, scan up with ✅/❌ checklist for each criterion from prose/criteria/formal notation "
        "[ ] Rung context: derive from P1,P6 — why re-emit rules at each rung; RULE: before each new rung label, re-emit key rules from derivation "
        "[ ] Rule citation at action: derive from P1,P3,P5 — why you must cite the specific derived rule before each action; what GOES WRONG if you don't cite rules at point of action: rule compliance becomes invisible, cannot verify protocol was followed, description of compliance is indistinguishable from compliance; RULE: BEFORE each file edit, rung transition, and completion emission, cite the specific derived rule that permits it "
        "[ ] Evidence at proximity: derive from P3,P5 — why evidence must be temporally close to action; what GOES WRONG if evidence is delayed: proof of rule compliance weakens, gaps in evidence allow violations to go undetected; RULE: evidence of rule compliance must appear IMMEDIATELY after each action, not in later summary — delayed evidence is weaker proof, proximity in transcript strengthens proof of rule adherence "
        "[ ] Evidence echoed in transcript: derive from P1,P3 — why you must explain how evidence proves rules were satisfied; what GOES WRONG if you don't explain: description of compliance is indistinguishable from compliance, evidence without explanation is just theory; RULE: after each completion sentinel, explain which evidence proves which rules were satisfied — make the connection visible, not implicit "
        "[ ] No contradiction in completion: derive from P3,P5 — why claiming complete while acknowledging gaps is a direct violation; what GOES WRONG if you write 'complete' in same message as 'gaps', 'caveats', 'needs', 'remaining': claim is void, contradiction visible to any reviewer, protocol becomes theater; RULE: if you write 'Ground complete' or 'Thread N complete' in a message that also contains 'gaps', 'caveats', 'needs', 'remaining', 'not yet', or 'still to do' — the completion is INVALID — return to upward scan and close actual gaps before claiming completion; BEFORE emitting 'Ground complete', scan ENTIRE message including Model interpretation/summary section for any 'gaps', 'caveats', 'not implemented', 'missing', 'needs' — if found anywhere, completion is INVALID, fix the message first "
        "This checklist must appear BEFORE the first ladder rung begins. The derivation results must be in the chat, not just in your head. "
        "Before starting each rung, re-emit key rules from your derivation relevant to that rung. "
        "BEFORE transitioning to next rung, verify and declare: [current rung artifact completed?], [evidence visible?], [gaps remaining?], [next rung requires?], [files permitted?]. If gaps remain, do NOT proceed downward — return upward or close gap first. "
        "Protocol derived MUST be emitted as: 🔵 Protocol derived — AFTER deriving all rules from P1-P6. "
        "Ladder derived MUST be emitted as: 🔵 Ladder derived — AFTER producing the rung table with columns: rung name | artifact type | gate condition | void condition | faithfulness test | permitted tool calls. "
        "No ladder descent before both 🔵 Protocol derived and 🔵 Ladder derived sentinels — these are gates on all subsequent work. "
        "Emit rung labels to begin each rung; emit completion sentinels (✅ [Rung] complete) to finish each rung. "
        "Evidence before claims: for every claim about code being correct, there must be tool execution output proving it. "
        "Ground complete may only be emitted after upward scan confirms all gaps closed. "
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
