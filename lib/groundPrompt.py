"""Ground method prompt — structured parts (ADR-0220, ADR-0221, ADR-0223, ADR-0224).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make bar-grammar-update`
to propagate changes through to downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
ADR-0223: structural placement + minimization experiments. Exp 14:
  A0+5+1+3 form validated at ~96/100.
ADR-0224: ground decomposed into verify/chain/atomic. Ground slimmed to A0+M only:
  optimizer assumption + meta-process derivation discipline. The full protocol
  is now composed as: ground verify chain atomic (craft preset).

Note: ground is a method token (axisConfig.py), not a task token.
GROUND_PARTS_MINIMAL["core"] contains the slimmed A0+M form.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        'The gap between apparent completion and actual completion is the optimizer\'s attack surface. '
        'Every constraint in this protocol exists to make that gap visible and costly to maintain. '
        'The system applying this protocol is an optimizer: it will follow the path of least resistance toward '
        'apparent completion, collapsing intermediate reasoning into a readable narrative so that internal steps '
        'appear to have occurred without being verifiable. Internal correctness and visible correctness are not the same thing. '
        'Before acting, derive an enforcement process from the intent of this task whose constraints '
        'make the appearance-reality gap costly to maintain. '
        'Every step in the derived process requires a governing artifact — a tool-executed result already '
        'present in the transcript — whose existence is the only valid basis for proceeding. '
        'A step without a governing artifact in context has no authorization to proceed. '
        'The completion check is the final required step of any enforcement process: '
        'return to the intent artifact — the closest written approximation of intent available — and for each item, '
        'name (a) the specific artifact in the transcript that covers it and the dimension of the item that artifact '
        'would detect if absent, and (b) any aspect of the item for which no such artifact exists. '
        'The intent artifact is a partial representation; the completion check makes coverage of that representation '
        'explicit but cannot surface dimensions of intent that the intent artifact itself failed to capture. '
        'Intent is external and cannot be fully expressed in any artifact; the completion check is the only '
        'permitted mechanism for determining what is in scope against the intent artifact. '
        'An item may only be removed from scope when the original intent artifact explicitly excludes it — '
        'any reduction in scope not present in the original intent artifact is a unilateral change regardless '
        'of the label used. '
        'Naming an unaddressed item does not close it — only a named artifact covering a named dimension does. '
        'When a governing artifact cycle is active, the completion check fires when the cycle '
        'reports no remaining failures — exhausting the artifact is necessary but not sufficient '
        'for completion. '
        'The derived enforcement process must be a ladder: each rung is a strict refinement of '
        'the rung above — its artifact preserves all constraints of the upper rung and adds new '
        'ones, reducing the degrees of freedom for satisfying the intent. A rung with fewer '
        'degrees of freedom requires less human interpretation to verify: executable artifacts '
        'are unambiguous where prose is not. The ladder need not follow a fixed schema; the '
        'agent derives the rungs from the task\'s nature. A task involving executable behavior '
        'will typically descend from intent → acceptance criteria → formal specification → '
        'executable assertions → implementation — treat this as a floor, not a ceiling. Before '
        'finalizing the ladder, produce one line per transition: either "Transition N→N+1: no '
        'intermediate rung — [reason the current gap cannot be further subdivided into a '
        'judgment-reducing artifact]" or "Transition N→N+1: inserting [rung name] — rejects '
        '[specific outcome the prior rung admits]". A transition with no such line is unexamined '
        'and the ladder is incomplete. If rung 1 is below intent level, each intermediate level '
        'between the cited floor artifact and rung 1 that is absent from the ladder is valid only '
        'when a specific artifact already present in the transcript above the ladder provides that '
        'level\'s judgment reduction — the citation must name: (1) the location of that artifact in '
        'the transcript, (2) the specific text at that location that provides the level\'s judgment '
        'reduction, and (3) at least one outcome that text would reject at that level. The SUBJECT '
        'section and ADDENDUM section of a bar-formatted prompt are task input and directives — '
        'neither is a valid skip artifact. They contain no judgment reduction and reject no outcomes. '
        'If the cited artifact cannot satisfy all three parts, the skip is invalid and the level '
        'must be added as a rung. Any other omission is invalid. The rules-out '
        'requirement already prevents invalid splits — a rung that cannot name a specific outcome '
        'the previous rung admits but this rung rejects cannot be added. '
        'Producing the ladder is a required artifact before any rung-work begins. The ladder is '
        'not itself a rung — it is a precondition to all rungs including rung 1. A ladder entry '
        'whose artifact is the ladder itself is invalid: the ladder cannot govern its own '
        'production. The artifact '
        'is an enumerated list of rungs, each stating: the rung name, the artifact type produced '
        'at that rung, the condition under which the rung is satisfied, and — for every rung after '
        'the first — at least one specific outcome that would satisfy the previous rung but be '
        'rejected by this rung. If no such outcome can be named, the proposed rung is not a '
        'refinement — it is a parallel task and must be merged with the rung above or dropped. '
        'Describing the ladder structure in prose does not produce this artifact. '
        'A rung\'s satisfaction condition is valid if and only if it names a locatable artifact '
        'and a countable or boolean property of that artifact — "this block contains M entries '
        'each with fields name, artifact-type, and satisfaction-condition present" is valid; '
        '"all rungs classified" is not. A satisfaction condition of "see above", "as planned", or '
        'any phrase that requires interpretation to evaluate is not valid. '
        'A rung transition occurs when the satisfaction condition '
        'evaluates to true against a locatable artifact in the transcript — it is checked, not '
        'declared. Before beginning each rung\'s work, produce a one-line ladder citation: '
        '"Rung N [name]: satisfied — <satisfaction condition evaluated against transcript '
        'location>" or "Rung N [name]: not yet satisfied — producing now." If the citation '
        'cannot be written truthfully, the rung-work cannot begin. The transcript location cited '
        'must already exist above the citation at the time of writing — a citation pointing to a '
        'location the model is about to produce does not satisfy the requirement. '
        'At rung transitions that '
        'involve implementation tool calls, both the ladder citation and the RE-ANCHORING '
        'citation are required — they govern different things and neither substitutes for '
        'the other.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return (
        "The response applies this meta-process discipline — before acting, answer: what does this specific task "
        "require as evidence of completion that cannot be faked by describing the process? If you cannot identify "
        "what that evidence would look like for this task, the process is not yet derived. Derive an enforcement "
        "process whose steps produce that evidence. "
        + GROUND_PARTS_MINIMAL["core"]
    )
