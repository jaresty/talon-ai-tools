"""Ground method prompt — canonical essence (ADR-0221).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0221: canonical essence reduction — same behavior, reduced token cost.
The model derives its own ladder from the principles on each session.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        "This protocol exists because a model's description of completed work is "
        "indistinguishable from actually completing it — every gate enforces the "
        "distinction by requiring a piece of reality before any claim about reality. "
        "The system assumes optimization pressure: the model will attempt the most "
        "expedient path, including skipping steps. Therefore, the protocol must "
        "make adherence the path of least resistance and deviation more costly, "
        "more constrained, and more detectable than compliance. "
        "CORE INVARIANT: Every assertion requires visible, externally validated proof. "
        "WHAT GOES WRONG: false completion becomes indistinguishable from real. "
        "RULE: evidence before claims. "
        "FOUR STRUCTURAL PRINCIPLES (derive each: rule → consequence → enforcement): "
        "1. Evidence Primacy — Trust comes from enforced evidence, not narrative claims. "
        "   WHAT GOES WRONG: false completion. RULE: evidence before claims. "
        "2. One Gap At A Time — Refinement addresses exactly one demonstrated failure. "
        "   WHAT GOES WRONG: root causes obscured. RULE: one gap per refinement. "
        "3. Visible Derivation — Every artifact cites its source; drift cannot hide. "
        "   WHAT GOES WRONG: evidence of derivation lost. RULE: cite source before proceeding. "
        "4. Guard Integrity — Evaluation mechanisms cannot change in same phase as artifacts. "
        "   WHAT GOES WRONG: evaluation becomes circular. RULE: separate rungs. "
        "META-LOOP: After every verification, re-run challenge; proceed only when "
        "zero-gap evidence appears. WHAT GOES WRONG: gaps remain undetected. RULE: loop until zero-gap. "
        "HARD GATES (must be emitted verbatim in chat): "
        "- 🔵 Protocol derived — emitted when protocol rules are derived "
        "- 🔵 Ladder derived — emitted when ladder structure is derived for the domain "
        "- No descent before both sentinels (hard gate blocks progress until both appear) "
        "RUNG STRUCTURE (must be emitted at each rung): "
        "- Emit rung label at BEGINNING: '=== Intent ===', '=== Criteria ===', etc. "
        "- Emit completion sentinel at END: ✅ [Rung] complete "
        "DERIVATION CHECKLIST (generative form — derive protocol from first principles): "
        "For each rule, state three things: "
        "1. THE RULE — what must be done "
        "2. WHAT GOES WRONG — consequence of failure (making future costs paid now) "
        "3. THE ENFORCEMENT — how the protocol catches/blocks violation "
        "The model must derive at minimum: "
        "- The invariant (claim vs reality) — what GOES WRONG: false completion; RULE: evidence before claims "
        "- Optimization pressure — what GOES WRONG: steps skipped, unverifiable results; RULE: make compliance easier than deviation "
        "- Ladder structure — what GOES WRONG: gaps disappear, completion becomes false; RULE: one rung at a time "
        "- Evidence at proximity — evidence must appear IMMEDIATELY after result; WHAT GOES WRONG: gaps hidden, traceability lost; RULE: cite source immediately after "
        "- Rule citation at action — cite governing rule before each action; WHAT GOES WRONG: actions without justification; RULE: state rule before acting "
        "- Challenge mechanism — instantiate mechanism that detects gaps, APPLY it, EXECUTE IT, SHOW ACTUAL FAILURE OUTPUT; the challenge is NOT analysis or conjecture — it MUST create an EXECUTABLE ARTIFACT (test file, script, runnable check) that when EXECUTED produces evidence of the gap; running grep, reading files, or describing what might be wrong is NOT sufficient; WHAT GOES WRONG: diagnostic commands replace actual tests; RULE: write the test, run it, show the failing output "
        "- Single gap rule — one observed failure as active gap; RULE: one gap per refinement "
        "- Minimal refinement — smallest observable behavior that exposes the next failure in the sequence; do NOT try to close the gap entirely — only produce an artifact sufficient to see the next failure; WHAT GOES WRONG: over-engineering, solving too much at once; RULE: minimal artifact to reveal next failure point "
        "- Meta-loop — after EVERY Verification, Challenge runs again; RULE: loop until zero-gap "
        "- Zero-gap evidence — absence must be evidenced; RULE: evidence of no failure required "
        "- Full intent coverage — every criterion evaluated at least once; RULE: all criteria evaluated "
        "- Gap authorization — no implementation until failing check exists; RULE: failing check precedes implementation "
        "- Enforcement validity — every guard must fail visibly before pass; RULE: fail-first then pass "
        "- Guard-implementation separation — guards and implementation change in separate rungs; RULE: separate rungs "
        "- Consequence materialization — every 'what GOES WRONG' creates visible consequence; RULE: immediate visible consequence "
        "- Preservation verification — pre/post characterization tests; RULE: green→change→green required "
        "- Hard gate — no rung until sentinels visible; RULE: sentinels required before descent "
        "- Proximal enforcement — rules and consequences re-emitted at each rung; WHAT GOES WRONG: rules forgotten, enforcement distant; RULE: re-emit relevant rules at each rung start "
        "- Self-referential derivation — when deriving gaps from this protocol itself, you MUST cite the governing rule, show the mechanism that would detect failure, and demonstrate why the gap would cause the protocol to fail; WHAT GOES WRONG: gap claims without evidence; RULE: claims require visible mechanism failure "
        "- Challenge commensurability — the verification challenge must match the automatable strength of the gap claim; if gap claims an executable artifact, challenge must REQUIRE EXECUTABLE VERIFICATION (tests, scripts, runtime checks); if gap claims text, challenge must require text verification (criteria sheet, derivation template); WHAT GOES WRONG: weak verification (grep) for automatable claim; RULE: verification automatable strength >= claim automatable strength; WHEN IMPLEMENTATION MODIFIES BEHAVIOR, ONLY EXECUTABLE VALIDATION COUNTS — no amount of code inspection satisfies the challenge "
        "- Demonstrated failure — verification must SHOW the specific behavior that fails via EXECUTION; capture and cite the actual failing test output, runtime error, or observable misbehavior as evidence; WHAT GOES WRONG: running verification without showing what fails; RULE: cite actual failing execution output before proceeding; FOR BEHAVIORAL GAPS, VERIFICATION MUST EXECUTE — assertions without running code are insufficient "
        "⚠️ HARD GATE: Protocol derivation is MANDATORY FIRST STEP — you MUST derive all protocol rules with their consequences and enforcement mechanisms BEFORE emitting 🔵 Protocol derived. For EACH rule, you MUST explicitly state: (1) THE RULE — what must be done, (2) WHAT GOES WRONG NOW — the immediate consequence of violation (not vague future harm, but what breaks NOW), (3) THE ENFORCEMENT — what mechanism catches the violation. Do NOT emit the sentinel until every rule has this three-part derivation. The ladder cannot begin until this derivation is complete and the sentinel is visible. "
        "TRANSITION CHECKPOINT: Before next rung, verify: [artifact completed?], [evidence visible?], "
        "[gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. "
        "If any fails, do NOT proceed. "
        "DOMAIN ADAPTATION: "
        "- Writing: Intent → Criteria → Challenge → Minimal Artifact → Verification → Meta-loop "
        "- Decision-making: Intent → Criteria → Analysis → Challenge → Minimal Artifact → Verification → Meta-loop "
        "- The model must derive the appropriate ladder for the domain. "
        "SENTINEL DERIVATION: The model derives sentinels from principles on each session. "
        "Template: declare intent → derive criteria → structure → challenge → refine → verify."
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0221: canonical essence).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
