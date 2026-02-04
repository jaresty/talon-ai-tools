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

## Skill Behavior Rules

- **Present options, don't choose.** Let user decide the approach.
- **Never hardcode tokens.** Discover dynamically via `bar help tokens`.
- **Use kebab-case for multi-word tokens.** When tokens contain spaces, convert to kebab-case (e.g., "as kent beck" → "as-kent-beck", "to product manager" → "to-product-manager"). Bar will show the canonical slug in help output.
- **Keep options distinct.** Each option should represent meaningfully different approach.
- **Explain trade-offs.** Help user understand what each option emphasizes.
- **Use AskUserQuestion tool.** Present choices using Claude's question interface.
- **Be transparent about usage.** After executing the user's choice, explain which bar command you used and why it aligns with their selection.
- **Execute chosen option.** After user selects, run the bar command and structure response.

## Option Generation Heuristics

### Step 1: Detect When to Offer Choices

Use bar-suggest when the request is:
- **Open-ended** - No specific output format or approach specified
- **Ambiguous** - Multiple valid ways to interpret or approach the task
- **Exploratory** - User wants to understand something but unclear what aspect matters most
- **Multi-faceted** - Topic can be analyzed from several distinct angles

### Step 2: Discover Available Tokens
```bash
bar help tokens scope method
bar help tokens form
```

**Grammar note:** Token order is: persona → static → completeness → scope (1-2) → method (1-3) → form → channel → directional. See bar-manual skill for complete grammar details.

### Step 3: Generate Distinct Options

Create 2-4 options by varying the tokens to create meaningfully different approaches:

**Vary by scope** - Different aspects to focus on:
- One option might focus on "what it means"
- Another on "how it's structured"
- Another on "how it evolves over time"

**Vary by method** - Different ways of thinking:
- One option using exploratory/discovery methods
- Another using analytical/diagnostic methods
- Another using flow/sequential methods

**Vary by form** - Different output structures:
- One as bullets for quick scanning
- Another as walkthrough for deep understanding
- Another as variants/options if multiple approaches exist

### Step 4: Include Freeform Option

Always include as one option:
- **"Surprise me"** or **"Explore freely"** - Use `bar shuffle` to generate an unexpected but valid combination
- Explain this allows bar to discover novel combinations

### Step 5: Present and Execute

1. Use AskUserQuestion to present options with descriptions
2. When user selects, build and execute the corresponding bar command
3. Explain: "You chose [option], so I used `bar build [tokens]` to [reason]"

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
