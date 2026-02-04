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
- **Use kebab-case for multi-word tokens.** When tokens contain spaces (e.g., "as kent beck", "to junior engineer"), convert to kebab-case: "as-kent-beck", "to-junior-engineer". Bar will show the canonical slug in help output.
- **Work proactively.** Users should not need to ask for bar structuring.
- **Be transparent about usage.** After using bar, briefly explain which command you used and why it fits the request type to aid user learning.
- **Graceful degradation.** If bar is unavailable, fall back to normal responses.
- **Cross-agent compatible.** Must work across all Claude agent types (general-purpose, Explore, Plan, etc.).
- **Use Bash tool.** Execute bar commands via the Bash tool.
- **Parse output reliably.** Extract the prompt structure from bar's output.

## Token Selection Heuristics

When a user request benefits from bar structuring, discover available tokens and select based on these characteristics:

### Step 1: Discover Current Tokens
Always begin by discovering what tokens are available in this version of bar:
```bash
bar help tokens scope method
bar help tokens form
# Add persona tokens if the request involves specific audience or voice
bar help tokens persona
```

**Grammar note:** Token order is: persona → static → completeness → scope (1-2) → method (1-3) → form → channel → directional. See bar-manual skill for complete grammar details.

### Step 2: Choose Scope Based on Request Focus

Analyze what aspect the request centers on:
- **Entities and boundaries** → Look for scope tokens related to "what exists"
- **Relationships and organization** → Look for scope tokens related to "how things connect"
- **Sequence and change** → Look for scope tokens related to "when things happen"
- **Understanding and framing** → Look for scope tokens related to "what it means"
- **Tasks and intentions** → Look for scope tokens related to "what to do"
- **Perspectives and viewpoints** → Look for scope tokens related to "from whose view"
- **Quality and success criteria** → Look for scope tokens related to "what makes it good"
- **Failure modes and limits** → Look for scope tokens related to "where it breaks"

### Step 3: Choose Method Based on Request Type

Analyze how the request wants you to think:
- **Deciding between options** → Look for method tokens about branching, comparing, or evaluating alternatives
- **Understanding architecture** → Look for method tokens about mapping, structure, or relationships
- **Explaining processes** → Look for method tokens about flow, sequence, or progression
- **Finding problems** → Look for method tokens about diagnosis, failure, or stress-testing
- **Exploring possibilities** → Look for method tokens about generation, survey, or divergence
- **Building cases** → Look for method tokens about argumentation, evidence, or reasoning
- **Learning concepts** → Look for method tokens about scaffolding, building understanding

### Step 4: Choose Form Based on Desired Output

Analyze how the response should be structured:
- **Actionable next steps** → Look for form tokens about actions, checklists, or tasks
- **Multiple alternatives** → Look for form tokens about variants, options, or comparison
- **Step-by-step guidance** → Look for form tokens about walkthroughs, recipes, or flows
- **Structured comparison** → Look for form tokens about tables or side-by-side layout
- **Building understanding** → Look for form tokens about scaffolding, gradual explanation
- **Decision documentation** → Look for form tokens about cases, arguments, or rationale

### Step 5: Freeform Discovery

If the request doesn't clearly match the heuristics above:
- Use `bar shuffle` to explore alternative token combinations
- Examine the shuffled output and select what resonates with the request
- Constrain shuffle with `--include` or `--exclude` to focus on relevant axes
- Use `--seed` for reproducible exploration if needed

### Step 6: Execute and Explain

After discovering tokens and selecting appropriate ones:
1. Build the bar command with chosen tokens
2. Execute it to structure your response
3. Briefly explain to the user: "I used `bar build [tokens]` to structure this response around [reason]"

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
