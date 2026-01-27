# ADR 0092: Consolidate All Output Formats in Channel Axis

## Status

Accepted

## Context

ADR 0091 implemented three architectural changes based on the first shuffle analysis (seeds 0001-0020):
1. Split form (content structure) and channel (delivery format)
2. Reframed method tokens as task modifiers
3. Embraced persona composition flexibility

The second shuffle analysis (seeds 0021-0040, post-refactor) validated these changes and showed significant improvements:

**Improvements achieved:**
- Overall quality: 4.04 → 4.16 (+0.12)
- Excellent prompts: 35% → 55% (+20 percentage points)
- Combination harmony: 3.75 → 4.05 (+0.30)
- Persona composition: Fully resolved (embracing flexibility worked)
- Method reframing: Measurably clearer (fewer task overlap issues)

However, the evaluation also revealed that **the form/channel split only partially resolved format conflicts**:

### Persistent Format Conflicts (25% of corpus)

Five prompts (seeds 0028, 0034, 0036, 0039, 0040) exhibited output format conflicts:

1. **Seed 0028**: `code` form + categorization needs prose
2. **Seed 0034**: `adr` + `sync` channels (both complete structural formats)
3. **Seed 0036**: `html` form + `slack` channel (HTML vs Slack Markdown)
4. **Seed 0039**: `shellscript` form + `presenterm` channel (shell script vs slides)
5. **Seed 0040**: `plain` form + `presenterm` channel (prose walls vs slide structure)

### Root Cause: Output Exclusivity, Not Axis Placement

The critical insight from the post-refactor analysis:

**The problem is NOT form vs channel taxonomy.**

**The problem IS output exclusivity.**

Tokens that specify "ONLY output format X" (e.g., `shellscript`, `diagram`, `presenterm`) fundamentally conflict with tokens specifying "ONLY format Y", **regardless of which axis they're in**.

Moving output formats from form to channel (ADR 0091 Phase 1) helped, but:
- `plain` remained in both form AND channel, creating cross-axis conflicts
- Multiple channel tokens could be selected (e.g., `adr` + `sync`), creating intra-axis conflicts
- Format conflicts occurred both within and across axes

### Current Token Distribution (Post-ADR 0091)

**Form axis** (35 tokens):
- Content structure: bullets, questions, scaffold, socratic, walkthrough, visual, table, variants
- Output formats still present: **plain** (also in channel)
- Total: actions, activities, bug, bullets, cards, case, checklist, cocreate, commit, contextualise, direct, facilitate, faq, formats, indirect, ladder, log, merge, **plain**, questions, recipe, rewrite, scaffold, socratic, spike, steps, story, table, test, tight, variants, visual, walkthrough, wardley, wasinawa

**Channel axis** (14 tokens):
- Output formats: code, gherkin, diagram, html, shellscript, svg, adr, presenterm, codetour, **plain**
- Platform wrappers: slack, jira, remote
- Facilitation format: sync

**Current validation**: None - users can select multiple output-exclusive formats (e.g., `adr` + `sync` + `plain`)

### Directional Axis Clarification

Separately, the directional axis tokens were refreshed to clarify they are **task modifiers** (like method tokens) rather than separate tasks. Directional tokens specify **navigation patterns within the response** (e.g., `fig` = abstract ↔ concrete alternation) and consistently scored 4-5/5 in both shuffle analyses with zero conflicts.

This clarification was made independently but aligns with the broader task modifier framing established in ADR 0091.

## Decision

Make two structural changes to eliminate output format conflicts:

### 1. Consolidate All Output Formats in Channel Axis

**Move `plain` from form to channel-only**, completing the migration of all output-exclusive formats to a single axis.

**Rationale:**
- `plain` specifies complete output format: "plain prose... no bullets, tables, or code blocks"
- Having `plain` in both axes allows `plain` form + `presenterm` channel = format conflict
- Consolidating all formats in one axis enables simple validation

**After migration:**

**Form axis** (34 tokens - content structure ONLY):
- actions, activities, bug, bullets, cards, case, checklist, cocreate, commit, contextualise
- direct, facilitate, faq, formats, indirect, ladder, log, merge, questions, recipe
- rewrite, scaffold, socratic, spike, steps, story, table, test, tight, variants
- visual, walkthrough, wardley, wasinawa

**Channel axis** (14 tokens - all output formats/delivery):
- Output formats: code, codetour, diagram, gherkin, html, **plain**, presenterm, shellscript, svg
- Structural formats: adr, sync
- Platform wrappers: jira, remote, slack

**Key principle:** Form describes *how ideas are organized inside the response*. Channel describes *what wrapper or format the response is delivered in*.

### 2. Channel is Already Single-Select (No Implementation Needed)

**Discovery:** Channel (and form) are already enforced as single-select in `internal/barcli/build.go` lines 348-352:

```go
case "channel":
    if len(s.channel) > 0 {
        return s.errorf(errorConflict, "channel accepts a single token")
    }
    s.channel = append(s.channel, token)
```

**Validation:**
```bash
$ ./bar build probe adr sync
error: channel accepts a single token
```

**This means:**
- Channel has been single-select since its implementation
- The completion system (`completion.go` line 198) treats it as boolean: `channel bool`
- Shuffle (`shuffle.go` line 73) picks ONE token per stage
- Build validates and rejects multiple channel tokens

**Rationale for single-select design:**
- Output-exclusive formats are mutually incompatible by definition
- "Output as shellscript" + "output as slide deck" = impossible requirement
- "ADR document structure" + "session plan structure" = conflicting structures
- Platform wrappers (slack, jira) conflict with format tokens (e.g., `html` + `slack`)

**Phase 2 originally planned: Add channel validation**
**Phase 2 actual outcome: Validation already exists, no implementation needed**

### 3. Document Directional as Task Modifiers

**Clarify in documentation** that directional tokens are task modifiers that specify navigation patterns within the response, not separate tasks or constraints.

**Examples:**
- `fig` = abstract ↔ concrete alternation (figure-ground reversal)
- `dip ong` = concrete → action → extension
- `fly ong` = abstract → action → extension
- `rog` = structure → reflection

This aligns directional with method tokens (both enhance/modify tasks) while maintaining their distinct purpose (navigation vs analytical technique).

## Implementation

### Phase 1: Remove plain from Form Axis

**Action:** Edit `lib/axisConfig.py` to remove `plain` token from form axis.

**Current state:**
```python
'form': {
    ...
    'plain': 'The response uses plain prose with natural paragraphs and sentences, imposing no additional structure such as bullets, tables, or code blocks.',
    ...
}
```

**After removal:** `plain` exists in channel axis only.

**Files affected:**
- `lib/axisConfig.py` - Remove plain from form dict
- Generated files will be updated by `make axis-regenerate-apply`

### Phase 2: Verify Python Consistency with Single-Select Channel

**Action:** Review Python code to ensure it respects the existing single-select channel design.

**Python files to check:**
- `lib/modelPatternGUI.py` - Recipe parsing (line 1261: `channel_tokens: list[str] = []`)
- `lib/talonSettings.py` - Axis values filtering
- Any validation or prompt building logic

**Verification:**
```python
# Check if Python allows multiple channel tokens:
# In modelPatternGUI.py _parse_bar_style_recipe():
# channel_tokens: list[str] = []  # Can hold multiple!
```

**Action items:**
1. Check if Python code allows multiple channel tokens in a recipe
2. If yes, add validation or modify to enforce single-select
3. Ensure Talon-triggered prompts behave same as `bar build` CLI
4. Test that saying "model <task> <channel1> <channel2>" triggers error

**Goal:** Ensure Python respects Go's single-select channel validation.

### Phase 3: Update Documentation

**Update in `GPT/readme.md` and docs:**

1. **Form/Channel distinction:**
   ```markdown
   ## Understanding Form and Channel

   **Form** describes the *internal structure* of your response:
   - How ideas are organized: bullets, prose, questions, steps
   - Pedagogical patterns: scaffold, socratic, walkthrough
   - Analytical structures: visual, table, variants

   **Channel** describes the *output format or delivery context*:
   - Complete output formats: code, diagram, gherkin, html, plain, presenterm, shellscript, svg
   - Structural formats: adr (ADR document), sync (session plan)
   - Platform wrappers: slack, jira, remote
   - codetour (VS Code tour format)

   **Rule:** Use maximum ONE channel token per prompt.
   ```

2. **Add examples:**
   ```markdown
   ### Good Combinations

   ✅ `bullets` form + `slack` channel = Bullet points in Slack message
   ✅ `visual` form + `presenterm` channel = Visual diagrams in slides
   ✅ `scaffold` form + `sync` channel = First-principles teaching workshop
   ✅ `questions` form (no channel) = Interactive questions in default format

   ### Conflicts Prevented by Validation

   ❌ `adr` + `sync` channels = Error: cannot combine ADR document with session plan
   ❌ `html` + `slack` channels = Error: cannot combine HTML output with Slack format
   ❌ `shellscript` + `presenterm` = Error: cannot combine shell script with slides
   ❌ `plain` + `diagram` = Error: cannot combine prose with diagram-only output
   ```

3. **Clarify directional tokens:**
   ```markdown
   ### Directional Tokens (Task Navigation Modifiers)

   Directional tokens specify navigation patterns within the response:
   - `fig`: Abstract ↔ concrete alternation (figure-ground reversal)
   - `fly ong`: Abstract → action → extension
   - `dip ong`: Concrete → action → extension
   - `rog`: Structure → reflection
   - `bog`: Bottom-up grounded reasoning
   - `jog`: Direct interpretation and execution

   Like method tokens, directional tokens enhance the task without redefining it.
   They scored 4-5/5 in all shuffle analysis instances with zero conflicts.
   ```

### Phase 4: Update ADR 0091 Consequences

Add post-evaluation findings section to ADR 0091:

```markdown
## Post-Evaluation Findings (ADR 0092)

The form/channel split produced significant improvements but revealed deeper issues
addressed in ADR 0092:

**Root cause identified:** Output-exclusive format conflicts occur regardless of axis
placement. Solution: Consolidate all output formats in channel axis and enforce
maximum one channel token per prompt.

See ADR 0092 for complete analysis and resolution.
```

## Consequences

### Positive

1. **Complete elimination of format conflicts**
   - All output formats in one axis enables simple validation
   - Cross-axis conflicts impossible (form has no formats, channel is singular)
   - Intra-axis conflicts already prevented by existing single-select enforcement
   - **Bonus:** Validation existed all along, just needed to be documented

2. **Clear axis semantics**
   - Form = content structure (how ideas are organized)
   - Channel = output format/delivery (what wrapper it's delivered in)
   - Directional = navigation pattern (how to move through the response)
   - No semantic overlap or ambiguity

3. **Simple validation rule (already implemented)**
   - "Maximum one channel token" already enforced in build.go since original implementation
   - Clear error messages: "channel accepts a single token"
   - Validation runs early (before prompt generation)
   - No new code needed!

4. **Evidence-based design**
   - Grounded in two shuffle analyses (40 prompts evaluated)
   - Addresses 100% of format conflict cases found
   - Expected improvement: 25% conflict rate → <5% in next evaluation
   - Single-select enforcement already working

5. **Consistent modifier pattern**
   - Method tokens = task modifiers (analytical techniques)
   - Directional tokens = task modifiers (navigation patterns)
   - Both enhance tasks without redefining them

### Tradeoffs

1. **Channel becomes singular**
   - Users cannot combine multiple channels (e.g., `slack` + `sync`)
   - **Mitigation:** This is intentional - multiple output formats are incompatible
   - **Note:** In practice, users rarely need multiple channels

2. **Plain moved to channel**
   - Form axis loses "plain prose" option
   - **Mitigation:** Default form is prose-like; `plain` channel still available
   - **Mitigation:** Other form tokens (bullets, table) provide alternative structures

3. **Validation may surprise users**
   - Users attempting `adr` + `sync` will receive error
   - **Mitigation:** Clear error messages with suggestions
   - **Mitigation:** Documentation explains channel exclusivity

4. **Migration effort**
   - Remove plain from form axis
   - Implement channel validation
   - Update documentation
   - **Mitigation:** Clear implementation plan, automated regeneration

### Risks

1. **Users may want multiple channels**
   - Risk: Some use cases genuinely need "slack-formatted session plan"
   - Response: Format inheritance not currently supported; choose primary format
   - Monitoring: Track user requests for multi-channel support in issues

2. **Plain semantics may be unclear**
   - Risk: Users expect plain in form axis (content style) vs channel (output format)
   - Response: Plain is primarily about output format ("no bullets, tables, code blocks")
   - Monitoring: Watch for confusion in usage patterns

3. **Validation too strict**
   - Risk: Some channel combinations may be compatible in practice
   - Response: Start strict, relax selectively if evidence warrants
   - Validation: Re-evaluate in next shuffle cycle (seeds 0041-0060)

## Validation Criteria

### Success Metrics (Seeds 0041-0060)

Compare to post-ADR 0091 baseline (seeds 0021-0040):

- **Overall quality**: ≥4.30 (baseline: 4.16) - target +0.14 improvement
- **Excellent prompts**: ≥70% (baseline: 55%) - target +15 percentage points
- **Format conflicts**: ≤5% (baseline: 25%) - **critical improvement required**
- **Output-exclusive conflicts**: 0% (baseline: 25%) - **must be eliminated by validation**
- **Combination harmony**: ≥4.20 (baseline: 4.05) - target +0.15 improvement

### Acceptance Tests

1. **Validation prevents format conflicts:**
   ```bash
   bar build fix adr sync
   # Error: Cannot combine multiple channel formats: adr, sync

   bar build check html slack
   # Error: Cannot combine multiple channel formats: html, slack

   bar build probe plain presenterm
   # Error: Cannot combine multiple channel formats: plain, presenterm
   ```

2. **Single channel token succeeds:**
   ```bash
   bar build probe bullets presenterm
   # Success: bullets (form) + presenterm (channel) = valid

   bar build show scaffold sync
   # Success: scaffold (form) + sync (channel) = valid

   bar build diff visual
   # Success: visual (form) + no channel = valid
   ```

3. **Plain removed from form axis:**
   ```bash
   bar build show plain
   # Should interpret plain as channel token, not form

   # Form axis no longer contains plain:
   python3 -c "from lib.axisConfig import AXIS_KEY_TO_VALUE; print('plain' not in AXIS_KEY_TO_VALUE['form'])"
   # True
   ```

4. **Form/channel composition works naturally:**
   ```bash
   bar build probe bullets slack
   # bullets (content structure) + slack (platform wrapper) = bullet points in Slack

   bar build show visual presenterm
   # visual (diagram structure) + presenterm (slide format) = visual slides
   ```

## Implementation Order

1. **Day 1**: Phase 1 - Remove plain from form axis ✅ **COMPLETE**
   - Edit `lib/axisConfig.py`
   - Run `make axis-regenerate-apply`
   - Run `make ci-guardrails` to verify tests pass
   - Commit: d2d689c "Implement ADR 0092 Phase 1"

2. **Day 2**: Phase 2 - Verify Python consistency with single-select channel
   - Review `lib/modelPatternGUI.py` recipe parsing
   - Check if Python allows multiple channel tokens
   - Add validation if needed to match Go behavior
   - Test Talon voice commands respect single-select
   - Commit changes

3. **Day 3**: Phase 3 - Update documentation
   - Update README with form/channel distinction
   - Document that channel is already single-select
   - Document directional as task modifiers
   - Add composition examples
   - Commit changes

4. **Day 4**: Phase 4 - Update ADR 0091
   - Add post-evaluation findings section
   - Link to ADR 0092
   - Commit changes

5. **Day 5-6**: Generate and evaluate seeds 0041-0060
   - Generate new corpus (channel is already single-select)
   - Evaluate using same rubric
   - Measure improvement against targets
   - Document findings

## References

- ADR 0085: Shuffle-Driven Catalog Refinement (evaluation process)
- ADR 0091: Refine Axis Boundaries After Shuffle Analysis (form/channel split, method reframing)
- Post-refactor evaluation: `docs/adr/evidence/0085/evaluations-post-refactor.md`
- Recommendations: `docs/adr/evidence/0085/recommendations-post-refactor.yaml`
- Shuffle corpus seeds 0021-0040: `docs/adr/evidence/0085/corpus/`

## Future Work

1. **Format inheritance (optional future enhancement)**
   - Allow platform wrapper + structural format composition (e.g., `slack` flavor of `sync`)
   - Would require: nested channel syntax, inheritance semantics, validation updates
   - Defer until evidence shows strong user demand

2. **Smart channel defaults**
   - Detect when form strongly implies channel (e.g., `wardley` → diagram output)
   - Provide suggestions rather than auto-selecting
   - Would improve UX for format-specific forms

3. **Channel metadata**
   - Add `output_exclusive: true` metadata to tokens
   - Add `platform_wrapper: true` for slack/jira/remote
   - Enable more sophisticated validation rules if needed

4. **Next shuffle cycle validation**
   - Generate seeds 0041-0060 after implementation
   - Validate format conflicts eliminated (target: 0%)
   - Measure overall quality improvement (target: ≥4.30)
   - Re-evaluate if further refinements needed
