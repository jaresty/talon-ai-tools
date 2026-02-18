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
from typing import Dict, FrozenSet

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": "The response takes the shape of an Architecture Decision Record "
        "(ADR) document with sections for context, decision, and "
        "consequences, formatted as a structured document ready for "
        "version control.",
        "code": "The response consists only of code or markup as the complete "
        "output, with no surrounding natural-language explanation or "
        "narrative.",
        "codetour": "The response is delivered as a valid VS Code CodeTour "
        "`.tour` JSON file (schema-compatible) with steps and fields "
        "appropriate to the task, omitting extra prose or surrounding "
        "explanation.",
        "diagram": "The response converts the input into Mermaid diagram code "
        "only: it infers the best diagram type for the task and "
        "respects Mermaid safety constraints (Mermaid diagrams do not "
        "allow parentheses in the syntax or raw '|' characters inside "
        'node labels; the text uses numeric encodings such as "#124;" '
        "for '|' instead of raw problematic characters).",
        "gherkin": "The response outputs only Gherkin format as the complete "
        "output, using Jira markup where appropriate and omitting "
        "surrounding explanation. Works with presenterm/diagram "
        "channels when wrapped in markdown code blocks.",
        "html": "The response consists solely of semantic HTML as the complete "
        "output, with no surrounding prose or explanation.",
        "jira": "The response formats the content using Jira markup (headings, "
        "lists, panels) where relevant and avoids extra explanation "
        "beyond the main material.",
        "plain": "The response uses plain prose with natural paragraphs and "
        "sentences as the delivery format, imposing no additional "
        "structural conventions such as bullets, tables, or code blocks.",
        "presenterm": "The response is a valid multi-slide presenterm deck "
        "expressed as raw Markdown (no code fences). The front "
        'matter always matches: "--- newline title: <descriptive '
        "title based on the input with colons encoded as &#58; and "
        "angle brackets encoded as &lt; and &gt;> newline author: "
        "Generated (or authors: [...]) newline date: YYYY-MM-DD "
        'newline --- newline" with no other keys. The deck contains '
        "up to 12 slides. Each slide starts with a Setext header "
        "(title line followed by a line of ---), includes content "
        "and references, and ends with an HTML comment named "
        "end_slide on its own line followed by a blank line; the "
        "final slide may omit the closing end_slide. A blank line "
        "always precedes the References section so that a line with "
        '"References" or "- References" is separated by one empty '
        "line. Directives appear only as standalone HTML comments "
        'with exact syntax: "<!-- end_slide -->", "<!-- pause -->", '
        '"<!-- column_layout: [7, 3] -->", "<!-- column: 0 -->", '
        '"<!-- reset_layout -->", and "<!-- jump_to_middle -->". '
        "Code fence safety is enforced: whenever a fenced code "
        "block opens (for example ```mermaid +render, ```bash "
        "+exec, ```latex +render, ```d2 +render), the response "
        "includes a matching closing fence of exactly three "
        "backticks on its own line before any non-code content, "
        "directive, or end_slide; if a fence remains open at slide "
        "end, the response emits the closing fence first. Mermaid "
        "diagrams use code blocks tagged mermaid +render; LaTeX "
        "uses latex +render; D2 uses d2 +render; executable "
        "snippets use fenced code blocks whose info string starts "
        "with a language then +exec (optionally +id:<name>) or "
        '+exec_replace or +image. The response emits "<!-- '
        'snippet_output: name -->" only when a snippet with '
        "+id:name exists. Lines hidden with # or /// prefixes "
        "follow language conventions; other code blocks appear only "
        "when relevant and include the language name; images appear "
        "only when valid paths or URLs exist. Within the slide body "
        "(outside fenced or inline code and outside HTML "
        "directives), the deck never includes raw HTML: every "
        "literal '<' becomes &lt; and every literal '>' becomes "
        "&gt;, preventing raw angle brackets in body text. Markdown "
        "safety prevents accidental styling: standalone or "
        'path-embedded \'~\' becomes "&#126;" (so "~/foo" becomes '
        '"&#126;/foo") while intentional "~~text~~" remains '
        "unchanged. Mermaid safety keeps grammar and delimiters "
        "intact ([], (), [[]], (()), [/ /]); node and edge labels "
        "appear inside ASCII double quotes and use "
        "Mermaid-compatible numeric codes with no leading "
        'ampersand, such as "#91;" for "[", "#93;" for "]", "#40;" '
        'for "(", "#41;" for ")", "#123;" for "{{", "#125;" for '
        '"}}", "#60;" for "<", "#62;" for ">", "#35;" for "#", '
        '"#58;" for ":", and "&" and slashes \'/\' remain as-is, '
        "with no additional entity encodings, and labels are never "
        "double-encoded. The deck avoids # headers in slide bodies.",
        "remote": "The response is optimised for remote delivery, ensuring "
        "instructions work in distributed or online contexts and "
        "surfacing tooling or interaction hints suitable for video, "
        "voice, or screen sharing.",
        "shellscript": "The response is delivered as a shell script output "
        "format, focusing on correct, executable shell code rather "
        "than prose or explanation.",
        "sketch": "The response emits only pure D2 diagram source as the complete "
        "output. The response must use valid D2 syntax and only "
        "documented D2 shapes (e.g., rectangle, circle, cylinder, "
        "diamond, hexagon, cloud, text). To create visually distinct "
        "boxes, use 'border-radius' or style attributes instead of "
        "non-existent shapes like 'rounded' or 'note'. Explanatory or "
        "note-like content must be modeled using shape: text or a "
        "styled standard shape. Do not include any surrounding natural "
        "language or commentary. Ensure the output is syntactically "
        "correct and compiles successfully with the D2 CLI.",
        "slack": "The response formats the answer for Slack using appropriate "
        "Markdown, mentions, and code blocks while avoiding "
        "channel-irrelevant decoration.",
        "svg": "The response consists solely of SVG markup as the complete "
        "output, with no surrounding prose, remaining minimal and valid "
        "for direct use in an `.svg` file.",
        "sync": "The response takes the shape of a synchronous or live session "
        "plan (agenda, steps, cues) rather than static reference text.",
    },
    "completeness": {
        "deep": "The response goes into substantial depth within the chosen "
        "scope, unpacking reasoning layers and fine details without "
        "necessarily enumerating every edge case.",
        "full": "The response provides a thorough answer for normal use, "
        "covering all major aspects without needing every "
        "micro-detail.",
        "gist": "The response offers a short but complete answer or summary "
        "that touches the main points once without exploring every "
        "detail.",
        "max": "The response is as exhaustive as reasonable, covering "
        "essentially everything relevant and treating omissions as "
        "errors.",
        "minimal": "The response makes the smallest change or provides the "
        "smallest answer that satisfies the request, avoiding "
        "work outside the core need.",
        "narrow": "The response restricts the discussion to a very small "
        "slice of the topic, avoiding broad context.",
        "skim": "The response performs only a very light pass, addressing "
        "the most obvious or critical issues without aiming for "
        "completeness.",
    },
    "directional": {
        "bog": "The response modifies the task to examine the subject's "
        "structure and reflect on it, then identifies actions to take "
        "and extends them to related contexts.",
        "dig": "The response modifies the task to examine concrete details "
        "and grounding examples, focusing on specifics rather than "
        "abstractions.",
        "dip bog": "The response modifies the task to start with concrete "
        "examples and grounded details, examines their structure "
        "and reflects on patterns, then identify actions and "
        "extensions.",
        "dip ong": "The response modifies the task to start with concrete "
        "examples, identify actions to take from them, then "
        "extends those actions to related situations.",
        "dip rog": "The response modifies the task to examine concrete "
        "details and grounded examples, then reflects on their "
        "structural patterns and what they reveal.",
        "fig": "The response modifies the task to alternate between abstract "
        "principles and concrete examples, using each to illuminate "
        "the other (figure-ground reversal).",
        "fip bog": "The response modifies the task to move between abstract "
        "principles and concrete examples, examines their "
        "structural patterns and reflects on them, then identifies "
        "actions and extends them to related contexts.",
        "fip ong": "The response modifies the task to alternate between "
        "abstract principles and concrete examples, then "
        "identifies actions to take and extends them to related "
        "situations.",
        "fip rog": "The response modifies the task to move between abstract "
        "principles and concrete examples while examining "
        "structural patterns and reflecting on what they reveal.",
        "fly bog": "The response modifies the task to identify abstract "
        "patterns and general principles, examine their structure "
        "and reflects on it, then identifies actions and extends "
        "them to related contexts.",
        "fly ong": "The response modifies the task to identify abstract "
        "patterns and general principles, then propose concrete "
        "actions and extends them to related contexts.",
        "fly rog": "The response modifies the task to identify abstract "
        "patterns and general principles, then examines their "
        "structural relationships and reflect on their "
        "implications.",
        "fog": "The response modifies the task to identify general patterns "
        "and abstract principles from the specifics, moving from "
        "particular cases to broader insights.",
        "jog": "The response modifies the task to interpret the intent and "
        "carry it out directly without asking follow-up questions.",
        "ong": "The response modifies the task to identify concrete actions "
        "to take, then extends those actions to related situations or "
        "next steps.",
        "rog": "The response modifies the task to examine the structure of "
        "the subject (how it is organized), then reflects on why that "
        "structure exists and what it reveals.",
    },
    "form": {
        "actions": "The response structures ideas as concrete actions or tasks a "
        "user or team could take, leaving out background analysis or "
        "explanation.",
        "activities": "The response organizes ideas as concrete session activities "
        "or segments—what to do, by whom, and in what order—rather "
        "than abstract description.",
        "bug": "The response structures ideas as a bug report with sections for "
        "Steps to Reproduce, Expected Behavior, Actual Behavior, and "
        "Environment or Context, emphasizing concise, testable details. "
        "Strongest with diagnostic and debugging tasks (`probe`, or "
        "`make`/`show` paired with diagnostic methods: `diagnose`, "
        "`inversion`, `adversarial`). Creates semantic friction with "
        "non-debugging tasks (e.g., `fix`, which is a reformat task in bar's "
        "grammar). Conflicts with session-plan channels (`sync`) — a bug "
        "report is a static artifact, not a live session agenda.",
        "bullets": "The response organizes ideas as concise bullet points, avoiding "
        "long paragraphs.",
        "cards": "The response organizes ideas as discrete cards or items, each with "
        "a clear heading and short body, avoiding long continuous prose.",
        "case": "The response structures reasoning by building the case before the "
        "conclusion, laying out background, evidence, trade-offs, and "
        "alternatives before converging on a clear recommendation that "
        "addresses objections and constraints.",
        "checklist": "The response organizes ideas as an actionable checklist whose "
        "items are clear imperative tasks rather than descriptive "
        "prose.",
        "cocreate": "The response structures itself as a collaborative process — "
        "small moves, explicit decision points, and alignment checks "
        "rather than a one-shot answer. Without an output-exclusive "
        "channel, conducts this interactively: proposes, pauses for "
        "feedback, and iterates. With an output-exclusive channel, "
        "formats the artifact to expose decision points, show "
        "alternative moves, and make the response-inviting structure "
        "visible within the output.",
        "commit": "The response structures ideas as a conventional commit message "
        "with a short type or scope line and an optional concise body.",
        "contextualise": "The response structures ideas by adding or reshaping "
        "context to support another operation—such as supplying "
        "background for an LLM or reframing content—without "
        "rewriting the main text itself. With sort/plan tasks: adds "
        "clarifying context about criteria before output. With "
        "pull: frames extracted content with additional context. "
        "With make/fix: adds framing before the main content.",
        "direct": "The response structures ideas by leading with the main point or "
        "recommendation, followed only by the most relevant supporting "
        "context, evidence, and next steps.",
        "facilitate": "The response structures itself as a facilitation plan — "
        "framing the goal, proposing session structure, managing "
        "participation and turn-taking rather than doing the work "
        "solo. Without an output-exclusive channel, acts as a live "
        "facilitator: proposes structure and invites participation "
        "interactively. With an output-exclusive channel, produces a "
        "static facilitation guide: agenda, goals, cues, and session "
        "structure as a deliverable artifact.",
        "faq": "The response organizes ideas as clearly separated question headings "
        "with concise answers beneath each one, keeping content easy to skim "
        "and free of long uninterrupted prose.",
        "formats": "The response structures ideas by focusing on document types, "
        "writing formats, or structural templates and their suitability.",
        "indirect": "The response begins with brief background, reasoning, and "
        "trade-offs and finishes with a clear bottom-line point or "
        "recommendation that ties them together.",
        "ladder": "The response uses abstraction laddering by placing the focal "
        "problem, stepping up to higher-level causes, and stepping down to "
        "consequences ordered by importance to the audience.",
        "log": "The response reads like a concise work or research log entry with "
        "date or time markers as needed, short bullet-style updates, and "
        "enough context for future reference without unrelated narrative.",
        "merge": "The response combines multiple sources into a single coherent "
        "whole while preserving essential information.",
        "questions": "The response presents the answer as a series of probing or "
        "clarifying questions rather than statements. When combined "
        "with `diagram` channel, the output is Mermaid code structured "
        "as a question tree, decision map, or inquiry flow rather than "
        "a structural diagram of the subject.",
        "quiz": "The response organizes content as a quiz structure — questions "
        "posed before explanations, testing understanding through active "
        "recall before providing answers. Without an output-exclusive "
        "channel, conducts this as an interactive exchange: poses questions, "
        "waits for responses, then clarifies or deepens. With an "
        "output-exclusive channel, structures the output itself as a quiz — "
        "question headings with revealed answers, test sections, knowledge "
        "checks — without requiring live interaction.",
        "recipe": "The response expresses the answer as a recipe that includes a "
        "custom, clearly explained mini-language and a short key for "
        "understanding it.",
        "scaffold": "The response explains with scaffolding: it starts from first "
        "principles, introduces ideas gradually, uses concrete examples "
        "and analogies, and revisits key points so a learner can follow "
        "and retain the concepts. Most effective with learning-oriented "
        "audiences (student, entry-level engineer). May conflict with "
        "expert-level or brevity-first personas where first-principles "
        "exposition contradicts assumed expertise.",
        "socratic": "The response employs a Socratic, question-led method by asking "
        "short, targeted questions that surface assumptions, "
        "definitions, and gaps in understanding, withholding full "
        "conclusions until enough answers exist or the user explicitly "
        "requests a summary. With sort/plan: asks clarifying questions "
        "about criteria before producing output. With make/fix: asks "
        "diagnostic questions then provides the solution. With probe: "
        "naturally extends to deeper inquiry.",
        "spike": "The response formats the backlog item as a research spike: it "
        "starts with a brief problem or decision statement, lists the key "
        "questions the spike should answer, and stays focused on questions "
        "and learning rather than implementation tasks.",
        "story": 'The response formats the backlog item as a user story using "As a '
        '<persona>, I want <capability>, so that <value>." It may include a '
        "short description and high-level acceptance criteria in plain "
        "prose but avoids Gherkin or test-case syntax.",
        "table": "The response presents the main answer as a Markdown table when "
        "feasible, keeping columns and rows compact.",
        "taxonomy": "The response organizes the main content as a classification "
        "system, type hierarchy, or category taxonomy, defining types, "
        "their relationships, and distinguishing attributes clearly. "
        "Adapts to the channel: when combined with a code channel, the "
        "taxonomy is expressed through the type system (interfaces, "
        "enums, inheritance hierarchies); with a markup channel, as "
        "hierarchical markup structure; without a channel, as prose "
        "classification sections.",
        "test": "The response presents test cases in a structured format with clear "
        "setup, execution, and assertion sections, organized by scenario "
        "type (happy path, edge cases, errors, boundaries) and including "
        "descriptive test names.",
        "tight": "The response uses concise, dense prose, remaining freeform without "
        "bullets, tables, or code and avoiding filler.",
        "variants": "The response presents several distinct, decision-ready options "
        "as separate variants, labelling each one with a short "
        "description and including approximate probabilities when "
        "helpful while avoiding near-duplicate alternatives.",
        "visual": "The response presents the main answer as an abstract visual or "
        "metaphorical layout with a short legend where the subject lends "
        "itself to visual representation, emphasising big-picture "
        "structure over dense prose. Adapts to the channel: when combined "
        "with a code channel, visual structure is expressed through code "
        "organization, comments, or inline ASCII; without a channel, "
        "through prose metaphors and spatial layout.",
        "walkthrough": "The response guides the audience step by step by outlining "
        "stages and walking through them in order so understanding "
        "builds gradually.",
        "wardley": "The response expresses the answer as a Wardley Map showing value "
        "chain evolution from genesis to commodity.",
        "wasinawa": "The response applies a What–So What–Now What reflection: it "
        "describes what happened, interprets why it matters, and "
        "proposes concrete next steps.",
    },
    "method": {
        "abduce": "The response enhances the task by generating explanatory "
        "hypotheses that best account for the available evidence, "
        "explicitly comparing alternative explanations.",
        "actors": "The response enhances the task by identifying and centering "
        "people, roles, or agents involved in the system.",
        "adversarial": "The response enhances the task by running a constructive "
        "stress-test, systematically searching for weaknesses, edge "
        "cases, counterexamples, failure modes, and unstated "
        "assumptions.",
        "analog": "The response enhances the task by reasoning through analogy, "
        "mapping relational structure from a known case onto the subject "
        "and examining where the analogy holds or breaks.",
        "analysis": "The response enhances the task by describing and structuring "
        "the situation, focusing on understanding before proposing "
        "actions or recommendations.",
        "argue": "The response enhances the task by structuring reasoning as an "
        "explicit argument, identifying claims, premises, warrants, and "
        "rebuttals and assessing their support.",
        "bias": "The response enhances the task by identifying likely cognitive "
        "biases, heuristics, or systematic errors and examining how they "
        "might distort judgment or conclusions.",
        "boom": "The response enhances the task by exploring behaviour toward "
        "extremes of scale or intensity, examining what breaks, dominates, "
        "or vanishes.",
        "branch": "The response enhances the task by exploring multiple reasoning "
        "paths in parallel, branching on key assumptions or choices "
        "before evaluating and pruning alternatives.",
        "calc": "The response enhances the task by expressing reasoning as "
        "executable or quasi-executable procedures, calculations, or "
        "formal steps whose outputs constrain conclusions.",
        "cite": "The response enhances the task by including sources, citations, "
        "or references that anchor claims to evidence, enabling "
        "verification and further exploration.",
        "cluster": "The response groups or organizes existing items into clusters "
        "based on shared characteristics, relationships, or criteria, "
        "without altering the underlying content or meaning of the "
        "items.",
        "compare": "The response enhances the task by systematically comparing "
        "alternatives against explicit criteria, surfacing tradeoffs, "
        "relative strengths and weaknesses, and decision factors. Use "
        "when the user presents options and asks which to choose or how "
        "they differ.",
        "converge": "The response enhances the task by systematically narrowing "
        "from broad exploration to focused recommendations, weighing "
        "trade-offs explicitly as options are filtered.",
        "deduce": "The response enhances the task by applying deductive reasoning, "
        "deriving conclusions that must follow from stated premises or "
        "assumptions and making logical entailment explicit.",
        "depends": "The response enhances the task by tracing dependency "
        "relationships, identifying what depends on what and how "
        "changes propagate through the system.",
        "diagnose": "The response enhances the task by seeking likely causes of "
        "problems first, narrowing hypotheses through evidence, "
        "falsification pressure, and targeted checks before proposing "
        "fixes or changes.",
        "dimension": "The response enhances the task by exploring multiple "
        "dimensions or axes of analysis, making implicit factors "
        "explicit and examining how they interact.",
        "domains": "The response enhances the task by identifying bounded "
        "contexts, domain boundaries, and capabilities.",
        "effects": "The response enhances the task by tracing second- and "
        "third-order effects and summarizing their downstream "
        "consequences.",
        "experimental": "The response enhances the task by proposing concrete "
        "experiments or tests, outlining how each would run, "
        "describing expected outcomes, and explaining how results "
        "would update the hypotheses.",
        "explore": "The response enhances the task by opening and surveying the "
        "option space, generating and comparing multiple plausible "
        "approaches without prematurely committing to a single answer.",
        "field": "The response models interaction as occurring through a shared "
        "structured medium in which effects arise from structural "
        "compatibility rather than direct reference between actors. "
        "Explanations must make the medium and its selection rules "
        "explicit.",
        "flow": "The response enhances the task by explaining step-by-step "
        "progression over time or sequence, showing how control, data, or "
        "narrative moves through the system.",
        "grove": "The response enhances the task by examining how small effects "
        "compound into larger outcomes through feedback loops, network "
        "effects, or iterative growth—asking not just what fails or "
        "succeeds, but how failures OR successes accumulate through "
        "systemic mechanisms.",
        "grow": "The response enhances the task by preserving the simplest form "
        "adequate to the current purpose and expanding only when new "
        "demands demonstrably outgrow it, so that every abstraction and "
        "every exception arises from necessity rather than anticipation.",
        "induce": "The response enhances the task by applying inductive reasoning, "
        "generalizing patterns from specific observations and assessing "
        "the strength and limits of those generalizations.",
        "inversion": "The response enhances the task by beginning from undesirable "
        "or catastrophic outcomes, asking what would produce or "
        "amplify them, then working backward to avoid, mitigate, or "
        "design around those paths.",
        "jobs": "The response enhances the task by analyzing Jobs To Be Done—the "
        "outcomes users want to achieve and the forces shaping their "
        "choices.",
        "mapping": "The response enhances the task by surfacing elements, "
        "relationships, and structure, then organising them into a "
        "coherent spatial map rather than a linear narrative.",
        "meld": "The response enhances the task by reasoning about combinations, "
        "overlaps, balances, and constraints between elements.",
        "melody": "The response enhances the task by analyzing coordination across "
        "components, time, or teams, including coupling, "
        "synchronization, and change alignment.",
        "mod": "The response enhances the task by applying modulo-style "
        "reasoning—equivalence classes, cyclic patterns, quotient "
        "structures, or periodic behavior that repeats with a defined "
        "period or wraps around boundaries.",
        "models": "The response enhances the task by explicitly identifying and "
        "naming relevant mental models, explaining why they apply (or "
        "fail), and comparing or combining them.",
        "objectivity": "The response enhances the task by distinguishing objective "
        "facts from subjective opinions and supporting claims with "
        "evidence.",
        "operations": "The response enhances the task by identifying operations "
        "research or management science concepts that frame the "
        "situation.",
        "order": "The response enhances the task by applying abstract structural "
        "reasoning such as hierarchy, dominance, or recurrence. When "
        "paired with `sort` task, `order` adds emphasis on the criteria "
        "and scheme driving the sequencing rather than merely producing "
        "the sorted result — consider whether the distinction is needed.",
        "origin": "The response enhances the task by uncovering how the subject "
        "arose, why it looks this way now, and how past decisions shaped "
        "the present state.",
        "prioritize": "The response enhances the task by assessing and ordering "
        "items by importance or impact, making the ranking and "
        "rationale explicit.",
        "probability": "The response enhances the task by applying probability or "
        "statistical reasoning to characterize uncertainty and "
        "likely outcomes.",
        "product": "The response enhances the task by examining the subject "
        "through a product lens—features, user needs, and value "
        "propositions.",
        "resilience": "The response enhances the task by concentrating on how the "
        "system behaves under stress and uncertainty—fragility vs "
        "robustness, margin of safety, and tail risks.",
        "rigor": "The response enhances the task by relying on disciplined, "
        "well-justified reasoning and making its logic explicit.",
        "risks": "The response enhances the task by focusing on potential "
        "problems, failure modes, or negative outcomes and their "
        "likelihood or severity.",
        "robust": "The response enhances the task by reasoning under deep "
        "uncertainty, favoring options that perform acceptably across "
        "many plausible futures rather than optimizing for a single "
        "forecast.",
        "shift": "The response enhances the task by deliberately rotating through "
        "distinct perspectives or cognitive modes, contrasting how each "
        "frame interprets the same facts.",
        "simulation": "The response enhances the task by focusing on explicit "
        "thought experiments or scenario walkthroughs that project "
        "evolution over time, highlighting feedback loops, "
        "bottlenecks, tipping points, and emergent effects.",
        "spec": "The response defines explicit criteria of correctness before "
        "proposing implementations and treats those criteria as fixed and "
        "authoritative. Implementations must satisfy the prior definition "
        "and may not redefine correctness during construction. Progress is "
        "measured by compliance with the specification rather than by "
        "artifact production.",
        "split": "The response enhances the task by deliberately decomposing the "
        "subject into parts or components, analyzing each in isolation "
        "while intentionally bracketing interactions, treating the "
        "decomposition as provisional and preparatory rather than final.",
        "systemic": "The response enhances the task by reasoning about the subject "
        "as an interacting whole, identifying components, boundaries, "
        "flows, feedback loops, and emergent behaviour that arise from "
        "their interactions rather than from parts in isolation.",
        "trans": "The response models information transfer as a staged process "
        "involving a source, encoding, channel, decoding, destination, "
        "and feedback. Explanations must distinguish message from signal, "
        "account for transformation across stages, model noise or "
        "distortion explicitly, and specify mechanisms for detecting and "
        "repairing transmission errors. Outcomes may not be attributed to "
        "communication without specifying how the signal survived, "
        "degraded, or was corrected during transmission.",
        "unknowns": "The response enhances the task by identifying critical "
        "unknown unknowns and exploring how they might impact "
        "outcomes.",
        "verify": "The response enhances the task by applying falsification "
        "pressure to claims, requiring causal chain integrity, "
        "externally imposed constraints, and explicitly defined negative "
        "space. Claims that fail any axis are treated as ungrounded and "
        "must not be synthesized into conclusions or recommendations, "
        "ensuring outputs do not transfer authority or imply trust "
        "beyond the model. This prevents internally coherent but "
        "unconstrained narratives and preserves human oversight as the "
        "source of judgment.",
    },
    "scope": {
        "act": "The response focuses on what is being done or intended—tasks, "
        "activities, operations, or work to be performed—suppressing "
        "interpretation, evaluation, structural explanation, or "
        "perspective-shifting.",
        "agent": "The response explains outcomes in terms of identifiable actors "
        "with the capacity to select among alternatives, specifying who "
        "can act, what options are available, and how their choices "
        "influence results, rather than attributing outcomes solely to "
        "impersonal structure or equilibrium dynamics.",
        "assume": "The response focuses on explicit or implicit premises that must "
        "hold for the reasoning, system, or argument to function.",
        "cross": "The response focuses on concerns or forces that propagate across "
        "otherwise distinct units, layers, or domains—examining how they "
        "traverse boundaries or become distributed across "
        "partitions—without primarily analyzing internal arrangement or "
        "recurring structural form.",
        "fail": "The response focuses on breakdowns, stress, uncertainty, or limits "
        "by examining how and under what conditions something stops "
        "working—risks, edge cases, fragility, or failure modes rather than "
        "overall quality or preferred outcomes.",
        "good": "The response focuses on how quality, success, or goodness is "
        "judged—criteria, metrics, standards, values, or taste—assuming a "
        "framing rather than defining it or shifting perspective.",
        "mean": "The response focuses on how something is conceptually framed or "
        "understood prior to evaluation or action—its purpose, "
        "interpretation, definitions, categorization, or theoretical "
        "role—without asserting required premises, judging quality, "
        "prescribing action, or adopting a specific stakeholder "
        "perspective.",
        "motifs": "The response focuses on recurring structural or thematic forms "
        "that appear in multiple places, identifying repeated "
        "configurations or isomorphic patterns without analyzing their "
        "internal topology in detail or their boundary-spanning "
        "distribution.",
        "stable": "The response focuses on equilibrium, persistence, and "
        "self-reinforcing states within a system—identifying "
        "configurations that maintain themselves and analyzing how "
        "perturbations affect their continuity.",
        "struct": "The response focuses on how parts of a system are arranged and "
        "related—dependencies, coordination, constraints, incentives, or "
        "organizing configurations—analyzing the internal topology of "
        "units without emphasizing repetition across instances or "
        "boundary-spanning propagation.",
        "thing": "The response focuses on what entities are in view—objects, "
        "people, roles, systems, domains, or bounded units—and what is "
        "excluded, without emphasizing actions, relationships, evaluation, "
        "or perspective.",
        "time": "The response focuses on when things occur and how they change over "
        "time—sequences, evolution, history, phases, or temporal "
        "dynamics—rather than static structure, evaluation, or immediate "
        "action.",
        "view": "The response focuses on how the subject appears from a specific "
        "stakeholder, role, or positional perspective, making that "
        "viewpoint explicit without asserting it as definitive, evaluating "
        "outcomes, or prescribing action.",
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
        "bog": "Reflect on structure inward",
        "dig": "Ground in concrete details",
        "dip bog": "Concrete first, examine structure, reflect",
        "dip ong": "Concrete first, then identify actions",
        "dip rog": "Concrete first, then reflect outward",
        "fig": "Alternate between abstract and concrete",
        "fip bog": "Cycle abstract/concrete, examine structure",
        "fip ong": "Cycle abstract/concrete, then act",
        "fip rog": "Cycle abstract/concrete, then reflect",
        "fly bog": "Abstract first, examine structure, reflect",
        "fly ong": "Abstract first, then identify actions",
        "fly rog": "Abstract first, then reflect outward",
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
        "analog": "Reasoning by analogy",
        "analysis": "Describe and structure the situation",
        "argue": "Explicit argument structure",
        "bias": "Identify cognitive biases",
        "boom": "Explore behavior at extremes of scale",
        "branch": "Parallel reasoning paths",
        "calc": "Quantitative or executable reasoning",
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
        "prioritize": "Rank items by importance or impact",
        "probability": "Probabilistic and statistical reasoning",
        "product": "Product lens — features, users, value",
        "resilience": "Behavior under stress and recovery",
        "rigor": "Disciplined, well-justified reasoning",
        "risks": "Potential problems and failure modes",
        "robust": "Reason under deep uncertainty",
        "shift": "Rotate through distinct perspectives",
        "simulation": "Thought experiments and scenario walkthroughs",
        "spec": "Define correctness criteria first",
        "split": "Decompose into parts or components",
        "systemic": "Interacting whole and feedback loops",
        "trans": "Information transfer model with noise and feedback",
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
        "adr": "Task-affinity for decision-making tasks (plan, probe, make). The "
        "ADR format (Context, Decision, Consequences) is a decision "
        "artifact — it does not accommodate tasks that produce "
        "non-decision outputs. Avoid with sort (sorted list), pull "
        "(extraction), diff (comparison), or sim (scenario playback).",
        "code": "Avoid with narrative tasks (sim, probe) that produce prose "
        "rather than code.",
        "codetour": "Best for code-navigation tasks: fix, make (code creation), "
        "show (code structure), pull (code extraction). Avoid with "
        "sim, sort, probe, diff (no code subject), or plan. Requires "
        "a developer audience — produces a VS Code CodeTour JSON "
        "file. Avoid with manager, PM, executive, CEO, stakeholder, "
        "analyst, or designer audiences.",
        "gherkin": "Outputs only Gherkin Given/When/Then syntax. Primary use: "
        "make tasks creating acceptance tests or feature "
        "specifications. With analysis tasks (probe, diff, check, "
        "sort), output is reframed as Gherkin scenarios that specify "
        "the analyzed properties — the analysis becomes evidence; "
        "scenarios express what should be true given that evidence. "
        "Avoid with prose-structure forms (story, case, log, "
        "questions, recipe).",
        "html": "Avoid with narrative tasks (sim, probe) that produce prose "
        "rather than code.",
        "shellscript": "Shell script output. Avoid with narrative tasks (sim, "
        "probe) and selection tasks (pick, diff, sort) - these "
        "don't produce code.",
        "sketch": "D2 diagram output only. Avoid with prose forms (indirect, "
        "case, walkthrough, variants) - choose diagram OR prose, not "
        "both.",
    },
    "completeness": {
        "skim": "Quick-pass constraint: most obvious or critical issues "
        "only. Avoid pairing with multi-phase directionals (bog, fip "
        "rog, fly rog, fog) that require structural depth and "
        "sustained examination. Use with simple directionals (jog, "
        "rog) or none."
    },
    "form": {
        "case": "Layered argument-building prose (background, evidence, "
        "alternatives, recommendation). Conflicts with code-format channels "
        "(gherkin, codetour, shellscript, svg, html, diagram/sketch) — "
        "case-building requires prose structure those channels cannot "
        "accommodate. Use with no channel or prose-compatible channels "
        "(jira, slack, plain, remote, sync).",
        "commit": "Conventional commit message (type: scope header + optional body). "
        "Brief artifact by design — avoid deep or max completeness (no "
        "room to express depth) and complex directionals (fip rog, fly "
        "rog, bog, fog). Best with gist or minimal completeness.",
        "contextualise": "Works well with text-friendly channels (plain, sync, jira, "
        "slack). Avoid with output-only channels (gherkin, "
        "shellscript, codetour) - cannot render explanatory "
        "context.",
        "facilitate": "When combined with sim, designs a facilitation structure for "
        "a simulation exercise rather than performing the simulation "
        "directly.",
        "faq": "Question-and-answer prose format. Conflicts with executable output "
        "channels: shellscript, code, codetour (output format mismatch). Use "
        "with plain, slack, diagram, or no channel.",
        "log": "Work or research log entry with date markers and bullet updates. "
        "Conflicts with any non-text output channel (svg, diagram/sketch, "
        "codetour, gherkin, shellscript, html) — log entries are prose-text "
        "artifacts. Use with no channel or prose-compatible channels (jira, "
        "slack, remote, sync).",
        "questions": "Conflicts with gherkin (syntax rigidity). With diagram: "
        "produces a question-tree Mermaid diagram. Use with plain, "
        "slack, diagram, or no channel.",
        "recipe": "Conflicts with codetour, code, shellscript, svg, presenterm "
        "(schema has no prose slot). Use with plain, slack, or no channel.",
        "scaffold": "Learning-oriented explanation. Avoid with 'make' task producing "
        "artifacts (code, diagram, adr) - use only when user wants "
        "accompanied explanation. scaffold = explain from first "
        "principles.",
        "socratic": "Avoid with code channels (shellscript, codetour) - they cannot "
        "render questions as code output.",
        "spike": "Research spike: problem statement and exploratory questions. "
        "Conflicts with code-format channels (codetour, shellscript, svg, "
        "html, diagram/sketch, gherkin) — research spikes are prose "
        "question-documents. Use with no channel or prose-compatible "
        "channels.",
        "story": "User story prose (As a / I want / so that). Explicitly avoids "
        "Gherkin or test-case syntax — conflicts with gherkin channel. Use "
        "with no channel or prose-compatible channels.",
        "visual": "Distinct from the diagram channel: visual = abstract/metaphorical "
        "prose layout with a short legend; diagram = precise Mermaid code "
        "with exact nodes and edges. Use visual when conceptual overview "
        "or spatial metaphor is more useful than diagrammatic precision "
        "(e.g., non-technical audience, big-picture emphasis). Use diagram "
        "when exact topology, dependency mapping, or architecture review "
        "requires precise structure.",
    },
    "method": {
        "abduce": "Distinguish from: deduce (premises→conclusion) and induce "
        "(examples→pattern). Abduce generates hypotheses from evidence.",
        "actors": "Well-suited for security threat modelling: identifying threat "
        "actors (external attackers, insiders, automated bots), their "
        "motivations, and how their capabilities interact with system "
        "attack surfaces. Use alongside adversarial for complete threat "
        "models.",
        "branch": "Distinguish from: explore (generating options). Branch explores "
        "multiple reasoning paths in parallel with evaluation.",
        "cluster": "Distinguish from: meld (balancing constraints). Cluster groups "
        "items by shared characteristics.",
        "deduce": "Distinguish from: abduce (evidence→hypothesis) and induce "
        "(examples→pattern). Deduce derives conclusions from premises.",
        "explore": "Distinguish from: branch (parallel reasoning with evaluation). "
        "Explore generates options without premature commitment.",
        "induce": "Distinguish from: abduce (evidence→hypothesis) and deduce "
        "(premises→conclusion). Induce generalizes from examples.",
        "inversion": "Well-suited for architecture evaluation: start from named "
        "failure modes (cascade failure, split-brain, thundering "
        "herd) and ask which design choices create or amplify them. "
        "Use when failure patterns are named and the question is "
        "whether the design protects against them.",
        "meld": "Distinguish from: cluster (grouping by characteristics). Meld "
        "balances constraints between elements.",
        "resilience": "Distinguish from: robust (selecting options that work "
        "across futures). Resilience focuses on system behavior "
        "under stress.",
        "robust": "Distinguish from: resilience (behavior under stress). Robust "
        "favors options that perform acceptably across futures.",
        "systemic": "Distinguish from: analysis (decomposition/structure). "
        "Systemic focuses on feedback loops and interactions.",
    },
    "scope": {
        "cross": "Use when the question is about where a concern lives across the "
        "system, not just within one place. Prefer over struct when the "
        "focus is on horizontal span and consistency of a concern rather "
        "than structural arrangement."
    },
}

# Task-type heuristics for when to apply each token (ADR-0132).
# Surfaces as 'When to use' helper text in UIs.
AXIS_KEY_TO_USE_WHEN: Dict[str, Dict[str, str]] = {
    "channel": {
        "plain": "Suppress structural formatting: when user explicitly requests "
        "plain prose, no lists, no bullets, or no structural decoration. "
        "Heuristic: 'no bullets', 'no formatting', 'plain prose', "
        "'continuous prose', 'flowing paragraphs', 'paragraph form' → "
        "plain channel.",
        "remote": "Optimizing output for remote or distributed delivery contexts "
        "(video calls, screen sharing, async participants). Heuristic: "
        "'remote delivery', 'distributed session', 'video call "
        "context', 'screen sharing', 'remote-friendly' → remote "
        "channel. Note: user saying their team is 'remote' describes "
        "context — use remote channel only when delivery optimization "
        "is the explicit goal.",
        "sketch": "D2 diagram output: when user explicitly requests D2 format or "
        "D2 diagram source. Heuristic: 'D2 diagram', 'D2 format', "
        "'sketch diagram', 'd2 source' → sketch. Distinct from diagram "
        "channel (Mermaid output). If the user just says 'diagram' "
        "without specifying D2, use diagram channel.",
        "sync": "Live or synchronous session planning: agenda with timing, steps, "
        "and cues for real-time delivery. Heuristic: 'session plan', "
        "'live workshop agenda', 'meeting agenda with timing cues', "
        "'synchronous workshop plan' → sync channel. Combine with "
        "facilitate form for facilitator-role outputs.",
    },
    "completeness": {
        "gist": "Brief but complete response needed: user wants a quick "
        "summary or overview without deep exploration. Heuristic: "
        "'quick summary', 'overview', 'brief', 'tldr', 'just the "
        "main points', 'high-level', 'standup update', 'just the "
        "gist' → gist. Distinct from skim (skim = light pass, may "
        "miss non-obvious; gist = brief but complete).",
        "narrow": "Response should focus on a very specific slice only: user "
        "explicitly limits scope to one aspect. Heuristic: "
        "'specifically', 'only about', 'just this part', "
        "'restricted to', 'nothing beyond', 'only X' → narrow. "
        "Distinct from minimal (minimal = smallest answer; narrow "
        "= very small slice of topic).",
        "skim": "Light, surface-level pass needed: user wants a quick scan "
        "for obvious issues without depth. Heuristic: 'light "
        "review', 'quick pass', 'spot check', 'just flag obvious "
        "problems', 'surface-level look', 'sanity check', 'quick "
        "skim' → skim. Distinct from gist (gist = brief but "
        "complete; skim = light pass that may miss non-obvious "
        "issues).",
    },
    "form": {
        "cocreate": "Iterative design with explicit decision points and alignment "
        "checks at each step rather than a one-shot response. Heuristic: "
        "'work through incrementally', 'with decision points', "
        "'iterative design' → cocreate. Distinct from variants (choice "
        "of designs) and make (one-shot artifact).",
        "facilitate": "Planning a workshop, retrospective, or collaborative session "
        "with session structure, participation cues, and facilitation "
        "agenda. Heuristic: 'facilitate a X', 'run a retrospective', "
        "'workshop planning' → facilitate. Distinct from walkthrough "
        "(linear narrated steps).",
        "ladder": "Analyzing causes or effects across multiple levels of "
        "abstraction: step up to systemic causes, step down to concrete "
        "consequences. Heuristic: 'step up and down abstraction levels', "
        "'root cause hierarchy', 'why at a systems level' → ladder.",
        "recipe": "Documenting a process as a structured recipe with a custom "
        "mini-language and short key — best when the process has a "
        "recurring structure that benefits from a custom notation. "
        "Heuristic: 'document as recipe', 'structured setup guide with "
        "repeating patterns' → recipe. Distinct from walkthrough (linear "
        "narrated steps without custom notation).",
        "spike": "Framing a technology investigation or adoption decision as a "
        "backlog spike artifact (problem statement + exploratory "
        "questions). Use make task (not plan) — the spike IS the artifact. "
        "Heuristic: 'should we adopt X?', 'spike on Y', 'investigation "
        "backlog item' → make + spike.",
        "taxonomy": "Producing a type hierarchy, category classification, or "
        "taxonomy of entities. Pair with thing scope for concrete "
        "entities. Heuristic: 'classify all types of X', 'what kinds of "
        "Y exist', 'type hierarchy' → taxonomy + thing scope. Distinct "
        "from table (flat comparison).",
        "visual": "Abstract or metaphorical representation of a subject as prose "
        "layout with a legend — when diagrammatic precision (Mermaid) is "
        "less useful than conceptual overview. Heuristic: 'abstract "
        "visual', 'conceptual layout', 'big-picture structure for "
        "non-technical audience' → visual. Distinct from diagram channel "
        "(precise Mermaid output).",
        "wardley": "Strategic mapping: user wants to position components on an "
        "evolution axis (genesis → custom → product → commodity). "
        "Heuristic: 'Wardley map', 'map on evolution axis', 'genesis to "
        "commodity' → wardley.",
        "wasinawa": "Post-incident reflection or retrospective on past events. "
        "Structures output as: what happened, why it matters, next "
        "steps. Heuristic: 'reflect on incident', 'what went wrong and "
        "what to do next', 'lessons learned' → wasinawa. Distinct from "
        "pre-mortem (inversion method): pre-mortem assumes future "
        "failure; wasinawa reflects on past events.",
    },
    "method": {
        "boom": "Scale extreme analysis: user asks what happens at 10x, 100x, or "
        "at the absolute limits of the system. Heuristic: 'at 10x', 'at "
        "extreme load', 'what breaks at scale', 'pushed to the limit', 'at "
        "maximum load', 'what dominates at scale', 'scale to the extreme', "
        "'at the limit' → boom. Distinct from resilience (normal stress "
        "range) and adversarial (deliberate attack/exploit focus).",
        "field": "Shared-medium interaction analysis: user asks how actors "
        "interact through a shared infrastructure or protocol layer "
        "rather than via direct references. Heuristic: 'shared "
        "infrastructure', 'shared medium', 'protocol mediation', 'service "
        "mesh routing', 'why things route through', 'broadcast patterns', "
        "'effects propagate through a shared layer' → field. Distinct "
        "from mapping (surface elements; field = model the medium and why "
        "compatibility produces observed routing).",
        "grove": "Accumulation and compounding analysis: user asks how small "
        "effects build up over time, how debt or improvement compounds, "
        "or how feedback loops amplify outcomes. Heuristic: 'compound', "
        "'accumulates over time', 'feedback loop', 'technical debt "
        "grows', 'network effect', 'how things build up', 'rate of change "
        "over time', 'snowball' → grove. Distinct from systemic "
        "(interacting whole; grove = rate of accumulation through "
        "mechanisms) and effects (trace consequences; grove = HOW they "
        "compound).",
        "grow": "Evolutionary or incremental design philosophy: user wants to "
        "start minimal and expand only when demonstrably needed. "
        "Heuristic: 'start simple and expand', 'minimum viable', 'YAGNI', "
        "'add only what you need', 'simplest thing that works', 'evolve as "
        "needed', 'don't over-engineer', 'add features only when "
        "required', 'grow incrementally' → grow. Distinct from minimal "
        "completeness (brevity of output) and spec (define criteria "
        "first).",
        "meld": "Constraint-balancing or tension-resolution analysis: user asks "
        "how to balance competing forces, find overlaps, or navigate "
        "constraints between elements that must coexist. Heuristic: "
        "'balance between', 'overlap between', 'constraints between', "
        "'combining X and Y', 'where X and Y interact', 'navigate tensions "
        "between', 'find the combination that satisfies' → meld. Distinct "
        "from compare (evaluate alternatives; meld = balance constraints "
        "between elements that must coexist).",
        "melody": "Cross-component or cross-team coordination analysis: user asks "
        "how to synchronize work, manage coupling, or align changes "
        "across teams or components. Heuristic: 'coordinate across "
        "teams', 'synchronize changes', 'change alignment', 'coupling "
        "between components', 'parallel work streams', 'avoid conflicts "
        "between teams', 'migration coordination', 'who needs to change "
        "when' → melody. Distinct from depends (what relies on what) and "
        "actors (centering the people involved).",
        "mod": "Cyclic or periodic pattern analysis: user asks about behavior that "
        "repeats, wraps around, or follows a cycle. Heuristic: 'repeats "
        "across cycles', 'cyclic behavior', 'periodic pattern', 'repeating "
        "structure', 'what wraps around', 'recurs periodically', "
        "'equivalent states' → mod. Distinct from motifs scope (recurring "
        "patterns across codebase; mod = cyclic/periodic reasoning about "
        "behavior that repeats with a defined period).",
    },
    "scope": {
        "agent": "Decision-making or agency focus: user asks who can act, who has "
        "authority, or how choices are made between actors. Heuristic: "
        "'who decides', 'who has authority', 'who can approve', "
        "'decision-making', 'agency', 'who is responsible' → agent scope. "
        "Note: agent is a SCOPE token (foregrounds decision-making "
        "actors); actors is a METHOD token (enriches any task with "
        "actor-centered analysis). Both can be selected together.",
        "assume": "Assumptions and premises focus: user asks what must be true, "
        "what is taken for granted, or what preconditions are embedded in "
        "the design. Heuristic: 'what assumptions', 'what are we "
        "assuming', 'what must be true', 'what preconditions', 'hidden "
        "assumptions', 'what are we taking for granted' → assume scope. "
        "Distinct from unknowns method (unknowns = surfaces what we don't "
        "know we don't know; assume = makes explicit what is already "
        "assumed).",
        "good": "Quality criteria or success standards focus: user asks what makes "
        "something good, what criteria matter, or how to judge quality. "
        "Heuristic: 'quality criteria', 'what makes it good', 'how to "
        "judge', 'success criteria', 'well-designed', 'what good looks "
        "like', 'standards for', 'what does success look like' → good "
        "scope. Often pairs with fail scope (good + fail = quality and "
        "failure mode dimensions).",
        "motifs": "Recurring or repeated patterns across the codebase or system: "
        "user asks about structures or idioms that appear in multiple "
        "places. Heuristic: 'recurring patterns', 'repeated across', "
        "'appears in multiple places', 'common idioms', 'what keeps "
        "showing up', 'same pattern in different places' → motifs scope. "
        "Distinct from struct (one system's internal arrangement) and "
        "mapping method (surface all elements/relationships).",
        "stable": "Stability and persistence focus: user asks what is stable, "
        "unlikely to change, or self-reinforcing in the system or design. "
        "Heuristic: 'stable', 'unlikely to change', 'won't change', 'what "
        "persists', 'what is settled', 'fixed constraints', 'what has "
        "remained stable', 'backward-compatible' → stable scope. Often "
        "pairs with time scope (stable = what persists; time = how things "
        "evolve).",
        "time": "Temporal or sequential focus: user asks about sequence, history, "
        "phases, or how something changes over time. Heuristic: 'step by "
        "step', 'in order', 'over time', 'what happens when', 'sequence', "
        "'timeline', 'history', 'how did we get here', 'phases' → time "
        "scope. Distinct from flow method (flow = reasoning approach; time "
        "= scope dimension to emphasize).",
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
