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

## Common Workflow Patterns

### Feature Design Workflow
**Trigger:** "Design a new feature for..."

**Sequence:**
1. Probe structure - Understand current system
2. Explore options - Survey approaches
3. Plan implementation - Concrete steps

### Architecture Analysis Workflow
**Trigger:** "Analyze the architecture of..."

**Sequence:**
1. Probe meaning - Understand purpose
2. Show structure - Map components
3. Identify risks - Find weaknesses

### Refactoring Workflow
**Trigger:** "Refactor this system..."

**Sequence:**
1. Probe current state - Understand existing code
2. Explore approaches - Consider options
3. Plan migration - Create steps

## Cross-Agent Compatibility Notes

- Works with all Claude agent types
- Explore agent benefits most from workflow structuring
- Plan agent can use workflows to enhance planning depth
- Token discovery ensures bar version compatibility

## Error Handling

- If any workflow step fails: Log error, continue with partial results
- If bar unavailable: Fall back to single-step autopilot or normal response
- Always prefer partial results over complete failure
