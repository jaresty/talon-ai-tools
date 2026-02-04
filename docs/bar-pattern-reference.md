# Bar Pattern Reference

This document contains example patterns discovered through bar usage. These are **reference examples only** - not prescriptive templates. Bar skills should discover tokens dynamically and explore new combinations rather than relying on these patterns.

## About This Reference

- **Purpose**: Preserve useful discovered patterns for human reference
- **Not for skill encoding**: Bar skills should NOT hardcode these patterns
- **Discovery-first**: Always use `bar help tokens` to discover current available tokens
- **Version-specific**: These examples may use tokens from a specific bar version
- **Exploration encouraged**: Use `bar shuffle` to find novel combinations beyond these examples

## Common Request Types and Example Patterns

These patterns were discovered through usage and may inspire approaches, but **should not be treated as the only valid approaches**.

### Decision-Making

Example discovered patterns for helping decide between options:

```bash
# Example 1: Using discovered tokens for comparison
bar help tokens scope method form
bar build <scope-about-entities> full <method-about-branching> <form-about-variants>

# Example 2: Using key=value for specific needs
bar build <discovered-scope> full method=<comparison-method> form=<variant-form>
```

**Why these might work**: Decisions often benefit from comparing alternatives, so looking for method tokens related to branching/comparison and form tokens about variants/options can be effective.

### Architecture Documentation (ADRs)

Example patterns for documenting decisions:

```bash
# Explore available tokens first
bar help tokens scope method form

# Example pattern discovered
bar build <planning-scope> full <action-scope> <exploration-method> <case-form>
```

**Why this might work**: ADRs typically need to make a case for a decision, so case-building forms combined with exploratory methods can work well.

### Explanation and Understanding

Example patterns for explaining concepts:

```bash
# For "how it works" type questions
bar help tokens scope method form
bar build <time-scope> full <flow-method> <walkthrough-form>

# For "what it means" type questions
bar build <meaning-scope> full <scaffold-form>
```

**Why these might work**: Process explanations often benefit from sequential/flow thinking, while conceptual understanding benefits from scaffolded learning.

### Structural Analysis

Example patterns for understanding organization:

```bash
bar help tokens scope method
bar build <structure-scope> full <mapping-method>
```

**Why this might work**: Analyzing architecture often benefits from mapping relationships and structure.

## Multi-Step Workflow Examples

These are examples of discovered workflow sequences, not prescriptive recipes:

### Three-Step Exploration Pattern

```bash
# Step 1: Understand current state
bar build <discovered-scope-1> full <analysis-method> --prompt "..."

# Step 2: Explore possibilities
bar build <discovered-scope-2> full <exploration-method> --prompt "..."

# Step 3: Plan action
bar build <action-scope> full <planning-method> --prompt "..."
```

**Why this might work**: Moving from understanding → exploration → planning is a common problem-solving progression.

## Discovery Techniques

Instead of memorizing patterns, use these techniques to discover new ones:

### Technique 1: Token Exploration
```bash
# Discover what's available
bar help tokens scope method form

# Pick based on request characteristics, not memorized patterns
# - What aspect does the request focus on? → Pick scope
# - How should I think about it? → Pick method
# - How should output be structured? → Pick form
```

### Technique 2: Shuffle-Based Discovery
```bash
# Generate alternatives
bar shuffle

# Constrain to specific axes
bar shuffle --include scope,method

# Fix certain elements
bar shuffle --exclude persona --fill 0.8
```

### Technique 3: Iterative Refinement
```bash
# Start with discovered basics
bar build <scope> full <method>

# Refine based on results
bar build <scope> full method=<different-method> form=<specific-form>

# Use //next to skip stages if needed
bar build //next <scope> full <method>
```

## Anti-Patterns to Avoid

- **Memorizing token combinations**: Always discover tokens for current bar version
- **Copying examples without understanding**: Understand why a pattern might work
- **Ignoring shuffle**: `bar shuffle` can discover better combinations than memorized patterns
- **Encoding patterns in skills**: Skills should use heuristics, not hardcoded patterns
- **Assuming tokens are stable**: Token sets evolve across bar versions

## How to Use This Reference

1. **As inspiration, not prescription**: These show what's possible, not what's required
2. **Verify tokens exist**: Always run `bar help tokens` to confirm tokens are available
3. **Experiment freely**: Try combinations not listed here
4. **Document discoveries**: Add new useful patterns you discover
5. **Prefer discovery**: Use skills' discovery mechanisms over consulting this reference

## Contributing Patterns

When you discover a useful new pattern:

1. Note what request type it addressed
2. Explain why the token combination was effective
3. Document as an example, not a rule
4. Encourage experimentation with variations
