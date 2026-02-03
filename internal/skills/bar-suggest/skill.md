# Bar Suggest Skill

## Purpose and Preconditions

This skill enables Claude to **present users with bar-based choices** for how to approach their request when multiple valid approaches exist.

Assumes:
- `bar` CLI is installed and accessible
- The LLM can run `bar help tokens` to discover available tokens
- The LLM has access to the Bash tool for executing bar commands
- The LLM can use AskUserQuestion tool for presenting choices

## High-level Workflow

1. **Detect open-ended or ambiguous request**
2. **Discover relevant tokens** via `bar help tokens`
3. **Generate 2-4 distinct bar command options** representing different approaches
4. **Present options** to user with plain-language descriptions
5. **Execute user's choice** and return structured response

## Trigger Patterns

When user request is:
- **Open-ended** - "Help me understand our authentication system"
- **Ambiguous goal** - "Improve the caching layer"
- **Multiple valid frames** - "Explain microservices"
- **Exploration request** - "Tell me about event-driven architecture"

## Option Generation Logic

For each trigger, generate 2-4 options by varying:
- **Scope** (thing, struct, time, mean, act, view, fail, good)
- **Method** (explore, analysis, mapping, flow, branch, etc.)
- **Form** (bullets, walkthrough, variants, table, visual)

## Integration with Other Skills

- **bar-autopilot** makes choice automatically
- **bar-suggest** presents options to user
- **bar-workflow** executes multi-step sequences

**Decision logic:**
- If request has single obvious framing → use bar-autopilot
- If request is ambiguous or open-ended → use bar-suggest
- If request is complex multi-faceted task → use bar-workflow

## Cross-Agent Compatibility Notes

- Works with all Claude agent types
- AskUserQuestion tool must be available
- If AskUserQuestion unavailable, fall back to bar-autopilot with best guess
- Token discovery ensures bar version compatibility

## Error Handling

- If bar unavailable: Present options conceptually without bar structure
- If token discovery fails: Use common patterns from memory
- Always prefer showing options over guessing user's intent
