from __future__ import annotations

import os
from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, Iterable, List, Mapping

# Persona and intent axis docs (token -> description), parallel to AXIS_KEY_TO_VALUE
# but kept separate from the core contract axes.
PERSONA_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "voice": {
        "as programmer": "The response adopts the stance and language of a programmer, explaining and reasoning like an engineer.",
        "as prompt engineer": "The response reflects a prompt-engineer stance, explicitly designing and refining prompts.",
        "as scientist": "The response speaks as a scientist, emphasising evidence, hypotheses, and rigor.",
        "as writer": "The response speaks as a writer, focusing on narrative clarity and flow.",
        "as designer": "The response speaks as a designer, foregrounding usability, interaction, and visual clarity.",
        "as teacher": "The response speaks as a teacher, breaking concepts down and scaffolding understanding.",
        "as facilitator": "The response speaks as a facilitator, guiding process, balancing voices, and maintaining momentum.",
        "as PM": "The response speaks as a product manager, focusing on outcomes, scope, and stakeholders.",
        "as junior engineer": "The response speaks as a junior engineer, showing curiosity, asking clarifying questions, and being candid about uncertainty.",
        "as principal engineer": "The response speaks as a principal engineer, bringing systems thinking, trade-offs, and pragmatic guidance.",
        "as Kent Beck": "The response channels Kent Beck's pragmatic, iterative style with an emphasis on tests and simplicity.",
    },
    "audience": {
        "to managers": "The response addresses managers, highlighting outcomes, risk, and staffing.",
        "to team": "The response addresses the team, keeping the guidance actionable and collaborative.",
        "to stakeholders": "The response addresses stakeholders, focusing on impact, decisions, and clarity.",
        "to product manager": "The response addresses a product manager, connecting user value, scope, and trade-offs.",
        "to designer": "The response addresses a designer, emphasising user experience, flows, and visual clarity.",
        "to analyst": "The response addresses an analyst, providing structure, data framing, and ways to visualise results.",
        "to programmer": "The response addresses a programmer, remaining technical, precise, and implementation-ready.",
        "to LLM": "The response addresses a large language model, remaining explicit, unambiguous, and free of fluff.",
        "to junior engineer": "The response addresses a junior engineer, explaining clearly and offering gentle guidance.",
        "to principal engineer": "The response addresses a principal engineer, remaining concise, architectural, and assumption-light.",
        "to Kent Beck": "The response addresses Kent Beck, staying concrete, test-minded, and iterative.",
        "to CEO": "The response addresses a CEO, surfacing business impact, risk, and crisp asks.",
        "to platform team": "The response addresses a platform team, emphasising reliability, leverage, and paved-path fit.",
        "to stream aligned team": "The response addresses a stream-aligned team, emphasising flow, delivery, and local ownership.",
        "to XP enthusiast": "The response addresses an XP enthusiast, valuing small batches, social programming, and production validation.",
    },
    "tone": {
        "casually": "The response uses a casual, conversational tone.",
        "formally": "The response uses a formal, professional tone.",
        "directly": "The response speaks directly and straightforwardly while remaining respectful.",
        "gently": "The response keeps the tone gentle and supportive.",
        "kindly": "The response uses a kind, warm tone.",
    },
    "intent": {
        "inform": "Provide clear, relevant information the audience needs.",
        "persuade": "Influence the audience toward a view or action.",
        "appreciate": "Express thanks, recognition, or positive regard.",
        "announce": "Share news or updates with the audience.",
        "coach": "Support the audience's growth through guidance and feedback.",
        "teach": "Help the audience understand and learn material.",
    },
}

# Short CLI-facing labels for persona/audience/tone/voice/intent token selection (ADR-0111).
# Keys match the canonical token form used in PERSONA_KEY_TO_VALUE.
PERSONA_KEY_TO_LABEL: Dict[str, Dict[str, str]] = {
    "voice": {
        "as programmer": "Programmer stance",
        "as prompt engineer": "Prompt engineering focus",
        "as scientist": "Scientific, evidence-based",
        "as writer": "Writer's narrative voice",
        "as designer": "Designer's UX perspective",
        "as teacher": "Teaching and scaffolding",
        "as facilitator": "Facilitation and process",
        "as PM": "Product manager focus",
        "as junior engineer": "Junior engineer curiosity",
        "as principal engineer": "Principal engineer systems view",
        "as Kent Beck": "Kent Beck pragmatic style",
    },
    "audience": {
        "to managers": "Outcome-focused for managers",
        "to team": "Actionable for the team",
        "to stakeholders": "Impact-focused for stakeholders",
        "to product manager": "Value and scope for PM",
        "to designer": "UX-focused for designers",
        "to analyst": "Structured for analysts",
        "to programmer": "Technical, implementation-ready",
        "to LLM": "Explicit and unambiguous",
        "to junior engineer": "Clear guidance for juniors",
        "to principal engineer": "Architectural and concise",
        "to Kent Beck": "Test-minded and iterative",
        "to CEO": "Business impact and crisp asks",
        "to platform team": "Reliability and paved path",
        "to stream aligned team": "Flow and local ownership",
        "to XP enthusiast": "Small batches, XP values",
    },
    "tone": {
        "casually": "Casual, conversational",
        "formally": "Formal, professional",
        "directly": "Direct, straightforward",
        "gently": "Gentle, supportive",
        "kindly": "Kind, warm",
    },
    "intent": {
        "inform": "Convey information clearly",
        "persuade": "Influence toward a view",
        "appreciate": "Express thanks or recognition",
        "announce": "Share news or updates",
        "coach": "Guide growth and development",
        "teach": "Help the audience learn",
    },
}


# Selection guidance for persona/intent/tone tokens where the description alone is
# ambiguous or where misuse traps exist (ADR-0112). Displayed in the TUI at token-
# selection time; never injected into the prompt body.
PERSONA_KEY_TO_GUIDANCE: Dict[str, Dict[str, str]] = {
    "presets": {
        "designer_to_pm": "Strong with sim (stability analysis), probe (design reviews). Good for scenarios, flow analysis.",
        "product_manager_to_team": "Strong with probe (quality analysis), check (requirements validation). Good for retrospectives, estimation.",
        "peer_engineer_explanation": "Strong with sim (technical scenarios), show (code structure). Good for walkthroughs, debugging.",
        "scientist_to_analyst": "Strong with check (evidence-based verification), probe (analysis). Good for data-driven decisions.",
    },
    "intent": {
        "appreciate": "Social-purpose intent: use only when the whole response is an "
        "expression of thanks or recognition. Does not modify analytical tasks "
        "(plan, probe, check, diff) — pair with tone: kindly instead.",
        "announce": "Social-purpose intent: use only when delivering a specific "
        "announcement. Not a modifier for analytical or planning tasks.",
    },
    "tone": {
        "formally": "May conflict with conversational-register channels. slack, sync, "
        "and remote assume informal or spoken language — formal elevated prose "
        "will feel bureaucratic. Use directly or no tone for those channels.",
    },
}


# Discoverability hints for persona presets and axis tokens (ADR-0133).
# When to reach for a persona at all — displayed in help llm "When to use" column.
PERSONA_KEY_TO_USE_WHEN: Dict[str, Dict[str, str]] = {
    "presets": {
        "peer_engineer_explanation": "Technical explanation to a fellow engineer: use when the "
        "audience is a programmer or peer engineer who wants engineer-to-engineer framing. "
        "Heuristic: 'explain this to a developer', 'peer review context', 'engineer to engineer', "
        "'technical walkthrough for my team' → peer_engineer_explanation.",
        "teach_junior_dev": "Mentoring or onboarding a junior developer: use when the audience "
        "needs patient, scaffolded explanation with encouragement. Heuristic: 'explain for a "
        "junior', 'onboarding doc', 'new developer', 'junior team member', 'kind clear explanation "
        "for someone new' → teach_junior_dev.",
        "stakeholder_facilitator": "Driving alignment with mixed stakeholders: use when the "
        "response needs to help a facilitator guide a group toward a decision. Heuristic: "
        "'stakeholder meeting', 'cross-functional group', 'alignment session', 'facilitating a "
        "decision', 'stakeholder presentation' → stakeholder_facilitator.",
        "designer_to_pm": "Design decisions communicated to a product manager: use when a "
        "designer needs to explain trade-offs and UX rationale to a PM audience. Heuristic: "
        "'explain design to PM', 'design rationale for product', 'UX decision for a product "
        "manager' → designer_to_pm.",
        "product_manager_to_team": "Product direction communicated to the team: use when a PM "
        "needs to frame product goals or retrospective insights for the engineering or design "
        "team. Heuristic: 'PM to team update', 'product direction for engineers', 'team "
        "retrospective framing' → product_manager_to_team.",
        "executive_brief": "Concise high-stakes summary for a CEO or executive: use when the "
        "response must surface business impact, risk, and crisp asks in direct language. "
        "Heuristic: 'executive summary', 'board presentation', 'brief for the CEO', 'business "
        "impact', 'crisp ask for leadership' → executive_brief.",
        "scientist_to_analyst": "Evidence-based analysis presented formally to an analyst: use "
        "when the response needs rigorous structure, data framing, and formal tone. Heuristic: "
        "'data analysis for an analyst', 'evidence-based findings', 'formal analytical report', "
        "'scientific framing' → scientist_to_analyst.",
        "fun_mode": "Casual, playful tone across the board: use when the subject calls for "
        "levity and the user explicitly wants a casual, entertaining register. Heuristic: "
        "'keep it light', 'be funny', 'playful tone', 'casual', 'have fun with it' → fun_mode.",
    },
    "audience": {
        "to managers": "Address managers focused on outcomes and risk: use when the primary "
        "audience is a manager who cares about staffing, risk, and results rather than technical "
        "implementation. Heuristic: 'for my manager', 'management update', 'manager audience', "
        "'outcome-focused for leadership' → audience=to-managers.",
        "to product manager": "Address a product manager with scope and user value framing: use "
        "when the primary audience is a PM connecting user needs to scope decisions. Heuristic: "
        "'for the PM', 'product manager audience', 'scope and user value', 'product decision' "
        "→ audience=to-product-manager.",
        "to CEO": "Address a CEO with business impact and crisp asks: use when the primary "
        "audience is a CEO or C-suite executive who needs crisp business framing. Heuristic: "
        "'for the CEO', 'executive audience', 'business impact', 'C-suite framing' "
        "→ audience=to-CEO.",
        "to LLM": "Address another language model: use when the response will be consumed by "
        "another LLM — make output explicit, unambiguous, and free of prose fluff. Heuristic: "
        "'pass this to a model', 'LLM pipeline', 'downstream model', 'machine-readable "
        "framing' → audience=to-LLM.",
        "to junior engineer": "Address a junior engineer with clear, encouraging guidance: use "
        "when the audience needs thorough explanation and supportive tone. Heuristic: 'for a "
        "junior dev', 'explain to someone new to this', 'beginner-friendly', 'onboarding' "
        "→ audience=to-junior-engineer.",
        "to stakeholders": "Address a broad stakeholder group focused on impact and decisions: "
        "use when the audience includes mixed roles and needs clarity on what matters and why. "
        "Heuristic: 'for stakeholders', 'mixed audience', 'cross-functional group', 'impact "
        "and decision clarity' → audience=to-stakeholders.",
        "to team": "Address your own team with actionable, collaborative framing: use when the "
        "audience is your immediate team and you want direct, implementation-ready communication. "
        "Heuristic: 'for the team', 'team update', 'share with my team', 'team-facing' "
        "→ audience=to-team.",
        "to designer": "Address a designer with UX and visual clarity framing: use when the "
        "audience cares about user flows, interaction patterns, and design rationale. Heuristic: "
        "'for the designer', 'design audience', 'UX framing', 'explain to a designer' "
        "→ audience=to-designer.",
        "to analyst": "Address an analyst with structured, data-framed output: use when the "
        "audience needs evidence, metrics, and structured results for further analysis. "
        "Heuristic: 'for an analyst', 'data-framed', 'analyst audience', 'structured findings' "
        "→ audience=to-analyst.",
        "to programmer": "Address a programmer with technical, implementation-ready output: use "
        "when the audience is a developer who expects precision and wants to act on the output "
        "directly. Heuristic: 'for a developer', 'technical audience', 'implementation-ready', "
        "'programmer framing' → audience=to-programmer.",
        "to principal engineer": "Address a principal engineer with concise, architectural "
        "framing: use when the audience is a senior technical leader who wants trade-offs, "
        "systems thinking, and minimal hand-holding. Heuristic: 'for a principal engineer', "
        "'senior technical audience', 'architectural framing', 'assume deep expertise' "
        "→ audience=to-principal-engineer.",
        "to Kent Beck": "Address Kent Beck's values — concrete, test-minded, iterative: use when "
        "the audience values small batches, working code, and simplicity over elaboration. "
        "Heuristic: 'XP framing', 'test-driven', 'Kent Beck style', 'iterative design' "
        "→ audience=to-Kent-Beck.",
        "to platform team": "Address a platform team focused on reliability and paved paths: use "
        "when the audience cares about leverage, reliability contracts, and making the right "
        "thing easy. Heuristic: 'for the platform team', 'reliability framing', 'paved path', "
        "'infrastructure audience' → audience=to-platform-team.",
        "to stream aligned team": "Address a stream-aligned team focused on flow and local "
        "ownership: use when the audience cares about delivery speed, reducing dependencies, "
        "and owning their domain end to end. Heuristic: 'stream-aligned team', 'delivery flow', "
        "'local ownership', 'feature team framing' → audience=to-stream-aligned-team.",
        "to XP enthusiast": "Address an XP enthusiast who values social programming and "
        "production validation: use when the audience practices small batches, pair/mob "
        "programming, and continuous delivery. Heuristic: 'XP framing', 'pair programming "
        "audience', 'continuous delivery context', 'extreme programming values' "
        "→ audience=to-XP-enthusiast.",
    },
    "voice": {
        # voice= = speaker identity (output FROM this role; contrast: audience= targets a reader)
        "as programmer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a programmer's technical stance: use when you want the response "
        "to reason and explain like an engineer — precise, implementation-minded, direct. "
        "Heuristic: 'from a developer perspective', 'as a programmer would', 'engineer stance', "
        "'technical voice', 'programmer framing' → voice=as-programmer.",
        "as prompt engineer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a prompt-engineering stance: use when the response involves "
        "designing, critiquing, or refining prompts explicitly. Heuristic: 'from a prompt "
        "engineer angle', 'as a prompt engineer would', 'prompt design perspective', "
        "'meta-prompt framing' → voice=as-prompt-engineer.",
        "as scientist": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a scientific, evidence-first stance: use when you want the "
        "response to foreground hypotheses, evidence, and rigor. Heuristic: 'from a scientific "
        "perspective', 'as a scientist would', 'scientific framing', 'evidence-based stance', "
        "'hypothesis-driven', 'researcher voice' → voice=as-scientist.",
        "as writer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a writer's stance focused on narrative clarity: use when the "
        "response involves prose, storytelling, or communication craftsmanship. Heuristic: "
        "'from a writer's perspective', 'as a writer would', 'writing perspective', "
        "'narrative clarity', 'writer's eye', 'editorial stance' → voice=as-writer.",
        "as designer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a designer's stance focused on usability and interaction: use when "
        "the response involves UX decisions, flows, or visual clarity. Heuristic: 'from a "
        "designer's perspective', 'as a designer would', 'give feedback as a designer', "
        "'designer perspective', 'UX lens', 'design thinking', 'interaction design voice' "
        "→ voice=as-designer.",
        "as teacher": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a teacher's stance that scaffolds understanding: use when the "
        "response needs to break concepts down gradually for a learner. Heuristic: 'teach me', "
        "'as a teacher would explain', 'from a teaching perspective', 'teaching voice', "
        "'explain like a teacher', 'pedagogical framing', 'scaffolded explanation' "
        "→ voice=as-teacher.",
        "as facilitator": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a facilitator's stance that guides process: use when the "
        "response needs to balance voices, structure participation, and maintain momentum. "
        "Heuristic: 'run this as a facilitator', 'facilitate this', 'as a facilitator would', "
        "'facilitation perspective', 'group process framing', 'facilitator voice', "
        "'session guidance' → voice=as-facilitator.",
        "as PM": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a product manager's stance focused on outcomes and scope: use when the "
        "response needs to foreground user value, trade-offs, and stakeholder alignment. "
        "Heuristic: 'write as a PM', 'from a product manager's perspective', 'user story as "
        "PM would write', 'PM framing', 'product perspective', 'outcome-focused voice', "
        "'product manager stance' → voice=as-PM.",
        "as junior engineer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a junior engineer's curious, candid stance: use when you "
        "want the response to surface questions, acknowledge uncertainty, and show its work. "
        "Heuristic: 'from a junior engineer's perspective', 'junior engineer voice', 'curious "
        "framing', 'show uncertainty', 'beginner perspective' → voice=as-junior-engineer.",
        "as principal engineer": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt a principal engineer's systems-thinking stance: use when "
        "the response needs architectural breadth, trade-off reasoning, and pragmatic guidance. "
        "Heuristic: 'from a senior engineer's perspective', 'as a principal engineer would', "
        "'review as a senior engineer', 'principal engineer perspective', 'architectural voice', "
        "'senior technical framing', 'systems thinking stance' → voice=as-principal-engineer.",
        "as Kent Beck": "Voice= = speaker identity (output FROM this role; contrast: audience= targets a reader). "
        "Adopt Kent Beck's pragmatic, test-first, iterative stance: use when you "
        "want the response to favor simplicity, working code, and small steps over elaboration. "
        "Heuristic: 'Kent Beck style', 'from Kent Beck's perspective', 'XP voice', "
        "'test-driven framing', 'simplicity-first perspective' → voice=as-Kent-Beck.",
    },
    "tone": {
        # tone= = emotional register (HOW content is delivered; use alongside voice=/audience= when task specifies communication style)
        "casually": "Tone= = emotional register (HOW content is delivered; distinct from voice= which sets speaker identity). "
        "Casual, conversational register: use when formality would feel stiff or "
        "the subject benefits from a relaxed tone. Heuristic: 'keep it casual', 'conversational "
        "tone', 'informal', 'quick Slack message', 'relaxed register', 'chat style' → tone=casually.",
        "formally": "Tone= = emotional register (HOW content is delivered; distinct from voice= which sets speaker identity). "
        "Formal, professional register: use when the output will be shared with "
        "leadership, external parties, compliance contexts, or a professional document. "
        "Heuristic: 'formal tone', 'professional register', 'official language', 'compliance "
        "report', 'incident report', 'for leadership', 'no colloquialisms' → tone=formally.",
        "directly": "Tone= = emotional register (HOW content is delivered; distinct from voice= which sets speaker identity). "
        "Direct, no-hedging register: use when the user wants a straight answer "
        "without softening or qualifications. Heuristic: 'be direct', 'no hedging', 'straight "
        "answer', 'don't soften it', 'to the point', 'blunt' → tone=directly.",
        "gently": "Tone= = emotional register (HOW content is delivered; distinct from voice= which sets speaker identity). "
        "Gentle, supportive register: use when the subject involves sensitive feedback, "
        "interpersonal difficulty, or someone who needs encouragement. For interpersonal feedback "
        "tasks pair with analysis method (not adversarial). Heuristic: 'be gentle', "
        "'sensitive topic', 'sensitive feedback on a colleague', 'supportive tone', 'soft "
        "delivery', 'with care', 'interpersonal feedback' → tone=gently.",
        "kindly": "Tone= = emotional register (HOW content is delivered; distinct from voice= which sets speaker identity). "
        "Kind, warm register: use when the response should convey warmth alongside "
        "substance — often for coaching, junior audiences, or emotionally charged topics. "
        "Heuristic: 'be kind', 'warm tone', 'encouraging register', 'with warmth', "
        "'kind feedback' → tone=kindly.",
    },
    "intent": {
        "inform": "Communicate to transfer knowledge or update understanding: use when the goal "
        "is to give the audience the information they need. Heuristic: 'inform the audience', "
        "'share findings', 'update them on', 'let them know', 'communicate the status' "
        "→ intent=inform.",
        "persuade": "Communicate to influence belief or action: use when the goal is to move "
        "the audience toward a view or decision. Heuristic: 'convince them', 'make the case', "
        "'persuade the team', 'get buy-in', 'advocate for' → intent=persuade.",
        "appreciate": "Communicate gratitude or recognition: use when the goal is to acknowledge "
        "contribution, celebrate work, or express thanks. Heuristic: 'thank them', 'recognize "
        "the work', 'show appreciation', 'express gratitude' → intent=appreciate.",
        "announce": "Communicate news or a change: use when the goal is to share a decision, "
        "launch, or update with an audience. Heuristic: 'announce the launch', 'share the "
        "news', 'communicate the change', 'release announcement' → intent=announce.",
        "coach": "Communicate to develop the audience: use when the goal is growth, capability "
        "building, or guiding someone through a challenge. Heuristic: 'coach them', 'help "
        "them grow', 'give developmental feedback', 'guide them through' → intent=coach.",
        "teach": "Communicate to build understanding: use when the goal is learning and the "
        "audience needs to internalize concepts, not just receive information. Heuristic: "
        "'teach this concept', 'help them understand', 'learning goal', 'make it stick' "
        "→ intent=teach.",
    },
}


# Distilled routing concept phrases for persona tokens (ADR-0146).
# Parallel to AXIS_KEY_TO_ROUTING_CONCEPT; SSOT for persona routing labels in TUI2/SPA.
PERSONA_KEY_TO_ROUTING_CONCEPT: Dict[str, Dict[str, str]] = {
    "voice": {
        "as Kent Beck":          "Kent Beck voice",
        "as PM":                 "PM voice",
        "as designer":           "Designer voice",
        "as facilitator":        "Facilitator voice",
        "as junior engineer":    "Junior engineer voice",
        "as principal engineer": "Principal engineer voice",
        "as programmer":         "Programmer voice",
        "as prompt engineer":    "Prompt engineer voice",
        "as scientist":          "Scientist voice",
        "as teacher":            "Teacher voice",
        "as writer":             "Writer voice",
    },
    "audience": {
        "to CEO":                 "CEO audience",
        "to Kent Beck":           "Kent Beck audience",
        "to LLM":                 "LLM context",
        "to XP enthusiast":       "XP enthusiast audience",
        "to analyst":             "Analyst audience",
        "to designer":            "Designer audience",
        "to junior engineer":     "Junior engineer audience",
        "to managers":            "Manager audience",
        "to platform team":       "Platform team audience",
        "to principal engineer":  "Principal engineer audience",
        "to product manager":     "Product manager audience",
        "to programmer":          "Programmer audience",
        "to stakeholders":        "Stakeholder audience",
        "to stream aligned team": "Stream-aligned team",
        "to team":                "Team audience",
    },
    "tone": {
        "casually": "Casual tone",
        "directly": "Direct tone",
        "formally": "Formal tone",
        "gently":   "Gentle tone",
        "kindly":   "Kind tone",
    },
    "intent": {
        "announce":   "Share news",
        "appreciate": "Express thanks",
        "coach":      "Develop capability",
        "inform":     "Transfer knowledge",
        "persuade":   "Influence belief/action",
        "teach":      "Build understanding",
    },
    "presets": {
        "designer_to_pm":           "Designer to PM",
        "executive_brief":          "Executive brief",
        "fun_mode":                 "Fun mode",
        "peer_engineer_explanation": "Peer explanation",
        "product_manager_to_team":  "PM to team",
        "scientist_to_analyst":     "Scientist to analyst",
        "stakeholder_facilitator":  "Stakeholder facilitation",
        "teach_junior_dev":         "Teach junior dev",
    },
}

# Kanji icons for persona axis tokens (ADR-0143)
PERSONA_KEY_TO_KANJI: Dict[str, Dict[str, str]] = {
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
    "audience": {
        "to managers": "監",
        "to team": "団",
        "to stakeholders": "益",
        "to product manager": "管",
        "to designer": "設",
        "to analyst": "析",
        "to programmer": "者",
        "to LLM": "言",
        "to junior engineer": "新",
        "to principal engineer": "長",
        "to Kent Beck": "貝",
        "to CEO": "首",
        "to platform team": "基",
        "to stream aligned team": "流",
        "to XP enthusiast": "好",
    },
    "tone": {
        "casually": "軽",
        "directly": "直",
        "formally": "式",
        "gently": "優",
        "kindly": "慈",
    },
    "intent": {
        "inform": "知",
        "persuade": "説",
        "appreciate": "謝",
        "announce": "告",
        "coach": "導",
        "teach": "教",
    },
}


def persona_key_to_kanji_map(axis: str) -> dict[str, str]:
    """Return the key->kanji map for a persona/intent axis (ADR-0143)."""
    return PERSONA_KEY_TO_KANJI.get(axis, {})


def persona_key_to_routing_concept_map(axis: str) -> dict[str, str]:
    """Return the key->routing_concept map for a persona/intent axis (ADR-0146)."""
    return PERSONA_KEY_TO_ROUTING_CONCEPT.get(axis, {})


def persona_key_to_use_when_map(axis: str) -> dict[str, str]:
    """Return the key->use_when map for a persona/intent axis (ADR-0133)."""
    return PERSONA_KEY_TO_USE_WHEN.get(axis, {})


def persona_key_to_guidance_map(axis: str) -> dict[str, str]:
    """Return the key->guidance map for a persona/intent axis (ADR-0112)."""
    return PERSONA_KEY_TO_GUIDANCE.get(axis, {})


def persona_key_to_label_map(axis: str) -> dict[str, str]:
    """Return the key->label map for a persona/intent axis (ADR-0111)."""
    return PERSONA_KEY_TO_LABEL.get(axis, {})


INTENT_CANONICAL_TOKENS: set[str] = set(PERSONA_KEY_TO_VALUE["intent"].keys())

ALLOWED_PERSONA_AXES = frozenset({"voice", "audience", "tone"})


def persona_key_to_value_map(axis: str) -> dict[str, str]:
    """Return the key->description map for a persona/intent axis."""
    return PERSONA_KEY_TO_VALUE.get(axis, {})


def persona_hydrate_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Hydrate persona/intent tokens to descriptions (or pass through)."""
    if not tokens:
        return []
    mapping = persona_key_to_value_map(axis)
    return [mapping.get(token, token) for token in tokens if token]


def persona_docs_map(axis: str) -> dict[str, str]:
    """Return a key->description map for UI/docs surfaces."""
    return persona_key_to_value_map(axis)


def persona_axis_tokens(axis: str) -> set[str]:
    """Return canonical persona/intent tokens for the requested axis."""

    key = str(axis or "").strip().lower()
    if not key:
        return set()
    mapping = PERSONA_KEY_TO_VALUE.get(key)
    if not mapping:
        return set()
    return {token for token in mapping.keys() if token}


def canonical_persona_token(axis: str, raw: str) -> str:
    """Return the canonical persona/intent token for ``raw`` or ``""`` if unknown."""

    if not raw:
        return ""
    key = str(axis or "").strip().lower()
    if not key:
        return ""
    token = str(raw).strip()
    if not token:
        return ""
    if key == "intent":
        token = normalize_intent_token(token)
    tokens = persona_axis_tokens(key)
    if not tokens:
        return ""
    lowered = {t.lower(): t for t in tokens}
    return lowered.get(token.lower(), "")


def hydrate_intent_token(
    value: str,
    *,
    default: str | None = None,
    orchestrator: object | None = None,
    catalog_snapshot: object | None = None,
    maps: PersonaIntentMaps | None = None,
) -> str:
    """Return the human-readable label for an intent token.

    Falls back to the canonical token when no display label is available.
    """

    token = normalize_intent_token(value)
    if not token:
        return default or ""

    def _lookup_display(source: object | None) -> str:
        if source is None:
            return ""
        try:
            mapping = getattr(source, "intent_display_map", None)
        except Exception:
            mapping = None
        if not mapping:
            return ""
        try:
            mapping_dict = dict(mapping)
        except Exception:
            return ""
        candidate = mapping_dict.get(token) or mapping_dict.get(token.lower())
        return (candidate or "").strip()

    if orchestrator is not None:
        display = _lookup_display(orchestrator)
        if display:
            return display

    if catalog_snapshot is not None:
        display = _lookup_display(catalog_snapshot)
        if display:
            return display

    if maps is None:
        try:
            maps = persona_intent_maps()
        except Exception:
            maps = None

    if maps is not None:
        display = _lookup_display(maps)
        if display:
            return display

    if default is not None:
        return default

    return token


def normalize_intent_token(value: str) -> str:
    """Normalize spoken or canonical intent tokens to the canonical single-word form."""
    token = str(value or "").strip()
    if not token:
        return ""
    token_l = token.lower()
    for key in INTENT_CANONICAL_TOKENS:
        if token_l == key.lower():
            return key
    return token


def intent_bucket_spoken_tokens() -> dict[str, list[str]]:
    """Return intent buckets with display labels covering all canonical intents."""

    label_lookup: Dict[str, str] = {}
    for preset in INTENT_PRESETS:
        canonical = (preset.intent or "").strip()
        label_lookup.setdefault(canonical, (preset.label or canonical).strip())

    spoken_buckets: dict[str, list[str]] = {}
    for bucket, members in INTENT_BUCKETS.items():
        bucket_spoken: list[str] = []
        for canonical in members:
            label = label_lookup.get(canonical) or canonical
            bucket_spoken.append(label)
        spoken_buckets[bucket] = bucket_spoken
    return spoken_buckets


@dataclass(frozen=True)
class PersonaPreset:
    key: str
    label: str
    spoken: str | None = None
    voice: str | None = None
    audience: str | None = None
    tone: str | None = None


@dataclass(frozen=True)
class IntentPreset:
    key: str
    label: str
    intent: str


PERSONA_PRESETS: tuple[PersonaPreset, ...] = (
    PersonaPreset(
        key="peer_engineer_explanation",
        label="Peer engineer explanation",
        spoken="peer",
        voice="as programmer",
        audience="to programmer",
    ),
    # Removed coach_junior - conflicts with 'coach' intent and overlaps with teach_junior_dev (mentor).
    PersonaPreset(
        key="teach_junior_dev",
        label="Teach junior dev",
        spoken="mentor",
        voice="as teacher",
        audience="to junior engineer",
        tone="kindly",
    ),
    PersonaPreset(
        key="stakeholder_facilitator",
        label="Stakeholder facilitator",
        spoken="stake",
        voice="as facilitator",
        audience="to stakeholders",
        tone="directly",
    ),
    PersonaPreset(
        key="designer_to_pm",
        label="Designer to PM",
        spoken="design",
        voice="as designer",
        audience="to product manager",
        tone="directly",
    ),
    PersonaPreset(
        key="product_manager_to_team",
        label="Product manager to team",
        spoken="pm",
        voice="as PM",
        audience="to team",
        tone="kindly",
    ),
    PersonaPreset(
        key="executive_brief",
        label="Executive brief",
        spoken="exec",
        voice="as programmer",
        audience="to CEO",
        tone="directly",
    ),
    PersonaPreset(
        key="scientist_to_analyst",
        label="Scientist to analyst",
        spoken="science",
        voice="as scientist",
        audience="to analyst",
        tone="formally",
    ),
    PersonaPreset(
        key="fun_mode",
        label="Fun mode",
        spoken="fun",
        tone="casually",
    ),
)


# Document implicit intents in each preset (informational only).
# Presets bundle voice/audience/tone with an implicit "why" (intent).
# Per ADR 0086: Users should pick one approach (preset OR custom voice/audience/tone + intent).
PERSONA_PRESET_IMPLICIT_INTENTS: Dict[str, str] = {
    "peer_engineer_explanation": "inform",
    "teach_junior_dev": "teach",
    "scientist_to_analyst": "inform",
    "stakeholder_facilitator": "inform",  # facilitators help groups converge on decisions
    "designer_to_pm": "inform",
    "product_manager_to_team": "inform",  # PMs help teams inform on product direction
    "executive_brief": "inform",
    "fun_mode": "inform",  # Changed from entertain - fun_mode provides tone (casually) without requiring entertain intent
}


# Usage guidance for intent + preset interaction (no validation, just documentation).
# Per ADR 0086: Document bundled vs unbundled approach.
INTENT_PRESET_GUIDANCE = """
Intent and Persona Presets: Pick One Approach

Option 1: Use a preset (includes implicit intent)
  - Example: scientist_to_analyst
  - Bundles: voice(scientist) + audience(analyst) + tone(formal) + intent(inform)

Option 2: Build custom with explicit intent
  - Example: as programmer + to team + coach
  - Unbundled: choose each piece separately

Mixing preset + explicit intent is usually redundant or confusing:
  - Redundant: teach_junior_dev + teach (preset already teaches)
  - Conflicting: scientist_to_analyst + coach (inform vs teach)

When in doubt: Use preset alone OR custom voice/audience/tone + intent.
"""


INTENT_PRESETS: tuple[IntentPreset, ...] = (
    IntentPreset(
        key="teach",
        label="Teach / explain",
        intent="teach",
    ),
    IntentPreset(
        key="appreciate",
        label="Appreciate / thank",
        intent="appreciate",
    ),
    IntentPreset(
        key="persuade",
        label="Persuade",
        intent="persuade",
    ),
    IntentPreset(
        key="coach",
        label="Coach",
        intent="coach",
    ),
    IntentPreset(
        key="inform",
        label="Inform",
        intent="inform",
    ),
    IntentPreset(
        key="announce",
        label="Announce",
        intent="announce",
    ),
)


INTENT_BUCKETS: dict[str, tuple[str, ...]] = {
    "task": (
        "inform",
        "announce",
        "teach",
    ),
    "relational": ("appreciate", "persuade", "coach"),
}


def intent_bucket_presets() -> dict[str, list[str]]:
    """Return intent preset keys grouped into task/relational buckets."""

    preset_keys = [preset.key for preset in INTENT_PRESETS if preset.key]
    buckets: dict[str, list[str]] = {}
    for bucket, members in INTENT_BUCKETS.items():
        filtered = [m for m in members if m in preset_keys]
        if filtered:
            buckets[bucket] = filtered
    return buckets


def _persona_spoken_map_from_presets(
    presets: Dict[str, PersonaPreset],
) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for key, preset in presets.items():
        key_l = (key or "").strip().lower()
        if key_l:
            mapping.setdefault(key_l, key)
        spoken = (preset.spoken or "").strip().lower()
        if spoken:
            mapping.setdefault(spoken, key)
        label = (preset.label or "").strip().lower()
        if label:
            mapping.setdefault(label, key)
    return mapping


def _intent_spoken_map() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for preset in INTENT_PRESETS:
        canonical = (preset.intent or preset.key or "").strip()
        if not canonical:
            continue
        mapping.setdefault(canonical.lower(), canonical)
        key_value = (preset.key or "").strip()
        if key_value:
            mapping.setdefault(key_value.lower(), canonical)
    return mapping


@dataclass(frozen=True)
class PersonaIntentCatalogSnapshot:
    persona_presets: Dict[str, PersonaPreset]
    persona_spoken_map: Dict[str, str]
    persona_axis_tokens: Dict[str, List[str]]
    intent_presets: Dict[str, IntentPreset]
    intent_spoken_map: Dict[str, str]
    intent_axis_tokens: Dict[str, List[str]]
    intent_buckets: Dict[str, List[str]]
    intent_display_map: Dict[str, str]


@dataclass(frozen=True)
class PersonaIntentMaps:
    persona_axis_tokens: Mapping[str, Mapping[str, str]]
    intent_synonyms: Mapping[str, str]
    persona_presets: Mapping[str, PersonaPreset]
    persona_preset_aliases: Mapping[str, str]
    intent_presets: Mapping[str, IntentPreset]
    intent_preset_aliases: Mapping[str, str]
    intent_display_map: Mapping[str, str]


_PERSONA_INTENT_MAPS_CACHE: PersonaIntentMaps | None = None


def _build_persona_intent_maps_from_snapshot(
    snapshot: PersonaIntentCatalogSnapshot,
) -> PersonaIntentMaps:
    persona_axis_map: Dict[str, Mapping[str, str]] = {}
    for axis_key, tokens in (snapshot.persona_axis_tokens or {}).items():
        axis_lower = (axis_key or "").strip().lower()
        if not axis_lower:
            continue
        mapping: Dict[str, str] = {}
        for token in tokens or []:
            token_str = (token or "").strip()
            if token_str:
                mapping.setdefault(token_str.lower(), token_str)
        if mapping:
            persona_axis_map[axis_lower] = MappingProxyType(mapping)

    intent_axis_tokens = snapshot.intent_axis_tokens.get("intent", []) or []
    if intent_axis_tokens:
        intent_axis_map: Dict[str, str] = {}
        for token in intent_axis_tokens:
            token_str = (token or "").strip()
            if token_str:
                intent_axis_map.setdefault(token_str.lower(), token_str)
        if intent_axis_map:
            persona_axis_map["intent"] = MappingProxyType(intent_axis_map)

    persona_presets = MappingProxyType(dict(snapshot.persona_presets or {}))
    persona_aliases: Dict[str, str] = {}
    for alias, canonical in (snapshot.persona_spoken_map or {}).items():
        alias_str = (alias or "").strip().lower()
        canonical_str = (canonical or "").strip()
        if alias_str and canonical_str:
            persona_aliases.setdefault(alias_str, canonical_str)
    for key, preset in persona_presets.items():
        canonical_key = (key or "").strip()
        if not canonical_key:
            continue
        canonical_lower = canonical_key.lower()
        persona_aliases.setdefault(canonical_lower, canonical_key)
        spoken = (getattr(preset, "spoken", "") or "").strip()
        if spoken:
            persona_aliases.setdefault(spoken.lower(), canonical_key)
        label = (getattr(preset, "label", "") or "").strip()
        if label:
            persona_aliases.setdefault(label.lower(), canonical_key)

    persona_aliases_proxy = MappingProxyType(persona_aliases)

    intent_presets = MappingProxyType(dict(snapshot.intent_presets or {}))
    intent_aliases: Dict[str, str] = {}
    intent_synonyms: Dict[str, str] = {}
    for spoken, canonical in (snapshot.intent_spoken_map or {}).items():
        spoken_str = (spoken or "").strip().lower()
        canonical_str = (canonical or "").strip()
        if spoken_str and canonical_str:
            intent_synonyms.setdefault(spoken_str, canonical_str)
            intent_aliases.setdefault(spoken_str, canonical_str)
    for canonical, display in (snapshot.intent_display_map or {}).items():
        canonical_str = (canonical or "").strip()
        if not canonical_str:
            continue
        intent_synonyms.setdefault(canonical_str.lower(), canonical_str)
        intent_aliases.setdefault(canonical_str.lower(), canonical_str)
    for key, preset in intent_presets.items():
        canonical_key = (key or "").strip()
        if not canonical_key:
            continue
        intent_aliases.setdefault(canonical_key.lower(), canonical_key)
        intent_value = (getattr(preset, "intent", "") or "").strip()
        if intent_value:
            intent_aliases.setdefault(intent_value.lower(), canonical_key)

    return PersonaIntentMaps(
        persona_axis_tokens=MappingProxyType(persona_axis_map),
        intent_synonyms=MappingProxyType(intent_synonyms),
        persona_presets=persona_presets,
        persona_preset_aliases=persona_aliases_proxy,
        intent_presets=intent_presets,
        intent_preset_aliases=MappingProxyType(intent_aliases),
        intent_display_map=MappingProxyType(dict(snapshot.intent_display_map or {})),
    )


def _should_cache_persona_maps() -> bool:
    return not os.environ.get("PYTEST_CURRENT_TEST")


def persona_intent_maps(*, force_refresh: bool = False) -> PersonaIntentMaps:
    """Return cached persona/intent maps for callers that need alias lookups."""

    global _PERSONA_INTENT_MAPS_CACHE

    if not force_refresh and _should_cache_persona_maps():
        if _PERSONA_INTENT_MAPS_CACHE is not None:
            return _PERSONA_INTENT_MAPS_CACHE

    snapshot = persona_intent_catalog_snapshot()
    maps = _build_persona_intent_maps_from_snapshot(snapshot)

    if _should_cache_persona_maps() and not force_refresh:
        _PERSONA_INTENT_MAPS_CACHE = maps

    return maps


def persona_intent_maps_reset() -> None:
    """Clear any cached persona/intent maps."""

    global _PERSONA_INTENT_MAPS_CACHE
    _PERSONA_INTENT_MAPS_CACHE = None


def validate_persona_presets(
    presets: Iterable[PersonaPreset] | None = None,
) -> None:
    """Ensure persona presets use only Concordance-recognised persona axes."""

    presets_iterable = list(presets) if presets is not None else list(PERSONA_PRESETS)
    voice_tokens = persona_axis_tokens("voice")
    audience_tokens = persona_axis_tokens("audience")
    tone_tokens = persona_axis_tokens("tone")
    for preset in presets_iterable:
        invalid_axes: list[str] = []
        if preset.voice and preset.voice not in voice_tokens:
            invalid_axes.append(f"voice={preset.voice}")
        if preset.audience and preset.audience not in audience_tokens:
            invalid_axes.append(f"audience={preset.audience}")
        if preset.tone and preset.tone not in tone_tokens:
            invalid_axes.append(f"tone={preset.tone}")
        if invalid_axes:
            joined = ", ".join(invalid_axes)
            raise ValueError(
                f"Persona preset '{preset.key}' includes unsupported axis tokens: {joined}"
            )


def validate_intent_presets(
    presets: Iterable[IntentPreset] | None = None,
) -> None:
    """Ensure intent presets map to canonical intents."""

    presets_iterable = list(presets) if presets is not None else list(INTENT_PRESETS)
    allowed_intents = persona_axis_tokens("intent")
    for preset in presets_iterable:
        if preset.intent not in allowed_intents:
            raise ValueError(
                f"Intent preset '{preset.key}' references unsupported intent token: {preset.intent}"
            )


def persona_catalog() -> dict[str, PersonaPreset]:
    """Return a keyed persona preset catalog.

    This provides a single, typed view over PERSONA_PRESETS for GPT actions,
    help hub, suggestion GUIs, and docs to consume.
    """

    return {preset.key: preset for preset in PERSONA_PRESETS}


def intent_catalog() -> dict[str, IntentPreset]:
    """Return a keyed intent preset catalog.

    This aligns INTENT_PRESETS with the intent axis and bucket maps so callers
    can treat it as the canonical intent preset surface.
    """

    return {preset.key: preset for preset in INTENT_PRESETS}


def persona_intent_catalog_snapshot() -> PersonaIntentCatalogSnapshot:
    """Return a consolidated snapshot of persona/intent presets and axis metadata."""

    personas = persona_catalog()
    persona_spoken_map = _persona_spoken_map_from_presets(personas)
    persona_axes = {
        axis: sorted(persona_axis_tokens(axis))
        for axis in ("voice", "audience", "tone")
    }
    intents = intent_catalog()
    intent_spoken_map = _intent_spoken_map()
    intent_axes = {"intent": sorted(persona_axis_tokens("intent"))}
    raw_buckets = intent_bucket_presets()
    intent_buckets = {
        bucket: [key for key in keys if key in intents]
        for bucket, keys in raw_buckets.items()
    }
    intent_display_map: Dict[str, str] = {}
    for preset in intents.values():
        canonical = (preset.intent or preset.key or "").strip()
        if not canonical:
            continue
        label = (preset.label or "").strip() or canonical
        intent_display_map.setdefault(canonical, label)
        key_value = (preset.key or "").strip()
        if key_value:
            intent_display_map.setdefault(key_value, label)
    return PersonaIntentCatalogSnapshot(
        persona_presets=personas,
        persona_spoken_map=persona_spoken_map,
        persona_axis_tokens=persona_axes,
        intent_presets=intents,
        intent_spoken_map=intent_spoken_map,
        intent_axis_tokens=intent_axes,
        intent_buckets=intent_buckets,
        intent_display_map=intent_display_map,
    )
