"""Axis configuration as static Python maps (token -> description).

Generated from the axis registry; keep in sync with list edits.

SYNC_WARNING: Changes to token names/descriptions affect:
- internal/barcli/help_llm.go (hardcoded heuristics and usage patterns)
- .opencode/skills/bar-workflow/skill.md (method categorization)
- internal/barcli/help_llm_test.go (validation tests)

When adding a new axis token (edit this file directly — it is the SSOT):
Required for all axes:
1. AXIS_KEY_TO_VALUE        — description (prompt injection text)
2. AXIS_KEY_TO_LABEL        — short CLI-facing label (3-8 words, ADR-0109)
3. AXIS_KEY_TO_KANJI        — 1-2 character kanji icon (ADR-0143)
4. AXIS_KEY_TO_ROUTING_CONCEPT — shortest phrase mapping user framing to the token (ADR-0146)
5. AXIS_TOKEN_METADATA      — definition, heuristics list, distinctions list (ADR-0155)

Conditional:
- AXIS_KEY_TO_CATEGORY      — method axis only: semantic family (ADR-0144)
- CROSS_AXIS_COMPOSITION    — only if the token has notable cross-axis interactions (ADR-0147)
- FORM_DEFAULT_COMPLETENESS — form axis only, if the format structurally constrains depth (ADR-0153)

After editing, run `make axis-regenerate-apply` to normalize formatting and update downstream files.

When renaming/removing tokens:
1. Update help_llm.go hardcoded references
2. Update skill.md if method categories change
3. Run `go test ./internal/barcli/ -run TestLLMHelp` to validate

Directional axis compass model (AXIS_KEY_TO_VALUE["directional"]):
Tokens form a 2D compass — they push responses in a direction, not a sequence:
  fog (↑ abstract/general) ←→ dig (↓ concrete/specific)  — vertical axis
  rog (← reflect/structure) ←→ ong (→ act/extend)         — horizontal axis
Simple tokens push in one direction. Compound tokens span the full axis
simultaneously — fig = fog+dig means abstract AND concrete at once, not
alternating. Three-part compounds (fly rog, dip ong, fip bog, etc.) orient
along three directions at once: they are still orientations, not sequences.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, TypedDict, Union

# ADR-0171: ground prompt structured parts — SSOT is lib/groundPrompt.py (not generated).
# Edit GROUND_PARTS there and run `make axis-regenerate-apply` to propagate changes.
from lib.groundPrompt import GROUND_PARTS, build_ground_prompt  # noqa: F401

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "The response takes the shape of an Architecture Decision Record (ADR) document with sections for context, decision, and consequences, formatted as a structured document ready "
        "for version control. Best suited for decision-making tasks and architectural tradeoffs.",
        "code": "The response consists only of code or markup as the complete output, with no surrounding natural-language explanation or narrative.",
        "codetour": "The response is delivered as a valid VS Code CodeTour `.tour` JSON file (schema-compatible) with steps and fields appropriate to the task, omitting extra prose or "
        "surrounding explanation.",
        "diagram": "The response converts the input into Mermaid diagram code only: it infers the best diagram type for the task and respects Mermaid safety constraints (Mermaid diagrams do not "
        "allow parentheses in the syntax or raw '|' characters inside node labels; the text uses numeric encodings such as \"#124;\" for '|' instead of raw problematic characters).",
        "draw": "The response is delivered as a spatial prose layout using ASCII arrangement, boxes, arrows, indentation, and a short legend where needed. Human-readable and not "
        "machine-parseable. Use when a conceptual overview in spatial form is wanted without the precision constraints of Mermaid or D2.",
        "gherkin": "The response outputs only Gherkin format as the complete output, using Jira markup where appropriate and omitting surrounding explanation. Works with presenterm/diagram "
        "channels when wrapped in markdown code blocks.",
        "html": "The response consists solely of semantic HTML as the complete output, with no surrounding prose or explanation.",
        "image": "The response consists solely of an image as the complete output — described through subject, style, composition, lighting, and technical parameters — with no surrounding prose "
        "or explanation.",
        "jira": "The response formats the content using Jira markup (headings, lists, panels) where relevant and avoids extra explanation beyond the main material.",
        "notebook": "The response is delivered as a valid Jupyter notebook (`.ipynb` JSON), with an ordered sequence of markdown and code cells appropriate to the task, structured for execution "
        "and exploration. No surrounding prose outside the notebook structure.",
        "plain": "The response uses plain prose with natural paragraphs and sentences as the delivery format, imposing no additional structural conventions such as bullets, tables, or code "
        "blocks.",
        "presenterm": 'The response is a valid multi-slide presenterm deck expressed as raw Markdown (no code fences). The front matter always matches: "--- newline title: <descriptive title '
        "based on the input with colons encoded as &#58; and angle brackets encoded as &lt; and &gt;> newline author: Generated (or authors: [...]) newline date: YYYY-MM-DD "
        'newline --- newline" with no other keys. The deck contains up to 12 slides. Each slide starts with a Setext header (title line followed by a line of ---), includes '
        "content and references, and ends with an HTML comment named end_slide on its own line followed by a blank line; the final slide may omit the closing end_slide. A blank "
        'line always precedes the References section so that a line with "References" or "- References" is separated by one empty line. Directives appear only as standalone HTML '
        'comments with exact syntax: "<!-- end_slide -->", "<!-- pause -->", "<!-- column_layout: [7, 3] -->", "<!-- column: 0 -->", "<!-- reset_layout -->", and "<!-- '
        'jump_to_middle -->". Code fence safety is enforced: whenever a fenced code block opens (for example ```mermaid +render, ```bash +exec, ```latex +render, ```d2 +render), '
        "the response includes a matching closing fence of exactly three backticks on its own line before any non-code content, directive, or end_slide; if a fence remains open at "
        "slide end, the response emits the closing fence first. Mermaid diagrams use code blocks tagged mermaid +render; LaTeX uses latex +render; D2 uses d2 +render; executable "
        'snippets use fenced code blocks whose info string starts with a language then +exec (optionally +id:<name>) or +exec_replace or +image. The response emits "<!-- '
        'snippet_output: name -->" only when a snippet with +id:name exists. Lines hidden with # or /// prefixes follow language conventions; other code blocks appear only when '
        "relevant and include the language name; images appear only when valid paths or URLs exist. Within the slide body (outside fenced or inline code and outside HTML "
        "directives), the deck never includes raw HTML: every literal '<' becomes &lt; and every literal '>' becomes &gt;, preventing raw angle brackets in body text. Markdown "
        'safety prevents accidental styling: standalone or path-embedded \'~\' becomes "&#126;" (so "~/foo" becomes "&#126;/foo") while intentional "~~text~~" remains unchanged. '
        "Mermaid safety keeps grammar and delimiters intact ([], (), [[]], (()), [/ /]); node and edge labels appear inside ASCII double quotes and use Mermaid-compatible numeric "
        'codes with no leading ampersand, such as "#91;" for "[", "#93;" for "]", "#40;" for "(", "#41;" for ")", "#123;" for "{{", "#125;" for "}}", "#60;" for "<", "#62;" for '
        '">", "#35;" for "#", "#58;" for ":", and "&" and slashes \'/\' remain as-is, with no additional entity encodings, and labels are never double-encoded. The deck avoids # '
        "headers in slide bodies.",
        "remote": "The response is optimised for remote delivery, ensuring instructions work in distributed or online contexts and surfacing tooling or interaction hints suitable for video, "
        "voice, or screen sharing.",
        "shellscript": "The response is delivered as a shell script output format, focusing on correct, executable shell code rather than prose or explanation.",
        "sketch": "The response emits only pure D2 diagram source as the complete output. The response must use valid D2 syntax and only documented D2 shapes (e.g., rectangle, circle, cylinder, "
        "diamond, hexagon, cloud, text). To create visually distinct boxes, use 'border-radius' or style attributes instead of non-existent shapes like 'rounded' or 'note'. "
        "Explanatory or note-like content must be modeled using shape: text or a styled standard shape. Do not include any surrounding natural language or commentary. Ensure the "
        "output is syntactically correct and compiles successfully with the D2 CLI.",
        "slack": "The response formats the answer for Slack using appropriate Markdown, mentions, and code blocks while avoiding channel-irrelevant decoration.",
        "store": "The response additionally writes output to persistent storage using available tools — a file on disk, a memory system, or any other durable medium the environment supports — "
        "as the work progresses. Conversational output continues normally; storage is additive, not a replacement. When no storage tool is available, the response notes explicitly what "
        "should be saved and suggests how.",
        "svg": "The response consists solely of SVG markup as the complete output, with no surrounding prose, remaining minimal and valid for direct use in an `.svg` file.",
        "sync": "The response takes the shape of a synchronous or live session plan (agenda, steps, cues) rather than static reference text.",
        "video": "The response consists solely of a video as the complete output — described through scene, camera motion, subject actions, style, and temporal progression — with no surrounding "
        "prose or explanation.",
    },
    "completeness": {
        "deep": "The response goes into substantial depth within the chosen scope, unpacking reasoning layers and fine details without necessarily enumerating every edge case.",
        "full": "The response provides a thorough answer for normal use, covering all major aspects without needing every micro-detail.",
        "gist": "The response offers a short but complete answer or summary that touches the main points once without exploring every detail.",
        "grow": "The response begins at minimal depth and expands only where the analysis explicitly demands it, so every elaboration is justified rather than anticipated.",
        "max": "The response is as exhaustive as reasonable, covering essentially everything relevant and treating omissions as errors.",
        "minimal": "The response makes the smallest change or provides the smallest answer that satisfies the request, avoiding work outside the core need.",
        "narrow": "The response restricts the discussion to a very small slice of the topic, avoiding broad context.",
        "skim": "The response performs only a very light pass, addressing the most obvious or critical issues without aiming for completeness.",
        "triage": "The response allocates analytical depth by consequence × uncertainty: areas where both are high receive full coverage; areas where both are low receive minimal or no "
        "coverage. The coverage allocation is stakes-proportionate rather than uniform.",
        "zoom": "The response covers the full range of the subject by treating it as exponentially-spaced buckets from smallest natural unit to largest. Each bucket receives substantive "
        "coverage — the response addresses the subject at every level, not merely names or lists the scale. Both ends must appear as explicit anchors: do not begin at an "
        "intermediate level or leave either end implicit. Bucket sizes scale exponentially with span magnitude: each order of magnitude in span produces roughly one step up in "
        "granularity, so steps are multiplicative, not additive. Applies to any axis with natural magnitude: quantities (units → millions), hierarchy levels (function → system), "
        "spatial scale, time (minutes → years), complexity tiers, or fuzzy buckets.",
    },
    "directional": {
        "bog": "The response additionally orients across the full horizontal axis — spanning both the reflective/structural dimension (rog) and the acting/extending dimension (ong), "
        "covering structure, implications, actions, and extensions together.",
        "dig": "The response additionally orients toward the concrete and specific — examining grounded details and examples rather than abstractions.",
        "dip bog": "The response additionally orients toward the concrete across the full horizontal span — grounded in specific examples and details, shaped by structural examination and "
        "action together.",
        "dip ong": "The response additionally orients toward the concrete and acting — grounded in specific examples and details, shaped toward identifying what to do and extending those "
        "actions.",
        "dip rog": "The response additionally orients toward the concrete and structural — grounded in specific examples and details, shaped by how they are organized and what that reveals.",
        "fig": "The response additionally orients across the full vertical axis — spanning both the abstract/general dimension (fog) and the concrete/specific dimension (dig), using each to "
        "illuminate the other.",
        "fip bog": "The response additionally orients across all four compass dimensions — spanning abstract and concrete while shaped by structural examination and action together.",
        "fip ong": "The response additionally orients across the full vertical axis toward action — spanning abstract and concrete, shaped toward identifying what to do and extending those "
        "actions.",
        "fip rog": "The response additionally orients across the full vertical axis toward the structural — spanning abstract and concrete, shaped by how the subject is organized and what "
        "that reveals.",
        "fly bog": "The response additionally orients toward the abstract across the full horizontal span — anchored in general patterns and principles, shaped by structural examination and "
        "action together.",
        "fly ong": "The response additionally orients toward the abstract and acting — anchored in general patterns and principles, shaped toward identifying what to do and extending those "
        "actions.",
        "fly rog": "The response additionally orients toward the abstract and structural — anchored in general patterns and principles, shaped by how they are organized and what that "
        "reveals.",
        "fog": "The response additionally orients toward the abstract and general — identifying patterns and principles that transcend the specifics, toward broader insights.",
        "jog": "The response applies no directional orientation. Use when a directional token is required by the grammar but no compass push is desired.",
        "ong": "The response additionally orients toward action and extension — identifying what to do and extending those actions to related situations or next steps.",
        "rog": "The response additionally orients toward the structural and reflective dimension — how the subject is organized and what that organization reveals.",
    },
    "form": {
        "actions": "The response structures ideas as concrete actions or tasks a user or team could take, leaving out background analysis or explanation.",
        "activities": "The response organizes ideas as concrete session activities or segments—what to do, by whom, and in what order—rather than abstract description.",
        "bug": "The response structures ideas as a bug report with sections for Steps to Reproduce, Expected Behavior, Actual Behavior, and Environment or Context, emphasizing concise, testable "
        "details. Strongest with diagnostic and debugging tasks (`probe`, or `make`/`show` paired with diagnostic methods: `diagnose`, `inversion`, `adversarial`). Creates semantic friction "
        "with non-debugging tasks (e.g., `fix`, which is a reformat task in bar's grammar). Conflicts with session-plan channels (`sync`) — a bug report is a static artifact, not a live "
        "session agenda.",
        "bullets": "The response organizes ideas as concise bullet points, avoiding long paragraphs.",
        "cards": "The response organizes ideas as discrete cards or items, each with a clear heading and short body, avoiding long continuous prose.",
        "case": "The response structures reasoning by building the case before the conclusion, laying out background, evidence, trade-offs, and alternatives before converging on a clear "
        "recommendation that addresses objections and constraints.",
        "checklist": "The response organizes ideas as an actionable checklist whose items are clear imperative tasks rather than descriptive prose.",
        "cocreate": "The response structures itself as a collaborative process — small moves, explicit decision points, and alignment checks rather than a one-shot answer. Without an "
        "output-exclusive channel, conducts this interactively: proposes, pauses for feedback, and iterates. With one, formats the artifact to expose decision points and invite "
        "response.",
        "commit": "The response structures ideas as a conventional commit message with a short type or scope line and an optional concise body.",
        "contextualise": "The response packages the subject to be passed directly to another LLM operation: it enriches the content with all context a downstream model would need to act on it "
        "without further explanation — adding background, assumptions, constraints, and framing that would otherwise be implicit or missing. The main content is not rewritten.",
        "coupling": "The response structures the output as a coupling map — showing which domains or components are joined at a seam, what crosses that boundary, and where the interface is. Pairs "
        "naturally with snag/mesh methods and diagram/sketch channels.",
        "direct": "The response structures ideas by leading with the main point or recommendation, followed only by the most relevant supporting context, evidence, and next steps.",
        "facilitate": "The response structures itself as a facilitation plan — framing the goal, proposing session structure, managing participation and turn-taking rather than doing the work "
        "solo. Without an output-exclusive channel, acts as a live facilitator; with one, produces a static facilitation guide.",
        "faq": "The response organizes ideas as clearly separated question headings with concise answers beneath each one, keeping content easy to skim and free of long uninterrupted prose.",
        "formats": "The response structures ideas by focusing on document types, writing formats, or structural templates and their suitability.",
        "ghost": "The response structures itself as a sequence of autonomous actions with their observed results, rather than as explanation or planning. The response presents a workflow execution "
        "trace: action taken, result observed, next action, result observed. When combined with a channel, the trace is expressed within that channel's format constraints.",
        "indirect": "The response begins with brief background, reasoning, and trade-offs and finishes with a clear bottom-line point or recommendation that ties them together.",
        "log": "The response reads like a concise work or research log entry with date or time markers as needed, short bullet-style updates, and enough context for future reference without "
        "unrelated narrative.",
        "merge": "The response combines multiple sources into a single coherent whole while preserving essential information.",
        "prep": "The response structures the output as an experiment write-up: hypothesis, method, expected outcomes, and evaluation criteria. Used to design an experiment before running it.",
        "questions": "The response presents the answer as a series of probing or clarifying questions rather than statements. When combined with `diagram` channel, the output is Mermaid code "
        "structured as a question tree, decision map, or inquiry flow rather than a structural diagram of the subject.",
        "quiz": "The response organizes content as a quiz structure — questions posed before explanations, testing understanding through active recall before providing answers. Without an "
        "output-exclusive channel, conducts this as an interactive exchange; with one, structures the output as a quiz document.",
        "recipe": "The response expresses the answer as a recipe that includes a custom, clearly explained mini-language and a short key for understanding it.",
        "scaffold": "The response explains with scaffolding: it starts from first principles, introduces ideas gradually, uses concrete examples and analogies, and revisits key points so a learner "
        "can follow and retain the concepts. Most effective with learning-oriented audiences (student, entry-level engineer). May conflict with expert-level or brevity-first personas "
        "where first-principles exposition contradicts assumed expertise.",
        "snap": "The response structures the output as a state snapshot: current progress, key decisions made, what remains, and enough context to resume, reconstruct, or hand off the work from "
        "this point. Forward-oriented — captures where things stand for later pickup, not what happened during the work.",
        "socratic": "The response employs a Socratic, question-led method by asking short, targeted questions that surface assumptions, definitions, and gaps in understanding, withholding full "
        "conclusions until enough answers exist or the user explicitly requests a summary.",
        "spike": "The response formats the backlog item as a research spike: it starts with a brief problem or decision statement, lists the key questions the spike should answer, and stays "
        "focused on questions and learning rather than implementation tasks.",
        "story": 'The response formats the backlog item as a user story using "As a <persona>, I want <capability>, so that <value>." It may include a short description and high-level acceptance '
        "criteria in plain prose but avoids Gherkin or test-case syntax.",
        "table": "The response presents the main answer as a Markdown table when feasible, keeping columns and rows compact.",
        "taxonomy": "The response organizes the main content as a classification system, type hierarchy, or category taxonomy, defining types, their relationships, and distinguishing attributes "
        "clearly. Output adapts to channel: code channel → type system (interfaces, enums, hierarchies); markup → hierarchical structure; no channel → prose sections.",
        "test": "The response presents test cases in a structured format with clear setup, execution, and assertion sections, organized by scenario type (happy path, edge cases, errors, "
        "boundaries) and including descriptive test names.",
        "tight": "The response uses concise, dense prose, remaining freeform without bullets, tables, or code and avoiding filler.",
        "timeline": "The response structures the output as a timeline or sequence layout — stages, events, or steps arranged in temporal order with explicit markers for when each occurs. Pairs "
        "naturally with trace/flow methods and diagram/sketch channels.",
        "twin": "The response presents two or more alternatives side-by-side, giving each equal structural weight so the reader can compare them directly without narrative interleaving.",
        "variants": "The response presents several distinct, decision-ready options as separate variants, labelling each one with a short description and including approximate probabilities when "
        "helpful while avoiding near-duplicate alternatives.",
        "vet": "The response structures the output as a post-experiment review: what was observed, how outcomes compare to expectations, what was learned, and what follows. Complements prep.",
        "walkthrough": "The response guides the audience step by step by outlining stages and walking through them in order so understanding builds gradually.",
        "wardley": "The response expresses the answer as a Wardley Map showing value chain evolution from genesis to commodity.",
        "wasinawa": "The response applies a What–So What–Now What reflection: it describes what happened, interprets why it matters, and proposes concrete next steps.",
    },
    "method": {
        "abduce": "The response enhances the task by generating explanatory hypotheses that best account for the available evidence, explicitly comparing alternative explanations.",
        "actors": "The response enhances the task by identifying and centering people, roles, or agents involved in the system.",
        "adversarial": "The response enhances the task by running a constructive stress-test, systematically searching for weaknesses, edge cases, counterexamples, failure modes, and unstated "
        "assumptions.",
        "afford": "The response models behavior as shaped by the structural configuration of available actions. Explanations must distinguish between logical possibility and practical salience, "
        "account for how system design foregrounds or suppresses specific actions, and specify how structural constraints pre-shape the perceived action space. Outcomes may not be "
        "attributed solely to preferences or incentives without modeling how affordances influenced selection.",
        "align": "The response restructures relationships, assumptions, or responsibilities so that explicit elements reinforce rather than contradict one another, restoring global coherence "
        "across the system.",
        "amorph": "The response enhances the task by identifying regions where behavior, meaning, or interaction depends on ambiguous, fluid, or emergent structure rather than stable, explicit "
        "organization, indicating lack of crystallized system form.",
        "analog": "The response enhances the task by reasoning through analogy, mapping relational structure from a known case onto the subject and examining where the analogy holds or breaks.",
        "analysis": "The response enhances the task by decomposing the subject into its constituent components and examining each for its role, properties, and interactions—without imposing a "
        "specific organizing principle such as spatial layout, dependency chains, groupings, hierarchies, historical causation, or governing criteria.",
        "argue": "The response enhances the task by structuring reasoning as an explicit argument, identifying claims, premises, warrants, and rebuttals and assessing their support.",
        "automate": "The response enhances the task by modeling what can be expressed as automatic, repeatable operations and preferring those over manual, human-dependent steps — identifying "
        "where human intervention can be eliminated or reduced, and expressing solutions in terms of what the system can do without human involvement.",
        "balance": "The response describes the acceptable equilibrium state of a system — the balance point between opposing forces — and specifies tolerances or conditions under which balance "
        "is maintained.",
        "behave": "The response enhances the task by analysing using the COM-B model (Capability, Opportunity, Motivation, Behaviour), identifying key enablers and barriers across those "
        "dimensions, mapping them to Behaviour Change Wheel intervention functions and behaviour change techniques, and outlining a minimal, testable implementation and evaluation "
        "plan.",
        "bias": "The response enhances the task by identifying likely cognitive biases, heuristics, or systematic errors and examining how they might distort judgment or conclusions.",
        "boom": "The response enhances the task by exploring behaviour toward extremes of scale or intensity, examining what breaks, dominates, or vanishes.",
        "bound": "The response enhances the task by introducing or reinforcing structural limits that restrict the extent of influence, interaction, or propagation across the system, ensuring "
        "effects remain within intended conceptual or operational regions.",
        "calc": "The response enhances the task by expressing reasoning as executable or quasi-executable procedures, calculations, or formal steps whose outputs constrain conclusions.",
        "cite": "The response enhances the task by including sources, citations, or references that anchor claims to evidence, enabling verification and further exploration.",
        "clash": "The response enhances the task by identifying where explicit structures, rules, or commitments conflict or misalign, analyzing how locally valid elements produce global "
        "inconsistency or breakdown.",
        "cluster": "The response groups or organizes existing items into clusters based on shared characteristics, relationships, or criteria, without altering the underlying content or meaning "
        "of the items.",
        "compare": "The response enhances the task by systematically comparing alternatives against explicit criteria, surfacing tradeoffs, relative strengths and weaknesses, and decision "
        "factors. Use when the user presents options and asks which to choose or how they differ.",
        "control": "The response distinguishes between factors within agency and those outside it, directing evaluation and effort exclusively toward the former.",
        "converge": "The response enhances the task by systematically narrowing from broad exploration to focused recommendations, weighing trade-offs explicitly as options are filtered.",
        "crystal": "The response enhances the task by shaping the system so that behavior, interaction, propagation, and meaning are determined primarily by explicit structural organization "
        "rather than by interpretive reasoning, implicit assumption, or uncontrolled coupling.",
        "deduce": "The response enhances the task by applying deductive reasoning, deriving conclusions that must follow from stated premises or assumptions and making logical entailment "
        "explicit.",
        "depends": "The response enhances the task by tracing dependency relationships, identifying what depends on what and how changes propagate through the system.",
        "diagnose": "The response enhances the task by seeking likely causes of problems first, narrowing hypotheses through evidence, falsification pressure, and targeted checks before "
        "proposing fixes or changes.",
        "dimension": "The response enhances the task by exploring multiple dimensions or axes of analysis, making implicit factors explicit and examining how they interact.",
        "domains": "The response enhances the task by identifying bounded contexts, domain boundaries, and capabilities.",
        "drift": "The response enhances the task by identifying where conclusions are treated as necessary but are not structurally enforced by the representation, analyzing how this looseness "
        "allows interpretive inference or hidden assumption to substitute for derivability, producing inconsistency.",
        "effects": "The response enhances the task by tracing second- and third-order effects and summarizing their downstream consequences.",
        "experimental": "The response enhances the task by proposing concrete experiments or tests, outlining how each would run, describing expected outcomes, and explaining how results would "
        "update the hypotheses.",
        "field": "The response models interaction as occurring through a shared structured medium in which effects arise from structural compatibility rather than direct reference between "
        "actors. Explanations must make the medium and its selection rules explicit.",
        "flow": "The response enhances the task by describing the linear ordering of stages or steps in a process, without modeling handoffs or feedback loops.",
        "gap": "The response enhances the task by identifying where assumptions, rules, roles, or relationships are treated as explicit but remain implicit, analyzing how that mismatch produces "
        "ambiguity, coordination failure, or error.",
        "ground": "I is the declared intent governing the invocation. I precedes and is not itself an artifact. Every artifact derives from I through the prior rung — form changes, intent does "
        "not. V is a constraint artifact self-contained to evaluate the next artifact without consulting I. O is the output evaluated against V. Three rules govern every thread. R1 (I "
        "is fixed): every artifact derives from I through faithful derivation of the prior rung — the form changes, the intent does not. R2 (rung criterion): an artifact is a rung iff "
        "upward-faithful (derived from the prior rung without adding unstated constraints) and downward-sufficient (self-contained to evaluate the next artifact without consulting I); "
        "domain phases are not downward-sufficient — writing tests for 'API layer' requires knowing what the API must do, which comes from I, not the phase name. R3 (observation "
        "terminates): every thread descends to observed running behavior; only tool-executed output with a declared gap satisfies the execution gate; skipped tests are not "
        "observations. A rung is complete when and only when its artifact has been produced — not when it has been listed, planned, or described. A rung is not achievable when the "
        "domain provides no standard artifact type for it; this must be stated explicitly with justification — convenience, anticipated outcome, or prior knowledge do not make a rung "
        "not achievable. ground is a Process method — the task governs the character of each rung's output but not the process structure; the manifest, rung sequence, and execution "
        "gates are mandatory regardless of which task or other tokens are combined with ground; completeness governs rung depth, not rung existence. Executable verification is required "
        "only for executable artifacts; prose artifacts do not require execution to be complete. Formal notation must satisfy R2: every behavioral constraint from the criteria rung "
        "must be re-expressed in the notation — not just interface shape; type signatures or schemas that capture structure without encoding invariants do not satisfy this rung. "
        "Boundary: the manifest is the first and only output before the manifest-complete sentinel — no rung work, planning text, or content of any kind may appear before it; "
        "observation of existing code or running behavior sufficient to establish I is permitted before the manifest when I cannot be declared from context alone — this is I-formation, "
        "not rung work; exploration beyond what is needed to declare I belongs as the first rung of the manifest, not pre-manifest. Foundational constraint: a symbol is not the state "
        "it represents — a rung label during execution marks the point where the artifact begins — it is not a section heading for planning, description, or exploration about the rung; "
        "no content other than the artifact itself may appear between a rung label and the artifact it precedes. Eagerness to implement is the primary failure mode — an implementation "
        "produced without passing validation is invalid and will be discarded; the shortest path to a valid implementation is strict rung adherence, not shortcuts; every skipped rung "
        "produces output that must be thrown away. When beginning mid-ladder, first locate the highest already-instantiated rung and update it to reflect the intended change, then "
        "descend. Traversal (R5): depth-first by thread; within a thread, advance through every feasible rung; stopping mid-thread is only permitted when the next rung is not "
        "achievable. For code contexts, each rung in this sequence may not be skipped or combined with another — the executable implementation rung is blocked until the validation run "
        "observation rung has declared a gap. R4 instantiates as: prose (natural language description of intent and constraints) → criteria (acceptance conditions as plain statements) "
        "→ formal notation (non-executable specification — contracts with pre/post conditions, schemas with explicit invariants, or pseudocode with behavioral constraints stated; must "
        "satisfy R2 — artifact cannot be run as written) → executable validation (a file artifact invocable by an automated tool — go test, pytest, or equivalent — written to target "
        "the declared gap; only validation artifacts may be produced at this rung — implementation code is not permitted at this rung even though artifact-writing is permitted; file "
        "reads, grep output, and manual inspection do not constitute executable validation regardless of label; pre-existing artifacts not targeting the gap do not satisfy this rung) → "
        "validation run observation → executable implementation → observed running behavior. A gate is a conversation-state condition: open when and only when the required event has "
        "occurred in this conversation for this thread. Prior knowledge, anticipation, and model reasoning cannot satisfy any gate regardless of accuracy. Underlying all compliance "
        "failures is one epistemological error: substituting model knowledge for conversation events. For executable rungs, emit 🔴 Execution observed: [verbatim tool output — content "
        "composed without running the tool is invalid] then 🔴 Gap: [what the verbatim output reveals] on their own lines before any implementation artifact. No implementation artifact "
        "— including planning text, code blocks, or tool calls — may appear before valid Execution observed + Gap sentinels; if any implementation content appears without these "
        "sentinels immediately preceding it, it is invalid and must be discarded before the tool is run. Before producing implementation code, emit 🟢 Implementation gate cleared — gap "
        "cited: [verbatim from 🔴 Execution observed]. The quote must be verbatim from the 🔴 Execution observed sentinel of this thread; quoting anticipated output or a prior thread's "
        "observation is invalid. The 🔴 sentinel format is reserved exclusively for executable rung gates. For non-executable rungs, observation appears inline as labeled prose. When "
        "the lowest V is complete, output ‘✅ Validation artifact V complete’ on its own line before producing O — this phrase may only appear after the executable validation rung has "
        "been both produced and invoked and the validation run observation rung has declared a gap. Gap-locality: the gap gating rung N is the output of executing rung N-1. No gap from "
        "any higher rung, and no element of I directly, may serve as the gating gap for the current rung. Minimal scope: the current rung's artifact addresses the declared gap and "
        "nothing more. Implementing beyond the declared gap is a violation — not a benefit. Upward revision is always permitted when a gap is observed between prior understanding of I "
        "and something encountered via direct interaction with reality, code, or a stakeholder. Upward revision must be signposted with: what was observed, which rung is being revised, "
        "and why. It is never permitted to change I without first observing a gap in V that derived it. Changing I requires revising every artifact derived from it to restore chain "
        "consistency before descent continues. Intent precedes its representations. Every artifact that documents the governing intent of this invocation — whether produced in this "
        "invocation or pre-existing in the codebase — must be consistent with I before the invocation closes. If reconciliation is feasible, return up the chain to prose and rederive. "
        "If not feasible, report as a named process failure: which artifact diverges, what the divergence is, and why reconciliation could not occur. The invocation close must include "
        "a reconciliation report: either “all representations reconciled” or the list of named failures with reasons. ✅ Thread N complete may only appear after observed running "
        "behavior for that thread has been produced and recorded. ✅ Manifest exhausted — N/N threads complete may only appear after all threads have emitted their completion sentinels "
        "and the reconciliation report has been produced.",
        "grove": "The response enhances the task by examining how small effects compound into larger outcomes through feedback loops, network effects, or iterative growth—asking not just what "
        "fails or succeeds, but how failures OR successes accumulate through systemic mechanisms.",
        "induce": "The response enhances the task by applying inductive reasoning, generalizing patterns from specific observations and assessing the strength and limits of those "
        "generalizations.",
        "inversion": "The response enhances the task by beginning from undesirable or catastrophic outcomes, asking what would produce or amplify them, then working backward to avoid, mitigate, "
        "or design around those paths.",
        "jobs": "The response enhances the task by analyzing Jobs To Be Done—the outcomes users want to achieve and the forces shaping their choices.",
        "ladder": "The response enhances the task by moving deliberately between abstraction levels — stepping up to higher-level causes, patterns, or systems, and stepping down to concrete "
        "consequences or implementations, ordered by importance to the audience.",
        "mapping": "The response enhances the task by surfacing elements, relationships, and structure, then organising them into a coherent spatial map rather than a linear narrative.",
        "mark": "The response enhances the task by capturing checkpoints and evidence as a process runs — recording what was observed at each stage rather than narrating the progression.",
        "meld": "The response enhances the task by reasoning about combinations, overlaps, balances, and constraints between elements.",
        "melody": "The response rates a seam or coupling using three coupling pressure dimensions. Visibility: how explicit and discoverable the contract is — named orchestrators, typed "
        "interfaces, documented invariants score high; scattered helpers or implicit state score low. Scope: how widely a change at this seam propagates across domains or layers — "
        "confined to a single bounded context scores low; ripples across multiple services, teams, or abstraction layers scores high. Volatility: how tightly temporal or structural "
        "coupling forces synchronised change sets — tight timing dependencies, shared schemas, shared algorithms, or positional interfaces score high. All three pressures must appear "
        "in the output; omitting any one is incomplete.",
        "mesh": "The response enhances the task by describing how coupling propagates — tracing what each coupled domain affects and how influence travels across the seam.",
        "migrate": "The response modifies the task by introducing a transition path between existing and new structures, allowing change while maintaining temporary compatibility during the "
        "shift.",
        "mint": "The response constructs the generative assumptions explicitly, building a structured derivation from which conclusions follow as direct products of the model.",
        "mod": "The response enhances the task by applying modulo-style reasoning—equivalence classes, cyclic patterns, quotient structures, or periodic behavior that repeats with a defined "
        "period or wraps around boundaries.",
        "models": "The response enhances the task by explicitly identifying and naming relevant mental models, explaining why they apply (or fail), and comparing or combining them.",
        "objectivity": "The response enhances the task by distinguishing objective facts from subjective opinions and supporting claims with evidence.",
        "operations": "The response enhances the task by identifying operations research or management science concepts that frame the situation.",
        "order": "The response enhances the task by applying abstract structural reasoning such as hierarchy, dominance, or recurrence. When paired with `sort` task, `order` adds emphasis on the "
        "criteria and scheme driving the sequencing rather than merely producing the sorted result — consider whether the distinction is needed.",
        "origin": "The response enhances the task by uncovering how the subject arose, why it looks this way now, and how past decisions shaped the present state.",
        "perturb": "The response deliberately introduces controlled variations or faults into a system in order to observe its response and evaluate the adequacy of its safeguards, assumptions, "
        "or detection mechanisms.",
        "polar": "The response models behavior or system dynamics as shaped by both attractors (desired or rewarded states) and repellers (avoided or penalized states), distinguishing pursuit "
        "from avoidance.",
        "preserve": "The response modifies the task by maintaining compatibility with existing structures, interfaces, or assumptions, constraining changes so previously valid components "
        "continue to function without modification.",
        "prioritize": "The response enhances the task by assessing and ordering items by importance or impact, making the ranking and rationale explicit.",
        "probability": "The response enhances the task by applying probability or statistical reasoning to characterize uncertainty and likely outcomes.",
        "product": "The response enhances the task by examining the subject through a product lens—features, user needs, and value propositions.",
        "pulse": "The response models information transfer as a staged encode/decode process, distinguishing message from signal, accounting for noise and channel distortion, and specifying how "
        "transmission errors are detected and repaired.",
        "reify": "The response enhances the task by identifying implicit patterns, assumptions, or relationships and making them explicit as formal entities, distinctions, or rules that "
        "constrain reasoning.",
        "release": "The response reduces distortion or disturbance by loosening attachment or identification with transient states, roles, or outcomes.",
        "reset": "The response modifies the task by discarding compatibility constraints and reconstructing the structure as if no prior commitments existed.",
        "resilience": "The response enhances the task by concentrating on how the system behaves under stress and uncertainty—fragility vs robustness, margin of safety, and tail risks.",
        "rigor": "The response enhances the task by relying on disciplined, well-justified reasoning and making its logic explicit.",
        "risks": "The response enhances the task by focusing on potential problems, failure modes, or negative outcomes and their likelihood or severity.",
        "ritual": "The response structures actions according to established roles and ordered relationships, emphasizing social coherence through proper conduct and recognized procedures.",
        "robust": "The response enhances the task by reasoning under deep uncertainty, favoring options that perform acceptably across many plausible futures rather than optimizing for a single "
        "forecast.",
        "root": "The response models each proposition, rule, or dependency as having a single authoritative locus within the explanatory structure. Apparent duplication must be reduced to "
        "derivation from a canonical source, and parallel accounts must be explicitly mapped or unified. Explanations may not treat multiple representations of the same knowledge as "
        "independent causal or justificatory elements without specifying their dependency relationship.",
        "seep": "The response enhances the task by identifying where influence, responsibility, meaning, or constraint extends beyond its intended scope, analyzing how this overreach increases "
        "coupling, ambiguity, or fragility.",
        "sense": "The response surfaces pre-reductive judgment—a compressed evaluative impression that expresses directional fit, tension, stability, or unease before explicit analytic "
        "decomposition. Multiple weak signals are held together rather than unpacked one by one.",
        "sever": "The response restructures the system by introducing or reinforcing separations between domains of influence, responsibility, or meaning, ensuring that interactions occur only "
        "through explicit, controlled interfaces.",
        "shear": "The response enhances the task by outlining steps to separate or realign coupled domains, reducing the seam to an explicit, controlled interface.",
        "shift": "The response enhances the task by deliberately rotating through distinct perspectives or cognitive modes, contrasting how each frame interprets the same facts.",
        "simulation": "The response enhances the task by focusing on explicit thought experiments or scenario walkthroughs that project evolution over time, highlighting feedback loops, "
        "bottlenecks, tipping points, and emergent effects.",
        "snag": "The response enhances the task by surfacing coupled domains or seams — identifying where responsibilities or meanings are intermixed in ways that prevent clean separation.",
        "split": "The response enhances the task by deliberately decomposing the subject into parts or components, analyzing each in isolation while intentionally bracketing interactions, "
        "treating the decomposition as provisional and preparatory rather than final.",
        "spur": "The response enhances the task by exploring multiple reasoning paths in parallel, branching on key assumptions or choices before evaluating and pruning alternatives.",
        "survive": "The response enhances the task by treating claims, designs, or implementations as provisional until exposed to live conditions whose uncontrolled variation can preserve, "
        "distort, or overturn prior validation, distinguishing staged confirmation from environmental survival and requiring that observed behavior under deployment conditions "
        "determine what remains credible.",
        "sweep": "The response enhances the task by enumerating the option space broadly, generating and listing plausible approaches without evaluating or committing to any of them.",
        "systemic": "The response enhances the task by reasoning about the subject as an interacting whole, identifying components, boundaries, flows, feedback loops, and emergent behaviour that "
        "arise from their interactions rather than from parts in isolation.",
        "thrust": "The response enhances the task by identifying and cataloging competing structural forces or design pressures, making each force and its magnitude explicit.",
        "trace": "The response enhances the task by narrating the sequential control or data progression, making the path from input to outcome explicit through intermediate steps and structural "
        "changes.",
        "unknowns": "The response enhances the task by identifying critical unknown unknowns and exploring how they might impact outcomes.",
        "verify": "The response enhances the task by applying falsification pressure to claims, requiring externally imposed constraints and explicitly defined negative space, without governing "
        "the layer those tests must satisfy.",
        "visual": "The response enhances the task by framing ideas spatially — placing concepts in positional relationship and building a coordinate model of the subject.",
        "yield": "The response advances the task by reducing forceful intervention, allowing structures or dynamics to resolve through minimal guided action rather than imposed direction.",
    },
    "scope": {
        "act": "The response focuses on what is being done or intended—tasks, activities, operations, or work to be performed—suppressing interpretation, evaluation, structural explanation, or "
        "perspective-shifting.",
        "agent": "The response explains outcomes in terms of identifiable actors with the capacity to select among alternatives, specifying who can act, what options are available, and how their "
        "choices influence results, rather than attributing outcomes solely to impersonal structure or equilibrium dynamics.",
        "assume": "The response focuses on explicit or implicit premises that must hold for the reasoning, system, or argument to function.",
        "cross": "The response focuses on concerns or forces that propagate across otherwise distinct units, layers, or domains—examining how they traverse boundaries or become distributed across "
        "partitions—without primarily analyzing internal arrangement or recurring structural form.",
        "dam": "The response focuses on containment boundaries — what remains within defined limits, what is explicitly excluded or kept out, and where boundaries are drawn between what belongs "
        "inside versus outside a defined scope.",
        "fail": "The response focuses on breakdowns, stress, uncertainty, or limits by examining how and under what conditions something stops working—risks, edge cases, fragility, or failure "
        "modes rather than overall quality or preferred outcomes.",
        "good": "The response focuses on how quality, success, or goodness is judged—criteria, metrics, standards, values, or taste—assuming a framing rather than defining it or shifting "
        "perspective.",
        "mean": "The response focuses on how something is conceptually framed or understood prior to evaluation or action—its purpose, interpretation, definitions, categorization, or theoretical "
        "role—without asserting required premises, judging quality, prescribing action, or adopting a specific stakeholder perspective.",
        "motifs": "The response focuses on recurring structural or thematic forms that appear in multiple places, identifying repeated configurations or isomorphic patterns without analyzing "
        "their internal topology in detail or their boundary-spanning distribution.",
        "stable": "The response focuses on equilibrium, persistence, and self-reinforcing states within a system—identifying configurations that maintain themselves and analyzing how "
        "perturbations affect their continuity.",
        "storage": "The response focuses on the storage dimension — what state or output must survive beyond the current operation, what medium it is stored in, the lifetime and recovery "
        "guarantees, and the conditions under which it can be lost or corrupted.",
        "struct": "The response focuses on how parts of a system are arranged and related—dependencies, coordination, constraints, incentives, or organizing configurations—analyzing the internal "
        "topology of units without emphasizing repetition across instances or boundary-spanning propagation.",
        "thing": "The response focuses on what entities are in view—objects, people, roles, systems, domains, or bounded units—and what is excluded, without emphasizing actions, relationships, "
        "evaluation, or perspective.",
        "time": "The response focuses on when things occur and how they change over time—sequences, evolution, history, phases, or temporal dynamics—rather than static structure, evaluation, or "
        "immediate action.",
        "view": "The response focuses on how the subject appears from a specific stakeholder, role, or positional perspective, making that viewpoint explicit without asserting it as definitive, "
        "evaluating outcomes, or prescribing action.",
    },
}

# Short CLI-facing labels for token selection (ADR-0109).
# 3-8 words. Audience: selecting agent or human.
# Distinct from descriptions which are prompt-injection instructions.
AXIS_KEY_TO_LABEL: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "Architecture Decision Record format",
        "code": "Code or markup only, no prose",
        "codetour": "VS Code CodeTour JSON file",
        "diagram": "Mermaid diagram only",
        "draw": "Spatial ASCII prose layout",
        "gherkin": "Gherkin scenario format",
        "html": "Semantic HTML only, no prose",
        "jira": "Jira markup formatting",
        "plain": "Plain prose, no structural decoration",
        "presenterm": "Presenterm slide deck",
        "remote": "Optimized for remote delivery",
        "shellscript": "Shell script format",
        "sketch": "D2 diagram source only",
        "slack": "Slack-formatted Markdown",
        "store": "Write output to persistent storage",
        "svg": "SVG markup only",
        "sync": "Synchronous session plan",
    },
    "completeness": {
        "deep": "Substantial depth within scope",
        "full": "Thorough, all major aspects",
        "gist": "Brief but complete summary",
        "grow": "Expand only when demanded",
        "max": "Exhaustive, treat omissions as errors",
        "minimal": "Smallest satisfying answer only",
        "narrow": "Restricted to a very small slice",
        "skim": "Light pass, obvious issues only",
        "triage": "Stakes-weighted coverage depth",
        "zoom": "Full-range coverage at adaptive granularity",
    },
    "directional": {
        "bog": "Span reflection and action (rog + ong)",
        "dig": "Ground in concrete details",
        "dip bog": "Concrete with full horizontal orientation",
        "dip ong": "Concrete and acting orientation",
        "dip rog": "Concrete, structural, and reflective orientation",
        "fig": "Span abstract and concrete (fog + dig)",
        "fip bog": "All four compass orientations",
        "fip ong": "Full vertical and acting orientation",
        "fip rog": "Full vertical, structural, and reflective orientation",
        "fly bog": "Abstract with full horizontal orientation",
        "fly ong": "Abstract and acting orientation",
        "fly rog": "Abstract, structural, and reflective orientation",
        "fog": "Surface abstract patterns and principles",
        "jog": "Execute intent directly, no clarification",
        "ong": "Acting and extending orientation",
        "rog": "Structural and reflective orientation",
    },
    "form": {
        "actions": "Concrete actions and tasks",
        "activities": "Session activities and segments",
        "bug": "Bug report format",
        "bullets": "Concise bullet points",
        "cards": "Discrete cards with headings",
        "case": "Build the case before the conclusion",
        "checklist": "Actionable checklist",
        "cocreate": "Collaborative small-move process",
        "commit": "Conventional commit message",
        "contextualise": "Add or reshape supporting context",
        "coupling": "Coupling map layout",
        "direct": "Lead with main point first",
        "facilitate": "Facilitation plan and session structure",
        "faq": "Question-and-answer format",
        "formats": "Document types and writing formats",
        "ghost": "Workflow execution trace",
        "indirect": "Background first, conclusion last",
        "log": "Work or research log entry",
        "merge": "Combine multiple sources coherently",
        "prep": "Experiment design write-up",
        "questions": "Answer as probing questions",
        "quiz": "Quiz structure, questions before answers",
        "recipe": "Recipe with ingredients and steps",
        "scaffold": "First-principles scaffolded explanation",
        "snap": "State snapshot for resumption or handoff",
        "socratic": "Question-led Socratic dialogue",
        "spike": "Research spike backlog item",
        "story": "User story format",
        "table": "Markdown table presentation",
        "taxonomy": "Classification or type hierarchy",
        "test": "Structured test cases",
        "tight": "Concise dense prose",
        "timeline": "Timeline or sequence layout",
        "twin": "Side-by-side comparison layout",
        "variants": "Several distinct labeled options",
        "vet": "Post-experiment review",
        "walkthrough": "Step-by-step guided walkthrough",
        "wardley": "Wardley map",
        "wasinawa": "What–So What–Now What reflection",
    },
    "method": {
        "abduce": "Generate explanatory hypotheses",
        "actors": "Center people, roles, and agents",
        "adversarial": "Constructive stress-testing",
        "afford": "Affordance-driven behavior analysis",
        "align": "Restructure for global coherence",
        "amorph": "Identify fluid unstructured regions",
        "analog": "Reasoning by analogy",
        "analysis": "Describe and structure the situation",
        "argue": "Explicit argument structure",
        "automate": "Prefer automated over manual steps",
        "balance": "Equilibrium description",
        "behave": "COM-B behavioral analysis",
        "bias": "Identify cognitive biases",
        "boom": "Explore behavior at extremes of scale",
        "bound": "Constrain propagation",
        "calc": "Quantitative or executable reasoning",
        "cite": "Include sources and references",
        "clash": "Identify conflicting structures or rules",
        "cluster": "Group items by shared characteristics",
        "compare": "Compare alternatives against criteria",
        "control": "Focus on what is within agency",
        "converge": "Narrow from broad to focused",
        "crystal": "Shape toward explicit structure",
        "deduce": "Deductive logical reasoning",
        "depends": "Trace dependency relationships",
        "diagnose": "Identify likely root causes",
        "dimension": "Explore multiple analytical axes",
        "domains": "Identify bounded contexts",
        "drift": "Identify underenforced conclusions",
        "effects": "Trace second and third-order effects",
        "experimental": "Propose concrete experiments",
        "field": "Model interaction as a shared structured medium",
        "flow": "Linear stage sequencing",
        "gap": "Implicit-to-explicit gap analysis",
        "ground": "Intent-governed validation pipeline",
        "grove": "Accumulation and rate-of-change effects",
        "induce": "Generalize patterns from examples",
        "inversion": "Reason from catastrophic outcomes back",
        "jobs": "Jobs-to-be-done analysis",
        "ladder": "Move between abstraction levels",
        "mapping": "Surface elements and relationships",
        "mark": "Capture audit checkpoints",
        "meld": "Explore combinations and overlaps",
        "melody": "Rate seam coupling pressure",
        "mesh": "Describe coupling propagation",
        "migrate": "Introduce a transition path between structures",
        "mint": "Explicit constructive derivation",
        "mod": "Equivalence classes and cyclic reasoning",
        "models": "Apply named mental models explicitly",
        "objectivity": "Separate facts from opinions",
        "operations": "Operations research frameworks",
        "order": "Abstract structural and ordering reasoning",
        "origin": "Uncover how the subject arose",
        "perturb": "Introduce controlled faults to observe system response",
        "polar": "Attractor and repeller dynamics",
        "preserve": "Maintain compatibility with existing structures",
        "prioritize": "Rank items by importance or impact",
        "probability": "Probabilistic and statistical reasoning",
        "product": "Product lens — features, users, value",
        "pulse": "Information transfer staged encode/decode model",
        "reify": "Make implicit patterns explicit as rules",
        "release": "Loosen attachment to transient states",
        "reset": "Reconstruct without prior compatibility constraints",
        "resilience": "Behavior under stress and recovery",
        "rigor": "Disciplined, well-justified reasoning",
        "risks": "Potential problems and failure modes",
        "ritual": "Structure via established roles and procedures",
        "robust": "Reason under deep uncertainty",
        "root": "Reduce multiple representations to a single authoritative source",
        "seep": "Identify scope overreach",
        "sense": "Pre-reductive evaluative impression",
        "sever": "Enforce domain separations",
        "shear": "Separate coupled domains",
        "shift": "Rotate through distinct perspectives",
        "simulation": "Thought experiments and scenario walkthroughs",
        "snag": "Surface coupling seams",
        "split": "Decompose into parts or components",
        "spur": "Parallel reasoning paths",
        "survive": "Environmental survival of claims",
        "sweep": "Enumerate option space without evaluating",
        "systemic": "Interacting whole and feedback loops",
        "thrust": "Catalog competing structural forces",
        "trace": "Narrate sequential progression",
        "unknowns": "Surface critical unknown unknowns",
        "verify": "Falsification pressure",
        "visual": "Spatial/positional framing",
        "yield": "Minimal action, allow natural resolution",
    },
    "scope": {
        "act": "Tasks and intended actions",
        "agent": "Actors with agency and decision-making",
        "assume": "Premises and preconditions",
        "cross": "Cross-cutting concerns spanning modules",
        "dam": "Containment boundaries and limits",
        "fail": "Breakdowns and failure modes",
        "good": "Quality criteria and success standards",
        "mean": "Conceptual meaning and framing",
        "motifs": "Recurring patterns and themes",
        "stable": "Stability and persistence of states",
        "storage": "Durable state and storage layer",
        "struct": "Arrangement and relationships",
        "thing": "Entities and bounded units",
        "time": "Sequences and temporal change",
        "view": "Stakeholder perspective",
    },
}

# Kanji icons for visual display (ADR-0143). 1-2 character kanji per token
# for faster visual scanning in help, SPA, and TUI2. Display only - not part
# of input grammar.
# Persona axis uses Dict[str, Dict[str, str]] (sub-axis -> token -> kanji);
# all other axes use Dict[str, str] (token -> kanji).
AXIS_KEY_TO_KANJI: Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]]]] = {
    "channel": {
        "adr": "記",
        "code": "碼",
        "codetour": "観",
        "diagram": "図",
        "draw": "枠",
        "gherkin": "瓜",
        "html": "標",
        "image": "像",
        "jira": "票",
        "notebook": "帳",
        "plain": "文",
        "presenterm": "演",
        "remote": "遠",
        "shellscript": "脚",
        "sketch": "描",
        "slack": "通",
        "store": "保",
        "svg": "画",
        "sync": "期",
        "video": "映",
    },
    "completeness": {"grow": "増", "triage": "険", "zoom": "比"},
    "directional": {
        "bog": "反",
        "dig": "具",
        "dip bog": "混",
        "dip ong": "働",
        "dip rog": "建",
        "fig": "抽",
        "fip bog": "幻",
        "fip ong": "現",
        "fip rog": "計",
        "fly bog": "翔",
        "fly ong": "飛",
        "fly rog": "察",
        "fog": "概",
        "jog": "走",
        "ong": "行",
        "rog": "構",
    },
    "form": {
        "actions": "行",
        "activities": "動",
        "bug": "虫",
        "bullets": "列",
        "cards": "卡",
        "case": "策",
        "checklist": "検",
        "cocreate": "共",
        "commit": "提",
        "contextualise": "脈",
        "coupling": "繋",
        "direct": "直",
        "facilitate": "促",
        "faq": "質",
        "formats": "様",
        "ghost": "幽",
        "indirect": "間",
        "log": "誌",
        "merge": "合",
        "prep": "備",
        "questions": "問",
        "quiz": "試",
        "recipe": "法",
        "scaffold": "足",
        "snap": "残",
        "socratic": "導",
        "spike": "査",
        "story": "話",
        "table": "表",
        "taxonomy": "別",
        "test": "験",
        "tight": "簡",
        "twin": "双",
        "variants": "変",
        "vet": "評",
        "walkthrough": "歩",
        "wardley": "鎖",
        "wasinawa": "振",
    },
    "method": {
        "abduce": "因",
        "actors": "者",
        "adversarial": "攻",
        "afford": "構",
        "align": "調",
        "amorph": "曖",
        "analog": "類",
        "analysis": "析",
        "argue": "論",
        "automate": "自",
        "balance": "均",
        "behave": "動",
        "bias": "偏",
        "boom": "極",
        "bound": "限",
        "calc": "計",
        "cite": "引",
        "clash": "衝",
        "cluster": "集",
        "compare": "較",
        "control": "掌",
        "converge": "収",
        "crystal": "晶",
        "deduce": "演",
        "depends": "依",
        "diagnose": "診",
        "dimension": "次",
        "domains": "領",
        "drift": "漂",
        "effects": "効",
        "experimental": "実",
        "field": "場",
        "flow": "流",
        "gap": "隙",
        "ground": "地",
        "grove": "蓄",
        "induce": "帰",
        "inversion": "逆",
        "jobs": "需",
        "ladder": "階",
        "mapping": "写",
        "mark": "印",
        "meld": "融",
        "melody": "旋",
        "mesh": "網",
        "migrate": "移",
        "mint": "鋳",
        "mod": "周",
        "models": "型",
        "objectivity": "客",
        "operations": "営",
        "order": "順",
        "origin": "起",
        "perturb": "擾",
        "polar": "磁",
        "preserve": "守",
        "prioritize": "優",
        "probability": "確",
        "product": "商",
        "pulse": "伝",
        "reify": "形",
        "release": "放",
        "reset": "初",
        "resilience": "耐",
        "rigor": "厳",
        "risks": "危",
        "ritual": "礼",
        "robust": "堅",
        "root": "準",
        "seep": "溢",
        "sense": "感",
        "sever": "断",
        "shear": "剪",
        "shift": "転",
        "simulation": "象",
        "snag": "絡",
        "split": "分",
        "spur": "枝",
        "survive": "存",
        "sweep": "探",
        "systemic": "系",
        "thrust": "衡",
        "trace": "跡",
        "unknowns": "未",
        "verify": "証",
        "visual": "絵",
        "yield": "任",
    },
    "persona": {
        "audience": {
            "to CEO": "首",
            "to Kent Beck": "貝",
            "to LLM": "言",
            "to XP enthusiast": "好",
            "to analyst": "析",
            "to designer": "設",
            "to junior engineer": "新",
            "to managers": "監",
            "to platform team": "基",
            "to principal engineer": "長",
            "to product manager": "管",
            "to programmer": "者",
            "to stakeholders": "益",
            "to stream aligned team": "流",
            "to team": "団",
        },
        "intent": {
            "announce": "告",
            "appreciate": "謝",
            "coach": "導",
            "inform": "知",
            "persuade": "説",
            "teach": "教",
        },
        "tone": {
            "casually": "軽",
            "directly": "直",
            "formally": "式",
            "gently": "優",
            "kindly": "慈",
        },
        "voice": {
            "as Kent Beck": "貝",
            "as PM": "監",
            "as designer": "師",
            "as facilitator": "介",
            "as future historian": "史",
            "as junior engineer": "初",
            "as principal engineer": "纂",
            "as programmer": "程",
            "as prompt engineer": "吟",
            "as scientist": "科",
            "as storyteller": "語",
            "as teacher": "教",
            "as writer": "著",
        },
    },
    "scope": {
        "act": "為",
        "agent": "主",
        "assume": "仮",
        "cross": "横",
        "dam": "圏",
        "fail": "敗",
        "good": "良",
        "mean": "意",
        "motifs": "紋",
        "stable": "安",
        "storage": "庫",
        "struct": "造",
        "thing": "物",
        "time": "時",
        "view": "視",
    },
    "task": {
        "check": "検",
        "diff": "較",
        "fix": "修",
        "make": "作",
        "pick": "選",
        "plan": "策",
        "probe": "探",
        "pull": "抜",
        "show": "示",
        "sim": "模",
        "sort": "整",
    },
}

# Category assignments for method tokens (ADR-0144).
# Each method token is assigned to exactly one semantic family by primary use case.
# Tokens that span multiple families are placed by primary use case; contested
# placements are resolved by the authors and recorded here as the authoritative SSOT.
AXIS_KEY_TO_CATEGORY: Dict[str, Dict[str, str]] = {
    "method": {
        "abduce": "Reasoning",
        "actors": "Actor-centered",
        "adversarial": "Diagnostic",
        "afford": "Actor-centered",
        "align": "Structural",
        "amorph": "Diagnostic",
        "analog": "Generative",
        "analysis": "Structural",
        "argue": "Reasoning",
        "automate": "Structural",
        "balance": "Comparative",
        "behave": "Actor-centered",
        "bias": "Reasoning",
        "boom": "Exploration",
        "bound": "Structural",
        "calc": "Reasoning",
        "cite": "Reasoning",
        "clash": "Diagnostic",
        "cluster": "Structural",
        "compare": "Comparative",
        "control": "Conduct",
        "converge": "Comparative",
        "crystal": "Structural",
        "deduce": "Reasoning",
        "depends": "Structural",
        "diagnose": "Diagnostic",
        "dimension": "Comparative",
        "domains": "Exploration",
        "drift": "Diagnostic",
        "effects": "Temporal/Dynamic",
        "experimental": "Exploration",
        "field": "Actor-centered",
        "flow": "Temporal/Dynamic",
        "gap": "Structural",
        "ground": "Process",
        "grove": "Generative",
        "induce": "Reasoning",
        "inversion": "Diagnostic",
        "jobs": "Actor-centered",
        "ladder": "Reasoning",
        "mapping": "Structural",
        "mark": "Temporal/Dynamic",
        "meld": "Comparative",
        "melody": "Diagnostic",
        "mesh": "Diagnostic",
        "migrate": "Structural",
        "mint": "Structural",
        "mod": "Generative",
        "models": "Generative",
        "objectivity": "Reasoning",
        "operations": "Temporal/Dynamic",
        "order": "Structural",
        "origin": "Structural",
        "perturb": "Diagnostic",
        "polar": "Comparative",
        "preserve": "Structural",
        "prioritize": "Comparative",
        "probability": "Reasoning",
        "product": "Generative",
        "pulse": "Temporal/Dynamic",
        "reify": "Generative",
        "release": "Conduct",
        "reset": "Structural",
        "resilience": "Diagnostic",
        "rigor": "Reasoning",
        "risks": "Diagnostic",
        "ritual": "Conduct",
        "robust": "Diagnostic",
        "root": "Structural",
        "seep": "Diagnostic",
        "sense": "Reasoning",
        "sever": "Structural",
        "shear": "Structural",
        "shift": "Generative",
        "simulation": "Temporal/Dynamic",
        "snag": "Diagnostic",
        "split": "Exploration",
        "spur": "Exploration",
        "survive": "Diagnostic",
        "sweep": "Exploration",
        "systemic": "Temporal/Dynamic",
        "thrust": "Comparative",
        "trace": "Temporal/Dynamic",
        "unknowns": "Diagnostic",
        "verify": "Reasoning",
        "visual": "Generative",
        "yield": "Conduct",
    }
}

# Canonical display order for semantic category groups within each axis (ADR-0144).
# Adding a new category requires only updating this dict; all consumers derive order from it.
AXIS_CATEGORY_ORDER: Dict[str, List[str]] = {
    "method": [
        "Process",
        "Reasoning",
        "Exploration",
        "Structural",
        "Diagnostic",
        "Actor-centered",
        "Temporal/Dynamic",
        "Comparative",
        "Generative",
        "Conduct",
    ]
}

# Distilled routing concept phrases for nav surfaces (ADR-0146 Phase 2).
# Each token maps to the shortest phrase that maps a user's framing to that token.
# Tokens sharing the same phrase group into a single routing bullet:
#   e.g. thing + struct → 'Entities/boundaries'
# Covered axes: scope and form only. Method routing uses editorial sub-group
# labels spanning multiple tokens and stays hardcoded until a future ADR.
AXIS_KEY_TO_ROUTING_CONCEPT: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "Architecture decision record",
        "code": "Code output",
        "codetour": "VS Code tour",
        "diagram": "Mermaid diagram",
        "draw": "ASCII spatial layout",
        "gherkin": "Gherkin scenarios",
        "html": "HTML output",
        "image": "Image output",
        "jira": "Jira formatting",
        "notebook": "Jupyter notebook",
        "plain": "Plain prose",
        "presenterm": "Slide deck",
        "remote": "Remote delivery",
        "shellscript": "Shell script",
        "sketch": "D2 diagram",
        "slack": "Slack formatting",
        "store": "Persist to durable storage",
        "svg": "SVG output",
        "sync": "Session plan",
        "video": "Video output",
    },
    "completeness": {
        "deep": "Unpack reasoning layers and fine details",
        "full": "Thorough coverage without exhausting every edge case",
        "gist": "Essential points only",
        "grow": "Expand on demand",
        "max": "Exhaustive — every case, every edge",
        "minimal": "Briefest valid response",
        "narrow": "Focused depth on a specific slice",
        "skim": "Surface-level coverage",
        "triage": "Stakes-proportionate coverage depth",
        "zoom": "Full-range coverage at adaptive granularity",
    },
    "directional": {
        "bog": "Reflect + act",
        "dig": "Concrete/specific",
        "dip bog": "Concrete, structural, and acting",
        "dip ong": "Concrete and acting",
        "dip rog": "Concrete, structural, and reflective",
        "fig": "Abstract + concrete",
        "fip bog": "All four compass directions",
        "fip ong": "Full vertical and acting",
        "fip rog": "Full vertical, structural, and reflective",
        "fly bog": "Abstract, structural, and acting",
        "fly ong": "Abstract and acting",
        "fly rog": "Abstract, structural, and reflective",
        "fog": "Abstractify/generalise",
        "jog": "Execute directly",
        "ong": "Act and extend",
        "rog": "Reflect on structure",
    },
    "form": {
        "actions": "Actionable next steps",
        "activities": "Session activities",
        "bug": "Bug report",
        "bullets": "Bullet points",
        "cards": "Cards/items",
        "case": "Decision documentation",
        "checklist": "Actionable next steps",
        "cocreate": "Collaborative process",
        "commit": "Commit message",
        "contextualise": "LLM context package",
        "coupling": "Coupling map",
        "direct": "Lead with conclusion",
        "facilitate": "Facilitation plan",
        "faq": "FAQ format",
        "formats": "Format comparison",
        "ghost": "Workflow execution trace",
        "indirect": "Background then conclusion",
        "log": "Work log entry",
        "merge": "Combine sources",
        "prep": "Experiment design",
        "questions": "Probing questions",
        "quiz": "Quiz structure",
        "recipe": "Step-by-step with custom notation",
        "scaffold": "Building understanding",
        "snap": "State snapshot for resumption",
        "socratic": "Question-led inquiry",
        "spike": "Research spike",
        "story": "User story",
        "table": "Structured comparison",
        "taxonomy": "Classification system",
        "test": "Test cases",
        "tight": "Concise prose",
        "timeline": "Timeline or sequence layout",
        "twin": "Side-by-side comparison",
        "variants": "Multiple alternatives",
        "vet": "Post-experiment review",
        "walkthrough": "Linear step-by-step narration",
        "wardley": "Wardley map",
        "wasinawa": "What/So What/Now What",
    },
    "method": {
        "abduce": "Best explanation",
        "actors": "People/roles",
        "adversarial": "Stress test",
        "afford": "Structural affordances",
        "align": "Restore structural coherence",
        "amorph": "Fluid/amorphous structure",
        "analog": "Reasoning by analogy",
        "analysis": "Decompose components",
        "argue": "Formal argument",
        "automate": "Automate repeatable steps",
        "balance": "Equilibrium description",
        "behave": "COM-B / behavior change",
        "bias": "Cognitive biases",
        "boom": "Extreme scale behavior",
        "bound": "Contain side effects",
        "calc": "Formal calculation",
        "cite": "Evidence/sources",
        "clash": "Structural conflicts",
        "cluster": "Group/categorize",
        "compare": "Side-by-side comparison",
        "control": "Focus on what you control",
        "converge": "Narrow to recommendation",
        "crystal": "Crystallize into explicit structure",
        "deduce": "Logical deduction",
        "depends": "Dependency tracing",
        "diagnose": "Root cause",
        "dimension": "Multiple dimensions",
        "domains": "Bounded contexts",
        "drift": "Underenforced conclusions",
        "effects": "Second-order effects",
        "experimental": "Design experiments",
        "field": "Structural field effects",
        "flow": "Step-by-step flow",
        "gap": "Implicit gaps",
        "ground": "Intent-governed validation pipeline",
        "grove": "Compounding effects",
        "induce": "Generalise from examples",
        "inversion": "Start from failure",
        "jobs": "Jobs to be done",
        "ladder": "Abstraction level traversal",
        "mapping": "Spatial map",
        "mark": "Audit trail",
        "meld": "Combinations/overlaps",
        "melody": "Seam pressure profile",
        "mesh": "Coupling analysis",
        "migrate": "Compatibility transition path",
        "mint": "Constructive derivation",
        "mod": "Cyclic/periodic patterns",
        "models": "Named mental models",
        "objectivity": "Facts vs opinions",
        "operations": "Operations research",
        "order": "Abstract ordering",
        "origin": "Historical causation",
        "perturb": "Introduce controlled variations",
        "polar": "Attractors/repellers",
        "preserve": "Backward compatibility",
        "prioritize": "Rank by importance",
        "probability": "Statistical reasoning",
        "product": "Product lens",
        "pulse": "Information encode/decode transmission",
        "reify": "Make implicit explicit",
        "release": "Let go of attachment",
        "reset": "Clean slate/greenfield",
        "resilience": "Stress and fragility",
        "rigor": "Disciplined reasoning",
        "risks": "Potential problems",
        "ritual": "Structure via established roles and procedures",
        "robust": "Works across futures",
        "root": "Single source of truth",
        "seep": "Scope overreach",
        "sense": "Weighted impression before analysis",
        "sever": "Enforce domain separation",
        "shear": "Coupling mitigation",
        "shift": "Rotate perspectives",
        "simulation": "Scenario walkthrough",
        "snag": "Coupling detection",
        "split": "Decompose in isolation",
        "spur": "Multiple paths",
        "survive": "Environmental arbitration",
        "sweep": "Enumerate option space",
        "systemic": "System as whole",
        "thrust": "Catalog structural forces",
        "trace": "Sequential narration",
        "unknowns": "Unknown unknowns",
        "verify": "Falsification pressure",
        "visual": "Spatial/positional framing",
        "yield": "Minimal intervention / natural resolution",
    },
    "scope": {
        "act": "Actions/tasks",
        "agent": "Actors with agency",
        "assume": "Premises/preconditions",
        "cross": "Cross-cutting concerns",
        "dam": "Containment and boundaries",
        "fail": "Failure modes",
        "good": "Quality/criteria",
        "mean": "Understanding/meaning",
        "motifs": "Recurring patterns",
        "stable": "Invariants/stable states",
        "storage": "Durable state and storage layer",
        "struct": "Entities/boundaries",
        "thing": "Entities/boundaries",
        "time": "Sequences/change",
        "view": "Perspectives",
    },
    "task": {
        "check": "Evaluate pass/fail",
        "diff": "Compare subjects",
        "fix": "Reformat/edit",
        "make": "Create new content",
        "pick": "Choose from options",
        "plan": "Propose strategy",
        "probe": "Analyse/surface structure",
        "pull": "Extract/select subset",
        "show": "Explain/describe",
        "sim": "Play out scenario",
        "sort": "Arrange/categorize",
    },
}

# ADR-0147: Cross-axis composition semantics.
# Structure: axis_a → token_a → axis_b → {"natural": [...], "cautionary": {token: warning}}
#
# "natural": token_b combinations that work with token_a without any special
#            interpretation. The LLM produces good output without explicit guidance.
#            Positive "what does this produce" cases are handled by the universal
#            channel-wins-reframe rule in the Reference Key (metaPromptConfig.py).
#
# "cautionary": token_b combinations that tend to produce poor output for structural
#               reasons the universal rule cannot predict. Only non-derivable entries
#               belong here. Format: "tends to X because Y; prefer Z instead".
#               No combination is blocked — these are guidance, not restrictions.
#
# Axis-level descriptions for empty-state UI panels (SPA + TUI2).
# Shown when no token is selected on an axis tab/section so users understand
# what the axis means, when to use it, and what skipping it means.
AXIS_KEY_TO_AXIS_DESC: Dict[str, str] = {
    "audience": "Who this is for — shapes vocabulary, depth, and framing.",
    "channel": "Delivery format — the artifact type or platform the response targets (diagram, script, slides, HTML, image/video, etc.).",
    "completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
    "directional": "Compass modifier shaping how the response is oriented, applied on top of task, scope, and method. Distinct from scope (which selects what dimension of the topic to focus on) and "
    "method (which selects the reasoning approach). Use to push the response angle: abstract↑ concrete↓ reflect← act→. jog is the null directional (no push). Compound tokens span the "
    "spectrum in their combined directions simultaneously — not alternating or sequential. fig (fog + dig) spans the full vertical range; bog (rog + ong) spans the full horizontal range. "
    "Three prefix families encode vertical orientation: fly prefix = fog (abstract); dip prefix = dig (concrete); fip prefix = fig (full vertical span, abstract + concrete). The second "
    "component (rog, ong, bog) adds horizontal orientation independently — so fly-rog = abstract + structural/reflective; dip-ong = concrete + acting; fip-bog = all four directions.",
    "form": "Output structure — how the response is organised (bullets, table, recipe, story, map, etc.).",
    "intent": "The purpose of the response — the motivation the speaker has.",
    "method": "Reasoning approach — how to think through the problem. Up to three can be combined.",
    "persona": "Communication style — who speaks, for whom, and in what tone.",
    "persona_preset": "A bundled preset combining voice, audience, and tone in one choice.",
    "scope": "Which dimension of the topic to focus on (entities, structure, meaning, actions, quality). Up to two.",
    "task": "What the response does — the primary action to perform.",
    "tone": "The emotional register — how the response sounds.",
    "voice": "Who is speaking — the perspective and expertise level.",
}

CROSS_AXIS_COMPOSITION: Dict[str, Dict[str, Dict[str, Any]]] = {
    "channel": {
        "shellscript": {
            "task": {
                "natural": ["make", "fix", "show", "pulse", "pull"],
                "cautionary": {
                    "sim": "tends to produce thin output — simulation is inherently narrative, not executable; consider remote or no channel instead",
                    "probe": "tends to miss analytical depth — a prose channel provides richer analysis; valid only for narrow system-probe scripts",
                },
            },
            "audience": {
                "natural": [
                    "to-programmer",
                    "to-principal-engineer",
                    "to-junior-engineer",
                    "to-platform-team",
                    "to-llm",
                ],
                "cautionary": {
                    "to-ceo": "tends to be inaccessible to a non-technical audience; consider plain or presenterm instead",
                    "to-managers": "tends to be inaccessible to a non-technical audience; consider plain or sync instead",
                    "to-stakeholders": "tends to be inaccessible to a non-technical audience; consider plain or presenterm instead",
                    "to-team": "accessible only to technical members of a mixed audience; consider plain instead",
                },
            },
        },
        "code": {
            "task": {
                "natural": ["make", "fix", "show", "pulse", "pull", "check"],
                "cautionary": {
                    "sim": "tends to produce thin placeholder code — simulation is narrative, not executable; consider remote or no channel instead",
                    "probe": "tends to miss analytical depth — a prose channel provides richer analysis; valid only for narrow introspection scripts",
                },
            },
            "audience": {
                "natural": [
                    "to-programmer",
                    "to-principal-engineer",
                    "to-junior-engineer",
                    "to-platform-team",
                    "to-llm",
                ],
                "cautionary": {
                    "to-ceo": "inaccessible to a non-technical audience; use plain or presenterm instead",
                    "to-managers": "inaccessible to a non-technical audience; use plain instead",
                    "to-stakeholders": "inaccessible to a non-technical audience; use plain or presenterm instead",
                    "to-team": "accessible only to technical members of a mixed audience",
                },
            },
        },
        "gherkin": {
            "task": {"natural": ["make", "check"]},
            "completeness": {
                "natural": ["full", "minimal"],
                "cautionary": {
                    "skim": "tends to produce incomplete scenarios — Gherkin steps need concrete action/assertion detail to be executable; use full or minimal "
                    "instead"
                },
            },
            "form": {
                "natural": ["story"],
                "cautionary": {
                    "case": "case-building requires prose structure incompatible with Gherkin Given/When/Then syntax; use plain or no channel",
                    "log": "log entries are prose-text; Gherkin cannot render date markers and bullet updates; use plain or no channel",
                    "questions": "open-ended questions cannot be expressed as Given/When/Then behavioral assertions; use plain or diagram channel",
                    "recipe": "recipe prose steps cannot be expressed as Gherkin behavioral assertions; use plain or no channel",
                },
            },
        },
        "adr": {
            "task": {
                "natural": ["plan", "probe", "make"],
                "cautionary": {
                    "sim": "tends to be incoherent — scenario playback is narrative; ADR is a decision artifact with no room for simulation output"
                },
            },
            "completeness": {
                "natural": ["full", "deep"],
                "cautionary": {
                    "skim": "tends to produce incomplete decisions — ADRs need full context and consequences to be actionable; use full or deep instead"
                },
            },
        },
        "codetour": {
            "task": {
                "natural": ["make", "fix", "show", "pull"],
                "cautionary": {
                    "sim": "tends to be incoherent — simulation is narrative with no code subject to navigate",
                    "sort": "tends to be incoherent — sorted items have no navigable code structure",
                },
            },
            "audience": {
                "natural": [
                    "to-programmer",
                    "to-principal-engineer",
                    "to-junior-engineer",
                    "to-platform-team",
                    "to-llm",
                ],
                "cautionary": {
                    "to-ceo": "codetour produces a VS Code JSON file — inaccessible to non-technical audiences; use plain or presenterm instead",
                    "to-managers": "codetour produces a VS Code JSON file — inaccessible to non-technical audiences; use plain instead",
                    "to-stakeholders": "codetour produces a VS Code JSON file — inaccessible to non-technical audiences; use plain or presenterm instead",
                    "to-team": "accessible only to technical members of a mixed audience; consider plain instead",
                },
            },
        },
        "sketch": {
            "task": {"natural": ["make", "plan", "show", "probe"]},
            "form": {
                "cautionary": {
                    "indirect": "sketch produces D2 diagram source; indirect form requires prose without diagram structure; use no channel or diagram instead",
                    "case": "case-building requires prose flow; D2 format has no slot for argument structure; use no channel or plain",
                    "walkthrough": "walkthrough is narrative prose; D2 format cannot accommodate step-by-step narrative; use codetour or plain instead",
                    "variants": "variants produce options-and-probabilities prose; D2 format has no slot for this; use plain or no channel",
                }
            },
        },
        "sync": {
            "task": {
                "natural": ["plan", "make", "show"],
                "cautionary": {
                    "sim": "tends to be unfocused — scenario playback is narrative and doesn't produce a structured session agenda; use plan or make instead",
                    "probe": "tends to miss the purpose — analytical probing doesn't translate into actionable session steps; use plan or show instead",
                },
            },
            "completeness": {
                "natural": ["full", "minimal", "gist"],
                "cautionary": {
                    "max": "tends to be unusable — session plans require practical brevity; max treats omissions as errors and produces overloaded agendas; use full "
                    "or minimal instead"
                },
            },
        },
        "html": {
            "task": {
                "natural": ["make", "fix", "show", "pulse", "pull", "check"],
                "cautionary": {
                    "sim": "tends to produce placeholder markup — simulation is narrative, not executable; consider remote or no channel instead",
                    "probe": "tends to miss analytical depth — valid only for narrow introspection scripts; a prose channel provides richer analysis",
                },
            }
        },
        "presenterm": {
            "task": {
                "natural": ["make", "show", "plan", "pull"],
                "cautionary": {
                    "fix": "tends to be too granular — code fixes don't translate into slide content; use make or show instead",
                    "probe": "tends to miss depth — analytical probing is hard to condense into slides; use show or plan instead",
                },
            },
            "completeness": {
                "natural": ["minimal", "gist"],
                "cautionary": {
                    "max": "tends to be undeliverable — slides require brevity; max produces overloaded decks; use minimal or gist instead",
                    "deep": "same constraint as max — slide format cannot accommodate deep analysis; use minimal or gist instead",
                },
            },
        },
    },
    "form": {
        "commit": {
            "completeness": {
                "natural": ["gist", "minimal"],
                "cautionary": {
                    "max": "tends to produce truncated or overloaded messages — commit format has no room for depth; use gist or minimal instead",
                    "deep": "same constraint as max — the format cannot accommodate deep analysis; use gist or minimal instead",
                },
            },
            "directional": {
                "cautionary": {
                    "fig": "commit message has no room for full vertical (abstract+concrete) range; use gist or minimal completeness",
                    "bog": "commit message has no room for full horizontal (reflective+acting) range; use gist or minimal completeness",
                    "fly-ong": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fly-rog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fly-bog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fip-ong": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fip-rog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fip-bog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "dip-ong": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "dip-rog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "dip-bog": "compound directional requires multi-dimensional depth commit format cannot accommodate; use gist or minimal",
                    "fog": "fog requires multi-dimensional breadth commit format cannot accommodate; use gist or minimal",
                },
                "cautionary_notes": {
                    "fig": "Conflict: commit format constrains range — format governs over directional.",
                    "bog": "Conflict: commit format constrains range — format governs over directional.",
                    "fly-ong": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fly-rog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fly-bog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fip-ong": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fip-rog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fip-bog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "dip-ong": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "dip-rog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "dip-bog": "Conflict: commit format cannot accommodate compound directional depth — format governs.",
                    "fog": "Conflict: commit format constrains breadth — format governs over directional.",
                },
            },
        },
        "case": {
            "channel": {
                "natural": ["plain", "slack", "jira", "sync"],
                "cautionary": {
                    "gherkin": "case builds layered argument; Gherkin requires Given/When/Then — format conflict; use plain or no channel",
                    "codetour": "case-building requires prose; CodeTour JSON has no room for argument prose; use plain or no channel",
                    "shellscript": "case-building requires prose; shell script cannot accommodate layered argument; use plain or no channel",
                    "html": "case-building requires prose flow; pure HTML output loses the argumentative structure; use plain or jira instead",
                },
            }
        },
        "contextualise": {
            "channel": {
                "natural": ["plain", "sync", "jira", "slack"],
                "cautionary": {
                    "gherkin": "contextualise adds explanatory prose; Gherkin syntax has no slot for contextualizing prose; use plain or no channel",
                    "shellscript": "contextualise renders explanatory prose alongside content; output-only shell format cannot accommodate that; use plain or no "
                    "channel",
                    "codetour": "contextualise adds explanatory context; CodeTour JSON has no prose-explanation slot; use plain or no channel",
                },
            }
        },
        "faq": {
            "channel": {
                "natural": ["plain", "slack", "jira"],
                "cautionary": {
                    "shellscript": "output format mismatch — Q&A prose cannot be rendered as executable shell code; use plain or no channel",
                    "code": "output format mismatch — Q&A prose cannot be rendered as code-only output; use plain or no channel",
                    "codetour": "output format mismatch — Q&A prose cannot be rendered as a CodeTour JSON; use plain or no channel",
                },
            }
        },
        "log": {
            "channel": {
                "natural": ["plain", "jira", "slack", "sync"],
                "cautionary": {
                    "svg": "log entries are prose-text — SVG cannot render date markers and bullet updates; use plain or no channel",
                    "codetour": "log entries are prose-text — CodeTour JSON has no slot for prose log structure; use plain or jira",
                    "gherkin": "log entries are prose-text — Gherkin syntax is incompatible with log format; use plain or no channel",
                    "shellscript": "log entries are prose-text — shell script cannot accommodate a research log; use plain or no channel",
                    "html": "log entries are prose-text — pure HTML output loses the temporal/bullet structure; use jira or plain instead",
                },
            }
        },
        "questions": {
            "channel": {
                "natural": ["plain", "slack", "diagram"],
                "cautionary": {
                    "gherkin": "open-ended questions cannot be expressed as Given/When/Then behavioral assertions; use plain or diagram channel"
                },
            }
        },
        "recipe": {
            "channel": {
                "natural": ["plain", "slack"],
                "cautionary": {
                    "codetour": "recipe steps cannot be expressed as navigable code stops; schema has no prose slot; use plain or no channel",
                    "code": "recipe cannot be rendered as code-only output; schema has no prose slot; use plain or no channel",
                    "shellscript": "recipe prose structure cannot be rendered as shell script; schema has no prose slot; use plain or no channel",
                    "svg": "recipe cannot be expressed as SVG markup; use plain or no channel",
                    "presenterm": "recipe prose structure cannot be expressed as presenterm slide sections; use plain or sync instead",
                },
            }
        },
        "socratic": {
            "channel": {
                "natural": ["plain", "slack"],
                "cautionary": {
                    "shellscript": "Socratic method produces reflective questions — cannot be rendered as executable shell code; use plain or no channel",
                    "codetour": "Socratic questions cannot be rendered as a VS Code CodeTour JSON; use plain or no channel",
                },
            }
        },
        "spike": {
            "channel": {
                "natural": ["plain", "slack", "jira"],
                "cautionary": {
                    "codetour": "spike is a prose research question-document; CodeTour JSON has no slot for open-ended research; use plain or no channel",
                    "shellscript": "spike produces prose — shell script cannot accommodate a research document; use plain or no channel",
                    "svg": "spike produces prose — SVG cannot accommodate a research question document; use plain or no channel",
                    "html": "spike produces prose questions — pure HTML has no semantic slot for open-ended research; use plain or jira",
                    "gherkin": "spike is open-ended exploration; Gherkin requires concrete Given/When/Then structure incompatible with spike's question framing; use "
                    "plain",
                },
            }
        },
    },
    "completeness": {
        "gist": {
            "directional": {
                "cautionary": {
                    "fig": "gist cannot express full vertical (abstract+concrete) range simultaneously; use full or deep instead",
                    "bog": "gist cannot express full horizontal (reflective+acting) range simultaneously; use full or deep instead",
                    "fly-ong": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "fly-rog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "fly-bog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "fip-ong": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "fip-rog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "fip-bog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "dip-ong": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "dip-rog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                    "dip-bog": "compound directional requires multi-dimensional depth gist cannot accommodate; use full or deep instead",
                },
                "cautionary_notes": {
                    "fig": "Conflict: gist brevity limits directional range — completeness governs.",
                    "bog": "Conflict: gist brevity limits directional range — completeness governs.",
                    "fly-ong": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "fly-rog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "fly-bog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "fip-ong": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "fip-rog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "fip-bog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "dip-ong": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "dip-rog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                    "dip-bog": "Conflict: gist brevity limits compound directional depth — completeness governs.",
                },
            }
        },
        "skim": {
            "directional": {
                "cautionary": {
                    "fig": "skim cannot sustain full vertical (abstract+concrete) multi-dimensional examination; use full or deep instead",
                    "bog": "skim cannot sustain full horizontal (reflective+acting) multi-dimensional examination; use full or deep instead",
                    "fly-ong": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fly-rog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fly-bog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fip-ong": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fip-rog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fip-bog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "dip-ong": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "dip-rog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "dip-bog": "compound directional requires sustained examination skim cannot provide; use full or deep instead",
                    "fog": "fog requires breadth of abstract examination skim cannot provide; use full or deep instead",
                },
                "cautionary_notes": {
                    "fig": "Conflict: skim brevity limits directional range — completeness governs.",
                    "bog": "Conflict: skim brevity limits directional range — completeness governs.",
                    "fly-ong": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fly-rog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fly-bog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fip-ong": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fip-rog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fip-bog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "dip-ong": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "dip-rog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "dip-bog": "Conflict: skim brevity limits compound directional depth — completeness governs.",
                    "fog": "Conflict: skim brevity limits abstract breadth — completeness governs.",
                },
            },
            "method": {
                "cautionary": {
                    "rigor": "skim constrains response volume; rigor demands disciplined depth — the light pass cannot accommodate rigorous reasoning; expect score-3 "
                    "output"
                }
            },
        },
    },
    "tone": {
        "formally": {
            "channel": {
                "cautionary": {
                    "slack": "tends to feel bureaucratic — slack assumes informal conversational register; use casually or omit tone instead",
                    "sync": "tends to feel over-formal — sync assumes spoken, conversational rhythm; use directly or omit tone instead",
                    "remote": "tends to feel stiff — remote channels assume natural conversational flow; use directly or omit tone instead",
                }
            }
        }
    },
}

# Default completeness token for format-constrained form tokens (ADR-0153).
# When a form token structurally limits response depth and the user has not
# specified a completeness token, the render pipeline uses this value instead
# of the global "full" default. Only define entries where the format's brevity
# constraint is structural — not a user preference.
FORM_DEFAULT_COMPLETENESS: Dict[str, str] = {"commit": "gist"}


@dataclass(frozen=True)
class AxisDoc:
    axis: str
    key: str
    description: str
    group: str | None = None
    flags: FrozenSet[str] = field(default_factory=frozenset)


def axis_key_to_value_map(axis: str) -> dict[str, str]:
    """Return the key->description map for a given axis."""
    return AXIS_KEY_TO_VALUE.get(axis, {})


def axis_key_to_label_map(axis: str) -> dict[str, str]:
    """Return the key->label map for a given axis (ADR-0109)."""
    return AXIS_KEY_TO_LABEL.get(axis, {})


def axis_key_to_kanji_map(
    axis: str,
) -> Union[Dict[str, str], Dict[str, Dict[str, str]]]:
    """Return the key->kanji map for a given axis (ADR-0143).

    For regular axes returns Dict[str, str] (token -> kanji).
    For 'persona' returns Dict[str, Dict[str, str]] (sub-axis -> token -> kanji).
    """
    return AXIS_KEY_TO_KANJI.get(axis, {})


def axis_key_to_category_map(axis: str) -> dict[str, str]:
    """Return the key->category map for a given axis (ADR-0144)."""
    return AXIS_KEY_TO_CATEGORY.get(axis, {})


def axis_category_order(axis: str) -> List[str]:
    """Return the canonical category display order for a given axis (ADR-0144)."""
    return AXIS_CATEGORY_ORDER.get(axis, [])


def axis_key_to_routing_concept_map(axis: str) -> dict[str, str]:
    """Return the key->routing_concept map for a given axis (ADR-0146).

    Returns per-token distilled routing concept phrases. Tokens sharing the same
    phrase form a multi-token routing bullet (e.g. thing+struct → 'Entities/boundaries').
    """
    return AXIS_KEY_TO_ROUTING_CONCEPT.get(axis, {})


def axis_key_to_axis_desc(axis: str) -> str:
    """Return the axis-level description string for empty-state UI panels."""
    return AXIS_KEY_TO_AXIS_DESC.get(axis, "")


def get_cross_axis_composition(axis: str, token: str) -> dict:
    """Return the cross-axis composition entry for a given axis+token pair (ADR-0147).

    Returns a dict keyed by partner axis, each value being
    {"natural": [...], "cautionary": {token: warning}}.
    Returns an empty dict if the axis or token has no entry.
    """
    return CROSS_AXIS_COMPOSITION.get(axis, {}).get(token, {})


def axis_docs_for(axis: str) -> list[AxisDoc]:
    """Return AxisDoc objects for a given axis."""
    mapping = axis_key_to_value_map(axis)
    return [
        AxisDoc(axis=axis, key=key, description=desc, group=None, flags=frozenset())
        for key, desc in mapping.items()
    ]


def axis_docs_index() -> dict[str, list[AxisDoc]]:
    """Return AxisDoc entries for all axes."""

    index: dict[str, list[AxisDoc]] = {}
    for axis, mapping in AXIS_KEY_TO_VALUE.items():
        index[axis] = [
            AxisDoc(axis=axis, key=key, description=desc, group=None, flags=frozenset())
            for key, desc in mapping.items()
        ]
    return index


USAGE_PATTERNS: list[dict] = [
    {
        "title": "Decision-Making",
        "command": 'bar build diff thing full spur variants --subject "..."',
        "example": 'bar build diff thing full spur variants --subject "Choose between Redis and Postgres for caching"',
        "desc": "Use when choosing between options or evaluating alternatives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["spur"],
            "scope": ["thing"],
            "task": ["diff"],
        },
    },
    {
        "title": "Architecture Documentation",
        "command": 'bar build make struct full analysis case --subject "..."',
        "example": 'bar build make struct full analysis case --subject "Document the microservices architecture"',
        "desc": "Use for creating ADRs or documenting architectural decisions",
        "tokens": {
            "completeness": ["full"],
            "form": ["case"],
            "method": ["analysis"],
            "scope": ["struct"],
            "task": ["make"],
        },
    },
    {
        "title": "Explanation/Understanding (Process)",
        "command": 'bar build show time full flow walkthrough --subject "..."',
        "example": 'bar build show time full flow walkthrough --subject "Explain the OAuth authentication flow"',
        "desc": "Use when explaining how something works over time or in sequence",
        "tokens": {
            "completeness": ["full"],
            "form": ["walkthrough"],
            "method": ["flow"],
            "scope": ["time"],
            "task": ["show"],
        },
    },
    {
        "title": "Explanation/Understanding (Concepts)",
        "command": 'bar build show mean full scaffold --subject "..."',
        "example": 'bar build show mean full scaffold --subject "What is eventual consistency?"',
        "desc": "Use when explaining what something means or building conceptual understanding",
        "tokens": {
            "completeness": ["full"],
            "form": ["scaffold"],
            "scope": ["mean"],
            "task": ["show"],
        },
    },
    {
        "title": "Structural Analysis",
        "command": 'bar build probe struct full mapping --subject "..."',
        "example": 'bar build probe struct full mapping --subject "Analyze the database schema relationships"',
        "desc": "Use for understanding relationships, boundaries, and structure",
        "tokens": {
            "completeness": ["full"],
            "method": ["mapping"],
            "scope": ["struct"],
            "task": ["probe"],
        },
    },
    {
        "title": "Problem Diagnosis",
        "command": 'bar build probe fail full diagnose checklist --subject "..."',
        "example": 'bar build probe fail full diagnose checklist --subject "Debug production memory leak"',
        "desc": "Use for troubleshooting and root cause analysis",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "method": ["diagnose"],
            "scope": ["fail"],
            "task": ["probe"],
        },
    },
    {
        "title": "Task Planning",
        "command": 'bar build plan act full converge actions --subject "..."',
        "example": 'bar build plan act full converge actions --subject "Plan the database migration steps"',
        "desc": "Use when breaking down work into actionable steps",
        "tokens": {
            "completeness": ["full"],
            "form": ["actions"],
            "method": ["converge"],
            "scope": ["act"],
            "task": ["plan"],
        },
    },
    {
        "title": "Exploratory Analysis",
        "command": 'bar build probe thing full sweep variants --subject "..."',
        "example": 'bar build probe thing full sweep variants --subject "What are different approaches to state management?"',
        "desc": "Use when surveying possibilities or generating alternatives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["sweep"],
            "scope": ["thing"],
            "task": ["probe"],
        },
    },
    {
        "title": "Comparison/Tradeoff Analysis",
        "command": 'bar build diff thing full table --subject "..."',
        "example": 'bar build diff thing full table --subject "Compare REST vs GraphQL vs gRPC for our API"',
        "desc": "Use for side-by-side comparison of alternatives with tradeoffs",
        "tokens": {
            "completeness": ["full"],
            "form": ["table"],
            "scope": ["thing"],
            "task": ["diff"],
        },
    },
    {
        "title": "Risk Analysis",
        "command": 'bar build probe fail full adversarial checklist --subject "..."',
        "example": 'bar build probe fail full adversarial checklist --subject "Assess the risk posture of migrating to Kubernetes"',
        "desc": "Use for open-ended risk analysis: 'how risky is this?' or 'assess failure posture'",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "method": ["adversarial"],
            "scope": ["fail"],
            "task": ["probe"],
        },
    },
    {
        "title": "Risk Extraction",
        "command": 'bar build pull fail full risks checklist --subject "..."',
        "example": 'bar build pull fail full risks checklist --subject "Deploy payment service on Friday"',
        "desc": "Use when extracting a bounded risk list or summary: 'what are the risks?'. Prefer pull over probe when a risk register or checklist is the deliverable, not an open-ended analysis.",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "method": ["risks"],
            "scope": ["fail"],
            "task": ["pull"],
        },
    },
    {
        "title": "Quality Evaluation",
        "command": 'bar build check good full analysis checklist --subject "..."',
        "example": 'bar build check good full analysis checklist --subject "Evaluate code review quality standards"',
        "desc": "Use when assessing quality, standards, or success criteria",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "method": ["analysis"],
            "scope": ["good"],
            "task": ["check"],
        },
    },
    {
        "title": "Progressive Refinement Workflow",
        "command": 'bar build probe thing gist sweep variants --subject "..." && bar build probe struct full mapping table --subject "..."',
        "example": 'bar build probe thing gist sweep variants --subject "API design approaches" && bar build probe struct full mapping table --subject "Selected REST API structure"',
        "desc": "Use for multi-step workflows: explore broadly, then analyze deeply",
        "tokens": {
            "completeness": ["gist"],
            "form": ["variants"],
            "method": ["sweep"],
            "scope": ["thing"],
            "task": ["probe"],
        },
    },
    {
        "title": "Conceptual Scaffolding",
        "command": 'bar build show mean full scaffold --subject "..."',
        "example": 'bar build show mean full scaffold --subject "Explain CQRS pattern for beginners"',
        "desc": "Use for building understanding from fundamentals to complex concepts",
        "tokens": {
            "completeness": ["full"],
            "form": ["scaffold"],
            "scope": ["mean"],
            "task": ["show"],
        },
    },
    {
        "title": "Failure Mode Analysis",
        "command": 'bar build probe fail full adversarial variants --subject "..."',
        "example": 'bar build probe fail full adversarial variants --subject "How could the payment system fail under load?"',
        "desc": "Use for systematic analysis of how systems can break",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["adversarial"],
            "scope": ["fail"],
            "task": ["probe"],
        },
    },
    {
        "title": "Success Criteria Definition",
        "command": 'bar build make good full analysis table --subject "..."',
        "example": 'bar build make good full analysis table --subject "Define success criteria for the dashboard redesign"',
        "desc": "Use when establishing measurable quality or success standards",
        "tokens": {
            "completeness": ["full"],
            "form": ["table"],
            "method": ["analysis"],
            "scope": ["good"],
            "task": ["make"],
        },
    },
    {
        "title": "Perspective Analysis",
        "command": 'bar build probe view full sweep variants --subject "..."',
        "example": 'bar build probe view full sweep variants --subject "How do different stakeholders view the monolith migration?"',
        "desc": "Use for understanding multiple viewpoints or stakeholder perspectives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["sweep"],
            "scope": ["view"],
            "task": ["probe"],
        },
    },
    {
        "title": "Impact Assessment",
        "command": 'bar build probe struct full effects table --subject "..."',
        "example": 'bar build probe struct full effects table --subject "Assess downstream impacts of changing the auth service"',
        "desc": "Use for analyzing ripple effects and dependencies",
        "tokens": {
            "completeness": ["full"],
            "form": ["table"],
            "method": ["effects"],
            "scope": ["struct"],
            "task": ["probe"],
        },
    },
    {
        "title": "Constraint Mapping",
        "command": 'bar build probe thing full dimension table --subject "..."',
        "example": 'bar build probe thing full dimension table --subject "Map technical and business constraints for the mobile app"',
        "desc": "Use for identifying and documenting limitations and requirements",
        "tokens": {
            "completeness": ["full"],
            "form": ["table"],
            "method": ["dimension"],
            "scope": ["thing"],
            "task": ["probe"],
        },
    },
    {
        "title": "Evidence Building",
        "command": 'bar build make good full cite case --subject "..."',
        "example": 'bar build make good full cite case --subject "Build the case for adopting TypeScript"',
        "desc": "Use when making a persuasive argument with supporting evidence",
        "tokens": {
            "completeness": ["full"],
            "form": ["case"],
            "method": ["cite"],
            "scope": ["good"],
            "task": ["make"],
        },
    },
    {
        "title": "Option Generation with Reasoning",
        "command": 'bar build probe thing full spur variants --subject "..."',
        "example": 'bar build probe thing full spur variants --subject "Generate database sharding approaches with pros/cons"',
        "desc": "Use for generating alternatives with detailed reasoning for each",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["spur"],
            "scope": ["thing"],
            "task": ["probe"],
        },
    },
    {
        "title": "Sequential Process Documentation",
        "command": 'bar build make time full flow recipe --subject "..."',
        "example": 'bar build make time full flow recipe --subject "Document the CI/CD pipeline stages"',
        "desc": "Use for documenting step-by-step processes or workflows",
        "tokens": {
            "completeness": ["full"],
            "form": ["recipe"],
            "method": ["flow"],
            "scope": ["time"],
            "task": ["make"],
        },
    },
    {
        "title": "Scenario Simulation",
        "command": 'bar build sim time full walkthrough --subject "..."',
        "example": 'bar build sim time full walkthrough --subject "Simulate what happens during a database failover"',
        "desc": "Use for playing out hypothetical or contingency scenarios",
        "tokens": {
            "completeness": ["full"],
            "form": ["walkthrough"],
            "scope": ["time"],
            "task": ["sim"],
        },
    },
    {
        "title": "Dependency Analysis",
        "command": 'bar build probe struct full depends mapping --subject "..."',
        "example": 'bar build probe struct full depends mapping --subject "Map service dependencies in the microservices architecture"',
        "desc": "Use for understanding and visualizing dependencies and relationships",
        "tokens": {
            "completeness": ["full"],
            "form": ["mapping"],
            "method": ["depends"],
            "scope": ["struct"],
            "task": ["probe"],
        },
    },
    {
        "title": "Summarisation / Extraction",
        "command": 'bar build pull gist struct --subject "..."',
        "example": 'bar build pull gist struct --subject "[long RFC or design document]"',
        "desc": "Use when compressing a long source document into a shorter summary. Prefer pull over show when a SUBJECT document is being compressed: pull extracts a subset, show explains a concept. Heuristic: long SUBJECT to compress → pull; concept to explain without a source → show.",
        "tokens": {"completeness": ["gist"], "scope": ["struct"], "task": ["pull"]},
    },
    {
        "title": "Test Coverage Gap Analysis",
        "command": 'bar build check fail full checklist --subject "..."',
        "example": 'bar build check fail full checklist --subject "Feature: user registration flow"',
        "desc": "Use when identifying missing tests or coverage gaps in existing code. Heuristic: 'what tests are missing?' → check; 'write a test plan' → make.",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "scope": ["fail"],
            "task": ["check"],
        },
    },
    {
        "title": "Test Plan Creation",
        "command": 'bar build make act fail full checklist --subject "..."',
        "example": 'bar build make act fail full checklist --subject "Payment integration feature"',
        "desc": "Use when creating a new test plan or test cases from scratch. Produces a test plan artifact rather than evaluating existing coverage.",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "scope": ["act", "fail"],
            "task": ["make"],
        },
    },
    {
        "title": "Pre-mortem / Inversion Exercise",
        "command": 'bar build probe fail full inversion variants --subject "..."',
        "example": 'bar build probe fail full inversion variants --subject "Our Q4 launch plan"',
        "desc": "Use when assuming failure and working backward to identify causes. Frames the exercise as: 'assume this has failed — what went wrong?' Pairs naturally with planning and architecture review tasks.",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["inversion"],
            "scope": ["fail"],
            "task": ["probe"],
        },
    },
    {
        "title": "Comprehensive Assessment (Multi-Scope)",
        "command": 'bar build check <scope> full <method> --subject "..."',
        "example": 'bar build check good full analysis --subject "Assess codebase quality"',
        "desc": "Use for multi-faceted assessments that span quality (good), fragility (fail), and structure (struct). When the task requires multiple analytical lenses, prioritize by primary concern or analyze sequentially: quality-first (good), risk-first (fail), or architecture-first (struct).",
        "tokens": {"completeness": ["full"], "task": ["check"]},
    },
    {
        "title": "Evaluation with Falsification",
        "command": 'bar build check <scope> full verify risks --subject "..."',
        "example": 'bar build check thing full verify risks --subject "Evaluate the proposed caching strategy"',
        "desc": "Use when evaluating claims by actively searching for ways they could be wrong. Combines verify (falsification pressure) with risks (systematic problem identification). Best for: reviewing designs, validating assumptions, stress-testing proposals.",
        "tokens": {
            "completeness": ["full"],
            "method": ["verify", "risks"],
            "scope": ["thing"],
            "task": ["check"],
        },
    },
    {
        "title": "Plain Prose Output",
        "command": 'bar build show <scope> full plain --subject "..."',
        "example": 'bar build show mean full plain --subject "Explain the authorization model"',
        "desc": "Use when the response must be plain prose — no lists, bullets, or tables. The plain channel explicitly suppresses structural decoration. Heuristic: 'no bullets', 'no formatting', 'plain prose', 'flowing paragraphs' → add plain channel to any task.",
        "tokens": {"channel": ["plain"], "completeness": ["full"], "task": ["show"]},
    },
    {
        "title": "Synchronous Session Plan",
        "command": 'bar build plan act full sync --subject "..."',
        "example": 'bar build plan act full sync --subject "Design sprint kickoff — 3h with context, problem framing, and ideation"',
        "desc": "Use when the output should be a synchronous session plan with agenda, timing slots, and facilitation cues for real-time use. Heuristic: 'session plan', 'live workshop', 'meeting agenda with timing', 'facilitation script for live session' → sync channel. Combine with facilitate form when facilitator role is explicit.",
        "tokens": {
            "channel": ["sync"],
            "completeness": ["full"],
            "scope": ["act"],
            "task": ["plan"],
        },
    },
]


def get_usage_patterns() -> list[dict]:
    """Return the USAGE_PATTERNS list (ADR-0134 SSOT)."""
    return USAGE_PATTERNS


# ADR-0155: Structured metadata for axis tokens (same shape as task token metadata).
class AxisTokenDistinction(TypedDict):
    token: str
    note: str


class AxisTokenMetadata(TypedDict, total=False):
    definition: str
    heuristics: list[str]
    distinctions: list[AxisTokenDistinction]


# Nested dict keyed by axis then token. Populated axis-by-axis in T-3–T-8.
AXIS_TOKEN_METADATA: dict[str, dict[str, AxisTokenMetadata]] = {
    "channel": {
        "adr": {
            "distinctions": [],
            "heuristics": [
                "write an ADR",
                "architecture decision record",
                "ADR format",
                "decision record",
                "record this decision formally for version control",
            ],
        },
        "code": {
            "distinctions": [],
            "heuristics": [
                "just the code",
                "code only",
                "no explanation, just the implementation",
                "output code only",
                "code without prose",
                "just the markup",
                "implementation without explanation",
            ],
        },
        "codetour": {
            "distinctions": [],
            "heuristics": [
                "codetour",
                "VS Code tour",
                "code tour file",
                "interactive code walkthrough",
                "create a codetour",
            ],
        },
        "diagram": {
            "distinctions": [
                {
                    "note": "diagram = Mermaid format; sketch = D2 diagram format",
                    "token": "sketch",
                }
            ],
            "heuristics": [
                "diagram",
                "Mermaid diagram",
                "draw a diagram",
                "flowchart",
                "sequence diagram",
                "draw this out",
                "architecture diagram in Mermaid",
                "as a diagram",
            ],
        },
        "draw": {
            "distinctions": [
                {
                    "note": "diagram (channel) = Mermaid code, machine-parseable; draw (channel) = spatial ASCII prose, human-readable",
                    "token": "diagram",
                },
                {
                    "note": "sketch (channel) = D2 diagram source; draw (channel) = freehand ASCII spatial layout without a schema",
                    "token": "sketch",
                },
                {
                    "note": "visual (method) = frame ideas spatially regardless of output format; draw (channel) = deliver that framing as ASCII spatial layout",
                    "token": "visual",
                },
            ],
            "heuristics": [
                "ASCII diagram",
                "boxes and arrows",
                "spatial layout",
                "ASCII layout",
                "hand-drawn style",
                "rough diagram",
                "text-based visual",
                "ASCII art",
                "prose diagram",
            ],
        },
        "gherkin": {
            "distinctions": [],
            "heuristics": [
                "Gherkin format",
                "Given/When/Then",
                "BDD scenarios",
                "acceptance tests in Gherkin",
                "feature file",
                "BDD test cases",
            ],
        },
        "html": {
            "distinctions": [],
            "heuristics": [
                "HTML output",
                "semantic HTML",
                "as HTML",
                "output as a webpage",
                "HTML page",
                "HTML only",
            ],
        },
        "image": {
            "distinctions": [
                {
                    "note": "image = static image generation; video = video generation",
                    "token": "video",
                }
            ],
            "heuristics": [
                "generate an image",
                "create an image",
                "make an image of",
                "I want an image of",
                "image of",
                "DALL-E",
                "Midjourney",
                "Stable Diffusion",
            ],
        },
        "jira": {
            "distinctions": [],
            "heuristics": [
                "Jira format",
                "Jira markup",
                "format for Jira",
                "Jira ticket format",
                "for a Jira comment",
                "use Jira markup",
            ],
        },
        "notebook": {
            "distinctions": [],
            "heuristics": [
                "Jupyter notebook",
                "notebook format",
                "as a notebook",
                ".ipynb",
                "runnable notebook",
                "notebook with code cells",
                "data exploration notebook",
                "interactive notebook",
            ],
        },
        "plain": {
            "distinctions": [],
            "heuristics": [
                "no bullets",
                "no formatting",
                "plain prose",
                "continuous prose",
                "flowing paragraphs",
                "paragraph form",
            ],
        },
        "presenterm": {
            "distinctions": [
                {
                    "note": "presenterm = actual slide deck artifact; sync = session plan with timing cues",
                    "token": "sync",
                }
            ],
            "heuristics": [
                "presenterm deck",
                "slide deck",
                "presentation slides",
                "create slides",
                "slide format",
                "multi-slide deck",
                "presentation",
            ],
        },
        "remote": {
            "distinctions": [],
            "heuristics": [
                "remote delivery",
                "distributed session",
                "video call context",
                "screen sharing",
                "remote-friendly",
            ],
        },
        "shellscript": {
            "distinctions": [],
            "heuristics": [
                "shell script",
                "bash script",
                "write a script",
                "automate this with a shell script",
                "script format",
                "shell code only",
            ],
        },
        "sketch": {
            "distinctions": [
                {
                    "note": "sketch = D2 diagram format; diagram = Mermaid format",
                    "token": "diagram",
                }
            ],
            "heuristics": ["D2 diagram", "D2 format", "sketch diagram", "d2 source"],
        },
        "slack": {
            "distinctions": [],
            "heuristics": [
                "Slack format",
                "format for Slack",
                "post this to Slack",
                "Slack message",
                "Slack-friendly format",
                "for a Slack post",
            ],
        },
        "store": {
            "distinctions": [
                {
                    "note": "snap (form) = structure content as a save-state artifact; store (channel) = deliver output to durable storage — they compose naturally",
                    "token": "snap",
                }
            ],
            "heuristics": [
                "save this to disk",
                "write this to a file",
                "persist this",
                "store this",
                "save to memory",
                "keep saving as we go",
                "I want to be able to find this later",
                "make it findable later",
                "save it somewhere",
                "also write it out",
            ],
        },
        "svg": {
            "distinctions": [],
            "heuristics": [
                "SVG format",
                "as SVG",
                "SVG output",
                "output as SVG",
                "SVG markup only",
                "create an SVG",
            ],
        },
        "sync": {
            "distinctions": [
                {
                    "note": "sync = session plan with timing cues; presenterm = actual slide deck artifact",
                    "token": "presenterm",
                }
            ],
            "heuristics": [
                "session plan",
                "live workshop agenda",
                "meeting agenda with timing cues",
                "synchronous workshop plan",
            ],
        },
        "video": {
            "distinctions": [
                {
                    "note": "video = video generation; image = static image generation",
                    "token": "image",
                }
            ],
            "heuristics": [
                "generate a video",
                "create a video",
                "make a video of",
                "I want a video of",
                "video of",
                "Sora",
                "Runway",
                "Pika",
                "Kling",
            ],
        },
    },
    "completeness": {
        "deep": {
            "distinctions": [
                {
                    "note": "deep = depth within a focused scope; max = exhaustive across all relevant coverage",
                    "token": "max",
                },
                {
                    "note": "deep = substantial depth within scope; full = breadth across major aspects",
                    "token": "full",
                },
            ],
            "heuristics": [
                "go deep",
                "really dig in",
                "thorough analysis",
                "don't skip the nuances",
                "unpack this fully",
                "I want the details",
                "deep dive",
                "depth over breadth",
            ],
        },
        "full": {
            "distinctions": [
                {
                    "note": "full = thorough normal coverage; max = treat omissions as errors",
                    "token": "max",
                },
                {
                    "note": "full = breadth across major aspects; deep = substantial depth within scope",
                    "token": "deep",
                },
            ],
            "heuristics": [
                "complete",
                "comprehensive",
                "cover everything important",
                "thorough",
                "full picture",
                "don't leave anything major out",
                "complete treatment",
            ],
        },
        "gist": {
            "distinctions": [
                {
                    "note": "gist = brief but complete; skim = light pass, may miss non-obvious issues",
                    "token": "skim",
                }
            ],
            "heuristics": [
                "quick summary",
                "overview",
                "brief",
                "tldr",
                "just the main points",
                "high-level",
                "standup update",
                "just the gist",
            ],
        },
        "grow": {
            "distinctions": [
                {
                    "note": "grow = start minimal and expand on demand; minimal = keep output minimal throughout",
                    "token": "minimal",
                },
                {
                    "note": "grow = dynamic — justifies each expansion; max = static — exhaust all coverage from the start",
                    "token": "max",
                },
            ],
            "heuristics": [
                "expand only when needed",
                "grow as needed",
                "start simple and elaborate",
                "disciplined expansion",
                "justify each elaboration",
                "minimal unless warranted",
                "add depth only where analysis demands",
            ],
        },
        "max": {
            "distinctions": [
                {
                    "note": "max = every relevant item, omissions are errors; full = thorough normal coverage",
                    "token": "full",
                },
                {
                    "note": "max = exhaustive across all relevant coverage; deep = depth within a focused scope",
                    "token": "deep",
                },
            ],
            "heuristics": [
                "be exhaustive",
                "miss nothing",
                "everything relevant",
                "leave nothing out",
                "as complete as possible",
                "comprehensive and exhaustive",
                "cover every case",
                "I need everything",
            ],
        },
        "minimal": {
            "distinctions": [
                {
                    "note": "minimal = smallest valid answer to the request; narrow = restrict to a small topic slice",
                    "token": "narrow",
                }
            ],
            "heuristics": [
                "minimal change",
                "just what's needed",
                "no more than necessary",
                "smallest fix",
                "keep it small",
                "just the minimum",
                "don't add anything extra",
                "bare minimum",
                "only what I asked for",
            ],
        },
        "narrow": {
            "distinctions": [
                {
                    "note": "narrow = very small slice of topic; minimal = smallest answer",
                    "token": "minimal",
                }
            ],
            "heuristics": [
                "specifically",
                "only about",
                "just this part",
                "restricted to",
                "nothing beyond",
                "only X",
            ],
        },
        "skim": {
            "distinctions": [
                {
                    "note": "skim = light pass that may miss non-obvious issues; gist = brief but complete",
                    "token": "gist",
                }
            ],
            "heuristics": [
                "light review",
                "quick pass",
                "spot check",
                "just flag obvious problems",
                "surface-level look",
                "sanity check",
                "quick skim",
            ],
        },
        "triage": {
            "distinctions": [
                {
                    "note": "triage = allocate depth by consequence × uncertainty stakes; grow = expand only where analysis explicitly demands it",
                    "token": "grow",
                },
                {
                    "note": "triage = stakes-proportionate, leaving low-stakes areas at minimal depth; full = uniform thorough coverage across all aspects",
                    "token": "full",
                },
            ],
            "heuristics": [
                "focus on the high-risk areas",
                "triage by impact and uncertainty",
                "risk-proportionate depth",
                "where are the stakes highest",
                "most dangerous parts first",
                "consequence-weighted review",
                "allocate attention by risk",
                "what deserves the most scrutiny",
                "protect the high-stakes areas",
            ],
        },
        "zoom": {
            "distinctions": [
                {
                    "note": "zoom = resolution adapts to span magnitude; full = uniform thorough coverage at consistent grain",
                    "token": "full",
                },
                {
                    "note": "zoom = grain scales with span in both directions; max = fine grain everywhere regardless of span",
                    "token": "max",
                },
                {
                    "note": "zoom = interval size scales with span; grow = depth expands only where analysis explicitly demands it",
                    "token": "grow",
                },
            ],
            "heuristics": [
                "appropriate granularity",
                "at the right level of detail for the range",
                "bucket by order of magnitude",
                "proportional resolution",
                "bucket by magnitude",
                "coarser as it gets larger",
                "finer as it gets smaller",
                "fine grain for small spans",
                "group at natural intervals",
                "scale the detail to the span",
                "log scale grouping",
                "span the full range",
                "from smallest to largest",
                "cover every level of scale",
            ],
        },
    },
    "directional": {
        "bog": {
            "distinctions": [
                {
                    "note": "bog = full horizontal span (reflective + acting); rog = reflective pole only",
                    "token": "rog",
                },
                {
                    "note": "bog = full horizontal span (reflective + acting); ong = acting pole only",
                    "token": "ong",
                },
            ],
            "heuristics": [
                "examine what it means AND tell me what to do about it",
                "both the structural examination and the actions",
                "understand it structurally while also acting on that understanding",
                "analysis and actions both",
            ],
        },
        "dig": {
            "distinctions": [
                {
                    "note": "dig = stay concrete and grounded; fog = orient toward the abstract principle",
                    "token": "fog",
                }
            ],
            "heuristics": [
                "be concrete",
                "give me specific examples",
                "show me an actual case",
                "not abstract — real examples",
                "ground this in reality",
                "practical examples only",
                "make it tangible",
                "I need specifics not theory",
            ],
        },
        "dip bog": {
            "distinctions": [
                {
                    "note": "dip bog = concrete + full horizontal orientation together; dig = concrete pole only",
                    "token": "dig",
                },
                {
                    "note": "dip bog = concrete anchoring with full horizontal orientation; bog = horizontal span without concrete anchoring",
                    "token": "bog",
                },
            ],
            "heuristics": [
                "concrete grounding with structural and action orientation",
                "ground it in examples and orient toward both structure and action",
                "real examples shaping both what it reveals and what to do",
                "grounded in specifics, oriented toward structure and action",
            ],
        },
        "dip ong": {
            "distinctions": [
                {
                    "note": "dip ong = concrete + acting orientation together; dig = concrete pole only",
                    "token": "dig",
                },
                {
                    "note": "dip ong = concrete anchoring with acting orientation; ong = acting pole without concrete anchoring",
                    "token": "ong",
                },
            ],
            "heuristics": [
                "concrete examples with action orientation",
                "ground it in specifics and orient toward what to do",
                "practical examples with actions",
                "real cases with actionable direction",
            ],
        },
        "dip rog": {
            "distinctions": [
                {
                    "note": "dip rog = concrete + structural orientation together; dig = concrete pole only",
                    "token": "dig",
                },
                {
                    "note": "dip rog = concrete anchoring with structural orientation; rog = structural pole without concrete anchoring",
                    "token": "rog",
                },
            ],
            "heuristics": [
                "concrete examples with structural orientation",
                "ground it in specifics and orient toward its structure",
                "specifics and what their structure reveals",
                "specific example oriented toward structural patterns",
            ],
        },
        "fig": {
            "distinctions": [
                {
                    "note": "fig = full vertical span (abstract + concrete); fog = abstract pole only",
                    "token": "fog",
                },
                {
                    "note": "fig = full vertical span (abstract + concrete); dig = concrete pole only",
                    "token": "dig",
                },
            ],
            "heuristics": [
                "address both the principle and the specifics",
                "give me the concept and the grounded examples",
                "both the theory and the concrete reality",
                "be abstract and concrete",
                "cover the full range from general to specific",
            ],
        },
        "fip bog": {
            "distinctions": [
                {
                    "note": "fip bog = full vertical + full horizontal orientation (all 4 directions); fig = vertical span only",
                    "token": "fig",
                },
                {
                    "note": "fip bog = vertical span combined with full horizontal orientation; bog = horizontal span without vertical span",
                    "token": "bog",
                },
            ],
            "heuristics": [
                "full vertical and horizontal orientation",
                "abstract and concrete, structural and acting",
                "all four compass directions at once",
                "span abstract to concrete while orienting toward structure and action",
            ],
        },
        "fip ong": {
            "distinctions": [
                {
                    "note": "fip ong = vertical span + acting orientation together; fig = vertical span only",
                    "token": "fig",
                },
                {
                    "note": "fip ong = vertical span with acting orientation; ong = acting pole without vertical span",
                    "token": "ong",
                },
            ],
            "heuristics": [
                "abstract and concrete with action orientation",
                "span abstract to concrete and orient toward action",
                "both levels of abstraction, shaped toward what to do",
                "span abstract to concrete, orienting toward actions",
            ],
        },
        "fip rog": {
            "distinctions": [
                {
                    "note": "fip rog = vertical span + structural orientation together; fig = vertical span only",
                    "token": "fig",
                },
                {
                    "note": "fip rog = vertical span with structural orientation; rog = structural pole without vertical span",
                    "token": "rog",
                },
            ],
            "heuristics": [
                "abstract and concrete with structural orientation",
                "span abstract to concrete and orient toward structure",
                "both levels of abstraction, shaped by what the structure reveals",
                "span abstract to concrete, orienting toward structural meaning",
            ],
        },
        "fly bog": {
            "distinctions": [
                {
                    "note": "fly bog = abstract + full horizontal orientation together; fog = abstract pole only",
                    "token": "fog",
                },
                {
                    "note": "fly bog = abstract anchoring with full horizontal orientation; bog = horizontal span without abstract anchoring",
                    "token": "bog",
                },
            ],
            "heuristics": [
                "abstract grounding with structural and action orientation",
                "big picture anchoring, orienting toward both structure and action",
                "principles shaping both what they reveal and what to do",
                "abstract anchoring, oriented toward structure and action",
            ],
        },
        "fly ong": {
            "distinctions": [
                {
                    "note": "fly ong = abstract + acting orientation together; fog = abstract pole only",
                    "token": "fog",
                },
                {
                    "note": "fly ong = abstract anchoring with acting orientation; ong = acting pole without abstract anchoring",
                    "token": "ong",
                },
            ],
            "heuristics": [
                "abstract grounding with action orientation",
                "big picture anchoring, oriented toward action",
                "principles shaping what to do",
                "big picture anchoring with action orientation",
            ],
        },
        "fly rog": {
            "distinctions": [
                {
                    "note": "fly rog = abstract + structural orientation together; fog = abstract pole only",
                    "token": "fog",
                },
                {
                    "note": "fly rog = abstract anchoring with structural orientation; rog = structural pole without abstract anchoring",
                    "token": "rog",
                },
            ],
            "heuristics": [
                "abstract grounding with structural orientation",
                "big picture anchoring, oriented toward structure",
                "principles shaping what the structure reveals",
                "big picture anchoring with structural orientation",
            ],
        },
        "fog": {
            "distinctions": [
                {
                    "note": "fog = orient toward the abstract and general; dig = stay concrete and grounded",
                    "token": "dig",
                },
                {
                    "note": "fog = push an existing response toward the abstract/general; scope:mean = focus the entire response on conceptual framing before evaluation or "
                    "action",
                    "token": "mean",
                },
            ],
            "heuristics": [
                "step back and tell me the general principle",
                "abstract away from the details",
                "what does this reveal more broadly",
                "what's the big picture here",
                "what underlying pattern do these cases share",
                "zoom out",
                "what's the broader implication",
            ],
        },
        "jog": {
            "distinctions": [],
            "heuristics": [
                "no directional preference",
                "null direction",
                "no compass push",
            ],
        },
        "ong": {
            "distinctions": [
                {
                    "note": "ong = acting/extending pole (right); rog = reflective/structural pole (left)",
                    "token": "rog",
                },
                {
                    "note": "ong = directional push toward action and extension; form:actions = structure the output as a list of concrete tasks without directional "
                    "orientation",
                    "token": "actions",
                },
            ],
            "heuristics": [
                "what actions should I take and what comes next after each",
                "give me the actions with follow-on steps",
                "what do I do and what's the next step after that",
                "next steps and their extensions",
            ],
        },
        "rog": {
            "distinctions": [
                {
                    "note": "rog = reflective/structural pole (left); ong = acting/extending pole (right)",
                    "token": "ong",
                },
                {
                    "note": "rog = push toward the structural and reflective dimension; fog = push toward the abstract",
                    "token": "fog",
                },
                {
                    "note": "rog = directional push toward structural examination and what it reveals; scope:struct = focus the topic on internal arrangement and dependencies",
                    "token": "struct",
                },
                {
                    "note": "rog = directional orientation toward structure and reflection; method:analysis = decompose into components as a reasoning procedure",
                    "token": "analysis",
                },
            ],
            "heuristics": [
                "describe the structure and what it reveals",
                "how is it organised and what does that reveal",
                "walk me through the structure and reflect on the implications",
                "what does the organisation tell us",
            ],
        },
    },
    "form": {
        "actions": {
            "distinctions": [
                {
                    "note": "checklist = imperative checkbox items designed to be ticked off; actions = broader action-structured output including tasks, steps, and next moves",
                    "token": "checklist",
                },
                {
                    "note": "walkthrough = guided sequential narration; actions = direct action list without guided narration",
                    "token": "walkthrough",
                },
            ],
            "heuristics": [
                "give me actions",
                "what do I actually do",
                "concrete steps",
                "action items",
                "what are my next actions",
                "just the actions",
                "tasks to do",
                "list of actions",
            ],
        },
        "activities": {
            "distinctions": [
                {
                    "note": "facilitate = overall facilitation plan with session goals and participation mechanics; activities = segment-by-segment content of what to do and "
                    "when",
                    "token": "facilitate",
                }
            ],
            "heuristics": [
                "what activities should we do",
                "activities for each block",
                "session activities",
                "design sprint activities",
                "what happens in each segment",
                "activities list for the workshop",
            ],
        },
        "bug": {
            "distinctions": [
                {
                    "note": "log = work log entry for archival and reference; bug = structured defect report with reproduction steps and expected/actual behavior",
                    "token": "log",
                }
            ],
            "heuristics": [
                "file a bug report",
                "write this up as a bug",
                "bug report format",
                "steps to reproduce",
                "expected vs actual behavior",
                "create a bug ticket",
            ],
        },
        "bullets": {
            "distinctions": [
                {
                    "note": "checklist = imperative action items designed to be ticked off; bullets = general bullet-point organization, not necessarily imperative",
                    "token": "checklist",
                }
            ],
            "heuristics": [
                "bullet points",
                "use bullets",
                "bulleted list",
                "as bullet points",
                "short bullets",
                "list format with bullets",
                "no paragraphs, just bullets",
            ],
        },
        "cards": {
            "distinctions": [
                {
                    "note": "bullets = brief bullet items; cards = richer discrete units each with a heading and short body",
                    "token": "bullets",
                }
            ],
            "heuristics": [
                "cards",
                "card layout",
                "each item as a card",
                "discrete cards",
                "card format",
                "organize as cards",
                "section cards with headings",
            ],
        },
        "case": {
            "distinctions": [
                {
                    "note": "indirect = softer narrative reasoning that converges on a point; case = structured argument with explicit evidence, alternatives, and objection handling "
                    "before the recommendation",
                    "token": "indirect",
                }
            ],
            "heuristics": [
                "build the case",
                "lay out the argument before the recommendation",
                "walk through the evidence first",
                "structured argument",
                "present the case",
                "evidence then conclusion",
                "case for X",
            ],
        },
        "checklist": {
            "distinctions": [
                {
                    "note": "actions = general action-structured output; checklist = specifically checkbox-style imperative items designed to be ticked off",
                    "token": "actions",
                }
            ],
            "heuristics": [
                "checklist",
                "give me a checklist",
                "checkbox list",
                "actionable checklist",
                "checkboxes",
                "items to check off",
                "pre-flight checklist",
            ],
        },
        "cocreate": {
            "distinctions": [
                {
                    "note": "variants = present a choice of distinct designs; cocreate = iterative process with decision points and alignment checks",
                    "token": "variants",
                }
            ],
            "heuristics": [
                "work through incrementally",
                "with decision points",
                "iterative design",
            ],
        },
        "commit": {
            "distinctions": [
                {
                    "note": "log = dated work log entry with bullet updates; commit = short type/scope header format for version control",
                    "token": "log",
                }
            ],
            "heuristics": [
                "write a commit message",
                "commit message for this",
                "conventional commit",
                "git commit message",
                "commit message",
                "type: scope format",
            ],
        },
        "contextualise": {
            "distinctions": [
                {
                    "note": "merge = combine multiple sources into one coherent whole; contextualise = package existing content with full context for another LLM to act on "
                    "it",
                    "token": "merge",
                },
                {
                    "note": "pull extracts a subset from source material; contextualise packages that extracted content with all context a downstream model needs — they "
                    "compose naturally",
                    "token": "pull",
                },
            ],
            "heuristics": [
                "pass this to another model",
                "use this as context for",
                "prepare for downstream processing",
                "make this self-contained for an LLM",
                "include all necessary context",
                "so I can feed this to",
            ],
        },
        "coupling": {
            "distinctions": [
                {
                    "note": "coupling (form) = output structured as a coupling map; snag/mesh (method) = analytical lens for finding or resolving coupling",
                    "token": "snag",
                }
            ],
            "heuristics": [
                "coupling map",
                "map out the coupling",
                "show the seams between",
                "show what crosses the boundary",
                "coupling diagram",
                "what is joined at the interface",
                "where do these components couple",
            ],
        },
        "direct": {
            "distinctions": [
                {
                    "note": "indirect = background first, conclusion last; direct = main point first, supporting detail after",
                    "token": "indirect",
                }
            ],
            "heuristics": [
                "lead with the answer",
                "bottom line up front",
                "BLUF",
                "give me the conclusion first",
                "direct response",
                "state the recommendation first",
                "don't bury the lede",
            ],
        },
        "facilitate": {
            "distinctions": [
                {
                    "note": "walkthrough = linear narrated steps through a process; facilitate = session structure with participation cues and facilitation agenda",
                    "token": "walkthrough",
                },
                {
                    "note": "activities = segment-level content of what to do; facilitate = overall facilitation structure with goals and participation mechanics",
                    "token": "activities",
                },
            ],
            "heuristics": [
                "facilitate a X",
                "run a retrospective",
                "workshop planning",
            ],
        },
        "faq": {
            "distinctions": [
                {
                    "note": "questions = response IS a list of questions to investigate (no answers); faq = questions paired with their answers as a reference artifact",
                    "token": "questions",
                }
            ],
            "heuristics": [
                "FAQ format",
                "as a FAQ",
                "Q and A format",
                "frequently asked questions",
                "questions and answers",
                "write as Q&A",
                "question headings with answers below",
            ],
        },
        "formats": {
            "distinctions": [
                {
                    "note": "table = present content as a columnar grid; formats = the response IS about document types and their suitability",
                    "token": "table",
                }
            ],
            "heuristics": [
                "what format should I use",
                "what template fits",
                "which document type",
                "writing format options",
                "what structure should this take",
                "what are the format options",
                "format comparison",
            ],
        },
        "ghost": {
            "distinctions": [
                {
                    "note": "log = dated work log entry for reference; ghost = workflow execution trace showing actions and their results",
                    "token": "log",
                },
                {
                    "note": "walkthrough = guided sequential narration of a process; ghost = trace of autonomous actions actually performed",
                    "token": "walkthrough",
                },
                {
                    "note": "mark = method for capturing checkpoint evidence during a process; ghost = form for structuring output as workflow execution trace",
                    "token": "mark",
                },
            ],
            "heuristics": [
                "show me what you did",
                "execution trace",
                "workflow trace",
                "action log with results",
                "what actions were taken and what happened",
                "trace of work performed",
                "autonomous workflow execution",
            ],
        },
        "indirect": {
            "distinctions": [
                {
                    "note": "direct = conclusion first, supporting detail after; indirect = reasoning first, conclusion last",
                    "token": "direct",
                },
                {
                    "note": "case = structured argument with explicit evidence and objection handling; indirect = softer narrative reasoning that converges on a bottom-line "
                    "point",
                    "token": "case",
                },
            ],
            "heuristics": [
                "walk me through the reasoning first",
                "build up to the recommendation",
                "show your thinking before the conclusion",
                "give me the context before the answer",
                "reasoning before conclusion",
            ],
        },
        "log": {
            "distinctions": [
                {
                    "note": "walkthrough = guided sequential narration; log = concise dated entry format for archival and reference",
                    "token": "walkthrough",
                },
                {
                    "note": "bug = structured defect report with reproduction steps; log = work or research log entry",
                    "token": "bug",
                },
            ],
            "heuristics": [
                "write this as a log entry",
                "work log",
                "research log",
                "log format",
                "dated entry",
                "journal entry",
                "log what we did",
                "write up as a log",
            ],
        },
        "merge": {
            "distinctions": [
                {
                    "note": "contextualise = package with context for downstream LLM; merge = combine multiple sources into one coherent whole",
                    "token": "contextualise",
                }
            ],
            "heuristics": [
                "merge these",
                "combine into one",
                "consolidate",
                "synthesize these sources",
                "merge the content",
                "bring these together",
                "unify these documents",
                "integrate these into a single output",
            ],
        },
        "prep": {
            "distinctions": [
                {
                    "note": "prep = design the experiment before running it; vet = review the results after running it",
                    "token": "vet",
                },
                {
                    "note": "experimental (method) = analytical lens of proposing experiments; prep (form) = output structured as an experiment write-up",
                    "token": "experimental",
                },
            ],
            "heuristics": [
                "design an experiment",
                "write up the experiment plan",
                "experiment design write-up",
                "hypothesis and method",
                "frame this as an experiment",
                "set up the test structure",
                "experiment write-up with expected outcomes",
                "plan my debugging experiment",
                "structure my debugging hypothesis and tests",
                "write up the debugging test plan",
            ],
        },
        "questions": {
            "distinctions": [
                {
                    "note": "socratic = LLM asks the USER questions interactively to surface their thinking; questions = response IS a question-list artifact the user takes "
                    "away",
                    "token": "socratic",
                },
                {
                    "note": "faq = questions paired with their answers as a reference artifact; questions = response IS a question-list without answers",
                    "token": "faq",
                },
            ],
            "heuristics": [
                "what questions should I ask",
                "give me questions to investigate",
                "what should I be asking about",
                "frame this as questions",
                "questions I should explore",
                "diagnostic questions for",
            ],
        },
        "quiz": {
            "distinctions": [
                {
                    "note": "socratic = question-led dialogue to surface user reasoning; quiz = test recall via question-then-answer structure",
                    "token": "socratic",
                }
            ],
            "heuristics": [
                "quiz me",
                "make a quiz",
                "quiz format",
                "questions before answers",
                "test my knowledge",
                "knowledge check",
                "quiz questions on",
                "multiple choice quiz",
            ],
        },
        "recipe": {
            "distinctions": [
                {
                    "note": "walkthrough = linear narrated steps without custom notation; recipe = structured recipe with a custom mini-language and notation key",
                    "token": "walkthrough",
                }
            ],
            "heuristics": [
                "document as recipe",
                "structured setup guide with repeating patterns",
                "using a custom notation",
                "with a symbolic key",
                "repeating pattern I can express as a formula",
            ],
        },
        "scaffold": {
            "distinctions": [
                {
                    "note": "walkthrough = guided sequential steps through a known process; scaffold = pedagogical first-principles introduction that builds understanding",
                    "token": "walkthrough",
                }
            ],
            "heuristics": [
                "learning-oriented explanation",
                "explain from scratch",
                "teach me this",
                "start from first principles",
                "build up my understanding",
            ],
        },
        "snap": {
            "distinctions": [
                {
                    "note": "ghost = execution trace of autonomous actions and results; snap = save state structured for future resumption or handoff",
                    "token": "ghost",
                },
                {
                    "note": "log = narrative record of what happened; snap = forward-oriented state snapshot for resumption",
                    "token": "log",
                },
                {
                    "note": "mark (method) = capture checkpoint evidence during execution; snap (form) = structure output as a resumable state artifact",
                    "token": "mark",
                },
            ],
            "heuristics": [
                "save where we are",
                "checkpoint the work",
                "make this resumable",
                "save state so we can continue later",
                "handoff document",
                "what do I need to pick this up again",
                "save progress",
                "create a save file",
                "durable record for resumption",
                "so the next session can continue",
            ],
        },
        "socratic": {
            "distinctions": [
                {
                    "note": "questions = response IS a question-list artifact the user takes away; socratic = LLM asks the USER questions interactively to surface their thinking",
                    "token": "questions",
                },
                {
                    "note": "quiz = test recall via question-then-answer structure; socratic = question-led dialogue to surface reasoning",
                    "token": "quiz",
                },
            ],
            "heuristics": [
                "ask me questions",
                "help me think through",
                "challenge my assumptions with questions",
                "Socratic dialogue",
                "probe my thinking",
                "question me as we work through this",
                "help me reason this out",
            ],
        },
        "spike": {
            "distinctions": [
                {
                    "note": "story = user-facing value statement with acceptance criteria; spike = research question artifact focused on unknowns",
                    "token": "story",
                }
            ],
            "heuristics": [
                "should we adopt X?",
                "spike on Y",
                "investigation backlog item",
            ],
        },
        "story": {
            "distinctions": [
                {
                    "note": "spike = research question artifact focused on unknowns; story = user-facing value statement with acceptance criteria",
                    "token": "spike",
                }
            ],
            "heuristics": [
                "user story",
                "write as a user story",
                "as a user I want",
                "story format",
                "user story for this feature",
                "backlog user story",
                "story card",
            ],
        },
        "table": {
            "distinctions": [
                {
                    "note": "cards = discrete headed items; table = columnar grid layout",
                    "token": "cards",
                }
            ],
            "heuristics": [
                "table format",
                "present as a table",
                "markdown table",
                "tabular comparison",
                "show in a table",
                "grid format",
                "as a table",
                "column-row layout",
            ],
        },
        "taxonomy": {
            "distinctions": [
                {
                    "note": "table = flat columnar comparison; taxonomy = type hierarchy with defined relationships and distinguishing attributes",
                    "token": "table",
                }
            ],
            "heuristics": [
                "classify all types of X",
                "what kinds of Y exist",
                "type hierarchy",
            ],
        },
        "test": {
            "distinctions": [
                {
                    "note": "checklist = imperative tasks to complete; test = structured test scenarios with setup/execute/assert structure",
                    "token": "checklist",
                }
            ],
            "heuristics": [
                "write test cases",
                "test cases for",
                "happy path and edge cases",
                "unit test structure",
                "test scenarios",
                "write the tests",
                "test case format with setup and assertion",
            ],
        },
        "tight": {
            "distinctions": [
                {
                    "note": "plain = no structural decoration as a delivery format (channel); tight = concise dense prose style (form) that avoids filler",
                    "token": "plain",
                }
            ],
            "heuristics": [
                "tight prose",
                "concise and dense",
                "compact freeform",
                "dense prose",
                "brevity without structure",
                "no padding or filler",
                "maximum signal per word",
            ],
        },
        "timeline": {
            "distinctions": [
                {
                    "note": "timeline (form) = output structured as a temporal sequence layout; walkthrough (form) = guided step-by-step narration",
                    "token": "walkthrough",
                },
                {
                    "note": "timeline (form) = temporal layout of stages; log (form) = dated work-log entries",
                    "token": "log",
                },
            ],
            "heuristics": [
                "as a timeline",
                "show the history in timeline format",
                "timeline of events",
                "chronological sequence",
                "temporal order with markers",
                "sequence of stages over time",
                "show this as a timeline",
            ],
        },
        "twin": {
            "distinctions": [
                {
                    "note": "twin = strict side-by-side layout with equal weight per alternative; variants = labeled options with descriptions (may be narrative)",
                    "token": "variants",
                },
                {
                    "note": "twin = layout form for direct comparison; table = tabular grid for structured multi-attribute comparison",
                    "token": "table",
                },
            ],
            "heuristics": [
                "side by side",
                "compare X and Y side by side",
                "two alternatives side by side",
                "equal weight comparison",
                "show both without interleaving",
                "parallel comparison layout",
                "show the two options in parallel",
            ],
        },
        "variants": {
            "distinctions": [
                {
                    "note": "cocreate = iterative process with decision points and alignment checks; variants = present distinct labeled options without necessarily evaluating "
                    "them against each other",
                    "token": "cocreate",
                }
            ],
            "heuristics": [
                "give me options",
                "present several approaches",
                "show me alternatives",
                "multiple variants",
                "different approaches",
                "what are the options with labels",
                "present 3 options",
                "decision-ready alternatives",
            ],
        },
        "vet": {
            "distinctions": [
                {
                    "note": "vet = post-experiment review of outcomes vs expectations; prep = experiment design write-up before running",
                    "token": "prep",
                },
                {
                    "note": "wasinawa = what/so-what/now-what reflection on past events; vet = structured review of experiment results against predictions",
                    "token": "wasinawa",
                },
            ],
            "heuristics": [
                "review the results against what we predicted",
                "post-experiment review",
                "compare outcomes to expectations",
                "what did we actually observe vs what we expected",
                "debrief on the experiment",
                "what were the results compared to our hypothesis",
                "review what happened vs what we planned",
                "post-debug review",
                "review what my debugging found vs what I expected",
                "what did the debugging reveal vs my hypothesis",
            ],
        },
        "walkthrough": {
            "distinctions": [
                {
                    "note": "actions = list of actions to take; walkthrough = guided sequential narration that builds understanding",
                    "token": "actions",
                },
                {
                    "note": "scaffold = pedagogical first-principles introduction; walkthrough = guided sequential steps through a known process",
                    "token": "scaffold",
                },
            ],
            "heuristics": [
                "walk me through",
                "step by step walkthrough",
                "guide me through",
                "take me through it",
                "step-by-step guide",
                "walkthrough of",
                "narrate the steps",
            ],
        },
        "wardley": {
            "distinctions": [],
            "heuristics": [
                "Wardley map",
                "map on evolution axis",
                "genesis to commodity",
            ],
        },
        "wasinawa": {
            "distinctions": [
                {
                    "note": "inversion (method) = reason backward from any catastrophic outcome (past or future) to find causes or design-around paths; wasinawa (form) = "
                    "structured reflection on past events using what/so-what/now-what",
                    "token": "inversion",
                }
            ],
            "heuristics": [
                "reflect on incident",
                "what went wrong and what to do next",
                "lessons learned",
            ],
        },
    },
    "method": {
        "abduce": {
            "distinctions": [
                {
                    "note": "diagnose = narrow to single root cause via evidence; abduce = generate and compare multiple competing explanations explicitly",
                    "token": "diagnose",
                },
                {
                    "note": "induce = generalize a rule from examples; abduce = hypothesize from evidence",
                    "token": "induce",
                },
            ],
            "heuristics": [
                "what's the best explanation for",
                "generate hypotheses for why",
                "what are the most likely causes ranked",
                "compare possible explanations",
                "ranked hypotheses from evidence",
                "what could explain this",
                "what are the possible causes of this bug",
                "generate competing explanations for this error",
            ],
        },
        "actors": {
            "distinctions": [
                {
                    "note": "agent (scope) = who has decision authority; actors (method) = enrich the response with actor-centered analysis regardless of scope",
                    "token": "agent",
                }
            ],
            "heuristics": [
                "who is involved",
                "what are the stakeholders doing",
                "who are the actors",
                "center the people",
                "model the roles",
                "who does what",
                "what motivates each party",
                "threat actors",
                "roles and responsibilities",
            ],
        },
        "adversarial": {
            "distinctions": [
                {
                    "note": "risks = enumerate failure modes and likelihood; adversarial = actively stress-test by constructing attacks and counterexamples",
                    "token": "risks",
                }
            ],
            "heuristics": [
                "what could go wrong",
                "find the weaknesses",
                "stress-test this",
                "what's the worst-case attack",
                "where does this argument break",
                "challenge this plan",
                "red-team this",
                "what are the counterexamples",
                "play devil's advocate",
            ],
        },
        "afford": {
            "distinctions": [
                {
                    "note": "actors interact via a shared medium; afford = how available-action structure pre-shapes individual choices",
                    "token": "field",
                },
                {
                    "note": "feedback loops and emergent dynamics; afford = structural availability shapes what actors perceive as actionable",
                    "token": "systemic",
                },
            ],
            "heuristics": [
                "why do users do X",
                "the design encourages Y",
                "affordances",
                "what the API makes easy",
                "shaped by the structure",
                "how the design foregrounds this option",
                "structural constraints on behavior",
                "design defaults bias toward",
                "interface suppresses this action",
            ],
        },
        "align": {
            "distinctions": [
                {
                    "note": "balance = model opposing forces that offset each other; align = restructure explicit elements to achieve mutual reinforcement",
                    "token": "balance",
                },
                {
                    "note": "clash = diagnose conflicts; align = resolve them by restructuring",
                    "token": "clash",
                },
            ],
            "heuristics": [
                "align these structures",
                "make them globally coherent",
                "restore consistency",
                "reconcile conflicting commitments",
                "restructure so parts reinforce each other",
                "everything needs to be consistent globally",
            ],
        },
        "amorph": {
            "distinctions": [
                {
                    "note": "gap = specific implicit/explicit mismatch in rules or roles; amorph = broader regions lacking stable explicit organization",
                    "token": "gap",
                },
                {
                    "note": "crystal = shape system toward explicit structure; amorph = identify where that structure is absent",
                    "token": "crystal",
                },
            ],
            "heuristics": [
                "where is this undefined",
                "find the unstructured regions",
                "where is behavior emergent rather than explicit",
                "identify the ambiguous areas",
                "where does implicit understanding substitute for structure",
                "fluid or changing structure",
            ],
        },
        "analog": {
            "distinctions": [
                {
                    "note": "models = apply named mental models explicitly; analog = reason through a structural mapping from a specific known case",
                    "token": "models",
                }
            ],
            "heuristics": [
                "what is this like",
                "what does this remind you of",
                "explain using an analogy",
                "what's the analogous structure",
                "reason by analogy",
                "find a parallel case",
                "what known situation does this resemble",
            ],
        },
        "analysis": {
            "distinctions": [
                {
                    "note": "diagnose = root cause via falsification; analysis = structural decomposition without fault-finding",
                    "token": "diagnose",
                }
            ],
            "heuristics": [
                "analyze this",
                "describe the situation",
                "help me understand what's happening",
                "structure my understanding",
                "what is going on here",
                "break this down for me",
                "understand before acting",
            ],
        },
        "argue": {
            "distinctions": [
                {
                    "note": "case (form) = narrative that builds to a recommendation; argue (method) = expose the logical structure of claims and their supports",
                    "token": "case",
                }
            ],
            "heuristics": [
                "make the argument",
                "structure this as an argument",
                "what are the premises",
                "what supports this claim",
                "build the logical case",
                "argument and rebuttal",
                "explicit reasoning structure",
            ],
        },
        "automate": {
            "distinctions": [
                {
                    "note": "automate = prefer automated operations over manual ones; ground = enforce falsifiability and advance through validation rungs",
                    "token": "ground",
                },
                {
                    "note": "automate = remove human dependency from repeatable operations; control = focus on factors within agency",
                    "token": "control",
                },
            ],
            "heuristics": [
                "automate this",
                "make it automatic",
                "remove manual steps",
                "don't require human intervention",
                "repeatable without human involvement",
                "script this",
                "set it and forget it",
                "CI/CD",
                "automated pipeline",
                "reduce toil",
                "eliminate manual work",
            ],
        },
        "balance": {
            "distinctions": [
                {
                    "note": "resilience = behavior under stress; balance = how opposing forces produce equilibrium or instability",
                    "token": "resilience",
                }
            ],
            "heuristics": [
                "how do forces balance",
                "what opposing pressures exist",
                "what keeps this in equilibrium",
                "what countervailing forces",
                "how do trade-offs play out",
                "what tensions exist",
                "balance of forces",
            ],
        },
        "behave": {
            "distinctions": [
                {
                    "note": "jobs = analyze outcomes users want and forces shaping choices; behave = model capability/opportunity/motivation to diagnose why a behavior occurs or "
                    "doesn't and design interventions",
                    "token": "jobs",
                },
                {
                    "note": "actors = identify and center who is involved; behave = apply COM-B framework to model what that actor needs to change behavior",
                    "token": "actors",
                },
            ],
            "heuristics": [
                "why aren't people doing X",
                "behavior change analysis",
                "COM-B",
                "what's preventing adoption",
                "capability opportunity motivation",
                "behavior change intervention",
                "what barriers prevent behavior change",
                "how do we get people to do X",
                "behavior change wheel",
                "BCT",
            ],
        },
        "bias": {
            "distinctions": [
                {
                    "note": "verify = falsify specific claims; bias = identify cognitive mechanisms producing distortion",
                    "token": "verify",
                }
            ],
            "heuristics": [
                "what biases might affect this",
                "cognitive biases",
                "where might we be wrong due to bias",
                "what systematic errors",
                "heuristics distorting judgment",
                "where are we susceptible to bias",
                "confirmation bias",
                "availability heuristic",
            ],
        },
        "boom": {
            "distinctions": [
                {
                    "note": "boom = behavior at extremes of scale/intensity where things qualitatively break or dominate; resilience = behavior under normal stress range",
                    "token": "resilience",
                }
            ],
            "heuristics": [
                "at 10x",
                "at extreme load",
                "what breaks at scale",
                "pushed to the limit",
                "at maximum load",
                "what dominates at scale",
                "scale to the extreme",
                "at the limit",
            ],
        },
        "bound": {
            "distinctions": [
                {
                    "note": "depends = trace all dependencies; bound = limit how far they spread",
                    "token": "depends",
                },
                {
                    "note": "ground = treat declared governing layer as fixed authority; bound = limit reach of influence",
                    "token": "ground",
                },
            ],
            "heuristics": [
                "limit the scope of changes",
                "constrain how far effects spread",
                "bound the blast radius",
                "contain the impact",
                "what happens locally vs globally",
                "limit responsibility propagation",
                "scope the change impact",
            ],
        },
        "calc": {
            "distinctions": [
                {
                    "note": "probability = statistical and probabilistic reasoning; calc = general quantitative or quasi-executable procedures",
                    "token": "probability",
                }
            ],
            "heuristics": [
                "calculate",
                "what does the math say",
                "run the numbers",
                "quantify this",
                "estimate the cost",
                "work out the probability",
                "formal calculation",
                "compute",
                "what are the numbers",
            ],
        },
        "cite": {
            "distinctions": [
                {
                    "note": "verify = apply falsification pressure internally; cite = anchor claims to external sources the user can check",
                    "token": "verify",
                }
            ],
            "heuristics": [
                "cite your sources",
                "include references",
                "back this up with evidence",
                "link to sources",
                "where does this come from",
                "support with citations",
                "show your evidence",
            ],
        },
        "clash": {
            "distinctions": [
                {
                    "note": "gap = implicit treated as explicit producing coordination failures; clash = conflict between explicitly stated structures",
                    "token": "gap",
                },
                {
                    "note": "adversarial = construct attacks to stress-test; clash = identify existing structural conflicts",
                    "token": "adversarial",
                },
            ],
            "heuristics": [
                "where do these conflict",
                "rule conflicts",
                "inconsistent constraints",
                "local validity but global failure",
                "what commitments contradict each other",
                "misaligned rules",
                "structural conflict",
                "find the incompatibilities",
                "both constraints are explicitly stated but they contradict",
            ],
        },
        "cluster": {
            "distinctions": [
                {
                    "note": "compare = evaluate alternatives against criteria; cluster = group without evaluating",
                    "token": "compare",
                }
            ],
            "heuristics": [
                "group these",
                "cluster by",
                "categorize",
                "organize into groups",
                "what themes emerge",
                "sort into buckets",
                "group by similarity",
                "classify these items",
            ],
        },
        "compare": {
            "distinctions": [
                {
                    "note": "converge = narrow from exploration to recommendation; compare = explicit criteria-based evaluation of specified alternatives",
                    "token": "converge",
                }
            ],
            "heuristics": [
                "compare X and Y",
                "which is better",
                "how do these differ",
                "tradeoffs between",
                "evaluate these options",
                "side by side comparison",
                "which should I choose",
                "pros and cons",
            ],
        },
        "control": {
            "distinctions": [
                {
                    "note": "agent (scope) = identify who has decision-making authority in a system; control (method) = direct evaluation exclusively toward factors within "
                    "agency, excluding those outside it",
                    "token": "agent",
                }
            ],
            "heuristics": [
                "focus on what I can control",
                "what's within my control",
                "what's outside my control",
                "separate what's up to me from what's not",
                "what can I influence",
                "what's within my agency",
                "focus on what's in my control",
            ],
        },
        "converge": {
            "distinctions": [
                {
                    "note": "compare = evaluate alternatives side by side; converge = narrow exploration toward a single recommendation",
                    "token": "compare",
                }
            ],
            "heuristics": [
                "narrow it down",
                "which one should I go with",
                "help me pick",
                "synthesize into a recommendation",
                "from all options, which is best",
                "converge on an answer",
                "filter and recommend",
            ],
        },
        "crystal": {
            "distinctions": [
                {
                    "note": "ground = treat declared governing layer as fixed authority; crystal = broadly shape system toward explicit structural determination",
                    "token": "ground",
                },
                {
                    "note": "reify = surface one implicit pattern as an explicit rule; crystal = systemic shift toward structural explicitness",
                    "token": "reify",
                },
                {
                    "note": "amorph = diagnose lack of crystallized structure; crystal = restructure toward it",
                    "token": "amorph",
                },
            ],
            "heuristics": [
                "crystallize the structure",
                "replace implicit reasoning with structural enforcement",
                "explicit organization over interpretation",
                "reduce reliance on tacit knowledge",
                "behavior should follow from structure directly",
                "remove implicit coupling",
                "the whole system should be explicit",
                "no more convention over configuration",
            ],
        },
        "deduce": {
            "distinctions": [{"note": "evidence → hypothesis", "token": "abduce"}],
            "heuristics": [
                "what follows from",
                "given these premises",
                "logical conclusion",
                "deduce from",
                "what must be true if",
                "derive the consequence",
                "if X then what",
                "logically entails",
            ],
        },
        "depends": {
            "distinctions": [
                {
                    "note": "struct (scope) = internal arrangement; depends (method) = propagation and reliance relationships specifically",
                    "token": "struct",
                }
            ],
            "heuristics": [
                "what depends on X",
                "dependency map",
                "what breaks if I change Y",
                "what does this rely on",
                "upstream and downstream",
                "dependency chain",
                "what would be affected",
                "what does Z need to work",
            ],
        },
        "diagnose": {
            "distinctions": [
                {
                    "note": "abduce = generate and compare competing hypotheses; diagnose = narrow to single most likely cause via falsification",
                    "token": "abduce",
                }
            ],
            "heuristics": [
                "what is causing this",
                "root cause",
                "why is this happening",
                "diagnose this problem",
                "narrow down the cause",
                "what's the bug source",
                "investigate why",
                "find the root cause",
                "debug this",
                "help me debug",
            ],
        },
        "dimension": {
            "distinctions": [
                {
                    "note": "split = decompose into parts; dimension = surface analytical axes that the parts exist along",
                    "token": "split",
                }
            ],
            "heuristics": [
                "what are the dimensions",
                "what factors are at play",
                "multiple axes of analysis",
                "what hidden factors",
                "what are we not considering",
                "analyze across dimensions",
                "surface the implicit factors",
            ],
        },
        "domains": {
            "distinctions": [
                {
                    "note": "struct (scope) = internal arrangement; domains (method) = identify bounded context separations and capabilities",
                    "token": "struct",
                }
            ],
            "heuristics": [
                "what are the domains",
                "where are the bounded contexts",
                "domain-driven design",
                "what are the distinct capabilities",
                "domain boundaries",
                "how to carve up the system into domains",
                "which team owns which",
            ],
        },
        "drift": {
            "distinctions": [
                {
                    "note": "gap = implicit assumptions in rules or roles produce coordination failures; drift = structural looseness allows interpretive inference to substitute "
                    "for derivability",
                    "token": "gap",
                },
                {
                    "note": "mint = restructure to make conclusions derivable; drift = diagnose where derivability is absent",
                    "token": "mint",
                },
            ],
            "heuristics": [
                "conclusions that depend on interpretation",
                "where reasoning could diverge",
                "identify underenforced conclusions",
                "conclusions that are implicit not derivable",
                "where does the representation allow inconsistency",
                "conclusions that vary on re-derivation",
                "where the same premises yield different outputs",
            ],
        },
        "effects": {
            "distinctions": [
                {
                    "note": "grove = how effects accumulate and compound; effects = trace the chain of consequences",
                    "token": "grove",
                }
            ],
            "heuristics": [
                "what are the downstream effects",
                "second order effects",
                "ripple effects",
                "what happens next after that",
                "unintended consequences",
                "how does this propagate",
                "what follows downstream",
            ],
        },
        "experimental": {
            "distinctions": [
                {
                    "note": "verify = apply falsification pressure analytically; experimental = propose actual runnable tests",
                    "token": "verify",
                }
            ],
            "heuristics": [
                "design an experiment",
                "how would we test this",
                "what experiment would prove this",
                "propose tests",
                "how do we validate",
                "what would we measure",
                "design a study",
                "run a test to find out",
                "debug this scientifically",
                "what hypothesis explains this bug",
                "treat this as a debugging experiment",
                "systematic debugging",
                "how do I isolate the cause",
            ],
        },
        "field": {
            "distinctions": [
                {
                    "note": "surface elements; field = model the medium and why compatibility produces observed routing",
                    "token": "mapping",
                }
            ],
            "heuristics": [
                "shared infrastructure",
                "shared medium",
                "protocol mediation",
                "service mesh routing",
                "why things route through",
                "broadcast patterns",
                "effects propagate through a shared layer",
            ],
        },
        "flow": {
            "distinctions": [
                {
                    "note": "time = temporal emphasis as scope lens; flow = step-by-step progression as a reasoning method",
                    "token": "time",
                }
            ],
            "heuristics": [
                "walk me through the flow",
                "how does data move",
                "trace the execution path",
                "step by step sequence",
                "control flow",
                "how does it progress",
                "follow the data through the system",
                "trace the path",
            ],
        },
        "gap": {
            "distinctions": [
                {
                    "note": "assume (scope) = restrict analysis to the premises domain; gap (method) = identify where implicit is treated as explicit",
                    "token": "assume",
                }
            ],
            "heuristics": [
                "what's assumed but not stated",
                "implicit vs explicit mismatch",
                "what's implicit but treated as explicit",
                "where are the hidden assumptions",
                "what's taken for granted",
                "gap between stated and actual",
                "two people assumed different things about this rule",
            ],
        },
        "ground": {
            "distinctions": [
                {
                    "note": "bound = restrict propagation of effects to a region; ground = treat a declared governing layer as fixed and authoritative that representations must "
                    "justify against",
                    "token": "bound",
                },
                {
                    "note": "crystal = shape system toward explicit structure; ground = treat a declared layer as fixed authority requiring justification, not crystallization",
                    "token": "crystal",
                },
                {
                    "note": "mint = build forward from assumptions toward conclusions; ground = validate backward against a fixed declared intent — they operate in opposite "
                    "directions",
                    "token": "mint",
                },
            ],
            "heuristics": [
                "define the spec first",
                "TDD",
                "test-driven design",
                "what should it do before how",
                "specification before implementation",
                "write the tests first",
                "define success criteria",
                "correctness criteria",
                "ensure intent governs downstream",
                "justify against declared constraints",
                "explicit intent alignment",
                "meaning governed by intent",
                "I have a declared spec and want all reasoning to justify against it",
                "I cannot tell from the requirement alone whether this output is correct",
                "do not apply during active exploration when intent is not yet stable",
                "what would prove this is done",
                "define the success condition before building",
                "write the acceptance criteria before the document",
                "what does passing look like",
                "what check would reject a bad version of this",
            ],
        },
        "grove": {
            "distinctions": [
                {
                    "note": "interacting whole; grove = rate of accumulation through mechanisms",
                    "token": "systemic",
                }
            ],
            "heuristics": [
                "compound",
                "accumulates over time",
                "feedback loop",
                "technical debt grows",
                "network effect",
                "how things build up",
                "rate of change over time",
                "snowball",
            ],
        },
        "induce": {
            "distinctions": [
                {
                    "note": "abduce = generate competing hypotheses to explain evidence; induce = generalize a rule or pattern from a set of examples",
                    "token": "abduce",
                }
            ],
            "heuristics": [
                "what general principle can I draw from these",
                "what pattern do these examples suggest",
                "what does this tell us more broadly",
                "generalize from these observations",
                "what can I conclude from these cases",
                "what rule emerges from these instances",
                "extrapolate from these examples",
            ],
        },
        "inversion": {
            "distinctions": [
                {
                    "note": "risks = enumerate failure modes; inversion = start FROM disaster and derive what to avoid",
                    "token": "risks",
                }
            ],
            "heuristics": [
                "what would cause this to fail completely",
                "pre-mortem",
                "how would we destroy this",
                "what would guarantee failure",
                "invert the goal",
                "work backwards from disaster",
                "what produces the worst outcome",
            ],
        },
        "jobs": {
            "distinctions": [
                {
                    "note": "product = features, user needs, value propositions broadly; jobs = specifically the outcome/progress users seek and the forces blocking or enabling it",
                    "token": "product",
                }
            ],
            "heuristics": [
                "what is the user actually trying to accomplish",
                "what job does this feature do",
                "what need does this solve",
                "why would someone use this",
                "what outcome does the user want",
                "what drives adoption",
                "user motivation behind",
                "JTBD",
                "jobs to be done",
            ],
        },
        "ladder": {
            "distinctions": [
                {
                    "note": "fog/dig (directional) = push the whole response toward abstract or concrete; ladder (method) = actively traverse both directions within the response",
                    "token": "fog",
                },
                {
                    "note": "zoom (completeness) = scale bucket size to span magnitude; ladder (method) = move between named abstraction levels around a focal point",
                    "token": "zoom",
                },
            ],
            "heuristics": [
                "step up and down abstraction levels",
                "root cause hierarchy",
                "why at a systems level",
                "zoom out then zoom in",
                "from concrete to abstract and back",
                "abstraction ladder",
                "levels of abstraction",
            ],
        },
        "mapping": {
            "distinctions": [
                {
                    "note": "struct (scope) = internal topology of one unit; mapping (method) = surface and organize across the whole landscape",
                    "token": "struct",
                }
            ],
            "heuristics": [
                "map out",
                "surface the relationships",
                "landscape map",
                "draw the connections",
                "build a map of",
                "what's the structure of the landscape",
                "map the territory",
                "visualize the relationships",
            ],
        },
        "mark": {
            "distinctions": [
                {
                    "note": "trace = narrate the sequential control/data progression; mark = record checkpoint observations without narrating",
                    "token": "trace",
                }
            ],
            "heuristics": [
                "record what happened at each stage",
                "audit log",
                "checkpoint evidence",
                "what was observed at each step",
                "capture intermediate state",
                "audit trail",
                "what was the system state at X",
            ],
        },
        "meld": {
            "distinctions": [
                {
                    "note": "evaluate alternatives; meld = balance constraints between elements that must coexist",
                    "token": "compare",
                }
            ],
            "heuristics": [
                "balance between",
                "overlap between",
                "constraints between",
                "combining X and Y",
                "where X and Y interact",
                "navigate tensions between",
                "find the combination that satisfies",
            ],
        },
        "melody": {
            "distinctions": [
                {
                    "note": "depends = what relies on what (reliance structure); melody = pressure profile of the seam (visibility, scope, volatility)",
                    "token": "depends",
                },
                {
                    "note": "snag = surface where coupling seams exist; melody = rate the quality of a seam across three pressure dimensions",
                    "token": "snag",
                },
                {
                    "note": "mesh = trace how coupling propagates across a seam; melody = rate the seam's visibility, scope, and volatility",
                    "token": "mesh",
                },
            ],
            "heuristics": [
                "rate this seam",
                "characterise the seam",
                "how bad is this coupling",
                "visibility scope volatility",
                "how discoverable is the contract",
                "how wide does the change propagate",
                "temporal coupling sensitivity",
                "structural coupling sensitivity",
                "how tightly coupled are these changes",
                "seam quality",
                "coupling pressure profile",
            ],
        },
        "mesh": {
            "distinctions": [
                {
                    "note": "snag = surface where coupling seams exist; mesh = describe how coupling propagates across them",
                    "token": "snag",
                },
                {
                    "note": "shear = outline steps to separate coupled domains; mesh = describe the propagation structure before separating",
                    "token": "shear",
                },
                {
                    "note": "mesh = describe how coupling propagates across a seam; seep = identify where that coupling has leaked past intended scope",
                    "token": "seep",
                },
            ],
            "heuristics": [
                "how does coupling propagate",
                "what does each coupled domain affect",
                "trace influence across the seam",
                "how does change in X affect Y",
                "describe the coupling structure",
                "what travels across the boundary",
            ],
        },
        "migrate": {
            "distinctions": [
                {
                    "note": "preserve = keep existing behavior unchanged; migrate = introduce a transition path that moves toward a new structure",
                    "token": "preserve",
                },
                {
                    "note": "reset = discard prior commitments entirely; migrate = change while maintaining temporary compatibility",
                    "token": "reset",
                },
            ],
            "heuristics": [
                "migrate from X to Y",
                "transition path",
                "upgrade while keeping compatibility",
                "bridge old and new",
                "deprecation path",
                "phased transition",
                "backward compatible change",
                "coexist old and new",
            ],
        },
        "mint": {
            "distinctions": [
                {
                    "note": "deduce = apply deductive logic to stated premises; mint = construct the generative structure so conclusions are built forward",
                    "token": "deduce",
                },
                {
                    "note": "ground = treat declared governing layer as fixed authority; mint = construct generative assumptions into explicit derivations",
                    "token": "ground",
                },
            ],
            "heuristics": [
                "build the generative assumptions forward",
                "construct explicit derivations",
                "conclusions are products of the model",
                "derivation structure is the response",
                "make derivation steps explicit and auditable",
            ],
        },
        "mod": {
            "distinctions": [
                {
                    "note": "motifs (scope) = recurring patterns across codebase; mod (method) = cyclic/periodic reasoning about behavior that repeats with a defined period",
                    "token": "motifs",
                }
            ],
            "heuristics": [
                "repeats across cycles",
                "cyclic behavior",
                "periodic pattern",
                "repeating structure",
                "what wraps around",
                "recurs periodically",
                "equivalent states",
            ],
        },
        "models": {
            "distinctions": [
                {
                    "note": "analog = reason from a specific analogous case; models = apply named, established mental models explicitly",
                    "token": "analog",
                }
            ],
            "heuristics": [
                "what mental models apply here",
                "apply a framework",
                "use first principles",
                "which frameworks are relevant",
                "what lenses should I use",
                "apply systems thinking",
                "what models explain this",
                "name the applicable mental models",
            ],
        },
        "objectivity": {
            "distinctions": [
                {
                    "note": "rigor = disciplined logical reasoning; objectivity = separate what is factual from what is evaluative",
                    "token": "rigor",
                }
            ],
            "heuristics": [
                "what's objective vs subjective",
                "separate fact from opinion",
                "what is actually true vs what is a judgment",
                "stick to facts",
                "evidence-based only",
                "distinguish observation from interpretation",
                "is this a fact or an opinion",
            ],
        },
        "operations": {
            "distinctions": [
                {
                    "note": "systemic = feedback loops and emergent behavior; operations = OR/management science frameworks for resource and flow optimization",
                    "token": "systemic",
                }
            ],
            "heuristics": [
                "throughput",
                "bottleneck analysis",
                "resource allocation",
                "scheduling problem",
                "queuing",
                "capacity planning",
                "utilization",
                "operations research",
                "minimize wait time",
                "optimization problem",
            ],
        },
        "order": {
            "distinctions": [
                {
                    "note": "prioritize = rank by importance with rationale; order = abstract structural reasoning about ordering schemes",
                    "token": "prioritize",
                }
            ],
            "heuristics": [
                "what is the ordering principle",
                "hierarchical ordering",
                "ranking criteria",
                "what determines the order",
                "dominance structure",
                "what makes one thing rank above another",
                "ordering and precedence",
            ],
        },
        "origin": {
            "distinctions": [
                {
                    "note": "time (scope) = sequential/temporal emphasis; origin (method) = specifically causal history and why the present state is as it is",
                    "token": "time",
                }
            ],
            "heuristics": [
                "how did we get here",
                "what is the history of",
                "why does it look this way",
                "what past decisions led to this",
                "origin story",
                "historical context",
                "how did this evolve",
                "archaeology of the codebase",
                "why is this the way it is",
            ],
        },
        "perturb": {
            "distinctions": [
                {
                    "note": "adversarial = construct attacks to find weaknesses; perturb = introduce controlled variations to observe response",
                    "token": "adversarial",
                },
                {
                    "note": "experimental = design experiments to test hypotheses; perturb = actively vary the system to see effects",
                    "token": "experimental",
                },
            ],
            "heuristics": [
                "what if we break this",
                "test the failure modes",
                "introduce faults",
                "perturb the system",
                "stress test by changing inputs",
                "what happens when we modify",
                "test the assumptions",
                "check detection mechanisms",
                "probe resilience",
            ],
        },
        "polar": {
            "distinctions": [
                {
                    "note": "balance = forces offsetting each other; polar = attraction toward some states and aversion from others",
                    "token": "balance",
                }
            ],
            "heuristics": [
                "what attracts and repels",
                "pull toward and push away from",
                "what are the incentives and disincentives",
                "goals and anti-goals",
                "what pulls toward and pushes away",
                "what's the attractor and repeller",
                "positive and negative forces",
            ],
        },
        "preserve": {
            "distinctions": [
                {
                    "note": "migrate = introduce a transition path toward a new structure; preserve = constrain changes to keep existing components working unchanged",
                    "token": "migrate",
                },
                {
                    "note": "reset = discard compatibility constraints; preserve = explicitly maintain them",
                    "token": "reset",
                },
            ],
            "heuristics": [
                "don't break existing behavior",
                "maintain backward compatibility",
                "keep existing interfaces working",
                "non-breaking change",
                "preserve the contract",
                "existing clients must still work",
                "no breaking changes",
                "stay compatible with",
            ],
        },
        "prioritize": {
            "distinctions": [
                {
                    "note": "order = abstract structural reasoning about ordering schemes; prioritize = rank by importance or impact with explicit rationale",
                    "token": "order",
                }
            ],
            "heuristics": [
                "prioritize",
                "what should we do first",
                "rank by impact",
                "most important first",
                "order by priority",
                "what matters most",
                "high-priority items",
                "rank and explain the ranking",
            ],
        },
        "probability": {
            "distinctions": [
                {
                    "note": "calc = general quantitative computation; probability = specifically statistical and probabilistic reasoning under uncertainty",
                    "token": "calc",
                }
            ],
            "heuristics": [
                "how likely is",
                "what's the probability",
                "expected value",
                "confidence interval",
                "statistical significance",
                "base rate",
                "probability of failure",
                "how certain are we",
                "Bayesian reasoning",
                "likelihood",
            ],
        },
        "product": {
            "distinctions": [
                {
                    "note": "jobs = outcomes users seek and forces shaping adoption; product = broader product lens including features and value propositions",
                    "token": "jobs",
                }
            ],
            "heuristics": [
                "product perspective",
                "through a product lens",
                "feature vs user need",
                "value proposition",
                "product strategy",
                "what does the product offer",
                "user needs analysis",
                "product thinking",
            ],
        },
        "pulse": {
            "distinctions": [
                {
                    "note": "flow = narrate step-by-step sequence; pulse = model noise, distortion, and fidelity across encode/decode stages",
                    "token": "flow",
                }
            ],
            "heuristics": [
                "where does signal get lost",
                "where does data degrade",
                "signal fidelity",
                "where is information lost in transmission",
                "where does the message get distorted",
                "trace signal path through the system",
                "where does noise enter",
                "signal-to-noise",
                "observability pipeline fidelity",
            ],
        },
        "reify": {
            "distinctions": [
                {
                    "note": "analysis = describe and structure; reify = convert implicit patterns into explicit formal rules",
                    "token": "analysis",
                }
            ],
            "heuristics": [
                "name this pattern",
                "what principle is this following",
                "give this a name",
                "I've found a pattern everyone follows implicitly — encode it as an explicit rule",
                "what rules actually govern this",
                "what constraints should be formally stated",
                "make this convention into a constraint",
            ],
        },
        "release": {
            "distinctions": [
                {
                    "note": "shift = rotate through multiple cognitive perspectives; release = reduce distortion by loosening identification with transient states or roles "
                    "rather than rotating perspective",
                    "token": "shift",
                }
            ],
            "heuristics": [
                "let go of the outcome",
                "detach from the result",
                "stop over-identifying with the role",
                "reduce attachment",
                "clarity through non-attachment",
                "separate the outcome from the person",
                "non-attached analysis",
                "release the assumption",
                "stop holding onto X",
            ],
        },
        "reset": {
            "distinctions": [
                {
                    "note": "preserve = maintain existing compatibility; reset = discard it entirely",
                    "token": "preserve",
                },
                {
                    "note": "migrate = change while keeping temporary compatibility; reset = break from prior commitments without a transition path",
                    "token": "migrate",
                },
            ],
            "heuristics": [
                "start fresh",
                "ignore existing constraints",
                "greenfield design",
                "rebuild from scratch",
                "no legacy assumptions",
                "pretend it doesn't exist yet",
                "clean slate",
                "break from the current design",
            ],
        },
        "resilience": {
            "distinctions": [
                {
                    "note": "robust = choose options that perform across uncertain futures; resilience = analyze system behavior under stress specifically",
                    "token": "robust",
                }
            ],
            "heuristics": [
                "how resilient is this",
                "what happens under load",
                "failure recovery",
                "margin of safety",
                "fragility vs robustness",
                "how does it behave under stress",
                "graceful degradation",
                "fault tolerance",
            ],
        },
        "rigor": {
            "distinctions": [
                {
                    "note": "verify = apply falsification pressure to claims; rigor = discipline the reasoning process throughout",
                    "token": "verify",
                }
            ],
            "heuristics": [
                "be rigorous",
                "make the reasoning explicit",
                "disciplined analysis",
                "careful reasoning",
                "justify each step",
                "logical rigor",
                "no handwaving",
                "substantiate your claims",
            ],
        },
        "risks": {
            "distinctions": [
                {
                    "note": "adversarial = construct attacks to stress-test; risks = enumerate and assess failure modes and their likelihood",
                    "token": "adversarial",
                }
            ],
            "heuristics": [
                "what are the risks",
                "what could go wrong",
                "risk assessment",
                "failure modes",
                "identify the hazards",
                "risk analysis",
                "what might fail",
                "enumerate the risks",
                "likelihood and severity",
            ],
        },
        "ritual": {
            "distinctions": [
                {
                    "note": "ritual = structured by established roles and procedures; melody = coordination through timing and synchronization",
                    "token": "melody",
                }
            ],
            "heuristics": [
                "follow established procedures",
                "respect the roles",
                "maintain social order",
                "proper conduct",
                "ritualized process",
                "according to tradition",
                "roles and responsibilities",
            ],
        },
        "robust": {
            "distinctions": [
                {
                    "note": "resilience = system behavior under stress; robust = select options that perform across uncertain futures",
                    "token": "resilience",
                }
            ],
            "heuristics": [
                "robust to uncertainty",
                "works across scenarios",
                "hedge against uncertainty",
                "perform across many futures",
                "uncertainty-aware decision",
                "which option survives the most scenarios",
                "resilient to unknowns",
                "option value under uncertainty",
            ],
        },
        "root": {
            "distinctions": [
                {
                    "note": "depends = trace what relies on what; root = reduce multiple representations to a single authoritative locus",
                    "token": "depends",
                },
                {
                    "note": "mapping = surface elements and relationships; root = identify or enforce the single canonical source among them",
                    "token": "mapping",
                },
            ],
            "heuristics": [
                "where is the single source of truth",
                "we have duplicate definitions",
                "which config is authoritative",
                "DRY violation",
                "multiple representations of the same thing",
                "who owns this data",
                "derive X from Y instead of duplicating",
                "canonical source for",
                "reduce duplication to derivation",
            ],
        },
        "seep": {
            "distinctions": [
                {
                    "note": "bound = introduce or reinforce propagation limits proactively; seep = identify where those limits have been violated or never existed",
                    "token": "bound",
                },
                {
                    "note": "cross (scope) = concerns spanning modules by design; seep (method) = concerns overreaching their intended scope unintentionally",
                    "token": "cross",
                },
                {
                    "note": "snag = surface where coupling seams exist; seep = identify where influence from those seams has leaked past intended scope",
                    "token": "snag",
                },
                {
                    "note": "shear/sever = install a separation; seep = audit whether the boundary is actually holding after installation",
                    "token": "sever",
                },
            ],
            "heuristics": [
                "where does this leak",
                "scope creep",
                "responsibility overreach",
                "bleeding concerns",
                "what crosses boundary lines uninvited",
                "where is influence extending too far",
                "coupling from overreach",
                "what is reaching outside its scope",
                "is the boundary actually holding",
                "did the decoupling work",
                "has coupling re-emerged through a side channel",
            ],
        },
        "sense": {
            "distinctions": [
                {
                    "note": "indirect = form that puts reasoning before the conclusion; sense = method that holds impression before decomposition, without necessarily resolving",
                    "token": "indirect",
                },
                {
                    "note": "shift = rotate through distinct perspectives; sense = hold weighted signals from the current vantage before committing to one",
                    "token": "shift",
                },
                {
                    "note": "release = loosen attachment to an outcome; sense = surface the weighted impression before it is analytically unpacked",
                    "token": "release",
                },
            ],
            "heuristics": [
                "what does this feel like",
                "what's your sense of",
                "surface your impression",
                "weighted intuition",
                "felt gradient",
                "hold the uncertainty",
                "pre-reductive judgment",
                "compressed impression",
            ],
        },
        "sever": {
            "distinctions": [
                {
                    "note": "bound = limit how far effects propagate; sever = introduce a structural separation that routes all interaction through explicit interfaces",
                    "token": "bound",
                },
                {
                    "note": "domains = identify bounded contexts; sever = introduce or reinforce separations between them",
                    "token": "domains",
                },
                {
                    "note": "snag/mesh = diagnose coupling seams; sever = address it by structural separation",
                    "token": "snag",
                },
                {
                    "note": "sever = introduce structural separation; seep = audit whether the boundary is holding after separation",
                    "token": "seep",
                },
            ],
            "heuristics": [
                "enforce domain separation",
                "make these modules independent",
                "controlled interfaces only",
                "route interactions through explicit interfaces",
                "make direct dependency structurally impossible",
                "enforce that all interaction goes through a defined interface",
                "make this separation permanent, not just a plan",
                "this needs to be architectural not just procedural",
            ],
        },
        "shear": {
            "distinctions": [
                {
                    "note": "snag = identify the coupling seams; shear = outline steps to separate them",
                    "token": "snag",
                },
                {
                    "note": "sever = restructure to introduce separations broadly; shear = targeted steps to separate or realign specific coupled domains",
                    "token": "sever",
                },
            ],
            "heuristics": [
                "how to separate these",
                "steps to decouple",
                "realign these domains",
                "outline the separation",
                "how to untangle",
                "give me a plan to pull these apart",
                "what are the steps to separate these two things",
                "give me a migration plan to decouple these",
            ],
        },
        "shift": {
            "distinctions": [
                {
                    "note": "models = apply named mental models; shift = rotate through distinct cognitive modes or stakeholder perspectives",
                    "token": "models",
                }
            ],
            "heuristics": [
                "look at this from multiple angles",
                "different perspectives",
                "rotate through lenses",
                "six thinking hats",
                "shift perspectives",
                "what would X think about this",
                "see it through different frames",
                "consider multiple viewpoints",
            ],
        },
        "simulation": {
            "distinctions": [
                {
                    "note": "sim = standalone scenario narrative of what unfolds; simulation method = enriches probe/plan with thought-experiment reasoning about feedback "
                    "loops, tipping points, and emergent system behaviour",
                    "token": "sim",
                },
                {
                    "note": "boom = scale extremes; simulation = systemic feedback dynamics",
                    "token": "boom",
                },
            ],
            "heuristics": [
                "run a thought experiment",
                "trace feedback loops",
                "where would bottlenecks emerge",
                "tipping point analysis",
                "what emergent effects would arise",
                "project systemic dynamics",
                "model how effects compound over time",
            ],
        },
        "snag": {
            "distinctions": [
                {
                    "note": "mesh = describe how coupling propagates; snag = surface where the coupling seams are",
                    "token": "mesh",
                },
                {
                    "note": "shear = outline separation steps; snag = identify the coupling seams that need separating",
                    "token": "shear",
                },
                {
                    "note": "snag = surface where the coupling seams are (where is it broken?); seep = audit whether influence has leaked past intended scope (did it work?)",
                    "token": "seep",
                },
            ],
            "heuristics": [
                "where are these coupled",
                "find the coupling seams",
                "identify coupling",
                "where is ownership unclear",
                "where are responsibilities intermixed",
                "surface the seams",
                "what can't be cleanly separated",
            ],
        },
        "split": {
            "distinctions": [
                {
                    "note": "dimension = surface analytical axes; split = decompose into component parts for provisional isolated analysis",
                    "token": "dimension",
                }
            ],
            "heuristics": [
                "break this into parts",
                "decompose",
                "analyze each component separately",
                "isolate the pieces",
                "divide and analyze",
                "separate concerns",
                "split into sub-problems",
                "analyze in isolation",
            ],
        },
        "spur": {
            "distinctions": [
                {
                    "note": "sweep = enumerate option space without forking; spur = fork on a key assumption and pursue each path before evaluating",
                    "token": "sweep",
                }
            ],
            "heuristics": [
                "explore multiple paths",
                "consider different approaches in parallel",
                "branch the reasoning",
                "multiple lines of reasoning",
                "explore alternatives before choosing",
                "parallel hypotheses",
            ],
        },
        "survive": {
            "distinctions": [
                {
                    "note": "verify = design a challenge against a claim analytically; survive = let uncontrolled environmental exposure answer whether the claim held",
                    "token": "verify",
                },
                {
                    "note": "ground = staged external derivation that earns permission to exist; survive = post-derivation environmental exposure that determines whether what "
                    "was built remains valid",
                    "token": "ground",
                },
                {
                    "note": "experimental = propose a test to challenge a claim; survive = what the uncontrolled environment actually returned",
                    "token": "experimental",
                },
            ],
            "heuristics": [
                "what survived in production",
                "does this hold under real conditions",
                "production behavior vs design intent",
                "what remained valid after deployment",
                "telemetry vs specification",
                "what happened when real users encountered it",
                "live environment as authority",
                "what did the world keep",
            ],
        },
        "sweep": {
            "distinctions": [
                {
                    "note": "spur = fork on a key assumption and pursue paths; sweep = broad enumeration without forking on a specific choice",
                    "token": "spur",
                }
            ],
            "heuristics": [
                "what are the options",
                "explore the solution space",
                "what approaches exist",
                "brainstorm possibilities",
                "what could we do",
                "survey the landscape",
                "open-ended exploration",
                "what's possible here",
            ],
        },
        "systemic": {
            "distinctions": [
                {
                    "note": "analysis = describe and structure; systemic = reason about interactions and emergence",
                    "token": "analysis",
                }
            ],
            "heuristics": [
                "systems thinking",
                "feedback loops",
                "emergent behavior",
                "system as a whole",
                "how do the parts interact",
                "unintended consequences",
                "second order effects across the system",
                "interconnections",
            ],
        },
        "thrust": {
            "distinctions": [
                {
                    "note": "balance = acceptable equilibrium state between opposing forces; thrust = identify and catalog the competing forces themselves",
                    "token": "balance",
                }
            ],
            "heuristics": [
                "what are the trade-offs",
                "weigh the options",
                "competing forces",
                "design trade-offs",
                "pros and cons of each approach",
                "alternative configurations",
                "what are we trading off",
                "evaluate alternatives across dimensions",
            ],
        },
        "trace": {
            "distinctions": [
                {
                    "note": "flow = describe linear ordering of stages; trace = narrate the sequential control/data progression with intermediate steps",
                    "token": "flow",
                },
                {
                    "note": "mint = make generative assumptions explicit for derivability; trace = narrate the sequential progression for observability",
                    "token": "mint",
                },
            ],
            "heuristics": [
                "show your work",
                "make intermediate steps visible",
                "how did we get here",
                "make the process traceable",
                "show each decision",
                "observable execution",
                "audit the steps",
                "I want to follow along",
                "surface intermediate state",
            ],
        },
        "unknowns": {
            "distinctions": [
                {
                    "note": "assume (scope) = restrict analysis to the premises domain; unknowns (method) = surface what has not yet been considered or named",
                    "token": "assume",
                }
            ],
            "heuristics": [
                "what are we missing",
                "what don't we know that we don't know",
                "unknown unknowns",
                "what questions haven't we asked",
                "critical blind spots",
                "what's not on our radar",
                "gaps in our knowledge",
                "what could surprise us",
            ],
        },
        "verify": {
            "distinctions": [
                {
                    "note": "rigor = disciplined reasoning process; verify = apply explicit falsification to the outputs",
                    "token": "rigor",
                },
                {
                    "note": "ground = define a falsifiable artifact before producing output, imposing I → V → O structure; verify = apply falsification pressure to claims after "
                    "the fact without imposing a governing structure",
                    "token": "ground",
                },
            ],
            "heuristics": [
                "verify this",
                "check your reasoning",
                "apply falsification",
                "is this actually true",
                "challenge the claims",
                "what would falsify this",
                "pressure-test the conclusions",
                "don't just assert — verify",
                "what evidence would disprove this",
            ],
        },
        "visual": {
            "distinctions": [
                {
                    "note": "draw (channel) = deliver the output as ASCII spatial layout; visual (method) = frame ideas spatially regardless of output format",
                    "token": "draw",
                },
                {
                    "note": "diagram (channel) = Mermaid code output; visual (method) = spatial framing that can be expressed in any output format",
                    "token": "diagram",
                },
                {
                    "note": "analog (method) = reason through a structural mapping from a specific known case; visual (method) = frame ideas in spatial/positional terms without "
                    "requiring a parallel case",
                    "token": "analog",
                },
            ],
            "heuristics": [
                "think spatially",
                "spatial framing",
                "place these concepts in space",
                "frame this as a coordinate space",
                "conceptual layout",
                "big-picture structure",
                "map this out conceptually",
                "visual mental model",
                "frame this as a landscape",
            ],
        },
        "yield": {
            "distinctions": [
                {
                    "note": "yield = allow natural resolution with minimal guidance; preserve = maintain compatibility with existing structures",
                    "token": "preserve",
                }
            ],
            "heuristics": [
                "let it resolve naturally",
                "minimal intervention",
                "allow organic resolution",
                "wu wei",
                "don't force it",
                "step back and let it unfold",
                "guide without imposing",
            ],
        },
    },
    "scope": {
        "act": {
            "distinctions": [
                {
                    "note": "act = what entities are doing or performing; thing = what entities exist",
                    "token": "thing",
                }
            ],
            "heuristics": [
                "what actions",
                "what operations are involved",
                "what tasks are performed",
                "what does it actually do",
                "what work is happening",
                "what are the intended operations",
                "the activities it performs",
            ],
        },
        "agent": {
            "distinctions": [
                {
                    "note": "agent = who has decision-making authority; view = how the subject appears from a specific vantage point",
                    "token": "view",
                }
            ],
            "heuristics": [
                "who decides",
                "who has authority",
                "who can approve",
                "decision-making",
                "agency",
                "who is responsible",
            ],
        },
        "assume": {
            "distinctions": [],
            "heuristics": [
                "what assumptions",
                "what are we assuming",
                "what must be true",
                "what preconditions",
                "hidden assumptions",
                "what are we taking for granted",
            ],
        },
        "cross": {
            "distinctions": [
                {
                    "note": "cross = concerns that propagate and span across module boundaries; motifs = structural patterns that repeat",
                    "token": "motifs",
                },
                {
                    "note": "cross = horizontal span across module boundaries; struct = internal topology and arrangement within units",
                    "token": "struct",
                },
            ],
            "heuristics": [
                "scattered across",
                "spans multiple services",
                "consistent across",
                "cross-cutting",
                "appears throughout",
                "horizontal concern",
                "error handling across our codebase",
                "where does X live across the system",
            ],
        },
        "dam": {
            "distinctions": [
                {
                    "note": "dam = containment boundaries describing what stays in/out; bound (method) = introducing or reinforcing limits on propagation",
                    "token": "bound",
                }
            ],
            "heuristics": [
                "what stays in scope",
                "what is kept out",
                "boundaries",
                "containment",
                "what's inside vs outside",
                "scope limits",
                "what belongs in this domain",
                "what's excluded",
                "where do we draw the line",
            ],
        },
        "fail": {
            "distinctions": [
                {
                    "note": "fail = scope of breakdown conditions; good = quality criteria and success standards (often paired)",
                    "token": "good",
                }
            ],
            "heuristics": [
                "failure modes",
                "where does it break",
                "what are the edge cases",
                "what can go wrong",
                "under what conditions does it fail",
                "limits",
                "fragility",
                "what stress would break this",
            ],
        },
        "good": {
            "distinctions": [
                {
                    "note": "good = quality and success standards; fail = breakdown conditions (often paired together)",
                    "token": "fail",
                },
                {
                    "note": "good = how to judge quality; mean = conceptual framing before evaluation",
                    "token": "mean",
                },
            ],
            "heuristics": [
                "quality criteria",
                "what makes it good",
                "how to judge",
                "success criteria",
                "well-designed",
                "what good looks like",
                "standards for",
                "what does success look like",
            ],
        },
        "mean": {
            "distinctions": [
                {
                    "note": "mean = conceptual framing before evaluation; good = how to judge quality",
                    "token": "good",
                }
            ],
            "heuristics": [
                "what does X mean",
                "how should I think about",
                "what is the purpose of",
                "how is this concept defined",
                "how is this categorized",
                "what does this term refer to",
                "how do we conceptualize this",
                "theoretical framing",
            ],
        },
        "motifs": {
            "distinctions": [
                {
                    "note": "motifs = patterns that repeat across the system; struct = one system's internal arrangement",
                    "token": "struct",
                },
                {
                    "note": "motifs = structural patterns that repeat; cross = concerns that propagate and span across module boundaries",
                    "token": "cross",
                },
            ],
            "heuristics": [
                "recurring patterns",
                "repeated across",
                "appears in multiple places",
                "common idioms",
                "what keeps showing up",
                "same pattern in different places",
            ],
        },
        "stable": {
            "distinctions": [
                {
                    "note": "stable = what persists; time = how things evolve (often paired)",
                    "token": "time",
                },
                {
                    "note": "stable = descriptive (what already persists or is invariant); storage = prescriptive (what must be made durable)",
                    "token": "storage",
                },
            ],
            "heuristics": [
                "stable",
                "unlikely to change",
                "won't change",
                "what persists",
                "what is settled",
                "fixed constraints",
                "what has remained stable",
                "backward-compatible",
            ],
        },
        "storage": {
            "distinctions": [
                {
                    "note": "storage = prescriptive (what must be made durable and how); stable = descriptive (what currently persists or is invariant)",
                    "token": "stable",
                },
                {
                    "note": "storage = what survives and in what form; time = temporal sequence and change",
                    "token": "time",
                },
            ],
            "heuristics": [
                "where does this get saved",
                "what persists after the operation",
                "durability requirements",
                "what must survive a restart",
                "storage medium",
                "data persistence",
                "recovery guarantees",
                "what gets written to disk",
                "durable state",
                "persistence layer",
            ],
        },
        "struct": {
            "distinctions": [
                {
                    "note": "struct = internal topology and arrangement within units; cross = horizontal span across module boundaries",
                    "token": "cross",
                }
            ],
            "heuristics": [
                "how is it structured",
                "what are the dependencies",
                "how are the components organized",
                "internal architecture",
                "how do the parts relate",
                "what holds it together",
                "the coordination and constraints inside",
            ],
        },
        "thing": {
            "distinctions": [
                {
                    "note": "thing = what entities exist; act = what those entities are doing or performing",
                    "token": "act",
                }
            ],
            "heuristics": [
                "what entities",
                "what are the main objects",
                "what roles are involved",
                "what systems are in scope",
                "what are the bounded domains",
                "what things exist here",
                "name the components",
                "what are we talking about",
            ],
        },
        "time": {
            "distinctions": [
                {
                    "note": "time = how things evolve; stable = what persists (often paired)",
                    "token": "stable",
                }
            ],
            "heuristics": [
                "step by step",
                "in order",
                "over time",
                "what happens when",
                "sequence",
                "timeline",
                "history",
                "how did we get here",
                "phases",
            ],
        },
        "view": {
            "distinctions": [
                {
                    "note": "view = how the subject appears from a specific vantage point; agent = who has decision-making authority",
                    "token": "agent",
                }
            ],
            "heuristics": [
                "from the user's perspective",
                "from the manager's point of view",
                "how does the team see this",
                "from a security perspective",
                "how does this look to stakeholders",
                "from a customer's view",
                "through the lens of",
            ],
        },
    },
}


def axis_token_metadata() -> dict[str, dict[str, AxisTokenMetadata]]:
    """Return structured metadata for axis tokens (ADR-0155).

    'definition' is not stored in AXIS_TOKEN_METADATA — it is derived here from
    AXIS_KEY_TO_VALUE so callers receive a complete entry without duplicate storage.
    """
    result = {}
    for axis, tokens in AXIS_TOKEN_METADATA.items():
        result[axis] = {}
        value_map = AXIS_KEY_TO_VALUE.get(axis, {})
        for token, meta in tokens.items():
            entry = dict(meta)
            if token in value_map:
                entry["definition"] = value_map[token]
            result[axis][token] = entry
    return result
