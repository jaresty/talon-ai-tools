package barcli

import (
	"fmt"
	"io"
	"sort"
	"strings"
	"time"
)

// renderLLMHelp generates a comprehensive Markdown reference document optimized for LLM consumption
// If section is non-empty, only renders that section
// If compact is true, outputs tables only without descriptions or examples
func renderLLMHelp(w io.Writer, grammar *Grammar, section string, compact bool) {
	shouldRender := func(sectionName string) bool {
		return section == "" || section == sectionName
	}

	// Always render header unless filtering or compact
	if section == "" && !compact {
		fmt.Fprintf(w, "# Bar CLI Reference for LLMs\n\n")
		fmt.Fprintf(w, "Generated: %s\n", time.Now().UTC().Format(time.RFC3339))
		fmt.Fprintf(w, "Grammar Schema Version: %s\n\n", grammar.SchemaVersion)
		fmt.Fprintf(w, "---\n\n")
	}

	if shouldRender("quickstart") {
		renderQuickStart(w, compact)
	}
	if shouldRender("architecture") {
		renderGrammarArchitecture(w, grammar, compact)
	}
	if shouldRender("cheatsheet") {
		renderTokenCheatSheet(w, grammar, compact)
	}
	if shouldRender("tokens") {
		renderTokenCatalog(w, grammar, compact)
	}
	if shouldRender("persona") {
		renderPersonaSystem(w, grammar, compact)
	}
	if shouldRender("rules") {
		renderCompositionRules(w, grammar, compact)
	}
	if shouldRender("patterns") {
		renderUsagePatterns(w, compact)
	}
	if shouldRender("heuristics") {
		renderTokenSelectionHeuristics(w, compact)
	}
	if shouldRender("advanced") {
		renderAdvancedFeatures(w, compact)
	}
	if shouldRender("metadata") {
		renderMetadata(w, grammar, compact)
	}
}

func renderQuickStart(w io.Writer, compact bool) {
	if compact {
		fmt.Fprintf(w, "## Quick Start\n\n")
		fmt.Fprintf(w, "```bash\n")
		fmt.Fprintf(w, "bar build <tokens>... --subject \"your text\"\n")
		fmt.Fprintf(w, "```\n\n")
		return
	}
	fmt.Fprintf(w, "## Quick Start\n\n")
	fmt.Fprintf(w, "Bar constructs structured prompts by combining tokens from multiple axes:\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "# Basic usage\n")
	fmt.Fprintf(w, "bar build <tokens>... --subject \"your text\"\n\n")
	fmt.Fprintf(w, "# Example: Decision-making prompt\n")
	fmt.Fprintf(w, "bar build diff thing full branch variants --subject \"Choose between Redis and Postgres\"\n\n")
	fmt.Fprintf(w, "# Example: Understanding flow\n")
	fmt.Fprintf(w, "bar build show time full flow walkthrough --subject \"Explain the authentication process\"\n")
	fmt.Fprintf(w, "```\n\n")
}

func renderGrammarArchitecture(w io.Writer, grammar *Grammar, compact bool) {
	if compact {
		fmt.Fprintf(w, "## Grammar Architecture\n\n")
		fmt.Fprintf(w, "Order: [persona] [static] [completeness] [scope 0-2] [method 0-3] [form] [channel] [directional]\n\n")
		return
	}
	fmt.Fprintf(w, "## Grammar Architecture\n\n")
	fmt.Fprintf(w, "### Token Ordering\n\n")
	fmt.Fprintf(w, "Tokens must follow this order:\n\n")
	fmt.Fprintf(w, "```\n")
	fmt.Fprintf(w, "[persona] [static] [completeness] [scope...] [method...] [form] [channel] [directional]\n")
	fmt.Fprintf(w, "```\n\n")

	fmt.Fprintf(w, "### Axis Capacity\n\n")
	fmt.Fprintf(w, "- **Tasks**: 1 token (required)\n")
	fmt.Fprintf(w, "- **Completeness**: 0-1 token\n")
	fmt.Fprintf(w, "- **Scope**: 0-2 tokens\n")
	fmt.Fprintf(w, "- **Method**: 0-3 tokens\n")
	fmt.Fprintf(w, "- **Form**: 0-1 token\n")
	fmt.Fprintf(w, "- **Channel**: 0-1 token\n")
	fmt.Fprintf(w, "- **Directional**: 0-1 token\n")
	fmt.Fprintf(w, "- **Persona**: voice, audience, tone, intent axes or preset\n\n")

	fmt.Fprintf(w, "### Usage Guidance for Automated/Agent Contexts\n\n")
	fmt.Fprintf(w, "**Tasks are REQUIRED for automated usage**, despite the grammar allowing 0-1 tokens. Always select a task token to provide clear task direction. Only omit the task in manual exploratory contexts where maximum flexibility is explicitly desired. Automated responses without a task lack focus and produce open-ended, poorly structured output.\n\n")

	renderFormalGrammar(w, grammar, compact)

	fmt.Fprintf(w, "### Key=Value Override Syntax\n\n")
	fmt.Fprintf(w, "After the first `key=value` override, all remaining tokens must use `key=value` format:\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "bar build make struct method=branch form=table --subject \"text\"\n")
	fmt.Fprintf(w, "```\n\n")
}

func renderFormalGrammar(w io.Writer, grammar *Grammar, compact bool) {
	if compact {
		fmt.Fprintf(w, "### Formal Grammar (EBNF)\n\n")
		fmt.Fprintf(w, "```ebnf\n")
		fmt.Fprintf(w, "<command> ::= \"bar\" \"build\" <token-sequence> <flags>\n")
		fmt.Fprintf(w, "<token-sequence> ::= <persona-tokens>? <static-token> <constraint-tokens> <override-tokens>*\n")
		fmt.Fprintf(w, "<constraint-tokens> ::= <completeness>? <scope>? <scope>? <method>? <method>? <method>? <form>? <channel>? <directional>?\n")
		fmt.Fprintf(w, "```\n\n")
		return
	}

	fmt.Fprintf(w, "### Formal Grammar Specification\n\n")
	fmt.Fprintf(w, "**For LLM agents generating bar commands: You MUST produce strings that conform to this grammar.**\n\n")

	fmt.Fprintf(w, "The grammar below uses Extended Backus-Naur Form (EBNF) notation:\n")
	fmt.Fprintf(w, "- **Angle brackets** like `<command>` denote nonterminals (placeholders to expand)\n")
	fmt.Fprintf(w, "- **Quoted strings** like `\"build\"` are literal tokens to output exactly as shown\n")
	fmt.Fprintf(w, "- **Pipe `|`** separates alternatives; choose exactly one\n")
	fmt.Fprintf(w, "- **Question mark `?`** means optional (zero or one occurrence)\n")
	fmt.Fprintf(w, "- **Asterisk `*`** means repeat zero or more times\n")
	fmt.Fprintf(w, "- **Plus `+`** means repeat one or more times\n")
	fmt.Fprintf(w, "- **Square brackets `[...]`** group optional elements\n")
	fmt.Fprintf(w, "- **Parentheses `(...)`** group required elements\n\n")

	fmt.Fprintf(w, "**Start symbol:** `<command>`\n\n")

	fmt.Fprintf(w, "```ebnf\n")
	fmt.Fprintf(w, "<command>       ::= \"bar\" \"build\" <token-sequence> <flags>\n\n")

	fmt.Fprintf(w, "<token-sequence> ::= <persona-tokens>? <static-token> <constraint-tokens> <override-tokens>*\n\n")

	fmt.Fprintf(w, "<persona-tokens> ::= (<persona-preset> | <persona-axis>)+\n\n")

	fmt.Fprintf(w, "<persona-preset> ::= \"persona=\" <preset-name>\n\n")

	fmt.Fprintf(w, "<persona-axis>   ::= <voice-token> | <audience-token> | <tone-token> | <intent-token>\n\n")

	fmt.Fprintf(w, "<voice-token>    ::= \"voice=\" <voice-value>\n")
	fmt.Fprintf(w, "<audience-token> ::= \"audience=\" <audience-value>\n")
	fmt.Fprintf(w, "<tone-token>     ::= \"tone=\" <tone-value>\n")
	fmt.Fprintf(w, "<intent-token>   ::= \"intent=\" <intent-value>\n\n")

	fmt.Fprintf(w, "<static-token>   ::= <static-value>\n\n")

	fmt.Fprintf(w, "<constraint-tokens> ::= <completeness-token>? <scope-token>? <scope-token>? <method-token>? <method-token>? <method-token>? <form-token>? <channel-token>? <directional-token>?\n\n")

	fmt.Fprintf(w, "<completeness-token> ::= <completeness-value>\n")
	fmt.Fprintf(w, "<scope-token>        ::= <scope-value>\n")
	fmt.Fprintf(w, "<method-token>       ::= <method-value>\n")
	fmt.Fprintf(w, "<form-token>         ::= <form-value>\n")
	fmt.Fprintf(w, "<channel-token>      ::= <channel-value>\n")
	fmt.Fprintf(w, "<directional-token>  ::= <directional-value>\n\n")

	fmt.Fprintf(w, "<override-tokens> ::= (<axis-override> | <constraint-override> | <persona-override>)*\n\n")

	fmt.Fprintf(w, "<axis-override>       ::= \"task=\" <task-value>\n")
	fmt.Fprintf(w, "<constraint-override> ::= \"completeness=\" <completeness-value>\n")
	fmt.Fprintf(w, "                       | \"scope=\" <scope-value>\n")
	fmt.Fprintf(w, "                       | \"method=\" <method-value>\n")
	fmt.Fprintf(w, "                       | \"form=\" <form-value>\n")
	fmt.Fprintf(w, "                       | \"channel=\" <channel-value>\n")
	fmt.Fprintf(w, "                       | \"directional=\" <directional-value>\n")
	fmt.Fprintf(w, "<persona-override>    ::= \"voice=\" <voice-value>\n")
	fmt.Fprintf(w, "                       | \"audience=\" <audience-value>\n")
	fmt.Fprintf(w, "                       | \"tone=\" <tone-value>\n")
	fmt.Fprintf(w, "                       | \"intent=\" <intent-value>\n\n")

	fmt.Fprintf(w, "<flags>          ::= <subject-flag>? <addendum-flag>? <output-flag>? <format-flag>?\n\n")

	fmt.Fprintf(w, "<subject-flag>   ::= \"--subject\" <quoted-string>\n")
	fmt.Fprintf(w, "                  | \"--input\" <filepath>\n")
	fmt.Fprintf(w, "<addendum-flag>  ::= \"--addendum\" <quoted-string>\n")
	fmt.Fprintf(w, "<output-flag>    ::= \"--output\" <filepath>\n")
	fmt.Fprintf(w, "<format-flag>    ::= \"--json\"\n\n")

	fmt.Fprintf(w, "<quoted-string>  ::= '\"' <any-text> '\"'\n")
	fmt.Fprintf(w, "<filepath>       ::= <any-text-without-spaces>\n\n")

	fmt.Fprintf(w, "# Terminal values (see Token Quick Reference for complete lists)\n")

	// Static values - get from grammar
	staticTokens := make([]string, 0, len(grammar.Static.Profiles))
	for name := range grammar.Static.Profiles {
		slug := grammar.slugForToken(name)
		if slug == "" {
			slug = name
		}
		staticTokens = append(staticTokens, fmt.Sprintf("\"%s\"", slug))
	}
	sort.Strings(staticTokens)
	fmt.Fprintf(w, "<static-value>       ::= %s\n", strings.Join(staticTokens, " | "))

	// Helper function to format axis tokens
	formatAxisTokens := func(axisName string, limit int) string {
		tokens, exists := grammar.Axes.Definitions[axisName]
		if !exists {
			return "..."
		}
		slugs := make([]string, 0, len(tokens))
		for token := range tokens {
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			slugs = append(slugs, fmt.Sprintf("\"%s\"", slug))
		}
		sort.Strings(slugs)
		if limit > 0 && len(slugs) > limit {
			return strings.Join(slugs[:limit], " | ") + " | ..."
		}
		return strings.Join(slugs, " | ")
	}

	fmt.Fprintf(w, "<completeness-value> ::= %s\n", formatAxisTokens("completeness", 0))
	fmt.Fprintf(w, "<scope-value>        ::= %s\n", formatAxisTokens("scope", 8))
	fmt.Fprintf(w, "<method-value>       ::= %s\n", formatAxisTokens("method", 7))
	fmt.Fprintf(w, "<form-value>         ::= %s\n", formatAxisTokens("form", 7))
	fmt.Fprintf(w, "<channel-value>      ::= %s\n", formatAxisTokens("channel", 7))
	fmt.Fprintf(w, "<directional-value>  ::= %s\n", formatAxisTokens("directional", 7))

	// Persona values - get from grammar.Persona.Axes instead of grammar.Axes.Definitions
	formatPersonaAxis := func(axisName string, limit int) string {
		tokens, exists := grammar.Persona.Axes[axisName]
		if !exists {
			return "..."
		}
		slugs := make([]string, 0, len(tokens))
		for _, token := range tokens {
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			slugs = append(slugs, fmt.Sprintf("\"%s\"", slug))
		}
		sort.Strings(slugs)
		if limit > 0 && len(slugs) > limit {
			return strings.Join(slugs[:limit], " | ") + " | ..."
		}
		return strings.Join(slugs, " | ")
	}

	fmt.Fprintf(w, "<voice-value>        ::= %s\n", formatPersonaAxis("voice", 7))
	fmt.Fprintf(w, "<audience-value>     ::= %s\n", formatPersonaAxis("audience", 7))
	fmt.Fprintf(w, "<tone-value>         ::= %s\n", formatPersonaAxis("tone", 0))

	// Persona presets
	presetTokens := make([]string, 0, len(grammar.Persona.Presets))
	for name := range grammar.Persona.Presets {
		presetTokens = append(presetTokens, fmt.Sprintf("\"%s\"", name))
	}
	sort.Strings(presetTokens)
	if len(presetTokens) > 7 {
		fmt.Fprintf(w, "<preset-name>        ::= %s | ...\n", strings.Join(presetTokens[:7], " | "))
	} else if len(presetTokens) > 0 {
		fmt.Fprintf(w, "<preset-name>        ::= %s\n", strings.Join(presetTokens, " | "))
	} else {
		fmt.Fprintf(w, "<preset-name>        ::= ...\n")
	}
	fmt.Fprintf(w, "```\n\n")

	fmt.Fprintf(w, "**Important constraints:**\n")
	fmt.Fprintf(w, "1. **Static token is REQUIRED** for LLM-generated commands\n")
	fmt.Fprintf(w, "2. **Scope**: maximum 2 tokens\n")
	fmt.Fprintf(w, "3. **Method**: maximum 3 tokens\n")
	fmt.Fprintf(w, "4. **All other constraint axes**: maximum 1 token each\n")
	fmt.Fprintf(w, "5. **Override mode**: Once you use `key=value` syntax, ALL subsequent tokens must use `key=value` format\n")
	fmt.Fprintf(w, "6. **Subject input**: Use either `--subject` OR stdin (piped input), never both\n")
	fmt.Fprintf(w, "7. **Multi-word tokens**: Use slug format with dashes (e.g., `as-teacher`, not `as teacher`)\n\n")

	fmt.Fprintf(w, "**Valid examples:**\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "# Basic structure: task + constraints + flags\n")
	fmt.Fprintf(w, "bar build make struct flow --subject \"Create login endpoint\"\n\n")

	fmt.Fprintf(w, "# With persona: persona tokens before task\n")
	fmt.Fprintf(w, "bar build voice=as-teacher show gist bullets --subject \"Explain recursion\"\n\n")

	fmt.Fprintf(w, "# With multiple constraints: follow axis capacity limits\n")
	fmt.Fprintf(w, "bar build probe struct mean flow mapping --subject \"Analyze architecture\"\n\n")

	fmt.Fprintf(w, "# With override syntax: key=value after first override\n")
	fmt.Fprintf(w, "bar build make struct method=branch form=table --subject \"Design API\"\n\n")

	fmt.Fprintf(w, "# With addendum: separate task clarification from subject\n")
	fmt.Fprintf(w, "bar build show struct --subject \"auth.go\" --addendum \"focus on security implications\"\n\n")

	fmt.Fprintf(w, "# Using stdin instead of --subject flag\n")
	fmt.Fprintf(w, "echo \"Fix the bug\" | bar build make focus steps\n")
	fmt.Fprintf(w, "```\n\n")

	fmt.Fprintf(w, "**Invalid examples (and why they fail):**\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "# WRONG: Missing task token\n")
	fmt.Fprintf(w, "bar build struct flow --subject \"text\"\n")
	fmt.Fprintf(w, "# Error: task is required\n\n")

	fmt.Fprintf(w, "# WRONG: Too many scope tokens (max 2)\n")
	fmt.Fprintf(w, "bar build show struct mean thing time --subject \"text\"\n")
	fmt.Fprintf(w, "# Error: scope accepts maximum 2 tokens\n\n")

	fmt.Fprintf(w, "# WRONG: Multi-word token without dashes\n")
	fmt.Fprintf(w, "bar build show voice=as teacher --subject \"text\"\n")
	fmt.Fprintf(w, "# Error: unknown token 'teacher'; did you mean 'as-teacher'?\n\n")

	fmt.Fprintf(w, "# WRONG: Mixed shorthand and override without consistency\n")
	fmt.Fprintf(w, "bar build make focus method=branch steps --subject \"text\"\n")
	fmt.Fprintf(w, "# Error: after key=value override, all remaining tokens must be key=value\n\n")

	fmt.Fprintf(w, "# WRONG: Both --subject and stdin provided\n")
	fmt.Fprintf(w, "echo \"text\" | bar build make --subject \"other text\"\n")
	fmt.Fprintf(w, "# Error: cannot provide both --subject flag and stdin input\n")
	fmt.Fprintf(w, "```\n\n")

	fmt.Fprintf(w, "**Generation instructions for LLMs:**\n\n")
	fmt.Fprintf(w, "When generating bar commands:\n")
	fmt.Fprintf(w, "1. **Start with the start symbol** `<command>` and expand top-down\n")

	// Get static token names for the instruction
	staticNames := make([]string, 0, len(grammar.Static.Profiles))
	for name := range grammar.Static.Profiles {
		slug := grammar.slugForToken(name)
		if slug == "" {
			slug = name
		}
		staticNames = append(staticNames, slug)
	}
	sort.Strings(staticNames)
	fmt.Fprintf(w, "2. **Always include a static token** (choose from: %s)\n", strings.Join(staticNames, ", "))

	fmt.Fprintf(w, "3. **Verify token counts** before outputting (scope ≤ 2, method ≤ 3, others ≤ 1)\n")
	fmt.Fprintf(w, "4. **Use slug format** for multi-word tokens (dashes, not spaces)\n")
	fmt.Fprintf(w, "5. **Check token names** against the Token Quick Reference section below\n")
	fmt.Fprintf(w, "6. **Do not add** comments, explanations, or text outside the grammar structure\n")
	fmt.Fprintf(w, "7. **Output only** valid bar command strings\n\n")
}

func renderTokenCheatSheet(w io.Writer, grammar *Grammar, compact bool) {
	fmt.Fprintf(w, "## Token Quick Reference\n\n")
	if !compact {
		fmt.Fprintf(w, "**At-a-glance list of all valid tokens by axis.** Use this to verify token names before diving into detailed descriptions below.\n\n")
	}

	// Tasks
	staticNames := make([]string, 0, len(grammar.Static.Profiles))
	for name := range grammar.Static.Profiles {
		slug := grammar.slugForToken(name)
		if slug == "" {
			slug = name
		}
		staticNames = append(staticNames, slug)
	}
	sort.Strings(staticNames)
	fmt.Fprintf(w, "**Static (required):** %s\n\n", strings.Join(staticNames, ", "))

	// Contract axes in canonical order
	orderedAxes := []string{"completeness", "scope", "method", "form", "channel", "directional"}

	for _, axisName := range orderedAxes {
		tokens, exists := grammar.Axes.Definitions[axisName]
		if !exists {
			continue
		}

		capacity := "0-1"
		if axisName == "scope" {
			capacity = "0-2"
		} else if axisName == "method" {
			capacity = "0-3"
		}

		tokenSlugs := make([]string, 0, len(tokens))
		for token := range tokens {
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			tokenSlugs = append(tokenSlugs, slug)
		}
		sort.Strings(tokenSlugs)

		fmt.Fprintf(w, "**%s (%s):** %s\n\n", strings.Title(axisName), capacity, strings.Join(tokenSlugs, ", "))
	}

	// Persona presets
	if len(grammar.Persona.Presets) > 0 {
		presetNames := make([]string, 0, len(grammar.Persona.Presets))
		for name := range grammar.Persona.Presets {
			slug := grammar.slugForToken(name)
			if slug == "" {
				slug = name
			}
			presetNames = append(presetNames, "persona="+slug)
		}
		sort.Strings(presetNames)
		fmt.Fprintf(w, "**Persona presets:** %s\n\n", strings.Join(presetNames, ", "))
	}

	// Persona axes
	personaAxes := []string{"voice", "audience", "tone", "intent"}
	for _, axisName := range personaAxes {
		tokenList, exists := grammar.Persona.Axes[axisName]
		if !exists || len(tokenList) == 0 {
			continue
		}

		tokenSlugs := make([]string, 0, len(tokenList))
		for _, token := range tokenList {
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			tokenSlugs = append(tokenSlugs, axisName+"="+slug)
		}
		sort.Strings(tokenSlugs)

		fmt.Fprintf(w, "**Persona %s:** %s\n\n", axisName, strings.Join(tokenSlugs, ", "))
	}

	if !compact {
		fmt.Fprintf(w, "---\n\n")
	}
}

func renderTokenCatalog(w io.Writer, grammar *Grammar, compact bool) {
	fmt.Fprintf(w, "## Token Catalog\n\n")

	// Tasks
	fmt.Fprintf(w, "### Tasks (required)\n\n")
	if !compact {
		fmt.Fprintf(w, "Pre-composed prompt strategies:\n\n")
	}
	fmt.Fprintf(w, "| Token | Description |\n")
	fmt.Fprintf(w, "|-------|-------------|\n")

	staticNames := make([]string, 0, len(grammar.Static.Profiles))
	for name := range grammar.Static.Profiles {
		staticNames = append(staticNames, name)
	}
	sort.Strings(staticNames)

	for _, name := range staticNames {
		desc := strings.TrimSpace(grammar.TaskDescription(name))
		if desc == "" {
			desc = "(no description)"
		}
		slug := grammar.slugForToken(name)
		if slug == "" {
			slug = name
		}
		fmt.Fprintf(w, "| `%s` | %s |\n", slug, desc)
	}
	fmt.Fprintf(w, "\n")

	// Contract axes in canonical order
	orderedAxes := []string{"completeness", "scope", "method", "form", "channel", "directional"}

	for _, axisName := range orderedAxes {
		tokens, exists := grammar.Axes.Definitions[axisName]
		if !exists {
			continue
		}

		capacity := "0-1"
		if axisName == "scope" {
			capacity = "0-2"
		} else if axisName == "method" {
			capacity = "0-3"
		}

		fmt.Fprintf(w, "### %s (%s token)\n\n", strings.Title(axisName), capacity)

		fmt.Fprintf(w, "| Token | Description |\n")
		fmt.Fprintf(w, "|-------|-------------|\n")

		tokenNames := make([]string, 0, len(tokens))
		for token := range tokens {
			tokenNames = append(tokenNames, token)
		}
		sort.Strings(tokenNames)

		for _, token := range tokenNames {
			desc := strings.TrimSpace(tokens[token])
			if desc == "" {
				desc = "(no description)"
			}
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			fmt.Fprintf(w, "| `%s` | %s |\n", slug, desc)
		}
		fmt.Fprintf(w, "\n")

		if axisName == "directional" && !compact {
			fmt.Fprintf(w, "**Compound directionals:** Primitive directional tokens can be combined ")
			fmt.Fprintf(w, "into compound tokens (e.g., `fly rog`, `fip rog`, `dip ong`, `dip bog`, `fip ong`). ")
			fmt.Fprintf(w, "A compound token merges the two directional pressures into a single constraint — ")
			fmt.Fprintf(w, "the compound counts as one directional token and does not exceed the axis cap. ")
			fmt.Fprintf(w, "Compound tokens appear in the table above. They are most easily discovered via ")
			fmt.Fprintf(w, "`bar shuffle --json` by inspecting the `directional` field in shuffled output.\n\n")
		}
	}
}

func renderPersonaSystem(w io.Writer, grammar *Grammar, compact bool) {
	fmt.Fprintf(w, "## Persona System\n\n")

	// Preset personas
	if len(grammar.Persona.Presets) > 0 {
		fmt.Fprintf(w, "### Preset Personas\n\n")
		if !compact {
			fmt.Fprintf(w, "Pre-configured combinations of voice, audience, and tone:\n\n")
		}
		fmt.Fprintf(w, "| Preset | Voice | Audience | Tone | Spoken Alias |\n")
		fmt.Fprintf(w, "|--------|-------|----------|------|--------------|\n")

		presetNames := make([]string, 0, len(grammar.Persona.Presets))
		for name := range grammar.Persona.Presets {
			presetNames = append(presetNames, name)
		}
		sort.Strings(presetNames)

		for _, name := range presetNames {
			preset := grammar.Persona.Presets[name]

			voice := "-"
			if preset.Voice != nil && *preset.Voice != "" {
				voice = *preset.Voice
			}

			audience := "-"
			if preset.Audience != nil && *preset.Audience != "" {
				audience = *preset.Audience
			}

			tone := "-"
			if preset.Tone != nil && *preset.Tone != "" {
				tone = *preset.Tone
			}

			spokenAlias := "-"
			if preset.Label != "" {
				spokenAlias = preset.Label
			}

			fmt.Fprintf(w, "| `persona=%s` | %s | %s | %s | %s |\n", name, voice, audience, tone, spokenAlias)
		}
		fmt.Fprintf(w, "\n")
	}

	// Persona axes
	fmt.Fprintf(w, "### Persona Axes (for custom composition)\n\n")
	if !compact {
		fmt.Fprintf(w, "Build custom personas by combining individual axes:\n\n")
	}

	personaAxes := []string{"voice", "audience", "tone", "intent"}
	for _, axisName := range personaAxes {
		tokenList, exists := grammar.Persona.Axes[axisName]
		if !exists {
			continue
		}

		axisDocs := grammar.Persona.Docs[axisName]

		fmt.Fprintf(w, "**%s**:\n\n", strings.Title(axisName))

		tokenNames := make([]string, 0, len(tokenList))
		tokenNames = append(tokenNames, tokenList...)
		sort.Strings(tokenNames)

		fmt.Fprintf(w, "Options: ")
		slugs := make([]string, 0, len(tokenNames))
		for _, token := range tokenNames {
			slug := grammar.slugForToken(token)
			if slug == "" {
				slug = token
			}
			slugs = append(slugs, "`"+slug+"`")
		}
		fmt.Fprintf(w, "%s\n\n", strings.Join(slugs, ", "))

		// Show descriptions if available (skip in compact mode)
		if len(axisDocs) > 0 && !compact {
			fmt.Fprintf(w, "| Token | Description |\n")
			fmt.Fprintf(w, "|-------|-------------|\n")
			for _, token := range tokenNames {
				slug := grammar.slugForToken(token)
				if slug == "" {
					slug = token
				}
				desc := axisDocs[token]
				if desc == "" {
					desc = "(no description)"
				}
				fmt.Fprintf(w, "| `%s` | %s |\n", slug, desc)
			}
			fmt.Fprintf(w, "\n")
		}
	}
}

func renderCompositionRules(w io.Writer, grammar *Grammar, compact bool) {
	fmt.Fprintf(w, "## Composition Rules\n\n")

	if compact {
		fmt.Fprintf(w, "- Order: see Grammar Architecture\n")
		fmt.Fprintf(w, "- Caps: scope 0-2, method 0-3, others 0-1\n")
		if len(grammar.Hierarchy.AxisIncompatibilities) > 0 {
			fmt.Fprintf(w, "- Incompatibilities exist (see full reference)\n")
		}
		fmt.Fprintf(w, "\n")
		return
	}

	fmt.Fprintf(w, "### Token Ordering Constraints\n\n")
	fmt.Fprintf(w, "1. Tokens must appear in the order specified in Grammar Architecture\n")
	fmt.Fprintf(w, "2. Skip stages with sentinels: `//next` (skip current) or `//:stage` (jump to stage)\n")
	fmt.Fprintf(w, "3. After the first `key=value`, all remaining tokens must be `key=value`\n\n")

	fmt.Fprintf(w, "### Soft Caps\n\n")
	if len(grammar.Hierarchy.AxisSoftCaps) > 0 {
		for _, axisName := range []string{"scope", "method", "completeness", "form", "channel", "directional"} {
			if cap, exists := grammar.Hierarchy.AxisSoftCaps[axisName]; exists {
				fmt.Fprintf(w, "- **%s**: maximum %d token(s)\n", strings.Title(axisName), cap)
			}
		}
	} else {
		fmt.Fprintf(w, "- Scope: maximum 2 tokens\n")
		fmt.Fprintf(w, "- Method: maximum 3 tokens\n")
		fmt.Fprintf(w, "- Other axes: maximum 1 token each\n")
	}
	fmt.Fprintf(w, "\n")

	fmt.Fprintf(w, "### Incompatibilities\n\n")
	fmt.Fprintf(w, "Certain token combinations are not allowed or produce low-quality results:\n\n")

	fmt.Fprintf(w, "**Output-exclusive conflicts:**\n")
	fmt.Fprintf(w, "All channel tokens are output-exclusive — they mandate the entire response format. ")
	fmt.Fprintf(w, "At most one channel token may appear per prompt. ")
	fmt.Fprintf(w, "Similarly, form tokens `code`, `html`, and `shellscript` are output-exclusive. ")
	fmt.Fprintf(w, "Combining two output-exclusive tokens produces contradictory instructions the LLM cannot reconcile.\n\n")

	fmt.Fprintf(w, "**Task-affinity restrictions:**\n")
	fmt.Fprintf(w, "- `codetour` channel: appropriate for tasks producing navigable code artifacts (`fix`, `make` with code, `show` with code structure, `pull` from code). ")
	fmt.Fprintf(w, "Not appropriate for non-code tasks: `sim`, `sort`, `probe`, `diff` without code subject, `plan`.\n")
	fmt.Fprintf(w, "- `gherkin` channel: appropriate for tasks mapping to scenario-based behavior specification (`check` for acceptance criteria, `plan` with BDD context, `make` when defining system behavior). ")
	fmt.Fprintf(w, "Not appropriate for tasks that don't involve system behavior: `sort`, `sim`, `probe`.\n")
	fmt.Fprintf(w, "- `code`, `html`, `shellscript` channels: not appropriate for narrative tasks (`sim`, `probe`) that produce prose output rather than code or markup.\n\n")

	fmt.Fprintf(w, "**Prose-form conflicts:**\n")
	fmt.Fprintf(w, "Form tokens that produce structured prose (`case`, `formats`, `walkthrough`, `scaffold`, `recipe`, `faq`, `table`, `taxonomy`, `visual`, `variants`, `checklist`, `actions`) ")
	fmt.Fprintf(w, "conflict with channels that mandate code or markup as the complete output (`code`, `html`, `shellscript`). ")
	fmt.Fprintf(w, "Use prose-producing forms only with channels that support natural language (`jira`, `slack`, `sketch`, `plain`) or with no channel token. ")
	fmt.Fprintf(w, "Exception: `test` form produces test case code and is compatible with `code` channel.\n\n")

	fmt.Fprintf(w, "**Semantic conflicts:**\n")
	fmt.Fprintf(w, "- `rewrite` form implies existing content to transform. ")
	fmt.Fprintf(w, "Pairing with `make` is semantically incoherent: `make` implies creating from nothing while `rewrite` implies transforming existing content.\n\n")

	if len(grammar.Hierarchy.AxisIncompatibilities) > 0 {
		fmt.Fprintf(w, "**Grammar-enforced restrictions:**\n")
		for axis1, conflicts := range grammar.Hierarchy.AxisIncompatibilities {
			for axis2, tokens := range conflicts {
				for _, token := range tokens {
					fmt.Fprintf(w, "- Tokens from `%s` cannot be used with `%s` token `%s`\n", axis1, axis2, token)
				}
			}
		}
		fmt.Fprintf(w, "\n")
	}
}

func renderUsagePatterns(w io.Writer, compact bool) {
	if compact {
		// Skip usage patterns in compact mode
		return
	}
	fmt.Fprintf(w, "## Usage Patterns by Task Type\n\n")
	fmt.Fprintf(w, "**Important**: These examples illustrate common composition patterns to help you understand\n")
	fmt.Fprintf(w, "how tokens combine across axes. They are **reference material for learning grammar and syntax**,\n")
	fmt.Fprintf(w, "not an exhaustive catalog of valid approaches.\n\n")
	fmt.Fprintf(w, "**LLMs should use their own reasoning** to discover appropriate token combinations by:\n")
	fmt.Fprintf(w, "- Consulting the Token Catalog for available tokens and their meanings\n")
	fmt.Fprintf(w, "- Applying the Token Selection Heuristics to the specific request\n")
	fmt.Fprintf(w, "- Composing novel combinations that fit the user's actual needs\n\n")
	fmt.Fprintf(w, "These patterns show **how** tokens work together, not **which** combinations to use.\n")
	fmt.Fprintf(w, "The full token space supports many more combinations than shown here.\n\n")
	fmt.Fprintf(w, "---\n\n")

	patterns := []struct {
		title   string
		command string
		example string
		desc    string
	}{
		{
			title:   "Decision-Making",
			command: "bar build diff thing full branch variants --subject \"...\"",
			example: "bar build diff thing full branch variants --subject \"Choose between Redis and Postgres for caching\"",
			desc:    "Use when choosing between options or evaluating alternatives",
		},
		{
			title:   "Architecture Documentation",
			command: "bar build make struct full explore case --subject \"...\"",
			example: "bar build make struct full explore case --subject \"Document the microservices architecture\"",
			desc:    "Use for creating ADRs or documenting architectural decisions",
		},
		{
			title:   "Explanation/Understanding (Process)",
			command: "bar build show time full flow walkthrough --subject \"...\"",
			example: "bar build show time full flow walkthrough --subject \"Explain the OAuth authentication flow\"",
			desc:    "Use when explaining how something works over time or in sequence",
		},
		{
			title:   "Explanation/Understanding (Concepts)",
			command: "bar build show mean full scaffold --subject \"...\"",
			example: "bar build show mean full scaffold --subject \"What is eventual consistency?\"",
			desc:    "Use when explaining what something means or building conceptual understanding",
		},
		{
			title:   "Structural Analysis",
			command: "bar build probe struct full mapping --subject \"...\"",
			example: "bar build probe struct full mapping --subject \"Analyze the database schema relationships\"",
			desc:    "Use for understanding relationships, boundaries, and structure",
		},
		{
			title:   "Problem Diagnosis",
			command: "bar build probe fail full diagnose checklist --subject \"...\"",
			example: "bar build probe fail full diagnose checklist --subject \"Debug production memory leak\"",
			desc:    "Use for troubleshooting and root cause analysis",
		},
		{
			title:   "Task Planning",
			command: "bar build plan act full converge actions --subject \"...\"",
			example: "bar build plan act full converge actions --subject \"Plan the database migration steps\"",
			desc:    "Use when breaking down work into actionable steps",
		},
		{
			title:   "Exploratory Analysis",
			command: "bar build probe thing full explore variants --subject \"...\"",
			example: "bar build probe thing full explore variants --subject \"What are different approaches to state management?\"",
			desc:    "Use when surveying possibilities or generating alternatives",
		},
		{
			title:   "Comparison/Tradeoff Analysis",
			command: "bar build diff thing full table --subject \"...\"",
			example: "bar build diff thing full table --subject \"Compare REST vs GraphQL vs gRPC for our API\"",
			desc:    "Use for side-by-side comparison of alternatives with tradeoffs",
		},
		{
			title:   "Risk Assessment",
			command: "bar build probe fail full adversarial checklist --subject \"...\"",
			example: "bar build probe fail full adversarial checklist --subject \"Assess risks of migrating to Kubernetes\"",
			desc:    "Use for identifying and evaluating potential risks",
		},
		{
			title:   "Quality Evaluation",
			command: "bar build check good full analysis checklist --subject \"...\"",
			example: "bar build check good full analysis checklist --subject \"Evaluate code review quality standards\"",
			desc:    "Use when assessing quality, standards, or success criteria",
		},
		{
			title:   "Progressive Refinement Workflow",
			command: "bar build probe thing gist explore variants --subject \"...\" && bar build probe struct full mapping table --subject \"...\"",
			example: "bar build probe thing gist explore variants --subject \"API design approaches\" && bar build probe struct full mapping table --subject \"Selected REST API structure\"",
			desc:    "Use for multi-step workflows: explore broadly, then analyze deeply",
		},
		{
			title:   "Conceptual Scaffolding",
			command: "bar build show mean full scaffold --subject \"...\"",
			example: "bar build show mean full scaffold --subject \"Explain CQRS pattern for beginners\"",
			desc:    "Use for building understanding from fundamentals to complex concepts",
		},
		{
			title:   "Failure Mode Analysis",
			command: "bar build probe fail full adversarial variants --subject \"...\"",
			example: "bar build probe fail full adversarial variants --subject \"How could the payment system fail under load?\"",
			desc:    "Use for systematic analysis of how systems can break",
		},
		{
			title:   "Success Criteria Definition",
			command: "bar build make good full analysis checklist --subject \"...\"",
			example: "bar build make good full analysis checklist --subject \"Define success criteria for the dashboard redesign\"",
			desc:    "Use when establishing measurable quality or success standards",
		},
		{
			title:   "Perspective Analysis",
			command: "bar build probe view full explore variants --subject \"...\"",
			example: "bar build probe view full explore variants --subject \"How do different stakeholders view the monolith migration?\"",
			desc:    "Use for understanding multiple viewpoints or stakeholder perspectives",
		},
		{
			title:   "Impact Assessment",
			command: "bar build probe struct full effects table --subject \"...\"",
			example: "bar build probe struct full effects table --subject \"Assess downstream impacts of changing the auth service\"",
			desc:    "Use for analyzing ripple effects and dependencies",
		},
		{
			title:   "Constraint Mapping",
			command: "bar build probe thing full dimension table --subject \"...\"",
			example: "bar build probe thing full dimension table --subject \"Map technical and business constraints for the mobile app\"",
			desc:    "Use for identifying and documenting limitations and requirements",
		},
		{
			title:   "Evidence Building",
			command: "bar build make thing full cite case --subject \"...\"",
			example: "bar build make thing full cite case --subject \"Build the case for adopting TypeScript\"",
			desc:    "Use when making a persuasive argument with supporting evidence",
		},
		{
			title:   "Option Generation with Reasoning",
			command: "bar build probe thing full branch variants --subject \"...\"",
			example: "bar build probe thing full branch variants --subject \"Generate database sharding approaches with pros/cons\"",
			desc:    "Use for generating alternatives with detailed reasoning for each",
		},
		{
			title:   "Sequential Process Documentation",
			command: "bar build make time full flow recipe --subject \"...\"",
			example: "bar build make time full flow recipe --subject \"Document the CI/CD pipeline stages\"",
			desc:    "Use for documenting step-by-step processes or workflows",
		},
		{
			title:   "Scenario Simulation",
			command: "bar build sim time full walkthrough --subject \"...\"",
			example: "bar build sim time full walkthrough --subject \"Simulate what happens during a database failover\"",
			desc:    "Use for playing out hypothetical or contingency scenarios",
		},
		{
			title:   "Dependency Analysis",
			command: "bar build probe struct full depends mapping --subject \"...\"",
			example: "bar build probe struct full depends mapping --subject \"Map service dependencies in the microservices architecture\"",
			desc:    "Use for understanding and visualizing dependencies and relationships",
		},
	}

	for _, p := range patterns {
		fmt.Fprintf(w, "### %s\n\n", p.title)
		fmt.Fprintf(w, "%s\n\n", p.desc)
		fmt.Fprintf(w, "**Pattern:**\n```bash\n%s\n```\n\n", p.command)
		fmt.Fprintf(w, "**Example:**\n```bash\n%s\n```\n\n", p.example)
	}
}

func renderTokenSelectionHeuristics(w io.Writer, compact bool) {
	if compact {
		// Skip heuristics in compact mode
		return
	}
	fmt.Fprintf(w, "## Token Selection Heuristics\n\n")

	fmt.Fprintf(w, "### Choosing Scope\n\n")
	fmt.Fprintf(w, "- **Entities/boundaries** → `thing`, `struct`\n")
	fmt.Fprintf(w, "- **Sequences/change** → `time`\n")
	fmt.Fprintf(w, "- **Understanding/meaning** → `mean`\n")
	fmt.Fprintf(w, "- **Actions/tasks** → `act`\n")
	fmt.Fprintf(w, "- **Quality/criteria** → `good`\n")
	fmt.Fprintf(w, "- **Failure modes** → `fail`\n")
	fmt.Fprintf(w, "- **Perspectives** → `view`\n")
	fmt.Fprintf(w, "- **Premises/preconditions** → `assume`\n")
	fmt.Fprintf(w, "- **Recurring patterns** → `motifs`\n")
	fmt.Fprintf(w, "- **Invariants/stable states** → `stable`\n\n")

	fmt.Fprintf(w, "### Choosing Method\n\n")
	fmt.Fprintf(w, "**Decision Methods:**\n")
	fmt.Fprintf(w, "- Deciding between options → `branch`, `explore`, `prioritize`\n")
	fmt.Fprintf(w, "- Narrowing to recommendation → `converge`, `meld`\n\n")

	fmt.Fprintf(w, "**Understanding Methods:**\n")
	fmt.Fprintf(w, "- Architecture/structure → `mapping`, `systemic`\n")
	fmt.Fprintf(w, "- Process/sequence → `flow`, `depends`\n")
	fmt.Fprintf(w, "- Causes/effects → `effects`, `origin`\n\n")

	fmt.Fprintf(w, "**Exploration Methods:**\n")
	fmt.Fprintf(w, "- Discovering possibilities → `explore`, `shift`, `models`\n")
	fmt.Fprintf(w, "- Deepening analysis → `dimension`, `domains`\n\n")

	fmt.Fprintf(w, "**Diagnostic Methods:**\n")
	fmt.Fprintf(w, "- Root cause analysis → `diagnose`, `inversion`, `adversarial`\n")
	fmt.Fprintf(w, "- Risk/resilience → `risks`, `resilience`\n\n")

	fmt.Fprintf(w, "### Choosing Form\n\n")
	fmt.Fprintf(w, "- **Actionable next steps** → `actions`, `checklist`\n")
	fmt.Fprintf(w, "- **Multiple alternatives** → `variants`\n")
	fmt.Fprintf(w, "- **Step-by-step guidance** → `walkthrough`, `recipe`\n")
	fmt.Fprintf(w, "- **Structured comparison** → `table`\n")
	fmt.Fprintf(w, "- **Building understanding** → `scaffold`\n")
	fmt.Fprintf(w, "- **Decision documentation** → `case`\n\n")
}

func renderAdvancedFeatures(w io.Writer, compact bool) {
	if compact {
		fmt.Fprintf(w, "## Advanced Features\n\n")
		fmt.Fprintf(w, "- `bar shuffle`: Random token generation\n")
		fmt.Fprintf(w, "- `--json`, `--output`, `--input`: Output options\n")
		fmt.Fprintf(w, "- `//next`, `//:stage`: Skip sentinels\n\n")
		return
	}
	fmt.Fprintf(w, "## Advanced Features\n\n")

	fmt.Fprintf(w, "### Shuffle for Exploration\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "bar shuffle [--seed N] [--include axes] [--exclude axes] [--fill 0.0-1.0]\n")
	fmt.Fprintf(w, "```\n\n")
	fmt.Fprintf(w, "Generate random token combinations for exploring the grammar space.\n\n")

	fmt.Fprintf(w, "### Output Formats\n\n")
	fmt.Fprintf(w, "- `--json`: Machine-readable contract output\n")
	fmt.Fprintf(w, "- `--output FILE`: Save to file\n")
	fmt.Fprintf(w, "- `--input FILE`: Read prompt from file\n\n")

	fmt.Fprintf(w, "### Skip Sentinels\n\n")
	fmt.Fprintf(w, "- `//next`: Skip current stage in token ordering\n")
	fmt.Fprintf(w, "- `//:static`: Jump directly to static stage\n")
	fmt.Fprintf(w, "- `//:completeness`: Jump directly to completeness stage\n\n")
}

func renderMetadata(w io.Writer, grammar *Grammar, compact bool) {
	if compact {
		// Skip metadata in compact mode
		return
	}
	fmt.Fprintf(w, "## Grammar Metadata\n\n")
	fmt.Fprintf(w, "- **Schema version**: %s\n", grammar.SchemaVersion)
	fmt.Fprintf(w, "- **Total axes**: 7 (completeness, scope, method, form, channel, directional, persona)\n")

	tokenCount := 0
	for _, tokens := range grammar.Axes.Definitions {
		tokenCount += len(tokens)
	}
	fmt.Fprintf(w, "- **Contract axis tokens**: %d\n", tokenCount)
	fmt.Fprintf(w, "- **Tasks**: %d\n", len(grammar.Static.Profiles))
	fmt.Fprintf(w, "- **Persona presets**: %d\n", len(grammar.Persona.Presets))

	fmt.Fprintf(w, "\n---\n\n")
	fmt.Fprintf(w, "*This reference is generated from the current grammar state. Use `bar help llm` to regenerate.*\n")
}
