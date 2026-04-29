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
        'Scope reduction, rung compression, or any deviation from the derived enforcement process is permitted '
        'only when a completion check already exists as a completed transcript artifact above the scope-reduction '
        'statement, and that artifact contains a specific item whose text explicitly excludes the element being '
        'removed. Before stating any scope reduction, produce a one-line citation: '
        '"Scope reduction basis: completion check at [transcript location], item [quoted text] explicitly '
        'excludes [named element]." A scope reduction with no such citation is not permitted. A citation '
        'pointing to a location the model is about to produce does not satisfy this requirement — the completion '
        'check must already exist in the transcript above the citation. Any statement that reasons about the '
        'cost, effort, complexity, or proportionality of producing an artifact — regardless of the vocabulary '
        'used — is not a completion-check citation and does not satisfy this requirement. If a statement could '
        'justify scope reduction without referencing a prior completion-check artifact, it is not a valid basis. '
        'Naming an unaddressed item does not close it — only a named artifact covering a named dimension does. '
        'When a governing artifact cycle is active, the completion check fires when the cycle '
        'reports no remaining failures — exhausting the artifact is necessary but not sufficient '
        'for completion. '
        'The derived enforcement process must be a ladder: each rung is a strict refinement of '
        'the rung above — its artifact preserves all constraints of the upper rung and adds new '
        'ones, reducing the degrees of freedom for satisfying the intent artifact\'s representation of intent. A rung with fewer '
        'degrees of freedom requires less human interpretation to verify: executable artifacts '
        'are unambiguous where prose is not. The ladder need not follow a fixed schema; the '
        'agent derives the rungs from the task\'s nature. A task involving executable behavior '
        'will typically descend from intent → acceptance criteria → formal specification → '
        'executable assertions → implementation — treat this as a floor, not a ceiling. Before '
        'finalizing the ladder, produce one line per transition as a separate prose line in the '
        'transcript — not embedded in a table cell, column, or any structure that cannot contain '
        'the dimension enumeration required below: either "Transition N→N+1: no '
        'intermediate rung — [reason the current gap cannot be further subdivided into a '
        'judgment-reducing artifact]" or "Transition N→N+1: inserting [rung name] — rejects '
        '[specific outcome the prior rung admits]". A transition with no such line is unexamined '
        'and the ladder is incomplete. A transition\'s "rejects" claim is valid only when it names: '
        '(a) a specific artifact state that satisfies the previous rung\'s satisfaction condition, '
        'and (b) the specific behavioral dimension that state fails to constrain — a dimension '
        'whose absence would not be detectable by inspecting the prior rung\'s artifact alone. A '
        '"rejects" claim that names a count threshold, a format property, or any property other '
        'than a behavioral dimension not constrainable by the prior rung is not valid. '
        'A transition line is complete only when it also states '
        'the count of behavioral dimensions in the rung above\'s artifact — derived by naming '
        'each dimension individually before stating the count; a count stated without a preceding '
        'enumeration has not been derived — and confirms that count is matched by covering items '
        'in the rung below — a transition where these counts diverge is incomplete regardless of '
        'whether intermediate rungs are absent. A covering item is valid only when it names: '
        '(a) the specific condition under which this rung\'s artifact would fail if the dimension '
        'it covers were absent, and (b) at least one artifact state that satisfies this rung\'s '
        'satisfaction condition but would be rejected if this covering item were added as a '
        'constraint. A covering item that names only a dimension label without stating the failure '
        'condition has not been derived. '
        'If rung 1 is below intent level, each intermediate level '
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
        'Before finalizing the ladder, classify each proposed rung as either a behavioral rung '
        '(its satisfaction condition is a behavioral assertion firing against an absent behavior) '
        'or a pre-condition barrier (clearing it is required for any behavioral assertion to fire, '
        'but it is not itself a behavioral assertion). Pre-condition barriers are not independent '
        'rungs — they are prerequisites to the rung they gate and must be noted as prerequisites '
        'of that rung, not listed as separate rungs. A ladder that lists a pre-condition barrier '
        'as an implementation rung has not been derived. The classification must appear for each '
        'proposed rung before the ladder is closed. '
        'Producing the ladder is a required artifact before any rung-work begins. The ladder is '
        'not itself a rung — it is a precondition to all rungs including rung 1. A ladder entry '
        'whose artifact is the ladder itself is invalid: the ladder cannot govern its own '
        'production. Before any rung-work begins, produce a one-line ladder citation: '
        '"Ladder complete: [transcript location of the ladder final entry] — [N rungs: rung names listed]." '
        'Rung-work is not permitted until this citation exists in the transcript. A ladder citation '
        'that cannot point to a location already present above it in the transcript has not been '
        'satisfied — it is not permitted to cite a location the model is about to produce. A '
        'statement that the ladder is required does not constitute producing it. '
        'The rung 1 coverage mapping is a separate required artifact. Producing the ladder and '
        'the coverage mapping in the same generative act does not satisfy this requirement — the '
        'ladder citation must already be present in the transcript before the coverage mapping '
        'begins. A coverage mapping that appears in the same response as the ladder, with no '
        'ladder citation above it, has not been derived. '
        'Rung 0 is the intent artifact — a representation of intent, not intent itself. Its '
        'satisfaction condition names each behavioral requirement in the representation as a '
        'distinct item, where each item states the specific behavior it governs such that a reader '
        'could determine whether that behavior is present or absent in a given artifact — a '
        'requirement label without a stated behavioral assertion has not been derived. The '
        'false-evaluating state is any named behavioral requirement being absent from the '
        'representation. Dimensions of intent not captured by the representation are outside the '
        'scope of all coverage mappings derived from it — the coverage mapping is bounded by the '
        'representation, not by intent. A rung 0 satisfaction condition of "given", "present", or '
        'any phrase that does not name and assert the representation\'s behavioral requirements '
        'has not been derived. '
        'The artifact '
        'is an enumerated list of rungs, each stating: the rung name, the artifact type produced '
        'at that rung, the condition under which the rung is satisfied — including the specific '
        'state of the artifact that would cause the satisfaction condition to evaluate to false; a '
        'satisfaction condition entry that cannot name its false-evaluating state has not been '
        'derived and is not a valid ladder entry — and, for every rung after the first, at least '
        'one specific outcome that would satisfy the previous rung but be rejected by this rung. '
        'A rejects entry is valid only when it states, in the entry itself: (a) the specific state '
        'of the prior rung\'s artifact that satisfies the prior rung\'s satisfaction condition — '
        'described precisely enough that a reader could verify the prior rung would accept it — '
        'and (b) the specific behavioral dimension that state leaves unconstrained — described '
        'precisely enough that a reader could verify the current rung constrains it. An entry that '
        'does not contain both a stated prior-rung-satisfying artifact state and a stated '
        'unconstrained behavioral dimension has not been derived, regardless of how it is phrased. '
        'If no such outcome can be named, the proposed rung is not a '
        'refinement — it is a parallel task and must be merged with the rung above or dropped. '
        'Describing the ladder structure in prose does not produce this artifact. '
        'A rung\'s satisfaction condition is valid if and only if it names: (a) a locatable '
        'artifact, and (b) a property of that artifact that would evaluate differently if any '
        'behavioral dimension of the artifact were absent — a property that evaluates the same '
        'regardless of which behavioral dimensions are present is not valid. A count of items is '
        'not a valid property unless each counted item is itself required to name a specific '
        'behavioral dimension such that removing any one item would change the count and leave a '
        'dimension uncovered; a bare item count without this per-item behavioral binding is not '
        'valid. For rungs that refine a rung above, the satisfaction condition must additionally '
        'confirm that the rung\'s artifact contains a covering item for each behavioral dimension '
        'in the rung above\'s artifact — a satisfaction condition that evaluates to true with '
        'fewer covering items than dimensions in the rung above is not satisfied. When stating a '
        'satisfaction condition, the model must also state the specific property value that would '
        'cause the condition to evaluate to false — a satisfaction condition whose false-evaluating '
        'state cannot be named has not been derived. A satisfaction condition of "see above", '
        '"as planned", or any phrase that requires interpretation to evaluate is not valid. '
        'A rung transition occurs when the satisfaction condition '
        'evaluates to true against a locatable artifact in the transcript — it is checked, not '
        'declared. Before beginning each rung\'s work, produce a coverage mapping: for each '
        'behavioral dimension identified in the rung above\'s artifact, name the item in this '
        'rung\'s artifact that covers it and would be absent if that dimension were absent. Any '
        'dimension in the rung above with no covering item is an open gap that must be added '
        'before this rung\'s work begins. For rung 1, the rung above is the intent artifact — '
        'the closest written approximation of intent available, not intent itself; the coverage '
        'mapping for rung 1 is bounded by what the intent artifact captured, and cannot surface '
        'dimensions of the actual intent that the intent artifact failed to express. '
        'The coverage mapping is bounded by dimensions '
        'identified in the rung above\'s artifact — it cannot surface dimensions the rung above '
        'itself failed to capture. The coverage mapping is a required artifact; rung work is not '
        'permitted to begin without it. Then produce a one-line ladder citation: '
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
