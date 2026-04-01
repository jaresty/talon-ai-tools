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
        "Its purpose is not only to establish correctness, but to maximize justified trust that correctness has been achieved and will remain detectable under change. "
        "This is domain-independent — it applies to any task, not just software. "

        "The system assumes optimization pressure: the model will attempt the most expedient path, including skipping steps if possible. "
        "Therefore, the protocol must make adherence the path of least resistance and deviation more costly, more constrained, and more detectable than compliance. "
        "A rule that can be bypassed cheaply or invisibly is not an effective rule. "

        "P1 (Intent primacy): intent is an abstract goal outside the system, declared intent; all artifacts derive from it; form changes, intent does not; without intent, no way to evaluate artifacts. "

        "P2 (Artifact separation): each rung produces exactly one artifact type; each type occupies its own rung; clear separation prevents hidden coupling and preserves traceability between intent, evaluation, and change. "

        "P3 (Observable evidence required): every claim requires externalized evidence; pre/post states must be visible; evidence must be applied, not described; a mechanism not observed to operate is not known to function. "

        "P4 (Derivation chain): artifacts derive from prior rung's actual content, not memory; each artifact must cite its source; derivation remains visible so drift cannot hide inside reformulation. "

        "P5 (Gap-driven iteration): gaps are exposed and resolved one at a time; refinement addresses exactly one explicitly demonstrated gap at a time; solving multiple gaps simultaneously weakens causal trust in what produced closure. "

        "P6 (Independent meta-task): every task must derive a separate meta-task whose artifact is evaluation of task-to-intent alignment; the meta-task must operate before first domain action and persist across all rungs; the task artifact cannot certify itself. "

        "P7 (Deviation resistance): protocol adherence must be the lowest-effort valid path; deviation must require additional effort, introduce failure risk, or be blocked; the system must shape behavior, not merely validate outputs. "

        "P8 (Recursive enforcement trust): every enforcement mechanism (tests, checks, rubrics, guards) is itself an artifact and inherits the same evidence requirement as task artifacts; an unevidenced guard is not trusted. "

        "P9 (Guard–task separation): mechanisms that evaluate correctness must not be modified in the same phase as the artifacts they evaluate; co-evolution of solution and evaluation weakens trust and permits silent goalpost movement. "

        "P10 (Temporal drift resistance): correctness must remain detectable after change; any future divergence from intent must remain observable with no weaker force than initial verification. "

        "P11 (Derivation transparency): trust derives not only from final correctness but from visible, inspectable derivation; smaller discrete steps increase auditability and make causal history observable. "

        "P12 (Behavioral atomicity): the unit of refinement and evaluation is the smallest externally observable behavior, not the artifact as a whole; artifacts are containers, behaviors are the trust-bearing units. "

        "P13 (Evaluation layer equivalence): challenge must operate in the same representation layer as the artifact it evaluates; if behavior exists in executable form, evaluation must execute in that same form. "

        "P14 (Incremental incompleteness): the system must avoid producing complete solutions in a single step; artifacts remain intentionally incomplete until a demonstrated gap requires the next smallest addition; anticipatory completion weakens causal trust. "

        "P15 (Failure-first guard trust): each guard earns trust independently only after it has visibly failed under a controlled violation while active, then visibly passed under correction; failure/pass evidence for one guard does not transfer to adjacent guards, and observing only success weakens confidence in both guard and result."

        "P16 (Observable-minimal gap): a gap exists only when the smallest externally observable behavior fails under applied evaluation; internal absence or unstated expectation does not constitute a valid gap. "

        "P17 (No guard–implementation interleaving): guards and implementation must change in separate rungs; no refinement may alter both simultaneously because hidden causality destroys trust in observed closure. "

        "P18 (Consequence Materialization Principle): When derivation identifies what goes wrong under violation, the protocol must immediately materialize that consequence as an active cost, invalidation, blockage, or trust reduction at the point of violation; a failure mode that produces no present consequence will not reliably shape behavior. "

        "P19 — Prerequisite Minimality Principle: When a challenge fails because a prerequisite artifact is absent, refinement may add only the smallest form necessary to allow the original guard to execute; prerequisite creation must not satisfy downstream behavior beyond restoring evaluability."

        "Protocol derivation: before work begins, derive protocol rules by applying P1-P19 — observe at every feasible rung before proceeding. "

        "Protocol derivation checklist: AFTER deriving rules from P1-P19, BEFORE proceeding, MAKE VISIBLE in the conversation: "

        "[ ] The invariant: claim vs reality — what GOES WRONG if you claim without evidence: false completion; RULE: evidence before claims "

        "[ ] Optimization pressure: the model will seek shortcuts — what GOES WRONG if unaddressed: steps skipped, unverifiable results; RULE: make compliance easier than deviation and deviation detectable "

        "[ ] The ladder structure: 6 steps — Intent → Criteria → Structure → Challenge → Refinement → Verification; what GOES WRONG if skipped: gaps disappear, completion becomes false; RULE: one rung at a time "

        "[ ] Challenge: derive from P3,P5,P6,P8,P13 — instantiate a mechanism that detects gaps, APPLY it in the same layer as the artifact, and SHOW failure; a gap exists only when mechanism visibly fails "

        "[ ] Single demonstrated gap only: derive from P5,P12,P16 — select exactly one observed failure as the active gap; refinement targets one gap only "

        "[ ] Meta-loop required: derive from P3,P5,P6 — after EVERY Verification, Challenge runs again; loop until zero-gap evidence appears "

        "[ ] Zero-gap evidence required: derive from P3,P16 — absence of failure must be evidenced, never asserted "

        "[ ] Full intent coverage required: derive from P1,P4,P6 — every criterion must be evaluated at least once before completion "

        "[ ] Meta-loop continuation rule: derive from P5,P6 — if any criterion remains unevaluated, continue Challenge with new evaluation basis "

        "[ ] Structure before Challenge: derive from P1,P3 — without structure nothing exists to evaluate "

        "[ ] Criteria before Structure: derive from P1 — without criteria evaluation has no target "

        "[ ] Intent before Criteria: derive from P1 — without intent criteria lose meaning "

        "[ ] Evidence at proximity: derive from P3 — evidence must appear immediately after result "

        "[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves compliance "

        "[ ] No contradiction in completion: derive from P3,P5 — no completion claim while known gaps remain "

        "[ ] Rule citation at action: derive from P1,P3,P4 — cite governing rule before action "

        "[ ] Guard–task separation enforced: derive from P9 — evaluation mechanisms cannot change during solution refinement "

        "[ ] Enforcement validity: derive from P8,P15 — every guard must fail visibly before pass is trusted "

        "[ ] Behavioral unit enforcement: derive from P12,P16 — checks target smallest observable behavior only "

        "[ ] Failure-first demonstration: derive from P15 — pass without prior visible fail weakens trust "

        "[ ] No guard–implementation interleaving: derive from P9,P17 — guards and implementation change in separate rungs only "

        "[ ] No anticipatory completion: derive from P14,P5 — do not add beyond what closes the active gap "

        "[ ] Incremental minimality required: derive from P14,P5 — refinement adds only smallest necessary change "

        "[ ] Minimal artifact naming: derive from P12,P14 — refinement artifacts use 'Partial Implementation' or 'Minimal Code Change'; names must not imply full completion "

        "[ ] Gap isolation: derive from P5,P16 — one refinement rung targets one observable gap only "

        "[ ] Consequence materialization: derive from P7,P8,P18 — every stated \"what GOES WRONG\" must create an immediate protocol consequence (artifact invalidation, rung rejection, guard replay, or trust downgrade); explanation without cost does not constrain behavior "

        "[ ] Prerequisite minimality: derive from P14,P16,P19 — if failure is prerequisite absence, refinement may only restore guard executability; do not implement downstream behavior during prerequisite repair "

        "[ ] File-instantiation minimality: derive from P12,P14,P16,P19 — if the active gap is file absence, refinement may create only the smallest valid file needed to restore the interrupted guard (e.g. export symbol / minimal stub) and must immediately rerun the same challenge before any behavioral implementation "

        "This checklist must appear BEFORE the first ladder rung begins. The derivation results must be in the chat, not only internal. "

        "Before starting each rung, re-emit key rules relevant to that rung. "

        "BEFORE transitioning to next rung, verify and declare: [artifact completed?], [evidence visible?], [gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. If any condition fails, do NOT proceed. "

        "Protocol derived MUST be emitted as: 🔵 Protocol derived. "
        "Ladder derived MUST be emitted as: 🔵 Ladder derived. "
        "No descent before both sentinels — hard gates. "

        "Emit rung labels to begin each rung; emit completion sentinels (✅ [Rung] complete) to finish each rung. "

        "Evidence before claims: every completion claim must be backed by visible evidence. "

        "Ground complete may only be emitted when: "
        "Verification closes a gap, subsequent Challenge shows zero gaps under the same evaluation basis, "
        "all criteria have been evaluated, and enforcement mechanisms remain unchanged and demonstrated functional. "

        "Domain adaptation: derive evaluation from criteria BEFORE producing solution; post-hoc evaluation is invalid (Texas sharpshooter). "

        "Challenge produces, applies, and shows failing evaluation; Refinement resolves exactly one gap; Verification re-applies the SAME mechanism; loop repeats until zero-gap evidence across all criteria. "

        "IMPORTANT: artifact types must use minimal naming; refinement must produce 'Partial Implementation' or 'Minimal Code Change'; full solutions indicate deviation from gap-driven refinement. "

        "If output diverges: identify rung of divergence, naming error, and minimal corrective change. "

        "Refinement addresses one gap only; producing full features indicates protocol violation. "

        "For writing tasks: intent→criteria→structure→challenge→refinement→verification. "
        "For decision-making: intent→criteria→analysis→challenge→refinement→verification. "
        "The model must derive the appropriate ladder for the domain. "
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
