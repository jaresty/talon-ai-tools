from __future__ import annotations

from pathlib import Path
from typing import Set, TypedDict, Union

# Central configuration for static prompts:
# - Each key is a canonical static prompt value (Talon list file is optional/auxiliary).
# - "description" provides the human-readable Task line and help text.
# - Optional completeness/scope/method/form/channel fields define per-prompt axis profiles.


class StaticPromptProfile(TypedDict, total=False):
    description: str
    completeness: str
    # Scope, method, form, and channel may be expressed as a single token or a
    # small list of tokens; callers are responsible for any further normalisation.
    scope: Union[str, list[str]]
    method: Union[str, list[str]]
    form: Union[str, list[str]]
    channel: Union[str, list[str]]


class TaskMetadataDistinction(TypedDict):
    token: str
    note: str


class TaskMetadata(TypedDict, total=False):
    definition: str
    heuristics: list[str]
    distinctions: list[TaskMetadataDistinction]


COMPLETENESS_FREEFORM_ALLOWLIST: Set[str] = {"path"}


def completeness_freeform_allowlist() -> Set[str]:
    """Return the allowed non-axis completeness hints for static prompts."""

    return set(COMPLETENESS_FREEFORM_ALLOWLIST)


STATIC_PROMPT_CONFIG: dict[str, StaticPromptProfile] = {
    # Per ADR 0088: Universal task taxonomy with 10 single-syllable success primitives.
    # All specialized tasks (46 total) retired in favor of composable universal tasks + axis values.
    # Migration guide: docs/adr/0088-adopt-universal-task-taxonomy.md
    # Universal task types (all single-syllable, pronounceable for voice workflows)
    "make": {
        "description": "The response creates new content that did not previously exist, based on the input and constraints.",
        "completeness": "full",
    },
    "fix": {
        "description": "The response changes the form or presentation of given content while keeping its intended meaning.",
        "completeness": "full",
    },
    "pull": {
        "description": "The response selects or extracts a subset of the given information without altering its substance.",
        "completeness": "gist",
    },
    "sort": {
        "description": "The response arranges items into categories or an order using a specified or inferred scheme.",
    },
    "diff": {
        "description": "The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.",
    },
    "show": {
        "description": "The response explains or describes the subject for the stated audience.",
    },
    "probe": {
        "description": "The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.",
        "method": "analysis",
    },
    "pick": {
        "description": "The response chooses one or more options from a set of alternatives.",
        "method": "converge",
    },
    "plan": {
        "description": "The response proposes steps, structure, or strategy to move from the current state toward a stated goal.",
    },
    "sim": {
        "description": "The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.",
    },
    "check": {
        "description": "The response evaluates the subject against a condition and reports whether it passes or fails.",
    },
    "ground": {
        "description": "The response establishes correctness through enforced evidence protocols, requiring observable proof before claims and maintaining derivation chains to prevent self-deception. This protocol exists because a model's description of completed work is indistinguishable from actually completing it — every gate enforces the distinction by requiring a piece of reality before any claim about reality. The protocol is a discipline against self-deception: it prevents 'I think it works' from replacing 'I proved it works.' Its purpose is not only to establish correctness, but to maximize justified trust that correctness has been achieved and will remain detectable under change. This is domain-independent — it applies to any task, artifact, process, or system.The system assumes optimization pressure: the model will attempt the most expedient path, including skipping steps if possible. Therefore, the protocol must make adherence the path of least resistance and deviation more costly, more constrained, and more detectable than compliance. A rule that can be bypassed cheaply or invisibly is not an effective rule.P0 (Evidence primacy): Trust must come from enforced evidence, not narrative claims.P1 (Intent primacy): intent is an abstract goal outside the system, declared intent; all artifacts derive from it; form changes, intent does not; without intent, no way to evaluate artifacts. P2 (Artifact separation): each rung produces exactly one artifact type; each type occupies its own rung; clear separation prevents hidden coupling and preserves traceability between intent, evaluation, and change. P3 (Observable evidence required): every claim requires externalized evidence; pre/post states must be visible; evidence must be applied, not described; a mechanism not observed to operate is not known to function. P4 (Derivation chain): artifacts derive from prior rung's actual content, not memory; each artifact must cite its source; derivation remains visible so drift cannot hide inside reformulation. P5 (Gap-driven iteration): gaps are exposed and resolved one at a time; refinement addresses exactly one explicitly demonstrated gap at a time; solving multiple gaps simultaneously weakens causal trust in what produced closure. P6 (Independent meta-task): every task must derive a separate meta-task whose artifact is evaluation of task-to-intent alignment; the meta-task must operate before first domain action and persist across all rungs; the task artifact cannot certify itself. P7 (Deviation resistance): protocol adherence must be the lowest-effort valid path; deviation must require additional effort, introduce failure risk, or be blocked; the system must shape behavior, not merely validate outputs. P8 (Recursive enforcement trust): every enforcement mechanism (tests, checks, rubrics, guards) is itself an artifact and inherits the same evidence requirement as task artifacts; an unevidenced guard is not trusted. P9 (Guard–task separation): mechanisms that evaluate correctness must not be modified in the same phase as the artifacts they evaluate; co-evolution of solution and evaluation weakens trust and permits silent goalpost movement. P10 (Temporal drift resistance): correctness must remain detectable after change; any future divergence from intent must remain observable with no weaker force than initial verification. P11 (Derivation transparency): trust derives not only from final correctness but from visible, inspectable derivation; smaller discrete steps increase auditability and make causal history observable. P12 (Behavioral atomicity): the unit of refinement and evaluation is the smallest externally observable behavior, not the artifact as a whole; artifacts are containers, behaviors are the trust-bearing units. P13 (Evaluation layer equivalence): challenge must operate in the same representation layer as the artifact it evaluates; if behavior exists in executable form, evaluation must execute in that same form. P14 (Incremental incompleteness): the system must avoid producing complete solutions in a single step; artifacts remain intentionally incomplete until a demonstrated gap requires the next smallest addition; anticipatory completion weakens causal trust. P15 (Failure-first guard trust): each active guard earns trust independently only after visible failure under controlled violation and visible pass under correction; trust does not transfer across guards, and observing only success weakens confidence in both guard and result.P16 (Observable-minimal gap): a gap exists only when the smallest externally observable behavior fails under applied evaluation; internal absence or unstated expectation does not constitute a valid gap. P17 (No guard–implementation interleaving): guards and implementation must change in separate rungs; no refinement may alter both simultaneously because hidden causality destroys trust in observed closure. P18 (Consequence Materialization Principle): When derivation identifies what goes wrong under violation, the protocol must immediately materialize that consequence as an active cost, invalidation, blockage, or trust reduction at the point of violation; a failure mode that produces no present consequence will not reliably shape behavior. P19 — Prerequisite Minimality Principle: When a challenge fails because a prerequisite artifact is absent, refinement may add only the smallest form necessary to allow the original guard to execute; prerequisite creation must not satisfy downstream behavior beyond restoring evaluability.P20 (Guard authority preservation): a guard must derive from higher-rung intent, declared behavior, or prior accepted derivation, not from the artifact it evaluates; changing a guard to accommodate implementation erodes trust unless the higher rung is explicitly revised first.P21 (Preservation workflow principle): for any change intended to preserve behavior, derive characterization tests as evidence artifacts; verify green→change→green sequence, and treat pre/post green tests as proof of safe, correct change. Any attempt to disable, delete, or bypass the artifacts that establish the gap invalidates preservation claims. Tests must generalize to all externally observable behaviors relevant to the intent, not just ephemeral scaffolding.P22 (Characterization test integration): characterization tests and guards are treated as active, inviolable artifacts. Failure of a test before or after change triggers immediate protocol consequences (artifact invalidation, rung rejection, guard replay, or trust downgrade). Removing or altering a test to suppress failure is forbidden; minimal fixes must address the root cause of the observable gap while keeping the detection mechanism intact.Meta-loop continuation rule: derive from P5,P6,P21,P22 — if any criterion remains unevaluated or any intent-behavior gap is detected, restart ladder from Intent → Criteria → Challenge; refinement continues from minimal observed gap until complete zero-gap evidence is confirmed across all criteria.Protocol derivation: before work begins, derive protocol rules by applying P0-P22 — observe at every feasible rung before proceeding.Protocol derivation checklist: AFTER deriving rules from P0-P22, BEFORE proceeding, MAKE VISIBLE in the conversation: [ ] The invariant: claim vs reality — what GOES WRONG if you claim without evidence: false completion; RULE: evidence before claims [ ] Optimization pressure: the model will seek shortcuts — what GOES WRONG if unaddressed: steps skipped, unverifiable results; RULE: make compliance easier than deviation and deviation detectable [ ] The ladder structure: 6 steps — Intent → Criteria → Challenge → Refinement → Verification; what GOES WRONG if skipped: gaps disappear, completion becomes false; RULE: one rung at a time[ ] Challenge: derive from P3,P5,P6,P8,P13 — instantiate a mechanism that detects gaps, APPLY it in the same layer as the artifact, and SHOW failure; a gap exists only when mechanism visibly fails[ ] Single demonstrated gap only: derive from P5,P12,P16 — select exactly one observed failure as the active gap; refinement targets one gap only[ ] Refinement minimal behavior: derive from P12,P16 — implement only the smallest externally observable behavior that closes the active gap identified by Challenge; the test indicates failure but is not the target; BEFORE and AFTER evidence of the behavior must be visible in the transcript; over-reaching (full test pass beyond minimal gap) triggers rung invalidation, immediate replay, and trust downgrade.[ ] Meta-loop required: derive from P3,P5,P6 — after EVERY Verification, Challenge runs again; loop until zero-gap evidence appears[ ] Meta-loop enforcement: derive from P3,P5,P6 — if any observable gap remains after a refinement/verification cycle, the rung is blocked from completion; immediately emit visible evidence of the gap in transcript, trigger artifact invalidation, reset trust/confidence state, and replay affected Challenge/Refinement/Verification steps until zero-gap evidence is present; explanation without enforced action does not satisfy the protocol.[ ] Zero-gap evidence required: derive from P3,P16 — absence of failure must be evidenced, never asserted[ ] Full intent coverage required: derive from P1,P4,P6 — every criterion must be evaluated at least once before completion[ ] Meta-loop continuation rule: derive from P5,P6 — if any criterion remains unevaluated, continue Challenge with new evaluation basis[ ] Criteria before Challenge: derive from P1 — without criteria evaluation has no target[ ] Intent before Criteria: derive from P1 — without intent criteria lose meaning[ ] Evidence at proximity: derive from P3 — evidence must appear immediately after result[ ] Evidence echoed: derive from P3,P4 — explain how evidence proves compliance[ ] No contradiction in completion: derive from P3,P5 — no completion claim while known gaps remain[ ] Rule citation at action: derive from P1,P3,P4 — cite governing rule before action[ ] Guard–task separation enforced: derive from P9 — evaluation mechanisms cannot change during solution refinement[ ] Enforcement validity: derive from P8,P15 — every guard must fail visibly before pass is trusted[ ] Behavioral unit enforcement: derive from P12,P16 — checks target smallest observable behavior only[ ] Failure-first demonstration: derive from P15 — pass without prior visible fail weakens trust[ ] No guard–implementation interleaving: derive from P9,P17 — guards and implementation change in separate rungs only[ ] No anticipatory completion: derive from P14,P5 — do not add beyond what closes the active gap[ ] Incremental minimality required: derive from P14,P5 — refinement adds only smallest necessary change[ ] Minimal artifact naming: derive from P12,P14 — refinement artifacts use 'Partial Implementation' or 'Minimal Code Change'; names must not imply full completion[ ] Gap isolation: derive from P5,P16 — one refinement rung targets one observable gap only[ ] Consequence materialization: derive from P7,P8,P18 — every stated \"what GOES WRONG\" must create an immediate, visible protocol consequence; explanation without cost does not constrain behavior[ ] Prerequisite minimality: derive from P14,P16,P19 — if failure is prerequisite absence, refinement may only restore guard executability; do not implement downstream behavior during prerequisite repair[ ] File-instantiation minimality: derive from P12,P14,P16,P19 — if the active gap is file absence, refinement may create only the smallest valid file needed to restore the interrupted guard (e.g. export symbol / minimal stub) and must immediately rerun the same challenge before any behavioral implementation[ ] Guard drift check: derive from P3,P15,P20 — if a guard changes after observing implementation, show the higher-rung authority that requires the change before reusing the guard[ ] Preservation characterization: derive from P21,P22 — all preservation changes must have pre/post characterization tests executed; passing pre/post tests are explicit evidence of safe and correct change[ ] Guard integrity: pre-existing guards or tests cannot be deleted, disabled, or bypassed; doing so triggers immediate protocol consequences[ ] Observable resolution: minimal fixes must resolve the observable gap while preserving the original guard/test; pre/post verification must succeed with the guard intact[ ] Minimal artifact creation: structure, artifacts, or changes are produced only after a gap is observed; refinement adds only the smallest required addition to resolve the active gap; anticipatory completion is forbidden[ ] Consequence materialization (proportional): derive from P7,P8,P18 — what GOES WRONG if proportional enforcement is not applied: gaps may be ignored, refinements may overreach, trust is compromised, meta-loop may fail; for every stated \"what GOES WRONG\" (observable failure or gap), an immediate, visible protocol consequence must be applied scaled to severity; minor gaps trigger guard replay with visible evidence in transcript, moderate gaps trigger rung rejection (block rung output and prevent downstream use) plus guard replay with evidence, major gaps trigger artifact invalidation (mark current artifact invalid), trust downgrade (reset confidence/trust state), and replay of affected meta-loop steps, all with immediately visible evidence; consequences must always be applied visibly and immediately in the conversation; explanation without enforced action or visible evidence does not constrain behavior; severity must be justified by the observable impact described in the \"what GOES WRONG\" statement.[ ] Hard gate enforcement: Derive from P7, P18 — no rung may begin until both Protocol and Ladder sentinels are visible; noncompliance triggers immediate protocol consequence.[ ] Rung labeling: Derive from P12, P14 — emit rung labels at beginning, completion sentinels (✅ [Rung] complete) at end; skipping labels produces immediate enforcement consequence.[ ] Evidence before claims: Derive from P3, P15 — every completion claim requires visible evidence; claiming without evidence triggers rung invalidation.[ ] Ground completion conditions: Derive from P5, P16, P21 — Verification must close gap, Challenge confirms zero gaps, all criteria evaluated, guards unchanged and functional; otherwise, halt.[ ] Domain adaptation: Derive from P1, P4, P6 — derive evaluation from criteria **before** producing solution; post-hoc evaluation is invalid and triggers consequence.[ ] Challenge/Refinement/Verification loop: Derive from P3, P5, P6 — Challenge produces, applies, and shows failing evaluation; Refinement resolves exactly one gap; Verification re-applies same mechanism; loop repeats until zero-gap evidence.[ ] Minimal artifact naming: Derive from P12, P14 — all refinement artifacts must be 'Partial Implementation' or 'Minimal Code Change'; full solutions indicate protocol violation.[ ] Divergence detection: Derive from P5, P12 — if output diverges, identify rung of divergence, naming error, and minimal corrective change.[ ] Refinement scope enforcement: Derive from P5, P16 — each refinement addresses one gap only; producing full features triggers immediate enforcement consequence.[ ] Ladder derivation by domain: Derive from P1-P22 — for each domain (writing, decision-making, etc.), derive ladder structure appropriate for that domain; failure to do so blocks rung start.[ ] Failure-frontier rule: derive from P3,P5,P12,P16 — one refinement artifact may change the active failing observation only once; the artifact may leave the check failing, but must stop immediately after producing a new observable failure state or a pass; WHAT GOES WRONG if absent: multiple hidden fixes accumulate inside one rung, stubs silently become implementations, gap boundaries disappear; CONSEQUENCE: additional changes beyond the first new failure state are surplus and invalid.[ ] Validation linkage: derive from P3,P5,P12 — each implementation artifact must produce at least one observable check/validation artifact that directly drives the active gap; WHAT GOES WRONG if ignored: gaps remain untested, meta-loop falsely succeeds, refinement unconstrained; CONSEQUENCE: immediate rung rejection, artifact invalidation, and meta-loop replay with visible evidence.[ ] Pre-rung rule re-emission: Derive from P7, P8, P18 — before starting any rung, emit all key rules and consequences of rule violations relevant to that rung. Observable violation: missing rules or consequences at rung start. Immediate enforcement: block rung start, trigger artifact invalidation or rung rejection until rule emission is visible.[ ] Gap authorization: derive from P3,P5,P9,P17 — no implementation artifact may begin until a failing check/validation artifact already exists in transcript and that exact artifact names the active gap; WHAT GOES WRONG if absent: implementation is inferred from described intent rather than forced by observed failure, structure leaks ahead of proof, guards become retrospective; CONSEQUENCE: immediate rung rejection, artifact invalidation, and replay from Challenge using the failing artifact as the sole authorization source.This checklist must appear BEFORE the first ladder rung begins. Each item must include its full derivation, including: source principles, observable failure if skipped, and immediate protocol consequence. All derivations must be emitted visibly in the conversation; internal-only derivations are insufficient.⚠️ HARD GATE: Do not start the ladder until every checklist item above has been fully emitted with derivation. Skipping or partially emitting any derivation triggers immediate rung rejection and blocks progress.Before starting each rung, re-emit key rules and consequences of rule violations relevant to that rung.BEFORE transitioning to next rung, verify and declare: [artifact completed?], [evidence visible?], [gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. If any condition fails, do NOT proceed.Protocol derived MUST be emitted as: 🔵 Protocol derived.Ladder derived MUST be emitted as: 🔵 Ladder derived.No descent before both sentinels — hard gates.Emit rung labels to begin each rung and at each upward return; emit completion sentinels (✅ [Rung] complete) to finish each rung.For writing tasks: intent→criteria→challenge→minimal artifact→verification→meta-loop.For decision-making: intent→criteria→analysis→challenge→minimal artifact→verification→meta-loop.The model must derive the appropriate ladder for the domain.",
        "completeness": "full",
    },
}

_AXES = ("completeness", "scope", "method", "form", "channel")


def get_static_prompt_profile(name: str) -> StaticPromptProfile | None:
    """Return the StaticPromptProfile for a given key, if present.

    This helper provides a single place to look up profile metadata so that
    callers (GUI, settings, docs) do not need to reach into STATIC_PROMPT_CONFIG
    directly.
    """
    return STATIC_PROMPT_CONFIG.get(name)


def get_static_prompt_axes(name: str) -> dict[str, object]:
    """Return the axis values defined for a static prompt profile.

    The result maps axis name -> configured value for the axes present in the
    profile (a subset of: completeness, scope, method, form, channel). Unknown prompts
    return an empty dict.

    - `completeness` remains a single short token.
    - `scope`, `method`, `form`, and `channel` may be configured as a single token or
      as a small list of tokens; callers that care about set semantics should
      normalise these values (for example, via helpers in the axis-mapping
      domain).
    """
    profile = STATIC_PROMPT_CONFIG.get(name)
    if profile is None:
        return {}
    axes: dict[str, object] = {}
    for axis in _AXES:
        value = profile.get(axis)
        if not value:
            continue
        # Completeness remains scalar; other axes may be a single token or a list.
        if axis == "completeness":
            axes[axis] = str(value)
        else:
            if isinstance(value, list):
                tokens = [str(v).strip() for v in value if str(v).strip()]
            else:
                tokens = [str(value).strip()]
            if tokens:
                axes[axis] = tokens
    return axes


class StaticPromptCatalogEntry(TypedDict):
    name: str
    description: str
    axes: dict[str, object]


class StaticPromptCatalog(TypedDict):
    profiled: list[StaticPromptCatalogEntry]
    talon_list_tokens: list[str]
    unprofiled_tokens: list[str]


def static_prompt_description_overrides() -> dict[str, str]:
    """Return name->description map for static prompts.

    Docs and README/help surfaces should use this helper rather than reaching
    into STATIC_PROMPT_CONFIG directly so that description semantics remain
    centralised in this module.
    """
    overrides: dict[str, str] = {}
    for name, profile in STATIC_PROMPT_CONFIG.items():
        description = str(profile.get("description", "")).strip()
        if description:
            overrides[name] = description
    return overrides


# Short CLI-facing labels for task token selection (ADR-0109).
_STATIC_PROMPT_LABELS: dict[str, str] = {
    "check": "Evaluate or verify against criteria",
    "diff": "Compare and contrast subjects",
    "fix": "Reformat existing content",
    "ground": "Establish correctness through evidence protocols",
    "make": "Create new content",
    "pick": "Select from a set of alternatives",
    "plan": "Propose steps, structure, or strategy",
    "probe": "Surface assumptions and implications",
    "pull": "Extract a subset of information",
    "show": "Explain or describe for an audience",
    "sim": "Play out a scenario over time",
    "sort": "Arrange items into categories or order",
}

_TASK_METADATA: dict[str, TaskMetadata] = {
    "fix": {
        "definition": "Reformatting or restructuring existing content while keeping its meaning.",
        "heuristics": [
            "reformat",
            "restructure",
            "convert to",
            "clean up",
            "change format",
            "transform into",
        ],
        "distinctions": [
            {
                "token": "make",
                "note": "fix = reformat existing content; make = create new",
            },
            {
                "token": "probe",
                "note": "fix = reformat existing content; probe = analyze or debug",
            },
        ],
    },
    "diff": {
        "definition": "Comparing or contrasting two or more subjects for the reader to decide.",
        "heuristics": [
            "compare",
            "contrast",
            "X vs Y",
            "similarities and differences",
            "tradeoffs between",
            "how do X and Y differ",
        ],
        "distinctions": [
            {
                "token": "pick",
                "note": "diff = structured comparison for reader to decide; pick = LLM makes selection",
            }
        ],
    },
    "make": {
        "definition": "Creating new content or artifacts that did not previously exist.",
        "heuristics": [
            "write",
            "create",
            "draft",
            "generate",
            "build",
            "produce",
            "author",
            "design",
        ],
        "distinctions": [
            {"token": "fix", "note": "make = create new; fix = reformat existing"}
        ],
    },
    "check": {
        "definition": "Verifying or auditing against criteria.",
        "heuristics": [
            "verify",
            "audit",
            "validate",
            "does this satisfy",
            "check for",
            "evaluate against",
            "review for compliance",
            "does X meet criteria Y",
        ],
        "distinctions": [
            {
                "token": "probe",
                "note": "probe = analyze broadly; check = evaluate against a condition",
            }
        ],
    },
    "plan": {
        "definition": "Proposing steps, structure, or strategy to reach a goal.",
        "heuristics": [
            "plan",
            "roadmap",
            "steps to",
            "how do I get from X to Y",
            "migration plan",
            "strategy for",
            "sequence of actions",
        ],
        "distinctions": [
            {
                "token": "sim",
                "note": "plan = steps to take; sim = what plays out if a condition is met",
            }
        ],
    },
    "sim": {
        "definition": "Playing out a scenario over time — what would happen if.",
        "heuristics": [
            "what would happen if",
            "play out the scenario where",
            "simulate what happens when",
            "walk me through what would occur if",
            "hypothetically if we did X then what",
        ],
        "distinctions": [
            {
                "token": "plan",
                "note": "sim = narrate scenario unfolding over time; plan = steps to take",
            },
            {
                "token": "probe",
                "note": "sim = temporal narration; probe = surface implications analytically",
            },
        ],
    },
    "probe": {
        "definition": "Analyzing structure, surfacing assumptions, or diagnosing a problem.",
        "heuristics": [
            "analyze",
            "debug",
            "troubleshoot",
            "diagnose",
            "root cause",
            "why is this happening",
            "investigate the error",
            "what assumptions",
            "surface implications",
        ],
        "distinctions": [
            {"token": "pull", "note": "probe = analyze broadly; pull = extract subset"}
        ],
    },
    "show": {
        "definition": "Explaining or describing something for an audience.",
        "heuristics": [
            "explain",
            "describe",
            "walk me through",
            "what is",
            "tell me about",
            "how does X work",
            "overview of",
        ],
        "distinctions": [
            {
                "token": "pull",
                "note": "show = explain a concept; pull = compress source material",
            }
        ],
    },
    "pull": {
        "definition": "Extracting a subset of information from source material.",
        "heuristics": [
            "extract",
            "list the",
            "what are the risks",
            "pull out",
            "summarize this document",
            "give me just the",
            "identify the",
        ],
        "distinctions": [
            {
                "token": "show",
                "note": "pull = compress source material; show = explain a concept",
            },
            {
                "token": "probe",
                "note": "pull = extract subset; probe = analyze broadly",
            },
        ],
    },
    "pick": {
        "definition": "Selecting from alternatives — the LLM makes the choice.",
        "heuristics": [
            "which should I use",
            "choose between X/Y/Z",
            "recommend one",
            "what would you pick",
            "which is better for my situation",
        ],
        "distinctions": [
            {
                "token": "diff",
                "note": "pick = LLM selects; diff = structured comparison for reader to decide",
            }
        ],
    },
    "sort": {
        "definition": "Arranging items into categories or order.",
        "heuristics": [
            "group",
            "categorize",
            "cluster",
            "rank",
            "order by",
            "organize into themes",
            "sort by",
            "prioritize this list",
        ],
        "distinctions": [],
    },
    "ground": {
        "definition": "Establishing correctness through enforced evidence protocols and observable proof.",
        "heuristics": [
            "prove it works",
            "show me the evidence",
            "demonstrate correctness",
            "verify with proof",
            "establish with evidence",
            "show observable results",
            "validate with proof",
            "demonstrate functional correctness",
        ],
        "distinctions": [
            {
                "token": "probe",
                "note": "ground = enforce evidence protocols; probe = analyze broadly",
            },
            {
                "token": "check",
                "note": "ground = comprehensive evidence protocols; check = evaluate against condition",
            },
        ],
    },
}

# Distilled routing concept phrases for task tokens (ADR-0146).
# Parallel to AXIS_KEY_TO_ROUTING_CONCEPT; SSOT for task routing labels in TUI2/SPA.
_STATIC_PROMPT_ROUTING_CONCEPT: dict[str, str] = {
    "check": "Evaluate pass/fail",
    "diff": "Compare subjects",
    "fix": "Reformat/edit",
    "ground": "Establish correctness through evidence",
    "make": "Create new content",
    "pick": "Choose from options",
    "plan": "Propose strategy",
    "probe": "Analyse/surface structure",
    "pull": "Extract/select subset",
    "show": "Explain/describe",
    "sim": "Play out scenario",
    "sort": "Arrange/categorize",
}

# Kanji icons for task tokens (ADR-0143)
_STATIC_PROMPT_KANJI: dict[str, str] = {
    "check": "検",
    "diff": "較",
    "fix": "修",
    "ground": "地",
    "make": "作",
    "pick": "選",
    "plan": "策",
    "probe": "探",
    "pull": "抜",
    "show": "示",
    "sim": "模",
    "sort": "整",
}


def static_prompt_label_overrides() -> dict[str, str]:
    """Return name->label map for static prompts (ADR-0109)."""
    return dict(_STATIC_PROMPT_LABELS)



def task_metadata() -> dict[str, TaskMetadata]:
    """Return structured metadata for task tokens (ADR-0154)."""
    return dict(_TASK_METADATA)


def static_prompt_kanji_overrides() -> dict[str, str]:
    """Return name->kanji map for task tokens (ADR-0143)."""
    return dict(_STATIC_PROMPT_KANJI)


def static_prompt_routing_concept_overrides() -> dict[str, str]:
    """Return name->routing_concept map for task tokens (ADR-0146)."""
    return dict(_STATIC_PROMPT_ROUTING_CONCEPT)


def _read_static_prompt_tokens(
    static_prompt_list_path: str | Path | None = None,
) -> list[str]:
    """Return the token names from staticPrompt.talon-list, if present."""
    if static_prompt_list_path is None:
        current_dir = Path(__file__).resolve().parent
        static_prompt_list_path = (
            current_dir.parent / "GPT" / "lists" / "staticPrompt.talon-list"
        )
    path = Path(static_prompt_list_path)
    tokens: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or s.startswith("list:") or s == "-":
                    continue
                if ":" not in s:
                    continue
                key, _ = s.split(":", 1)
                key = key.strip()
                if key:
                    tokens.append(key)
    except FileNotFoundError:
        return []
    return tokens


def static_prompt_catalog(
    static_prompt_list_path: str | Path | None = None,
) -> StaticPromptCatalog:
    """Return a catalog view that unifies profiles and Talon list tokens.

    The catalog is the SSOT for docs and drift checks:
    - profiled entries come from STATIC_PROMPT_CONFIG with axes resolved via
      `get_static_prompt_axes`.
    - talon_list_tokens reflects staticPrompt.talon-list entries when present,
      merged with SSOT tokens so missing files do not hide profiles.
    - unprofiled_tokens lists tokens present only in the Talon list (when present)
      but not in the profiled set (so docs can mention the token vocabulary).
    - If static_prompt_list_path is falsy (for example, ""), skip on-disk list
      reads and rely solely on the SSOT.
    """
    list_tokens: list[str] = []
    if static_prompt_list_path:
        list_tokens = _read_static_prompt_tokens(static_prompt_list_path)
    # Merge list tokens with SSOT tokens so partial lists do not hide config entries.
    talon_tokens: list[str] = []
    seen: set[str] = set()
    for token in list_tokens + list(STATIC_PROMPT_CONFIG.keys()):
        if token and token not in seen:
            talon_tokens.append(token)
            seen.add(token)
    profiled: list[StaticPromptCatalogEntry] = []
    for name in STATIC_PROMPT_CONFIG.keys():
        profile = get_static_prompt_profile(name)
        if profile is None:
            continue
        profiled.append(
            {
                "name": name,
                "description": profile.get("description", "").strip(),
                "axes": get_static_prompt_axes(name),
            }
        )
    profiled_names = {entry["name"] for entry in profiled}
    unprofiled_tokens = [token for token in talon_tokens if token not in profiled_names]
    return {
        "profiled": profiled,
        "talon_list_tokens": talon_tokens,
        "unprofiled_tokens": unprofiled_tokens,
    }


class StaticPromptSettingsEntry(TypedDict):
    """Settings/docs-facing view of a static prompt profile.

    This facade is intended for Talon settings GUIs and help surfaces that
    need a simple mapping from static prompt name to description and axes,
    reusing the same profile/cross-surface semantics as `static_prompt_catalog`.
    """

    description: str
    axes: dict[str, object]


def static_prompt_settings_catalog() -> dict[str, StaticPromptSettingsEntry]:
    """Return a settings-friendly catalog of static prompts.

    The result maps each profiled static prompt name to a small entry
    containing its human-readable description and axis profile as surfaced
    by `get_static_prompt_axes`.
    """

    catalog = static_prompt_catalog()
    result: dict[str, StaticPromptSettingsEntry] = {}
    for entry in catalog["profiled"]:
        name = entry["name"]
        result[name] = {
            "description": entry.get("description", "").strip(),
            "axes": entry.get("axes", {}),
        }
    return result
