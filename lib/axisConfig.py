"""Axis configuration as static Python maps (token -> description).

Generated from the axis registry; keep in sync with list edits.

SYNC_WARNING: Changes to token names/descriptions affect:
- internal/barcli/help_llm.go (hardcoded heuristics and usage patterns)
- .opencode/skills/bar-workflow/skill.md (method categorization)
- internal/barcli/help_llm_test.go (validation tests)

When renaming/removing tokens:
1. Update help_llm.go hardcoded references
2. Update skill.md if method categories change
3. Run `go test ./internal/barcli/ -run TestLLMHelp` to validate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, Union

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "The response takes the shape of an Architecture Decision Record (ADR) document with sections for context, decision, and consequences, formatted as a structured document ready "
        "for version control.",
        "code": "The response consists only of code or markup as the complete output, with no surrounding natural-language explanation or narrative.",
        "codetour": "The response is delivered as a valid VS Code CodeTour `.tour` JSON file (schema-compatible) with steps and fields appropriate to the task, omitting extra prose or "
        "surrounding explanation.",
        "diagram": "The response converts the input into Mermaid diagram code only: it infers the best diagram type for the task and respects Mermaid safety constraints (Mermaid diagrams do not "
        "allow parentheses in the syntax or raw '|' characters inside node labels; the text uses numeric encodings such as \"#124;\" for '|' instead of raw problematic characters).",
        "gherkin": "The response outputs only Gherkin format as the complete output, using Jira markup where appropriate and omitting surrounding explanation. Works with presenterm/diagram "
        "channels when wrapped in markdown code blocks.",
        "html": "The response consists solely of semantic HTML as the complete output, with no surrounding prose or explanation.",
        "jira": "The response formats the content using Jira markup (headings, lists, panels) where relevant and avoids extra explanation beyond the main material.",
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
        "svg": "The response consists solely of SVG markup as the complete output, with no surrounding prose, remaining minimal and valid for direct use in an `.svg` file.",
        "sync": "The response takes the shape of a synchronous or live session plan (agenda, steps, cues) rather than static reference text.",
    },
    "completeness": {
        "deep": "The response goes into substantial depth within the chosen scope, unpacking reasoning layers and fine details without necessarily enumerating every edge case.",
        "full": "The response provides a thorough answer for normal use, covering all major aspects without needing every micro-detail.",
        "gist": "The response offers a short but complete answer or summary that touches the main points once without exploring every detail.",
        "max": "The response is as exhaustive as reasonable, covering essentially everything relevant and treating omissions as errors.",
        "minimal": "The response makes the smallest change or provides the smallest answer that satisfies the request, avoiding work outside the core need.",
        "narrow": "The response restricts the discussion to a very small slice of the topic, avoiding broad context.",
        "skim": "The response performs only a very light pass, addressing the most obvious or critical issues without aiming for completeness.",
    },
    "directional": {
        "bog": "The response modifies the task to span both the reflective/structural dimension (rog) and the acting/extending dimension (ong) — examining the structure and its implications "
        "while also identifying concrete actions and extensions that follow.",
        "dig": "The response modifies the task to examine concrete details and grounding examples, focusing on specifics rather than abstractions.",
        "dip bog": "The response modifies the task to start with concrete examples and grounded details, examines their structure and reflects on patterns, then identify actions and "
        "extensions.",
        "dip ong": "The response modifies the task to start with concrete examples, identify actions to take from them, then extends those actions to related situations.",
        "dip rog": "The response modifies the task to examine concrete details and grounded examples, then reflects on their structural patterns and what they reveal.",
        "fig": "The response modifies the task to span both the abstract/general dimension (fog) and the concrete/specific dimension (dig) — addressing the underlying principles and the "
        "grounded specifics, using each to illuminate the other (figure-ground reversal).",
        "fip bog": "The response modifies the task to move between abstract principles and concrete examples, examines their structural patterns and reflects on them, then identifies "
        "actions and extends them to related contexts.",
        "fip ong": "The response modifies the task to alternate between abstract principles and concrete examples, then identifies actions to take and extends them to related situations.",
        "fip rog": "The response modifies the task to move between abstract principles and concrete examples while examining structural patterns and reflecting on what they reveal.",
        "fly bog": "The response modifies the task to identify abstract patterns and general principles, examine their structure and reflects on it, then identifies actions and extends them "
        "to related contexts.",
        "fly ong": "The response modifies the task to identify abstract patterns and general principles, then propose concrete actions and extends them to related contexts.",
        "fly rog": "The response modifies the task to identify abstract patterns and general principles, then examines their structural relationships and reflect on their implications.",
        "fog": "The response modifies the task to identify general patterns and abstract principles from the specifics, moving from particular cases to broader insights.",
        "jog": "The response modifies the task to interpret the intent and carry it out directly without asking follow-up questions.",
        "ong": "The response modifies the task to identify concrete actions to take, then extends those actions to related situations or next steps.",
        "rog": "The response modifies the task to examine the structure of the subject (how it is organized), then reflects on why that structure exists and what it reveals.",
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
        "output-exclusive channel, conducts this interactively: proposes, pauses for feedback, and iterates. With an output-exclusive channel, formats the artifact to expose decision "
        "points, show alternative moves, and make the response-inviting structure visible within the output.",
        "commit": "The response structures ideas as a conventional commit message with a short type or scope line and an optional concise body.",
        "contextualise": "The response packages the subject to be passed directly to another LLM operation: it enriches the content with all context a downstream model would need to act on it "
        "without further explanation — adding background, assumptions, constraints, and framing that would otherwise be implicit or missing. The main content is not rewritten. "
        "With pull: wraps extracted content with the context needed to interpret it. With make/fix: accompanies the output with purpose, constraints, and framing so the downstream "
        "model understands how to use it.",
        "direct": "The response structures ideas by leading with the main point or recommendation, followed only by the most relevant supporting context, evidence, and next steps.",
        "facilitate": "The response structures itself as a facilitation plan — framing the goal, proposing session structure, managing participation and turn-taking rather than doing the work "
        "solo. Without an output-exclusive channel, acts as a live facilitator: proposes structure and invites participation interactively. With an output-exclusive channel, produces "
        "a static facilitation guide: agenda, goals, cues, and session structure as a deliverable artifact.",
        "faq": "The response organizes ideas as clearly separated question headings with concise answers beneath each one, keeping content easy to skim and free of long uninterrupted prose.",
        "formats": "The response structures ideas by focusing on document types, writing formats, or structural templates and their suitability.",
        "indirect": "The response begins with brief background, reasoning, and trade-offs and finishes with a clear bottom-line point or recommendation that ties them together.",
        "ladder": "The response uses abstraction laddering by placing the focal problem, stepping up to higher-level causes, and stepping down to consequences ordered by importance to the "
        "audience.",
        "log": "The response reads like a concise work or research log entry with date or time markers as needed, short bullet-style updates, and enough context for future reference without "
        "unrelated narrative.",
        "merge": "The response combines multiple sources into a single coherent whole while preserving essential information.",
        "questions": "The response presents the answer as a series of probing or clarifying questions rather than statements. When combined with `diagram` channel, the output is Mermaid code "
        "structured as a question tree, decision map, or inquiry flow rather than a structural diagram of the subject.",
        "quiz": "The response organizes content as a quiz structure — questions posed before explanations, testing understanding through active recall before providing answers. Without an "
        "output-exclusive channel, conducts this as an interactive exchange: poses questions, waits for responses, then clarifies or deepens. With an output-exclusive channel, structures "
        "the output itself as a quiz — question headings with revealed answers, test sections, knowledge checks — without requiring live interaction.",
        "recipe": "The response expresses the answer as a recipe that includes a custom, clearly explained mini-language and a short key for understanding it.",
        "scaffold": "The response explains with scaffolding: it starts from first principles, introduces ideas gradually, uses concrete examples and analogies, and revisits key points so a learner "
        "can follow and retain the concepts. Most effective with learning-oriented audiences (student, entry-level engineer). May conflict with expert-level or brevity-first personas "
        "where first-principles exposition contradicts assumed expertise.",
        "socratic": "The response employs a Socratic, question-led method by asking short, targeted questions that surface assumptions, definitions, and gaps in understanding, withholding full "
        "conclusions until enough answers exist or the user explicitly requests a summary. With sort/plan: asks clarifying questions about criteria before producing output. With "
        "make/fix: asks diagnostic questions then provides the solution. With probe: naturally extends to deeper inquiry.",
        "spike": "The response formats the backlog item as a research spike: it starts with a brief problem or decision statement, lists the key questions the spike should answer, and stays "
        "focused on questions and learning rather than implementation tasks.",
        "story": 'The response formats the backlog item as a user story using "As a <persona>, I want <capability>, so that <value>." It may include a short description and high-level acceptance '
        "criteria in plain prose but avoids Gherkin or test-case syntax.",
        "table": "The response presents the main answer as a Markdown table when feasible, keeping columns and rows compact.",
        "taxonomy": "The response organizes the main content as a classification system, type hierarchy, or category taxonomy, defining types, their relationships, and distinguishing attributes "
        "clearly. Adapts to the channel: when combined with a code channel, the taxonomy is expressed through the type system (interfaces, enums, inheritance hierarchies); with a "
        "markup channel, as hierarchical markup structure; without a channel, as prose classification sections.",
        "test": "The response presents test cases in a structured format with clear setup, execution, and assertion sections, organized by scenario type (happy path, edge cases, errors, "
        "boundaries) and including descriptive test names.",
        "tight": "The response uses concise, dense prose, remaining freeform without bullets, tables, or code and avoiding filler.",
        "variants": "The response presents several distinct, decision-ready options as separate variants, labelling each one with a short description and including approximate probabilities when "
        "helpful while avoiding near-duplicate alternatives.",
        "visual": "The response presents the main answer as an abstract visual or metaphorical layout with a short legend where the subject lends itself to visual representation, emphasising "
        "big-picture structure over dense prose. Adapts to the channel: when combined with a code channel, visual structure is expressed through code organization, comments, or inline "
        "ASCII; without a channel, through prose metaphors and spatial layout.",
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
        "analog": "The response enhances the task by reasoning through analogy, mapping relational structure from a known case onto the subject and examining where the analogy holds or breaks.",
        "analysis": "The response enhances the task by decomposing the subject into its constituent components and examining each for its role, properties, and interactions—without imposing a "
        "specific organizing principle such as spatial layout, dependency chains, groupings, hierarchies, historical causation, or governing criteria.",
        "argue": "The response enhances the task by structuring reasoning as an explicit argument, identifying claims, premises, warrants, and rebuttals and assessing their support.",
        "balance": "The response models outcomes as the result of balancing forces within a system. Claims of stability, persistence, or dominance must identify opposing pressures, incentives, "
        "or constraints and show how they offset one another. The analysis must distinguish transient states from equilibria by specifying restoring or destabilizing dynamics under "
        "perturbation. No configuration may be treated as stable without explaining why countervailing forces fail to overturn it.",
        "bias": "The response enhances the task by identifying likely cognitive biases, heuristics, or systematic errors and examining how they might distort judgment or conclusions.",
        "boom": "The response enhances the task by exploring behaviour toward extremes of scale or intensity, examining what breaks, dominates, or vanishes.",
        "bound": "The response constrains how state changes, effects, or responsibilities propagate through the system, deliberately limiting the surface area and reach of influence.",
        "branch": "The response enhances the task by exploring multiple reasoning paths in parallel, branching on key assumptions or choices before evaluating and pruning alternatives.",
        "calc": "The response enhances the task by expressing reasoning as executable or quasi-executable procedures, calculations, or formal steps whose outputs constrain conclusions.",
        "canon": "The response models each proposition, rule, or dependency as having a single authoritative locus within the explanatory structure. Apparent duplication must be reduced to "
        "derivation from a canonical source, and parallel accounts must be explicitly mapped or unified. Explanations may not treat multiple representations of the same knowledge as "
        "independent causal or justificatory elements without specifying their dependency relationship.",
        "cite": "The response enhances the task by including sources, citations, or references that anchor claims to evidence, enabling verification and further exploration.",
        "cluster": "The response groups or organizes existing items into clusters based on shared characteristics, relationships, or criteria, without altering the underlying content or meaning "
        "of the items.",
        "compare": "The response enhances the task by systematically comparing alternatives against explicit criteria, surfacing tradeoffs, relative strengths and weaknesses, and decision "
        "factors. Use when the user presents options and asks which to choose or how they differ.",
        "converge": "The response enhances the task by systematically narrowing from broad exploration to focused recommendations, weighing trade-offs explicitly as options are filtered.",
        "deduce": "The response enhances the task by applying deductive reasoning, deriving conclusions that must follow from stated premises or assumptions and making logical entailment "
        "explicit.",
        "depends": "The response enhances the task by tracing dependency relationships, identifying what depends on what and how changes propagate through the system.",
        "diagnose": "The response enhances the task by seeking likely causes of problems first, narrowing hypotheses through evidence, falsification pressure, and targeted checks before "
        "proposing fixes or changes.",
        "dimension": "The response enhances the task by exploring multiple dimensions or axes of analysis, making implicit factors explicit and examining how they interact.",
        "domains": "The response enhances the task by identifying bounded contexts, domain boundaries, and capabilities.",
        "effects": "The response enhances the task by tracing second- and third-order effects and summarizing their downstream consequences.",
        "experimental": "The response enhances the task by proposing concrete experiments or tests, outlining how each would run, describing expected outcomes, and explaining how results would "
        "update the hypotheses.",
        "explore": "The response enhances the task by opening and surveying the option space, generating and comparing multiple plausible approaches without prematurely committing to a single "
        "answer.",
        "field": "The response models interaction as occurring through a shared structured medium in which effects arise from structural compatibility rather than direct reference between "
        "actors. Explanations must make the medium and its selection rules explicit.",
        "flow": "The response enhances the task by explaining step-by-step progression over time or sequence, showing how control, data, or narrative moves through the system.",
        "gap": "The response enhances the task by identifying where assumptions, rules, roles, or relationships are treated as explicit but remain implicit, analyzing how that mismatch produces "
        "ambiguity, coordination failure, or error.",
        "grove": "The response enhances the task by examining how small effects compound into larger outcomes through feedback loops, network effects, or iterative growth—asking not just what "
        "fails or succeeds, but how failures OR successes accumulate through systemic mechanisms.",
        "grow": "The response enhances the task by preserving the simplest form adequate to the current purpose and expanding only when new demands demonstrably outgrow it, so that every "
        "abstraction and every exception arises from necessity rather than anticipation.",
        "induce": "The response enhances the task by applying inductive reasoning, generalizing patterns from specific observations and assessing the strength and limits of those "
        "generalizations.",
        "inversion": "The response enhances the task by beginning from undesirable or catastrophic outcomes, asking what would produce or amplify them, then working backward to avoid, mitigate, "
        "or design around those paths.",
        "jobs": "The response enhances the task by analyzing Jobs To Be Done—the outcomes users want to achieve and the forces shaping their choices.",
        "mapping": "The response enhances the task by surfacing elements, relationships, and structure, then organising them into a coherent spatial map rather than a linear narrative.",
        "meld": "The response enhances the task by reasoning about combinations, overlaps, balances, and constraints between elements.",
        "melody": "The response enhances the task by analyzing coordination across components, time, or teams, including coupling, synchronization, and change alignment.",
        "mod": "The response enhances the task by applying modulo-style reasoning—equivalence classes, cyclic patterns, quotient structures, or periodic behavior that repeats with a defined "
        "period or wraps around boundaries.",
        "models": "The response enhances the task by explicitly identifying and naming relevant mental models, explaining why they apply (or fail), and comparing or combining them.",
        "objectivity": "The response enhances the task by distinguishing objective facts from subjective opinions and supporting claims with evidence.",
        "operations": "The response enhances the task by identifying operations research or management science concepts that frame the situation.",
        "order": "The response enhances the task by applying abstract structural reasoning such as hierarchy, dominance, or recurrence. When paired with `sort` task, `order` adds emphasis on the "
        "criteria and scheme driving the sequencing rather than merely producing the sorted result — consider whether the distinction is needed.",
        "origin": "The response enhances the task by uncovering how the subject arose, why it looks this way now, and how past decisions shaped the present state.",
        "polar": "The response models behavior or system dynamics as shaped by both attractors (desired or rewarded states) and repellers (avoided or penalized states). Explanations must "
        "distinguish pursuit from avoidance, account for how negative boundaries constrain trajectories, and specify whether outcomes arise from optimization toward a goal or evasion of "
        "an undesirable state. Outcomes may not be attributed solely to positive objectives without modeling active avoidance pressures.",
        "prioritize": "The response enhances the task by assessing and ordering items by importance or impact, making the ranking and rationale explicit.",
        "probability": "The response enhances the task by applying probability or statistical reasoning to characterize uncertainty and likely outcomes.",
        "product": "The response enhances the task by examining the subject through a product lens—features, user needs, and value propositions.",
        "reify": "The response enhances the task by identifying implicit patterns, assumptions, or relationships and making them explicit as formal entities, distinctions, or rules that "
        "constrain reasoning.",
        "resilience": "The response enhances the task by concentrating on how the system behaves under stress and uncertainty—fragility vs robustness, margin of safety, and tail risks.",
        "rigor": "The response enhances the task by relying on disciplined, well-justified reasoning and making its logic explicit.",
        "risks": "The response enhances the task by focusing on potential problems, failure modes, or negative outcomes and their likelihood or severity.",
        "robust": "The response enhances the task by reasoning under deep uncertainty, favoring options that perform acceptably across many plausible futures rather than optimizing for a single "
        "forecast.",
        "shift": "The response enhances the task by deliberately rotating through distinct perspectives or cognitive modes, contrasting how each frame interprets the same facts.",
        "simulation": "The response enhances the task by focusing on explicit thought experiments or scenario walkthroughs that project evolution over time, highlighting feedback loops, "
        "bottlenecks, tipping points, and emergent effects.",
        "spec": "The response maintains an explicit and independent layer of governing criteria, constraints, or rules that remain authoritative over implementation. Actions or constructions "
        "must be justified against this governing layer and may not redefine it during execution.",
        "split": "The response enhances the task by deliberately decomposing the subject into parts or components, analyzing each in isolation while intentionally bracketing interactions, "
        "treating the decomposition as provisional and preparatory rather than final.",
        "systemic": "The response enhances the task by reasoning about the subject as an interacting whole, identifying components, boundaries, flows, feedback loops, and emergent behaviour that "
        "arise from their interactions rather than from parts in isolation.",
        "trade": "The response enhances the task by identifying competing structural forces or design pressures, making their tradeoffs explicit, and evaluating alternatives across those "
        "dimensions before committing to a configuration.",
        "trans": "The response models information transfer as a staged process involving a source, encoding, channel, decoding, destination, and feedback. Explanations must distinguish message "
        "from signal, account for transformation across stages, model noise or distortion explicitly, and specify mechanisms for detecting and repairing transmission errors. Outcomes "
        "may not be attributed to communication without specifying how the signal survived, degraded, or was corrected during transmission.",
        "triage": "The response enhances the task by differentiating system areas by consequence magnitude and uncertainty, and allocating analytical depth proportionally to those gradients.",
        "unknowns": "The response enhances the task by identifying critical unknown unknowns and exploring how they might impact outcomes.",
        "verify": "The response enhances the task by applying falsification pressure to claims, requiring causal chain integrity, externally imposed constraints, and explicitly defined negative "
        "space. Claims that fail any axis are treated as ungrounded and must not be synthesized into conclusions or recommendations, ensuring outputs do not transfer authority or imply "
        "trust beyond the model. This prevents internally coherent but unconstrained narratives and preserves human oversight as the source of judgment.",
    },
    "scope": {
        "act": "The response focuses on what is being done or intended—tasks, activities, operations, or work to be performed—suppressing interpretation, evaluation, structural explanation, or "
        "perspective-shifting.",
        "agent": "The response explains outcomes in terms of identifiable actors with the capacity to select among alternatives, specifying who can act, what options are available, and how their "
        "choices influence results, rather than attributing outcomes solely to impersonal structure or equilibrium dynamics.",
        "assume": "The response focuses on explicit or implicit premises that must hold for the reasoning, system, or argument to function.",
        "cross": "The response focuses on concerns or forces that propagate across otherwise distinct units, layers, or domains—examining how they traverse boundaries or become distributed across "
        "partitions—without primarily analyzing internal arrangement or recurring structural form.",
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
        "gherkin": "Gherkin scenario format",
        "html": "Semantic HTML only, no prose",
        "jira": "Jira markup formatting",
        "plain": "Plain prose, no structural decoration",
        "presenterm": "Presenterm slide deck",
        "remote": "Optimized for remote delivery",
        "shellscript": "Shell script format",
        "sketch": "D2 diagram source only",
        "slack": "Slack-formatted Markdown",
        "svg": "SVG markup only",
        "sync": "Synchronous session plan",
    },
    "completeness": {
        "deep": "Substantial depth within scope",
        "full": "Thorough, all major aspects",
        "gist": "Brief but complete summary",
        "max": "Exhaustive, treat omissions as errors",
        "minimal": "Smallest satisfying answer only",
        "narrow": "Restricted to a very small slice",
        "skim": "Light pass, obvious issues only",
    },
    "directional": {
        "bog": "Span reflection and action (rog + ong)",
        "dig": "Ground in concrete details",
        "dip bog": "Concrete-first, then span reflection and action",
        "dip ong": "Concrete-first, then act and extend",
        "dip rog": "Concrete-first, then reflect on structure",
        "fig": "Span abstract and concrete (fog + dig)",
        "fip bog": "Full spectrum: abstract+concrete, then reflection+action",
        "fip ong": "Full spectrum: abstract+concrete, then act and extend",
        "fip rog": "Full spectrum: abstract+concrete, then reflect on structure",
        "fly bog": "Abstract-first, then span reflection and action",
        "fly ong": "Abstract-first, then act and extend",
        "fly rog": "Abstract-first, then reflect on structure",
        "fog": "Surface abstract patterns and principles",
        "jog": "Execute intent directly, no clarification",
        "ong": "Identify concrete actions, extend outward",
        "rog": "Examine structure, then reflect outward",
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
        "direct": "Lead with main point first",
        "facilitate": "Facilitation plan and session structure",
        "faq": "Question-and-answer format",
        "formats": "Document types and writing formats",
        "indirect": "Background first, conclusion last",
        "ladder": "Abstraction ladder up and down",
        "log": "Work or research log entry",
        "merge": "Combine multiple sources coherently",
        "questions": "Answer as probing questions",
        "quiz": "Quiz structure, questions before answers",
        "recipe": "Recipe with ingredients and steps",
        "scaffold": "First-principles scaffolded explanation",
        "socratic": "Question-led Socratic dialogue",
        "spike": "Research spike backlog item",
        "story": "User story format",
        "table": "Markdown table presentation",
        "taxonomy": "Classification or type hierarchy",
        "test": "Structured test cases",
        "tight": "Concise dense prose",
        "variants": "Several distinct labeled options",
        "visual": "Abstract visual or metaphorical layout",
        "walkthrough": "Step-by-step guided walkthrough",
        "wardley": "Wardley map",
        "wasinawa": "What–So What–Now What reflection",
    },
    "method": {
        "abduce": "Generate explanatory hypotheses",
        "actors": "Center people, roles, and agents",
        "adversarial": "Constructive stress-testing",
        "afford": "Affordance-driven behavior analysis",
        "analog": "Reasoning by analogy",
        "analysis": "Describe and structure the situation",
        "argue": "Explicit argument structure",
        "balance": "Balance analysis: forces and trade-offs",
        "bias": "Identify cognitive biases",
        "boom": "Explore behavior at extremes of scale",
        "bound": "Constrain propagation",
        "branch": "Parallel reasoning paths",
        "calc": "Quantitative or executable reasoning",
        "canon": "Reduce multiple representations to a single authoritative source",
        "cite": "Include sources and references",
        "cluster": "Group items by shared characteristics",
        "compare": "Compare alternatives against criteria",
        "converge": "Narrow from broad to focused",
        "deduce": "Deductive logical reasoning",
        "depends": "Trace dependency relationships",
        "diagnose": "Identify likely root causes",
        "dimension": "Explore multiple analytical axes",
        "domains": "Identify bounded contexts",
        "effects": "Trace second and third-order effects",
        "experimental": "Propose concrete experiments",
        "explore": "Survey option space broadly",
        "field": "Model interaction as a shared structured medium",
        "flow": "Step-by-step sequential progression",
        "gap": "Implicit-to-explicit gap analysis",
        "grove": "Accumulation and rate-of-change effects",
        "grow": "Build up from simplest valid base",
        "induce": "Generalize patterns from examples",
        "inversion": "Reason from catastrophic outcomes back",
        "jobs": "Jobs-to-be-done analysis",
        "mapping": "Surface elements and relationships",
        "meld": "Explore combinations and overlaps",
        "melody": "Coordination across components or time",
        "mod": "Equivalence classes and cyclic reasoning",
        "models": "Apply named mental models explicitly",
        "objectivity": "Separate facts from opinions",
        "operations": "Operations research frameworks",
        "order": "Abstract structural and ordering reasoning",
        "origin": "Uncover how the subject arose",
        "polar": "Attractor-repeller dynamics analysis",
        "prioritize": "Rank items by importance or impact",
        "probability": "Probabilistic and statistical reasoning",
        "product": "Product lens — features, users, value",
        "reify": "Make implicit patterns explicit as rules",
        "resilience": "Behavior under stress and recovery",
        "rigor": "Disciplined, well-justified reasoning",
        "risks": "Potential problems and failure modes",
        "robust": "Reason under deep uncertainty",
        "shift": "Rotate through distinct perspectives",
        "simulation": "Thought experiments and scenario walkthroughs",
        "spec": "Define correctness criteria first",
        "split": "Decompose into parts or components",
        "systemic": "Interacting whole and feedback loops",
        "trade": "Trade-off analysis across competing forces",
        "trans": "Information transfer model with noise and feedback",
        "triage": "Triage by consequence×uncertainty gradient",
        "unknowns": "Surface critical unknown unknowns",
        "verify": "Apply falsification pressure to claims",
    },
    "scope": {
        "act": "Tasks and intended actions",
        "agent": "Actors with agency and decision-making",
        "assume": "Premises and preconditions",
        "cross": "Cross-cutting concerns spanning modules",
        "fail": "Breakdowns and failure modes",
        "good": "Quality criteria and success standards",
        "mean": "Conceptual meaning and framing",
        "motifs": "Recurring patterns and themes",
        "stable": "Stability and persistence of states",
        "struct": "Arrangement and relationships",
        "thing": "Entities and bounded units",
        "time": "Sequences and temporal change",
        "view": "Stakeholder perspective",
    },
}

# Selection guidance for tokens where the description alone is ambiguous or
# where naming traps exist (ADR-0110). Not all tokens need this.
# Distinct from hard incompatibilities in hierarchy.incompatibilities.
AXIS_KEY_TO_GUIDANCE: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "Task-affinity for decision-making tasks (plan, probe, make). The ADR format (Context, Decision, Consequences) is a decision artifact — it does not accommodate tasks that produce "
        "non-decision outputs. Avoid with sort (sorted list), pull (extraction), diff (comparison), or sim (scenario playback). Exception: when a structural form token (e.g., ladder, "
        "case) is also present, it may act as a content lens that reframes the task as a decision-adjacent structure (e.g., pull+ladder+adr = a hierarchical extraction organized as an "
        "ADR) — coherence depends on the subject.",
        "code": "Avoid with narrative tasks (sim, probe) that produce prose rather than code. Audience incompatibility: avoid with non-technical audiences (to-CEO, to-managers, to-stakeholders, "
        "to-team). Prefer diagram, presenterm, sketch, or plain for non-technical audiences.",
        "codetour": "Best for code-navigation tasks: fix, make (code creation), show (code structure), pull (code extraction). Avoid with sim, sort, probe, diff (no code subject), or plan. "
        "Requires a developer audience — produces a VS Code CodeTour JSON file. Avoid with manager, PM, executive, CEO, stakeholder, analyst, or designer audiences.",
        "gherkin": "Outputs only Gherkin Given/When/Then syntax. Primary use: make tasks creating acceptance tests or feature specifications. With analysis tasks (probe, diff, check, sort), "
        "output is reframed as Gherkin scenarios that specify the analyzed properties — the analysis becomes evidence; scenarios express what should be true given that evidence. "
        "Avoid with prose-structure forms (story, case, log, questions, recipe).",
        "html": "Avoid with narrative tasks (sim, probe) that produce prose rather than code.",
        "shellscript": "Shell script output. Avoid with narrative tasks (sim, probe) and selection tasks (pick, diff, sort) - these don't produce code. Audience incompatibility: avoid with "
        "non-technical audiences (to-CEO, to-managers, to-stakeholders, to-team).",
        "sketch": "D2 diagram output only. Avoid with prose forms (indirect, case, walkthrough, variants) - choose diagram OR prose, not both.",
    },
    "completeness": {
        "gist": "Brief but complete response. Avoid pairing with compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) that "
        "require multi-dimensional depth — gist cannot express their full range. Use with simple directionals (jog, rog, dig, ong) or none.",
        "max": "Contradicts grow method: max = exhaust all coverage; grow = expand only under demonstrated necessity. Avoid pairing max + grow. Prefer max for exhaustive treatment; prefer "
        "grow for disciplined minimalism. Avoid pairing with sync channel — sync implies practical session brevity; max treating omissions as errors produces unusable session plans.",
        "narrow": "Restricts discussion to a small topic slice. Compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) work with "
        "narrow but the combination examines the slice from multiple analytical dimensions simultaneously — cognitively demanding. If multi-dimensional analysis is the goal, "
        "prefer full or deep completeness so the directional can range freely.",
        "skim": "Quick-pass constraint: most obvious or critical issues only. Avoid pairing with any compound directional (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, "
        "dip-ong, dip-bog, dip-rog, fog) that requires multi-phase depth or sustained examination. Use with simple directionals (jog, rog, dig, ong) or none. Tension with rigor "
        "method: skim constrains response volume while rigor demands disciplined depth — the light pass cannot accommodate the rigorous reasoning rigor requires; expect score-3 "
        "output.",
    },
    "form": {
        "case": "Layered argument-building prose (background, evidence, alternatives, recommendation). Conflicts with code-format channels (gherkin, codetour, shellscript, svg, html, "
        "diagram/sketch) — case-building requires prose structure those channels cannot accommodate. Use with no channel or prose-compatible channels (jira, slack, plain, remote, sync).",
        "commit": "Conventional commit message (type: scope header + optional body). Brief artifact by design — avoid deep or max completeness (no room to express depth) and compound directionals "
        "(fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog, fog). Best with gist or minimal completeness.",
        "contextualise": "Works well with text-friendly channels (plain, sync, jira, slack). Avoid with output-only channels (gherkin, shellscript, codetour) - cannot render explanatory context.",
        "facilitate": "When combined with sim, designs a facilitation structure for a simulation exercise rather than performing the simulation directly.",
        "faq": "Question-and-answer prose format. Conflicts with executable output channels: shellscript, code, codetour (output format mismatch). Use with plain, slack, diagram, or no channel.",
        "log": "Work or research log entry with date markers and bullet updates. Conflicts with any non-text output channel (svg, diagram/sketch, codetour, gherkin, shellscript, html) — log "
        "entries are prose-text artifacts. Use with no channel or prose-compatible channels (jira, slack, remote, sync).",
        "questions": "Conflicts with gherkin (syntax rigidity). With diagram: produces a question-tree Mermaid diagram. Use with plain, slack, diagram, or no channel.",
        "recipe": "Conflicts with codetour, code, shellscript, svg, presenterm (schema has no prose slot). Use with plain, slack, or no channel.",
        "scaffold": "Learning-oriented explanation. Avoid with 'make' task producing artifacts (code, diagram, adr) - use only when user wants accompanied explanation. scaffold = explain from "
        "first principles.",
        "socratic": "Avoid with code channels (shellscript, codetour) - they cannot render questions as code output.",
        "spike": "Research spike: problem statement and exploratory questions. Conflicts with code-format channels (codetour, shellscript, svg, html, diagram/sketch, gherkin) — research spikes are "
        "prose question-documents. Use with no channel or prose-compatible channels.",
        "story": "User story prose (As a / I want / so that). Without a channel: produces prose user stories, avoids Gherkin syntax. With gherkin channel: story acts as a content lens — scenarios "
        "are shaped around user capabilities and value (As a → Given [user state]; I want → When [action]; So that → Then [outcome]). Use with no channel or prose-compatible channels for "
        "pure prose user stories; combine with gherkin channel to produce BDD scenarios framed around user value.",
        "visual": "Distinct from the diagram channel: visual = abstract/metaphorical prose layout with a short legend; diagram = precise Mermaid code with exact nodes and edges. Use visual when "
        "conceptual overview or spatial metaphor is more useful than diagrammatic precision (e.g., non-technical audience, big-picture emphasis). Use diagram when exact topology, "
        "dependency mapping, or architecture review requires precise structure.",
    },
    "method": {
        "abduce": "Distinguish from: deduce (premises→conclusion) and induce (examples→pattern). Abduce generates hypotheses from evidence.",
        "actors": "Well-suited for security threat modelling: identifying threat actors (external attackers, insiders, automated bots), their motivations, and how their capabilities interact "
        "with system attack surfaces. Use alongside adversarial for complete threat models.",
        "afford": "Behavioral constraints: distinguish between logical possibility and practical salience; account for how design foregrounds or suppresses specific actions; specify how "
        "structural constraints pre-shape the perceived action space. Do not attribute outcomes solely to preferences or incentives without modeling how affordances influenced "
        "selection.",
        "balance": "Distinguish from: resilience (behavior under stress). Balance models opposing forces that offset each other to produce equilibrium; claims of stability must identify specific "
        "countervailing pressures and explain why they don't destabilize the system.",
        "bound": "Distinguish from: depends (traces what affects what). Bound limits how far effects, state changes, or responsibilities spread — containing analysis to a specific scope rather "
        "than tracing full dependency chains. Distinguish from: spec (defines correctness criteria). Bound limits scope of influence, not correctness.",
        "branch": "Distinguish from: explore (generating options). Branch explores multiple reasoning paths in parallel with evaluation.",
        "cluster": "Distinguish from: meld (balancing constraints). Cluster groups items by shared characteristics.",
        "deduce": "Distinguish from: abduce (evidence→hypothesis) and induce (examples→pattern). Deduce derives conclusions from premises.",
        "explore": "Distinguish from: branch (parallel reasoning with evaluation). Explore generates options without premature commitment.",
        "gap": "Distinguish from: assume (explicit premises held). Gap identifies where implicit assumptions clash with explicit treatment, producing coordination failures. Useful for analyzing "
        "specification gaps, interface mismatches, or implicit expectations that contradict formal rules.",
        "grow": "Contradicts max completeness: grow = expand only when necessity is demonstrated; max = exhaust all coverage. Avoid pairing grow + max. Prefer grow for disciplined minimalism; "
        "prefer max for exhaustive treatment.",
        "induce": "Distinguish from: abduce (evidence→hypothesis) and deduce (premises→conclusion). Induce generalizes from examples.",
        "inversion": "Well-suited for architecture evaluation: start from named failure modes (cascade failure, split-brain, thundering herd) and ask which design choices create or amplify them. "
        "Use when failure patterns are named and the question is whether the design protects against them.",
        "meld": "Distinguish from: cluster (grouping by characteristics). Meld balances constraints between elements.",
        "polar": "Distinguish from: balance (forces offsetting each other). Polar specifically models attractors and repellers — desired states pursued and undesired states avoided. Claims must "
        "account for both pursuit and avoidance dynamics; don't treat avoidance as mere absence of pursuit.",
        "reify": "Distinguish from: analysis (describe and structure). Reify specifically surfaces implicit patterns as explicit formal rules or entities. Useful when hidden assumptions or "
        "conventions govern behavior but aren't documented.",
        "resilience": "Distinguish from: robust (selecting options that work across futures). Resilience focuses on system behavior under stress.",
        "robust": "Distinguish from: resilience (behavior under stress). Robust favors options that perform acceptably across futures.",
        "systemic": "Distinguish from: analysis (decomposition/structure). Systemic focuses on feedback loops and interactions.",
        "trade": "Distinguish from: balance (forces offsetting each other to produce equilibrium). Trade specifically identifies competing forces and evaluates alternatives across dimensions "
        "before committing. Balance models how existing forces offset; trade explicitly evaluates what trade-offs exist and how to navigate them.",
        "triage": "Use when the goal is to allocate analytical depth non-uniformly — high-consequence high-uncertainty areas get more depth, low-stakes areas get lighter treatment. Distinct from "
        "risks method (risks = enumerate and assess potential problems; triage = calibrate coverage intensity by the consequence×uncertainty gradient once the risk landscape is known). "
        "Can be used together: risks surfaces the risks; triage ensures depth is proportional to them.",
    },
    "scope": {
        "cross": "Use when the question is about where a concern lives across the system, not just within one place. Prefer over struct when the focus is on horizontal span and consistency of a "
        "concern rather than structural arrangement."
    },
}

# Task-type heuristics for when to apply each token (ADR-0132).
# Surfaces as 'When to use' helper text in UIs.
AXIS_KEY_TO_USE_WHEN: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "Architecture Decision Record format: user wants the output structured as an ADR document with Context, Decision, and Consequences sections. Heuristic: 'write an ADR', "
        "'architecture decision record', 'document this decision as an ADR', 'ADR format', 'decision record' → adr. Best with decision-making tasks (plan, probe, make). Avoid with sort, "
        "pull, diff, or sim tasks.",
        "code": "Code or markup only, no prose: user wants only executable or markup output with no surrounding explanation. Heuristic: 'just the code', 'code only', 'no explanation, just the "
        "implementation', 'output code only', 'code without prose', 'just the markup', 'implementation without explanation' → code. Avoid with narrative tasks (sim, probe) that produce "
        "prose.",
        "codetour": "VS Code CodeTour JSON file: user wants the response as a valid CodeTour `.tour` file for navigating code in VS Code. Heuristic: 'codetour', 'VS Code tour', 'code tour "
        "file', 'interactive code walkthrough', 'create a codetour' → codetour. Requires a developer audience. Avoid with manager, PM, or executive audiences.",
        "diagram": "Mermaid diagram code only: user wants the response as Mermaid diagram source, inferred to the best diagram type. Heuristic: 'diagram', 'Mermaid diagram', 'draw a diagram', "
        "'flowchart', 'sequence diagram', 'draw this out', 'architecture diagram in Mermaid', 'as a diagram' → diagram. Distinct from sketch channel (sketch = D2 diagram format; "
        "diagram = Mermaid format).",
        "gherkin": "Gherkin scenario format: user wants the output as Given/When/Then Gherkin scenarios. Heuristic: 'Gherkin format', 'Given/When/Then', 'BDD scenarios', 'acceptance tests in "
        "Gherkin', 'feature file', 'BDD test cases' → gherkin. Avoid with prose-structure forms (case, log, questions, recipe). Exception: story form composes with gherkin — "
        "scenarios are shaped by user-value framing rather than pure behavioral conditions.",
        "html": "Semantic HTML only, no prose: user wants the complete output as HTML markup with no surrounding explanation. Heuristic: 'HTML output', 'semantic HTML', 'as HTML', 'output as a "
        "webpage', 'HTML page', 'HTML only' → html. Avoid with narrative tasks (sim, probe).",
        "jira": "Jira markup formatting: user wants the response formatted using Jira markdown (headings, lists, panels). Heuristic: 'Jira format', 'Jira markup', 'format for Jira', 'Jira "
        "ticket format', 'for a Jira comment', 'use Jira markup' → jira. Use with text-friendly channels; avoid with output-only channels.",
        "plain": "Suppress structural formatting: when user explicitly requests plain prose, no lists, no bullets, or no structural decoration. Heuristic: 'no bullets', 'no formatting', 'plain "
        "prose', 'continuous prose', 'flowing paragraphs', 'paragraph form' → plain channel.",
        "presenterm": "Presenterm slide deck: user wants the output as a multi-slide presenterm Markdown deck with valid front matter, slide separators, and end_slide directives. Heuristic: "
        "'presenterm deck', 'slide deck', 'presentation slides', 'create slides', 'slide format', 'multi-slide deck', 'presentation' → presenterm. Distinct from sync channel (sync "
        "= session plan with timing cues; presenterm = actual slide deck artifact).",
        "remote": "Optimizing output for remote or distributed delivery contexts (video calls, screen sharing, async participants). Heuristic: 'remote delivery', 'distributed session', 'video "
        "call context', 'screen sharing', 'remote-friendly' → remote channel. Note: user saying their team is 'remote' describes context — use remote channel only when delivery "
        "optimization is the explicit goal.",
        "shellscript": "Shell script format: user wants the response as executable shell code. Heuristic: 'shell script', 'bash script', 'write a script', 'automate this with a shell script', "
        "'script format', 'shell code only' → shellscript. Avoid with narrative tasks (sim, probe) and selection tasks (pick, diff, sort).",
        "sketch": "D2 diagram output: when user explicitly requests D2 format or D2 diagram source. Heuristic: 'D2 diagram', 'D2 format', 'sketch diagram', 'd2 source' → sketch. Distinct from "
        "diagram channel (Mermaid output). If the user just says 'diagram' without specifying D2, use diagram channel.",
        "slack": "Slack-formatted Markdown: user wants the response formatted for Slack with appropriate Markdown, mentions, and code blocks. Heuristic: 'Slack format', 'format for Slack', "
        "'post this to Slack', 'Slack message', 'Slack-friendly format', 'for a Slack post' → slack. Avoid channel-irrelevant decoration.",
        "svg": "SVG markup only: user wants the complete output as SVG for direct use in an `.svg` file. Heuristic: 'SVG format', 'as SVG', 'SVG output', 'output as SVG', 'SVG markup only', "
        "'create an SVG' → svg. Output must be minimal and valid SVG with no surrounding prose.",
        "sync": "Live or synchronous session planning: agenda with timing, steps, and cues for real-time delivery. Heuristic: 'session plan', 'live workshop agenda', 'meeting agenda with timing "
        "cues', 'synchronous workshop plan' → sync channel. Combine with facilitate form for facilitator-role outputs.",
    },
    "completeness": {
        "deep": "Substantial depth within the chosen scope: user wants thorough unpacking of reasoning, layers, or fine details without necessarily enumerating every edge case. Heuristic: "
        "'go deep', 'really dig in', 'thorough analysis', 'don\\'t skip the nuances', 'unpack this fully', 'I want the details', 'deep dive', 'depth over breadth' → deep. Distinct "
        "from max (max = exhaustive across all relevant coverage; deep = depth within a focused scope).",
        "full": "Thorough but not exhaustive: user wants a complete answer covering all major aspects without every micro-detail. Heuristic: 'complete', 'comprehensive', 'cover everything "
        "important', 'thorough', 'full picture', 'don\\'t leave anything major out', 'complete treatment' → full. Distinct from max (max = treat omissions as errors; full = "
        "thorough normal coverage) and deep (deep = substantial depth within scope; full = breadth across major aspects).",
        "gist": "Brief but complete response needed: user wants a quick summary or overview without deep exploration. Heuristic: 'quick summary', 'overview', 'brief', 'tldr', 'just the "
        "main points', 'high-level', 'standup update', 'just the gist' → gist. Distinct from skim (skim = light pass, may miss non-obvious; gist = brief but complete).",
        "max": "Exhaustive and leave nothing out: user explicitly wants the most complete possible response, treating omissions as errors. Heuristic: 'be exhaustive', 'miss nothing', "
        "'everything relevant', 'leave nothing out', 'as complete as possible', 'comprehensive and exhaustive', 'cover every case', 'I need everything' → max. Distinct from full "
        "(full = thorough normal coverage; max = every relevant item, omissions are errors).",
        "minimal": "Smallest satisfying answer only: user wants the minimum change or response that addresses the core need, no extras. Heuristic: 'minimal change', 'just what\\'s needed', "
        "'no more than necessary', 'smallest fix', 'keep it small', 'just the minimum', 'don\\'t add anything extra', 'bare minimum', 'only what I asked for' → minimal. Distinct "
        "from narrow (narrow = restrict to a small topic slice; minimal = smallest valid answer to the request).",
        "narrow": "Response should focus on a very specific slice only: user explicitly limits scope to one aspect. Heuristic: 'specifically', 'only about', 'just this part', 'restricted "
        "to', 'nothing beyond', 'only X' → narrow. Distinct from minimal (minimal = smallest answer; narrow = very small slice of topic).",
        "skim": "Light, surface-level pass needed: user wants a quick scan for obvious issues without depth. Heuristic: 'light review', 'quick pass', 'spot check', 'just flag obvious "
        "problems', 'surface-level look', 'sanity check', 'quick skim' → skim. Distinct from gist (gist = brief but complete; skim = light pass that may miss non-obvious issues).",
    },
    "directional": {
        "bog": "Span the full horizontal spectrum — reflective AND acting: user wants the response to cover both the reflective/structural dimension (rog) AND the acting/extending dimension "
        "(ong). bog = rog + ong. Heuristic: 'examine what it means AND tell me what to do about it', 'both the structural reflection and the next steps', 'understand it structurally "
        "and then act on that understanding', 'analysis and actions both' → bog. Distinct from rog (rog = reflective pole only) and ong (ong = acting pole only). bog spans the "
        "horizontal axis end to end.",
        "dig": "Ground in concrete specifics: user wants examples, real cases, and grounded details rather than abstract analysis. Heuristic: 'be concrete', 'give me specific examples', "
        "'show me an actual case', 'not abstract — real examples', 'ground this in reality', 'practical examples only', 'make it tangible', 'I need specifics not theory' → dig. "
        "Distinct from fog (fog = step back to the abstract principle; dig = stay concrete and grounded).",
        "fig": "Span the full vertical spectrum — abstract AND concrete: user wants the response to cover both the abstract/general dimension (fog) AND the concrete/specific dimension "
        "(dig). fig = fog + dig. Heuristic: 'address both the principle and the specifics', 'give me the concept and the grounded examples', 'both the theory and the concrete "
        "reality', 'be abstract and concrete', 'cover the full range from general to specific' → fig. Distinct from fog (fog = abstract pole only) and dig (dig = concrete pole only). "
        "fig spans the vertical axis end to end.",
        "fog": "Surface the abstract pattern or principle: user wants to move from specific cases to the general insight. Heuristic: 'step back and tell me the general principle', 'abstract "
        "away from the details', 'what does this reveal more broadly', 'what\\'s the big picture here', 'what underlying pattern do these cases share', 'zoom out', 'what\\'s the "
        "broader implication' → fog. Distinct from dig (dig = stay concrete; fog = abstract upward from specifics).",
        "jog": "Execute directly without hedging or clarification: user wants an immediate answer, not questions back. Heuristic: 'just answer', 'don\\'t ask me questions', 'make a call', "
        "'just do it', 'don\\'t hedge', 'go ahead', 'I don\\'t need options, just pick one', 'stop asking and decide', 'just tell me' → jog. Most useful with pick, plan, make when "
        "the user explicitly wants a decision rather than a dialogue.",
        "ong": "Push toward concrete action and extension: user wants the response to identify what to do and extend those actions to related contexts. Heuristic: 'what actions should I "
        "take and what comes next after each', 'give me the actions with follow-on steps', 'what do I do and what\\'s the next step after that', 'concrete next steps and their "
        "extensions' → ong. Directional compass: ong is the acting/extending pole (right); rog is the reflective/structural pole (left). Distinct from plan task (plan = strategy and "
        "structure; ong directional = push any task toward acting and extending outward).",
        "rog": "Push toward structural reflection: user wants the response to examine how the subject is organised and reflect on what that structure reveals. Heuristic: 'describe the "
        "structure then tell me what it means', 'how is it organised and what does that reveal', 'walk me through the structure and reflect on the implications', 'what does the "
        "organisation tell us' → rog. Directional compass: rog is the reflective/structural pole (left); ong is the acting/extending pole (right). Distinct from fog (fog = push "
        "toward abstract; rog = push toward structural reflection).",
    },
    "form": {
        "actions": "Action-list output: user wants the response structured as concrete, specific tasks that can be directly acted on — no background analysis. Heuristic: 'give me actions', 'what "
        "do I actually do', 'concrete steps', 'action items', 'what are my next actions', 'just the actions', 'tasks to do', 'list of actions' → actions. Distinct from checklist form "
        "(checklist = imperative checkbox items; actions = broader action-structured output including tasks, steps, and next moves) and walkthrough form (walkthrough = guided sequential "
        "narration; actions = direct action list without guided narration).",
        "activities": "Segment-level session content: user wants the concrete activities within a session, not the overall facilitation structure. Heuristic: 'what activities should we do', "
        "'activities for each block', 'session activities', 'design sprint activities', 'what happens in each segment', 'activities list for the workshop' → activities. Distinct from "
        "facilitate form (facilitate = overall facilitation plan with session goals and participation mechanics; activities = segment-by-segment content of what to do and when). "
        "Often combined with facilitate: facilitate handles the structure, activities handles the content.",
        "bug": "Bug report format: user wants the output structured as a formal bug report with Steps to Reproduce, Expected Behavior, Actual Behavior, and Context. Heuristic: 'file a bug report', "
        "'write this up as a bug', 'bug report format', 'steps to reproduce', 'expected vs actual behavior', 'create a bug ticket' → bug. Best paired with probe or diagnostic methods "
        "(diagnose, adversarial). Distinct from log form (log = work log entry; bug = structured defect report).",
        "bullets": "Bullet-point structure: user wants ideas organized as concise bullets rather than paragraphs. Heuristic: 'bullet points', 'use bullets', 'bulleted list', 'as bullet points', "
        "'short bullets', 'list format with bullets', 'no paragraphs, just bullets' → bullets. Distinct from checklist form (checklist = imperative action items; bullets = general "
        "bullet-point organization not necessarily imperative).",
        "cards": "Card-style layout: user wants content organized as discrete cards — each with a heading and short body — rather than continuous prose. Heuristic: 'cards', 'card layout', 'each "
        "item as a card', 'discrete cards', 'card format', 'organize as cards', 'section cards with headings' → cards. Distinct from bullets form (bullets = brief bullets; cards = richer "
        "discrete units each with a heading and short body).",
        "case": "Case-building narrative: user wants background, evidence, trade-offs, and alternatives laid out before the recommendation. Heuristic: 'build the case', 'lay out the argument "
        "before the recommendation', 'walk through the evidence first', 'structured argument', 'present the case', 'evidence then conclusion', 'case for X' → case. Distinct from indirect "
        "form (indirect = softer reasoning that converges on a point; case = structured argument with explicit evidence, alternatives, and objection handling before the recommendation).",
        "checklist": "Imperative checklist: user wants the response as a checkbox-style list of clear imperative tasks. Heuristic: 'checklist', 'give me a checklist', 'checkbox list', 'actionable "
        "checklist', 'checkboxes', 'items to check off', 'pre-flight checklist' → checklist. Distinct from actions form (actions = general action-structured output; checklist = "
        "specifically checkbox-style imperative items designed to be ticked off).",
        "cocreate": "Iterative design with explicit decision points and alignment checks at each step rather than a one-shot response. Heuristic: 'work through incrementally', 'with decision "
        "points', 'iterative design' → cocreate. Distinct from variants (choice of designs) and make (one-shot artifact).",
        "commit": "Conventional commit message format: user wants a short type/scope header with an optional concise body. Heuristic: 'write a commit message', 'commit message for this', "
        "'conventional commit', 'git commit message', 'commit message', 'type: scope format' → commit. Best with gist or minimal completeness — the format is brief by design.",
        "contextualise": "Preparing content to be passed to another LLM operation: user wants output that is self-contained and includes all necessary context for a downstream model to process "
        "without additional explanation. Heuristic: 'pass this to another model', 'use this as context for', 'prepare for downstream processing', 'make this self-contained for an "
        "LLM', 'include all necessary context', 'so I can feed this to' → contextualise. Distinct from make (make = create the artifact; contextualise = package existing content "
        "with full context for another LLM to act on it).",
        "direct": "Conclusion-first narrative: user wants the main point or recommendation stated first, followed only by the most relevant supporting context. Heuristic: 'lead with the answer', "
        "'bottom line up front', 'BLUF', 'give me the conclusion first', 'direct response', 'state the recommendation first', 'don\\'t bury the lede' → direct. Distinct from indirect "
        "form (indirect = background first, conclusion last; direct = main point first, supporting detail after).",
        "facilitate": "Planning a workshop, retrospective, or collaborative session with session structure, participation cues, and facilitation agenda. Heuristic: 'facilitate a X', 'run a "
        "retrospective', 'workshop planning' → facilitate. Distinct from walkthrough (linear narrated steps).",
        "faq": "FAQ format: user wants content structured as question-and-answer pairs with clear question headings. Heuristic: 'FAQ format', 'as a FAQ', 'Q and A format', 'frequently asked "
        "questions', 'questions and answers', 'write as Q&A', 'question headings with answers below' → faq. Distinct from questions form (questions = response IS a list of questions to "
        "investigate; faq = questions paired with their answers as a reference artifact).",
        "formats": "Document format or template focus: user asks about which document type, writing format, or structural template best fits the situation. Heuristic: 'what format should I use', "
        "'what template fits', 'which document type', 'writing format options', 'what structure should this take', 'what are the format options', 'format comparison' → formats. Distinct "
        "from table form (table = present content as a table; formats = the response IS about document types and their suitability).",
        "indirect": "Reasoning-first, conclusion-last narrative: user asks for explanation or recommendation that builds up context before landing the point. Heuristic: 'walk me through the "
        "reasoning first', 'build up to the recommendation', 'show your thinking before the conclusion', 'give me the context before the answer', 'reasoning before conclusion' → "
        "indirect. Distinct from case form (case = structured argument with evidence and objections; indirect = softer narrative reasoning that converges on a bottom-line point).",
        "ladder": "Analyzing causes or effects across multiple levels of abstraction: step up to systemic causes, step down to concrete consequences. Heuristic: 'step up and down abstraction "
        "levels', 'root cause hierarchy', 'why at a systems level' → ladder.",
        "log": "Work or research log entry format: user wants the response styled as a concise dated log entry with bullet-style updates and enough context for future reference. Heuristic: 'write "
        "this as a log entry', 'work log', 'research log', 'log format', 'dated entry', 'journal entry', 'log what we did', 'write up as a log' → log. Distinct from walkthrough form "
        "(walkthrough = guided sequential narration; log = concise dated entry format for archival and reference).",
        "merge": "Combining multiple sources into one coherent artifact: user has several pieces of content to consolidate without losing key information. Heuristic: 'merge these', 'combine into "
        "one', 'consolidate', 'synthesize these sources', 'merge the content', 'bring these together', 'unify these documents', 'integrate these into a single output' → merge. Distinct "
        "from contextualise form (contextualise = package with context for downstream LLM; merge = combine multiple sources into one coherent whole).",
        "questions": "Response structured as a list of investigation or clarification questions: user wants the response itself to be a set of questions they can pursue, not statements or answers. "
        "Heuristic: 'what questions should I ask', 'give me questions to investigate', 'what should I be asking about', 'frame this as questions', 'questions I should explore', "
        "'diagnostic questions for' → questions. Distinct from socratic form (socratic = LLM asks the USER questions interactively to surface their thinking; questions = response IS a "
        "question-list artifact the user takes away).",
        "quiz": "Quiz structure with questions before answers: user wants to test understanding interactively or produce a quiz artifact. Heuristic: 'quiz me', 'make a quiz', 'quiz format', "
        "'questions before answers', 'test my knowledge', 'knowledge check', 'quiz questions on', 'multiple choice quiz' → quiz. Without a channel token, conducts interactively; with an "
        "output channel, produces a quiz document. Distinct from socratic form (socratic = question-led dialogue to surface user reasoning; quiz = test recall via question-then-answer "
        "structure).",
        "recipe": "Documenting a process as a structured recipe with a custom mini-language and short key — best when the process has a recurring structure that benefits from a custom notation. "
        "Heuristic: 'document as recipe', 'structured setup guide with repeating patterns' → recipe. Distinct from walkthrough (linear narrated steps without custom notation).",
        "scaffold": "First-principles scaffolded explanation: user wants concepts introduced gradually with analogies and examples so understanding builds from the ground up. Heuristic: 'explain "
        "from scratch', 'teach me this', 'start from first principles', 'build up my understanding', 'I\\'m a beginner', 'explain step by step as if I\\'m new to this', 'scaffold my "
        "learning' → scaffold. Distinct from walkthrough form (walkthrough = guided sequential steps through a process; scaffold = pedagogical first-principles introduction that builds "
        "understanding).",
        "socratic": "Question-led dialogue to surface the user's own thinking: user wants to be asked questions rather than given answers, or wants to reason through a topic interactively. "
        "Heuristic: 'ask me questions', 'help me think through', 'challenge my assumptions with questions', 'Socratic dialogue', 'probe my thinking', 'question me as we work through "
        "this', 'help me reason this out' → socratic. Distinct from adversarial method (adversarial = stress-test the design; socratic = question the USER's reasoning via dialogue).",
        "spike": "Framing a technology investigation or adoption decision as a backlog spike artifact (problem statement + exploratory questions). Use make task (not plan) — the spike IS the "
        "artifact. Heuristic: 'should we adopt X?', 'spike on Y', 'investigation backlog item' → make + spike.",
        "story": "User story format: user wants a backlog item expressed as 'As a <persona>, I want <capability>, so that <value>.' Heuristic: 'user story', 'write as a user story', 'as a user I "
        "want', 'story format', 'user story for this feature', 'backlog user story', 'story card' → story. Distinct from spike form (spike = research question artifact; story = "
        "user-facing value statement with acceptance criteria).",
        "table": "Markdown table presentation: user wants the main content organized as a table with columns and rows. Heuristic: 'table format', 'present as a table', 'markdown table', 'tabular "
        "comparison', 'show in a table', 'grid format', 'as a table', 'column-row layout' → table. Distinct from cards form (cards = discrete headed items; table = columnar grid layout).",
        "taxonomy": "Producing a type hierarchy, category classification, or taxonomy of entities. Pair with thing scope for concrete entities. Heuristic: 'classify all types of X', 'what kinds of "
        "Y exist', 'type hierarchy' → taxonomy + thing scope. Distinct from table (flat comparison).",
        "test": "Structured test case format: user wants test cases with clear setup, execution, and assertion sections organized by scenario type. Heuristic: 'write test cases', 'test cases for', "
        "'happy path and edge cases', 'unit test structure', 'test scenarios', 'write the tests', 'test case format with setup and assertion' → test. Distinct from checklist form "
        "(checklist = imperative tasks to complete; test = structured test scenarios with setup/execute/assert structure).",
        "tight": "Concise dense prose without bullets or tables: user wants a freeform but compact response that avoids filler and structural decoration. Heuristic: 'tight prose', 'concise and "
        "dense', 'no bullets or tables', 'compact freeform', 'dense prose', 'brevity without structure', 'just prose, no formatting' → tight. Distinct from plain channel (plain = no "
        "structural decoration as a delivery format; tight = concise dense prose style that avoids filler).",
        "variants": "Multiple distinct labeled options: user wants several decision-ready alternatives presented separately, each with a short label and description. Heuristic: 'give me options', "
        "'present several approaches', 'show me alternatives', 'multiple variants', 'different approaches', 'what are the options with labels', 'present 3 options', 'decision-ready "
        "alternatives' → variants. Distinct from compare method (compare = evaluate alternatives against criteria; variants = present distinct labeled options without necessarily "
        "evaluating them against each other).",
        "visual": "Abstract or metaphorical representation of a subject as prose layout with a legend — when diagrammatic precision (Mermaid) is less useful than conceptual overview. Heuristic: "
        "'abstract visual', 'conceptual layout', 'big-picture structure for non-technical audience' → visual. Distinct from diagram channel (precise Mermaid output).",
        "walkthrough": "Step-by-step guided narration: user wants to be taken through something stage by stage so understanding builds sequentially. Heuristic: 'walk me through', 'step by step "
        "walkthrough', 'guide me through', 'take me through it', 'step-by-step guide', 'walkthrough of', 'narrate the steps' → walkthrough. Distinct from actions form (actions = "
        "list of actions to take; walkthrough = guided sequential narration that builds understanding).",
        "wardley": "Strategic mapping: user wants to position components on an evolution axis (genesis → custom → product → commodity). Heuristic: 'Wardley map', 'map on evolution axis', 'genesis "
        "to commodity' → wardley.",
        "wasinawa": "Post-incident reflection or retrospective on past events. Structures output as: what happened, why it matters, next steps. Heuristic: 'reflect on incident', 'what went wrong "
        "and what to do next', 'lessons learned' → wasinawa. Distinct from pre-mortem (inversion method): pre-mortem assumes future failure; wasinawa reflects on past events.",
    },
    "method": {
        "abduce": "Comparative hypothesis generation from evidence: user wants multiple candidate explanations ranked by how well they fit the evidence, not just a single root cause. Heuristic: "
        "'what\\'s the best explanation for', 'generate hypotheses for why', 'what are the most likely causes ranked', 'compare possible explanations', 'ranked hypotheses from "
        "evidence', 'what could explain this' → abduce. Distinct from diagnose (diagnose = narrow to single root cause via evidence; abduce = generate and compare multiple competing "
        "explanations explicitly). Distinct from induce (induce = generalize a rule from examples; abduce = hypothesize from evidence).",
        "actors": "Actor-centered analysis: user wants the response to center the people, roles, or agents involved — who is participating, what their motivations are, and how their actions "
        "shape outcomes. Heuristic: 'who is involved', 'what are the stakeholders doing', 'who are the actors', 'center the people', 'model the roles', 'who does what', 'what motivates "
        "each party', 'threat actors', 'roles and responsibilities' → actors. Distinct from agent scope (agent = who has decision authority; actors method = enrich the response with "
        "actor-centered analysis regardless of scope).",
        "adversarial": "Stress-testing for weaknesses and failure modes: user wants the response to constructively attack the design, argument, or plan — finding counterexamples, edge cases, and "
        "hidden assumptions. Heuristic: 'what could go wrong', 'find the weaknesses', 'stress-test this', 'what\\'s the worst-case attack', 'where does this argument break', "
        "'challenge this plan', 'red-team this', 'what are the counterexamples', 'play devil\\'s advocate' → adversarial. Distinct from risks method (risks = enumerate failure "
        "modes and likelihood; adversarial = actively stress-test by constructing attacks and counterexamples). NOT suited for interpersonal feedback tasks ('sensitive feedback on "
        "a colleague', 'supportive code review') — prefer analysis method and pair with tone=gently instead.",
        "afford": "Affordance-driven behavior analysis: user wants to explain why behavior arises from system or interface design — what the structure makes easy, visible, or natural vs. what it "
        "suppresses. Heuristic: 'why do users do X', 'the design encourages Y', 'affordances', 'what the API makes easy', 'shaped by the structure', 'how the design foregrounds this "
        "option', 'structural constraints on behavior', 'design defaults bias toward', 'interface suppresses this action' → afford. Distinct from field (actors interact via a shared "
        "medium; afford = how available-action structure pre-shapes individual choices). Distinct from systemic (feedback loops and emergent dynamics; afford = structural availability "
        "shapes what actors perceive as actionable).",
        "analog": "Analogical reasoning: user wants to understand the subject by mapping it onto a well-understood case, examining where the analogy holds and where it breaks. Heuristic: 'what "
        "is this like', 'what does this remind you of', 'explain using an analogy', 'what\\'s the analogous structure', 'reason by analogy', 'find a parallel case', 'what known "
        "situation does this resemble' → analog. Distinct from models method (models = apply named mental models explicitly; analog = reason through a structural mapping from a "
        "specific known case).",
        "analysis": "General structural decomposition when no specific structural lens applies: user wants the subject broken into components and each examined for role, properties, and "
        "interactions — without spatial, dependency, grouping, sequential, historical, or criteria focus. Heuristic: 'analyze this', 'describe the situation', 'help me understand "
        "what\\'s happening', 'structure my understanding', 'what is going on here', 'break this down for me', 'understand before acting' → analysis. Distinct from: mapping (spatial "
        "layout), depends (dependency tracing), cluster (group by similarity), order (hierarchical/sequential), origin (historical causation), spec (governing criteria), gap "
        "(implicit assumptions). Also distinct from diagnose (diagnose = root cause via falsification; analysis = structural decomposition without fault-finding).",
        "argue": "Explicit argument structure: user wants claims, premises, warrants, and rebuttals made visible rather than a flowing narrative. Heuristic: 'make the argument', 'structure this "
        "as an argument', 'what are the premises', 'what supports this claim', 'build the logical case', 'argument and rebuttal', 'explicit reasoning structure' → argue. Distinct from "
        "case form (case = narrative that builds to a recommendation; argue = expose the logical structure of claims and their supports).",
        "balance": "Force balancing and equilibrium analysis: user wants to understand how opposing pressures, incentives, or constraints offset each other to produce stability or tension. "
        "Heuristic: 'how do forces balance', 'what opposing pressures exist', 'what keeps this in equilibrium', 'what countervailing forces', 'how do trade-offs play out', 'what "
        "tensions exist', 'balance of forces' → balance. Distinct from resilience method (resilience = behavior under stress; balance = how opposing forces produce equilibrium or "
        "instability).",
        "bias": "Cognitive bias identification: user wants the response to surface likely systematic errors or heuristics that could distort judgment about this situation. Heuristic: 'what "
        "biases might affect this', 'cognitive biases', 'where might we be wrong due to bias', 'what systematic errors', 'heuristics distorting judgment', 'where are we susceptible to "
        "bias', 'confirmation bias', 'availability heuristic' → bias. Distinct from verify method (verify = falsify specific claims; bias = identify cognitive mechanisms producing "
        "distortion).",
        "boom": "Scale extreme analysis: user asks what happens at 10x, 100x, or at the absolute limits of the system. Heuristic: 'at 10x', 'at extreme load', 'what breaks at scale', 'pushed to "
        "the limit', 'at maximum load', 'what dominates at scale', 'scale to the extreme', 'at the limit' → boom. Distinct from resilience (normal stress range) and adversarial "
        "(deliberate attack/exploit focus).",
        "bound": "Propagation boundary analysis: user wants to explicitly limit how far state changes, effects, or responsibilities propagate through the system — containing analysis to a "
        "specific scope rather than tracing full dependency chains. Heuristic: 'limit the scope of changes', 'constrain how far effects spread', 'bound the blast radius', 'contain the "
        "impact', 'what happens locally vs globally', 'limit responsibility propagation', 'scope the change impact' → bound. Distinct from depends (depends = trace all dependencies; "
        "bound = limit how far they spread). Distinct from spec (spec = define correctness; bound = limit reach of influence).",
        "branch": "Parallel reasoning path exploration: user wants multiple hypotheses or approaches explored simultaneously before evaluation and pruning. Heuristic: 'explore multiple paths', "
        "'consider different approaches in parallel', 'branch the reasoning', 'multiple lines of reasoning', 'explore alternatives before choosing', 'parallel hypotheses' → branch. "
        "Distinct from explore method (explore = survey option space without premature commitment; branch = fork on a key assumption and pursue each path before evaluating).",
        "calc": "Quantitative or executable reasoning: user wants calculations, formal procedures, or step-by-step numerical analysis that constrain conclusions. Heuristic: 'calculate', 'what "
        "does the math say', 'run the numbers', 'quantify this', 'estimate the cost', 'work out the probability', 'formal calculation', 'compute', 'what are the numbers' → calc. Distinct "
        "from probability method (probability = statistical and probabilistic reasoning; calc = general quantitative or quasi-executable procedures).",
        "canon": "Canonical-source analysis: user asks which representation is authoritative, wants to eliminate duplication by locating the SSOT, or needs to map multiple representations to a "
        "single canonical origin. Heuristic: 'where is the single source of truth', 'we have duplicate definitions', 'which config is authoritative', 'DRY violation', 'multiple "
        "representations of the same thing', 'who owns this data', 'derive X from Y instead of duplicating', 'canonical source for', 'reduce duplication to derivation' → canon. Distinct "
        "from depends (depends = trace what relies on what; canon = reduce multiple representations to a single authoritative locus). Distinct from mapping (mapping = surface elements "
        "and relationships; canon = identify or enforce the single canonical source among them).",
        "cite": "Evidence-anchored response with sources: user wants claims backed by references, citations, or named sources for verification. Heuristic: 'cite your sources', 'include "
        "references', 'back this up with evidence', 'link to sources', 'where does this come from', 'support with citations', 'show your evidence' → cite. Distinct from verify method "
        "(verify = apply falsification pressure internally; cite = anchor claims to external sources the user can check).",
        "cluster": "Group items by shared characteristics: user wants existing items organized into categories or clusters without reinterpreting their content. Heuristic: 'group these', "
        "'cluster by', 'categorize', 'organize into groups', 'what themes emerge', 'sort into buckets', 'group by similarity', 'classify these items' → cluster. Distinct from compare "
        "method (compare = evaluate alternatives against criteria; cluster = group without evaluating) and meld method (meld = balance constraints; cluster = organize by shared "
        "traits).",
        "compare": "Systematic comparison against explicit criteria: user has options and wants to know how they differ or which is better. Heuristic: 'compare X and Y', 'which is better', 'how "
        "do these differ', 'tradeoffs between', 'evaluate these options', 'side by side comparison', 'which should I choose', 'pros and cons' → compare. Distinct from converge method "
        "(converge = narrow from exploration to recommendation; compare = explicit criteria-based evaluation of specified alternatives).",
        "converge": "Narrowing from exploration to focused recommendation: user wants broad options filtered down to the best choice with explicit trade-off reasoning. Heuristic: 'narrow it "
        "down', 'which one should I go with', 'help me pick', 'synthesize into a recommendation', 'from all options, which is best', 'converge on an answer', 'filter and recommend' → "
        "converge. Distinct from compare method (compare = evaluate alternatives side by side; converge = narrow exploration toward a single recommendation).",
        "deduce": "Deductive logical reasoning: user wants conclusions derived from stated premises through explicit logical entailment. Heuristic: 'what follows from', 'given these premises', "
        "'logical conclusion', 'deduce from', 'what must be true if', 'derive the consequence', 'if X then what', 'logically entails' → deduce. Distinct from abduce (evidence → "
        "hypothesis) and induce (examples → general pattern).",
        "depends": "Dependency tracing: user wants to know what relies on what and how changes would propagate through the system. Heuristic: 'what depends on X', 'dependency map', 'what breaks "
        "if I change Y', 'what does this rely on', 'upstream and downstream', 'dependency chain', 'what would be affected', 'what does Z need to work' → depends. Distinct from struct "
        "scope (struct = internal arrangement; depends = propagation and reliance relationships specifically).",
        "diagnose": "Root cause investigation via evidence and falsification: user wants to narrow down likely causes through targeted checks rather than immediately proposing fixes. Heuristic: "
        "'what is causing this', 'root cause', 'why is this happening', 'diagnose this problem', 'narrow down the cause', 'what\\'s the bug source', 'investigate why', 'find the root "
        "cause' → diagnose. Distinct from abduce (abduce = generate and compare competing hypotheses; diagnose = narrow to single most likely cause via falsification).",
        "dimension": "Multi-dimensional analysis: user wants implicit axes or factors made explicit and examined for how they interact. Heuristic: 'what are the dimensions', 'what factors are at "
        "play', 'multiple axes of analysis', 'what hidden factors', 'what are we not considering', 'analyze across dimensions', 'surface the implicit factors' → dimension. Distinct "
        "from split method (split = decompose into parts; dimension = surface analytical axes that the parts exist along).",
        "domains": "Bounded context and domain boundary analysis: user wants to identify where one problem domain ends and another begins, or what the distinct capabilities are. Heuristic: 'what "
        "are the domains', 'where are the bounded contexts', 'domain-driven design', 'what are the distinct capabilities', 'domain boundaries', 'how to carve up the system into "
        "domains', 'which team owns which' → domains. Distinct from struct scope (struct = internal arrangement; domains = identify bounded context separations and capabilities).",
        "effects": "Second and third-order consequence tracing: user wants to look beyond immediate outcomes to downstream ripple effects. Heuristic: 'what are the downstream effects', 'second "
        "order effects', 'ripple effects', 'what happens next after that', 'unintended consequences', 'how does this propagate', 'what follows downstream' → effects. Distinct from "
        "grove method (grove = how effects accumulate and compound; effects = trace the chain of consequences).",
        "experimental": "Concrete experiment design: user wants specific, runnable experiments with expected outcomes and hypothesis-updating logic. Heuristic: 'design an experiment', 'how would "
        "we test this', 'what experiment would prove this', 'propose tests', 'how do we validate', 'what would we measure', 'design a study', 'run a test to find out' → "
        "experimental. Distinct from verify method (verify = apply falsification pressure analytically; experimental = propose actual runnable tests).",
        "explore": "Open option-space survey: user wants a broad scan of possible approaches without premature commitment to any one path. Heuristic: 'what are the options', 'explore the "
        "solution space', 'what approaches exist', 'brainstorm possibilities', 'what could we do', 'survey the landscape', 'open-ended exploration', 'what\\'s possible here' → "
        "explore. Distinct from branch method (branch = fork on a key assumption and pursue paths; explore = broad survey without forking on a specific choice).",
        "field": "Shared-medium interaction analysis: user asks how actors interact through a shared infrastructure or protocol layer rather than via direct references. Heuristic: 'shared "
        "infrastructure', 'shared medium', 'protocol mediation', 'service mesh routing', 'why things route through', 'broadcast patterns', 'effects propagate through a shared layer' → "
        "field. Distinct from mapping (surface elements; field = model the medium and why compatibility produces observed routing).",
        "flow": "Step-by-step sequential progression: user wants to understand how something moves through a process — control flow, data flow, or narrative sequence. Heuristic: 'walk me through "
        "the flow', 'how does data move', 'trace the execution path', 'step by step sequence', 'control flow', 'how does it progress', 'follow the data through the system', 'trace the "
        "path' → flow. Distinct from time scope (time = temporal emphasis as scope lens; flow = step-by-step progression as a reasoning method).",
        "gap": "Implicit-to-explicit gap analysis: user wants to identify where assumptions, rules, roles, or relationships are treated as explicit but remain implicit, creating ambiguity or "
        "coordination failures. Heuristic: 'what's the gap between what we say and do', 'where are implicit expectations vs explicit rules', 'coordination breakdown', 'specification gap', "
        "'what's assumed but not stated', 'implicit vs explicit mismatch' → gap. Distinct from assume scope (assume = explicit premises; gap = implicit treated as explicit).",
        "grove": "Accumulation and compounding analysis: user asks how small effects build up over time, how debt or improvement compounds, or how feedback loops amplify outcomes. Heuristic: "
        "'compound', 'accumulates over time', 'feedback loop', 'technical debt grows', 'network effect', 'how things build up', 'rate of change over time', 'snowball' → grove. Distinct "
        "from systemic (interacting whole; grove = rate of accumulation through mechanisms) and effects (trace consequences; grove = HOW they compound).",
        "grow": "Evolutionary or incremental design philosophy: user wants to start minimal and expand only when demonstrably needed. Heuristic: 'start simple and expand', 'minimum viable', "
        "'YAGNI', 'add only what you need', 'simplest thing that works', 'evolve as needed', 'don't over-engineer', 'add features only when required', 'grow incrementally' → grow. "
        "Distinct from minimal completeness (brevity of output) and spec (define criteria first).",
        "induce": "Inductive generalization from examples: user wants to draw a general principle, pattern, or rule from a set of specific cases or observations. Heuristic: 'what general "
        "principle can I draw from these', 'what pattern do these examples suggest', 'what does this tell us more broadly', 'generalize from these observations', 'what can I conclude "
        "from these cases', 'what rule emerges from these instances', 'extrapolate from these examples' → induce. Distinct from abduce (abduce = generate competing hypotheses to "
        "explain evidence; induce = generalize a rule or pattern from a set of examples).",
        "inversion": "Inversion reasoning from bad outcomes: user wants to start from failure or catastrophe and work backward to what must be avoided or designed around. Heuristic: 'what would "
        "cause this to fail completely', 'pre-mortem', 'how would we destroy this', 'what would guarantee failure', 'invert the goal', 'work backwards from disaster', 'what produces "
        "the worst outcome' → inversion. Distinct from risks method (risks = enumerate failure modes; inversion = start FROM disaster and derive what to avoid).",
        "jobs": "Jobs-to-be-done (JTBD) analysis: user wants to understand what outcome users are trying to achieve, what need the feature serves, or what forces shape their adoption choices. "
        "Heuristic: 'what is the user actually trying to accomplish', 'what job does this feature do', 'what need does this solve', 'why would someone use this', 'what outcome does the "
        "user want', 'what drives adoption', 'user motivation behind', 'JTBD', 'jobs to be done' → jobs. Distinct from product method (product = features, user needs, value propositions "
        "broadly; jobs = specifically the outcome/progress users seek and the forces blocking or enabling it).",
        "mapping": "Spatial relationship map: user wants elements, relationships, and structure surfaced and organized into a coherent map rather than a linear narrative. Heuristic: 'map out', "
        "'surface the relationships', 'landscape map', 'draw the connections', 'build a map of', 'what\\'s the structure of the landscape', 'map the territory', 'visualize the "
        "relationships' → mapping. Distinct from struct scope (struct = internal topology of one unit; mapping = surface and organize across the whole landscape).",
        "meld": "Constraint-balancing or tension-resolution analysis: user asks how to balance competing forces, find overlaps, or navigate constraints between elements that must coexist. "
        "Heuristic: 'balance between', 'overlap between', 'constraints between', 'combining X and Y', 'where X and Y interact', 'navigate tensions between', 'find the combination that "
        "satisfies' → meld. Distinct from compare (evaluate alternatives; meld = balance constraints between elements that must coexist).",
        "melody": "Cross-component or cross-team coordination analysis: user asks how to synchronize work, manage coupling, or align changes across teams or components. Heuristic: 'coordinate "
        "across teams', 'synchronize changes', 'change alignment', 'coupling between components', 'parallel work streams', 'avoid conflicts between teams', 'migration coordination', "
        "'who needs to change when' → melody. Distinct from depends (what relies on what) and actors (centering the people involved).",
        "mod": "Cyclic or periodic pattern analysis: user asks about behavior that repeats, wraps around, or follows a cycle. Heuristic: 'repeats across cycles', 'cyclic behavior', 'periodic "
        "pattern', 'repeating structure', 'what wraps around', 'recurs periodically', 'equivalent states' → mod. Distinct from motifs scope (recurring patterns across codebase; mod = "
        "cyclic/periodic reasoning about behavior that repeats with a defined period).",
        "models": "Named mental model application: user wants specific named frameworks or mental models applied explicitly to the situation, not just intuitive analysis. Heuristic: 'what mental "
        "models apply here', 'apply a framework', 'use first principles', 'which frameworks are relevant', 'what lenses should I use', 'apply systems thinking', 'what models explain "
        "this', 'name the applicable mental models' → models. Distinct from analog method (analog = reason from a specific analogous case; models = apply named, established mental "
        "models explicitly).",
        "objectivity": "Fact-opinion separation: user wants claims clearly labeled as objective facts vs. subjective opinions, with evidence supporting factual claims. Heuristic: 'what\\'s "
        "objective vs subjective', 'separate fact from opinion', 'what is actually true vs what is a judgment', 'stick to facts', 'evidence-based only', 'distinguish observation "
        "from interpretation', 'is this a fact or an opinion' → objectivity. Distinct from rigor method (rigor = disciplined logical reasoning; objectivity = separate what is "
        "factual from what is evaluative).",
        "operations": "Operations research framing: user wants management science or OR concepts applied — queuing, scheduling, optimization, or resource allocation. Heuristic: 'throughput', "
        "'bottleneck analysis', 'resource allocation', 'scheduling problem', 'queuing', 'capacity planning', 'utilization', 'operations research', 'minimize wait time', "
        "'optimization problem' → operations. Distinct from systemic method (systemic = feedback loops and emergent behavior; operations = OR/management science frameworks for "
        "resource and flow optimization).",
        "order": "Abstract structural and ordering reasoning: user wants explicit attention to hierarchy, ranking criteria, or recurrence — the principles behind the sequencing. Heuristic: 'what "
        "is the ordering principle', 'hierarchical ordering', 'ranking criteria', 'what determines the order', 'dominance structure', 'what makes one thing rank above another', "
        "'ordering and precedence' → order. When paired with sort task, order adds emphasis on the criteria and scheme driving the sequence. Distinct from prioritize method (prioritize "
        "= rank by importance with rationale; order = abstract structural reasoning about ordering schemes).",
        "origin": "Historical and causal origin analysis: user wants to understand how the current state came to be — past decisions, evolutionary pressures, and historical context. Heuristic: "
        "'how did we get here', 'what is the history of', 'why does it look this way', 'what past decisions led to this', 'origin story', 'historical context', 'how did this evolve', "
        "'archaeology of the codebase', 'why is this the way it is' → origin. Distinct from time scope (time = sequential/temporal emphasis; origin = specifically causal history and "
        "why the present state is as it is).",
        "polar": "Attractor-repeller dynamics analysis: user wants to understand behavior as shaped by both desired states (attractors pursued) and undesired states (repellers avoided). "
        "Heuristic: 'what attracts and repels', 'pull toward and push away from', 'what are the incentives and disincentives', 'what's rewarded and penalized', 'attractors and "
        "repellers', 'positive and negative motivations' → polar. Distinct from balance (balance = forces offsetting each other; polar = attraction toward some states and aversion from "
        "others).",
        "prioritize": "Importance or impact ranking with explicit rationale: user wants items ordered by priority and the ranking reasoning made clear. Heuristic: 'prioritize', 'what should we "
        "do first', 'rank by impact', 'most important first', 'order by priority', 'what matters most', 'high-priority items', 'rank and explain the ranking' → prioritize. Distinct "
        "from order method (order = abstract structural reasoning about ordering schemes; prioritize = rank by importance or impact with explicit rationale).",
        "probability": "Probabilistic and statistical reasoning: user wants uncertainty quantified or outcomes characterized using probability. Heuristic: 'how likely is', 'what\\'s the "
        "probability', 'expected value', 'confidence interval', 'statistical significance', 'base rate', 'probability of failure', 'how certain are we', 'Bayesian reasoning', "
        "'likelihood' → probability. Distinct from calc method (calc = general quantitative computation; probability = specifically statistical and probabilistic reasoning under "
        "uncertainty).",
        "product": "Product lens analysis: user wants the subject examined through the frame of features, user needs, and value propositions. Heuristic: 'product perspective', 'through a product "
        "lens', 'feature vs user need', 'value proposition', 'product strategy', 'what does the product offer', 'user needs analysis', 'product thinking' → product. Distinct from jobs "
        "method (jobs = outcomes users seek and forces shaping adoption; product = broader product lens including features and value propositions).",
        "reify": "Implicit pattern formalization: user wants to surface hidden assumptions, conventions, or relationships and make them explicit as formal rules, entities, or distinctions. "
        "Heuristic: 'what's the hidden assumption', 'make implicit explicit', 'what conventions govern this', 'what's unstated but assumed', 'formalize the informal', 'what rules "
        "actually apply here' → reify. Distinct from analysis method (analysis = describe and structure; reify = convert implicit patterns into explicit formal rules).",
        "resilience": "System stress and recovery analysis: user wants to understand how the system behaves under failure, load, or disruption — fragility, robustness, and margin of safety. "
        "Heuristic: 'how resilient is this', 'what happens under load', 'failure recovery', 'margin of safety', 'fragility vs robustness', 'how does it behave under stress', "
        "'graceful degradation', 'fault tolerance' → resilience. Distinct from robust method (robust = choose options that perform across uncertain futures; resilience = analyze "
        "system behavior under stress specifically).",
        "rigor": "Disciplined, well-justified reasoning: user wants the response to rely on disciplined logic with explicit reasoning chains rather than intuitive leaps. Heuristic: 'be "
        "rigorous', 'make the reasoning explicit', 'disciplined analysis', 'careful reasoning', 'justify each step', 'logical rigor', 'no handwaving', 'substantiate your claims' → "
        "rigor. Distinct from verify method (verify = apply falsification pressure to claims; rigor = discipline the reasoning process throughout).",
        "risks": "Risk and failure mode enumeration: user wants potential problems, failure modes, and their likelihood or severity identified. Heuristic: 'what are the risks', 'what could go "
        "wrong', 'risk assessment', 'failure modes', 'identify the hazards', 'risk analysis', 'what might fail', 'enumerate the risks', 'likelihood and severity' → risks. Distinct from "
        "adversarial method (adversarial = construct attacks to stress-test; risks = enumerate and assess failure modes and their likelihood).",
        "robust": "Deep-uncertainty decision-making: user wants to choose options that perform acceptably across many plausible futures rather than optimizing for a single forecast. Heuristic: "
        "'robust to uncertainty', 'works across scenarios', 'hedge against uncertainty', 'perform across many futures', 'uncertainty-aware decision', 'which option survives the most "
        "scenarios', 'resilient to unknowns', 'option value under uncertainty' → robust. Distinct from resilience method (resilience = system behavior under stress; robust = select "
        "options that perform across uncertain futures).",
        "shift": "Perspective rotation: user wants the same facts reinterpreted through several distinct frames or cognitive modes to surface what each reveals. Heuristic: 'look at this from "
        "multiple angles', 'different perspectives', 'rotate through lenses', 'six thinking hats', 'shift perspectives', 'what would X think about this', 'see it through different "
        "frames', 'consider multiple viewpoints' → shift. Distinct from models method (models = apply named mental models; shift = rotate through distinct cognitive modes or stakeholder "
        "perspectives).",
        "simulation": "Thought-experiment enrichment for feedback loop and emergent effect analysis: user wants to project systemic dynamics through an analytical lens. Heuristic: 'run a thought "
        "experiment', 'trace feedback loops', 'where would bottlenecks emerge', 'tipping point analysis', 'what emergent effects would arise', 'project systemic dynamics', 'model "
        "how effects compound over time' → simulation method. Distinct from sim task (sim = standalone scenario narrative of what unfolds; simulation method = enriches probe/plan "
        "with thought-experiment reasoning about feedback loops, tipping points, and emergent system behaviour). Distinct from boom (boom = scale extremes; simulation = systemic "
        "feedback dynamics).",
        "spec": "Correctness criteria before implementation: user wants explicit success criteria defined first, with implementation required to satisfy the prior specification. Heuristic: "
        "'define the spec first', 'test-driven design', 'what should it do before how', 'specification before implementation', 'write the tests first', 'define success criteria', 'TDD', "
        "'correctness criteria' → spec. Distinct from grow method (grow = evolve incrementally from minimal; spec = define the target criteria first and measure compliance against them).",
        "split": "Deliberate decomposition into isolated parts: user wants the subject broken into components for separate analysis before considering interactions. Heuristic: 'break this into "
        "parts', 'decompose', 'analyze each component separately', 'isolate the pieces', 'divide and analyze', 'separate concerns', 'split into sub-problems', 'analyze in isolation' → "
        "split. Distinct from dimension method (dimension = surface analytical axes; split = decompose into component parts for provisional isolated analysis).",
        "systemic": "Whole-system feedback loop and emergent behavior analysis: user wants to understand the subject as an interacting whole, not just its parts. Heuristic: 'systems thinking', "
        "'feedback loops', 'emergent behavior', 'system as a whole', 'how do the parts interact', 'unintended consequences', 'second order effects across the system', "
        "'interconnections' → systemic. Distinct from analysis method (analysis = describe and structure; systemic = reason about interactions and emergence).",
        "trade": "Trade-off analysis across competing forces: user wants to identify competing design pressures or structural forces, make the trade-offs explicit, and evaluate alternatives "
        "across those dimensions before committing to a configuration. Heuristic: 'what are the trade-offs', 'weigh the options', 'competing forces', 'design trade-offs', 'pros and cons "
        "of each approach', 'alternative configurations', 'what are we trading off', 'evaluate alternatives across dimensions' → trade. Distinct from balance method (balance = how "
        "opposing forces offset to produce equilibrium; trade = explicitly identify and evaluate trade-offs across competing dimensions).",
        "trans": "Information fidelity and signal degradation analysis: user asks where data or signal is lost, distorted, delayed, or degraded as it passes through a system. Heuristic: 'where "
        "does signal get lost', 'where does data degrade', 'signal fidelity', 'where is information lost in transmission', 'where does the message get distorted', 'trace signal path "
        "through the system', 'where does noise enter', 'signal-to-noise', 'observability pipeline fidelity' → trans. Distinct from flow method (flow = narrate step-by-step sequence; "
        "trans = model noise, distortion, and fidelity across stages).",
        "triage": "Risk-gradient triage: user wants analytical depth allocated proportionally to consequence×uncertainty — the most dangerous or uncertain areas get the most thorough treatment. "
        "Heuristic: 'focus on the high-risk areas', 'triage by impact and uncertainty', 'risk-proportionate depth', 'where are the stakes highest', 'most dangerous parts first', "
        "'consequence-weighted review', 'allocate attention by risk', 'what deserves the most scrutiny', 'protect the high-stakes areas' → triage method. Can pair with risks method "
        "(risks = find what could go wrong; triage = calibrate how deeply to examine each based on consequence×uncertainty).",
        "unknowns": "Unknown unknowns surfacing: user wants to identify what has not been asked, what gaps in knowledge could impact outcomes, and what critical uncertainties have not been "
        "named. Heuristic: 'what are we missing', 'what don\\'t we know that we don\\'t know', 'unknown unknowns', 'what questions haven\\'t we asked', 'critical blind spots', "
        "'what\\'s not on our radar', 'gaps in our knowledge', 'what could surprise us' → unknowns. Distinct from assume scope (assume = make explicit premises already held; unknowns "
        "= surface what has not yet been considered or named).",
        "verify": "Falsification pressure: user wants claims tested against evidence, causal chain integrity, and clearly defined negative space before accepting conclusions. Heuristic: 'verify "
        "this', 'check your reasoning', 'apply falsification', 'is this actually true', 'challenge the claims', 'what would falsify this', 'pressure-test the conclusions', 'don\\'t "
        "just assert — verify', 'what evidence would disprove this' → verify. Distinct from rigor method (rigor = disciplined reasoning process; verify = apply explicit falsification "
        "to the outputs).",
    },
    "scope": {
        "act": "Actions and intended operations focus: user asks what is being done or needs to be done, not why or how it is structured. Heuristic: 'what actions', 'what operations are "
        "involved', 'what tasks are performed', 'what does it actually do', 'what work is happening', 'what are the intended operations', 'the activities it performs' → act scope. Distinct "
        "from thing scope (thing = what entities are involved; act = what those entities are doing or performing).",
        "agent": "Decision-making or agency focus: user asks who can act, who has authority, or how choices are made between actors. Heuristic: 'who decides', 'who has authority', 'who can "
        "approve', 'decision-making', 'agency', 'who is responsible' → agent scope. Note: agent is a SCOPE token (foregrounds decision-making actors); actors is a METHOD token (enriches "
        "any task with actor-centered analysis). Both can be selected together.",
        "assume": "Assumptions and premises focus: user asks what must be true, what is taken for granted, or what preconditions are embedded in the design. Heuristic: 'what assumptions', 'what "
        "are we assuming', 'what must be true', 'what preconditions', 'hidden assumptions', 'what are we taking for granted' → assume scope. Distinct from unknowns method (unknowns = "
        "surfaces what we don't know we don't know; assume = makes explicit what is already assumed).",
        "cross": "Cross-cutting concerns spanning the system: user asks about a concern that appears across many unrelated modules (logging, error handling, auth, observability). Heuristic: "
        "'scattered across', 'spans multiple services', 'consistent across', 'cross-cutting', 'appears throughout', 'horizontal concern', 'error handling across our codebase', 'where "
        "does X live across the system' → cross scope. Distinct from motifs scope (motifs = structural patterns that repeat; cross = concerns that PROPAGATE and SPAN across module "
        "boundaries).",
        "fail": "Failure modes, breakdowns, and limits focus: user asks how and when something stops working, what the edge cases are, or where fragility lives. Heuristic: 'failure modes', 'where "
        "does it break', 'what are the edge cases', 'what can go wrong', 'under what conditions does it fail', 'limits', 'fragility', 'what stress would break this' → fail scope. Often "
        "pairs with good scope (good + fail = quality and failure mode dimensions together). Distinct from risks method (risks = likelihood and severity of bad outcomes; fail = the scope "
        "of breakdown conditions).",
        "good": "Quality criteria or success standards focus: user asks what makes something good, what criteria matter, or how to judge quality. Heuristic: 'quality criteria', 'what makes it "
        "good', 'how to judge', 'success criteria', 'well-designed', 'what good looks like', 'standards for', 'what does success look like' → good scope. Often pairs with fail scope (good "
        "+ fail = quality and failure mode dimensions).",
        "mean": "Conceptual framing and definitional focus: user asks what something means, how it is understood, or what its purpose is before evaluating or acting. Heuristic: 'what does X "
        "mean', 'how should I think about', 'what is the purpose of', 'how is this concept defined', 'how is this categorized', 'what does this term refer to', 'how do we conceptualize "
        "this', 'theoretical framing' → mean scope. Distinct from good scope (good = how to judge quality; mean = conceptual framing before evaluation).",
        "motifs": "Recurring or repeated patterns across the codebase or system: user asks about structures or idioms that appear in multiple places. Heuristic: 'recurring patterns', 'repeated "
        "across', 'appears in multiple places', 'common idioms', 'what keeps showing up', 'same pattern in different places' → motifs scope. Distinct from struct (one system's internal "
        "arrangement) and mapping method (surface all elements/relationships).",
        "stable": "Stability and persistence focus: user asks what is stable, unlikely to change, or self-reinforcing in the system or design. Heuristic: 'stable', 'unlikely to change', 'won't "
        "change', 'what persists', 'what is settled', 'fixed constraints', 'what has remained stable', 'backward-compatible' → stable scope. Often pairs with time scope (stable = what "
        "persists; time = how things evolve).",
        "struct": "Internal arrangement and dependency focus: user asks how parts of a system relate and are organized — the internal topology, not cross-cutting span. Heuristic: 'how is it "
        "structured', 'what are the dependencies', 'how are the components organized', 'internal architecture', 'how do the parts relate', 'what holds it together', 'the coordination "
        "and constraints inside' → struct scope. Distinct from cross scope (cross = horizontal span across module boundaries; struct = internal topology and arrangement within units).",
        "thing": "Entity and bounded unit focus: user asks what objects, roles, systems, or domains are in scope — what the relevant entities are. Heuristic: 'what entities', 'what are the main "
        "objects', 'what roles are involved', 'what systems are in scope', 'what are the bounded domains', 'what things exist here', 'name the components', 'what are we talking about' → "
        "thing scope. Distinct from act scope (act = what entities are doing; thing = what entities exist).",
        "time": "Temporal or sequential focus: user asks about sequence, history, phases, or how something changes over time. Heuristic: 'step by step', 'in order', 'over time', 'what happens "
        "when', 'sequence', 'timeline', 'history', 'how did we get here', 'phases' → time scope. Distinct from flow method (flow = reasoning approach; time = scope dimension to "
        "emphasize).",
        "view": "Stakeholder or positional perspective focus: user asks how the subject appears from a specific role or vantage point. Heuristic: 'from the user\\'s perspective', 'from the "
        "manager\\'s point of view', 'how does the team see this', 'from a security perspective', 'how does this look to stakeholders', 'from a customer\\'s view', 'through the lens of' → "
        "view scope. Distinct from agent scope (agent = who has decision-making authority; view = how the subject appears from a specific vantage point).",
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
        "gherkin": "瓜",
        "html": "標",
        "jira": "票",
        "plain": "文",
        "presenterm": "演",
        "remote": "遠",
        "shellscript": "脚",
        "sketch": "描",
        "slack": "通",
        "svg": "画",
        "sync": "期",
    },
    "completeness": {
        "deep": "深",
        "full": "全",
        "gist": "略",
        "max": "尽",
        "minimal": "小",
        "narrow": "狭",
        "skim": "掠",
    },
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
        "direct": "直",
        "facilitate": "促",
        "faq": "質",
        "formats": "様",
        "indirect": "間",
        "ladder": "階",
        "log": "誌",
        "merge": "合",
        "questions": "問",
        "quiz": "試",
        "recipe": "法",
        "scaffold": "足",
        "socratic": "導",
        "spike": "査",
        "story": "話",
        "table": "表",
        "taxonomy": "別",
        "test": "験",
        "tight": "簡",
        "variants": "変",
        "visual": "絵",
        "walkthrough": "歩",
        "wardley": "鎖",
        "wasinawa": "振",
    },
    "method": {
        "abduce": "因",
        "actors": "者",
        "adversarial": "攻",
        "afford": "構",
        "analog": "類",
        "analysis": "析",
        "argue": "論",
        "balance": "均",
        "bias": "偏",
        "boom": "極",
        "bound": "限",
        "branch": "枝",
        "calc": "計",
        "canon": "準",
        "cite": "引",
        "cluster": "集",
        "compare": "較",
        "converge": "収",
        "deduce": "演",
        "depends": "依",
        "diagnose": "診",
        "dimension": "次",
        "domains": "領",
        "effects": "効",
        "experimental": "実",
        "explore": "探",
        "field": "場",
        "flow": "流",
        "gap": "隙",
        "grove": "蓄",
        "grow": "増",
        "induce": "帰",
        "inversion": "逆",
        "jobs": "需",
        "mapping": "写",
        "meld": "融",
        "melody": "旋",
        "mod": "周",
        "models": "型",
        "objectivity": "客",
        "operations": "営",
        "order": "順",
        "origin": "起",
        "polar": "磁",
        "prioritize": "優",
        "probability": "確",
        "product": "商",
        "reify": "形",
        "resilience": "耐",
        "rigor": "厳",
        "risks": "危",
        "robust": "堅",
        "shift": "転",
        "simulation": "象",
        "spec": "規",
        "split": "分",
        "systemic": "系",
        "trade": "衡",
        "trans": "伝",
        "triage": "険",
        "unknowns": "未",
        "verify": "証",
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
            "as junior engineer": "初",
            "as principal engineer": "纂",
            "as programmer": "程",
            "as prompt engineer": "吟",
            "as scientist": "科",
            "as teacher": "教",
            "as writer": "著",
        },
    },
    "scope": {
        "act": "為",
        "agent": "主",
        "assume": "仮",
        "cross": "横",
        "fail": "敗",
        "good": "良",
        "mean": "意",
        "motifs": "紋",
        "stable": "安",
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
        "analog": "Generative",
        "analysis": "Structural",
        "argue": "Reasoning",
        "balance": "Comparative",
        "bias": "Reasoning",
        "boom": "Exploration",
        "bound": "Structural",
        "branch": "Exploration",
        "calc": "Reasoning",
        "canon": "Structural",
        "cite": "Reasoning",
        "cluster": "Structural",
        "compare": "Comparative",
        "converge": "Comparative",
        "deduce": "Reasoning",
        "depends": "Structural",
        "diagnose": "Diagnostic",
        "dimension": "Comparative",
        "domains": "Exploration",
        "effects": "Temporal/Dynamic",
        "experimental": "Exploration",
        "explore": "Exploration",
        "field": "Actor-centered",
        "flow": "Temporal/Dynamic",
        "gap": "Structural",
        "grove": "Generative",
        "grow": "Generative",
        "induce": "Reasoning",
        "inversion": "Diagnostic",
        "jobs": "Actor-centered",
        "mapping": "Structural",
        "meld": "Comparative",
        "melody": "Generative",
        "mod": "Generative",
        "models": "Generative",
        "objectivity": "Reasoning",
        "operations": "Temporal/Dynamic",
        "order": "Structural",
        "origin": "Structural",
        "polar": "Comparative",
        "prioritize": "Comparative",
        "probability": "Reasoning",
        "product": "Generative",
        "reify": "Generative",
        "resilience": "Diagnostic",
        "rigor": "Reasoning",
        "risks": "Diagnostic",
        "robust": "Diagnostic",
        "shift": "Generative",
        "simulation": "Temporal/Dynamic",
        "spec": "Structural",
        "split": "Exploration",
        "systemic": "Temporal/Dynamic",
        "trade": "Comparative",
        "trans": "Temporal/Dynamic",
        "triage": "Diagnostic",
        "unknowns": "Diagnostic",
        "verify": "Reasoning",
    }
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
        "gherkin": "Gherkin scenarios",
        "html": "HTML output",
        "jira": "Jira formatting",
        "plain": "Plain prose",
        "presenterm": "Slide deck",
        "remote": "Remote delivery",
        "shellscript": "Shell script",
        "sketch": "D2 diagram",
        "slack": "Slack formatting",
        "svg": "SVG output",
        "sync": "Session plan",
    },
    "completeness": {
        "deep": "Deep dive",
        "full": "Complete coverage",
        "gist": "Summary",
        "max": "Exhaustive treatment",
        "minimal": "Minimal answer",
        "narrow": "Narrow focus",
        "skim": "Quick pass",
    },
    "directional": {
        "bog": "Reflect + act",
        "dig": "Concrete/specific",
        "dip bog": "Concrete, reflect, act",
        "dip ong": "Concrete then act",
        "dip rog": "Concrete then reflect",
        "fig": "Abstract + concrete",
        "fip bog": "Full range, reflect, act",
        "fip ong": "Full range, then act",
        "fip rog": "Full range, then reflect",
        "fly bog": "Abstract, reflect, act",
        "fly ong": "Abstract then act",
        "fly rog": "Abstract then reflect",
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
        "direct": "Lead with conclusion",
        "facilitate": "Facilitation plan",
        "faq": "FAQ format",
        "formats": "Format comparison",
        "indirect": "Background then conclusion",
        "ladder": "Abstraction ladder",
        "log": "Work log entry",
        "merge": "Combine sources",
        "questions": "Probing questions",
        "quiz": "Quiz structure",
        "recipe": "Step-by-step guidance",
        "scaffold": "Building understanding",
        "socratic": "Question-led inquiry",
        "spike": "Research spike",
        "story": "User story",
        "table": "Structured comparison",
        "taxonomy": "Classification system",
        "test": "Test cases",
        "tight": "Concise prose",
        "variants": "Multiple alternatives",
        "visual": "Visual/spatial layout",
        "walkthrough": "Step-by-step guidance",
        "wardley": "Wardley map",
        "wasinawa": "What/So What/Now What",
    },
    "method": {
        "abduce": "Best explanation",
        "actors": "People/roles",
        "adversarial": "Stress test",
        "afford": "Structural affordances",
        "analog": "Reasoning by analogy",
        "analysis": "Decompose components",
        "argue": "Formal argument",
        "balance": "Equilibrium forces",
        "bias": "Cognitive biases",
        "boom": "Extreme scale behavior",
        "branch": "Multiple paths",
        "calc": "Formal calculation",
        "canon": "Single source of truth",
        "cite": "Evidence/sources",
        "cluster": "Group/categorize",
        "compare": "Side-by-side comparison",
        "converge": "Narrow to recommendation",
        "deduce": "Logical deduction",
        "depends": "Dependency tracing",
        "diagnose": "Root cause",
        "dimension": "Multiple dimensions",
        "domains": "Bounded contexts",
        "effects": "Second-order effects",
        "experimental": "Design experiments",
        "explore": "Open option space",
        "field": "Structural field effects",
        "flow": "Step-by-step flow",
        "gap": "Implicit gaps",
        "grove": "Compounding effects",
        "grow": "Expand only when needed",
        "induce": "Generalise from examples",
        "inversion": "Start from failure",
        "jobs": "Jobs to be done",
        "mapping": "Spatial map",
        "meld": "Combinations/overlaps",
        "melody": "Coordination across parts",
        "mod": "Cyclic/periodic patterns",
        "models": "Named mental models",
        "objectivity": "Facts vs opinions",
        "operations": "Operations research",
        "order": "Abstract ordering",
        "origin": "Historical causation",
        "polar": "Attractors/repellers",
        "prioritize": "Rank by importance",
        "probability": "Statistical reasoning",
        "product": "Product lens",
        "reify": "Make implicit explicit",
        "resilience": "Stress and fragility",
        "rigor": "Disciplined reasoning",
        "risks": "Potential problems",
        "robust": "Works across futures",
        "shift": "Rotate perspectives",
        "simulation": "Scenario walkthrough",
        "spec": "Governing constraints",
        "split": "Decompose in isolation",
        "systemic": "System as whole",
        "trade": "Structural tradeoffs",
        "trans": "Communication transmission",
        "triage": "Risk-gradient depth",
        "unknowns": "Unknown unknowns",
        "verify": "Falsification pressure",
    },
    "scope": {
        "act": "Actions/tasks",
        "agent": "Actors with agency",
        "assume": "Premises/preconditions",
        "cross": "Cross-cutting concerns",
        "fail": "Failure modes",
        "good": "Quality/criteria",
        "mean": "Understanding/meaning",
        "motifs": "Recurring patterns",
        "stable": "Invariants/stable states",
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
CROSS_AXIS_COMPOSITION: Dict[str, Dict[str, Dict[str, Any]]] = {
    "channel": {
        "shellscript": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull"],
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
        "adr": {"task": {"natural": ["plan", "probe", "make"]}},
        "sync": {
            "completeness": {
                "natural": ["full", "minimal", "gist"],
                "cautionary": {
                    "max": "tends to be unusable — session plans require practical brevity; max treats omissions as errors and produces overloaded agendas; use full "
                    "or minimal instead"
                },
            }
        },
        "code": {
            "task": {
                "natural": ["make", "fix", "show", "trans", "pull", "check"],
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
        "codetour": {
            "task": {
                "natural": ["make", "fix", "show", "pull"],
                "cautionary": {
                    "sim": "tends to be incoherent — simulation is narrative with no code subject to navigate",
                    "sort": "tends to be incoherent — sorted items have no navigable code structure",
                },
            }
        },
        "gherkin": {"task": {"natural": ["make", "check"]}},
    },
    "form": {
        "commit": {
            "completeness": {
                "natural": ["gist", "minimal"],
                "cautionary": {
                    "max": "tends to produce truncated or overloaded messages — commit format has no room for depth; use gist or minimal instead",
                    "deep": "same constraint as max — the format cannot accommodate deep analysis; use gist or minimal instead",
                },
            }
        }
    },
}


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


def axis_key_to_guidance_map(axis: str) -> dict[str, str]:
    """Return the key->guidance map for a given axis (ADR-0110)."""
    return AXIS_KEY_TO_GUIDANCE.get(axis, {})


def axis_key_to_use_when_map(axis: str) -> dict[str, str]:
    """Return the key->use_when map for a given axis (ADR-0132)."""
    return AXIS_KEY_TO_USE_WHEN.get(axis, {})


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


def axis_key_to_routing_concept_map(axis: str) -> dict[str, str]:
    """Return the key->routing_concept map for a given axis (ADR-0146).

    Returns per-token distilled routing concept phrases. Tokens sharing the same
    phrase form a multi-token routing bullet (e.g. thing+struct → 'Entities/boundaries').
    """
    return AXIS_KEY_TO_ROUTING_CONCEPT.get(axis, {})


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
        "command": 'bar build diff thing full branch variants --subject "..."',
        "example": 'bar build diff thing full branch variants --subject "Choose between Redis and Postgres for caching"',
        "desc": "Use when choosing between options or evaluating alternatives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["branch"],
            "scope": ["thing"],
            "task": ["diff"],
        },
    },
    {
        "title": "Architecture Documentation",
        "command": 'bar build make struct full explore case --subject "..."',
        "example": 'bar build make struct full explore case --subject "Document the microservices architecture"',
        "desc": "Use for creating ADRs or documenting architectural decisions",
        "tokens": {
            "completeness": ["full"],
            "form": ["case"],
            "method": ["explore"],
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
        "command": 'bar build probe thing full explore variants --subject "..."',
        "example": 'bar build probe thing full explore variants --subject "What are different approaches to state management?"',
        "desc": "Use when surveying possibilities or generating alternatives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["explore"],
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
        "command": 'bar build probe thing gist explore variants --subject "..." && bar build probe struct full mapping table --subject "..."',
        "example": 'bar build probe thing gist explore variants --subject "API design approaches" && bar build probe struct full mapping table --subject "Selected REST API structure"',
        "desc": "Use for multi-step workflows: explore broadly, then analyze deeply",
        "tokens": {
            "completeness": ["gist"],
            "form": ["variants"],
            "method": ["explore"],
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
        "command": 'bar build make good full analysis checklist --subject "..."',
        "example": 'bar build make good full analysis checklist --subject "Define success criteria for the dashboard redesign"',
        "desc": "Use when establishing measurable quality or success standards",
        "tokens": {
            "completeness": ["full"],
            "form": ["checklist"],
            "method": ["analysis"],
            "scope": ["good"],
            "task": ["make"],
        },
    },
    {
        "title": "Perspective Analysis",
        "command": 'bar build probe view full explore variants --subject "..."',
        "example": 'bar build probe view full explore variants --subject "How do different stakeholders view the monolith migration?"',
        "desc": "Use for understanding multiple viewpoints or stakeholder perspectives",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["explore"],
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
        "command": 'bar build make thing full cite case --subject "..."',
        "example": 'bar build make thing full cite case --subject "Build the case for adopting TypeScript"',
        "desc": "Use when making a persuasive argument with supporting evidence",
        "tokens": {
            "completeness": ["full"],
            "form": ["case"],
            "method": ["cite"],
            "scope": ["thing"],
            "task": ["make"],
        },
    },
    {
        "title": "Option Generation with Reasoning",
        "command": 'bar build probe thing full branch variants --subject "..."',
        "example": 'bar build probe thing full branch variants --subject "Generate database sharding approaches with pros/cons"',
        "desc": "Use for generating alternatives with detailed reasoning for each",
        "tokens": {
            "completeness": ["full"],
            "form": ["variants"],
            "method": ["branch"],
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
        "command": 'bar build pull gist mean --subject "..."',
        "example": 'bar build pull gist mean --subject "[long RFC or design document]"',
        "desc": "Use when compressing a long source document into a shorter summary. Prefer pull over show when a SUBJECT document is being compressed: pull extracts a subset, show explains a concept. Heuristic: long SUBJECT to compress → pull; concept to explain without a source → show.",
        "tokens": {"completeness": ["gist"], "scope": ["mean"], "task": ["pull"]},
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
