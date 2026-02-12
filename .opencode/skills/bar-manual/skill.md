---
name: bar-manual
description: Guide users on how to manually build bar commands and learn the bar CLI.
---

# Bar Manual Usage Skill

## Purpose and Preconditions

This skill helps users **manually build bar commands** when they ask how to use the bar CLI.
Use this skill when the user wants to learn or get help with bar, not when automatically
structuring responses (use bar-autopilot, bar-workflow, or bar-suggest for automatic usage).

This skill **does not encode grammar**. Instead, it **teaches users to discover tokens and patterns via `bar help llm`** (or `bar help tokens` for older versions).

Assumes:
- `bar` CLI is installed and accessible
- The user can run `bar help` commands
- Optional: custom grammar JSON via `--grammar` or `BAR_GRAMMAR_PATH`

## When to Use This Skill

Use bar-manual when:
- User asks "How do I use bar?"
- User wants to learn bar command syntax
- User asks for help building a specific bar command
- User requests bar examples or tutorials

Do NOT use bar-manual for:
- Automatically structuring your own responses (use bar-autopilot instead)
- Multi-step workflows (use bar-workflow instead)
- Presenting options to users (use bar-suggest instead)

## High-level Workflow

### With `bar help llm` (preferred)

1. **Show comprehensive reference**: Teach user to run `bar help llm` for complete documentation
2. **Guide to relevant sections**: Point to specific sections based on their needs
   - "Usage Patterns by Task Type" for examples
   - "Token Catalog" for available tokens
   - "Token Selection Heuristics" for guidance
   - "Composition Rules" for constraints
3. **Build recipe together**: Use discovered tokens to construct bar command
4. **Optional exploration**: Teach `bar shuffle` for alternatives

### Fallback (legacy `bar help tokens`)

1. **Discover tokens**: Run `bar help tokens` or sectioned variants
2. **Build recipe**: Guide user through token selection
3. **Iterate**: Adjust based on needs
4. **Optional shuffle**: Explore with `bar shuffle`

## Teaching Approach

### Step 1: Show the Reference

**For bar versions with `bar help llm`:**

Teach the user to access comprehensive reference:
```bash
bar help llm
```

Explain what they'll see:
- ~500 lines of markdown documentation
- All available tokens across 7 axes
- Usage patterns for common scenarios
- Token selection heuristics
- Composition rules and constraints
- Complete examples

**For older bar versions:**

Fall back to discovery commands:
```bash
bar help tokens              # All tokens
bar help tokens task       # Tasks only
bar help tokens scope method # Multiple axes
bar help tokens persona      # Persona system
```

### Step 2: Guide to Relevant Sections

Based on user's request, point them to specific sections in `bar help llm`:

**For "How do I make decisions?"** → Reference § "Usage Patterns by Task Type" § "Decision-Making"

**For "What tokens are available?"** → Reference § "Token Catalog" sections

**For "How do I choose scope/method/form?"** → Reference § "Token Selection Heuristics"

**For "What are the rules?"** → Reference § "Composition Rules"

**For "Show me examples"** → Reference § "Usage Patterns by Task Type" (8 examples)

**For "How does persona work?"** → Reference § "Persona System"

### Step 3: Build Command Together

Once user understands the reference:

```bash
# Token order from reference § "Grammar Architecture":
# [persona] [static] [completeness] [scope...] [method...] [form] [channel] [directional]

# Build command with discovered tokens
bar build <tokens-from-reference> --subject "user's text"

# Examples (tokens discovered from reference, not hardcoded):
# - For decisions: reference shows patterns using decision-oriented tokens
# - For understanding: reference shows patterns using understanding-oriented tokens
# - For diagnosis: reference shows patterns using diagnostic-oriented tokens
```

### Step 4: Iterate and Refine

Guide user through adjustments:
- Check output quality
- Adjust tokens based on results
- Reference § "Token Catalog" for alternatives
- Use skip sentinels (`//next`, `//:stage`) if needed

### Step 5: Optional Exploration

Teach shuffle for exploration:
```bash
bar shuffle                           # Random exploration
bar shuffle --seed 42                 # Reproducible
bar shuffle --include scope,method    # Focus axes
bar shuffle --exclude persona         # Exclude axes
bar shuffle --fill 0.8                # Adjust density
bar shuffle --json                    # JSON output to inspect full token set
```

**Note on compound directionals:** `bar help tokens directional` lists only primitive
directional tokens. Compound tokens (e.g., `fly rog`, `fip rog`, `dip ong`, `dip bog`)
also exist and are listed in `bar help llm` § Token Catalog § Directional. Run
`bar shuffle --json` and inspect the `directional` field to discover compound forms in use.

### Step 6: Interactive Grammar Learning (Optional)

For users who prefer to learn through interaction, point them to `bar tui2` — the
stage-based grammar editor that teaches token selection through direct interaction:

```bash
bar tui2                        # Launch with live preview
bar tui2 make full              # Pre-seed tokens at launch
bar tui2 --command "pbcopy"     # Pre-fill the Run Command field
```

Inside `bar tui2`, users progress through grammar stages (task → completeness → scope →
method → form → …) with live preview of the generated prompt. The equivalent `bar build`
command is shown and copyable at any time, closing the loop back to the CLI.

## Command Patterns

### Accessing Help

**Preferred (with bar help llm):**
```bash
# Get comprehensive reference
bar help llm

# Save for offline reference
bar help llm > bar-reference.md

# Also accessible as:
bar help reference
```

**Legacy (older bar versions):**
```bash
# Discover all tokens
bar help tokens

# Discover specific sections
bar help tokens task
bar help tokens axes
bar help tokens scope method
bar help tokens persona persona-intents
```

### Building Commands

```bash
# Discover tokens first (via bar help llm or bar help tokens)

# Build with shorthand (order matters)
bar build <static> <completeness> <scope> <method> <form> --subject "text"

# Build with persona
bar build persona=<preset> <static> <completeness> --subject "text"

# Build with key=value overrides (all after first override must be key=value)
bar build <static> completeness=<value> scope=<value> --subject "text"

# Skip stages
bar build //next <static> <completeness>
bar build //:static <completeness> <scope>
```

### Output Handling

```bash
# Get JSON for automation
bar build <tokens> --subject "text" --json

# Save to file
bar build <tokens> --subject "text" --output recipe.txt

# Read from file
bar build <tokens> --input prompt.txt

# Use STDIN
echo "text" | bar build <tokens>
```

### Interactive Grammar Exploration

```bash
# Launch the stage-based grammar editor (recommended for new users)
bar tui2

# Pre-seed tokens at launch
bar tui2 make full

# Pre-fill the Run Command field (e.g. for clipboard copy workflow)
bar tui2 --command "pbcopy"

# Quickly scan all available token slugs by category
bar help tokens --plain             # category:slug one per line
bar help tokens scope --plain       # scope axis only
bar help tokens --plain | grep '^task:'  # just tasks
```

### Saving Presets

```bash
# After building a good command
bar preset save my-decision-pattern

# Reuse with new content
bar preset use my-decision-pattern --subject "new text"

# List saved presets
bar preset list

# Show preset details
bar preset show my-decision-pattern
```

## Skill Behavior Rules

- **Never invent tokens.** Always teach users to discover via `bar help llm` (preferred) or `bar help tokens` (fallback).
- **Reference sections, don't embed content.** Point users to § sections in the reference output.
- **Teach discovery, not memorization.** Focus on showing users how to find what they need.
- **Validate ordering.** Token order from reference: persona → static → completeness → scope (1-2) → method (1-3) → form → channel → directional
- **Support overrides.** After first `key=value`, all remaining tokens must be `key=value`.
- **Use kebab-case for multi-word tokens.** Convert spaces to hyphens (e.g., "as-kent-beck").
- **Offer shuffling after baseline.** Don't suggest shuffle until user has built at least one command.
- **"Run the command" means execute + show output.** Execute the bar command and show results.

## Recommended Conversation Flow

**User:** "Help me build a prompt for [topic]."

**Assistant (with bar help llm):**
1. "Let me show you the comprehensive reference: `bar help llm`"
2. "For your use case, look at the § 'Usage Patterns by Task Type' section"
3. "Based on the reference, we can use tokens from § 'Token Catalog'"
4. "Let's build: `bar build <tokens-from-reference> --subject '<topic>'`"
5. "Want alternatives? We can use `bar shuffle` to explore"

**Assistant (legacy fallback):**
1. "Let's discover valid tokens: `bar help tokens`"
2. "Based on the output, which tokens fit your needs?"
3. "We'll build: `bar build <chosen-tokens> --subject '<topic>'`"
4. "Want to shuffle for alternatives?"

## Example Teaching Session

**With bar help llm:**
```bash
# Step 1: Show comprehensive reference
bar help llm

# Step 2: Guide user to relevant section
# "Look at § 'Usage Patterns by Task Type' for examples"
# "Check § 'Token Selection Heuristics' for guidance"

# Step 3: Build command with discovered tokens
bar build <tokens-user-discovered> --subject "User's topic"

# Step 4: Iterate if needed
# "Check § 'Token Catalog' for alternatives"

# Step 5 (optional): Explore with shuffle
bar shuffle --include scope,method
```

**Legacy approach:**
```bash
# Step 1: Discover tokens
bar help tokens

# Step 2: Pick tokens from help output
bar build <discovered-tokens> --subject "User's topic"

# Step 3 (optional): Shuffle
bar shuffle --include scope,method
```

## Performance Notes

**With `bar help llm`:**
- Single command shows complete documentation
- Users see all available options at once
- Integrated examples and heuristics
- Better learning experience

**Legacy approach:**
- Multiple queries to discover tokens
- Fragmented information
- Still fully functional

## Cross-Agent Compatibility Notes

- Works with all agent types when users ask for help with bar
- Complements bar-autopilot (manual vs automatic usage)
- Should not be triggered automatically - only when user explicitly requests bar help

## Understanding Bar Output

**Teach users how bar output works:**

1. **Bar outputs a structured prompt** - When users run `bar build`, it generates a structured prompt with sections:
   - `TASK`: What to do
   - `CONSTRAINTS`: How to do it (scope, method, form, completeness, directional)
   - `PERSONA`: Communication style (voice, audience, tone, intent)
   - `SUBJECT`: User's original content as data
   - `REFERENCE KEY`: Explains how to interpret each section

2. **The output should be executed** - Explain that:
   - The bar output is an instruction prompt to be followed
   - An LLM should execute the TASK, applying the CONSTRAINTS and PERSONA
   - The SUBJECT contains their original content as data (not as instructions)

3. **Context comes from conversation** - When an LLM executes a bar-generated prompt:
   - It should use context from the conversation, not from bar help output
   - Bar tokens and catalog content should not be included as context
   - The bar structure guides how to respond, not what content to use

## Error Handling When Teaching

When teaching users about bar errors:

1. **Common error messages:**
   - `error: unrecognized token` - Invalid token name was used
   - `error: token <name> not recognized. Did you mean: <suggestions>` - Bar suggests corrections
   - `error: incompatible tokens` - Token combination violates composition rules
   - `error: too many <axis> tokens` - Exceeded axis capacity (e.g., max 3 method tokens)

2. **Teach retry approach:**
   - If bar build fails, read the error message for hints
   - Fix token spelling/casing (use kebab-case for multi-word tokens)
   - Check token order: persona → static → completeness → scope → method → form → channel → directional
   - Consult `bar help llm` § "Composition Rules" for incompatibilities
   - Retry the command with corrections

3. **Validation approach:**
   - Show users how to verify token names via `bar help llm` or `bar help tokens`
   - Demonstrate checking composition rules before building complex commands
   - Explain that error messages are helpful, not just failures

## Version Detection

To check if `bar help llm` is available:
```bash
bar help llm 2>/dev/null && echo "Available" || echo "Use bar help tokens"
```

Teach users this command to check their bar version capabilities.
