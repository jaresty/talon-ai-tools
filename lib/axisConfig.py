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
        "diagram": (
            "The response converts the input into Mermaid diagram code only: it infers "
            "the best diagram type for the task and respects Mermaid safety constraints "
            "(Mermaid diagrams do not allow parentheses in the syntax or raw '|' "
            "characters inside node labels; the text uses numeric encodings such as "
            "\"#124;\" for '|' instead of raw problematic characters)."
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
        "skim": (
            "The response performs only a very light pass, addressing the most "
            "obvious or critical issues without aiming for completeness."
        ),
        "deep": (
            "The response goes into substantial depth within the chosen scope, unpacking "
            "reasoning layers and fine details without necessarily enumerating every edge "
            "case."
        ),
        "narrow": (
            "The response restricts the discussion to a very small slice of the topic, "
            "avoiding broad context."
        ),
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
        "contextualise": (
            "The response adds or reshapes context to support another "
            "operation—such as supplying background for an LLM or reframing "
            "content—without rewriting the main text itself."
        ),
        "formats": (
            "The response focuses on document types, writing formats, or structural "
            "templates and their suitability."
        ),
        "actions": (
            "The response stays within the selected target and focuses only on concrete "
            "actions or tasks a user or team could take, leaving out background analysis "
            "or explanation."
        ),
        "cocreate": (
            "The response works collaboratively with the user, proposing small moves, "
            "checking alignment, and iterating together instead of delivering a "
            "one-shot answer."
        ),
        "merge": (
            "The response combines multiple sources into a single coherent whole while "
            "preserving essential information."
        ),
        "rewrite": (
            "The response rewrites or refactors while preserving the original intent, "
            "treating the work as a mechanical transform rather than a "
            "reinterpretation."
        ),
        "facilitate": (
            "The response facilitates the session by framing the goal, proposing "
            "structure, managing turns, and keeping participation balanced rather "
            "than doing the work solo."
        ),
        "scaffold": (
            "The response explains with scaffolding: it starts from first principles, "
            "introduces ideas gradually, uses concrete examples and analogies, and "
            "revisits key points so a beginner can follow and retain the concepts."
        ),
        "indirect": (
            "The response begins with brief background, reasoning, and trade-offs and "
            "finishes with a clear bottom-line point or recommendation that ties them "
            "together."
        ),
        "direct": (
            "The response leads with the main point or recommendation, followed only by "
            "the most relevant supporting context, evidence, and next steps."
        ),
        "socratic": (
            "The response employs a Socratic, question-led method by asking short, "
            "targeted questions that surface assumptions, definitions, and gaps in "
            "understanding, withholding full conclusions until enough answers exist or "
            "the user explicitly requests a summary."
        ),
        "activities": (
            "The response lists concrete session activities or segments—what to do, "
            "by whom, and in what order—rather than abstract description."
        ),
        "case": (
            "The response builds the case before the conclusion by laying out background, "
            "evidence, trade-offs, and alternatives before converging on a clear "
            "recommendation that addresses objections and constraints."
        ),
        "ladder": (
            "The response uses abstraction laddering by placing the focal problem, "
            "stepping up to higher-level causes, and stepping down to consequences "
            "ordered by importance to the audience."
        ),
        "steps": (
            "The response solves the problem step by step, briefly labelling and "
            "explaining each step before presenting the final answer."
        ),
        "wasinawa": (
            "The response applies a What–So What–Now What reflection: it describes "
            "what happened, interprets why it matters, and proposes concrete next "
            "steps."
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
        # Stress, failure, and uncertainty
        "adversarial": (
            "The response runs a constructive stress-test, systematically searching "
            "for weaknesses, edge cases, counterexamples, failure modes, and "
            "unstated assumptions in order to improve the work."
        ),
        "inversion": (
            "The response begins from undesirable or catastrophic outcomes, asks what "
            "would reliably produce or amplify those outcomes, and works backward to "
            "avoid, mitigate, or design around those paths."
        ),
        "risks": (
            "The response focuses on potential problems, failure modes, or negative "
            "outcomes and their likelihood or severity."
        ),
        "unknowns": (
            "The response identifies critical unknown unknowns and explores how they "
            "might impact outcomes."
        ),
        "resilience": (
            "The response concentrates on how the system behaves under stress and "
            "uncertainty—fragility vs robustness, margin of safety, and tail risks."
        ),
        "probability": (
            "The response applies probability or statistical reasoning to characterise "
            "uncertainty and likely outcomes."
        ),
        # Causality, diagnosis, and testing
        "diagnose": (
            "The response seeks likely causes of problems first, narrowing hypotheses "
            "through evidence, falsification pressure, and targeted checks before "
            "proposing fixes or changes."
        ),
        "experimental": (
            "The response proposes concrete experiments or tests, outlines how each "
            "would run, describes expected outcomes, and explains how results would "
            "update the hypotheses."
        ),
        "effects": (
            "The response traces second- and third-order effects and summarises their "
            "downstream consequences."
        ),
        "constraints": (
            "The response identifies the system’s primary constraints, analyses the "
            "behaviours they enforce, and frames ways to balance or relieve them."
        ),
        # Time, dynamics, and evolution
        "simulation": (
            "The response uses explicit thought experiments or scenario walkthroughs "
            "to project how the situation might evolve over time, including feedback "
            "loops, bottlenecks, tipping points, and emergent effects."
        ),
        "dynamics": (
            "The response concentrates on how the system’s behaviour and state evolve "
            "over time, including transitions and feedback."
        ),
        "flow": (
            "The response explains step-by-step progression over time or sequence, "
            "showing how control, data, or narrative moves through the system."
        ),
        "origin": (
            "The response uncovers how the subject arose, why it looks this way now, "
            "and how past decisions shaped the present state."
        ),
        # Structure, relationships, and coordination
        "mapping": (
            "The response surfaces elements, relationships, and structure, organising "
            "them into a coherent map rather than a linear narrative."
        ),
        "depends": (
            "The response traces dependency relationships, identifying what depends on "
            "what and how changes propagate through the system."
        ),
        "melody": (
            "The response analyses coordination across components, time, or teams, "
            "including coupling, synchronization, and change alignment."
        ),
        "interfaces": (
            "The response concentrates on external interfaces, contracts, and "
            "boundaries between components or systems."
        ),
        # Option space and decision-making
        "explore": (
            "The response opens and surveys the option space by generating and "
            "comparing multiple plausible approaches without prematurely committing "
            "to a single answer."
        ),
        "converge": (
            "The response narrows the field, weighs trade-offs, and arrives at a small "
            "set of recommendations or a single decision."
        ),
        "prioritize": (
            "The response assesses and orders items by importance or impact, making "
            "the ranking and rationale explicit."
        ),
        # Patterns, abstraction, and models
        "motifs": (
            "The response identifies recurring patterns, themes, or clusters and "
            "explains why they matter."
        ),
        "models": (
            "The response explicitly identifies and names relevant mental models, "
            "explains why they apply (or fail), and compares or combines them."
        ),
        "dimension": (
            "The response expands conceptual dimensions of the subject and examines "
            "each axis to expose structure."
        ),
        # Math-inspired reasoning (non-numerical)
        "boom": (
            "The response explores behaviour toward extremes of scale or intensity, "
            "examining what breaks, dominates, or vanishes."
        ),
        "grove": (
            "The response examines accumulation, decay, or rate-of-change effects "
            "and how small contributions compound over time."
        ),
        "meld": (
            "The response reasons about combinations, overlaps, balances, and "
            "constraints between elements."
        ),
        "order": (
            "The response applies abstract structural reasoning such as hierarchy, "
            "dominance, or recurrence."
        ),
        # Human, organisational, and product lenses
        "actors": (
            "The response identifies people, roles, or agents involved in the system."
        ),
        "roles": (
            "The response focuses on responsibilities, ownership, and collaboration "
            "patterns."
        ),
        "incentives": (
            "The response analyses explicit and implicit incentive structures and how "
            "they drive behaviour."
        ),
        "jobs": (
            "The response analyses Jobs To Be Done—the outcomes users want to achieve "
            "and the forces shaping their choices."
        ),
        "product": (
            "The response examines the subject through a product lens—features, user "
            "needs, and value propositions."
        ),
        # Quality, clarity, and evaluation
        "analysis": (
            "The response describes and structures the situation without proposing "
            "specific actions or recommendations."
        ),
        "rigor": (
            "The response relies on disciplined, well-justified reasoning and makes "
            "its logic explicit."
        ),
        "objectivity": (
            "The response distinguishes objective facts from subjective opinions and "
            "supports claims with evidence."
        ),
        # System scope and context
        "systemic": (
            "The response analyses the subject as a whole system, including components, "
            "boundaries, flows, and feedback loops."
        ),
        "domains": (
            "The response identifies bounded contexts, domain boundaries, and "
            "capabilities."
        ),
        "operations": (
            "The response identifies operations research or management science concepts "
            "that frame the situation."
        ),
    },
    "scope": {
        "thing": (
            "The response focuses on what things are in view—objects, people, roles, "
            "systems, domains, or bounded units—without emphasizing actions or evaluation."
        ),
        "act": (
            "The response focuses on what is being done or intended—tasks, activities, "
            "operations, or work to be performed—rather than structure or meaning."
        ),
        "struct": (
            "The response focuses on how things are arranged or related—dependencies, "
            "coordination, constraints, incentives, or organizing patterns."
        ),
        "time": (
            "The response focuses on when things occur and how they change over time—"
            "sequences, evolution, history, or temporal dynamics."
        ),
        "good": (
            "The response focuses on how quality, success, or goodness is judged—criteria, "
            "metrics, value, taste, or standards of assessment."
        ),
        "fail": (
            "The response focuses on breakdowns, stress, uncertainty, or limits—risks, "
            "edge cases, pain points, resilience, or what can go wrong."
        ),
        "mean": (
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
