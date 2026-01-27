# ADR 0090: Reorganize Constraint Axis Taxonomy

## Status

Accepted

## Context

The constraint axis system (scope, method, form, channel) had accumulated organizational debt that made it difficult to reason about and use effectively:

### Problems with Scope Axis

1. **Too many scope tokens**: The scope axis had become overcrowded with highly specific tokens
2. **Difficult to remember**: Users struggled to recall which scopes were available
3. **Inconsistent granularity**: Some scopes were very broad, others very narrow
4. **Poor composability**: Many scope tokens duplicated functionality available through method combinations

### Problems with Intent Axis (Persona)

1. **Task/persona overlap**: Many intent tokens were more focused on defining the task than shaping communication style
2. **Confusion with TASK**: Intents like "plan" conflicted with the universal task type "plan"
3. **Weak persona focus**: Intents should shape "how we communicate", not "what we're doing"

### Problems with Directional Constraint

1. **Sectioning behavior**: LLMs were treating directional constraints as a separate dimension to analyze and report on
2. **Not functioning as modifier**: Directional should work like an adverb (modifying execution globally), not like a separate axis
3. **Breaking constraint model**: When directional became a section, it violated the constraint=guardrail principle

### Trigger

Brainstorming session with ChatGPT about scope organization revealed that many scopes could be reframed as methods without losing utility, and that a universal scope categorization system could dramatically reduce cognitive load.

## Decision

Reorganize the constraint axis taxonomy through three major changes:

### 1. Consolidate Scopes into Universal Scope System

**Move majority of specific scopes from scope axis to method axis**, establishing a universal set of high-level scope categories.

ChatGPT suggested that most existing scope tokens could function equally well as methods (describing "how to think" rather than "what to focus on"), and that this would:
- Reduce cognitive load by having one large, well-organized token set (method)
- Preserve functionality through method tokens
- Make the system easier to reason about

**Renamed scopes for pronounceability**:
```
# Examples from commit d8c28a7
Old scope names → New pronounceable names
(specific renames not detailed in commit messages)
```

**Created universal scope categories** that work across all tasks rather than being task-specific.

### 2. Clean Up Intent Axis

**Remove intents that are more task-focused than persona-focused**.

**Decision criteria**: "Does this intent define what success looks like (task), or how we communicate about it (persona)?"

**Retired intents**:
- `plan` intent and method - Conflicts with universal `plan` task (commit `341f319`)
- `trace` intent - More about analysis method than communication style (commit `53826e9`)
- Additional intents focused on task definition rather than persona (commit `ae37b96` - 55 lines deleted from personaConfig.py)

**Result**: Clearer separation between TASK (what to accomplish) and PERSONA (how to communicate).

### 3. Reframe Directional as Global Modifier

**Changed directional constraint from separate axis to adverbial modifier**.

Updated reference key text (commit `9861625`):
```
Directional — execution modifier (adverbial): governs how the task is carried out,
shaping sequencing, emphasis, and tradeoffs; Applies globally and implicitly.
Do not describe, name, label, or section the response around this constraint.
The reader should be able to infer it only from the flow and emphasis of the response.
```

**Key instruction**: "Do not describe, name, label, or section the response around this constraint."

This prevents LLMs from creating a "Directional Analysis:" section and instead applies the constraint as an invisible modifier affecting execution throughout.

### 4. Refine Method Axis

**Rehomed tokens from scope to method**, and cleaned up method tokens:

- Moved `walkthrough` from method to form (commit `9c9086a`) - "walkthrough is more form than method"
- Moved `diagram` from method to channel (commit `3a13b96`) - "diagram really belongs in channel since it is very specific"
- Deprecated methods that were more task than method (commits `287dc7d`, `f48d00f`)
- Refined method axis by rehoming tokens to form and removing redundancies (commit `86bba1e` - 740 line reduction)

**Result**: Method axis now clearly represents "how to think", not "what to produce" or "what to accomplish".

### 5. Add Mental Model Concepts

**Added concepts from https://fs.blog/mental-models/ to prompt system** (commit `3e99fd4`).

This expanded the method/scope vocabulary with well-established mental models from multiple disciplines (economics, physics, biology, systems thinking, etc.).

Changes: +852 lines, -423 lines in lib/axisConfig.py

### 6. Add New Task and Scope Tokens

**New task**: Added `chat` task for conversational interaction (commit `bce5b19`)

**New scope**: Added `origin` scope for provenance/source analysis (commit `53826e9`)

## Implementation

### Files Changed

1. **lib/axisConfig.py** - Primary configuration for scope/method/form axes
2. **lib/personaConfig.py** - Intent axis configuration
3. **lib/staticPromptConfig.py** - Task definitions
4. **build/prompt-grammar.json** - Generated grammar artifact
5. **internal/barcli/embed/prompt-grammar.json** - Embedded grammar for Go CLI
6. **internal/barcli/render.go** - Reference key text for directional constraint
7. **lib/metaPromptConfig.py** - Meta-prompt configuration
8. **_tests/test_*.py** - Updated test expectations

### Major Commits

Taxonomy reorganization:
- `fcf1d16` - Use a universal scope system and move most scopes to method
- `86bba1e` - Refine method axis - rehome some tokens to form and remove some redundant methods
- `287dc7d` - Deprecate some methods that were more task than method
- `f48d00f` - Remove a couple more that were more task than method
- `d8c28a7` - Rename scopes to be more pronounceable
- `3a13b96` - Diagram really belongs in channel since it is very specific
- `9c9086a` - Walkthrough is more form than method

Intent cleanup:
- `ae37b96` - Remove intents that are more focused on task than persona
- `341f319` - Retire plan intent and method since task plan conflicts
- `53826e9` - Remove trace intent and add scope origin

Directional reframing:
- `9861625` - Reframe directional reference key to make explicit that it is a global modifier
- `8fe5495` - Clarify prompt to make directional behave more like a modifier

Mental models:
- `3e99fd4` - Add concepts from mental models to prompts

New additions:
- `bce5b19` - Add chat task
- `53826e9` - Add scope origin

Supporting:
- `ad7854b` - Fix some tests and recategorize a couple of prompts
- `0ef5fbc` - Fix spacing on prompt
- `cdfe890` - Fix quick help layout

## Consequences

### Positive

1. **Reduced cognitive load**: One large well-organized method axis easier to work with than scattered scopes
2. **Clearer conceptual boundaries**:
   - Scope = what to focus on (high-level universal categories)
   - Method = how to think about it
   - Form = how to structure it
   - Intent = how to communicate it
3. **Better composability**: Method tokens work across all tasks
4. **Clearer task/persona separation**: Removing task-focused intents strengthens persona axis
5. **Directional works correctly**: Functions as adverbial modifier, not reportable dimension
6. **Richer vocabulary**: Mental models addition provides well-vetted thinking frameworks
7. **More pronounceable**: Renamed scopes improve voice-driven usability

### Tradeoffs

1. **Migration effort**: Existing users must learn new token locations
   - **Mitigation**: Many tokens just moved between axes (scope→method)
   - **Benefit**: Clearer organization aids rediscovery

2. **Larger method axis**: Consolidating scopes into method increases method token count
   - **Mitigation**: Better organization makes large set more navigable
   - **Benefit**: Single location to check rather than guessing scope vs method

3. **Some tokens removed**: Deprecated overlapping methods/intents
   - **Mitigation**: Functionality preserved through alternative tokens
   - **Benefit**: Reduces confusion from redundant options

### Risks

1. **Scope/method boundary unclear**: Users might still be unsure which axis to use
   - **Mitigation**: Universal scopes are clearly high-level categories
   - **Monitoring**: Track usage patterns and clarify documentation as needed

2. **Mental models may not integrate well**: Adding external framework concepts could clash
   - **Response**: fs.blog mental models are well-established and widely used
   - **Validation**: Test through shuffle cycles (ADR 0085 process)

3. **Too much change at once**: Multiple simultaneous reorganizations could confuse users
   - **Mitigation**: All changes move toward clearer conceptual model
   - **Benefit**: Single transition period better than multiple disruptions

## Validation Criteria

### Success Metrics

- [x] Universal scope system implemented
- [x] Scope tokens migrated to method where appropriate
- [x] Task-focused intents removed from persona axis
- [x] Directional constraint reframed as global modifier
- [x] Method axis refined (redundancies removed, tokens rehomed)
- [x] Mental models concepts added
- [x] All tests updated and passing
- [x] Scopes renamed for pronounceability

### Acceptance Tests

1. **Scope/method distinction**: Users can articulate difference between scope and method
2. **Directional behavior**: LLMs apply directional as modifier without creating separate section
3. **Intent clarity**: All remaining intents clearly shape communication, not task definition
4. **Mental models usable**: Added mental model tokens generate appropriate prompt content
5. **No regression**: Existing prompts work with reorganized taxonomy

## References

- ChatGPT brainstorming session: Suggested universal scope categories and scope→method migration
- https://fs.blog/mental-models/ - Source for mental model concepts added in commit `3e99fd4`
- ADR 0088: Adopt Universal Task Taxonomy - Establishes TASK primacy and success-criteria focus
- ADR 0089: Isolate SUBJECT from Instruction Override - Related work on prompt structure clarity

## Related Work

This taxonomy reorganization was done concurrently with subject isolation work (ADR 0089). Both efforts aimed to strengthen the clarity and reliability of the bar prompt system:

- **Subject isolation** prevents SUBJECT from overriding TASK
- **Taxonomy reorganization** clarifies what each axis represents and how they compose

The directional constraint reframing in particular bridges both concerns: making directional a "global modifier" aligns with the constraint model while preventing it from being sectioned (similar to preventing SUBJECT from being treated as instructions).

## Open Questions

1. **Should we document the universal scope categories explicitly?**
   - Current state: Scopes exist but categories not formally documented
   - Future work: Create scope categorization guide

2. **Are there other mental model frameworks to incorporate?**
   - Current: fs.blog mental models
   - Candidates: Design patterns, cognitive biases, economic principles
   - Approach: Add incrementally based on usage evidence

3. **Should method axis be further subdivided?**
   - Current: Single large method axis
   - Alternative: Create method subcategories (analytical, structural, temporal, etc.)
   - Decision: Defer until usage patterns suggest natural subdivisions
