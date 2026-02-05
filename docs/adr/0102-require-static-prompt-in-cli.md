# ADR 0102: Require Static Prompt in Go CLI

## Status

Implemented

## Date

2026-02-05

## Context

The bar CLI grammar is designed around a fundamental principle established in ADR 0083: **"TASK: The primary action to perform. This defines success."** The static prompt (task) is the single most important axis because it explicitly defines what constitutes a successful response.

ADR 0086 previously allowed empty static prompts to support "open-ended responses when no task is specified," with the rationale that "the task catalog doesn't cover all possible definitions of success." This design decision created two significant problems in practice:

### Problem 1: LLM-Generated Recipes Skip the Task Definition

When LLM agents (particularly those in bar skills) generate bar commands programmatically, they frequently omit the static prompt, producing commands like:

```bash
bar build full code --prompt "implement user authentication"
```

Instead of:

```bash
bar build make full code --prompt "implement user authentication"
```

This happens because:
1. **Optional = skippable**: LLMs treat optional parameters as lower priority
2. **Implicit task inference**: LLMs assume the prompt text implies the task
3. **Token minimization**: LLMs prefer shorter commands when possible
4. **Gradient descent**: Training data likely includes many prompts without explicit task framing

### Problem 2: Reduced Skill Quality

When static prompts are omitted, the resulting prompts lose critical clarity:

- **Ambiguous success criteria**: Without an explicit task (make, fix, show, etc.), the LLM must infer what success means
- **Inconsistent output**: Same prompt text produces different results based on LLM interpretation
- **Lost composability**: The grammar's power comes from explicit task definition combined with constraints
- **Weaker guardrails**: Constraints like "code" or "full" have less effect without a clear task anchor

**Example of quality degradation:**

```bash
# Without static prompt (ambiguous):
bar build code --prompt "handle auth errors"
→ Could mean: make new code, fix existing code, show how to handle errors, probe error patterns

# With static prompt (explicit):
bar build make code --prompt "handle auth errors"
→ Clearly: create new error handling code
```

### Current State

- Default static prompt: `""` (empty string per ADR 0086)
- Grammar allows builds without static prompts
- No validation enforcing static prompt presence
- Skills frequently produce commands without static prompts

## Decision

**Require static prompt validation in the Go CLI build process.**

The CLI will reject any build command that does not include an explicit static prompt, returning a clear error message listing all available static prompts with descriptions.

### Implementation

1. **Add validation in `build.go:finalise()`**
   - Check if `state.static == ""`
   - Return `errorMissingStatic` with helpful error message
   - List all available static prompts from grammar
   - Show example usage

2. **Update help documentation**
   - Change `app.go` token order from `(0..1 tokens, default: open-ended)` to `(REQUIRED: 1 token)`
   - Update `promptGrammar.py` comments to note requirement

3. **Error message format**
   ```
   error: static prompt (task) is required

   Available static prompts:
     make - The response creates new content...
     fix - The response changes the form or presentation...
     pull - The response selects or extracts...
     [all 11 static prompts with descriptions]

   Example: bar build make full code <prompt>
   ```

### Affected Components

- `internal/barcli/build.go`: Add validation
- `internal/barcli/app.go`: Update help text
- `lib/promptGrammar.py`: Update comments

### Migration Path

This is a **breaking change** for:
- Commands using `bar build --prompt "text"` without a static prompt
- Skills that omit static prompts in generated commands

Migration:
- Users must add an explicit static prompt to their commands
- Skills will fail on first invocation, forcing correction
- Error message provides clear guidance on valid options

## Rationale

### Why This Improves Quality

1. **Forces task clarity**: Every prompt must define what success means
2. **Consistent LLM behavior**: Skills must explicitly state the task
3. **Aligns with ADR 0083**: Reinforces "task defines success" principle
4. **Better error detection**: Missing tasks caught early rather than producing ambiguous output
5. **Clearer composition**: Constraints make sense in context of explicit task

### Why the ADR 0086 Rationale No Longer Applies

ADR 0086 justified empty static prompts with: *"the current task catalog doesn't cover all possible definitions of success."*

Counter-argument:
- The 11 static prompts (make, fix, pull, sort, diff, show, probe, pick, plan, sim, check) cover the vast majority of use cases
- When task is truly ambiguous, users can use `show` or `probe` as general-purpose options
- Forcing explicit task selection improves prompt quality more than allowing "open-ended" helps edge cases
- Skills can dynamically choose the appropriate task rather than omitting it entirely

### Trade-offs

**Pros:**
- ✅ Significantly improves skill-generated prompt quality
- ✅ Enforces grammar's core design principle
- ✅ Reduces ambiguity and improves consistency
- ✅ Clear, helpful error messaging guides users
- ✅ Makes task selection a first-class decision

**Cons:**
- ❌ Breaking change requires migration
- ❌ Slightly more verbose commands (one extra token)
- ❌ Removes flexibility for truly open-ended use cases

The quality improvement for LLM-generated commands outweighs the inconvenience of requiring one additional token.

## Consequences

### Positive

- Skills will produce higher-quality bar commands with explicit task definitions
- Users receive clearer guidance on available tasks via error messages
- Grammar usage aligns with its foundational design principles
- Prompt composition becomes more intentional and less ambiguous

### Negative

- Existing workflows using `bar build --prompt "text"` will break
- Requires one-time update to all skills that generate bar commands
- Removes (rarely used) ability to have completely open-ended prompts

### Neutral

- Grammar exports still include empty default for schema compatibility
- Python side unchanged (validation only in Go CLI)
- Completion and TUI behavior unchanged (they already guide users to select static prompt)

## Validation

### Functional Testing

```bash
# Should fail with clear error
bar build --prompt "test"
bar build full code --prompt "test"

# Should succeed
bar build make --prompt "test"
bar build fix full code --prompt "test"
```

### Regression Testing

```bash
# All existing tests should pass
go test ./internal/barcli/...
go test ./...
```

### Error Message Quality

Validate that error message:
- ✅ Clearly states static prompt is required
- ✅ Lists all 11 available static prompts with descriptions
- ✅ Provides concrete example usage
- ✅ Uses `errorMissingStatic` error type for programmatic detection

## References

- **ADR 0083**: Prompt Key Refinement (defines "task defines success" principle)
- **ADR 0086**: Catalog Refinements (introduced empty static prompt default)
- **Implementation**: Commit superseding ADR 0086 Section 1 decision
- **Error format**: Follows ADR 0101 pattern for helpful error messages

## Alternatives Considered

### Alternative 1: Warn Instead of Error

Show warning but allow build to proceed with empty static prompt.

**Rejected because:**
- Warnings are easily ignored by automated systems
- Doesn't solve the core problem of LLMs omitting static prompts
- Produces same quality degradation issues

### Alternative 2: Infer Task from Prompt Text

Automatically detect task intent from prompt text and select appropriate static prompt.

**Rejected because:**
- Fragile and error-prone (requires NLP or heuristics)
- Violates explicitness principle
- Hidden magic reduces user understanding
- Debugging becomes harder ("why did it choose 'fix' instead of 'make'?")

### Alternative 3: Add "open" Static Prompt

Add a new static prompt called "open" for explicitly open-ended tasks.

**Rejected because:**
- Doesn't solve the omission problem (LLMs would still skip it)
- "show" and "probe" already serve this purpose
- Adds token without clear semantic value
- Task should be specific, not explicitly non-specific

### Alternative 4: Default to "show"

When static prompt omitted, default to `show` task.

**Rejected because:**
- Implicit behavior reduces clarity
- "show" may not be appropriate for all prompts
- Better to force explicit choice than guess
- Doesn't teach users/LLMs the correct pattern

## Success Metrics

After implementation:

1. **Skill quality**: Skills generate commands with explicit static prompts 100% of the time
2. **User feedback**: Error message provides clear guidance (measured by reduction in "what task should I use?" support questions)
3. **Consistency**: Prompts with same text but different static prompts produce appropriately different outputs
4. **Adoption**: Skills update their command generation within one iteration after encountering error

## Implementation Checklist

- [x] Add validation in `build.go:finalise()`
- [x] Update help text in `app.go`
- [x] Update comments in `promptGrammar.py`
- [x] Verify all tests pass
- [x] Test error message format
- [x] Create work log documenting implementation loops
- [ ] Update skills documentation if needed
- [ ] Monitor skill behavior after deployment
