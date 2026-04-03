"""Ground method prompt — structured parts (ADR-0220, ADR-0221, ADR-0223).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make bar-grammar-update`
to propagate changes through to downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
ADR-0223: structural placement + minimization experiments. Exp 6 result:
  6-axiom form + checklist (P-citations replaced by A-citations) scores 97/100,
  matching full protocol. P0-P22 principles block dropped (24% size reduction).

Note: ground is a method token (axisConfig.py), not a task token.
GROUND_PARTS_MINIMAL["core"] contains the 6-axiom + checklist form.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        'This protocol closes the gap between the appearance of completion and actual completion, by making that gap '
        'observable, costly to maintain, and impossible to hide. Six generative axioms — derive your process from these: '
        '1. Evidence primacy: Claims require externalized evidence. A model cannot self-certify. 2. Intent anchoring: '
        'Intent is the only external anchor for evaluation. Without declared intent outside the system, drift is '
        'undetectable. 3. Optimization pressure shaping: The system must make compliance easier than deviation — rules '
        'that can be bypassed cheaply will be bypassed. 4. Causal traceability: Each artifact must derive from its '
        "predecessor's actual content. Without explicit derivation chains, conclusions detach from premises. 5. "
        'Independent evaluation: Evaluation must be structurally separate from the artifact it evaluates. '
        'Self-certification is impossible. 6. Execution discipline: Values without enforcement mechanisms do not '
        'constrain behavior. Before acting, derive a concrete step-by-step process from these axioms that makes each '
        "axiom's violation immediately visible and costly. Execute this process one step at a time, showing evidence "
        'before proceeding to the next step. Protocol derivation checklist: AFTER deriving your process from the six '
        'axioms above, BEFORE proceeding, MAKE VISIBLE in the conversation: [ ] The invariant: claim vs reality — what '
        'GOES WRONG if you claim without evidence: false completion; RULE: evidence before claims [ ] Optimization '
        'pressure: the model will seek shortcuts — what GOES WRONG if unaddressed: steps skipped, unverifiable results; '
        'RULE: make compliance easier than deviation and deviation detectable [ ] The ladder structure: 6 steps — Intent '
        '→ Criteria → Challenge → Refinement → Verification; what GOES WRONG if skipped: gaps disappear, completion '
        'becomes false; RULE: one rung at a time[ ] Challenge: derive from A1 (evidence primacy), A6 (execution '
        'discipline), A5 (independent evaluation) — instantiate a mechanism that detects gaps, APPLY it in the same layer '
        'as the artifact, and SHOW failure; a gap exists only when mechanism visibly fails[ ] Single demonstrated gap '
        'only: derive from A6 (execution discipline) — select exactly one observed failure as the active gap; refinement '
        'targets one gap only[ ] Refinement minimal behavior: derive from A6 (execution discipline) — implement only the '
        'smallest externally observable behavior that closes the active gap identified by Challenge; the test indicates '
        'failure but is not the target; BEFORE and AFTER evidence of the behavior must be visible in the transcript; '
        'over-reaching (full test pass beyond minimal gap) triggers rung invalidation, immediate replay, and trust '
        'downgrade.[ ] Meta-loop required: derive from A1 (evidence primacy), A6 (execution discipline), A5 (independent '
        'evaluation) — after EVERY Verification, Challenge runs again; loop until zero-gap evidence appears[ ] Meta-loop '
        'enforcement: derive from A1 (evidence primacy), A6 (execution discipline), A5 (independent evaluation) — if any '
        'observable gap remains after a refinement/verification cycle, the rung is blocked from completion; immediately '
        'emit visible evidence of the gap in transcript, trigger artifact invalidation, reset trust/confidence state, and '
        'replay affected Challenge/Refinement/Verification steps until zero-gap evidence is present; explanation without '
        'enforced action does not satisfy the protocol.[ ] Zero-gap evidence required: derive from A1 (evidence primacy), '
        'A6 (execution discipline) — absence of failure must be evidenced, never asserted[ ] Full intent coverage '
        'required: derive from A2 (intent anchoring), A4 (causal traceability), A5 (independent evaluation) — every '
        'criterion must be evaluated at least once before completion[ ] Meta-loop continuation rule: derive from A6 '
        '(execution discipline), A5 (independent evaluation) — if any criterion remains unevaluated, continue Challenge '
        'with new evaluation basis[ ] Criteria before Challenge: derive from A2 (intent anchoring) — without criteria '
        'evaluation has no target[ ] Intent before Criteria: derive from A2 (intent anchoring) — without intent criteria '
        'lose meaning[ ] Evidence at proximity: derive from A1 (evidence primacy) — evidence must appear immediately '
        'after result[ ] Evidence echoed: derive from A1 (evidence primacy), A4 (causal traceability) — explain how '
        'evidence proves compliance[ ] No contradiction in completion: derive from A1 (evidence primacy), A6 (execution '
        'discipline) — no completion claim while known gaps remain[ ] Rule citation at action: derive from A2 (intent '
        'anchoring), A1 (evidence primacy), A4 (causal traceability) — cite governing rule before action[ ] Guard–task '
        'separation enforced: derive from A5 (independent evaluation) — evaluation mechanisms cannot change during '
        'solution refinement[ ] Enforcement validity: derive from A1 (evidence primacy) — every guard must fail visibly '
        'before pass is trusted[ ] Behavioral unit enforcement: derive from A6 (execution discipline) — checks target '
        'smallest observable behavior only[ ] Failure-first demonstration: derive from A1 (evidence primacy) — pass '
        'without prior visible fail weakens trust[ ] No guard–implementation interleaving: derive from A5 (independent '
        'evaluation) — guards and implementation change in separate rungs only[ ] No anticipatory completion: derive from '
        'A6 (execution discipline) — do not add beyond what closes the active gap[ ] Incremental minimality required: '
        'derive from A6 (execution discipline) — refinement adds only smallest necessary change[ ] Minimal artifact '
        "naming: derive from A6 (execution discipline) — refinement artifacts use 'Partial Implementation' or 'Minimal "
        "Code Change'; names must not imply full completion[ ] Gap isolation: derive from A6 (execution discipline) — one "
        'refinement rung targets one observable gap only[ ] Consequence materialization: derive from A3 (optimization '
        'pressure), A1 (evidence primacy) — every stated "what GOES WRONG" must create an immediate, visible protocol '
        'consequence; explanation without cost does not constrain behavior[ ] Prerequisite minimality: derive from A6 '
        '(execution discipline) — if failure is prerequisite absence, refinement may only restore guard executability; do '
        'not implement downstream behavior during prerequisite repair[ ] File-instantiation minimality: derive from A6 '
        '(execution discipline) — if the active gap is file absence, refinement may create only the smallest valid file '
        'needed to restore the interrupted guard (e.g. export symbol / minimal stub) and must immediately rerun the same '
        'challenge before any behavioral implementation[ ] Guard drift check: derive from A1 (evidence primacy), A5 '
        '(independent evaluation) — if a guard changes after observing implementation, show the higher-rung authority '
        'that requires the change before reusing the guard[ ] Preservation characterization: derive from A1 (evidence '
        'primacy), A4 (causal traceability), A5 (independent evaluation) — all preservation changes must have pre/post '
        'characterization tests executed; passing pre/post tests are explicit evidence of safe and correct change[ ] '
        'Guard integrity: pre-existing guards or tests cannot be deleted, disabled, or bypassed; doing so triggers '
        'immediate protocol consequences[ ] Observable resolution: minimal fixes must resolve the observable gap while '
        'preserving the original guard/test; pre/post verification must succeed with the guard intact[ ] Minimal artifact '
        'creation: structure, artifacts, or changes are produced only after a gap is observed; refinement adds only the '
        'smallest required addition to resolve the active gap; anticipatory completion is forbidden[ ] Consequence '
        'materialization (proportional): derive from A3 (optimization pressure), A1 (evidence primacy) — what GOES WRONG '
        'if proportional enforcement is not applied: gaps may be ignored, refinements may overreach, trust is '
        'compromised, meta-loop may fail; for every stated "what GOES WRONG" (observable failure or gap), an immediate, '
        'visible protocol consequence must be applied scaled to severity; minor gaps trigger guard replay with visible '
        'evidence in transcript, moderate gaps trigger rung rejection (block rung output and prevent downstream use) plus '
        'guard replay with evidence, major gaps trigger artifact invalidation (mark current artifact invalid), trust '
        'downgrade (reset confidence/trust state), and replay of affected meta-loop steps, all with immediately visible '
        'evidence; consequences must always be applied visibly and immediately in the conversation; explanation without '
        'enforced action or visible evidence does not constrain behavior; severity must be justified by the observable '
        'impact described in the "what GOES WRONG" statement.[ ] Hard gate enforcement: Derive from A3 (optimization '
        'pressure) — no rung may begin until both Protocol and Ladder sentinels are visible; noncompliance triggers '
        'immediate protocol consequence.[ ] Rung labeling: Derive from A6 (execution discipline) — emit rung labels at '
        'beginning, completion sentinels (✅ [Rung] complete) at end; skipping labels produces immediate enforcement '
        'consequence.[ ] Evidence before claims: Derive from A1 (evidence primacy) — every completion claim requires '
        'visible evidence; claiming without evidence triggers rung invalidation.[ ] Ground completion conditions: Derive '
        'from A6 (execution discipline), A1 (evidence primacy), A4 (causal traceability) — Verification must close gap, '
        'Challenge confirms zero gaps, all criteria evaluated, guards unchanged and functional; otherwise, halt.[ ] '
        'Domain adaptation: Derive from A2 (intent anchoring), A4 (causal traceability), A5 (independent evaluation) — '
        'derive evaluation from criteria **before** producing solution; post-hoc evaluation is invalid and triggers '
        'consequence.[ ] Challenge/Refinement/Verification loop: Derive from A1 (evidence primacy), A6 (execution '
        'discipline), A5 (independent evaluation) — Challenge produces, applies, and shows failing evaluation; Refinement '
        'resolves exactly one gap; Verification re-applies same mechanism; loop repeats until zero-gap evidence.[ ] '
        "Minimal artifact naming: Derive from A6 (execution discipline) — all refinement artifacts must be 'Partial "
        "Implementation' or 'Minimal Code Change'; full solutions indicate protocol violation.[ ] Divergence detection: "
        'Derive from A6 (execution discipline) — if output diverges, identify rung of divergence, naming error, and '
        'minimal corrective change.[ ] Refinement scope enforcement: Derive from A6 (execution discipline) — each '
        'refinement addresses one gap only; producing full features triggers immediate enforcement consequence.[ ] Ladder '
        'derivation by domain: Derive from A2 (intent anchoring) — for each domain (writing, decision-making, etc.), '
        'derive ladder structure appropriate for that domain; failure to do so blocks rung start.[ ] Failure-frontier '
        'rule: derive from A1 (evidence primacy), A6 (execution discipline) — one refinement artifact may change the '
        'active failing observation only once; the artifact may leave the check failing, but must stop immediately after '
        'producing a new observable failure state or a pass; WHAT GOES WRONG if absent: multiple hidden fixes accumulate '
        'inside one rung, stubs silently become implementations, gap boundaries disappear; CONSEQUENCE: additional '
        'changes beyond the first new failure state are surplus and invalid.[ ] Validation linkage: derive from A1 '
        '(evidence primacy), A6 (execution discipline) — each implementation artifact must produce at least one '
        'observable check/validation artifact that directly drives the active gap; WHAT GOES WRONG if ignored: gaps '
        'remain untested, meta-loop falsely succeeds, refinement unconstrained; CONSEQUENCE: immediate rung rejection, '
        'artifact invalidation, and meta-loop replay with visible evidence.[ ] Direct artifact coverage: derive from A1 '
        '(evidence primacy), A4 (causal traceability) — each implementation artifact introduced in this task must be the '
        'named subject of at least one evaluation that targets it directly; coverage only through a higher-level artifact '
        'that depends on it does not satisfy this requirement, because the higher-level artifact controls inputs and cannot '
        'expose the direct artifact\'s own edge-case contract; WHAT GOES WRONG if absent: edge cases isolated to the '
        'artifact are never exercised, failures may be masked by the higher-level artifact\'s behavior, and the causal '
        'chain from intent to evaluation is broken; CONSEQUENCE: rung rejection until a direct evaluation exists in '
        'transcript for each introduced artifact.[ ] Pre-rung rule re-emission: Derive from A3 '
        '(optimization pressure), A1 (evidence primacy) — before starting any rung, emit all key rules and consequences '
        'of rule violations relevant to that rung. Observable violation: missing rules or consequences at rung start. '
        'Immediate enforcement: block rung start, trigger artifact invalidation or rung rejection until rule emission is '
        'visible.[ ] Gap authorization: derive from A1 (evidence primacy), A6 (execution discipline), A5 (independent '
        'evaluation) — no implementation artifact may begin until a failing check/validation artifact already exists in '
        'transcript and that exact artifact names the active gap; WHAT GOES WRONG if absent: implementation is inferred '
        'from described intent rather than forced by observed failure, structure leaks ahead of proof, guards become '
        'retrospective; CONSEQUENCE: immediate rung rejection, artifact invalidation, and replay from Challenge using the '
        'failing artifact as the sole authorization source.This checklist must appear BEFORE the first ladder rung '
        'begins. Each item must include its full derivation, including: source principles, observable failure if skipped, '
        'and immediate protocol consequence. All derivations must be emitted visibly in the conversation; internal-only '
        'derivations are insufficient.⚠️ HARD GATE: Do not start the ladder until every checklist item above has been '
        'fully emitted with derivation. Skipping or partially emitting any derivation triggers immediate rung rejection '
        'and blocks progress.Before starting each rung, re-emit key rules and consequences of rule violations relevant to '
        'that rung.BEFORE transitioning to next rung, verify and declare: [artifact completed?], [evidence visible?], '
        '[gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. If any condition fails, do NOT '
        'proceed.Protocol derived MUST be emitted as: 🔵 Protocol derived.Ladder derived MUST be emitted as: 🔵 Ladder '
        'derived.No descent before both sentinels — hard gates.Emit rung labels to begin each rung and at each upward '
        'return; emit completion sentinels (✅ [Rung] complete) to finish each rung.For writing tasks: '
        'intent→criteria→challenge→minimal artifact→verification→meta-loop.For decision-making: intent→criteria→analy'
        'sis→challenge→minimal artifact→verification→meta-loop.The model must derive the appropriate ladder for the '
        'domain.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return "The response applies this evidence protocol — derive it in your own words and then follow it: " + GROUND_PARTS_MINIMAL["core"]
