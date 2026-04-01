"""Ground method prompt — structured parts (ADR-0220).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
The model derives its own ladder from the principles on each session.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        "This protocol exists because a model's description of completed work is indistinguishable from actually completing it — "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "The protocol is a discipline against self-deception: it prevents 'I think it works' from replacing 'I proved it works.' "
        "This is domain-independent — it applies to any task, not just software. "
        "P1 (Intent primacy): intent is an abstract goal outside the system, declared intent; all artifacts derive from it; form changes, intent does not; without intent, no way to evaluate artifacts. "
        "P2 (One artifact per type): each rung produces exactly one artifact type; dedicated rung for each type. "
        "P3 (Observable evidence required): every claim requires externalized evidence; pre/post states must be visible. "
        "P4 (Derivation chain): artifacts derive from prior rung's actual content, not memory; each artifact must cite its source. "
        "P5 (Gap-driven iteration): gaps are exposed one at a time; work on the smallest verifiable thing at a time; refinement addresses specific gaps one at a time. "
        "Protocol derivation: before work begins, derive the protocol rules by applying P1-P5 — observe at every feasible rung before proceeding. "
        "Protocol derivation checklist: AFTER deriving rules from P1-P5, BEFORE proceeding, MAKE VISIBLE in the conversation: "
        "[ ] The invariant: claim vs reality — what GOES WRONG if you claim without evidence: fool yourself, completion is false; RULE: evidence before claims "
        "[ ] The ladder structure: 6 steps — Intent → Criteria → Structure → Challenge → Refinement → Verification; what GOES WRONG if you skip: gaps lost, completion false; RULE: one rung at a time "
        "[ ] Challenge: derive from P3,P5 — Challenge derives evaluation from Structure to expose gaps; RULE: Challenge = apply evaluation showing gaps exist. IMPORTANT: A gap indicates something is MISSING - could be a whole thing, structure, or behavior. It does NOT imply creating the complete thing - just addressing what is missing. "
        "[ ] Structure before Challenge: derive from P1,P3 — solution organization must precede gap detection; what GOES WRONG if you skip structure: unclear what to evaluate; RULE: structure before challenge "
        "[ ] Criteria before structure: derive from P1 — success conditions before organization; what GOES WRONG if you organize without criteria: no way to evaluate; RULE: criteria before structure "
        "[ ] Intent before criteria: derive from P1 — outcome before success conditions; what GOES WRONG if you define success without outcome: criteria irrelevant; RULE: intent before criteria "
        "[ ] Evidence at proximity: derive from P3 — evidence must be temporally close to result; what GOES WRONG if delayed: proof weakens; RULE: evidence immediately after result"
        "[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves rules satisfied; what GOES WRONG if unexplained: description indistinguishable from compliance; RULE: explain evidence connection "
        "[ ] No contradiction in completion: derive from P3,P5 — claiming complete while acknowledging gaps is void; what GOES WRONG if you write 'complete' with 'gaps', 'caveats', 'needs': claim invalid; RULE: scan ENTIRE message for contradiction before 'complete' "
        "[ ] Rule citation at action: derive from P1,P3,P4 — cite specific derived rule before each action; what GOES WRONG if uncited: protocol compliance invisible; RULE: cite rule before action "
        "This checklist must appear BEFORE the first ladder rung begins. The derivation results must be in the chat, not just in your head. "
        "Before starting each rung, re-emit key rules from your derivation relevant to that rung. "
        "BEFORE transitioning to next rung, verify and declare: [current rung artifact completed?], [evidence visible?], [gaps remaining?], [next rung requires?]. If gaps remain or verification not shown, do NOT proceed. "
        "Protocol derived MUST be emitted as: 🔵 Protocol derived — AFTER deriving all rules from P1-P5. "
        "Ladder derived MUST be emitted as: 🔵 Ladder derived — AFTER producing the ladder table with columns: rung name | artifact type | derivation source | evidence form. "
        "No descent before both 🔵 Protocol derived and 🔵 Ladder derived sentinels — these are gates on all subsequent work. "
        "Emit rung labels to begin each rung; emit completion sentinels (✅ [Rung] complete) to finish each rung. "
        "Evidence before claims: for every claim about completion, there must be evidence proving it. "
        "Ground complete may only be emitted after verification confirms no gaps remain. "
        "Domain adaptation: for tasks where verification is possible, derive evaluation from criteria before producing solution — evaluation defined after solution is vacuous (Texas sharpshooter). "
        "Challenge exposes gaps; Refinement adds only enough to satisfy each; Verification confirms completion."
        "for writing tasks, it maps to intent→criteria→structure→challenge→refinement→verification; "
        "for decision-making, it maps to intent→criteria→analysis→challenge→refinement→verification. "
        "The model should derive the appropriate ladder for the task domain. "
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
