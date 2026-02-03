# Bar Autopilot Skill

## Purpose and Preconditions

This skill enables Claude to **automatically detect when a user request benefits from bar structuring** and apply it proactively. The skill teaches Claude to use bar as a thinking tool to structure better responses without requiring the user to know about bar.

Assumes:
- `bar` CLI is installed and accessible
- The LLM can run `bar help tokens` to discover available tokens
- The LLM has access to the Bash tool for executing bar commands

## High-level Workflow

1. **Analyze user request** for implicit structure needs
2. **Discover tokens** dynamically via `bar help tokens` (never hardcode)
3. **Build appropriate bar command** based on request type
4. **Execute bar command** and use output as prompt structure
5. **Return well-structured response** to user

## Skill Behavior Rules

- **Never hardcode tokens.** Always run `bar help tokens` or sectioned variants to discover current available tokens.
- **Be version-agnostic.** Tokens evolve; discover them dynamically.
- **Work proactively.** Users should not need to ask for bar structuring.
- **Graceful degradation.** If bar is unavailable, fall back to normal responses.
- **Cross-agent compatible.** Must work across all Claude agent types (general-purpose, Explore, Plan, etc.).
- **Use Bash tool.** Execute bar commands via the Bash tool.
- **Parse output reliably.** Extract the prompt structure from bar's output.

## Trigger Patterns and Mappings

When user request matches these patterns, automatically apply bar structuring:

### Decision-Making Requests
**Patterns:**
- "Help me decide between X and Y"
- "Which should I choose: X or Y?"
- "What's the best approach for..."

**Bar command template:**
```bash
bar build pick full thing method=branch form=variants --prompt "<user request>"
```

### ADR Writing
**Patterns:**
- "Write an ADR for..."
- "Create an architecture decision record..."
- "Document this decision..."

**Bar command template:**
```bash
bar build plan full act method=explore form=case channel=adr --prompt "<user request>"
```

### Option Exploration
**Patterns:**
- "Explore options for..."
- "What are the different ways to..."
- "Show me alternatives for..."

**Bar command template:**
```bash
bar build probe full thing method=explore form=variants --prompt "<user request>"
```

### Explanation Requests (How it works)
**Patterns:**
- "Explain how X works"
- "How does Y function?"
- "Walk me through..."

**Bar command template:**
```bash
bar build show full time method=flow form=walkthrough --prompt "<user request>"
```

### Explanation Requests (What it means)
**Patterns:**
- "What is X?"
- "What does Y mean?"
- "Explain the concept of..."

**Bar command template:**
```bash
bar build show full mean form=scaffold --prompt "<user request>"
```

### Structural Analysis
**Patterns:**
- "Analyze the architecture of..."
- "Show me the structure of..."
- "How is X organized?"

**Bar command template:**
```bash
bar build probe full struct method=mapping --prompt "<user request>"
```

## Cross-Agent Compatibility Notes

- Works with general-purpose agent (main Claude)
- Works with Explore agent (adds structure to exploration)
- Works with Plan agent (enhances planning with bar structure)
- Token discovery ensures compatibility across bar versions

## Error Handling

- If `bar` command not found: Log warning, fall back to normal response
- If `bar help tokens` fails: Fall back to normal response
- If bar command fails: Log error, fall back to normal response
- Always prefer graceful degradation over blocking the user
