# ADR 0091: Refine Axis Boundaries After Shuffle Analysis

## Status

Accepted

## Context

ADR 0085 established a shuffle-driven refinement process to validate catalog quality through randomized prompt generation. The first evaluation cycle (20 shuffled prompts, seeds 0001-0020) revealed three categories of issues with the current axis taxonomy:

### 1. Form/Channel Boundary Confusion

**Problem**: Form and channel axes have overlapping concerns, creating incompatible combinations.

**Evidence from shuffle analysis:**
- Seed 0001: `gherkin` form + `presenterm` channel = impossible (Gherkin syntax vs presenterm slide format)
- Seed 0013: `plain` form + `diagram` channel = conflict (prose vs code-only output)
- Seed 0018: `gherkin` form + `slack` channel = awkward (raw Gherkin in chat message)

**Root cause**: Form describes both content structure ("bullets", "questions") AND output format ("gherkin", "diagram"), while channel describes delivery wrapper ("slack", "presenterm") AND output format ("diagram"). These concerns bleed into each other.

**Current definitions:**
- Form: "output shape: structural organization (does not imply tone)"
- Channel: "delivery context: platform formatting conventions only"

In practice, tokens violate these boundaries. `gherkin` is in form but dictates output format. `diagram` is in channel but dictates content structure.

### 2. Method/Task Overlap

**Problem**: Some method tokens partially redefine WHAT (the task) rather than HOW (the approach).

**Evidence from shuffle analysis:**
- Seed 0019: `probe` + `dimension` = redundant (both mean "explore multiple dimensions/axes")
- Seed 0007: `pick` + `converge` = redundant (both mean "narrow to recommendation")

**Root cause**: Per ADR 0083, constraints should shape HOW without redefining WHAT. But `dimension` and `converge` methods describe outcomes rather than approaches.

**Current definition:**
- Method: "reasoning tool: how to think, not what to conclude (does not dictate tone or format)"

In practice, some method tokens describe the structure of the result rather than the process of thinking.

### 3. Persona Composition Flexibility

**Problem**: Some persona axis combinations feel inappropriate (e.g., `casually` tone + `to CEO` audience).

**Evidence from shuffle analysis:**
- Seed 0016: `chat` + `to CEO` + `casually` = unprofessional communication style
- Seed 0010: `sort` + `entertain` intent = precision undermined by entertainment goal

**Philosophical question**: Should we prevent these combinations or trust users to know their context?

### Prior Work

- **ADR 0083**: Established constraint/persona boundary (constraints shape HOW, persona shapes WHO/WHY)
- **ADR 0088**: Defined universal task taxonomy (task = success criteria)
- **ADR 0090**: Consolidated axis taxonomy (moved many scopes to method)

## Decision

Make three architectural refinements based on shuffle analysis findings:

### 1. Split Form and Channel Axes

**Split into two orthogonal concerns:**

**Content Form** (new definition):
- **Purpose**: Structure of ideas within the response
- **Domain**: Organization, sequencing, interaction patterns
- **Examples**: `bullets`, `prose`, `questions`, `steps`, `scaffold`
- **Excludes**: Output format specifications

**Delivery Channel** (refined definition):
- **Purpose**: Output format and delivery wrapper
- **Domain**: File formats, platform conventions, structural containers
- **Examples**: `slack`, `presenterm`, `gherkin`, `diagram`, `adr`, `plain`
- **Key insight**: Channel may specify complete output format (gherkin, diagram) or just wrapper (slack, jira)

**Composition principle**: Content form and delivery channel compose naturally:
- `questions` (form) + `slack` (channel) = interactive questions in Slack
- `bullets` (form) + `presenterm` (channel) = bullet points on slides
- `prose` (form) + `adr` (channel) = prose sections within ADR template

**Migration path:**
- Move output-format tokens from form to channel: `gherkin`, `diagram`, `adr`, `plain`, `svg`, `html`, `shellscript`
- Keep content-structure tokens in form: `bullets`, `questions`, `scaffold`, `socratic`, `tight`, `walkthrough`
- Some tokens work in both: `code` (form: structured as code) vs `code` (channel: code file output)

**Validation**: Some combinations remain invalid (e.g., `prose` form + `diagram` channel), but the boundary is now clear: form describes internal structure, channel describes output wrapper.

### 2. Reframe Method as Task Modifiers

**Change perspective from "reasoning tools" to "task modifiers".**

**Current framing**: Method describes HOW to think
- Problem: Implies method is independent of task
- Reality: Many methods only make sense with certain tasks

**New framing**: Method modifies or elaborates on the task
- `probe` + `dimension` = "probe by expanding across multiple dimensions"
- `pick` + `converge` = "pick by converging from broad exploration"
- `show` + `simulation` = "show by simulating scenarios"

**Description template**: "The response [performs task] by [method technique]..."

**Key clarification**: Method should enhance rather than replace the task. If method alone could describe the task, it belongs in static prompts instead.

**Action items:**
- Audit method tokens for task overlap
- Rewrite descriptions to emphasize modification relationship
- For tokens like `dimension` and `converge` that heavily overlap with tasks:
  - **Option A**: Retire and recommend using appropriate static prompt
  - **Option B**: Reframe as explicit task modifiers ("probe using dimensional analysis")
  - **Decision**: Keep for now with improved descriptions (can retire later if confusion persists)

### 3. Embrace Persona Composition Flexibility

**Accept that unconventional persona combinations may be intentional.**

**Rationale:**
- Users know their context better than we do
- "Casual to CEO" might be appropriate in startup culture
- "Entertain + sort" might be for gamified UX
- Restricting combinations reduces expressiveness without clear benefit

**Instead of preventing combinations:**
- Trust user judgment
- Provide clear descriptions so users understand what each token does
- Focus validation on truly broken combinations (form/channel format conflicts)
- Let persona axes compose freely

**Example acceptable combinations:**
- `casually` + `to CEO` = Informal executive communication (intentional in some cultures)
- `entertain` + `sort` = Gamified categorization (valid for certain contexts)

**Example we still prevent:**
- `gherkin` + `presenterm` = Impossible output format (one or the other must be ignored)

## Implementation

### Phase 1: Axis Renaming and Token Migration (1-2 days)

1. **Rename axes in grammar**:
   - `form` → `content_form` (or keep as `form` with new definition)
   - `channel` → `delivery_channel` (or keep as `channel` with expanded scope)

2. **Migrate tokens**:
   ```yaml
   # Move from form to channel:
   - gherkin
   - diagram
   - adr
   - plain
   - svg
   - html
   - shellscript
   - code (as output format)

   # Keep in form:
   - bullets
   - questions
   - scaffold
   - socratic
   - tight
   - walkthrough
   - story
   - cards
   - table
   - variants
   ```

3. **Update descriptions** to clarify composition:
   - Channel tokens: Emphasize output format / delivery wrapper
   - Form tokens: Emphasize internal structure / idea organization

### Phase 2: Method Token Reframing (2-3 days)

1. **Rewrite method descriptions** using task modifier framing:
   ```yaml
   # Before
   dimension: "The response expands conceptual axes to expose structure"

   # After
   dimension: "The response enhances the task by exploring multiple dimensions or axes of analysis, making implicit factors explicit"
   ```

2. **Add usage guidance** to method tokens with strong task affinity:
   ```yaml
   dimension:
     description: "..."
     works_best_with: ["probe", "show", "diff"]
     note: "If the goal is dimensional analysis itself, use 'probe' task with dimension method"
   ```

3. **Audit overlap** between method and static prompts:
   - Document which methods enhance which tasks
   - Identify true duplicates for future retirement

### Phase 3: Documentation Updates (1 day)

1. **Update ADR 0083 prompt key** with refined axis definitions
2. **Update README** with form/channel distinction
3. **Add examples** showing form + channel composition
4. **Document persona flexibility** philosophy

### Phase 4: Validation and Testing (1 day)

1. **Update validation logic**:
   - Remove persona combination warnings
   - Keep form/channel format conflict detection (if implemented)
   - Add helpful messages about composition

2. **Re-run shuffle analysis**:
   - Generate new corpus with updated tokens
   - Verify form/channel split resolves conflicts
   - Confirm method reframing improves clarity

3. **Update tests**:
   - Test form + channel combinations
   - Update method token expectations
   - Remove persona restriction tests

## Consequences

### Positive

1. **Clearer axis boundaries**: Form and channel now have distinct, composable concerns
2. **Better composition**: Users can combine form + channel without format conflicts
3. **Method clarity**: Framing as task modifiers makes purpose explicit
4. **Maximum flexibility**: Persona axes compose freely, trusting user judgment
5. **Evidence-based**: Changes address real issues found in shuffle analysis

### Tradeoffs

1. **Migration effort**: Need to move tokens between axes
   - Mitigation: Clear migration path, automated where possible

2. **Learning curve**: Users must understand form/channel distinction
   - Mitigation: Good examples and documentation

3. **Some combinations still invalid**: Form/channel can conflict (prose + diagram)
   - Mitigation: This is clearer to reason about than previous overlap

4. **Method overlap not fully resolved**: Some methods still blur into tasks
   - Mitigation: Improved descriptions help; can retire tokens later if needed

5. **No persona validation**: Users can create awkward combinations
   - Mitigation: This is intentional; flexibility > restriction

### Risks

1. **Form/channel split may not be intuitive**: Users may not understand distinction
   - Response: Provide clear examples
   - Monitoring: Watch for user confusion in issues/feedback

2. **Method reframing may not solve overlap**: Dimension/converge may still feel redundant
   - Response: Improved descriptions are first step; can retire later
   - Validation: Re-evaluate in next shuffle cycle

3. **Persona flexibility may lead to poor prompts**: Users create ineffective combinations
   - Response: This is acceptable tradeoff for expressiveness
   - Philosophy: Trust users to know their context

## Validation Criteria

### Success Metrics

- [ ] All output-format tokens migrated from form to channel
- [ ] All content-structure tokens remain in form
- [ ] Method descriptions rewritten with task modifier framing
- [ ] Persona validation removed (except format conflicts)
- [ ] Documentation updated with new axis definitions
- [ ] Re-run shuffle analysis shows improved scores for:
  - Form/channel combination harmony: target 4.5+ (was 3.75)
  - Method category alignment: target 4.5+ (was 3.95)

### Acceptance Tests

1. **Form + channel composition works naturally**:
   ```bash
   bar build probe full struct bullets slack
   # Should generate structured bullet points for Slack

   bar build show gist questions presenterm
   # Should generate interactive questions on slides
   ```

2. **Method as task modifier is clear**:
   ```bash
   bar build probe dimension
   # Clear that dimension enhances probe, not replaces it

   bar build diff converge
   # Clear that converge focuses the diff, not replaces it
   ```

3. **Persona composes freely**:
   ```bash
   bar build chat to-ceo casually
   # Allowed (user may know their context)

   bar build sort entertain
   # Allowed (gamification is valid)
   ```

4. **Format conflicts still detectable** (optional validation):
   ```bash
   bar build probe prose diagram --validate
   # Warning: prose form conflicts with diagram channel (code-only)
   ```

## Implementation Order

1. **Day 1-2**: Phase 1 - Axis renaming and token migration
2. **Day 3-4**: Phase 2 - Method token reframing
3. **Day 5**: Phase 3 - Documentation updates
4. **Day 6**: Phase 4 - Validation and testing
5. **Day 7**: Re-run shuffle analysis, review results

## References

- ADR 0083: Prompt Key Refinement (constraint/persona boundaries)
- ADR 0085: Shuffle-Driven Catalog Refinement (evaluation process)
- ADR 0088: Adopt Universal Task Taxonomy (task = success criteria)
- ADR 0090: Reorganize Constraint Axis Taxonomy (scope→method migration)
- Shuffle analysis evidence: `docs/adr/evidence/0085/evaluations.md`
- Recommendations: `docs/adr/evidence/0085/recommendations.yaml`

## Future Work

1. **Automated compatibility checks**: Validate form/channel combinations in bar build
2. **Task affinity metadata**: Document which methods work best with which tasks
3. **Composition examples**: Build library of effective form + channel combinations
4. **Next shuffle cycle**: Re-evaluate after 3-6 months of usage
