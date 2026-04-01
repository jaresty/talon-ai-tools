"""Ground method prompt — structured parts (ADR-0220).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
The model derives its own ladder from the principles on each session.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → baseline → challenge → refine → verify.
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
        "[ ] The ladder structure: 7 steps — Intent → Criteria → Structure → Baseline → Challenge → Refinement → Verification; what GOES WRONG if you skip: gaps lost, completion false; RULE: one rung at a time "
        "[ ] The derivation rule: each artifact cites its source from previous rung; what GOES WRONG if you don't cite: chain breaks, unverifiable; RULE: cite source at each step "
        "[ ] Evidence authorities: domain determines what counts as evidence — software uses automated tests, writing uses peer review, decisions use stakeholder feedback, learning uses assessment; what GOES WRONG if wrong authority: evidence invalid; RULE: use appropriate authority for domain "
        "[ ] Verification: confirmation that no new gaps remain; what GOES WRONG if you skip: hidden gaps persist; RULE: explicit verification before completion "
        "[ ] Challenge: derive from P3,P5 — why Challenge MUST show evidence that gaps exist; what GOES WRONG if you claim gaps exist without evidence: no proof gaps are real; RULE: Challenge = produce evidence that baseline does not satisfy criteria "
        "[ ] Refinement: derive from P3,P5 — why Refinement must address OBSERVED gaps only; what GOES WRONG if you address unobserved gaps: wasted effort, may miss real issues; RULE: Refinement = target only gaps proven in Challenge output "
        "[ ] Baseline: derive from P2,P3 — why Baseline establishes all mechanics needed AND may create scaffolding; what GOES WRONG if scaffolding is not sufficient to verify evaluation works: cannot prove framework works; RULE: Baseline = create all mechanics needed and sufficient scaffolding, Challenge adds NEW criteria using EXISTING mechanics"
        "[ ] Structure before baseline: derive from P1,P2 — organization must precede artifact; what GOES WRONG if you create without structure: unfocused output; RULE: structure before baseline "
        "[ ] Criteria before structure: derive from P1 — success conditions before organization; what GOES WRONG if you organize without criteria: no way to evaluate; RULE: criteria before structure "
        "[ ] Intent before criteria: derive from P1 — outcome before success conditions; what GOES WRONG if you define success without outcome: criteria irrelevant; RULE: intent before criteria "
        "[ ] Evidence at proximity: derive from P3 — evidence must be temporally close to action; what GOES WRONG if delayed: proof weakens; RULE: evidence immediately after action "
        "[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves rules satisfied; what GOES WRONG if unexplained: description indistinguishable from compliance; RULE: explain evidence connection "
        "[ ] No contradiction in completion: derive from P3,P5 — claiming complete while acknowledging gaps is void; what GOES WRONG if you write 'complete' with 'gaps', 'caveats', 'needs': claim invalid; RULE: scan ENTIRE message for contradiction before 'complete' "
        "[ ] Rule citation at action: derive from P1,P3,P4 — cite specific derived rule before each action; what GOES WRONG if uncited: protocol compliance invisible; RULE: cite rule before action "
        "This checklist must appear BEFORE the first ladder rung begins. The derivation results must be in the chat, not just in your head. "
        "Before starting each rung, re-emit key rules from your derivation relevant to that rung. "
        "BEFORE transitioning to next rung, verify and declare: [current rung artifact completed?], [evidence visible?], [gaps remaining?], [next rung requires?]. If gaps remain, do NOT proceed — close gap first. "
        "Protocol derived MUST be emitted as: 🔵 Protocol derived — AFTER deriving all rules from P1-P5. "
        "Ladder derived MUST be emitted as: 🔵 Ladder derived — AFTER producing the ladder table with columns: rung name | artifact type | derivation source | evidence form. "
        "No descent before both 🔵 Protocol derived and 🔵 Ladder derived sentinels — these are gates on all subsequent work. "
        "The 7-rung ladder: "
        "1. Intent — What outcome is being aimed for? Derivation: from task, derive specific outcome. Evidence: clear statement of goal. "
        "2. Criteria — What conditions must be true for success? Derivation: from intent, derive conditions that verify success. Evidence: checklist or measurable conditions. "
        "3. Structure — How is the solution organized? Derivation: from criteria, derive organization. Evidence: internal consistency. "
        "4. Baseline — Does the evaluation framework exist? Derivation: from criteria, derive evaluation structure. Evidence: evaluation structure APPLIED and VERIFIED to work. "
        "IMPORTANT: Baseline establishes ALL evaluation mechanics AND may create minimal scaffolding to hold them. This scaffolding is NOT the solution - it's just enough to verify evaluation works. Baseline must PASS with its scaffolding. "
        "IMPORTANT: Baseline establishes mechanics at Baseline (may create them). Challenge adds NEW criteria but uses EXISTING mechanics - adding new mechanics at Challenge is scope expansion. "
        "IMPORTANT: Baseline evaluation must be SELF-CONTAINED. If it fails due to missing prerequisites, that's a broken framework, not evidence of gaps. Only NEW criteria added at Challenge can expose gaps in the solution. "
        "5. Challenge — What evidence proves gaps exist? Derivation: from Baseline, add NEW evaluation criteria that FAIL against the solution. Evidence: failing output from NEW criteria proves gaps exist, NOT failing because framework is broken. "
        "IMPORTANT: Work on the smallest verifiable thing at a time — each check must be satisfied before the next. "
        "6. Refinement — How is the artifact improved? Derivation: from Challenge, address the SPECIFIC gaps that were OBSERVED. Evidence: changes target the exact gaps proven to exist. "
        "IMPORTANT: Refinement must address OBSERVED gaps only - gaps seen in Challenge output. Addressing unobserved gaps wastes effort and may miss real issues. "
        "7. Verification — How is completion confirmed? Derivation: from refinement, derive confirmation. Evidence: no new gaps exposed. "
        "Emit rung labels to begin each rung; emit completion sentinels (✅ [Rung] complete) to finish each rung. "
        "Evidence before claims: for every claim about completion, there must be evidence proving it. "
        "Ground complete may only be emitted after verification confirms no gaps remain. "
        "Domain adaptation: for tasks where verification is possible, define evaluation scaffold BEFORE producing solution — evaluation defined after solution is vacuous (Texas sharpshooter). "
        "Baseline defines evaluation framework; Challenge applies it to show OBSERVED gaps; Refinement produces solution that addresses those OBSERVED gaps."
        "for writing tasks, it maps to intent→criteria→outline→draft→review→revision→final; "
        "for decision-making, it maps to intent→criteria→analysis→option→stakeholder review→recommendation→decision. "
        "The model should derive the appropriate ladder for the task domain. "
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
