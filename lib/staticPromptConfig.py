from __future__ import annotations

from typing import NotRequired, TypedDict

# Central configuration for static prompts:
# - Each key is a canonical static prompt value (as used in GPT/lists/staticPrompt.talon-list).
# - "description" provides the human-readable Task line and help text.
# - Optional completeness/scope/method/style fields define per-prompt axis profiles.


class StaticPromptProfile(TypedDict):
    description: str
    completeness: NotRequired[str]
    scope: NotRequired[str]
    method: NotRequired[str]
    style: NotRequired[str]


STATIC_PROMPT_CONFIG: dict[str, StaticPromptProfile] = {
    "announce": {
        "description": "Announce this to the audience.",
    },
    "emoji": {
        "description": "Return only emoji.",
    },
    "format": {
        "description": "Add appropriate formatting leveraging commands available in the context (slack, markdown, etc) to the text.",
    },
    "LLM": {
        "description": "Return one or more prompts for an LLM, each fitting on a single line.",
    },
    # Analysis, structure, and perspective prompts (description-only profiles).
    "describe": {
        "description": "Just describe this objectively.",
    },
    "structure": {
        "description": "Describe the structure of the whole input.",
    },
    "flow": {
        "description": "Explain the flow.",
    },
    "undefined": {
        "description": "List undefined terms only.",
    },
    "relation": {
        "description": "Invert this so it focuses on the relationships between things and describe those relationships.",
    },
    "type": {
        "description": "Represent this as a type or taxonomy.",
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
    "compare": {
        "description": (
            "Given two items (with the first provided as additional_source), carefully compare them: "
            "list all differences and similarities, highlighting subtle distinctions and commonalities."
        ),
    },
    "clusters": {
        "description": "Create a table of subtle differences among similar ideas, omitting singletons and keeping width ≤ 100 characters.",
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
    "system": {
        "description": "Evaluate the subject from a systems theory perspective: boundaries, components, stakeholders, flows, feedback, emergence, and leverage points.",
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
        "style": "bullets",
        "scope": "focus",
    },
    "experiment": {
        "description": "Given a problem, suggest one or more experiments that could help solve it.",
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "science": {
        "description": "Give me testable, relevant, and specific hypotheses.",
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "debug": {
        "description": "Analyze the full transcript using the scientific method of debugging—summarize stable facts, list unresolved questions, propose hypotheses, and design a minimal experiment to confirm or refute them.",
        "completeness": "full",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    "wasinawa": {
        "description": "Perform a What–So What–Now What reflection with three clear sections.",
        "completeness": "full",
        "method": "steps",
        "style": "plain",
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
        "style": "bullets",
        "scope": "focus",
    },
    "relevant": {
        "description": "Identify what is relevant here.",
        "completeness": "gist",
        "style": "bullets",
        "scope": "focus",
    },
    "misunderstood": {
        "description": "Identify what is misunderstood in this situation.",
        "completeness": "gist",
        "style": "bullets",
        "scope": "focus",
    },
    "risky": {
        "description": "Highlight what is risky and why.",
        "completeness": "gist",
        "style": "bullets",
        "scope": "focus",
    },
    # Transformation and reformatting prompts (description-only profiles).
    "group": {
        "description": "Group into labeled categories; results only.",
    },
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
    "sort": {
        "description": "Sort items in order of importance to the audience.",
    },
    "context": {
        "description": "Add LLM-ready context only; do not rewrite the main text.",
    },
    "code": {
        "description": "Write code for this.",
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
    },
    "cochange": {
        "description": "For multiple subjects, show how each directly cochanges with the others.",
    },
    "interact": {
        "description": "Explain how these elements interact.",
    },
    "dependent": {
        "description": "Explain how these elements are dependent on each other.",
    },
    "independent": {
        "description": "Explain how these elements are independent.",
    },
    "parallel": {
        "description": "Describe problems that could arise if these two items were parallelized.",
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
        "scope": "focus",
    },
    # Variations and playful prompts (description-only profiles).
    "silly": {
        "description": "Say something silly about this.",
    },
    "style": {
        "description": "Describe style instructions with one example.",
        "completeness": "gist",
        "style": "plain",
    },
    "recipe": {
        "description": "Represent this as a recipe using a custom language and include a key for understanding it.",
        "completeness": "full",
        "style": "code",
    },
    "problem": {
        "description": (
            "Help with abstraction laddering: place the given problem in the middle, list three reasons why it is a problem above, "
            "and three problems it causes below, ordered by importance to the audience."
        ),
        "completeness": "full",
        "method": "steps",
        "style": "plain",
        "scope": "focus",
    },
    "lens": {
        "description": (
            "Create an abstract visualization that avoids diagrams or maps: express the big picture as a loose metaphorical form highlighting contrasts "
            "and points of interest, with a short legend and optional SVG or code instructions."
        ),
        "completeness": "gist",
        "method": "rigor",
        "style": "plain",
        "scope": "focus",
    },
    # Fix-style prompts tend to want solid, local, code-level edits.
    "fix": {
        "description": "Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text.",
        "completeness": "full",
        "scope": "narrow",
    },
    # Simple explanations lean toward gist-level completeness with tight scope.
    "simple": {
        "description": "Rewrite this in a simpler way while preserving the core meaning.",
        "completeness": "gist",
        "scope": "narrow",
    },
    # Shortening and clarity prompts bias style and completeness.
    "short": {
        "description": "Shorten this while preserving meaning; return only the modified text.",
        "completeness": "gist",
        "style": "tight",
    },
    "clear": {
        "description": "Remove all jargon and complex language; rewrite this so it is easy to understand.",
        "completeness": "full",
        "style": "plain",
    },
    # TODO and planning prompts are usually concise, stepwise, and bullet-oriented.
    "todo": {
        "description": "Format this as a todo list.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "how to": {
        "description": "Provide a quick plan to solve today’s problem.",
        "completeness": "gist",
        "method": "steps",
        "style": "bullets",
        "scope": "focus",
    },
    "incremental": {
        "description": "Break this down into smaller steps to do just the next tiny increment.",
        "completeness": "gist",
        "method": "steps",
        "scope": "focus",
    },
    "bridge": {
        "description": "Guide me from the current state to the desired situation described in the additional source.",
        "completeness": "full",
        "method": "steps",
        "scope": "focus",
    },
    # Diagrams and other code/format-only prompts tend to be markup/code only.
    "diagram": {
        "description": "Convert plain text to appropriate mermaid diagram syntax, inferring the best diagram type; mermaid diagrams do not allow parentheses.",
        "completeness": "gist",
        "scope": "focus",
        "style": "code",
    },
    "HTML": {
        "description": "Rewrite this as semantic HTML only.",
        "completeness": "full",
        "scope": "bound",
        "style": "code",
    },
    "gherkin": {
        "description": "Reformat this into proper Gherkin using Jira markup; output only the reformatted Gherkin with no surrounding explanation.",
        "completeness": "full",
        "scope": "bound",
        "style": "code",
    },
    "shell": {
        "description": "Write a shell script that implements this.",
        "completeness": "full",
        "scope": "bound",
        "style": "code",
    },
    # Document-shaped and summary-style outputs.
    "commit": {
        "description": "Write a conventional commit message for the staged changes.",
        "completeness": "gist",
        "scope": "bound",
        "style": "plain",
    },
    "ADR": {
        "description": "Write an Architecture Decision Record (ADR) for this situation.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
        "style": "plain",
    },
}
