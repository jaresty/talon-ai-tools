---
name: bar-suggest
description: Present users with bar-based approach options when multiple valid approaches exist.
---

# Bar Suggest Skill

## Purpose and Preconditions

This skill enables Claude to **present users with bar-based choices** for how to approach their request when multiple valid approaches exist.

Assumes:
- `bar` CLI is installed and accessible
- The LLM can run `bar help llm` (or `bar help tokens` for older versions) to discover available tokens
- The LLM has access to the Bash tool for executing bar commands
- The LLM can use AskUserQuestion tool for presenting choices

## High-level Workflow

1. **Detect open-ended or ambiguous request**
2. **Load comprehensive reference** via `bar help llm` once per conversation
3. **Generate 2-4 distinct bar command options** using method categorization and patterns from reference
4. **Present options** to user with plain-language descriptions
5. **Execute user's choice** and return structured response

## Skill Behavior Rules

- **Present options, don't choose.** Let user decide the approach.
- **Never hardcode tokens.** Discover via `bar help llm` (preferred) or `bar help tokens` (fallback).
- **Use kebab-case for multi-word tokens.** Convert spaces to hyphens (e.g., "as-kent-beck").
- **Keep options distinct.** Each option should represent meaningfully different approach.
- **Explain trade-offs.** Help user understand what each option emphasizes.
- **Use AskUserQuestion tool.** Present choices using Claude's question interface.
- **Be transparent about usage.** After executing the user's choice, explain the bar command used.
- **Execute chosen option.** After user selects, run the bar command and structure response.

## Discovery Workflow

### With `bar help llm` (preferred)

**For bar versions with `bar help llm` support:**

1. **Check for cached reference** - If already loaded in conversation, reuse it
2. **Load reference once** - Run `bar help llm` to load comprehensive reference
3. **Option generation strategy:**
   - Consult **"Usage Patterns by Task Type"** section for diverse examples
   - Reference **"Choosing Method"** section to understand method categorization
   - Use **"Token Catalog"** to discover tokens across all axes
   - Check **"Composition Rules"** for valid combinations

**Performance benefit:** Single reference load enables generating multiple diverse options

**Method categorization for option diversity:**
- **Exploration Methods** → For discovery-oriented options
- **Understanding Methods** → For analysis-oriented options
- **Decision Methods** → For evaluation-oriented options
- **Diagnostic Methods** → For problem-focused options

### Fallback (legacy `bar help tokens`)

**For older bar versions without `bar help llm`:**

1. Run `bar help tokens` to discover available tokens
2. Use sectioned queries: `bar help tokens scope method form`
3. Apply embedded heuristics for option generation

**Grammar note:** Token order is: persona → static → completeness → scope (1-2) → method (1-3) → form → channel → directional.

## Option Generation Strategy

**IMPORTANT:** Never hardcode tokens. Always discover them from `bar help llm` or `bar help tokens` first.

### Step 1: Detect When to Offer Choices

Use bar-suggest when the request is:
- **Open-ended** - No specific output format or approach specified
- **Ambiguous** - Multiple valid ways to interpret or approach the task
- **Exploratory** - User wants to understand something but unclear what aspect matters most
- **Multi-faceted** - Topic can be analyzed from several distinct angles

### Step 2: Generate Distinct Options

**With `bar help llm` Reference:**

1. **Read method categorization** - Reference § "Choosing Method" to discover:
   - Which method categories exist
   - Specific methods within each category
   - How categories represent different thinking modes

2. **Select static prompts for options** - **Almost always select a static prompt token** for each option to give clear task direction. Discover available static prompt tokens from the reference § "Token Catalog" § "Static Prompts". While the grammar marks static prompts as optional (0..1), omitting them results in open-ended responses that lack focus and make options less distinct.

3. **Create cross-category options** - Generate options using methods from different categories:
   - **Option 1**: Use methods from Exploration category (discover from reference)
   - **Option 2**: Use methods from Understanding category (discover from reference)
   - **Option 3**: Use methods from Decision category (discover from reference)
   - **Option 4**: Use methods from Diagnostic category (discover from reference)

4. **Vary scope and form** - Read reference § "Choosing Scope" and § "Choosing Form" to:
   - Discover available scope tokens for different focus areas
   - Discover available form tokens for different output structures
   - Combine with method variation for truly distinct options

5. **Check patterns** - Reference § "Usage Patterns by Task Type" to:
   - See examples of different approach types
   - Understand how token combinations create distinct experiences
   - Ensure your options match established patterns

**Example option diversity (tokens discovered from reference):**
- **Exploratory approach**: Methods from Exploration category
- **Analytical approach**: Methods from Understanding category
- **Decisional approach**: Methods from Decision category
- **Diagnostic approach**: Methods from Diagnostic category

### Legacy Option Generation (without bar help llm)

If `bar help llm` is unavailable, use these heuristics after discovering tokens:

1. **Discover tokens** - Run `bar help tokens scope method form`

2. **Vary by scope** - Different aspects to focus on:
   - Look for scope tokens related to "what it means"
   - Look for scope tokens related to "how it's structured"
   - Look for scope tokens related to "how it evolves over time"

3. **Vary by method** - Different ways of thinking:
   - Look for exploratory/discovery method tokens
   - Look for analytical/diagnostic method tokens
   - Look for flow/sequential method tokens

4. **Vary by form** - Different output structures:
   - Look for form tokens about bullets/lists
   - Look for form tokens about walkthroughs/flows
   - Look for form tokens about variants/options

### Include Freeform Option

Always include as one option:
- **"Surprise me"** or **"Explore freely"** - Use `bar shuffle` to generate an unexpected combination
- Explain this allows bar to discover novel token combinations
- Reference § "Advanced Features" § "Shuffle for Exploration" if using bar help llm

### Present and Execute

1. Use AskUserQuestion to present options with:
   - **Header**: Brief label for each option
   - **Description**: What the approach emphasizes, expected output characteristics
   - Optional: Reference to similar pattern from § "Usage Patterns" if using bar help llm

2. When user selects, build and execute the corresponding bar command with discovered tokens

3. Explain: "You chose [option], so I used `bar build [tokens]` to [reason]"

## Example Option Generation

**With bar help llm:**

```bash
# Step 1: Load reference
bar help llm

# Step 2: Read sections for option generation
# - Read § "Choosing Method" to understand categorization
# - Read § "Usage Patterns by Task Type" for examples
# - Read § "Token Catalog" to discover available tokens

# Step 3: Present options (tokens discovered from reference)
# Example for "Explain microservices architecture":
# Option 1 (Exploratory): Methods from Exploration category + appropriate scope/form
# Option 2 (Analytical): Methods from Understanding category + appropriate scope/form
# Option 3 (Decisional): Methods from Decision category + appropriate scope/form
# Option 4 (Freeform): bar shuffle

# Step 4: Execute user's choice with discovered tokens
bar build <user-chosen-tokens> --prompt "microservices architecture"
```

**Legacy approach:**

```bash
# Step 1: Discover tokens
bar help tokens scope method form

# Step 2: Generate options from discovered tokens
# Option 1: Exploratory method + broad scope + variants form
# Option 2: Analytical method + structure scope + table form
# Option 3: Flow method + time scope + walkthrough form
# Option 4: bar shuffle

# Step 3: Execute user's choice
bar build <discovered-tokens-for-choice> --prompt "topic"
```

## Integration with Other Skills

- **bar-autopilot** makes choice automatically
- **bar-suggest** presents options to user
- **bar-workflow** executes multi-step sequences

**Decision logic:**
- If request has single obvious framing → use bar-autopilot
- If request is ambiguous or open-ended → use bar-suggest
- If request is complex multi-faceted task → use bar-workflow

## Performance Notes

**With `bar help llm`:**
- **Tool calls:** 1 reference load per conversation
- **Benefits:** Method categorization provides natural option diversity
- **Planning:** Integrated patterns show proven option types

**Legacy approach:**
- **Tool calls:** 1-2 discovery queries per suggestion request
- Still fully functional with embedded heuristics

## Cross-Agent Compatibility Notes

- Works with all Claude agent types
- AskUserQuestion tool must be available
- If AskUserQuestion unavailable, fall back to bar-autopilot with best guess
- Token discovery ensures bar version compatibility

## Error Handling

- If bar unavailable: Present options conceptually without bar structure
- If token discovery fails: Use common patterns from memory
- Always prefer showing options over guessing user's intent

## Version Detection

To check if `bar help llm` is available:
```bash
bar help llm 2>/dev/null || bar help tokens
```

If the first command succeeds (exit 0), use the reference approach for option generation.
