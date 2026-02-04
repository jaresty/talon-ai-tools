# ADR 0098: LLM-Optimized Bar CLI Reference Help Page

## Status

Proposed

## Context

The bar CLI provides a sophisticated grammar-based prompt construction system with 7 axes, 100+ tokens, persona presets, and complex composition rules. Currently, LLMs (particularly those embedded in the bar skills) access this information through:

1. **`bar help tokens`** - Dynamic token discovery listing all available tokens across axes
2. **`bar help tokens <filter>`** - Filtered views (static, axes, persona, individual axes)
3. **`bar help`** - General usage and token ordering rules
4. **Skill documentation** - Embedded SKILL.md files with usage patterns and heuristics
5. **Pattern reference** - `docs/bar-pattern-reference.md` with example recipes

While this distributed approach works, it presents challenges for LLM consumption:

- **Multiple queries required**: An LLM must run several commands to gather complete information
- **Fragmented context**: Grammar rules, tokens, patterns, and heuristics exist in separate locations
- **No integrated examples**: Token listings don't show composition patterns or real-world usage
- **Parsing overhead**: Raw `bar help tokens` output requires interpretation and structuring
- **Missing constraints**: Axis caps, incompatibilities, and hierarchy not easily discoverable

The bar skills use discovery-based heuristics to remain version-agnostic, but each invocation requires multiple tool calls to gather sufficient context. A comprehensive, LLM-optimized reference would enable:

- Single-command context loading
- Faster skill execution (fewer discovery queries)
- Better token selection through integrated examples
- Clearer understanding of grammar constraints and composition rules

## Problem

**How do we provide LLMs with a comprehensive, easily digestible reference for the bar CLI grammar that answers all necessary questions (available tokens, grammar rules, composition patterns) with a single command?**

Requirements:
1. **Complete coverage**: All axes, tokens, persona presets, constraints, and ordering rules
2. **LLM-optimized format**: Structured, parseable, with clear semantic sections
3. **Integrated examples**: Show real-world composition patterns for common use cases
4. **Single command access**: No need to run multiple queries or read multiple files
5. **Machine and human readable**: Useful for both LLM consumption and developer reference
6. **Version-agnostic**: Generated from current grammar state, not hardcoded
7. **Extensible**: Easy to add new sections as the grammar evolves

## Decision

Implement **`bar help llm`** (or `bar help reference`) that generates a comprehensive Markdown reference document optimized for LLM consumption.

### Output Format: Markdown

**Rationale for Markdown:**
- **LLM-friendly**: Modern LLMs excel at parsing structured Markdown
- **Hierarchical structure**: Headers create clear semantic sections
- **Code blocks**: Clean syntax for examples and patterns
- **Human-readable**: Developers can use it as reference documentation
- **Extensible**: Easy to add tables, lists, examples, and formatting
- **Portable**: Can be saved to files, piped, or displayed directly

### Document Structure

```markdown
# Bar CLI Reference for LLMs

## Quick Start
- Single-command overview of typical bar workflow
- Example: bar build <tokens> --prompt "text"

## Grammar Architecture
- 7 axes with token counts
- Ordering rules: [persona] [static] [completeness] [scope...] [method...] [form] [channel] [directional]
- Soft caps per axis
- Key=value override syntax

## Token Catalog

### Static Prompts (0-1 token)
[Table with columns: Token Slug | Description | When to Use]

### Completeness (0-1 token)
[Table: Token | Description | Use Case]
- minimal, narrow, gist, full, deep, max, skim

### Scope (0-2 tokens)
[Table: Token | Description | Use Case]
- thing (entities), struct (relationships), act (tasks), time (sequences), mean (semantics), fail (failure modes), good (criteria), view (perspectives)

### Method (0-3 tokens)
[Categorized by thinking style with token tables]
**Decision Methods**: branch, compare, prioritize, constraints...
**Understanding Methods**: mapping, flow, structure, relationships...
**Exploration Methods**: explore, diverge, survey, variants...
**Diagnostic Methods**: diagnose, failure, stress, risks...
[60+ methods organized by category]

### Form (0-1 token)
[Table with output structure examples]
- actions, bullets, checklist, recipe, table, walkthrough, etc.

### Channel (0-1 token)
[Table with delivery contexts]
- adr, code, diagram, plain, slack, etc.

### Directional (0-1 token)
[Table with execution modifiers]
- Complex compounds: bog, dig, dip-bog, dip-ong, fly-ong, etc.

## Persona System

### Preset Personas
[Table: Preset Name | Voice | Audience | Tone | Intent | Spoken Alias]

### Persona Axes (for custom composition)
**Voice**: Who speaks (mentor, colleague, teacher...)
**Audience**: Who receives (junior-engineer, executive...)
**Tone**: Emotional modulation (encouraging, formal, casual...)
**Intent**: Purpose (coach, inform, decide...)

## Composition Rules

### Token Ordering
[Detailed explanation of position constraints]

### Axis Caps
[List of soft caps per axis]

### Incompatibilities
[Table of conflicting token combinations]

### Key=Value Overrides
[Syntax and examples]

## Usage Patterns by Task Type

### Decision-Making
```bash
bar build <decision-scope> full <branching-method> <variants-form> --prompt "..."
```
Example: `bar build thing full branch variants --prompt "Choose between Redis and Postgres"`

### Architecture Documentation
```bash
bar build <planning-scope> full <exploration-method> case adr --prompt "..."
```

### Explanation/Understanding
```bash
bar build time full flow walkthrough --prompt "Explain authentication flow"
bar build mean full scaffold --prompt "What is eventual consistency?"
```

### Structural Analysis
```bash
bar build struct full mapping --prompt "Analyze microservice boundaries"
```

### Problem Diagnosis
```bash
bar build fail full diagnose checklist --prompt "Debug production errors"
```

[10-15 common patterns with concrete examples]

## Token Selection Heuristics

### Choosing Scope
- **Entities/boundaries** → thing, struct
- **Sequences/change** → time
- **Understanding/meaning** → mean
- **Actions/tasks** → act
- **Quality/criteria** → good
- **Failure modes** → fail
- **Perspectives** → view

### Choosing Method
- **Deciding** → branch, compare, prioritize
- **Understanding** → mapping, flow, structure
- **Exploring** → explore, diverge, survey
- **Diagnosing** → diagnose, failure, stress
- **Building cases** → argue, evidence, reasoning
- **Learning** → scaffold, build understanding

### Choosing Form
- **Actionable next steps** → actions, checklist, tasks
- **Multiple alternatives** → variants, options
- **Step-by-step** → walkthrough, recipe, flow
- **Comparison** → table, side-by-side
- **Building understanding** → scaffold
- **Documentation** → case, adr, log

## Advanced Features

### Shuffle for Exploration
```bash
bar shuffle [--seed N] [--include axes] [--exclude axes] [--fill 0.0-1.0]
```

### Output Formats
- `--json`: Machine-readable contract output
- `--output FILE`: Save to file
- `--input FILE`: Read prompt from file

### Skip Sentinels
- `//next`: Skip current stage
- `//:static`: Jump to static stage
- `//:completeness`: Jump to completeness stage

## Examples from Real Usage

[5-10 complete examples showing:]
- User request
- Token selection reasoning
- Complete bar command
- Expected output characteristics

## Grammar Metadata
- Schema version: 1.0
- Total axes: 7
- Total tokens: [count from grammar]
- Static prompts: [count]
- Persona presets: [count]
```

### Implementation Approach

**New command in `internal/barcli/app.go`:**

```go
func (app *App) handleHelpLLM(args []string) error {
    // Load grammar
    grammar := app.loadGrammar()

    // Render comprehensive LLM-optimized markdown
    output := renderLLMHelp(grammar, &renderOptions{
        includeExamples: true,
        includeHeuristics: true,
        includeMetadata: true,
    })

    fmt.Println(output)
    return nil
}
```

**Template-based rendering in `internal/barcli/help_llm.go`:**
- Separate module for LLM help rendering
- Template-driven generation from grammar JSON
- Includes hardcoded example patterns and heuristics
- Categorizes methods by thinking style
- Provides token selection guidance

**Command aliases:**
- `bar help llm` (primary)
- `bar help reference` (alias)
- `bar reference` (shorthand)

### Alternative Formats Considered

**JSON:**
```json
{
  "grammar": {...},
  "axes": [...],
  "tokens": {...},
  "patterns": [...],
  "heuristics": {...}
}
```
- **Pros**: Highly structured, easy to parse programmatically
- **Cons**: Less readable for humans, requires more LLM interpretation, verbose

**YAML:**
- Similar trade-offs to JSON
- More readable than JSON but less standard for LLM consumption

**Plain text with sections:**
- Simpler but less structured
- Harder to parse specific sections
- No syntax highlighting for examples

**Decision: Markdown wins** due to optimal balance of structure, readability, and LLM parsing capabilities.

## Consequences

### Benefits

1. **Single-command context loading**: LLMs can gather all necessary bar information with one query
2. **Faster skill execution**: Bar skills can load complete context upfront instead of multiple discovery queries
3. **Better token selection**: Integrated heuristics and examples guide LLMs to appropriate tokens
4. **Reduced tool calls**: From 3-5 discovery queries down to 1 reference load
5. **Improved consistency**: All LLMs work from the same comprehensive reference
6. **Human-readable documentation**: Developers can use the same output as reference docs
7. **Version-agnostic**: Generated from current grammar, automatically stays in sync
8. **Extensible structure**: Easy to add new sections (troubleshooting, advanced patterns, etc.)

### Drawbacks

1. **Large output**: Comprehensive reference may be 2000-5000 lines, consuming significant context
2. **Maintenance burden**: Examples and heuristics need manual updates as grammar evolves
3. **Duplication**: Some information duplicated from `bar help tokens` and skill docs
4. **Staleness risk**: Hardcoded examples may drift from best practices
5. **One-size-fits-all**: May include irrelevant information for specific use cases

### Mitigation Strategies

**For output size:**
- Implement filtering: `bar help llm --section tokens` or `bar help llm --axes method,form`
- Provide condensed mode: `bar help llm --compact` (tables only, no examples)
- LLMs can handle 5000 lines easily in modern contexts

**For maintenance:**
- Store examples in separate testdata files
- Add `make bar-help-llm-test` to verify examples still compile
- Include generation timestamp and grammar version in output
- Add comment: "<!-- Generated from grammar version X on YYYY-MM-DD -->"

**For duplication:**
- Treat `bar help llm` as the authoritative comprehensive reference
- Other help commands remain for human interactive use
- Skills should prefer `bar help llm` when available, fall back to `bar help tokens`

**For staleness:**
- Regular review cadence (quarterly)
- Link to example validation: examples must be valid `bar build` commands
- Version metadata helps users know if reference is outdated

### Impact on Existing Systems

**Bar skills:**
- **bar-autopilot**: Can load reference once per conversation for faster token discovery
- **bar-manual**: Can reference patterns section directly when teaching users
- **bar-workflow**: Can consult heuristics for multi-step planning
- **bar-suggest**: Can use example patterns to generate diverse options

**Backward compatibility:**
- Existing help commands unchanged
- Skills continue to work with `bar help tokens` if `bar help llm` unavailable
- Additive change only

### Success Metrics

- **Tool call reduction**: Bar skills should make 50-70% fewer discovery queries
- **Response quality**: Better token selection leading to more appropriate prompts
- **Adoption**: Bar skills updated to prefer `bar help llm` within one release cycle
- **Documentation**: Human developers reference `bar help llm` output in issues/PRs

## Alternatives Considered

### Alternative 1: Enhance `bar help tokens` output
- Add inline examples and heuristics to existing output
- **Rejected**: Would clutter the human-focused interactive help
- Breaks single-responsibility principle (discovery vs comprehensive reference)

### Alternative 2: Separate `bar reference` markdown file in repo
- Maintain static `docs/bar-llm-reference.md`
- **Rejected**: Requires manual sync with grammar changes
- Not guaranteed to be available where bar is installed
- Version drift between grammar and docs

### Alternative 3: Embed reference in skill SKILL.md files
- Expand bar-manual or bar-autopilot with full reference
- **Rejected**: Skills should be focused on behavior, not documentation
- Bloats skill files significantly
- Multiple skills would duplicate the same reference

### Alternative 4: JSON API endpoint
- `bar help llm --json` outputs structured JSON
- **Rejected**: Requires more LLM interpretation overhead
- Less readable for humans
- Can still be added later as `--format json` if needed

### Alternative 5: Interactive query mode
- `bar help llm "How do I build a decision prompt?"`
- Uses embedded LLM to answer specific questions
- **Rejected**: Requires embedding LLM or calling external API
- Adds complexity and latency
- Static comprehensive reference is simpler and faster

## Implementation Plan

### Phase 1: Core Implementation (First PR)
1. Create `internal/barcli/help_llm.go` with rendering logic
2. Implement `bar help llm` command handler in `app.go`
3. Generate basic structure: axes, tokens, ordering rules
4. Add 5-10 example patterns from `bar-pattern-reference.md`
5. Add token selection heuristics from bar-manual skill

### Phase 2: Enhancement (Follow-up PR)
1. Add filtering: `bar help llm --section <name>`
2. Add compact mode: `bar help llm --compact`
3. Categorize methods by thinking style
4. Expand examples to 15-20 patterns
5. Add persona preset table with spoken aliases

### Phase 3: Integration (Follow-up PR)
1. Update all four bar skills to use `bar help llm`
2. Modify SKILL.md files with new reference-based workflows
3. Implement fallback logic for older bar versions
4. Update skill behaviors to leverage integrated examples and heuristics
5. Remove redundant heuristics from SKILL.md (defer to reference)

See "Skill Updates" section below for detailed changes.

### Phase 4: Validation (Follow-up PR)
1. Create `make bar-help-llm-test` target
2. Validate all example commands are valid
3. Add version metadata to output
4. Document usage in main README

## Skill Updates

This section details how each of the four bar skills should be updated to leverage `bar help llm`.

### General Principles for All Skills

1. **Load reference once per conversation**: Call `bar help llm` early in the skill workflow, cache in context
2. **Fallback for older versions**: Check if `bar help llm` exists, fall back to `bar help tokens` if not
3. **Remove redundant documentation**: Defer token listings and heuristics to the reference
4. **Maintain version-agnostic approach**: Still use discovery, but with a single comprehensive query
5. **Improve token selection**: Leverage integrated examples and categorized methods

### Version Detection Pattern

All skills should detect `bar help llm` availability using this pattern:

```bash
# Check if bar help llm is available
bar help llm 2>/dev/null || bar help tokens
```

Or detect programmatically:
```bash
if bar help llm --version 2>/dev/null | grep -q "Bar CLI Reference"; then
    # Use new reference
    bar help llm
else
    # Fall back to legacy discovery
    bar help tokens
fi
```

### Skill 1: bar-autopilot Updates

**Location**: `.claude/skills/bar-autopilot/SKILL.md`

**Current Behavior**:
- Analyzes user request
- Runs `bar help tokens` to discover available tokens
- Selects appropriate tokens based on embedded heuristics
- Builds bar command
- Explains usage transparently

**Updated Behavior**:
1. **On first invocation**: Load `bar help llm` once and reference throughout conversation
2. **Token selection**: Consult "Usage Patterns by Task Type" section for similar examples
3. **Method selection**: Use categorized method tables (Decision/Understanding/Exploration/Diagnostic)
4. **Explanation**: Reference specific sections when explaining choices to users

**Specific SKILL.md Changes**:

**Before (Current Discovery Section)**:
```markdown
## Discovery Workflow
1. Run `bar help tokens` to discover all available tokens
2. Parse axes: static, completeness, scope, method, form, channel, directional
3. Use embedded heuristics to select tokens based on request type
```

**After (Updated Discovery Section)**:
```markdown
## Discovery Workflow

### With `bar help llm` (preferred):
1. Load `bar help llm` once at conversation start
2. Reference "Usage Patterns by Task Type" for similar use cases
3. Consult "Token Selection Heuristics" for guidance
4. Use "Token Catalog" for complete axis definitions
5. Check "Composition Rules" for constraints and ordering

### Fallback (legacy `bar help tokens`):
1. Run `bar help tokens` to discover all available tokens
2. Parse axes and use embedded heuristics for selection
```

**Performance Improvement**:
- **Before**: 2-3 tool calls per request (tokens, maybe filtered queries)
- **After**: 1 tool call per conversation (cached reference)
- **Reduction**: ~60-75% fewer tool calls

**New Heuristic References**:
```markdown
## Token Selection Strategy

Instead of embedding all heuristics in this skill, consult the bar reference:

1. **For user requests about decisions**: See "Usage Patterns > Decision-Making"
2. **For explanations**: See "Usage Patterns > Explanation/Understanding"
3. **For architecture**: See "Usage Patterns > Architecture Documentation"
4. **For diagnosis**: See "Usage Patterns > Problem Diagnosis"

The reference provides concrete examples for each pattern.
```

---

### Skill 2: bar-manual Updates

**Location**: `.claude/skills/bar-manual/SKILL.md`

**Current Behavior**:
- Teaches users how to manually build bar commands
- Runs `bar help tokens` to show available options
- Explains token selection through embedded heuristics
- Iterates with user to refine commands

**Updated Behavior**:
1. **Initial teaching**: Load `bar help llm` and show "Quick Start" section
2. **Token explanation**: Reference "Token Catalog" sections directly
3. **Examples**: Point users to "Usage Patterns by Task Type" for similar use cases
4. **Iteration**: Use "Token Selection Heuristics" to guide refinement

**Specific SKILL.md Changes**:

**Before (Current Teaching Workflow)**:
```markdown
## Teaching Workflow
1. Ask user what they want to accomplish
2. Run `bar help tokens` to show available tokens
3. Explain token selection using examples:
   - For decisions: scope=thing, method=branch, form=variants
   - For understanding: scope=time, method=flow, form=walkthrough
   [... many embedded examples ...]
4. Build command iteratively
5. Offer `bar shuffle` for exploration
```

**After (Updated Teaching Workflow)**:
```markdown
## Teaching Workflow

### With `bar help llm` (preferred):
1. Ask user what they want to accomplish
2. Load `bar help llm` reference (cache for conversation)
3. Show relevant "Usage Patterns by Task Type" section:
   - Match user's goal to pattern category
   - Show example from reference
   - Explain token choices from the example
4. Guide user to customize tokens using "Token Catalog"
5. Reference "Composition Rules" if user violates constraints
6. Offer `bar shuffle` for exploration

### Fallback (legacy):
[Keep existing embedded heuristics for users with older bar versions]
```

**Remove Redundant Content**:
- Delete embedded token selection heuristics (scope/method/form tables)
- Delete example patterns (defer to reference "Usage Patterns")
- Keep only high-level workflow and teaching philosophy

**Performance Improvement**:
- **Before**: 3-5 tool calls (tokens, filtered queries, maybe patterns)
- **After**: 1 tool call per conversation
- **Reduction**: ~70-80% fewer tool calls
- **Bonus**: Users see richer examples from integrated reference

---

### Skill 3: bar-workflow Updates

**Location**: `.claude/skills/bar-workflow/SKILL.md`

**Current Behavior**:
- Builds multi-step bar command sequences
- Discovers tokens with `bar help tokens`
- Plans progressive refinement workflows
- Chains commands where output informs next step

**Updated Behavior**:
1. **Workflow planning**: Load `bar help llm` to understand full token space
2. **Sequence design**: Reference "Usage Patterns" to identify complementary commands
3. **Progressive refinement**: Use heuristics to choose broadening vs focusing tokens
4. **Integration**: Leverage "Token Catalog" categorizations for method chaining

**Specific SKILL.md Changes**:

**Before (Current Workflow Planning)**:
```markdown
## Multi-Step Planning
1. Discover tokens with `bar help tokens`
2. Identify initial command (typically broad scope + exploratory method)
3. Plan follow-up commands (narrow scope + specific method)
4. Pattern examples:
   - Discovery → Focus: `explore` then `mapping`
   - Understand → Act: `flow` then `diagnose`
   [... embedded workflow patterns ...]
```

**After (Updated Workflow Planning)**:
```markdown
## Multi-Step Planning

### With `bar help llm` (preferred):
1. Load `bar help llm` reference once
2. Consult "Usage Patterns by Task Type" for end-to-end examples
3. Use "Method" categorization to identify complementary thinking modes:
   - Start with Exploration Methods (explore, diverge, survey)
   - Progress to Understanding Methods (mapping, flow, structure)
   - Conclude with Decision Methods (branch, compare, prioritize)
4. Reference "Token Selection Heuristics" for scope evolution
5. Check "Composition Rules" for valid multi-step sequences

### Workflow Pattern Examples
See reference section "Usage Patterns by Task Type" for:
- Architecture exploration workflows
- Problem diagnosis sequences
- Decision-making progressions

### Fallback (legacy):
[Keep embedded workflow patterns for older bar versions]
```

**New Integration Pattern**:
```markdown
## Method Chaining Strategy

The `bar help llm` reference categorizes methods by thinking style:
- **Exploration** (divergent): explore, survey, variants
- **Understanding** (analysis): mapping, flow, structure
- **Decision** (convergent): branch, compare, prioritize
- **Diagnostic** (root cause): diagnose, failure, stress

Effective workflows often progress through these stages:
1. Explore (broad, divergent)
2. Understand (structure, relationships)
3. Decide or Diagnose (specific, convergent)
```

**Performance Improvement**:
- **Before**: 2-4 tool calls per workflow design
- **After**: 1 tool call per conversation
- **Reduction**: ~60-75% fewer tool calls
- **Bonus**: Better workflow design through categorized methods

---

### Skill 4: bar-suggest Updates

**Location**: `.claude/skills/bar-suggest/SKILL.md`

**Current Behavior**:
- Detects ambiguous user requests
- Discovers tokens with `bar help tokens`
- Generates 2-4 distinct bar-based approach options
- Presents options with trade-off explanations using AskUserQuestion

**Updated Behavior**:
1. **Option generation**: Load `bar help llm` to see full pattern space
2. **Diversity**: Use "Usage Patterns" to generate distinct approaches
3. **Trade-off explanation**: Reference "Token Catalog" descriptions for clarity
4. **Cross-axis variation**: Leverage categorized methods to create truly different options

**Specific SKILL.md Changes**:

**Before (Current Option Generation)**:
```markdown
## Option Generation
1. Run `bar help tokens` to discover available tokens
2. Identify multiple valid approaches by varying:
   - Scope (thing vs struct vs time)
   - Method (branch vs explore vs mapping)
   - Form (table vs bullets vs walkthrough)
3. Ensure options are meaningfully different
4. Explain trade-offs using token descriptions
```

**After (Updated Option Generation)**:
```markdown
## Option Generation

### With `bar help llm` (preferred):
1. Load `bar help llm` reference once
2. Consult "Usage Patterns by Task Type" for established patterns
3. Generate 2-4 distinct options by:
   - Varying pattern categories (Decision vs Exploration vs Diagnostic)
   - Mixing method categories (see Method categorization)
   - Using different form structures (actions vs walkthrough vs table)
4. Reference "Token Catalog" descriptions to explain trade-offs
5. Optionally show similar examples from "Usage Patterns"

Example option diversity:
- **Option 1** (Exploration): explore + diverge + variants
- **Option 2** (Understanding): mapping + structure + table
- **Option 3** (Decision): branch + compare + checklist
- **Option 4** (Diagnostic): diagnose + failure + actions

### Fallback (legacy):
[Keep existing token-based variation logic]
```

**Enhanced Option Presentation**:
```markdown
## Presenting Options with Examples

When using `bar help llm`, enhance AskUserQuestion with:
1. **Option label**: Concise approach name (e.g., "Exploratory Survey")
2. **Description**:
   - Token selection with reasoning
   - Reference to similar pattern from "Usage Patterns"
   - Expected output characteristics
3. **Example command**: Show complete bar build command

This gives users concrete context for choosing.
```

**Performance Improvement**:
- **Before**: 2-3 tool calls per suggestion request
- **After**: 1 tool call per conversation
- **Reduction**: ~60-75% fewer tool calls
- **Bonus**: More diverse options through method categorization

---

### Cross-Skill Integration Changes

**Shared Reference Caching**:
All skills should detect if `bar help llm` output already exists in conversation context:

```markdown
## Reference Loading

Before calling `bar help llm`, check if another skill has already loaded it:
1. Search conversation history for "Bar CLI Reference for LLMs"
2. If found, reuse existing reference
3. If not found, load with `bar help llm`

This prevents duplicate loading when multiple skills run in same conversation.
```

**Consistent Fallback Pattern**:
```markdown
## Version Compatibility

All bar skills support both new and legacy bar versions:

**With `bar help llm`** (bar >= v0.XX):
- Single comprehensive reference load
- Access to integrated examples and heuristics
- Categorized method tables
- Complete composition rules

**Without `bar help llm`** (bar < v0.XX):
- Fall back to `bar help tokens`
- Use embedded heuristics from SKILL.md
- Gracefully degrade functionality
- Still fully operational
```

---

### Documentation Updates

**Each SKILL.md should add**:

```markdown
## Using the Bar Reference

This skill leverages `bar help llm` for comprehensive bar grammar information.

The reference includes:
- **Token Catalog**: All axes with descriptions and use cases
- **Usage Patterns by Task Type**: 15-20 concrete examples
- **Token Selection Heuristics**: Guidance for choosing tokens
- **Composition Rules**: Ordering, caps, incompatibilities
- **Examples from Real Usage**: Complete request-to-command flows

### Performance
- **New approach**: 1 reference load per conversation (~2500 lines)
- **Legacy approach**: 3-5 discovery queries per invocation
- **Tool call reduction**: ~70% fewer queries

### Version Requirements
- **Recommended**: bar >= v0.XX (with `bar help llm`)
- **Minimum**: bar >= v0.XX (falls back to `bar help tokens`)
```

---

### Summary of Changes Per Skill

| Skill | Current Tool Calls | Updated Tool Calls | Key Improvements |
|-------|-------------------|-------------------|------------------|
| **bar-autopilot** | 2-3 per request | 1 per conversation | Token selection from examples, categorized methods |
| **bar-manual** | 3-5 per teaching session | 1 per conversation | Richer examples, integrated patterns, less repetition |
| **bar-workflow** | 2-4 per workflow | 1 per conversation | Better chaining through method categories |
| **bar-suggest** | 2-3 per suggestion | 1 per conversation | More diverse options from pattern space |

**Overall Impact**:
- **~70% reduction** in discovery-related tool calls
- **Faster skill execution** due to cached comprehensive reference
- **Better token selection** through integrated examples
- **Consistent behavior** across all skills using same reference
- **Maintained backward compatibility** with legacy bar versions

---

## References

- ADR 0068: Grammar Token Normalization for CLI
- ADR 0097: Bar Install-Skills Command
- `docs/bar-pattern-reference.md`: Existing pattern documentation
- `.claude/skills/bar-manual/SKILL.md`: Token selection heuristics
- `.claude/skills/bar-autopilot/SKILL.md`: Discovery-based approach
- `internal/barcli/grammar.go`: Grammar structure and loading

## Notes

- Consider adding `bar help llm --examples-only` for quick pattern reference
- Future: Generate reference as part of CI/CD and publish to docs site
- Future: Add troubleshooting section for common composition errors
- Future: Include token co-occurrence statistics from usage logs
- Consider adding shell variable: `BAR_LLM_REF=$(bar help llm)` for fast caching
