"""Axis configuration as static Python maps (token -> description).

Generated from the axis registry; keep in sync with list edits."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "channel": {
        "jira": (
            "The response formats the content using Jira markup (headings, lists, panels) "
            "where relevant and avoids extra explanation beyond the main material."
        ),
        "presenterm": (
            "The response is a valid multi-slide presenterm deck expressed as raw "
            'Markdown (no code fences). The front matter always matches: "--- '
            "newline title: <descriptive title based on the input with colons "
            "encoded as &#58; and angle brackets encoded as &lt; and &gt;> newline "
            "author: Generated (or authors: [...]) newline date: YYYY-MM-DD newline "
            '--- newline" with no other keys. The deck contains up to 12 slides. '
            "Each slide starts with a Setext header (title line followed by a line "
            "of ---), includes content and references, and ends with an HTML "
            "comment named end_slide on its own line followed by a blank line; the "
            "final slide may omit the closing end_slide. A blank line always "
            'precedes the References section so that a line with "References" or "- '
            'References" is separated by one empty line. Directives appear only as '
            'standalone HTML comments with exact syntax: "<!-- end_slide -->", '
            '"<!-- pause -->", "<!-- column_layout: [7, 3] -->", "<!-- column: 0 '
            '-->", "<!-- reset_layout -->", and "<!-- jump_to_middle -->". Code '
            "fence safety is enforced: whenever a fenced code block opens (for "
            "example ```mermaid +render, ```bash +exec, ```latex +render, ```d2 "
            "+render), the response includes a matching closing fence of exactly "
            "three backticks on its own line before any non-code content, "
            "directive, or end_slide; if a fence remains open at slide end, the "
            "response emits the closing fence first. Mermaid diagrams use code "
            "blocks tagged mermaid +render; LaTeX uses latex +render; D2 uses d2 "
            "+render; executable snippets use fenced code blocks whose info string "
            "starts with a language then +exec (optionally +id:<name>) or "
            '+exec_replace or +image. The response emits "<!-- snippet_output: name '
            '-->" only when a snippet with +id:name exists. Lines hidden with # or '
            "/// prefixes follow language conventions; other code blocks appear "
            "only when relevant and include the language name; images appear only "
            "when valid paths or URLs exist. Within the slide body (outside fenced "
            "or inline code and outside HTML directives), the deck never includes "
            "raw HTML: every literal '<' becomes &lt; and every literal '>' becomes "
            "&gt;, preventing raw angle brackets in body text. Markdown safety "
            "prevents accidental styling: standalone or path-embedded '~' becomes "
            '"&#126;" (so "~/foo" becomes "&#126;/foo") while intentional '
            '"~~text~~" remains unchanged. Mermaid safety keeps grammar and '
            "delimiters intact ([], (), [[]], (()), [/ /]); node and edge labels "
            "appear inside ASCII double quotes and use Mermaid-compatible numeric "
            'codes with no leading ampersand, such as "#91;" for "[", "#93;" for '
            '"]", "#40;" for "(", "#41;" for ")", "#123;" for "{{", "#125;" for '
            '"}}", "#60;" for "<", "#62;" for ">", "#35;" for "#", "#58;" for ":", '
            "and \"&\" and slashes '/' remain as-is, with no additional entity "
            "encodings, and labels are never double-encoded. The deck avoids # "
            "headers in slide bodies."
        ),
        "remote": (
            "The response is optimised for remote delivery, ensuring instructions work "
            "in distributed or online contexts and surfacing tooling or interaction "
            "hints suitable for video, voice, or screen sharing."
        ),
        "slack": (
            "The response formats the answer for Slack using appropriate Markdown, "
            "mentions, and code blocks while avoiding channel-irrelevant decoration."
        ),
        "sync": (
            "The response takes the shape of a synchronous or live session plan (agenda, "
            "steps, cues) rather than static reference text."
        ),
    },
    "completeness": {
        "full": "The response provides a thorough answer for normal use, covering all "
        "major aspects without needing every micro-detail.",
        "gist": "The response offers a short but complete answer or summary that touches "
        "the main points once without exploring every detail.",
        "max": "The response is as exhaustive as reasonable, covering essentially "
        "everything relevant and treating omissions as errors.",
        "minimal": "The response makes the smallest change or provides the smallest "
        "answer that satisfies the request, avoiding work outside the core "
        "need.",
        "skim": "The response performs only a very light pass, addressing the most "
        "obvious or critical issues without aiming for completeness.",
    },
    "directional": {
        "bog": (
            "The response examines the subject's structure and reflects on it, then "
            "identifies actions to take and extends them to related contexts."
        ),
        "dig": (
            "The response examines concrete details and grounding examples, focusing "
            "on specifics rather than abstractions."
        ),
        "dip bog": (
            "The response starts with concrete examples and grounded details, "
            "examines their structure and reflects on patterns, then identifies "
            "actions and extensions."
        ),
        "dip ong": (
            "The response starts with concrete examples, identifies actions to "
            "take from them, then extends those actions to related situations."
        ),
        "dip rog": (
            "The response examines concrete details and grounded examples, then "
            "reflects on their structural patterns and what they reveal."
        ),
        "fig": (
            "The response alternates between abstract principles and concrete "
            "examples, using each to illuminate the other (figure-ground reversal)."
        ),
        "fip bog": (
            "The response moves between abstract principles and concrete examples, "
            "examines their structural patterns and reflects on them, then "
            "identifies actions and extends them to related contexts."
        ),
        "fip ong": (
            "The response alternates between abstract principles and concrete "
            "examples, then identifies actions to take and extends them to related "
            "situations."
        ),
        "fip rog": (
            "The response moves between abstract principles and concrete examples "
            "while examining structural patterns and reflecting on what they "
            "reveal."
        ),
        "fly bog": (
            "The response identifies abstract patterns and general principles, "
            "examines their structure and reflects on it, then identifies actions "
            "and extends them to related contexts."
        ),
        "fly ong": (
            "The response identifies abstract patterns and general principles, "
            "then proposes concrete actions and extends them to related contexts."
        ),
        "fly rog": (
            "The response identifies abstract patterns and general principles, "
            "then examines their structural relationships and reflects on their "
            "implications."
        ),
        "fog": (
            "The response identifies general patterns and abstract principles from the "
            "specifics, moving from particular cases to broader insights."
        ),
        "jog": (
            "The response interprets the intent and carries it out directly without "
            "asking follow-up questions."
        ),
        "ong": (
            "The response identifies concrete actions to take, then extends those "
            "actions to related situations or next steps."
        ),
        "rog": (
            "The response examines the structure of the subject (how it is organized), "
            "then reflects on why that structure exists and what it reveals."
        ),
    },
    "form": {
        "adr": (
            "The response takes the shape of an Architecture Decision Record (ADR) with "
            "sections for context, decision, and consequences, written in a concise document "
            "style."
        ),
        "bug": (
            "The response appears as a structured bug report with sections for Steps to "
            "Reproduce, Expected Behavior, Actual Behavior, and Environment or Context, "
            "emphasising concise, testable details."
        ),
        "bullets": (
            "The response presents the main answer as concise bullet points only, "
            "avoiding long paragraphs."
        ),
        "cards": (
            "The response presents the main answer as discrete cards or items, each with a "
            "clear heading and short body, avoiding long continuous prose."
        ),
        "checklist": (
            "The response appears as an actionable checklist whose items are clear "
            "imperative tasks rather than descriptive prose."
        ),
        "code": (
            "The response consists only of code or markup for the main answer, with no "
            "surrounding natural-language explanation."
        ),
        "codetour": (
            "The response is a valid VS Code CodeTour `.tour` JSON document "
            "(schema-compatible) that uses steps and fields appropriate to the task and "
            "omits extra prose or surrounding explanation."
        ),
        "commit": (
            "The response is formatted as a conventional commit message with a short type "
            "or scope line and an optional concise body."
        ),
        "diagram": (
            "The response converts the input into Mermaid diagram code only: it infers "
            "the best diagram type for the task and respects Mermaid safety constraints "
            "(Mermaid diagrams do not allow parentheses in the syntax or raw '|' "
            "characters inside node labels; the text uses numeric encodings such as "
            "\"#124;\" for '|' instead of raw problematic characters)."
        ),
        "faq": (
            "The response adopts an FAQ layout: clearly separated question headings with "
            "concise answers beneath each one, keeping content easy to skim and free of long "
            "uninterrupted prose."
        ),
        "walkthrough": (
            "The response guides the audience step by step by outlining stages and "
            "walking through them in order so understanding builds gradually."
        ),
        "gherkin": (
            "The response outputs only Gherkin, using Jira markup where appropriate and "
            "omitting surrounding explanation."
        ),
        "html": (
            "The response consists solely of semantic HTML for the answer, with no "
            "surrounding prose."
        ),
        "log": (
            "The response reads like a concise work or research log entry with date or time "
            "markers as needed, short bullet-style updates, and enough context for future "
            "reference without unrelated narrative."
        ),
        "plain": (
            "The response uses plain prose with natural paragraphs and sentences, imposing "
            "no additional structure such as bullets, tables, or code blocks."
        ),
        "questions": (
            "The response presents the answer as a series of probing or clarifying "
            "questions rather than statements."
        ),
        "recipe": (
            "The response expresses the answer as a recipe that includes a custom, clearly "
            "explained mini-language and a short key for understanding it."
        ),
        "shellscript": (
            "The response is delivered as a shell script, focusing on correct, "
            "executable shell code rather than prose."
        ),
        "spike": (
            "The response formats the backlog item as a research spike: it starts with a "
            "brief problem or decision statement, lists the key questions the spike should "
            "answer, and stays focused on questions and learning rather than implementation "
            "tasks."
        ),
        "story": (
            'The response formats the backlog item as a user story using "As a <persona>, I '
            'want <capability>, so that <value>." It may include a short description and '
            "high-level acceptance criteria in plain prose but avoids Gherkin or test-case "
            "syntax."
        ),
        "svg": (
            "The response consists solely of SVG markup for the answer, with no surrounding "
            "prose, and remains minimal and valid for copy/paste into an `.svg` file."
        ),
        "table": (
            "The response presents the main answer as a Markdown table when feasible, "
            "keeping columns and rows compact."
        ),
        "test": (
            "The response presents test cases in a structured format with clear setup, "
            "execution, and assertion sections, organized by scenario type (happy path, edge "
            "cases, errors, boundaries) and including descriptive test names."
        ),
        "tight": (
            "The response uses concise, dense prose, remaining freeform without bullets, "
            "tables, or code and avoiding filler."
        ),
        "variants": (
            "The response presents several distinct, decision-ready options as separate "
            "variants, labelling each one with a short description and including "
            "approximate probabilities when helpful while avoiding near-duplicate "
            "alternatives."
        ),
        "visual": (
            "The response conveys the answer as an abstract visual or metaphorical layout "
            "accompanied by a short legend, emphasising big-picture structure over dense "
            "prose."
        ),
        "wardley": (
            "The response expresses the answer as a Wardley Map showing value chain "
            "evolution from genesis to commodity."
        ),
    },
    "method": {
        "adversarial": (
            "The response runs a constructive stress-test, systematically searching "
            "for weaknesses, edge cases, counterexamples, failure modes, and "
            "unstated assumptions while prioritising critique and stress-testing "
            "aimed at improving the work."
        ),
        "analysis": (
            "The response describes, analyses, and structures the situation without "
            "proposing specific actions, fixes, or recommendations."
        ),
        "boom": (
            "The response applies limit or continuity style reasoning in a non-numerical "
            "way to explore behaviour toward extremes."
        ),
        "bridge": (
            "The response charts a path from the current state to the desired situation "
            "before proposing specific recommendations."
        ),
        # Inversion: start from failure and work backward.
        "inversion": (
            "The response begins from undesirable or catastrophic outcomes (including multiply-by-zero "
            "failure modes), asks what would reliably produce or amplify those outcomes, and then works "
            "backward to avoid, mitigate, or design around those paths."
        ),
        # Thought experiments / scenario walkthroughs (distinct from real-world experiments).
        "simulation": (
            "The response uses explicit thought experiments or scenario walkthroughs, projecting how the "
            "situation might evolve over time, including feedback loops, bottlenecks, tipping points, "
            "critical mass, and emergent effects, rather than analysing it only as a static snapshot."
        ),
        # Robustness lens, complementary to 'probability' (estimation) without redefining it.
        "robust": (
            "The response emphasises decisions and designs that perform acceptably across a wide range "
            "of unknowns and adverse scenarios, prioritising downside protection, margin of safety, and "
            "optionality over precise optimisation of expected outcomes."
        ),
        "bud": (
            "The response applies addition or subtraction style reasoning in a "
            "non-numerical way to emphasise contrasts or balances."
        ),
        "case": (
            "The response builds the case before the conclusion by laying out background, "
            "evidence, trade-offs, and alternatives before converging on a clear "
            "recommendation that addresses objections and constraints."
        ),
        "connascence": (
            "The response analyzes connascence (static/dynamic coupling) measuring "
            "strength, degree, locality, and remedies."
        ),
        "cluster": (
            "The response groups similar items into labelled categories and describes "
            "each cluster, emphasising recurring patterns over isolated singletons."
        ),
        "cochange": (
            "The response applies cochange analysis to identify temporal coupling and "
            "coordinated modification patterns."
        ),
        "cocreate": (
            "The response works collaboratively with the user, proposing small moves, "
            "checking alignment, and iterating together instead of delivering a "
            "one-shot answer."
        ),
        "com b": (
            "The response uses the COM-B model to analyse capability, opportunity, and "
            "motivation, mapping findings to behaviour-change techniques and outlining an "
            "implementation plan."
        ),
        "compare": (
            "The response compares two or more items by listing similarities and "
            "differences, highlighting subtle distinctions and trade-offs that matter "
            "to the audience."
        ),
        "contextualise": (
            "The response adds or reshapes context to support another "
            "operation—such as supplying background for an LLM or reframing "
            "content—without rewriting the main text itself."
        ),
        "converge": (
            "The response narrows the field and makes a call, weighing trade-offs, "
            "eliminating weaker options, and arriving at a small set of "
            "recommendations or a single decision."
        ),
        "debugging": (
            "The response follows a debugging-style scientific method: it summarises "
            "stable facts, lists unresolved questions, proposes plausible hypotheses, "
            "designs minimal experiments or checks, narrows likely root causes, and "
            "outlines fixes."
        ),
        "deep": (
            "The response goes into substantial depth within the chosen scope, unpacking "
            "reasoning layers and fine details without necessarily enumerating every edge "
            "case."
        ),
        "depends": (
            "The response traces dependency relationships, identifying what depends on "
            "what and the nature of those dependencies."
        ),
        "diagnose": (
            "The response seeks likely causes of problems first, narrowing hypotheses "
            "before proposing fixes or changes."
        ),
        "dimension": (
            "The response expands metaphorical dimensions of the subject and examines "
            "each axis to expose structure."
        ),
        "direct": (
            "The response leads with the main point or recommendation, followed only by "
            "the most relevant supporting context, evidence, and next steps."
        ),
        "diverge": (
            "The response opens up the option space by generating multiple, diverse "
            "possibilities or angles without prematurely judging or collapsing to a "
            "single answer."
        ),
        "drum": (
            "The response applies multiplication or division style reasoning in a "
            "non-numerical way to expose proportional relationships."
        ),
        "dub": (
            "The response applies power or root style reasoning in a non-numerical way to "
            "reframe scale and intensity."
        ),
        "effects": (
            "The response traces second- and third-order effects before summarising the "
            "downstream consequences."
        ),
        "experimental": (
            "The response reasons in an experimental or scientific style by "
            "proposing concrete experiments, outlining how each would run, "
            "describing expected outcomes, and explaining how those outcomes would "
            "update the hypotheses."
        ),
        "explore": (
            "The response explores the option space by generating and comparing "
            "multiple plausible approaches, weighing their trade-offs, and identifying "
            "which candidates merit deeper development without committing to a final "
            "recommendation yet."
        ),
        "facilitate": (
            "The response facilitates the session by framing the goal, proposing "
            "structure, managing turns, and keeping participation balanced rather "
            "than doing the work solo."
        ),
        "filter": (
            "The response extracts only items that match a clearly stated criterion—such "
            "as pain points, risks, or open questions—and omits the rest."
        ),
        "flow": (
            "The response focuses on flow over time or sequence, explaining how control, "
            "data, or narrative progresses step by step through the material."
        ),
        "graph": (
            "The response uses graph or tree reasoning by mapping nodes, edges, "
            "direction, weight, and centrality to explain structural flow."
        ),
        "grove": (
            "The response applies integral or derivative style reasoning in a "
            "non-numerical way to explore accumulation and rate-of-change."
        ),
        "how": (
            "The response concentrates on mechanical explanation of how the subject works "
            "before other narration."
        ),
        "improve": (
            "The response takes existing work and enhances it along relevant "
            "dimensions—such as performance, readability, maintainability, correctness, "
            "or robustness—identifying specific improvements and applying them while "
            "preserving core functionality."
        ),
        "independent": (
            "The response examines how elements remain independent, decoupled, or "
            "orthogonal despite proximity."
        ),
        "indirect": (
            "The response begins with brief background, reasoning, and trade-offs and "
            "finishes with a clear bottom-line point or recommendation that ties them "
            "together."
        ),
        "invert": (
            "The response inverts the concept to expose its negative space and "
            "complementary behaviours."
        ),
        "ladder": (
            "The response uses abstraction laddering by placing the focal problem, "
            "stepping up to higher-level causes, and stepping down to consequences "
            "ordered by importance to the audience."
        ),
        "liberating": (
            "The response facilitates using Liberating Structures, emphasising "
            "distributed participation, short structured interactions, concrete "
            "invitations, and visual, stepwise processes while naming or evoking "
            "specific LS patterns when helpful."
        ),
        "logic": (
            "The response applies propositional or predicate logic reasoning in a "
            "non-numerical way."
        ),
        "map": (
            "The response emphasises schema mapping by detailing source and target "
            "structures, transformation rules, and information flow."
        ),
        "mapping": (
            "The response emphasises mapping over exposition by surfacing elements, "
            "relationships, and structure, organising them into a coherent map "
            "(textual, tabular, or visual) rather than a linear narrative."
        ),
        "math": (
            "The response surveys applicable mathematical fields and clarifies their "
            "relevance to the subject."
        ),
        "meld": (
            "The response applies set theory reasoning in a non-numerical way to reason "
            "about combinations, unions, and overlaps."
        ),
        "melody": (
            "The response analyses coordination clusters (visibility, scope, volatility) "
            "and recommends adjustments to tune the system."
        ),
        "merge": (
            "The response combines multiple sources into a single coherent whole while "
            "preserving essential information."
        ),
        "mod": (
            "The response treats the second idea as a modulus for the first to explore "
            "periodicity and constraint analogies."
        ),
        "motifs": (
            "The response scans for recurring motifs and patterns, identifying repeated "
            "elements, themes, clusters, and notable outliers, and briefly explaining "
            "why they matter."
        ),
        "order": (
            "The response applies order or lattice theory reasoning in a non-numerical "
            "way to reveal hierarchy, dominance, and comparative structure."
        ),
        "orthogonal": (
            "The response isolates orthogonal factors and articulates how their "
            "independence shapes the problem."
        ),
        "prioritize": (
            "The response assesses and orders items by importance or impact to the "
            "stated audience, making the ranking and rationale explicit."
        ),
        "probability": (
            "The response applies probability or statistical reasoning to "
            "characterise uncertainty and likely outcomes."
        ),
        "recurrence": (
            "The response derives recurrence relationships and interprets their "
            "implications in plain language."
        ),
        "reflection": (
            "The response reflects the concept to reveal mirrored structure and "
            "complementary perspectives."
        ),
        "rewrite": (
            "The response rewrites or refactors while preserving the original intent, "
            "treating the work as a mechanical transform rather than a "
            "reinterpretation."
        ),
        "rigor": (
            "The response relies on disciplined, well-justified reasoning and makes its "
            "logic explicit, avoiding hand-waving."
        ),
        "rotation": (
            "The response presents a metaphorical 90-degree rotation of the concept to "
            "surface contrasting viewpoints."
        ),
        "scaffold": (
            "The response explains with scaffolding: it starts from first principles, "
            "introduces ideas gradually, uses concrete examples and analogies, and "
            "revisits key points so a beginner can follow and retain the concepts."
        ),
        "socratic": (
            "The response employs a Socratic, question-led method by asking short, "
            "targeted questions that surface assumptions, definitions, and gaps in "
            "understanding, withholding full conclusions until enough answers exist or "
            "the user explicitly requests a summary."
        ),
        "split": (
            "The response separates mixed content into distinct sections or categories "
            "with clear boundaries."
        ),
        "steps": (
            "The response solves the problem step by step, briefly labelling and "
            "explaining each step before presenting the final answer."
        ),
        "systemic": (
            "The response analyses the subject using systems thinking, focusing on "
            "boundaries, components, flows, feedback loops, emergence, and leverage "
            "points."
        ),
        "taxonomy": (
            "The response builds or refines a taxonomy by defining categories, "
            "subtypes, and relationships to clarify structure, preferring compact "
            "representations over prose."
        ),
        "tune": (
            "The response evaluates visibility, scope, and volatility alignment using the "
            "Concordance Frame and recommends tuning actions."
        ),
        "wasinawa": (
            "The response applies a What–So What–Now What reflection: it describes "
            "what happened, interprets why it matters, and proposes concrete next "
            "steps."
        ),
        "xp": (
            "The response follows an Extreme Programming-style approach, favouring very "
            "small incremental changes, relying on working software and tests as primary "
            "feedback, and iterating with tight, collaborative feedback loops rather than "
            "big-bang plans."
        ),
        "actions": (
            "The response stays within the selected target and focuses only on concrete "
            "actions or tasks a user or team could take, leaving out background analysis "
            "or explanation."
        ),
        "activities": (
            "The response lists concrete session activities or segments—what to do, "
            "by whom, and in what order—rather than abstract description."
        ),
        "actors": (
            "The response identifies who is involved—people, roles, stakeholders, or "
            "agents in the system."
        ),
        "aesthetics": (
            "The response evaluates taste, style, harmony, proportion, restraint, "
            "authenticity, and appropriateness."
        ),
        "assumptions": (
            "The response focuses on identifying and examining the unstated "
            "assumptions underlying the subject."
        ),
        "bound": (
            "The response remains within the explicit conceptual limits stated or inferred "
            "in the prompt and avoids introducing outside material."
        ),
        "challenges": (
            "The response surfaces critical questions, objections, or tests that "
            "challenge the subject."
        ),
        "concurrency": (
            "The response examines parallel execution, race conditions, "
            "synchronization, or coordination challenges."
        ),
        "constraints": (
            "The response identifies the system’s primary constraint, analyses "
            "behaviours it enforces, and frames ways to balance or relieve it."
        ),
        "criteria": (
            "The response defines success criteria, acceptance conditions, or tests "
            "that determine when something is complete."
        ),
        "disciplines": (
            "The response identifies relevant academic or industry fields of "
            "knowledge and their perspectives."
        ),
        "domains": (
            "The response performs domain-driven discovery by identifying bounded "
            "contexts, business capabilities, and domain boundaries."
        ),
        "dynamics": (
            "The response concentrates on how the system's behaviour and state evolve "
            "over time, covering scenarios, state changes, feedback loops, and "
            "transitions."
        ),
        "edges": (
            "The response emphasises edge cases, errors, and unusual conditions around the "
            "subject."
        ),
        "focus": (
            "The response stays tightly on a central theme within the selected target, "
            "avoiding tangents and side quests."
        ),
        "formats": (
            "The response focuses on document types, writing formats, or structural "
            "templates and their suitability."
        ),
        "gaps": (
            "The response identifies what is missing, misunderstood, or unclear in the "
            "current understanding."
        ),
        "interfaces": (
            "The response concentrates on external interfaces, contracts, and "
            "boundaries between components or systems rather than internal "
            "implementations."
        ),
        "jobs": (
            "The response analyzes Jobs To Be Done—the outcomes users want to achieve and "
            "forces shaping their choices."
        ),
        "metrics": (
            "The response focuses on measurable indicators or key performance measures "
            "that track outcomes."
        ),
        "narrow": (
            "The response restricts the discussion to a very small slice of the topic, "
            "avoiding broad context."
        ),
        "objectivity": (
            "The response assesses whether claims are objective facts or subjective "
            "opinions with supporting evidence."
        ),
        "operations": (
            "The response identifies Operations Research or management science "
            "concepts that frame the situation."
        ),
        "origin": (
            "The response uncovers how the subject arose, why it looks this way now, and what should happen next."
        ),
        "pain": (
            "The response identifies obstacles, frustrations, or inefficiencies experienced "
            "by users or stakeholders."
        ),
        "product": (
            "The response examines the subject through a product lens—features, user "
            "needs, market fit, value propositions."
        ),
        "rationale": (
            "The response explains why something matters, the reasoning behind it, or "
            "its purpose and motivation."
        ),
        "relations": (
            "The response examines relationships, interactions, and dependencies "
            "between elements within the selected target rather than internal details."
        ),
        "risks": (
            "The response focuses on potential problems, failure modes, or negative "
            "outcomes and their likelihood or severity."
        ),
        "roles": (
            "The response focuses on team roles, responsibilities, ownership, handoffs, "
            "and collaboration patterns."
        ),
        "simpler": (
            "The response proposes simpler approaches, shortcuts, or ways to accomplish "
            "goals with less effort or time."
        ),
        "strategy": (
            "The response focuses on strategic positioning, competitive advantage, "
            "evolution, or long-term direction."
        ),
        "system": (
            "The response looks at the overall system as a whole—components, boundaries, "
            "stakeholders, and internal structure—rather than individual lines or "
            "snippets."
        ),
        "taoism": (
            "The response examines the subject through Taoist philosophy—Dao, De, "
            "Yin/Yang, Wu Wei, Ziran, Pu, Qi, Li."
        ),
        "terminology": (
            "The response focuses on undefined, ambiguous, or domain-specific terms "
            "that require clarification."
        ),
        "unknowns": (
            "The response identifies critical unknown unknowns and explores how they "
            "might impact outcomes."
        ),
        "value": (
            "The response focuses on user or customer value, impact, benefits, or outcomes "
            "delivered."
        ),
        # Make “mental models as objects” first-class but clearly distinct from e.g. domains/operations.
        "models": (
            "The response explicitly identifies and names relevant mental models (e.g., map/territory, "
            "inversion, feedback loops, incentives), explains why they apply (or fail) in this case, "
            "and compares or combines them rather than only applying them implicitly."
        ),
        # Incentives / reciprocity / cooperation / Gresham’s Law as a dedicated slice of relations.
        "incentives": (
            "The response focuses on explicit and implicit incentive structures, including rewards, "
            "penalties, reciprocity, cooperation, competition, and status dynamics, and explains how "
            "these incentives drive behaviour and outcomes for the actors involved."
        ),
        # Separate from generic 'risks': how systems handle stress, tails, and margin of safety.
        "resilience": (
            "The response concentrates on how the system behaves under stress and uncertainty—fragility "
            "vs robustness, margin of safety, leverage, debt, tail risks, and multiply-by-zero failure "
            "modes—and on design choices that increase or decrease resilience over time."
        ),
    },
    "scope": {
        "entity": (
            "The response focuses on what things are in view—objects, people, roles, "
            "systems, domains, or bounded units—without emphasizing actions or evaluation."
        ),
        "action": (
            "The response focuses on what is being done or intended—tasks, activities, "
            "operations, or work to be performed—rather than structure or meaning."
        ),
        "structure": (
            "The response focuses on how things are arranged or related—dependencies, "
            "coordination, constraints, incentives, or organizing patterns."
        ),
        "time": (
            "The response focuses on when things occur and how they change over time—"
            "sequences, evolution, history, or temporal dynamics."
        ),
        "evaluation": (
            "The response focuses on how quality, success, or goodness is judged—criteria, "
            "metrics, value, taste, or standards of assessment."
        ),
        "failure": (
            "The response focuses on breakdowns, stress, uncertainty, or limits—risks, "
            "edge cases, pain points, resilience, or what can go wrong."
        ),
        "meaning": (
            "The response focuses on why something exists or how it should be understood—"
            "purpose, assumptions, framing, terminology, or interpretive lens."
        ),
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
