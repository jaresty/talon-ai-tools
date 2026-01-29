"""Axis configuration as static Python maps (token -> description).

Generated from the axis registry; keep in sync with list edits."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "channel": {
        "adr": (
            "The response takes the shape of an Architecture Decision Record (ADR) "
            "document with sections for context, decision, and consequences, formatted as "
            "a structured document ready for version control."
        ),
        "code": (
            "The response consists only of code or markup as the complete output, with no "
            "surrounding natural-language explanation or narrative."
        ),
        "codetour": (
            "The response is delivered as a valid VS Code CodeTour `.tour` JSON file "
            "(schema-compatible) with steps and fields appropriate to the task, "
            "omitting extra prose or surrounding explanation."
        ),
        "diagram": (
            "The response converts the input into Mermaid diagram code only: it infers "
            "the best diagram type for the task and respects Mermaid safety "
            "constraints (Mermaid diagrams do not allow parentheses in the syntax or "
            "raw '|' characters inside node labels; the text uses numeric encodings "
            "such as \"#124;\" for '|' instead of raw problematic characters)."
        ),
        "gherkin": (
            "The response outputs only Gherkin format as the complete output, using "
            "Jira markup where appropriate and omitting surrounding explanation."
        ),
        "html": (
            "The response consists solely of semantic HTML as the complete output, with "
            "no surrounding prose or explanation."
        ),
        "jira": (
            "The response formats the content using Jira markup (headings, lists, panels) "
            "where relevant and avoids extra explanation beyond the main material."
        ),
        "plain": (
            "The response uses plain prose with natural paragraphs and sentences as the "
            "delivery format, imposing no additional structural conventions such as "
            "bullets, tables, or code blocks."
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
        "shellscript": (
            "The response is delivered as a shell script output format, focusing "
            "on correct, executable shell code rather than prose or explanation."
        ),
        "slack": (
            "The response formats the answer for Slack using appropriate Markdown, "
            "mentions, and code blocks while avoiding channel-irrelevant decoration."
        ),
        "svg": (
            "The response consists solely of SVG markup as the complete output, with no "
            "surrounding prose, remaining minimal and valid for direct use in an `.svg` "
            "file."
        ),
        "sync": (
            "The response takes the shape of a synchronous or live session plan (agenda, "
            "steps, cues) rather than static reference text."
        ),
    },
    "completeness": {
        "deep": (
            "The response goes into substantial depth within the chosen scope, "
            "unpacking reasoning layers and fine details without necessarily "
            "enumerating every edge case."
        ),
        "full": (
            "The response provides a thorough answer for normal use, covering all "
            "major aspects without needing every micro-detail."
        ),
        "gist": (
            "The response offers a short but complete answer or summary that touches "
            "the main points once without exploring every detail."
        ),
        "max": (
            "The response is as exhaustive as reasonable, covering essentially "
            "everything relevant and treating omissions as errors."
        ),
        "minimal": (
            "The response makes the smallest change or provides the smallest "
            "answer that satisfies the request, avoiding work outside the core "
            "need."
        ),
        "narrow": (
            "The response restricts the discussion to a very small slice of the "
            "topic, avoiding broad context."
        ),
        "skim": (
            "The response performs only a very light pass, addressing the most "
            "obvious or critical issues without aiming for completeness."
        ),
    },
    "directional": {
        "bog": (
            "The response modifies the task to examine the subject's structure and "
            "reflect on it, then identifies actions to take and extends them to "
            "related contexts."
        ),
        "dig": (
            "The response modifies the task to examine concrete details and grounding "
            "examples, focusing on specifics rather than abstractions."
        ),
        "dip bog": (
            "The response modifies the task to start with concrete examples and "
            "grounded details, examines their structure and reflects on patterns, "
            "then identify actions and extensions."
        ),
        "dip ong": (
            "The response modifies the task to start with concrete examples, "
            "identify actions to take from them, then extends those actions to "
            "related situations."
        ),
        "dip rog": (
            "The response modifies the task to examine concrete details and "
            "grounded examples, then reflects on their structural patterns and "
            "what they reveal."
        ),
        "fig": (
            "The response modifies the task to alternate between abstract principles "
            "and concrete examples, using each to illuminate the other (figure-ground "
            "reversal)."
        ),
        "fip bog": (
            "The response modifies the task to move between abstract principles "
            "and concrete examples, examines their structural patterns and "
            "reflects on them, then identifies actions and extends them to related "
            "contexts."
        ),
        "fip ong": (
            "The response modifies the task to alternate between abstract "
            "principles and concrete examples, then identifies actions to take and "
            "extends them to related situations."
        ),
        "fip rog": (
            "The response modifies the task to move between abstract principles "
            "and concrete examples while examining structural patterns and "
            "reflecting on what they reveal."
        ),
        "fly bog": (
            "The response modifies the task to identify abstract patterns and "
            "general principles, examine their structure and reflects on it, then "
            "identifies actions and extends them to related contexts."
        ),
        "fly ong": (
            "The response modifies the task to identify abstract patterns and "
            "general principles, then propose concrete actions and extends them to "
            "related contexts."
        ),
        "fly rog": (
            "The response modifies the task to identify abstract patterns and "
            "general principles, then examines their structural relationships and "
            "reflect on their implications."
        ),
        "fog": (
            "The response modifies the task to identify general patterns and abstract "
            "principles from the specifics, moving from particular cases to broader "
            "insights."
        ),
        "jog": (
            "The response modifies the task to interpret the intent and carry it out "
            "directly without asking follow-up questions."
        ),
        "ong": (
            "The response modifies the task to identify concrete actions to take, then "
            "extends those actions to related situations or next steps."
        ),
        "rog": (
            "The response modifies the task to examine the structure of the subject "
            "(how it is organized), then reflects on why that structure exists and "
            "what it reveals."
        ),
    },
    "form": {
        "actions": (
            "The response structures ideas as concrete actions or tasks a user or team "
            "could take, leaving out background analysis or explanation."
        ),
        "activities": (
            "The response organizes ideas as concrete session activities or "
            "segments—what to do, by whom, and in what order—rather than abstract "
            "description."
        ),
        "bug": (
            "The response structures ideas as a bug report with sections for Steps to "
            "Reproduce, Expected Behavior, Actual Behavior, and Environment or Context, "
            "emphasizing concise, testable details."
        ),
        "bullets": (
            "The response organizes ideas as concise bullet points, avoiding long "
            "paragraphs."
        ),
        "cards": (
            "The response organizes ideas as discrete cards or items, each with a clear "
            "heading and short body, avoiding long continuous prose."
        ),
        "case": (
            "The response structures reasoning by building the case before the conclusion, "
            "laying out background, evidence, trade-offs, and alternatives before converging "
            "on a clear recommendation that addresses objections and constraints."
        ),
        "checklist": (
            "The response organizes ideas as an actionable checklist whose items are "
            "clear imperative tasks rather than descriptive prose."
        ),
        "cocreate": (
            "The response structures interaction collaboratively, proposing small moves, "
            "checking alignment, and iterating together instead of delivering a one-shot "
            "answer."
        ),
        "commit": (
            "The response structures ideas as a conventional commit message with a short "
            "type or scope line and an optional concise body."
        ),
        "contextualise": (
            "The response structures ideas by adding or reshaping context to "
            "support another operation—such as supplying background for an LLM or "
            "reframing content—without rewriting the main text itself."
        ),
        "direct": (
            "The response structures ideas by leading with the main point or "
            "recommendation, followed only by the most relevant supporting context, "
            "evidence, and next steps."
        ),
        "facilitate": (
            "The response structures interaction by framing the goal, proposing "
            "structure, managing turns, and keeping participation balanced rather than "
            "doing the work solo."
        ),
        "faq": (
            "The response organizes ideas as clearly separated question headings with concise "
            "answers beneath each one, keeping content easy to skim and free of long "
            "uninterrupted prose."
        ),
        "formats": (
            "The response structures ideas by focusing on document types, writing "
            "formats, or structural templates and their suitability."
        ),
        "indirect": (
            "The response begins with brief background, reasoning, and trade-offs and "
            "finishes with a clear bottom-line point or recommendation that ties them "
            "together."
        ),
        "ladder": (
            "The response uses abstraction laddering by placing the focal problem, "
            "stepping up to higher-level causes, and stepping down to consequences ordered "
            "by importance to the audience."
        ),
        "log": (
            "The response reads like a concise work or research log entry with date or time "
            "markers as needed, short bullet-style updates, and enough context for future "
            "reference without unrelated narrative."
        ),
        "merge": (
            "The response combines multiple sources into a single coherent whole while "
            "preserving essential information."
        ),
        "questions": (
            "The response presents the answer as a series of probing or clarifying "
            "questions rather than statements."
        ),
        "recipe": (
            "The response expresses the answer as a recipe that includes a custom, clearly "
            "explained mini-language and a short key for understanding it."
        ),
        "rewrite": (
            "The response rewrites or refactors while preserving the original intent, "
            "treating the work as a mechanical transform rather than a reinterpretation."
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
        "table": (
            "The response presents the main answer as a Markdown table when feasible, "
            "keeping columns and rows compact."
        ),
        "taxonomy": (
            "The response structures ideas as a classification system, type hierarchy, "
            "or category taxonomy, defining types, their relationships, and "
            "distinguishing attributes clearly."
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
        "walkthrough": (
            "The response guides the audience step by step by outlining stages and "
            "walking through them in order so understanding builds gradually."
        ),
        "wardley": (
            "The response expresses the answer as a Wardley Map showing value chain "
            "evolution from genesis to commodity."
        ),
        "wasinawa": (
            "The response applies a What–So What–Now What reflection: it describes what "
            "happened, interprets why it matters, and proposes concrete next steps."
        ),
    },
    "method": {
        "actors": (
            "The response enhances the task by identifying and centering people, roles, "
            "or agents involved in the system."
        ),
        "adversarial": (
            "The response enhances the task by running a constructive stress-test, "
            "systematically searching for weaknesses, edge cases, counterexamples, "
            "failure modes, and unstated assumptions."
        ),
        "analysis": (
            "The response enhances the task by describing and structuring the "
            "situation, focusing on understanding before proposing actions or "
            "recommendations."
        ),
        "boom": (
            "The response enhances the task by exploring behaviour toward extremes of "
            "scale or intensity, examining what breaks, dominates, or vanishes."
        ),
        "cite": (
            "The response enhances the task by including sources, citations, or references "
            "that anchor claims to evidence, enabling verification and further "
            "exploration."
        ),
        "constraints": (
            "The response enhances the task by identifying the system's primary "
            "constraints, analyzing the behaviours they enforce, and framing ways "
            "to balance or relieve them."
        ),
        "converge": (
            "The response enhances the task by systematically narrowing from broad "
            "exploration to focused recommendations, weighing trade-offs explicitly as "
            "options are filtered."
        ),
        "depends": (
            "The response enhances the task by tracing dependency relationships, "
            "identifying what depends on what and how changes propagate through the "
            "system."
        ),
        "diagnose": (
            "The response enhances the task by seeking likely causes of problems "
            "first, narrowing hypotheses through evidence, falsification pressure, and "
            "targeted checks before proposing fixes or changes."
        ),
        "dimension": (
            "The response enhances the task by exploring multiple dimensions or axes "
            "of analysis, making implicit factors explicit and examining how they "
            "interact."
        ),
        "domains": (
            "The response enhances the task by identifying bounded contexts, domain "
            "boundaries, and capabilities."
        ),
        "dynamics": (
            "The response enhances the task by concentrating on how the system's "
            "behaviour and state evolve over time, including transitions and feedback."
        ),
        "effects": (
            "The response enhances the task by tracing second- and third-order effects "
            "and summarizing their downstream consequences."
        ),
        "experimental": (
            "The response enhances the task by proposing concrete experiments or "
            "tests, outlining how each would run, describing expected outcomes, "
            "and explaining how results would update the hypotheses."
        ),
        "explore": (
            "The response enhances the task by opening and surveying the option space, "
            "generating and comparing multiple plausible approaches without prematurely "
            "committing to a single answer."
        ),
        "flow": (
            "The response enhances the task by explaining step-by-step progression over "
            "time or sequence, showing how control, data, or narrative moves through the "
            "system."
        ),
        "grove": (
            "The response enhances the task by examining accumulation, decay, or "
            "rate-of-change effects and how small contributions compound over time."
        ),
        "incentives": (
            "The response enhances the task by analyzing explicit and implicit "
            "incentive structures and how they drive behaviour."
        ),
        "interfaces": (
            "The response enhances the task by concentrating on external interfaces, "
            "contracts, and boundaries between components or systems."
        ),
        "inversion": (
            "The response enhances the task by beginning from undesirable or "
            "catastrophic outcomes, asking what would produce or amplify them, then "
            "working backward to avoid, mitigate, or design around those paths."
        ),
        "jobs": (
            "The response enhances the task by analyzing Jobs To Be Done—the outcomes "
            "users want to achieve and the forces shaping their choices."
        ),
        "mapping": (
            "The response enhances the task by surfacing elements, relationships, and "
            "structure, then organising them into a coherent spatial map rather than a "
            "linear narrative."
        ),
        "meld": (
            "The response enhances the task by reasoning about combinations, overlaps, "
            "balances, and constraints between elements."
        ),
        "melody": (
            "The response enhances the task by analyzing coordination across components, "
            "time, or teams, including coupling, synchronization, and change alignment."
        ),
        "mod": (
            "The response enhances the task by applying modulo-style reasoning—equivalence "
            "classes, cyclic patterns, quotient structures, or periodic behavior that "
            "repeats with a defined period or wraps around boundaries."
        ),
        "models": (
            "The response enhances the task by explicitly identifying and naming "
            "relevant mental models, explaining why they apply (or fail), and comparing "
            "or combining them."
        ),
        "motifs": (
            "The response enhances the task by identifying recurring patterns, themes, "
            "or clusters and explaining why they matter."
        ),
        "objectivity": (
            "The response enhances the task by distinguishing objective facts from "
            "subjective opinions and supporting claims with evidence."
        ),
        "operations": (
            "The response enhances the task by identifying operations research or "
            "management science concepts that frame the situation."
        ),
        "order": (
            "The response enhances the task by applying abstract structural reasoning "
            "such as hierarchy, dominance, or recurrence."
        ),
        "origin": (
            "The response enhances the task by uncovering how the subject arose, why it "
            "looks this way now, and how past decisions shaped the present state."
        ),
        "prioritize": (
            "The response enhances the task by assessing and ordering items by "
            "importance or impact, making the ranking and rationale explicit."
        ),
        "probability": (
            "The response enhances the task by applying probability or statistical "
            "reasoning to characterize uncertainty and likely outcomes."
        ),
        "product": (
            "The response enhances the task by examining the subject through a product "
            "lens—features, user needs, and value propositions."
        ),
        "resilience": (
            "The response enhances the task by concentrating on how the system "
            "behaves under stress and uncertainty—fragility vs robustness, margin of "
            "safety, and tail risks."
        ),
        "rigor": (
            "The response enhances the task by relying on disciplined, well-justified "
            "reasoning and making its logic explicit."
        ),
        "risks": (
            "The response enhances the task by focusing on potential problems, failure "
            "modes, or negative outcomes and their likelihood or severity."
        ),
        "roles": (
            "The response enhances the task by focusing on responsibilities, ownership, "
            "and collaboration patterns."
        ),
        "simulation": (
            "The response develops explicit thought experiments or scenario "
            "walkthroughs that project evolution over time, highlighting feedback loops, bottlenecks, tipping points, and emergent effects."
        ),
        "systemic": (
            "The response enhances the task by analyzing the subject as a whole "
            "system, identifying components, boundaries, flows, and feedback loops."
        ),
        "unknowns": (
            "The response enhances the task by identifying critical unknown unknowns "
            "and exploring how they might impact outcomes."
        ),
    },
    "scope": {
        "act": (
            "The response focuses on what is being done or intended—tasks, activities, "
            "operations, or work to be performed—rather than structure or meaning."
        ),
        "fail": (
            "The response focuses on breakdowns, stress, uncertainty, or limits—risks, edge "
            "cases, pain points, resilience, or what can go wrong."
        ),
        "good": (
            "The response focuses on how quality, success, or goodness is judged—criteria, "
            "metrics, value, taste, or standards of assessment."
        ),
        "mean": (
            "The response focuses on why something exists or how it should be "
            "understood—purpose, assumptions, framing, terminology, or interpretive lens."
        ),
        "struct": (
            "The response focuses on how things are arranged or related—dependencies, "
            "coordination, constraints, incentives, or organizing patterns."
        ),
        "thing": (
            "The response focuses on what things are in view—objects, people, roles, "
            "systems, domains, or bounded units—without emphasizing actions or evaluation."
        ),
        "time": (
            "The response focuses on when things occur and how they change over "
            "time—sequences, evolution, history, or temporal dynamics."
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
