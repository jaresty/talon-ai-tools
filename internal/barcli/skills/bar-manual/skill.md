# Bar Manual Usage Skill

## Purpose and Preconditions

This skill helps users **manually build bar commands** when they ask how to use the bar CLI.
Use this skill when the user wants to learn or get help with bar, not when automatically
structuring responses (use bar-autopilot, bar-workflow, or bar-suggest for automatic usage).

This skill **does not encode grammar**. Instead, it **discovers available tokens via `bar help tokens`**
and guides the user to compose valid sequences.

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

1. **Discover tokens** (never guess):
   - `bar help tokens`
   - Use sections to narrow: `bar help tokens static`, `... scope`, `... method`, `... persona`, etc.

2. **Build a prompt recipe**:
   - Use `bar build <tokens>...` with shorthand or `key=value` overrides.
   - Use `--prompt`, `--input`, or STDIN for subject text.

3. **Iterate for clarity**:
   - Adjust tokens based on ambiguity or missing constraints.
   - Use `//next` to skip stages if needed.

4. **Optionally shuffle**:
   - Use `bar shuffle` for exploration and pattern-breaking.
   - Fix axes with `--include`/`--exclude` and control randomness via `--seed`.

## Command Patterns

### Discover Tokens (Required First Step)
```bash
bar help tokens
bar help tokens static
bar help tokens axes
bar help tokens scope method
bar help tokens persona persona-intents
```

### Build Prompt Recipes
```bash
bar build plan full act analysis bullets plain fog
bar build plan full act analysis --prompt "Fix onboarding"
bar build //next plan full act
bar build plan full act method=analysis directional=fog
```

### Shuffle for Exploration
```bash
bar shuffle --seed 42
bar shuffle --include scope,method --fill 0.8
bar shuffle --exclude persona
```

### Use Alternate Grammar (if needed)
```bash
bar help tokens --grammar /path/to/grammar.json
bar build plan full act --grammar /path/to/grammar.json
```

## Skill Behavior Rules

- **Never invent tokens.** Always run `bar help tokens` or a sectioned variant first.
- **Prefer guidance over grammar.** Ask the user which section(s) to explore next.
- **Validate ordering.** Follow the token order shown in `bar help` output.
- **Support overrides.** After a `key=value` override, all remaining tokens must be `key=value`.
- **Use kebab-case for multi-word tokens.** When tokens contain spaces, convert to kebab-case (e.g., "as kent beck" → "as-kent-beck"). Bar will show the canonical slug in help output.
- **Offer shuffling only after a baseline recipe is built.**
- **"Run the command" means execute + re-prompt.** When asked to run a `bar ...` command, run it and then treat the command output as the new prompt/context before responding.
- **"bar suggest" means offer options to choose from.** When asked to do `bar suggest`, propose a short list of valid `bar ...` commands the user can pick from for you to run next.

## Recommended Conversation Flow

**User:** "Help me build a prompt for onboarding improvements."

**Assistant:**
1. "Let's discover valid tokens first: `bar help tokens scope method`."
2. "Pick a scope + method token that fits."
3. "Now we'll build the recipe: `bar build <tokens> --prompt "<subject>"`."
4. "Want to shuffle for alternatives? We can constrain scope/method."

## Example Session (Minimal)

```bash
bar help tokens scope method
bar build plan full act method=analysis --prompt "Improve onboarding flow"
```

## Output Handling

- Use `--json` when integrating into automation pipelines.
- Use `bar preset save` after a good build to reuse later with new prompt content.

## Cross-Agent Compatibility Notes

- Works with all agent types when users ask for help with bar
- Complements bar-autopilot (manual vs automatic usage)
- Should not be triggered automatically - only when user explicitly requests bar help
