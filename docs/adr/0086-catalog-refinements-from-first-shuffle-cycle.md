# ADR 0086: Catalog Refinements from First Shuffle Cycle

## Status

Implemented

**Implementation Summary:**
- Phase 1 (Loops 1-5): Preset-first intent/persona interaction across TUI2, CLI completion, and shuffle
- Phase 2 (Loops 6-7): Retired "infer" static prompt, rewrote directional descriptions with operational language

**Completed Sections:**
- Section 1: Retire "infer" Static Task ✅
- Section 2: Document Intent/Preset Interaction Pattern ✅
- Section 3: Clarify Directional Descriptions ✅

**Optional Sections (Deferred):**
- Section 4: Add Tone/Audience Compatibility Guidance (medium priority, optional)
- Section 5: Document Constraint Combination Patterns (low priority, optional)
- Section 6: Investigation: Consolidate Compound Directionals (future work)

See work log at: docs/adr/0086-catalog-refinements-from-first-shuffle-cycle.work-log.md

## Context

ADR 0085 established a shuffle-driven refinement process for systematically evaluating the prompt catalog. The first refinement cycle (Loop 4) evaluated 20 randomly generated prompts and identified several catalog quality issues:

**High-Severity Issues (2):**
1. The "infer" static task contradicts ADR 0083's principle that "task defines success"
2. Intent + persona preset combinations create ambiguity (e.g., "coach" intent + "scientist_to_analyst" preset)

**Medium-Severity Issues (6):**
3. Directional descriptions use vague language ("synthesized lens", "fused stance") without operational clarity
4. Compound directionals (fig, fog, rog, bog, dig, dip, fip) are hard to distinguish
5. Tone + audience combinations can conflict (e.g., "casually" to "CEO")

**Evidence:** See `docs/adr/evidence/0085/recommendations.yaml` with seeds demonstrating each issue.

These findings represent systematic catalog debt that reduces prompt clarity and user confidence in token selection.

---

## Decision

Apply the following catalog edits based on first refinement cycle evidence:

### 1. Retire "infer" Static Task (High Priority)

**Current:**
```python
STATIC_PROMPTS = {
    "infer": "The response infers the task without being told what to do."
}
```

**Issue:** This contradicts ADR 0083's core principle: "TASK: The primary action to perform. This defines success." If the task is to infer, that's a meta-task that should be stated explicitly.

**Decision:** **RETIRE** the "infer" token.

**Rationale:**
- Violates the prompt key's foundational contract
- Creates confusion about what "success" means
- Users selecting "infer" want the LLM to propose a task, which should be explicit: "The response proposes what task would be most valuable for this subject, then executes that task"
- Evidence: seed_1 produced ambiguous output

**Migration:**
- Remove from `lib/promptConfig.py`
- Add deprecation note if needed for backwards compatibility
- Suggest users explicitly state "propose and execute a task" in subject text instead

---

### 2. Document Intent/Preset Interaction Pattern (High Priority)

**Current behavior:** Intent can be freely combined with persona presets, leading to redundancy or contradictory stances.

**Issue:** Persona presets have implicit intents. Example:
- `scientist_to_analyst` preset implies "inform" intent
- Adding explicit `coach` intent creates ambiguity: should I inform (preset) or coach (intent)?
- Evidence: seed_20 combined these, producing confused output

**Root cause:** Presets are **bundled** (voice + audience + tone + implicit intent), while intent is an **unbundled** "why" modifier. Mixing bundled and unbundled creates confusion.

**Decision:** Document that presets and explicit intent are **usually mutually exclusive**. No validation logic needed—just clear guidance.

**Rationale:**
- **ADR 015/051 design intent**: Intent exists as standalone "why" modifier for custom voice/audience/tone combinations
- **Legitimate use case**: `"as programmer" + "to team" + "coach"` (custom combo without full preset commitment)
- **Presets already bundle intent**: `teach_junior_dev` = voice(teacher) + audience(junior) + tone(kind) + intent(teach)
- **Keep it simple**: Documentation > validation infrastructure

**Implementation:**

```python
# lib/personaConfig.py

# Document implicit intents in each preset (informational only)
PERSONA_PRESET_IMPLICIT_INTENTS = {
    "peer_engineer_explanation": "inform",
    "teach_junior_dev": "teach",
    "scientist_to_analyst": "inform",
    "stakeholder_facilitator": "plan",      # facilitators help groups plan and align
    "designer_to_pm": "inform",
    "product_manager_to_team": "plan",      # PMs plan product direction with team
    "executive_brief": "inform",
    "fun_mode": "entertain",
}

# Usage guidance (no validation, just documentation)
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
  - Confusing: fun_mode + inform (entertainment vs information)

When in doubt: Use preset alone OR custom voice/audience/tone + intent.
"""
```

**TUI2 stage order change:**

Reorder stage progression to put preset before intent, creating a clearer decision fork:

```go
// internal/bartui2/program.go - stageOrder

var stageOrder = []string{
	"persona_preset", // Bundled persona configuration (optional) - Path 1: takes precedence
	"intent",         // What the user wants to accomplish (optional) - Path 2: for custom builds
	"voice",          // Speaking style (optional) - Path 2 continued
	"audience",       // Target audience (optional) - Path 2 continued
	"tone",           // Emotional tone (optional) - Path 2 continued
	"static",         // Static Prompt - the main prompt type
	"completeness",   // How thorough
	"scope",          // How focused
	"method",         // How to approach
	"form",           // Output format
	"channel",        // Communication style
	"directional",    // Emphasis direction
}
```

**Smart stage skipping:**

When user selects a preset, mark intent as implicitly satisfied:

```go
// In selectCompletion() when currentStage == "persona_preset"
if len(c.Fills) > 0 {
	sourceKey := currentStage + ":" + c.Value
	for category, value := range c.Fills {
		// Existing auto-fill logic for voice/audience/tone...
	}
	// NEW: Mark intent as implicitly satisfied
	m.tokensByCategory["intent"] = []string{"(implicit)"}
	m.autoFilledTokens["intent:(implicit)"] = true
	m.autoFillSource["intent:(implicit)"] = sourceKey
}
```

This creates two natural paths:
- **Path 1 (bundled)**: Select preset → skip to static (intent auto-satisfied)
- **Path 2 (unbundled)**: Skip preset → select intent → select voice/audience/tone → static

Users can still Shift+Tab back to override if needed (power user escape hatch).

**CLI completion order alignment:**

Update completion priorities to match TUI2 stage order:

```go
// internal/barcli/completion.go - order constants

const (
	orderDefault         = 1
	orderCommand         = 20
	orderHelpTopic       = 18
	orderCompletionShell = 17
	orderPersonaPreset   = 16  // CHANGED: was 15, now comes first
	orderPersonaIntent   = 15  // CHANGED: was 16, now comes after preset
	orderPersonaVoice    = 14
	orderPersonaAudience = 13
	orderPersonaTone     = 12
	orderStatic          = 11
	// ... rest unchanged
)

// Update stageOrder() function to handle persona stages explicitly:
func stageOrder(stage string) int {
	switch stage {
	case "persona_preset":        // NEW: explicit case
		return orderPersonaPreset
	case "intent":                // NEW: explicit case
		return orderPersonaIntent
	case "voice":                 // NEW: explicit case
		return orderPersonaVoice
	case "audience":              // NEW: explicit case
		return orderPersonaAudience
	case "tone":                  // NEW: explicit case
		return orderPersonaTone
	case "persona":               // Keep generic fallback
		return orderPersonaPreset  // CHANGED: was orderPersonaIntent, now use highest priority
	case "static":
		return orderStatic
	case "completeness":
		return orderCompleteness
	case "method":
		return orderMethod
	case "scope":
		return orderScope
	case "form":
		return orderForm
	case "channel":
		return orderChannel
	case "directional":
		return orderDirectional
	default:
		return orderDefault
	}
}
```

**Shuffle stage order alignment:**

Update shuffle to match the new preset-first order and skip intent when preset selected:

```go
// internal/barcli/shuffle.go - shuffleStageOrder

var shuffleStageOrder = []string{
	"persona_preset",  // CHANGED: was second, now first
	"intent",          // CHANGED: was first, now second
	"voice",
	"audience",
	"tone",
	"static",
	"completeness",
	"scope",
	"method",
	"form",
	"channel",
	"directional",
}

// In Shuffle() function, expand skip logic:
for _, stage := range shuffleStageOrder {
	if excludeSet[stage] {
		continue
	}

	// If we selected a persona_preset, skip intent and individual persona axes
	// since the preset already provides them.
	if hasPersonaPreset && (stage == "intent" || stage == "voice" || stage == "audience" || stage == "tone") {
		continue
	}

	// ... rest of selection logic
}
```

This ensures shuffled prompts follow the same preset-first, intent-skipping pattern as TUI2 and CLI completions.

**Help documentation updates:**

Update `internal/barcli/app.go` TOKEN ORDER section:

```
8. Persona hints / preset (persona=<preset>, intent, voice, audience, tone)
```

Update README.md example to show preset-first pattern:

```bash
# Before:
echo "Fix onboarding" | bar build todo focus steps fog intent=coach persona=facilitator

# After:
echo "Fix onboarding" | bar build todo focus steps fog persona=facilitator
# OR (custom build):
echo "Fix onboarding" | bar build todo focus steps fog intent=coach as-facilitator to-team kindly
```

**Documentation additions:**
- Add guidance to README/help text explaining bundled vs unbundled approach
- Note in TUI2 help: "Presets include implicit intent—usually don't need explicit intent"
- Update CLI help text to show preset before intent in persona stage
- Update examples to demonstrate preset-first pattern
- No warnings, no blocking—just clear conceptual model

**Migration:** None needed. This is documentation-only clarification of existing design, plus TUI2 UX improvement and completion order alignment.

---

### 3. Clarify Directional Descriptions (Medium Priority)

**Current problem:** Many directionals use similar abstract language:
- "synthesized lens" (fig)
- "fused stance" (fog, bog)
- "unified perspective" (multiple)

Users cannot distinguish operational differences.

**Decision:** Rewrite directional descriptions with concrete, operational language.

**Proposed rewrites:**

```python
# lib/axisConfig.py - DIRECTIONAL axis
#
# Core directional axes:
#   fog = abstract + general (vertical axis: top)
#   dig = concrete + ground (vertical axis: bottom)
#   rog = reflect + structure (horizontal axis: left)
#   ong = act + extend (horizontal axis: right)
#
# Compounds:
#   fig = fog + dig (full vertical axis)
#   bog = rog + ong (full horizontal axis)

DIRECTIONAL = {
    # Simple directionals (keep as-is or minor clarification)
    "act": "The response provides actionable steps or procedures.",
    "dig": "The response examines concrete details and grounding examples.",

    # Core directionals (clarify)
    "fog": {
        "old": "The response applies an abstracting-generalizing perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response identifies general patterns and abstract principles from the specifics, moving from particular cases to broader insights.",
        "rationale": "Replace 'synthesized lens' with operational description of abstraction/generalization process"
    },

    "rog": {
        "old": "The response applies a reflective-structural perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response examines the structure of the subject (how it's organized), then reflects on why that structure exists and what it reveals.",
        "rationale": "Distinguish from 'analytical' method; emphasize structure-first then reflection"
    },

    "ong": {
        "old": "The response applies an acting-extending perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response identifies concrete actions to take, then extends those actions to related situations or next steps.",
        "rationale": "Replace 'synthesized lens' with operational description of action/extension flow"
    },

    # Compound directionals (clarify)
    "fig": {
        "old": "The response applies an abstracting-generalizing-concretizing-grounding perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response alternates between abstract principles and concrete examples, using each to illuminate the other (figure-ground reversal).",
        "rationale": "Users need operational definition of how abstraction and concretization interact"
    },

    "bog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends acting, extending, reflection, and structure, treating them as a single fused stance.",
        "new": "The response examines the subject's structure and reflects on it, then identifies actions to take and extends them to related contexts.",
        "rationale": "bog = rog + ong (structural reflection + actionable extension); no concrete component"
    },

    # Compound variants (dip/fip/fly combinations)
    "dip bog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends concreteness, grounding, acting, extending, reflection, and structure, treating them as a single fused stance.",
        "new": "The response starts with concrete examples and grounded details, examines their structure and reflects on patterns, then identifies actions and extensions.",
        "rationale": "dip bog = dig + bog: concrete/ground foundation + structural reflection + action/extension"
    },

    "fip rog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends abstraction, generalization, concreteness, grounding, reflection, and structure, treating them as a single fused stance.",
        "new": "The response moves between abstract principles and concrete examples while examining structural patterns and reflecting on what they reveal.",
        "rationale": "fip rog = fig + rog: full vertical axis (abstract ↔ concrete) + structural reflection"
    },

    "fly rog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends abstraction, generalization, reflection, and structure, treating them as a single fused stance.",
        "new": "The response identifies abstract patterns and general principles, then examines their structural relationships and reflects on their implications.",
        "rationale": "fly rog = fog + rog: abstraction/generalization + structural reflection"
    },
}
```

**Key changes:**
- Replace "synthesized lens" / "fused stance" with operational descriptions
- Use verbs describing what the response does (identifies, examines, alternates, moves)
- Preserve semantic components: fog (abstract/general), dig (concrete/ground), rog (reflect/structure), ong (act/extend)
- Make compound relationships explicit: fig = fog + dig, bog = rog + ong
- Distinguish each directional by its component axes, not arbitrary sequences

---

### 4. Add Tone/Audience Compatibility Guidance (Medium Priority)

**Issue:** Some tone + audience combinations are contradictory.
- Evidence: seed_16 combined "casually" (tone) with "to CEO" (audience)
- Result: Tonal mismatch (CEOs expect professional communication)

**Decision:** Document tone/audience compatibility matrix.

**Implementation:**

```python
# lib/personaConfig.py or documentation

TONE_AUDIENCE_GUIDANCE = """
Tone and audience are independent axes, but some combinations create friction:

COMPATIBLE COMBINATIONS:
- "directly" works with all audiences (neutral)
- "kindly" works well with "to junior engineer", "to team"
- "formally" works well with "to CEO", "to stakeholders"
- "casually" works well with "to programmer", "to team"

POTENTIAL CONFLICTS:
- "casually" + "to CEO" → CEOs expect professional tone even if friendly
- "formally" + "to junior engineer" → May create distance that hinders learning
- "bluntly" + "to stakeholders" → May damage relationships

RECOMMENDATIONS:
- Match tone to audience expectations and context
- When in doubt, "directly" is the safe neutral choice
- Consider relationship dynamics (peer vs authority vs learner)
"""
```

**TUI2 guidance:** Show hint when conflicting tone/audience selected:
> "Note: 'casually' to 'CEO' may conflict. Consider 'directly' for professional contexts."

---

### 5. Document Constraint Combination Patterns (Low Priority)

**Issue:** Some constraint combinations work against each other:
- "gist" (short) + "max" (exhaustive) = contradiction
- "edges" (edge cases) + "narrow" (single focus) = tension
- "recipe" + "gherkin" = redundant structured formats

**Decision:** Add constraint compatibility documentation.

**Implementation:**

Create `docs/constraint-combinations.md`:

```markdown
# Constraint Combination Patterns

## Contradictory Combinations

Avoid these combinations as they create conflicting instructions:

| Constraint 1 | Constraint 2 | Conflict | Recommendation |
|--------------|--------------|----------|----------------|
| gist (short) | max (exhaustive) | Length conflict | Choose one based on priority |
| minimal | full | Coverage conflict | Choose one based on scope |
| narrow (single focus) | edges (boundary cases) | Scope conflict | Use 'bound' (specific boundaries) instead |
| recipe | gherkin | Both define format | Choose one structured format |
| tight | outline | Detail level conflict | Choose based on desired depth |

## Complementary Combinations

These combinations reinforce each other:

- **focus + narrow**: Both emphasize single-item specificity
- **edges + bound**: Both deal with boundaries (unusual vs limits)
- **skim + gist**: Both favor brevity
- **max + full**: Both favor completeness
- **dynamics + relations**: Both examine interactions

## Method + Form Synergies

Some methods pair naturally with certain forms:

- **systemic** (systems thinking) + **diagram**: Visual systems
- **cocreate** (collaborative) + **dialogue**: Back-and-forth format
- **tradeoffs** + **table**: Comparison structure
- **tune** (parameter exploration) + **matrix**: Parameter space

## Shuffle Recommendations

When `bar shuffle` generates conflicting constraints:
1. Check this compatibility guide
2. Regenerate with adjusted `--exclude` if needed
3. Manually adjust tokens for better harmony
```

---

### 6. Investigation: Consolidate Compound Directionals (Future Work)

**Issue:** 7+ compound directionals (fig, fog, rog, bog, dig, dip, fip variants) are hard to distinguish.

**Decision:** **Defer to ADR 0087** pending deeper investigation.

**Investigation plan:**
1. Generate 20 shuffles with `--include directional --fill 1.0`
2. Compare outputs for fig vs fog vs rog vs bog
3. Measure user comprehension (survey or user testing)
4. Decide which directionals to retire/merge

**Hypothesis:** Can consolidate to 3-4 core patterns:
- **act** (action-oriented)
- **dig** (concrete details)
- **fig** (abstract ↔ concrete alternation)
- **rog** (structure + reflection)

Evidence requirement: 3+ evaluators agreeing outputs are indistinguishable before retiring.

---

## Implementation

### Phase 1: High Priority (Immediate)

1. **Retire "infer"**
   - Remove from `lib/promptConfig.py`
   - Regenerate grammar: `python scripts/export_prompt_grammar.py`
   - Update tests
   - Add migration note in CHANGELOG

2. **Add intent/preset validation**
   - Add compatibility matrix to `lib/personaConfig.py`
   - Update TUI2 to show warnings
   - Document in help text

### Phase 2: Medium Priority (Next Sprint)

3. **Rewrite directional descriptions**
   - Update `lib/axisConfig.py` with new operational descriptions
   - Regenerate grammar
   - Update documentation

4. **Add tone/audience guidance**
   - Document compatibility in `lib/personaConfig.py`
   - Add TUI2 hints for conflicting combinations

### Phase 3: Low Priority (Background)

5. **Document constraint patterns**
   - Create `docs/constraint-combinations.md`
   - Link from main README
   - Reference in shuffle documentation

6. **Plan directional consolidation investigation**
   - Create ADR 0087 for investigation plan
   - Execute investigation cycle per ADR 0085 process

---

## Consequences

### Positive

- Catalog quality improves systematically
- User confidence in token selection increases
- Contradictory combinations prevented
- Clearer operational guidance for complex tokens
- Evidence-based changes (not arbitrary)

### Tradeoffs

- "infer" retirement may break existing workflows (mitigation: document migration)
- Intent/preset validation adds complexity (mitigation: make warnings, not errors)
- Directional rewrites require user re-learning (mitigation: keep old descriptions in CHANGELOG)

### Risks

- Users may disagree with specific descriptions (mitigation: iterate based on feedback)
- Validation logic may be too restrictive (mitigation: warnings not blocking errors)
- Consolidating directionals may remove nuance (mitigation: require strong evidence)

---

## Validation

### Phase 1 Validation

```bash
# Verify "infer" removed
grep -r "infer" lib/promptConfig.py && echo "ERROR: infer still present" || echo "OK: infer retired"

# Verify grammar regenerated
python scripts/export_prompt_grammar.py
jq '.static_prompts.profiles | has("infer")' prompt_grammar.json
# Should output: false

# Test intent/preset validation
go test ./internal/barcli/... -run TestPersonaIntentValidation
```

### Phase 2 Validation

```bash
# Generate test shuffles with new directionals
for seed in 1 5 9 14 20; do
  echo "=== Seed $seed with new descriptions ==="
  ./bar shuffle --seed $seed | grep -A10 "DIRECTIONAL"
done

# Compare clarity vs old descriptions
diff -u <(git show HEAD~1:lib/axisConfig.py | grep -A5 '"fig":') \
        <(cat lib/axisConfig.py | grep -A5 '"fig":')
```

### Regression Testing

```bash
# Re-run original problematic seeds
./bar shuffle --seed 1   # Should no longer use "infer"
./bar shuffle --seed 16  # Should show tone/audience hint
./bar shuffle --seed 20  # Should show intent/preset hint

# Verify improvements via second refinement cycle
./scripts/shuffle_corpus.sh --count 20 --seed-start 100
# Evaluate seeds 100-119 and compare issue rate vs original 40%
```

---

## References

- ADR 0083: Prompt Key Refinement (defines TASK precedence)
- ADR 0085: Shuffle-Driven Catalog Refinement (established process)
- Evidence: `docs/adr/evidence/0085/recommendations.yaml`
- Seeds demonstrating issues: 1, 5, 7, 9, 14, 16, 18, 20

---

## Success Metrics

**Target after implementation:**
- Issue rate in shuffle evaluations drops from 40% (8/20 seeds) to <20%
- User-reported catalog confusion issues decrease
- Persona preset + intent combinations have clear guidance
- Directional descriptions score >4.0 on clarity (1-5 scale)

**Measurement:**
- Run second refinement cycle (ADR 0085 Loop 5+)
- Compare issue rates and severity distributions
- Track user feedback on directional clarity
