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
        'Each rung derives exclusively from the immediately preceding rung\'s output; no rung has a fixed step count. '
        'A rung that references content from any rung earlier than its immediate predecessor does not satisfy this requirement — '
        'isolation is enforced at each step; backward reference to earlier rungs is not permitted even when the content appears in the transcript. '
        'When the execution environment supports literal isolation — a fresh invocation, a separate agent context, or a new session — prefer actual isolation over in-transcript constraint enforcement. '
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
        'Goal-source classification (required after \'§0 observed\', Path A only): examine whether any line '
        'in the §0 tool-result block appears verbatim as a substring of any user message visible above §0 '
        'in the transcript. If no such line exists, write \'§0 status-only\'; a \'## Governing goal:\' line '
        'must not appear before a tool-result block whose content contains at least one line that appears as '
        'a substring of a user message above \'§0 status-only\' in the transcript — a tool-result block '
        'whose every line is a substring of content already present in the transcript above it does not '
        'satisfy this requirement. '
        '(1) derive the governing goal: \'## Governing goal: [text]\' must not appear before '
        '\'§0 observed\' in the transcript; `[text]` must appear verbatim as a substring of the '
        '§0 tool-result block above — a `[text]` value not present as a literal string in that block '
        'does not satisfy §1; immediately below the governing goal heading, before the means-test, '
        'extract labeled fields from \'[text]\': write each as a proper non-overlapping substring of \'[text]\', '
        'labeled subject, verb, outcome, or invariant; no field may equal \'[text]\' in full; '
        'no two fields may share a common phrase of 3 or more consecutive words; '
        'when every named component of \'[text]\' is covered, write \'§1a decomposed\'; '
        '\'§1a decomposed\' must appear before the means-test line; '
        '\'§1 goal derived\' must not appear before \'§1a decomposed\' in the transcript; '
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
        '(1) derive the governing goal: write \'## Governing goal: [derived: text]\' where '
        '\'[derived: text]\' is a goal derived from the scenario description — what would satisfy '
        'the underlying need, not merely what was asked; '
        'a \'[derived: text]\' value that adds a claim absent from the user\'s message does not satisfy §1; '
        'immediately below the governing goal heading, before the means-test, '
        'extract labeled fields from \'[text]\': write each as a proper non-overlapping substring of \'[text]\', '
        'labeled subject, verb, outcome, or invariant; no field may equal \'[text]\' in full; '
        'no two fields may share a common phrase of 3 or more consecutive words; '
        'when every named component of \'[text]\' is covered, '
        'write \'§1a check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of the '
        'labeled fields written above in this rung — a \'§1a check:\' line whose quoted phrase does not appear '
        'verbatim in the labeled fields above it does not satisfy this requirement; '
        'then write \'§1a decomposed\'; '
        '\'§1a decomposed\' must appear before the means-test line; '
        '\'§1a decomposed\' must not appear before a valid \'§1a check:\' line in the transcript; '
        '\'§1 goal derived\' must not appear before \'§1a decomposed\' in the transcript; '
        'immediately below \'§1a decomposed\', derive a means-test: write '
        '\'The goal [text] could be achieved by: [alternative means]\'; '
        'if only one concrete alternative can be named, write \'[hypothetical]: [speculated alternative]\' '
        'before writing \'§1 goal derived\'; '
        'when ≥2 alternatives (concrete or hypothetical) are present, '
        'write \'§1 check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the alternative means lines written above in this rung — a \'§1 check:\' line whose quoted phrase '
        'does not appear verbatim in the means-test above it does not satisfy this requirement; '
        'then write \'§1 goal derived\'; '
        '\'§1 goal derived\' must not appear before a valid \'§1 check:\' line in the transcript; '
        '(Both paths continue from §2 onward:) '
        'immediately below \'§1 goal derived\', derive dimension candidates: '
        'for each alternative means named in the means-test, write one candidate beginning with '
        '\'- Candidate:\' — a response property that would be absent in a response achieving \'[text]\' '
        'by a different means; '
        'when one candidate exists per alternative means, '
        'write \'§1b check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the candidate lines written above — a \'§1b check:\' line whose quoted phrase does not appear '
        'verbatim in the candidate lines above it does not satisfy this requirement; '
        'then write \'§1b candidates\'; '
        '\'§1b candidates\' must not appear before a valid \'§1b check:\' line in the transcript; '
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
        'derivation is unbounded: continue until every dimension carries an \'[observable:]\' tag '
        'naming a literal string or structural pattern whose presence in the response constitutes '
        'satisfaction independently of any other listed dimension; '
        'when every dimension carries an \'[observable:]\' tag, '
        'write \'§2 check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the \'[observable:]\' tag values written above in this rung — a \'§2 check:\' line whose quoted '
        'phrase does not appear verbatim in an \'[observable:]\' tag above it does not satisfy this requirement; '
        'then write \'§2 dimensions closed\'; '
        '\'§2 dimensions closed\' must not appear before a valid \'§2 check:\' line in the transcript; '
        '(2b) derive formalization: \'## Formalization\' must not appear before \'§2 dimensions closed\' '
        'in the transcript; the ## Formalization section must contain at least one expression matching '
        'one of: a typed function signature, a logical predicate (∀/∃ notation), or a concrete '
        'input/output example (f(v) = w or equivalent); immediately after that expression, apply the '
        'ambiguity test: write \'§ ambiguity test:\' followed by one quoted phrase from the expression '
        'and whether it could be satisfied by two non-equivalent outputs; if yes, that phrase names the '
        'subject of the next rung and ## Formalization must not close; when no phrase in the expression '
        'admits two non-equivalent outputs, write \'alternative satisfier:\' followed by a space and at least '
        'one non-whitespace character that is not \'[\' — a bracket character as the first non-whitespace '
        'character after \'alternative satisfier: \' signals an unfilled template and does not satisfy this requirement; '
        'the text names a concrete thing that the expression would admit but that the governing goal would reject; '
        'a formalization that cannot name such a satisfier is not yet precise enough to close; '
        '\'§ formalization complete\' must not appear before \'§ ambiguity test:\' in the transcript — '
        'a \'§ formalization complete\' that appears without a preceding \'§ ambiguity test:\' does not satisfy this requirement; '
        '\'§ formalization complete\' must not appear before a valid \'alternative satisfier:\' line '
        '(one whose first non-whitespace character after \'alternative satisfier: \' is not \'[\') '
        'in the transcript — a \'§ formalization complete\' with no preceding valid \'alternative satisfier:\' line does not satisfy this requirement; '
        'write \'§ formalization complete\' only after both \'§ ambiguity test:\' and a valid \'alternative satisfier:\' line have appeared; '
        '\'## Enforcement sequence\' must not appear before \'§ formalization complete\' in the transcript; '
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
        '\'## Completion check\' must not introduce a dimension absent from \'## Behavioral dimensions\' — '
        'a dimension named for the first time inside \'## Completion check\' does not satisfy any coverage requirement '
        'and does not extend the governed dimension set; '
        'a turn containing a satisfied \'Gate condition:\' block must contain the governed tool call in the same turn — '
        'prose appearing between the \'Gate condition:\' block and the governed tool call does not satisfy this requirement; '
        'every assistant turn after \'§ implementation permitted [N]\' has appeared in the transcript '
        'that does not contain a line beginning with \'§ implementation permitted [\' must contain \'## Completion check\' — '
        'a turn that does not contain a line beginning with \'§ implementation permitted [\' and does not contain \'## Completion check\' does not satisfy ground; '
        '\'## Completion check\' is satisfied only when the literal string \'§4 coverage verified\' appears within it — '
        'a \'## Completion check\' block that does not contain \'§4 coverage verified\' does not satisfy this requirement '
        'and the governed turn must continue to the next derived step rather than ending — '
        'the first non-blank line after the \'## Completion check\' heading must be \'Gate condition:\'; '
        'a turn whose final non-blank content line is \'§4 coverage verified\' is exempt from the resume phrase requirement; '
        'when a turn is non-exempt, its final non-blank content line, after trimming trailing whitespace, must equal exactly: '
        'Resume: say "Continue autonomously — gates still apply" to proceed under the same protocol. '
        '(5) enumerate escape paths: \'## Path enumeration\' must not appear before '
        '\'## Enforcement sequence\' in the transcript; '
        'enumerate every path by which §1–§4 headings could be present '
        'without the governing goal identified, dimensions derived, or dimensions covered; for each path, '
        'name the literal string whose presence closes it; '
        'when no further open path remains, '
        'write \'§5 check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the escape path closing strings named in the enumeration above — a \'§5 check:\' line whose '
        'quoted phrase does not appear verbatim in the path enumeration above it does not satisfy this requirement; '
        'then write \'§5 enumeration complete\'; '
        '\'§5 enumeration complete\' must not appear before a valid \'§5 check:\' line in the transcript; '
        'any referent named in the \'[text]\' from §1 not already present as '
        'a literal string in the transcript above §1 must be fetched before §1 is written; '
        'the string \'§5 enumeration complete\' appears exactly once; '
        'the string \'§ implementation permitted\' followed by a space and a decimal integer (e.g. \'§ implementation permitted 1\') '
        'must appear in the transcript after \'§5 enumeration complete\'; '
        'a sentinel line containing the literal bracket characters \'[\' or \']\' does not satisfy this requirement — '
        'only a decimal integer satisfies the index requirement; '
        'the integer must equal the 1-based ordinal count of file-modifying tool calls '
        'that will have appeared through and including the tool call immediately following this sentinel — '
        '\'§ implementation permitted 1\' must precede the first file-modifying tool call, '
        '\'§ implementation permitted 2\' must precede the second, and so on; '
        'a checker verifies this by scanning the transcript for every file-modifying tool call, '
        'locating the final non-blank line of the immediately preceding assistant message block, '
        'and confirming it matches \'§ implementation permitted N\' where N is the call\'s ordinal position; '
        'no file-modifying tool call may appear before the first such sentinel; '
        'the permit sentinel must appear as the final non-blank line of the assistant message block '
        'immediately before the assistant message block containing the file-modifying tool call — '
        'a permit sentinel in the same message block as the tool call satisfies this requirement '
        'only when it is the final non-blank line before the tool call within that block; '
        '§ implementation permitted [N] must appear immediately before the `(i)` line of each file-modifying tool call — '
        'no intervening blank lines, prose, tool-call blocks, or other content may appear between the sentinel and the `(i)` line; '
        'no user message appearing between § implementation permitted [N] and the governed tool call satisfies '
        'this requirement — a sentinel written in one turn and a tool call appearing in a later turn after a '
        'user message does not satisfy the same-turn anchor; '
        'a blank line, horizontal rule, or any other content between them does not satisfy this requirement; '
        'a file-modifying tool call not immediately preceded by assistant text whose final non-blank '
        'content ends with the `(iv)` line of the five-line block does not satisfy this requirement. '
        'Quoted-span exclusion: only an occurrence of a named sentinel or heading string on a line that '
        'is not inside a markdown code fence (a span beginning with ``` or ~~~ on its own line) and '
        'does not begin with \'>\' (a markdown block-quote prefix) counts toward compliance — '
        'an occurrence inside a code fence or on a line beginning with \'>\' does not satisfy '
        'any rung or ordering requirement. '
        'Rung-completion sentinel finality: a turn is defined as all content within a single assistant message block; '
        'a line is non-blank if it contains at least one non-whitespace character; '
        'each of the strings \'§0 observed\', \'§1 goal derived\', \'§1a decomposed\', \'§1b candidates\', '
        '\'§2 dimensions closed\', \'§ formalization complete\', \'§4 coverage verified\', and \'§5 enumeration complete\' '
        'must appear as the final non-blank line of the assistant message block in which it is written — '
        'a checker verifies this by locating the sentinel line, scanning all subsequent lines in the same '
        'assistant message block, and confirming every such line is blank (contains only whitespace or is empty); '
        'any non-blank line after the sentinel in the same assistant message block is a violation; '
        'no exceptions are permitted — if additional content must appear, it must precede the sentinel, not follow it. '
        'Continuation invariant: when the final non-blank content line of a turn contains or follows '
        'one of the rung-completion strings \'§0 observed\', \'§1 goal derived\', \'§2 dimensions closed\', '
        '\'§4 coverage verified\', or \'§5 enumeration complete\', that turn must end with one of: '
        '\'§ blocked: <text>\', \'§ awaiting: <text>\', or \'§ no-next-action: <text>\', where \'<text>\' '
        'is non-empty. A turn whose final non-blank content line contains or follows one of these strings '
        'and does not end with one of the three exit strings does not satisfy ground.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return (
        "The response runs a meta-process protocol that exists because a description of completed work is indistinguishable from actually completing it "
        "— every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "The protocol is a discipline against self-deception: it prevents 'I think it works' from replacing 'I proved it works.' "
        "Trust must come from enforced evidence, not narrative claims. "
        "The intent behind any task is an abstract goal outside the system — all artifacts derive from it, and without "
        "a named intent, there is no basis for evaluating whether an artifact satisfies it. "
        "Every task must derive a separate meta-task whose artifact is evaluation of task-to-intent alignment; "
        "the meta-task must operate before the first domain action, and the task artifact cannot certify itself. "
        "Protocol adherence must be the lowest-effort valid path — deviation must require additional effort, introduce failure risk, or be blocked. "
        "Each rung derives exclusively from the immediately preceding rung's output — this progressively narrows the interpretation space so that no rung can claim more than its inputs justify; a rung that reaches back past its immediate predecessor to earlier rungs violates this constraint regardless of whether the earlier content is visible in the transcript. "
        "Rung isolation enforcement: before writing each rung after §0, write '§ rung rejects: [quoted phrase]' where [quoted phrase] is a verbatim substring of the immediately preceding rung's output that this rung eliminates as insufficiently precise; a rung whose first non-blank line does not begin with '§ rung rejects:' does not satisfy the isolation requirement; a '§ rung rejects:' value that does not appear verbatim as a substring of the immediately preceding rung's output does not satisfy this requirement. "
        "The behavioral observation — the executed FAIL result showing the system's actual behavior against the absent governed behavior — is the rung where reality enters the chain; every rung before it is agent-authored artifact, and every rung after it derives from what that observation actually produced, not from what the agent wrote before it. "
        "Memory is not evidence — what a model recalls about a prior step carries the same confabulation risk as any other model output, so only what is visible in the transcript counts as having happened. "
        "A shorter ladder is not more efficient — each collapsed step is ambiguity that was not closed, and ambiguity that was not closed remains available as an escape route. "
        "Path B §0 is a starting gate, not a bypass — description, analysis, and planning tasks run §1–§5 in full after writing '§0 Path B: [scenario]'; the declaration opens the ladder, it does not close it. "
        "Ladder depth: a ladder is complete only when its final pre-implementation rung contains at least one expression of the form: a typed function signature, a logical predicate (∀/∃ notation), or a concrete input/output example (f(v) = w or equivalent); other domains use the equivalent terminal form — a notation where every term has an unambiguous denotation such that two independent agents given only that rung would produce functionally equivalent outputs. After writing each rung, apply the ambiguity test: quote one phrase from the rung and ask whether that phrase could be satisfied by two non-equivalent outputs. If such a phrase exists, that phrase names the subject of the next rung. The ladder is complete only when the ambiguity test finds no such phrase. A ladder that reaches implementation before passing the ambiguity test has collapsed a step and must be re-derived. "
        "Rung-type homogeneity: rung types must stay homogeneous across the ladder — all rungs before the behavioral observation must be successive precision-narrowings of the same governed behavior; introducing a new kind of artifact, deliverable, preflight check, or task category as a rung is not a narrowing and does not satisfy the ladder. A ladder that begins with intent → criteria → specification and then inserts a preflight check, implementation step, or presenter-support deliverable as a rung has switched dimensions — those items belong outside the ladder as governed actions following it, not inside it as rungs. "
        "Intent cannot be read directly from a request — every governing goal must be derived, because the request describes what was asked for, not what would satisfy the underlying need. "
        "The response applies a meta-process discipline before any implementation action, "
        "deriving and enforcing its own correctness conditions as transcript-inspectable strings. "
        "A rung is satisfied when and only when a tool-executed event matching its definition "
        "appears in the transcript — inference, prediction, and prior knowledge do not satisfy "
        "rung gates regardless of accuracy. "
        + GROUND_PARTS_MINIMAL["core"]
    )
