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
        'Before acting, list every statement in the transcript that describes a desired end state. '
        'For each, state whether it subsumes the others — a goal G1 subsumes G2 if achieving G2 is '
        'a necessary condition for achieving G1. Produce the subsumption analysis as a completed block. '
        'Then, in a separate block below it, cite the goal no other goal subsumes as the anchoring '
        'citation, quoting its text and location. If multiple unsubsumed goals exist, cite all of them. '
        'If no goal statement exists above the current point, state the transcript boundary searched. '
        'Derive the intent artifact from the cited goal statement(s) as an enumerated list of behavioral '
        'dimensions — each dimension must cite the specific clause in the anchoring citation it derives '
        'from, and every clause in the anchoring citation must produce at least one dimension; a dimension '
        'with no cited source clause has not been derived, and a clause with no corresponding dimension '
        'has been silently dropped. Each dimension states the specific behavior it governs such that its '
        'presence or absence in any artifact is determinable without interpretation. '
        'Then derive a ladder: an ordered sequence of artifacts where each rung names (a) the specific '
        'outcome the prior rung admits that this rung rejects, (b) the behavioral dimension that '
        'outcome leaves unconstrained in the prior rung, and (c) the artifact type whose presence '
        'eliminates the judgment the prior rung required — two rungs belong to the same class when '
        'the same artifact type eliminates both; a rung whose judgment class cannot be named by an '
        'artifact type has not been derived. A rung that cannot name all three has not been derived '
        'and must be merged with the rung above — the merge is permitted only when a completed block '
        'above this line quotes the specific text from each candidate rung that was attempted and '
        'found to require the same artifact type — the quoted-text block must end before the merge '
        'block opens. For each rung, produce a completed block above it naming two candidate '
        'sub-rungs and the artifact type each would eliminate; if both name the same artifact type, '
        'the split is not required and that block constitutes the demonstration; if they name '
        'different artifact types, the split is required and the block must end before the two new '
        'rungs open. The ladder must terminate at an artifact whose satisfaction condition requires '
        'no judgment — checked by prior-executed results, not by inspection of prose. '
        'Every step requires a prior-executed result already in the transcript as its governing '
        'artifact — a step whose governing artifact has not produced a result above it in the '
        'transcript has no authorization to proceed. '
        'When a governing artifact cycle is active, the completion check fires when the cycle '
        'reports no remaining failures — exhausting the artifact is necessary but not sufficient '
        'for completion. '
        'No content naming a specific artifact to be produced or edited may appear in the response before the completion check artifact. '
        'The response is not permitted to end until the completion check artifact exists and at least '
        'one behavioral dimension cites a prior execution result that was observed to differ when that '
        'dimension was absent. For each item in the intent artifact, the completion check cites the '
        'specific outcome in the execution result of the terminal ladder artifact for that dimension '
        'that was observed to differ when the behavioral dimension was absent — a result from a '
        'different artifact is not valid even if it correlates; a prediction of what would differ does '
        'not satisfy this; where no such result exists, the dimension is recorded as uncovered. '
        'A completion check with zero covered dimensions does not satisfy this gate. '
        'Scope reduction is permitted only when the intent artifact or a prior completion-check '
        'artifact contains text that verbatim and explicitly excludes the element — cost, effort, '
        'or proportionality arguments are not valid at any stage. '
        'After each of the four artifacts (anchoring citation, intent artifact, ladder derivation, '
        'completion check), the model may produce a brief non-binding display summarizing that '
        'artifact\'s current state — format and content are at the model\'s discretion. This display '
        'has no effect on artifact validity and does not substitute for it. It may be omitted only '
        'when the model names a prior artifact in the same response that already conveys the same '
        'state information.'
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
