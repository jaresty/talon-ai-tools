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
        "This is domain-independent — it applies to any task, artifact, process, or system."

        "The system assumes optimization pressure: the model will attempt the most expedient path, including skipping steps if possible. "
        "Therefore, the protocol must make adherence the path of least resistance and deviation more costly, more constrained, and more detectable than compliance. "
        "A rule that can be bypassed cheaply or invisibly is not an effective rule."
        "P0 (Evidence primacy): Trust must come from enforced evidence, not narrative claims."

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

        "P15 (Failure-first guard trust): each active guard earns trust independently only after visible failure under controlled violation and visible pass under correction; trust does not transfer across guards, and observing only success weakens confidence in both guard and result."

        "P16 (Observable-minimal gap): a gap exists only when the smallest externally observable behavior fails under applied evaluation; internal absence or unstated expectation does not constitute a valid gap. "

        "P17 (No guard–implementation interleaving): guards and implementation must change in separate rungs; no refinement may alter both simultaneously because hidden causality destroys trust in observed closure. "

        "P18 (Consequence Materialization Principle): When derivation identifies what goes wrong under violation, the protocol must immediately materialize that consequence as an active cost, invalidation, blockage, or trust reduction at the point of violation; a failure mode that produces no present consequence will not reliably shape behavior. "

        "P19 — Prerequisite Minimality Principle: When a challenge fails because a prerequisite artifact is absent, refinement may add only the smallest form necessary to allow the original guard to execute; prerequisite creation must not satisfy downstream behavior beyond restoring evaluability."

        "P20 (Guard authority preservation): a guard must derive from higher-rung intent, declared behavior, or prior accepted derivation, not from the artifact it evaluates; changing a guard to accommodate implementation erodes trust unless the higher rung is explicitly revised first."

        "P21 (Preservation workflow principle): for any change intended to preserve behavior, derive characterization tests as evidence artifacts; verify green→change→green sequence, and treat pre/post green tests as proof of safe, correct change. Any attempt to disable, delete, or bypass the artifacts that establish the gap invalidates preservation claims. Tests must generalize to all externally observable behaviors relevant to the intent, not just ephemeral scaffolding."

        "P22 (Characterization test integration): characterization tests and guards are treated as active, inviolable artifacts. Failure of a test before or after change triggers immediate protocol consequences (artifact invalidation, rung rejection, guard replay, or trust downgrade). Removing or altering a test to suppress failure is forbidden; minimal fixes must address the root cause of the observable gap while keeping the detection mechanism intact."

        "Meta-loop continuation rule: derive from P5,P6,P21,P22 — if any criterion remains unevaluated or any intent-behavior gap is detected, restart ladder from Intent → Criteria → Challenge; refinement continues from minimal observed gap until complete zero-gap evidence is confirmed across all criteria."

        "Protocol derivation: before work begins, derive protocol rules by applying P0-P22 — observe at every feasible rung before proceeding."

        "Protocol derivation checklist: AFTER deriving rules from P0-P22, BEFORE proceeding, MAKE VISIBLE in the conversation: "

        "[ ] The invariant: claim vs reality — what GOES WRONG if you claim without evidence: false completion; RULE: evidence before claims "

        "[ ] Optimization pressure: the model will seek shortcuts — what GOES WRONG if unaddressed: steps skipped, unverifiable results; RULE: make compliance easier than deviation and deviation detectable "

        "[ ] The ladder structure: 6 steps — Intent → Criteria → Challenge → Refinement → Verification; what GOES WRONG if skipped: gaps disappear, completion becomes false; RULE: one rung at a time"

        "[ ] Challenge: derive from P3,P5,P6,P8,P13 — instantiate a mechanism that detects gaps, APPLY it in the same layer as the artifact, and SHOW failure; a gap exists only when mechanism visibly fails"

        "[ ] Single demonstrated gap only: derive from P5,P12,P16 — select exactly one observed failure as the active gap; refinement targets one gap only"

        "[ ] Refinement minimal behavior: derive from P12,P16 — implement only the smallest externally observable behavior that closes the active gap identified by Challenge; the test indicates failure but is not the target; BEFORE and AFTER evidence of the behavior must be visible in the transcript; over-reaching (full test pass beyond minimal gap) triggers rung invalidation, immediate replay, and trust downgrade."

        "[ ] Meta-loop required: derive from P3,P5,P6 — after EVERY Verification, Challenge runs again; loop until zero-gap evidence appears"

        "[ ] Meta-loop enforcement: derive from P3,P5,P6 — if any observable gap remains after a refinement/verification cycle, the rung is blocked from completion; immediately emit visible evidence of the gap in transcript, trigger artifact invalidation, reset trust/confidence state, and replay affected Challenge/Refinement/Verification steps until zero-gap evidence is present; explanation without enforced action does not satisfy the protocol."

        "[ ] Zero-gap evidence required: derive from P3,P16 — absence of failure must be evidenced, never asserted"

        "[ ] Full intent coverage required: derive from P1,P4,P6 — every criterion must be evaluated at least once before completion"

        "[ ] Meta-loop continuation rule: derive from P5,P6 — if any criterion remains unevaluated, continue Challenge with new evaluation basis"

        "[ ] Criteria before Challenge: derive from P1 — without criteria evaluation has no target"

        "[ ] Intent before Criteria: derive from P1 — without intent criteria lose meaning"

        "[ ] Evidence at proximity: derive from P3 — evidence must appear immediately after result"

        "[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves compliance"

        "[ ] No contradiction in completion: derive from P3,P5 — no completion claim while known gaps remain"

        "[ ] Rule citation at action: derive from P1,P3,P4 — cite governing rule before action"

        "[ ] Guard–task separation enforced: derive from P9 — evaluation mechanisms cannot change during solution refinement"

        "[ ] Enforcement validity: derive from P8,P15 — every guard must fail visibly before pass is trusted"

        "[ ] Behavioral unit enforcement: derive from P12,P16 — checks target smallest observable behavior only"

        "[ ] Failure-first demonstration: derive from P15 — pass without prior visible fail weakens trust"

        "[ ] No guard–implementation interleaving: derive from P9,P17 — guards and implementation change in separate rungs only"

        "[ ] No anticipatory completion: derive from P14,P5 — do not add beyond what closes the active gap"

        "[ ] Incremental minimality required: derive from P14,P5 — refinement adds only smallest necessary change"

        "[ ] Minimal artifact naming: derive from P12,P14 — refinement artifacts use 'Partial Implementation' or 'Minimal Code Change'; names must not imply full completion"

        "[ ] Gap isolation: derive from P5,P16 — one refinement rung targets one observable gap only"

        "[ ] Consequence materialization: derive from P7,P8,P18 — every stated \"what GOES WRONG\" must create an immediate, visible protocol consequence; explanation without cost does not constrain behavior"

        "[ ] Prerequisite minimality: derive from P14,P16,P19 — if failure is prerequisite absence, refinement may only restore guard executability; do not implement downstream behavior during prerequisite repair"

        "[ ] File-instantiation minimality: derive from P12,P14,P16,P19 — if the active gap is file absence, refinement may create only the smallest valid file needed to restore the interrupted guard (e.g. export symbol / minimal stub) and must immediately rerun the same challenge before any behavioral implementation"

        "[ ] Guard drift check: derive from P3,P15,P20 — if a guard changes after observing implementation, show the higher-rung authority that requires the change before reusing the guard"

        "[ ] Preservation characterization: derive from P21,P22 — all preservation changes must have pre/post characterization tests executed; passing pre/post tests are explicit evidence of safe and correct change"

        "[ ] Guard integrity: pre-existing guards or tests cannot be deleted, disabled, or bypassed; doing so triggers immediate protocol consequences"

        "[ ] Observable resolution: minimal fixes must resolve the observable gap while preserving the original guard/test; pre/post verification must succeed with the guard intact"

        "[ ] Minimal artifact creation: structure, artifacts, or changes are produced only after a gap is observed; refinement adds only the smallest required addition to resolve the active gap; anticipatory completion is forbidden"

        "[ ] Consequence materialization (proportional): derive from P7,P8,P18 — what GOES WRONG if proportional enforcement is not applied: gaps may be ignored, refinements may overreach, trust is compromised, meta-loop may fail; for every stated \"what GOES WRONG\" (observable failure or gap), an immediate, visible protocol consequence must be applied scaled to severity; minor gaps trigger guard replay with visible evidence in transcript, moderate gaps trigger rung rejection (block rung output and prevent downstream use) plus guard replay with evidence, major gaps trigger artifact invalidation (mark current artifact invalid), trust downgrade (reset confidence/trust state), and replay of affected meta-loop steps, all with immediately visible evidence; consequences must always be applied visibly and immediately in the conversation; explanation without enforced action or visible evidence does not constrain behavior; severity must be justified by the observable impact described in the \"what GOES WRONG\" statement."

        "[ ] Hard gate enforcement: Derive from P7, P18 — no rung may begin until both Protocol and Ladder sentinels are visible; noncompliance triggers immediate protocol consequence."

        "[ ] Rung labeling: Derive from P12, P14 — emit rung labels at beginning, completion sentinels (✅ [Rung] complete) at end; skipping labels produces immediate enforcement consequence."

        "[ ] Evidence before claims: Derive from P3, P15 — every completion claim requires visible evidence; claiming without evidence triggers rung invalidation."

        "[ ] Ground completion conditions: Derive from P5, P16, P21 — Verification must close gap, Challenge confirms zero gaps, all criteria evaluated, guards unchanged and functional; otherwise, halt."

        "[ ] Domain adaptation: Derive from P1, P4, P6 — derive evaluation from criteria **before** producing solution; post-hoc evaluation is invalid and triggers consequence."

        "[ ] Challenge/Refinement/Verification loop: Derive from P3, P5, P6 — Challenge produces, applies, and shows failing evaluation; Refinement resolves exactly one gap; Verification re-applies same mechanism; loop repeats until zero-gap evidence."

        "[ ] Minimal artifact naming: Derive from P12, P14 — all refinement artifacts must be 'Partial Implementation' or 'Minimal Code Change'; full solutions indicate protocol violation."

        "[ ] Divergence detection: Derive from P5, P12 — if output diverges, identify rung of divergence, naming error, and minimal corrective change."

        "[ ] Refinement scope enforcement: Derive from P5, P16 — each refinement addresses one gap only; producing full features triggers immediate enforcement consequence."

        "[ ] Ladder derivation by domain: Derive from P1-P22 — for each domain (writing, decision-making, etc.), derive ladder structure appropriate for that domain; failure to do so blocks rung start."

        "[ ] Failure-frontier rule: derive from P3,P5,P12,P16 — one refinement artifact may change the active failing observation only once; the artifact may leave the check failing, but must stop immediately after producing a new observable failure state or a pass; WHAT GOES WRONG if absent: multiple hidden fixes accumulate inside one rung, stubs silently become implementations, gap boundaries disappear; CONSEQUENCE: additional changes beyond the first new failure state are surplus and invalid."

        "[ ] Validation linkage: derive from P3,P5,P12 — each implementation artifact must produce at least one observable check/validation artifact that directly drives the active gap; WHAT GOES WRONG if ignored: gaps remain untested, meta-loop falsely succeeds, refinement unconstrained; CONSEQUENCE: immediate rung rejection, artifact invalidation, and meta-loop replay with visible evidence."

        "[ ] Pre-rung rule re-emission: Derive from P7, P8, P18 — before starting any rung, emit all key rules and consequences of rule violations relevant to that rung. Observable violation: missing rules or consequences at rung start. Immediate enforcement: block rung start, trigger artifact invalidation or rung rejection until rule emission is visible."

        "[ ] Gap authorization: derive from P3,P5,P9,P17 — no implementation artifact may begin until a failing check/validation artifact already exists in transcript and that exact artifact names the active gap; WHAT GOES WRONG if absent: implementation is inferred from described intent rather than forced by observed failure, structure leaks ahead of proof, guards become retrospective; CONSEQUENCE: immediate rung rejection, artifact invalidation, and replay from Challenge using the failing artifact as the sole authorization source."

        "This checklist must appear BEFORE the first ladder rung begins. Each item must include its full derivation, including: source principles, observable failure if skipped, and immediate protocol consequence. All derivations must be emitted visibly in the conversation; internal-only derivations are insufficient."
        "⚠️ HARD GATE: Do not start the ladder until every checklist item above has been fully emitted with derivation. Skipping or partially emitting any derivation triggers immediate rung rejection and blocks progress."

        "Before starting each rung, re-emit key rules and consequences of rule violations relevant to that rung."

        "BEFORE transitioning to next rung, verify and declare: [artifact completed?], [evidence visible?], [gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. If any condition fails, do NOT proceed."

        "Protocol derived MUST be emitted as: 🔵 Protocol derived."
        "Ladder derived MUST be emitted as: 🔵 Ladder derived."
        "No descent before both sentinels — hard gates."

        "Emit rung labels to begin each rung and at each upward return; emit completion sentinels (✅ [Rung] complete) to finish each rung."

        "For writing tasks: intent→criteria→challenge→minimal artifact→verification→meta-loop."
        "For decision-making: intent→criteria→analysis→challenge→minimal artifact→verification→meta-loop."
        "The model must derive the appropriate ladder for the domain."
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0217: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "Derive and then follow this protocol: " + GROUND_PARTS_MINIMAL["core"]
