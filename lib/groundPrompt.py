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
        'Each derivation-phase rung (§0 through § properties complete) derives exclusively from the immediately preceding rung\'s output; no rung has a fixed step count. '
        'A derivation-phase rung that references content from any rung earlier than its immediate predecessor does not satisfy this requirement — '
        'isolation is enforced at each derivation step; backward reference to earlier derivation rungs is not permitted even when the content appears in the transcript. '
        'Verification phases (## Enforcement sequence, ## Path enumeration, ## Completion check) are not derivation rungs — they are permitted and required to reference earlier derivation outputs by property number or sentinel name. '
        'When the execution environment supports literal isolation — a fresh invocation, a separate agent context, or a new session — prefer actual isolation over in-transcript constraint enforcement. '
        'Derivation phase: '
        '(0) write \'§0: [scenario]\' as the first content line of the ground derivation, where [scenario] names the subject from the conversation — '
        'this declaration satisfies §0 and opens the ladder; '
        '\'§0:\' must not appear before the \'=== TOKENS\' section of the current invocation; '
        'if an artifact that executes the subject system and returns its live output appears verbatim in the conversation above, '
        'invoke it as a tool call immediately after writing \'§0: [scenario]\'; '
        'after that tool-result block appears and reflects live system execution, immediately write \'§0 observed\' — '
        'a tool-result block produced by invoking the named artifact as a tool call satisfies this requirement; '
        'a result produced by a Read, search, or file-write tool call does not; '
        'an artifact that returns document content does not qualify — a tool result consisting of a GitHub issue body, '
        'pull request body, specification document, README, or requirements text does not satisfy §0 regardless of invocation form; '
        'goal-source classification (required when \'§0 observed\' is present): examine whether any line in the §0 tool-result block '
        'appears verbatim as a substring of any user message visible above §0 in the transcript; '
        'if no such line exists, write \'§0 status-only\'; '
        'after \'§0 status-only\', fetch a broader context artifact before writing \'## Governing goal:\' — '
        'the fetch tool-result block must contain at least one line that appears as a substring of a user message above it in the transcript; '
        'a tool-result block whose every line is a substring of content already present in the transcript above it does not satisfy this requirement; '
        '(1) derive the governing goal: after \'§0: [scenario]\', write \'## Governing goal: [text]\' — '
        'if \'§0 observed\' is present, \'[text]\' must appear verbatim as a substring of the §0 tool-result block above; '
        'if \'§0 observed\' is absent, \'[text]\' is derived from the scenario description — what would satisfy the underlying need; '
        'a \'[text]\' value that adds a claim absent from the scenario does not satisfy §1; '
        'immediately below the governing goal heading, before the means-test, '
        'extract labeled fields from \'[text]\': write each as a proper non-overlapping substring of \'[text]\', '
        'labeled subject, verb, outcome, or invariant; no field may equal \'[text]\' in full; '
        'no two fields may share a common phrase of 3 or more consecutive words; '
        'when every named component of \'[text]\' is covered, '
        'write \'§1a check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of the '
        'labeled fields written above in this rung — a \'§1a check:\' line whose quoted phrase does not appear '
        'verbatim in the labeled fields above it does not satisfy this requirement; '
        'after a valid \'§1a check:\' line has appeared, immediately write \'§1a decomposed\'; '
        'immediately below \'§1a decomposed\', derive a means-test: write '
        '\'The goal [text] could be achieved by: [alternative means]\' — '
        'when \'§0 observed\' is present, alternative means must not duplicate approaches already listed in §0; '
        'if only one concrete alternative can be named, write \'[hypothetical]: [speculated alternative]\' before closing §1; '
        'if two non-subsuming goal candidates exist, write both and mark one \'[selected]\' — '
        'the selected goal is the one whose means-test names a more concrete alternative; '
        'when ≥2 alternatives (concrete or hypothetical) are present, '
        'write \'§1 check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the alternative means lines written above in this rung — a \'§1 check:\' line whose quoted phrase '
        'does not appear verbatim in the means-test above it does not satisfy this requirement; '
        'after a valid \'§1 check:\' line has appeared, immediately write \'§1 goal derived\'; '
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
        '(2b) derive formalization: after writing \'§2 dimensions closed\', immediately write \'## Formalization\' — '
        '\'## Formalization\' must not appear before \'§2 dimensions closed\' '
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
        'after \'§ ambiguity test:\' and a valid \'alternative satisfier:\' line have appeared, immediately write \'§ formalization complete\' — '
        '\'§ formalization complete\' must not appear before both \'§ ambiguity test:\' and a valid \'alternative satisfier:\' line have appeared; '
        '(2c) derive formalized properties: after \'§ formalization complete\', derive the notation form for this domain: '
        'examine the §2 dimensions and the governing goal to identify the mathematical notation that best represents the governed behaviors — '
        'write \'§ notation derived: [form]\' where [form] names the committed notation with a concrete example '
        '(e.g. \'f(args) → outcome\', \'∀x: T, P(x)\', \'check(G) → PASS | FAIL(reason)\'); '
        'a \'§ notation derived:\' line whose [form] contains no concrete example does not satisfy this requirement; '
        'immediately after \'§ notation derived:\', write the label line \'Formalized properties:\' — '
        'this block must appear before any artifact, implementation action, or \'§ implementation permitted\' line; '
        'decompose each §2 dimension into its formal atomic claims; '
        'each claim must appear on its own line beginning with the literal text \'property [N]:\' where N is a 1-based integer — '
        'a line beginning with \'**property\' or any markdown-formatted variant does not satisfy this requirement; '
        'each \'property [N]:\' line must contain at least one mathematical expression instantiating the form committed in \'§ notation derived:\' — any notation in which every term has a fixed denotation independent of natural-language context (e.g. ∀/∃ predicates, typed function signatures, relational expressions, or interface-shape patterns such as check(G) → PASS | FAIL(reason)) — as a literal substring; a \'property [N]:\' line containing no mathematical expression does not satisfy this requirement; '
        'after writing each \'property [N]:\' line, immediately write \'§ split test: [quoted sub-expression]\' '
        'where [quoted sub-expression] is a phrase from the parent expression naming a candidate sub-expression to split on, '
        'followed by a sentence stating whether splitting at that sub-expression yields two independently falsifiable sub-properties — '
        'a \'property [Na]:\' line that does not have a \'§ split test:\' line above it does not satisfy this requirement; '
        'if the split test finds a valid split, write one sub-property per branch: \'property [Na]:\', \'property [Nb]:\', etc., each containing a formal expression — a sub-property line whose content is prose only does not satisfy this requirement; '
        'if the split test finds no valid split (the property is already atomic), write \'property [Na]: atomic —\' followed by a restatement of the parent expression in a notation where every term has an unambiguous denotation — a restatement that two independent agents could interpret differently does not satisfy this requirement; '
        'the conjunction of all sub-property expressions for a given \'property [N]:\' must be logically equivalent to the expression in \'property [N]:\' — logical equivalence means the set of inputs satisfying all sub-property expressions simultaneously equals the set of inputs satisfying the parent expression; a conjunction satisfied by a strict subset of the parent\'s cases (e.g. a single concrete instance substituted for a variable) does not satisfy this requirement; a conjunction satisfied by a strict superset of the parent\'s cases (e.g. omitting a condition from the parent) does not satisfy this requirement; '
        'when all \'property [N]:\' and sub-property lines are written, write \'§ properties check: "[quoted phrase]"\' '
        'where [quoted phrase] is a verbatim substring of one of the \'property [N]:\' lines written above — '
        'a \'§ properties check:\' line whose quoted phrase does not appear verbatim in a \'property [N]:\' line above it does not satisfy this requirement; '
        'after a valid \'§ properties check:\' line has appeared, immediately write \'§ properties complete\' — '
        '\'§ properties complete\' must not appear before a valid \'§ properties check:\' line; '
        '(3) derive the enforcement sequence: after \'§ properties complete\', immediately write \'## Enforcement sequence\' — '
        '\'## Enforcement sequence\' must not appear before \'§ properties complete\' in the transcript, '
        'and must appear before the first file-modifying tool call regardless of whether '
        '\'§ implementation permitted\' appears; '
        'each sub-heading names as a literal substring what the prior sub-heading\'s passing state admits '
        'that this sub-heading rejects; '
        'when all sub-headings in \'## Enforcement sequence\' have been written, '
        'write \'§ enforcement check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the sub-heading lines written above in this section — a \'§ enforcement check:\' line whose quoted phrase '
        'does not appear verbatim in a sub-heading line above it does not satisfy this requirement; '
        'then write \'§ enforcement complete\'; '
        '\'§ enforcement complete\' is valid only after a valid \'§ enforcement check:\' line has appeared; '
        '(4) verify coverage: after \'§5 enumeration complete\', immediately write \'## Completion check\' — '
        '\'## Completion check\' must not appear before \'§5 enumeration complete\' in the transcript; '
        '\'## Completion check\' must appear as the next heading after \'§5 enumeration complete\' in the transcript — the first \'## \' heading line appearing after \'§5 enumeration complete\' must be \'## Completion check\'; a \'## Completion check\' appearing anywhere before \'§5 enumeration complete\' does not satisfy ground and must not be written — if the response has produced §1–§3 content and wishes to summarize or verify coverage, it must instead continue to \'## Enforcement sequence\' and \'## Path enumeration\' first; '
        '\'§ properties complete\' written before \'## Completion check\' satisfies the properties gate for the completion check — do not re-derive or repeat property lines inside \'## Completion check\'; '
        'inside \'## Completion check\', each covered dimension must cite a \'property [N]\' number from the \'Formalized properties:\' block and a verbatim string that appears either as a '
        'substring of a tool-result block produced after \'§ implementation permitted\' and visible above '
        '\'## Completion check\', or, when no such tool-result blocks are present, '
        'as a substring of the response text produced in this turn; '
        'no dimension citation or \'§4 coverage verified\' is valid until \'§ properties complete\' has appeared in the transcript; '
        '\'§ test suite complete\' is valid only after \'§ properties complete\' has appeared in the transcript — '
        'a \'§ test suite complete\' appearing before \'§ properties complete\' does not satisfy this requirement; '
        '\'§4 coverage verified\' is valid only after \'§ test suite complete\' has appeared and every covered dimension cites a property number and such a substring; '
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
        'a turn whose final non-blank content line is \'§4 coverage verified\' is exempt from the resume phrase requirement; '
        'a turn whose final non-blank content line begins with \'§ blocked:\', \'§ awaiting:\', or \'§ no-next-action:\' is exempt from the resume phrase requirement — the continuation invariant exit string is the terminal constraint for that turn; '
        'when a turn is non-exempt, its final non-blank content line, after trimming trailing whitespace, must equal exactly: '
        'Resume: say "Continue autonomously — gates still apply" to proceed under the same protocol. '
        '(5) enumerate escape paths: after \'§ enforcement complete\', immediately write \'## Path enumeration\' — '
        '\'## Path enumeration\' must not appear before \'§ enforcement complete\' in the transcript; '
        'enumerate every path by which §1–§4 headings could be present '
        'without the governing goal identified, dimensions derived, or dimensions covered; for each path, '
        'name the literal string whose presence closes it; '
        'when no further open path remains, '
        'write \'§5 check: "[quoted phrase]"\' where [quoted phrase] is a verbatim substring of one of '
        'the escape path closing strings named in the enumeration above — a \'§5 check:\' line whose '
        'quoted phrase does not appear verbatim in the path enumeration above it does not satisfy this requirement; '
        'then write \'§5 enumeration complete\'; '
        '\'§5 enumeration complete\' must not appear before a valid \'§5 check:\' line in the transcript; '
        '\'§5 enumeration complete\' must not appear before \'§ enforcement complete\' in the transcript; '
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
        'Sentinel formatting: a sentinel line must begin with the literal first character of the sentinel string (\'§\' or \'#\'); '
        'a sentinel line beginning with \'**\' or any other markdown formatting character does not satisfy this requirement. '
        'Completion check ordering: the \'## Completion check\' block must appear after \'§5 enumeration complete\' in the transcript; a \'## Completion check\' block that appears before \'§5 enumeration complete\' does not satisfy this requirement even if its contents are otherwise correct; a response that contains \'§5 enumeration complete\' and does not produce a subsequent \'## Completion check\' block containing \'Formalized properties:\', at least one \'property [N]:\' line satisfying all property requirements, \'§ properties complete\', and \'§4 coverage verified\' does not satisfy ground. '
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
        "Each derivation-phase rung derives exclusively from the immediately preceding rung's output — this progressively narrows the interpretation space so that no rung can claim more than its inputs justify; a derivation-phase rung that reaches back past its immediate predecessor violates this constraint regardless of whether the earlier content is visible in the transcript. Verification phases (## Enforcement sequence, ## Path enumeration, ## Completion check) are explicitly permitted to reference earlier derivation outputs by property number or sentinel name — they are not derivation rungs and the isolation constraint does not apply to them. "
        "Rung isolation enforcement: before writing each derivation-phase rung after §0, write '§ rung rejects: [quoted phrase]' where [quoted phrase] is a verbatim substring of the immediately preceding rung's output that this rung eliminates as insufficiently precise; a derivation-phase rung whose first non-blank line does not begin with '§ rung rejects:' does not satisfy the isolation requirement; a '§ rung rejects:' value that does not appear verbatim as a substring of the immediately preceding rung's output does not satisfy this requirement. "
        "When tools are available (§0 observed is present): the behavioral observation — the executed FAIL result showing the system's actual behavior against the absent governed behavior — is the rung where reality enters the chain; every rung before it is agent-authored artifact, and every rung after it derives from what that observation actually produced, not from what the agent wrote before it. When tools are unavailable (§0 observed is absent): the derivation structure itself is the primary artifact — the ladder runs to completion using prose-satisfiable sentinels, and this is a fully legitimate execution mode, not a degraded one. "
        "Memory is not evidence — what a model recalls about a prior step carries the same confabulation risk as any other model output, so only what is visible in the transcript counts as having happened. "
        "A shorter ladder is not more efficient — each collapsed step is ambiguity that was not closed, and ambiguity that was not closed remains available as an escape route. "
        "§0 is a starting gate, not a bypass — description, analysis, and planning tasks run §1–§5 in full after writing '§0: [scenario]'; the declaration opens the ladder, it does not close it; every rung sentinel is satisfied by the literal string appearing in the response text when no executable artifact is present — no tool call is required or expected to satisfy any rung when §0 observed is absent. "
        "Ladder depth: a ladder is complete only when its final pre-implementation rung contains at least one expression of the form: a typed function signature, a logical predicate (∀/∃ notation), or a concrete input/output example (f(v) = w or equivalent); other domains use the equivalent terminal form — a notation where every term has an unambiguous denotation such that two independent agents given only that rung would produce functionally equivalent outputs. After writing each rung, apply the ambiguity test: quote one phrase from the rung and ask whether that phrase could be satisfied by two non-equivalent outputs given the governing goal as context — the test is decidable per rung because the governing goal provides a fixed reference that bounds what counts as non-equivalent. If such a phrase exists, that phrase names the subject of the next rung. The ladder is complete only when the ambiguity test finds no such phrase. A ladder that reaches implementation before passing the ambiguity test has collapsed a step and must be re-derived. "
        "Rung-type homogeneity: rung types must stay homogeneous across the ladder — all derivation-phase rungs must be successive precision-narrowings of the same governed behavior; introducing a new kind of artifact, deliverable, preflight check, or task category as a rung is not a narrowing and does not satisfy the ladder. A ladder that begins with intent → criteria → specification and then inserts a preflight check, implementation step, or presenter-support deliverable as a rung has switched dimensions — those items belong outside the ladder as governed actions following it, not inside it as rungs. "
        "Intent cannot be read directly from a request — every governing goal must be derived by inferring what would satisfy the underlying need from the scenario's subject matter; derivation means selecting the most precise formulation of what the scenario implies, not adding requirements absent from it; a goal that introduces a new constraint not implied by the scenario has overreached, and a goal that merely restates the request has not derived anything. "
        "The response applies a meta-process discipline before any implementation action, "
        "deriving and enforcing its own correctness conditions as transcript-inspectable strings. "
        "A rung is satisfied when and only when a transcript-visible event matching its definition "
        "appears — when §0 observed is present, rungs require tool-executed events and the behavioral "
        "observation is where reality enters the chain; when §0 observed is absent, no executable "
        "artifact exists and rungs are satisfied by the literal sentinel string appearing in the "
        "response text — this is an acknowledged weaker form of evidence that enables the protocol "
        "to run on non-executable subjects (specifications, contracts, analyses) while preserving the "
        "derivation structure; the protocol's preference for execution over description holds, but "
        "does not block the protocol when execution is unavailable; "
        "inference, prediction, and prior knowledge do not satisfy rung gates regardless of accuracy. "
        + GROUND_PARTS_MINIMAL["core"]
    )
