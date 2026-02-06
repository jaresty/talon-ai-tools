# ADR 0103: Add Formal Grammar Specification to `bar help llm`

## Status
Accepted

## Context

The `bar help llm` command provides comprehensive reference documentation for LLMs to generate valid bar commands. However, the current output uses natural language descriptions of syntax rules, which can be ambiguous and lead to LLMs generating invalid commands.

### Current Problems
- **Ambiguous token ordering**: Natural language descriptions like "tokens must follow this order" are interpreted inconsistently
- **Count constraints unclear**: Rules like "scope accepts 0-2 tokens" are sometimes violated
- **Override mode confusion**: The rule "after first key=value, all must be key=value" is frequently misunderstood
- **Multi-word token errors**: LLMs output "as teacher" instead of "as-teacher"

### Why LLMs Need Formal Grammar

Research on LLM grammar adherence shows that:
1. **EBNF/BNF notation** is well-represented in training data (textbooks, RFCs, specs)
2. **Explicit meta-conventions** (explaining what symbols mean) dramatically improve parsing
3. **Positive and negative examples** anchor abstract rules in concrete patterns
4. **Clear role instructions** ("you MUST conform to this grammar") improve compliance

## Decision

Add a formal EBNF-style grammar specification to `bar help llm` output that:
1. **Uses standard EBNF notation** with explicit meta-convention explanations
2. **Includes positive and negative examples** with explanations
3. **Provides generation instructions** as a step-by-step checklist for LLMs
4. **Enforces current constraints**: required static token (ADR 0102), subject flags (ADR 0082)

### Grammar Location

Insert new "Formal Grammar Specification" subsection in `renderGrammarArchitecture()` function immediately after "Token Ordering" subsection in `internal/barcli/help_llm.go`.

### Grammar Format

```ebnf
<command> ::= "bar" "build" <token-sequence> <flags>

<token-sequence> ::= <persona-tokens>? <static-token> <constraint-tokens> <override-tokens>*

<persona-tokens> ::= (<persona-preset> | <persona-axis>)+
<static-token>   ::= <static-value>
<constraint-tokens> ::= <completeness-token>? <scope-token>? <scope-token>? <method-token>? <method-token>? <method-token>? <form-token>? <channel-token>? <directional-token>?
<override-tokens> ::= (<axis-override> | <constraint-override> | <persona-override>)*
<flags>          ::= <subject-flag>? <addendum-flag>? <output-flag>? <format-flag>?
```

See full grammar in implementation below.

### Key Constraints Enforced

1. **Static token is REQUIRED** for LLM-generated commands (ADR 0102)
2. **Scope**: maximum 2 tokens
3. **Method**: maximum 3 tokens
4. **All other axes**: maximum 1 token each
5. **Override mode**: Once `key=value` used, ALL subsequent tokens must be `key=value`
6. **Subject input**: Either `--subject` OR stdin, never both (ADR 0082)
7. **Multi-word tokens**: Slug format with dashes (e.g., `as-teacher`)

## Implementation

### Code Changes

File: `internal/barcli/help_llm.go`

**Add new function:**

```go
func renderFormalGrammar(w io.Writer, grammar *Grammar, compact bool) {
	if compact {
		// Compact mode: just the EBNF rules
		fmt.Fprintf(w, "### Formal Grammar (EBNF)\n\n")
		fmt.Fprintf(w, "```ebnf\n")
		fmt.Fprintf(w, "<command> ::= \"bar\" \"build\" <token-sequence> <flags>\n")
		fmt.Fprintf(w, "<token-sequence> ::= <persona-tokens>? <static-token> <constraint-tokens> <override-tokens>*\n")
		// ... rest of compact grammar
		fmt.Fprintf(w, "```\n\n")
		return
	}

	// Full mode: complete specification with examples
	fmt.Fprintf(w, "### Formal Grammar Specification\n\n")
	fmt.Fprintf(w, "**For LLM agents generating bar commands: You MUST produce strings that conform to this grammar.**\n\n")

	// Meta-convention explanation
	fmt.Fprintf(w, "The grammar below uses Extended Backus-Naur Form (EBNF) notation:\n")
	fmt.Fprintf(w, "- **Angle brackets** like `<command>` denote nonterminals (placeholders to expand)\n")
	fmt.Fprintf(w, "- **Quoted strings** like `\"build\"` are literal tokens to output exactly as shown\n")
	// ... rest of meta-conventions

	// Grammar rules
	fmt.Fprintf(w, "\n**Start symbol:** `<command>`\n\n")
	fmt.Fprintf(w, "```ebnf\n")
	// ... full EBNF grammar
	fmt.Fprintf(w, "```\n\n")

	// Important constraints
	fmt.Fprintf(w, "**Important constraints:**\n")
	fmt.Fprintf(w, "1. **Static token is REQUIRED** for LLM-generated commands\n")
	// ... rest of constraints

	// Valid examples
	fmt.Fprintf(w, "\n**Valid examples:**\n\n")
	fmt.Fprintf(w, "```bash\n")
	// ... examples
	fmt.Fprintf(w, "```\n\n")

	// Invalid examples
	fmt.Fprintf(w, "**Invalid examples (and why they fail):**\n\n")
	fmt.Fprintf(w, "```bash\n")
	// ... invalid examples with explanations
	fmt.Fprintf(w, "```\n\n")

	// Generation instructions
	fmt.Fprintf(w, "**Generation instructions for LLMs:**\n\n")
	fmt.Fprintf(w, "When generating bar commands:\n")
	fmt.Fprintf(w, "1. **Start with the start symbol** `<command>` and expand top-down\n")
	// ... rest of checklist
	fmt.Fprintf(w, "\n")
}
```

**Update `renderGrammarArchitecture()`:**

```go
func renderGrammarArchitecture(w io.Writer, grammar *Grammar, compact bool) {
	// ... existing code for Token Ordering, Axis Capacity, Usage Guidance

	// NEW: Add formal grammar specification
	renderFormalGrammar(w, grammar, compact)

	// ... existing code for Key=Value Override Syntax
}
```

### Terminal Value Strategy

Use ellipsis `...` for long lists and reference "Token Quick Reference" section:

```ebnf
<scope-value> ::= "act" | "fail" | "good" | "mean" | "struct" | "thing" | "time" | "view" | ...
```

This avoids duplication while keeping the grammar readable.

## Rationale

### Why EBNF Over Alternatives

**Regex-style patterns**: Rejected - less expressive for nested syntax, harder to show ordering

**JSON Schema**: Rejected - LLMs trained more on BNF/EBNF than JSON Schema for command syntax

**Natural language only**: Current state - ambiguous, frequently misinterpreted

### Why Include Examples

LLMs respond very strongly to in-context examples. Showing:
- **Valid examples**: Anchors abstract grammar in concrete patterns to mimic
- **Invalid examples with errors**: Helps LLMs learn what NOT to do and why

### Why Explicit Meta-Conventions

Different EBNF variants use symbols differently. Explicitly defining:
- `<nonterminal>` vs `"terminal"`
- `|` (alternation), `?` (optional), `*` (zero-or-more), `+` (one-or-more)

Eliminates ambiguity and leverages LLM's pattern-matching on familiar notation.

## Consequences

### Positive

- **Improved LLM adherence**: Skills generate syntactically valid bar commands more reliably
- **Fewer syntax errors**: bar-autopilot, bar-workflow, bar-suggest produce correct invocations
- **Self-documenting**: Grammar serves as authoritative reference for both humans and LLMs
- **Single source of truth**: Formal spec lives alongside token catalog
- **Validation target**: Can build syntax validators/linters from this grammar
- **Evolution clarity**: When grammar changes, update one formal spec

### Negative

- **Longer help output**: Adds ~100 lines to `bar help llm` (mitigated by compact mode)
- **Maintenance burden**: Grammar must stay in sync with code changes
- **Complexity**: EBNF may be unfamiliar to some users (mitigated by meta-convention explanations)

### Neutral

- **Training required**: Bar skills may need updates to reference formal grammar
- **Testing strategy**: Need to validate LLM adherence improvements empirically

## Validation

### Success Metrics

- [ ] `bar help llm` includes Formal Grammar Specification section
- [ ] Grammar includes all current constraints (static required, scope ≤ 2, method ≤ 3, etc.)
- [ ] Grammar reflects ADR 0082 flags (--subject, --addendum)
- [ ] Valid examples compile and execute correctly
- [ ] Invalid examples fail with expected error messages
- [ ] Compact mode works (`bar help llm --compact` shows abbreviated grammar)

### Acceptance Tests

1. **Manual verification**: Read generated `bar help llm` output, verify grammar is complete
2. **Valid example testing**: Run each valid example, confirm it works
3. **Invalid example testing**: Run each invalid example, confirm expected error
4. **LLM testing** (future): Provide updated help to Claude/GPT-4, measure syntax error rate reduction

## Future Enhancements

1. **Grammar versioning**: Include grammar version in output so LLMs can adapt to changes
2. **Auto-generation**: Generate EBNF from `Grammar` struct to ensure sync
3. **Syntax validator**: Build validator that checks commands against grammar
4. **Skills linter**: Lint bar automation skills to ensure they reference formal grammar
5. **Grammar evolution tracking**: Document grammar changes in ADR work logs

## Related ADRs

- **ADR 0097**: Bar install-skills command - Skills will benefit from formal grammar reference
- **ADR 0082**: --subject and --addendum flags - Grammar reflects new flag syntax (--subject, --addendum deprecates --prompt)
- **ADR 0102**: Require static prompt in CLI - Grammar enforces static token requirement
- **ADR 0098**: LLM-optimized bar reference help - Builds on existing LLM help infrastructure

## References

- "How to make LLMs follow grammar/format constraints" best practices (EBNF, meta-conventions, examples, role instructions)
- EBNF notation: ISO/IEC 14977
- Common LLM training corpus: RFC grammars, language specs, textbook BNF definitions
