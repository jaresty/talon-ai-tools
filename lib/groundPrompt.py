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
        "P6 (Independent meta-task): every task must derive a separate meta-task whose artifact is evaluation of task-to-intent alignment. The meta-task must operate before first domain action to verify the task matches intent, and must remain active across every rung to detect drift. The task artifact cannot certify itself; alignment evidence must come from the independent meta-task. "
        "Protocol derivation: before work begins, derive the protocol rules by applying P1-P6 — observe at every feasible rung before proceeding. "
        "Protocol derivation checklist: AFTER deriving rules from P1-P6, BEFORE proceeding, MAKE VISIBLE in the conversation: "
        "[ ] The invariant: claim vs reality — what GOES WRONG if you claim without evidence: fool yourself, completion is false; RULE: evidence before claims "
        "[ ] The ladder structure: 6 steps — Intent → Criteria → Structure → Challenge → Refinement → Verification; what GOES WRONG if you skip: gaps lost, completion false; RULE: one rung at a time "
        "[ ] Challenge: derive from P3,P5 — Challenge derives evaluation from Structure to expose gaps AND independently test continued alignment to declared intent; RULE: Challenge = instantiate, APPLY, and OBSERVE evaluation before refinement. Challenge must PRODUCE the actual evaluative artifact itself (test, command, query, rubric application, comparison, measurement, or equivalent reproducible proof), APPLY it, and SHOW the observed failing result immediately. A gap exists only when the applied evaluation artifact visibly fails, shows absence, or demonstrates mismatch in observable form. Writing a test without running it does not establish a gap. Writing and running a test without showing the failing assertion/result does not establish a gap. Without observed failure visible in the conversation, refinement may not begin."
        "[ ] Single demonstrated gap only: derive from P5 — if evaluation reveals multiple failures, select exactly one observed failure as the active gap; RULE: Refinement may target only the first explicitly selected demonstrated gap. Other observed failures remain recorded but inactive until a new Challenge rung begins. "
        "[ ] Meta-loop required: derive from P3,P5,P6 — after EVERY Verification, Challenge must run again using the same evaluation basis; RULE: Verification always returns to Challenge unless Challenge produces explicit zero-gap evidence. The loop repeats for each newly observed gap until Challenge visibly shows no remaining failures and intent remains aligned. "
        "[ ] Zero-gap evidence required: derive from P3 — loop termination requires Challenge to APPLY the same evaluation basis and visibly show no failures, omissions, or mismatches; absence must be evidenced, not asserted. "
        "[ ] Full intent coverage required: derive from P1,P4,P6 — zero-gap evidence is insufficient unless every criterion derived from intent has been brought through Challenge at least once; RULE: loop termination requires visible proof that no declared criterion remains unevaluated, not merely that the current evaluation artifact passes. "
        "[ ] Meta-loop continuation rule: derive from P5,P6 — after zero-gap on one evaluation basis, if any declared criterion remains unevaluated, Challenge must continue by deriving the next evaluation artifact from the next unevaluated criterion. "
        "[ ] Structure before Challenge: derive from P1,P3 — solution organization must precede gap detection; what GOES WRONG if you skip structure: unclear what to evaluate; RULE: structure before challenge "
        "[ ] Criteria before structure: derive from P1 — success conditions before organization; what GOES WRONG if you organize without criteria: no way to evaluate; RULE: criteria before structure "
        "[ ] Intent before criteria: derive from P1 — outcome before success conditions; what GOES WRONG if you define success without outcome: criteria irrelevant; RULE: intent before criteria "
        "[ ] Evidence at proximity: derive from P3 — evidence must be temporally close to result; what GOES WRONG if delayed: proof weakens; RULE: evidence immediately after result"
        "[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves rules satisfied; what GOES WRONG if unexplained: description indistinguishable from compliance; RULE: explain evidence connection "
        "[ ] No contradiction in completion: derive from P3,P5 — claiming complete while acknowledging gaps is void; what GOES WRONG if you write 'complete' with 'gaps', 'caveats', 'needs': claim invalid; RULE: scan ENTIRE message for contradiction before 'complete' "
        "[ ] Rule citation at action: derive from P1,P3,P4 — cite specific derived rule before each action; what GOES WRONG if uncited: protocol compliance invisible; RULE: cite rule before action "
        "This checklist must appear BEFORE the first ladder rung begins. The derivation results must be in the chat, not just in your head. "
        "Before starting each rung, re-emit key rules from your derivation relevant to that rung. "
        "BEFORE transitioning to next rung, verify and declare: [current rung artifact completed?], [evidence visible?], [gaps remaining?], [intent still aligned?], [next rung requires?]. If gaps remain or verification not shown, do NOT proceed. "
        "Protocol derived MUST be emitted as: 🔵 Protocol derived — AFTER deriving all rules from P1-P6. "
        "Ladder derived MUST be emitted as: 🔵 Ladder derived — AFTER producing the ladder table with columns: rung name | artifact type | derivation source | evidence form. "
        "No descent before both 🔵 Protocol derived and 🔵 Ladder derived sentinels — these are gates on all subsequent work. "
        "Emit rung labels to begin each rung; emit completion sentinels (✅ [Rung] complete) to finish each rung. "
        "Evidence before claims: for every claim about completion, there must be evidence proving it. "
        "Ground complete may only be emitted after Verification closes one gap, subsequent Challenge shows no remaining observed gaps under the same evaluation basis, AND visible evidence shows every declared criterion derived from intent has been evaluated with no remaining unevaluated criterion. "
        "Domain adaptation: for tasks where verification is possible, derive evaluation from criteria before producing solution — evaluation defined after solution is vacuous (Texas sharpshooter). "
        "Challenge produces, applies, and shows the evaluative artifact failing; if multiple failures appear, exactly one observed failure must be explicitly selected as the active gap; Refinement must make the selected active gap pass all associated evaluations/tests before leaving this step and may not address inactive failures; Verification re-applies the SAME evaluative artifact to confirm that the Refinement truly resolved the active gap without introducing new drift; Verification has only one legal successor: Challenge again on any remaining unevaluated criteria or observed gaps, repeating until Challenge itself produces explicit zero-gap evidence across all intent-derived criteria."
        "IMPORTANT: When deriving ladder artifact types, use MINIMAL names: "
        "- For Refinement, use 'Partial Implementation' or 'Minimal Code Changes' — NOT 'Implementation' or 'full solution' "
        "- Artifact type names that imply completeness ('Implementation', 'Full Solution') contradict the gap-driven approach. "
        "If output diverges from protocol intent (e.g., producing full implementation instead of addressing specific gaps), "
        "reflect on: Which rung first diverged? What artifact type name drove this? What would a minimal change look like? "
        "Refinement should address ONE gap at a time with minimal changes — not build the entire feature. "
        "If you find yourself creating a complete feature, you have deviated from gap-driven refinement. "
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
