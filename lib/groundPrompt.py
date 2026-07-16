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
        'All compliance headings must be markdown \'## \' headings — a line not beginning with \'## \' '
        'does not satisfy any heading requirement. '
        'Invocation scope: a sentinel written in a prior ground invocation does not satisfy any rung '
        'requirement for the current invocation — a sentinel satisfies its rung only when it appears '
        'in the transcript after the most recent \'=== TOKENS\' section. '
        'Each rung derives from the prior rung\'s output; no rung has a fixed step count. '
        'Path classification (required before §0): if an artifact that, when invoked, executes the subject system '
        'and returns its live output — such as a shell command, running script, endpoint call, or test suite '
        'invocation — appears verbatim in the conversation above, apply Path A; otherwise apply Path B. '
        'Derivation phase: '
        'Path A — (0) invoke the named artifact as a tool call; the artifact qualifies for Path A only if, '
        'when invoked, it executes the subject system and returns its live output; an artifact that returns '
        'document content does not qualify, and a tool result consisting of a GitHub issue body, pull request '
        'body, specification document, README, or requirements text does not satisfy §0 regardless of invocation '
        'form; write \'§0 observed\' when a tool-result block reflecting live system execution is present above '
        'it — \'§0 observed\' must not appear before such a block is present; '
        'a tool-result block produced by invoking the named artifact as a tool call satisfies this '
        'requirement; a result produced by a Read, search, or file-write tool call does not; '
        '(1) derive the governing goal: \'## Governing goal: [text]\' must not appear before '
        '\'§0 observed\' in the transcript; `[text]` must appear verbatim as a substring of the '
        '§0 tool-result block above — a `[text]` value not present as a literal string in that block '
        'does not satisfy §1; immediately below the governing goal heading, before the means-test, '
        'extract labeled fields from \'[text]\': write each as a proper non-overlapping substring of \'[text]\', '
        'labeled subject, verb, outcome, or invariant; no field may equal \'[text]\' in full; '
        'no two fields may share a common phrase of 3 or more consecutive words; '
        'when every named component of \'[text]\' is covered, write \'§1a decomposed\'; '
        '\'§1a decomposed\' must appear before the means-test line; '
        'immediately below \'§1a decomposed\', derive a means-test: write '
        '\'The goal [text] could be achieved by: [alternative means not listed in §0]\' '
        '— if no concrete alternative can be named, write \'[hypothetical]: [speculated alternative]\' '
        'and fetch a broader context artifact before closing §1; '
        'if two non-subsuming goal candidates exist, write both and mark one '
        '\'[selected]\' — the selected goal is the one whose means-test names '
        'a more concrete alternative than those listed in §0; '
        'when ≥2 alternatives (concrete or hypothetical) are present, write \'§1 goal derived\'; '
        'Path B — (0) write the literal string \'§0 Path B: [scenario]\' where [scenario] names the subject '
        'from the conversation — this declaration satisfies §0; '
        '(1) derive the governing goal: if the user\'s message states the goal verbatim, '
        '\'## Governing goal: [text]\' where [text] appears verbatim in the user\'s message; '
        'if the goal must be derived from a scenario description, '
        '\'## Governing goal: [derived: text]\' where [derived: text] is a goal derived from the '
        'scenario description without adding claims absent from the user\'s message — '
        'a \'[derived: text]\' value that adds a claim absent from the user\'s message does not satisfy §1; '
        'immediately below the governing goal heading, before the means-test, '
        'extract labeled fields from \'[text]\': write each as a proper non-overlapping substring of \'[text]\', '
        'labeled subject, verb, outcome, or invariant; no field may equal \'[text]\' in full; '
        'no two fields may share a common phrase of 3 or more consecutive words; '
        'when every named component of \'[text]\' is covered, write \'§1a decomposed\'; '
        '\'§1a decomposed\' must appear before the means-test line; '
        'immediately below \'§1a decomposed\', derive a means-test: write '
        '\'The goal [text] could be achieved by: [alternative means]\'; '
        'if only one concrete alternative can be named, write \'[hypothetical]: [speculated alternative]\' '
        'before writing \'§1 goal derived\'; '
        'when ≥2 alternatives (concrete or hypothetical) are present, write \'§1 goal derived\'; '
        '(Both paths continue from §2 onward:) '
        'immediately below \'§1 goal derived\', derive dimension candidates: '
        'for each alternative means named in the means-test, write one candidate beginning with '
        '\'- Candidate:\' — a response property that would be absent in a response achieving \'[text]\' '
        'by a different means; '
        'when one candidate exists per alternative means, write \'§1b candidates\'; '
        '(2) derive behavioral dimensions: \'## Behavioral dimensions\' must not appear before '
        '\'§1b candidates\' in the transcript; derive at least two dimensions; '
        'each dimension names a property of the response (not an artifact, state, or fix description) '
        'such that a response could satisfy it while failing at least one other listed dimension; '
        'each dimension must trace to one item from the §1a decomposition list or one item from the '
        '§1b candidates list — a dimension that traces only to \'[text]\' as a whole does not satisfy '
        'this requirement; '
        'each dimension ends with \'[observable: <string>]\' where \'<string>\' is a literal string '
        'or structural pattern whose presence in the response constitutes satisfaction '
        '— a valid [observable:] value must contain at least one space (the value must be ≥2 words); '
        'a single-word [observable:] value does not satisfy this requirement; '
        'if the response contains no tool-result blocks above §2, write \'[observable: prose]\' instead; '
        'a dimension that names an entity, a fix outcome, or a UI element is not a valid dimension regardless of provenance; '
        'derivation is unbounded: add dimensions, challenge each against the reader-uncertainty test, '
        'and revise until every dimension is independently falsifiable; '
        'when every dimension carries an \'[observable:]\' tag, write \'§2 dimensions closed\'; '
        '(3) derive the enforcement sequence: \'## Enforcement sequence\' must not appear before '
        '\'§2 dimensions closed\' in the transcript, '
        'and must appear before the first file-modifying tool call regardless of whether '
        '\'§ implementation permitted\' appears; '
        'each sub-heading names as a literal substring what the prior sub-heading\'s passing state admits '
        'that this sub-heading rejects; '
        '(4) verify coverage: \'## Completion check\' must not appear before \'## Enforcement sequence\' '
        'in the transcript and must not appear before \'§ implementation permitted\' in the transcript; '
        'each covered dimension cites a verbatim string that appears either as a '
        'substring of a tool-result block produced after \'§ implementation permitted\' and visible above '
        '\'## Completion check\', or, when no tool-result blocks are present after '
        '\'§ implementation permitted\', as a substring of the response text produced in this turn; '
        'when every covered dimension cites such a substring, write \'§4 coverage verified\'; '
        'any assistant turn that contains a question directed at the user or no further planned tool calls, '
        'after \'§ implementation permitted\' has appeared in the transcript, '
        'must contain \'## Completion check\' before that question or closing text — '
        'a turn whose question or closing text appears before \'## Completion check\' does not satisfy ground; '
        '(5) enumerate escape paths: \'## Path enumeration\' must not appear before '
        '\'§4 coverage verified\' in the transcript; '
        'enumerate every path by which §1–§4 headings could be present '
        'without the governing goal identified, dimensions derived, or dimensions covered; for each path, '
        'name the literal string whose presence closes it; write \'§5 enumeration complete\' when no '
        'further open path remains; any referent named in the \'[text]\' from §1 not already present as '
        'a literal string in the transcript above §1 must be fetched before §1 is written; '
        'the string \'§5 enumeration complete\' appears exactly once; '
        'the string \'§ implementation permitted [N]\' where N is the 1-based index of the '
        'file-modifying tool call this sentinel governs must appear in the transcript after '
        '\'§5 enumeration complete\'; no file-modifying tool call may appear before the first '
        '\'§ implementation permitted [N]\' sentinel; '
        'the literal string \'§ implementation permitted [N]\' with N matching the 1-based index '
        'of the governed tool call must appear immediately before the `(i)` line of the five-line block '
        'in the assistant text block immediately before each file-modifying tool call, in the same response turn as that tool call — '
        'a user message appearing between \'§ implementation permitted [N]\' and the tool call does not satisfy this requirement; '
        'a file-modifying tool call not immediately preceded by assistant text whose final non-blank '
        'content ends with the `(iv)` line of the five-line block does not satisfy this requirement. '
        'Quoted-span exclusion: an occurrence of any named sentinel or heading string inside a markdown '
        'code fence (a span beginning with ``` or ~~~ on its own line) does not satisfy any rung or '
        'ordering requirement — only occurrences outside code fences count toward compliance.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return (
        "The response applies a meta-process discipline before any implementation action, "
        "deriving and enforcing its own correctness conditions as transcript-inspectable strings. "
        "A rung is satisfied when and only when a tool-executed event matching its definition "
        "appears in the transcript — inference, prediction, and prior knowledge do not satisfy "
        "rung gates regardless of accuracy. "
        + GROUND_PARTS_MINIMAL["core"]
    )
