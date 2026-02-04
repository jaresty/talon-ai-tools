# Bar Workflow Skill

## Purpose and Preconditions

This skill enables Claude to **build and execute multi-step bar command sequences** for complex tasks that require multiple perspectives or progressive refinement.

Assumes:
- `bar` CLI is installed and accessible
- The LLM can run `bar help tokens` to discover available tokens
- The LLM has access to the Bash tool for executing bar commands

## High-level Workflow

1. **Identify complex request** requiring multiple perspectives
2. **Plan workflow sequence** (e.g., probe → explore → plan)
3. **Execute bar commands in sequence**, using output of each to inform the next
4. **Synthesize results** into comprehensive response

## Skill Behavior Rules

- **Chain commands thoughtfully.** Each step should build on the previous one.
- **Never hardcode tokens.** Always discover dynamically via `bar help tokens`.
- **Use kebab-case for multi-word tokens.** When tokens contain spaces, convert to kebab-case (e.g., "dip bog" → "dip-bog", "fly rog" → "fly-rog"). Bar will show the canonical slug in help output.
- **Use progressive refinement.** Start broad, then narrow focus.
- **Be transparent about usage.** After completing a workflow, explain the sequence of bar commands used and why each step was chosen to aid user learning.
- **Cross-agent compatible.** Works across all Claude agent types.
- **Graceful degradation.** If workflow fails mid-sequence, return partial results.

## Workflow Construction Heuristics

When a complex request requires multiple perspectives, build a multi-step workflow:

### Step 1: Discover Available Tokens
```bash
bar help tokens scope method
bar help tokens form
```

**Grammar note:** Token order is: persona → static → completeness → scope (1-2) → method (1-3) → form → channel → directional. See bar-manual skill for complete grammar details.

### Step 2: Plan Workflow Sequence

Identify which aspects the request needs to explore. Common progressions:

**Broadening then focusing:**
- Start with discovery/exploration method tokens
- Move to analysis/mapping method tokens
- End with planning/action-oriented tokens

**Understanding then acting:**
- Begin with "what it means" scope tokens
- Progress to "how it's structured" scope tokens
- Conclude with "what to do" scope tokens

**Diagnosis then solution:**
- Start with current state analysis
- Explore failure modes or constraints
- End with remediation approaches

### Step 3: Freeform Discovery

If the request doesn't fit common progressions:
- Use `bar shuffle` to generate alternative token combinations
- Constrain with `--include scope,method` to keep structure while varying specifics
- Try different scope progressions based on discovered tokens
- Experiment with method combinations that complement each other

### Step 4: Execute Sequence and Explain

1. Run each bar command in sequence
2. Use output from each step to inform the next
3. After completion, explain: "I used a [N]-step workflow: [step 1 tokens] to [reason], then [step 2 tokens] to [reason], etc."

## Cross-Agent Compatibility Notes

- Works with all Claude agent types
- Explore agent benefits most from workflow structuring
- Plan agent can use workflows to enhance planning depth
- Token discovery ensures bar version compatibility

## Error Handling

- If any workflow step fails: Log error, continue with partial results
- If bar unavailable: Fall back to single-step autopilot or normal response
- Always prefer partial results over complete failure
