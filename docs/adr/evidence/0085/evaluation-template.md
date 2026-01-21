# Shuffle Evaluation Template

Use this template to evaluate each shuffled prompt against the prompt key (ADR 0083).

## Seed: {N}

**Evaluator:** {name}
**Date:** {YYYY-MM-DD}
**Corpus source:** {corpus directory or generation command}

---

## Tokens Selected

- **static:** `{token}` — {description if needed}
- **completeness:** `{token}` — {description if needed}
- **scope:** `{token(s)}` — {description if needed}
- **method:** `{token(s)}` — {description if needed}
- **form:** `{token}` — {description if needed}
- **channel:** `{token}` — {description if needed}
- **directional:** `{token}` — {description if needed}
- **persona:**
  - preset: `{preset_name}` — {label}
  - voice: `{token}` — {description if needed}
  - audience: `{token}` — {description if needed}
  - tone: `{token}` — {description if needed}
  - intent: `{token}` — {description if needed}

---

## Generated Prompt Preview

```
{First 300 characters of rendered prompt text, or full TASK + first CONSTRAINT if shorter}
```

<details>
<summary>Full prompt (click to expand)</summary>

```
{Full rendered prompt}
```

</details>

---

## Evaluation Scores

Score each criterion on a 1-5 scale based on the rubric below.

### Task Clarity (1-5)

**Question:** Does the static prompt clearly define what success looks like?

**Score:** {1-5}

**Rubric:**
- **5 - Excellent**: Static prompt is unambiguous, actionable, and defines success criteria clearly
- **4 - Good**: Task is clear with minor room for interpretation
- **3 - Acceptable**: Task is understandable but could be more specific
- **2 - Problematic**: Task is vague or success criteria are unclear
- **1 - Broken**: Task is incomprehensible or contradictory

**Notes:** {Specific observations about task clarity}

---

### Constraint Independence (1-5)

**Question:** Do constraints shape HOW without redefining WHAT?

**Score:** {1-5}

**Rubric:**
- **5 - Excellent**: All constraints stay within their category boundaries; no scope/method/form redefines the task
- **4 - Good**: Minor boundary blur but intent remains clear
- **3 - Acceptable**: One constraint slightly oversteps but overall remains usable
- **2 - Problematic**: Multiple constraints fight over defining the task itself
- **1 - Broken**: Constraints contradict the task or each other

**Notes:** {Specific observations about constraint independence}

---

### Persona Coherence (1-5)

**Question:** Does the persona stance make sense for this task?

**Score:** {1-5}

**Rubric:**
- **5 - Excellent**: Persona reinforces task and constraints; voice/audience/tone harmonize
- **4 - Good**: Persona mostly appropriate with minor mismatches
- **3 - Acceptable**: Persona feels forced but doesn't break the prompt
- **2 - Problematic**: Persona conflicts with task or constraints
- **1 - Broken**: Persona is nonsensical or contradictory for this context

**Notes:** {Specific observations about persona coherence}

---

### Category Alignment (1-5)

**Question:** Is each token doing the job of its stated category?

**Score:** {1-5}

**Rubric:**
- **5 - Excellent**: Every token operates within its category's purpose (scope defines boundary, method defines reasoning tool, etc.)
- **4 - Good**: One token slightly blurs category lines but remains interpretable
- **3 - Acceptable**: Tokens work but one feels miscategorized
- **2 - Problematic**: Multiple tokens appear to be in wrong categories
- **1 - Broken**: Token categories are clearly misaligned with their behavior

**Notes:** {Specific observations about category alignment}

---

### Combination Harmony (1-5)

**Question:** Do the selected tokens work together or fight?

**Score:** {1-5}

**Rubric:**
- **5 - Excellent**: Tokens reinforce each other; the whole is greater than the sum
- **4 - Good**: Tokens coexist peacefully with some synergy
- **3 - Acceptable**: Tokens are neutral; no conflict but no amplification
- **2 - Problematic**: Some tokens create tension or redundancy
- **1 - Broken**: Tokens produce incoherent or contradictory combination

**Notes:** {Specific observations about combination harmony}

---

## Overall Assessment

**Overall Score:** {average of five scores above, rounded to nearest 0.5}

**Summary:** {2-3 sentence summary of prompt quality and key strengths/weaknesses}

---

## Detailed Notes

{Qualitative observations, specific concerns, token interactions, edge cases, surprising behaviors, etc.}

**Positive observations:**
- {bullet points of what worked well}

**Concerns:**
- {bullet points of issues identified}

**Interesting interactions:**
- {bullet points of notable token combinations}

---

## Recommendations

Based on this evaluation, what actions should be taken on the catalog?

### Retire

```yaml
- action: retire
  token: "{token}"
  axis: "{axis}"
  reason: "{brief explanation}"
  evidence: [seed_{N}]
```

### Edit

```yaml
- action: edit
  token: "{token}"
  axis: "{axis}"
  current: "{current description}"
  proposed: "{proposed description}"
  reason: "{brief explanation}"
  evidence: [seed_{N}]
```

### Recategorize

```yaml
- action: recategorize
  token: "{token}"
  from_axis: "{current_axis}"
  to_axis: "{proposed_axis}"
  reason: "{brief explanation}"
  evidence: [seed_{N}]
```

### Add

```yaml
- action: add
  axis: "{axis}"
  proposed_token: "{token}"
  proposed_description: "{description}"
  reason: "{explanation of gap}"
  evidence: [seed_{N}]
```

---

## Metadata

- **Seed:** {N}
- **Evaluation date:** {YYYY-MM-DD}
- **Evaluator:** {name}
- **Time spent:** {minutes}
- **Prompt key version:** ADR 0083 (2026-01-20)
