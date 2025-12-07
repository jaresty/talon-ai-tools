from __future__ import annotations

from typing import TypedDict, Union

# Central configuration for static prompts:
# - Each key is a canonical static prompt value (as used in GPT/lists/staticPrompt.talon-list).
# - "description" provides the human-readable Task line and help text.
# - Optional completeness/scope/method/style fields define per-prompt axis profiles.


class StaticPromptProfile(TypedDict, total=False):
    description: str
    completeness: str
    # Scope, method, and style may be expressed as a single token or a small
    # list of tokens; callers are responsible for any further normalisation.
    scope: Union[str, list[str]]
    method: Union[str, list[str]]
    style: Union[str, list[str]]


STATIC_PROMPT_CONFIG: dict[str, StaticPromptProfile] = {
    # Default "infer the task" prompt used when no explicit staticPrompt
    # is provided. This keeps the visible Task description consistent with
    # the historical fallback while giving it a concise recipe token.
    "infer": {
        "description": "I'm not telling you what to do. Infer the task.",
    },
    "LLM": {
        "description": "Return one or more prompts for an LLM, each fitting on a single line.",
    },
    # Analysis, structure, and perspective prompts (description-only profiles).
    "describe": {
        "description": "Just describe this objectively.",
    },
    "undefined": {
        "description": "List undefined terms only.",
    },
    "who": {
        "description": "Explain who.",
    },
    "what": {
        "description": "Explain what.",
    },
    "when": {
        "description": "Explain when.",
    },
    "where": {
        "description": "Explain where.",
    },
    "why": {
        "description": "Explain why.",
    },
    "how": {
        "description": "Explain how.",
    },
    "assumption": {
        "description": "Identify and explain the assumptions behind this.",
    },
    "objectivity": {
        "description": "Assess objectivity with examples.",
    },
    "knowledge": {
        "description": "Identify relevant academic or industry fields of knowledge and explain why each applies and what perspective it offers.",
    },
    "taste": {
        "description": (
            "Evaluate the taste of the subject by analysing harmony, proportion, restraint, authenticity, and cultural/historical appropriateness, "
            "explaining strengths, weaknesses, and contextual fit."
        ),
    },
    "tao": {
        "description": (
            "Classify the subject through Taoist philosophy—relate it to Dao, De, Yin/Yang, Wu Wei, Ziran, Pu, Qi, and Li; identify which apply and why."
        ),
    },
    # Planning, product, and execution prompts (description-only profiles).
    "product": {
        "description": "Frame this through a product lens.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "metrics": {
        "description": "List metrics that result in these outcomes with concrete examples.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "value": {
        "description": "Explain the user value of this.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "jobs": {
        "description": "List the Jobs To Be Done (JTBD) for this.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "done": {
        "description": "Describe the definition of done for this.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "operations": {
        "description": "Infer an appropriate Operations Research or management science concept to apply.",
        "completeness": "gist",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "facilitate": {
        "description": "Design a meeting for this.",
        "completeness": "full",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "ticket": {
        "description": "Draft a Jira-style user story ticket for this issue.",
        "completeness": "full",
        "scope": ["actions"],
        "method": ["structure"],
        "style": ["jira", "story"],
    },
    # Exploration, critique, and reflection prompts (description-only profiles).
    "challenge": {
        "description": "Challenge this with questions so we can make it better.",
    },
    "critique": {
        "description": "This looks bad. What is wrong with it?",
    },
    "retro": {
        "description": "Help me introspect or reflect on this.",
    },
    "pain": {
        "description": "List 3–5 pain points, issues, obstacles, or challenges, ordered by importance to the audience.",
        "completeness": "gist",
        "method": "filter",
        "style": "bullets",
        "scope": "focus",
    },
    "easier": {
        "description": "This is too much work; propose something I can accomplish in a smaller timescale.",
    },
    "true": {
        "description": "Assess whether this is true, based on the available information.",
    },
    "question": {
        "description": "Ask open-ended questions about this that are important to the audience.",
        "completeness": "gist",
        "method": "filter",
        "style": "bullets",
        "scope": "focus",
    },
    "relevant": {
        "description": "Identify what is relevant here.",
        "completeness": "gist",
        "method": "filter",
        "style": "bullets",
        "scope": "focus",
    },
    "misunderstood": {
        "description": "Identify what is misunderstood in this situation.",
        "completeness": "gist",
        "method": "filter",
        "style": "bullets",
        "scope": "focus",
    },
    "risky": {
        "description": "Highlight what is risky and why.",
        "completeness": "gist",
        "method": "filter",
        "style": "bullets",
        "scope": "focus",
    },
    # Transformation and reformatting prompts (description-only profiles).
    "split": {
        "description": "Separate topics into clear sections; reformatted text only.",
    },
    "shuffled": {
        "description": "Reconstruct text so layout is logical and significantly different, creating new categories for each idea.",
    },
    "match": {
        "description": "Rewrite to match the provided style; modified text only.",
    },
    "blend": {
        "description": (
            "Combine source and destination texts coherently, using the destination’s structure while reordering and renaming as needed; "
            "return only the final integrated text, treating additional_source as the destination."
        ),
    },
    "join": {
        "description": "Merge content into one coherent part, removing redundancy.",
    },
    "context": {
        "description": "Add LLM-ready context only; do not rewrite the main text.",
        "completeness": "gist",
        "method": "contextualise",
        "style": "plain",
        "scope": "focus",
    },
    # Mathematical and abstract lenses (description-only profiles).
    "math": {
        "description": "Consider mathematical fields that apply to this and specify which are used.",
    },
    "orthogonal": {
        "description": "Identify what is orthogonal in this situation.",
    },
    "bud": {
        "description": "Apply addition/subtraction-like reasoning non-numerically.",
    },
    "boom": {
        "description": "Apply limit/continuity-like reasoning non-numerically.",
    },
    "meld": {
        "description": "Apply set theory reasoning non-numerically.",
    },
    "order": {
        "description": "Apply order or lattice theory reasoning non-numerically.",
    },
    "logic": {
        "description": "Apply propositional or predicate logic reasoning non-numerically.",
    },
    "probability": {
        "description": "Apply probability or statistics reasoning non-numerically.",
    },
    "recurrence": {
        "description": "Calculate the recurrence relation of this idea and explain its consequences in plain language.",
    },
    "map": {
        "description": (
            "Use data mapping and transformation concepts to describe this: identify source and target schemas, "
            "specify transformation rules, and describe information flow, including loss, duplication, or enrichment."
        ),
    },
    "mod": {
        "description": "Modulo the first idea by the second idea non-numerically.",
    },
    "dimension": {
        "description": "Expand dimensions of this geometrically and describe each axis.",
    },
    "rotation": {
        "description": "Compute the 90-degree rotation metaphorically.",
    },
    "reflection": {
        "description": "Compute the reflection metaphorically.",
    },
    "invert": {
        "description": "Invert the concept to reveal negative space.",
    },
    "graph": {
        "description": (
            "Apply graph or tree theory reasoning non-numerically: identify nodes and edges, describe direction, weight, and centrality, "
            "and explain how structure influences flow or dependency."
        ),
    },
    "grove": {
        "description": "Apply integral/derivative concepts non-numerically.",
    },
    "dub": {
        "description": "Apply power/root concepts non-numerically.",
    },
    "drum": {
        "description": "Apply multiplication/division concepts non-numerically.",
    },
    "document": {
        "description": "List document or writing formats (e.g., ADRs, experiment logs, RFCs, briefs), explain why each fits, and what perspective it reveals.",
    },
    "com b": {
        "description": (
            "Analyze the subject using the COM-B model (Capability, Opportunity, Motivation, Behavior), "
            "identify key enablers and barriers across Capability, Opportunity, and Motivation, map them to Behavior Change Wheel "
            "intervention functions and behavior change techniques, and outline a minimal, testable implementation and evaluation plan."
        ),
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    # Strategy, mapping, and dependency prompts (description-only profiles).
    "wardley": {
        "description": (
            "Generate a Wardley Map by identifying users, needs, and components, then output it as a Markdown table where rows are visibility "
            "levels and columns are evolution stages, plus a concise summary of dependencies and key strategic insights."
        ),
        "completeness": "full",
        "method": "steps",
        "style": "table",
        "scope": "focus",
    },
    "dependency": {
        "description": "List dependencies and what they depend on.",
        "scope": "relations",
    },
    "cochange": {
        "description": "For multiple subjects, show how each directly cochanges with the others.",
        "scope": "relations",
    },
    "interact": {
        "description": "Explain how these elements interact.",
        "scope": "relations",
    },
    "dependent": {
        "description": "Explain how these elements are dependent on each other.",
        "scope": "relations",
    },
    "independent": {
        "description": "Explain how these elements are independent.",
        "scope": "relations",
    },
    "parallel": {
        "description": "Describe problems that could arise if these two items were parallelized.",
        "scope": "relations",
    },
    "team": {
        "description": "Describe the team structure, focusing on people and their roles.",
    },
    "unknown": {
        "description": "Imagine critical unknown unknowns in this situation and how they might impact the outcome.",
    },
    "jim": {
        "description": (
            "Analyze the subject for connascence (Strength, Degree, Locality), identify its type, compute Severity = Strength × Degree ÷ Locality, "
            "and propose remedies to reduce harmful connascence."
        ),
    },
    "domain": {
        "description": (
            "Perform a connascence-driven discovery of business domains: group elements by coupling where multiple forms of connascence converge, "
            "describe obligations and change scenarios, and suggest boundary-strengthening remedies."
        ),
    },
    "tune": {
        "description": "Evaluate this design through the Concordance Frame: visibility, scope, and volatility of dependencies that must stay in tune.",
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "melody": {
        "description": (
            "Analyze the system for clusters that share coordination patterns in visibility, scope, and volatility, infer the shared intent or 'tune', "
            "and recommend ways to clarify or strengthen domains by reducing coordination cost."
        ),
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "constraints": {
        "description": "Identify the key constraint in this system, describe behaviours it promotes and discourages, and discuss how to balance it for long-term health.",
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "effects": {
        "description": "Describe the second- and third-order effects of this situation or change.",
        "completeness": "full",
        "method": "steps",
        "style": "plain",
        "scope": "dynamics",
    },
    # Fix-style prompts tend to want solid, local, code-level edits.
    "fix": {
        "description": "Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text.",
        "completeness": "full",
        "scope": "narrow",
    },
    # TODO and planning prompts are usually concise, stepwise, and bullet-oriented.
    "todo": {
        "description": "Format this as a todo list.",
        "completeness": "gist",
        "method": "steps",
        "style": "checklist",
        "scope": "actions",
    },
    "bridge": {
        "description": "Guide me from the current state to the desired situation described in the additional source.",
        "completeness": "path",
        "method": "steps",
        "scope": "focus",
    },
    # Document-shaped and summary-style outputs.
}

_AXES = ("completeness", "scope", "method", "style")


def get_static_prompt_profile(name: str) -> StaticPromptProfile | None:
    """Return the StaticPromptProfile for a given key, if present.

    This helper provides a single place to look up profile metadata so that
    callers (GUI, settings, docs) do not need to reach into STATIC_PROMPT_CONFIG
    directly.
    """
    return STATIC_PROMPT_CONFIG.get(name)


def get_static_prompt_axes(name: str) -> dict[str, object]:
    """Return the axis values defined for a static prompt profile.

    The result maps axis name -> configured value for the axes present in the
    profile (a subset of: completeness, scope, method, style). Unknown prompts
    return an empty dict.

    - `completeness` remains a single short token.
    - `scope`, `method`, and `style` may be configured as a single token or
      as a small list of tokens; callers that care about set semantics should
      normalise these values (for example, via helpers in the axis-mapping
      domain).
    """
    profile = STATIC_PROMPT_CONFIG.get(name)
    if profile is None:
        return {}
    axes: dict[str, object] = {}
    for axis in _AXES:
        value = profile.get(axis)
        if not value:
            continue
        # Completeness remains scalar; other axes may be a single token or a list.
        if axis == "completeness":
            axes[axis] = str(value)
        else:
            if isinstance(value, list):
                tokens = [str(v).strip() for v in value if str(v).strip()]
            else:
                tokens = [str(value).strip()]
            if tokens:
                axes[axis] = tokens
    return axes
