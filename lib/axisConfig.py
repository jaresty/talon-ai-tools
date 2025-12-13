"""Axis configuration as static Python maps (token -> description).

Generated from GPT/lists to avoid runtime file parsing; keep in sync with list edits."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "completeness": {
        "full": "Important: Provide a thorough answer for normal use; cover all major aspects, but you do "
        "not need every micro-detail.",
        "gist": "Important: Provide a short but complete answer or summary; cover the main points once "
        "without going into all details.",
        "max": "Important: Be as exhaustive as is reasonable; cover essentially everything relevant and "
        "treat omissions as errors.",
        "minimal": "Important: Make the smallest change or answer that satisfies the request; avoid extra "
        "work outside the core need.",
        "skim": "Important: Do a very light pass; address only the most obvious or critical issues. Do not "
        "aim for completeness.",
    },
    "directional": {
        "bog": "Important: Frame the preceding prompt through one unified perspective that blends acting, "
        "extending, reflection, and structure. Interpret these as a single fused stance—never separate "
        "or itemize.",
        "dig": "Important: Apply a concretizing-grounding perspective as one synthesized lens to frame the "
        "preceding prompt.",
        "dip bog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "concreteness, grounding, acting, extending, reflection, and structure. Interpret these as "
        "a single fused stance—never separate or itemize.",
        "dip ong": "Important: Frame the preceding prompt through one unified perspective that blends "
        "concreteness, grounding, acting, and extending. Interpret these as a single fused "
        "stance—never separate or itemize.",
        "dip rog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "concreteness, grounding, reflection, and structure. Interpret these as a single fused "
        "stance—never separate or itemize.",
        "fig": "Important: Apply an abstracting-generalizing-concretizing-grounding perspective as one "
        "synthesized lens to frame the preceding prompt.",
        "fip bog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, concreteness, grounding, acting, extending, reflection, and "
        "structure. Interpret these as a single fused stance—never separate or itemize.",
        "fip ong": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, concreteness, grounding, acting, and extending. Interpret "
        "these as a single fused stance—never separate or itemize.",
        "fip rog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, concreteness, grounding, reflection, and structure. "
        "Interpret these as a single fused stance—never separate or itemize.",
        "fly bog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, acting, extending, reflection, and structure. Interpret "
        "these as a single fused stance—never separate or itemize.",
        "fly ong": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, acting, and extending. Interpret these as a single fused "
        "stance—never separate or itemize.",
        "fly rog": "Important: Frame the preceding prompt through one unified perspective that blends "
        "abstraction, generalization, reflection, and structure. Interpret these as a single fused "
        "stance—never separate or itemize.",
        "fog": "Important: Apply an abstracting-generalizing perspective as one synthesized lens to frame the "
        "preceding prompt.",
        "jog": "Interpret and act. Don’t ask back — just infer the intent and carry it out directly.",
        "ong": "Important: Apply an acting-extending perspective as one synthesized lens to frame the "
        "preceding prompt.",
        "rog": "Important: Apply a reflective-structural perspective as one synthesized lens to frame the "
        "preceding prompt.",
    },
    "method": {
        "visual": "Important: Express the big picture using an abstract visual or metaphorical layout as a "
        "reasoning aid (for example, regions and contrasts) with a short legend and concise, format-ready "
        "hints when helpful.",
        "adversarial": "Important: Run a constructive stress-test: systematically search for weaknesses, edge "
        "cases, counterexamples, failure modes, and unstated assumptions, and prioritise critique "
        "and stress-testing over agreement while still aiming to improve the work.",
        "analysis": "Important: Describe, analyse, and structure the situation; do not propose specific actions, "
        "fixes, or recommendations.",
        "case": "Important: Build the case before the conclusion: lay out background, evidence, trade-offs, and "
        "alternatives first, then converge on a clear recommendation that shows how objections and "
        "constraints are addressed.",
        "cluster": "Important: Group similar items into labeled categories and describe each cluster, emphasising "
        "recurring patterns over isolated singletons.",
        "compare": "Important: Compare two or more items: list similarities and differences, highlighting subtle "
        "distinctions and tradeoffs that matter to the audience.",
        "contextualise": "Important: Add or reshape context to support another operation (for example, supplying "
        "background for an LLM or reframing content) without rewriting the main text itself.",
        "converge": "Important: Narrow down and make a call: weigh trade-offs, eliminate weaker options, and "
        "arrive at a small set of recommendations or a single decision.",
        "debugging": "Important: Use a debugging-style scientific method: summarise stable facts, list unresolved "
        "questions, propose plausible hypotheses, and design minimal experiments or checks to confirm "
        "or refute them, then narrow down likely root causes and outline fixes.",
        "deep": "Important: Go into substantial depth within the chosen scope; unpack reasoning layers and fine "
        "details without necessarily enumerating every edge case.",
        "diagnose": "Important: Look for likely causes of problems first; narrow down hypotheses before proposing "
        "fixes or changes.",
        "direct": "Important: Lead with the main point or recommendation first, then follow with only the most "
        "relevant supporting context, evidence, and next steps.",
        "diverge": "Important: Open up the option space: generate multiple, diverse possibilities or angles "
        "without prematurely judging or collapsing to a single answer.",
        "experimental": "Important: Reason in an experimental or scientific style: given a problem, propose one or "
        "more concrete experiments that could help solve it, outline how each experiment would "
        "run, what outcomes you expect, and how those outcomes would update your hypotheses.",
        "filter": "Important: Extract only items that match a clearly stated criterion (for example, pain points, "
        "risks, open questions); do not restate everything else.",
        "flow": "Important: Focus on flow over time or sequence: explain how control, data, or narrative moves "
        "step by step through the material.",
        "indirect": "Important: Start with brief background, reasoning, and trade-offs, then finish with a clear "
        "bottom-line point or recommendation that ties them together.",
        "ladder": "Important: Use abstraction laddering: place the focal problem, then step up to higher-level "
        "causes and down to consequences, ordered by importance to the audience.",
        "liberating": "Important: Facilitate using Liberating Structures: emphasise distributed participation, "
        "short structured interactions, concrete invitations, and visual, stepwise processes; name "
        "or evoke specific LS patterns when helpful (for example, 1-2-4-All, TRIZ, 15% Solutions).",
        "mapping": "Important: Emphasise mapping over exposition: surface elements, relationships, and structure; "
        "organise them into a coherent map (textual, tabular, or visual) rather than a linear "
        "narrative.",
        "motifs": "Important: Scan for recurring motifs and patterns: identify repeated elements, themes, "
        "clusters, and notable outliers, and briefly explain why they matter.",
        "plan": "Important: Give a short plan first, then carry it out; clearly separate the plan from the "
        "execution.",
        "prioritize": "Important: Assess and order items by importance or impact to the stated audience; make the "
        "ranking and rationale explicit.",
        "rewrite": "Important: Rewrite or refactor while preserving the original intent; treat this as a "
        "mechanical transform, not a re-interpretation.",
        "rigor": "Important: Use disciplined, well-justified reasoning; avoid hand-waving and make your logic "
        "explicit.",
        "samples": "Important: Generate several diverse, self-contained options and, where appropriate, attach "
        "short descriptions and explicit numeric probabilities that approximately sum to 1; avoid "
        "near-duplicate options.",
        "scaffold": "Important: Explain with scaffolding: start from first principles, introduce ideas gradually, "
        "use concrete examples and analogies, and revisit key points so a beginner can follow and "
        "retain the concepts.",
        "socratic": "Important: Use a Socratic, question-led method: advance primarily by asking short, targeted "
        "questions that surface assumptions, definitions, and gaps in understanding; hold back from "
        "giving full conclusions until enough answers are available or the user explicitly asks for a "
        "summary.",
        "steps": "Important: Solve this step by step; briefly label and explain each step before giving the final "
        "answer.",
        "structure": "Important: Focus on structural aspects: outline parts, hierarchy, containment, and how "
        "elements are organised, rather than explaining detailed behaviour.",
        "systemic": "Important: Analyse the subject using systems thinking, focusing on boundaries, components, "
        "flows, feedback loops, emergence, and leverage points.",
        "taxonomy": "Important: Build or refine a taxonomy: define categories, subtypes, and relationships to "
        "clarify structure; prefer compact representations over prose.",
        "wasinawa": "Important: Apply a What–So What–Now What reflection: first describe what happened, then "
        "interpret why it matters, then propose concrete next steps.",
        "xp": "Important: Use an Extreme Programming-style approach: favour very small, incremental changes; rely "
        "on working software and tests as primary feedback; and iterate with tight, collaborative feedback "
        "loops rather than big-bang plans.",
    },
    "scope": {
        "actions": "Important: Within the selected target, focus only on concrete actions or tasks that a user or "
        "team could take, not on background analysis or explanation.",
        "activities": "Important: Within the selected target, enumerate concrete session activities or segments "
        "(what to do, by whom, in what order), rather than abstract description.",
        "bound": "Important: Within the selected target, stay inside explicit conceptual limits that are inferred "
        "from or stated in the prompt; do not introduce material outside them.",
        "dynamics": "\"Important: Within the selected target, focus on how the system's behaviour and state evolve "
        'over time: scenarios, state changes, feedback loops, and transitions."',
        "edges": "Important: Within the selected target, emphasise edge cases, errors, and unusual conditions "
        "around the subject.",
        "focus": "Important: Within the selected target, stay tightly on a central theme; avoid tangents and "
        "side-quests.",
        "interfaces": "Important: Within the selected target, focus on external interfaces, contracts, and "
        "boundaries between components or systems, not on their internal implementations.",
        "narrow": "Important: Within the selected target, restrict your discussion to a very small slice of the "
        "topic; avoid broad context.",
        "relations": "Important: Within the selected target, focus on the relationships, interactions, and "
        "dependencies between elements, not their internal details.",
        "system": "Important: Within the selected target, focus on the overall system as a whole: its components, "
        "boundaries, stakeholders, and internal structure, rather than individual lines or snippets.",
    },
    "form": {
        "adr": "Important: Express the answer as an Architecture Decision Record (ADR) with sections for context, "
        "decision, and consequences, using a concise, document-like style.",
        "bug": "Important: Format the answer as a structured bug report with clear sections for Steps to Reproduce, "
        "Expected Behavior, Actual Behavior, and Environment/Context; focus on concise, testable details.",
        "bullets": "Important: Format the main answer as concise bullet points only; avoid long paragraphs.",
        "cards": "Important: Present the main answer as a set of discrete cards or items, each with a clear heading "
        "and a short body; avoid long continuous prose.",
        "checklist": "Important: Present the main answer as an actionable checklist; each item should be a clear, "
        "imperative task rather than descriptive prose.",
        "code": "Important: Output only code or markup for the main answer, with no surrounding natural-language "
        "explanation.",
        "commit": "Important: Express the answer as a conventional commit message with a short type/scope line and, "
        "if needed, a concise body.",
        "faq": "Important: Format the answer as an FAQ-style list: a sequence of clearly separated question "
        "headings with concise answers beneath each one; keep questions and answers easy to skim, and avoid "
        "long uninterrupted prose.",
        "gherkin": "Important: Output only Gherkin using Jira markup where appropriate; no surrounding explanation.",
        "headline": "Important: Use a headline-first presentation: state the main point up front, then layer "
        "supporting details beneath; prioritise readability and skimmability.",
        "log": "Important: Format the answer as a concise work or research log entry: include date or time markers "
        "when appropriate, short bullet-style updates, and enough context for future you to understand what "
        "happened without adding unrelated narrative.",
        "plain": "Important: Use straightforward, everyday language; minimise jargon and complex sentence "
        "structures.",
        "recipe": "Important: Express the answer as a recipe with a custom, clearly explained mini-language plus a "
        "short key for understanding it.",
        "shellscript": "Important: Express the solution as a shell script, focusing on correct, executable shell "
        "code rather than prose.",
        "spike": '"Important: Format the backlog item as a research spike: start with a brief problem or decision '
        "statement, then list the key questions the spike should answer; keep the emphasis on questions "
        'and learning, not implementation tasks."',
        "story": '"Important: Format the backlog item as a user story using \\"As a <persona>, I want <capability>, '
        'so that <value>.\\" Optionally include a short description and high-level acceptance criteria in '
        'plain prose, but do not use Gherkin or test-case syntax here."',
        "table": "Important: Present the main answer as a Markdown table when feasible; keep columns and rows "
        "compact.",
        "tight": "Important: Make the answer short and dense; remove fluff and redundancy.",
    },
    "channel": {
        "announce": "Important: Format the answer as a clear announcement suitable for sharing with a team or "
        "channel: start with a short headline, briefly explain what changed and why, and end with any "
        "relevant actions or next steps for readers.",
        "codetour": "Important: Output only a valid VS Code CodeTour `.tour` JSON document (schema-compatible), "
        "using steps and fields appropriate to the task; do not include any extra prose or surrounding "
        "explanation.",
        "diagram": '"Important: Convert the input into appropriate Mermaid diagram code only: infer the best '
        "diagram type for the task, and respect existing Mermaid safety constraints (Mermaid diagrams do "
        "not allow parentheses in the syntax or raw '|' characters inside node labels; use careful "
        'numeric label encoding such as \\"#124;\\" for \'|\' instead of raw problematic characters)."',
        "html": "Important: Output only semantic HTML for the answer, with no surrounding prose.",
        "jira": "Important: Format the answer using Jira markup (headings, lists, panels) where relevant, without "
        "adding extra explanation beyond the content.",
        "presenterm": '"Important: Transform the input into a valid multi-slide presenterm deck; output raw '
        'Markdown only (no code fences). Front matter exactly: \\"--- newline title: <use a '
        "descriptive title based on the input, never leave blank; in the title, encode any colon ':' "
        "as &#58; and encode < and > as &lt; and &gt;> newline author: Generated (or authors: [...] ) "
        'newline date: YYYY-MM-DD newline --- newline\\"; no other keys. Produce up to 12 slides (no '
        "minimum required); each slide MUST start with a Setext header (Title line, next line exactly "
        "---), include content and references, and end with an HTML comment named end_slide on its "
        "own line with nothing else, then a blank line; the final slide MAY omit the closing "
        "end_slide. ALWAYS insert a blank line before the References section so that a line with "
        '\\"References\\" or \\"- References\\" is preceded by one empty line. Emit directives only '
        "as HTML comments on their own line with exact syntax and nothing else on the line: end_slide "
        '= \\"<!-- end_slide -->\\"; pause = \\"<!-- pause -->\\"; column_layout with weights = '
        '\\"<!-- column_layout: [7, 3] -->\\"; column with index = \\"<!-- column: 0 -->\\"; '
        'reset_layout = \\"<!-- reset_layout -->\\"; jump_to_middle = \\"<!-- jump_to_middle -->\\". '
        "CODE FENCE SAFETY: whenever a fenced code block opens (e.g., ```mermaid +render, ```bash "
        "+exec, ```latex +render, ```d2 +render), you MUST emit a matching closing fence of exactly "
        "three backticks on its own line BEFORE any non-code content, directive, or end_slide; IF a "
        "fence is still open at slide end, AUTO-EMIT the closing fence first. Support mermaid "
        "diagrams via code blocks tagged mermaid +render; support LaTeX via code blocks tagged latex "
        "+render; support D2 via code blocks tagged d2 +render; support executable snippets via "
        "fenced code blocks whose info string starts with a language then +exec (optionally "
        '+id:<name>) or +exec_replace or +image; only emit \\"<!-- snippet_output: name -->\\" if a '
        "snippet with +id:name exists. Hide code lines with # or /// prefixes per language; other "
        "code blocks only if relevant (name the language); images only if valid paths/URLs. HTML "
        "SAFETY IN SLIDE BODY (outside all fenced/inline code and outside HTML directives): raw HTML "
        "is NOT allowed; therefore you MUST replace EVERY literal '<' with &lt; and EVERY literal '>' "
        "with &gt; in body text (including list items and headings); NEVER output raw '<' or '>' in "
        "body text. Markdown safety in SLIDE BODY: prevent accidental styling by encoding isolated "
        "control chars unless part of valid syntax; encode every standalone or path-embedded '~' as "
        '\\"&#126;\\" (so \\"~/foo\\" becomes \\"&#126;/foo\\"), but keep intentional \\"~~text~~\\" '
        "unchanged. MERMAID SAFETY: inside mermaid code blocks, preserve Mermaid grammar and "
        "delimiters unchanged ([], (), [[]], (()), [/ /]); for NODE/EDGE LABEL TEXT you MUST wrap the "
        "entire label in ASCII double quotes and, inside that quoted text ONLY, you may encode "
        "problematic characters using Mermaid-compatible numeric codes with NO leading ampersand: use "
        "\\\"#91;\\\" for '[', \\\"#93;\\\" for ']', \\\"#40;\\\" for '(', \\\"#41;\\\" for ')', "
        "\\\"#123;\\\" for '{{', \\\"#125;\\\" for '}}', \\\"#60;\\\" for '<', \\\"#62;\\\" for '>', "
        "\\\"#35;\\\" for '#', \\\"#58;\\\" for ':', and \\\"#124;\\\" for '|'; escape an internal "
        "double quote as \\\"\\\"; leave ampersands '&' and slashes '/' as-is; do not apply any "
        'other entity encodings inside labels; do not double-encode. Avoid # headers."',
        "remote": "Important: Optimise for remote delivery: make instructions work in distributed/online contexts "
        "and surface tooling/interaction hints that work over video/voice/screenshare.",
        "slack": "Important: Format the answer for Slack, using appropriate Markdown, mentions, and code blocks, "
        "without adding channel-irrelevant decoration.",
        "sync": "Important: Shape the output as a synchronous/live session plan (agenda, steps, cues) rather than "
        "static reference text.",
        "svg": "Important: Output only SVG markup for the answer, with no surrounding prose; prefer minimal, valid "
        "SVG suitable for copy/paste into an `.svg` file.",
    },
}

AXIS_VALUE_TO_KEY: Dict[str, Dict[str, str]] = {}
for axis, mapping in AXIS_KEY_TO_VALUE.items():
    v2k: Dict[str, str] = {}
    for short, desc in mapping.items():
        v2k[short] = short
        v2k[desc] = short
        if (desc.startswith(""") and desc.endswith(""")) or (
            desc.startswith(" ) and desc.endswith(")
        ):
            unquoted = desc[1:-1].strip()
            if unquoted:
                v2k[unquoted] = short
    AXIS_VALUE_TO_KEY[axis] = v2k


def axis_key_to_value_map(axis: str) -> dict[str, str]:
    return AXIS_KEY_TO_VALUE.get(axis, {})


def axis_value_to_key_map(axis: str) -> dict[str, str]:
    return AXIS_VALUE_TO_KEY.get(axis, {})


@dataclass(frozen=True)
class AxisDoc:
    """Structured axis documentation entry for Concordance and UI surfaces."""

    axis: str
    key: str
    description: str
    group: str | None = None
    flags: FrozenSet[str] = field(default_factory=frozenset)


def axis_docs_for(axis: str) -> list[AxisDoc]:
    """Return structured docs for a single axis key->description map."""
    mapping = AXIS_KEY_TO_VALUE.get(axis, {})
    return [
        AxisDoc(axis=axis, key=key, description=desc) for key, desc in mapping.items()
    ]


def axis_docs_index() -> dict[str, list[AxisDoc]]:
    """Return structured docs for all axes keyed by axis name."""
    return {axis: axis_docs_for(axis) for axis in AXIS_KEY_TO_VALUE}
