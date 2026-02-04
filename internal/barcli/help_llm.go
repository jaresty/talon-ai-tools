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
		fmt.Fprintf(w, "bar build <tokens>... --prompt \"your text\"\n")
		fmt.Fprintf(w, "```\n\n")
		return
	}
	fmt.Fprintf(w, "## Quick Start\n\n")
	fmt.Fprintf(w, "Bar constructs structured prompts by combining tokens from multiple axes:\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "# Basic usage\n")
	fmt.Fprintf(w, "bar build <tokens>... --prompt \"your text\"\n\n")
	fmt.Fprintf(w, "# Example: Decision-making prompt\n")
	fmt.Fprintf(w, "bar build thing full branch variants --prompt \"Choose between Redis and Postgres\"\n\n")
	fmt.Fprintf(w, "# Example: Understanding flow\n")
	fmt.Fprintf(w, "bar build time full flow walkthrough --prompt \"Explain the authentication process\"\n")
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
	fmt.Fprintf(w, "- **Static prompts**: 0-1 token\n")
	fmt.Fprintf(w, "- **Completeness**: 0-1 token\n")
	fmt.Fprintf(w, "- **Scope**: 0-2 tokens\n")
	fmt.Fprintf(w, "- **Method**: 0-3 tokens\n")
	fmt.Fprintf(w, "- **Form**: 0-1 token\n")
	fmt.Fprintf(w, "- **Channel**: 0-1 token\n")
	fmt.Fprintf(w, "- **Directional**: 0-1 token\n")
	fmt.Fprintf(w, "- **Persona**: voice, audience, tone, intent axes or preset\n\n")

	fmt.Fprintf(w, "### Key=Value Override Syntax\n\n")
	fmt.Fprintf(w, "After the first `key=value` override, all remaining tokens must use `key=value` format:\n\n")
	fmt.Fprintf(w, "```bash\n")
	fmt.Fprintf(w, "bar build todo focus method=branch form=table --prompt \"text\"\n")
	fmt.Fprintf(w, "```\n\n")
}

func renderTokenCatalog(w io.Writer, grammar *Grammar, compact bool) {
	fmt.Fprintf(w, "## Token Catalog\n\n")

	// Static prompts
	fmt.Fprintf(w, "### Static Prompts (0-1 token)\n\n")
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
		desc := strings.TrimSpace(grammar.StaticPromptDescription(name))
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

	if len(grammar.Hierarchy.AxisIncompatibilities) > 0 {
		fmt.Fprintf(w, "### Incompatibilities\n\n")
		fmt.Fprintf(w, "Certain token combinations are not allowed:\n\n")

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

	patterns := []struct {
		title   string
		command string
		example string
		desc    string
	}{
		{
			title:   "Decision-Making",
			command: "bar build thing full branch variants --prompt \"...\"",
			example: "bar build thing full branch variants --prompt \"Choose between Redis and Postgres for caching\"",
			desc:    "Use when choosing between options or evaluating alternatives",
		},
		{
			title:   "Architecture Documentation",
			command: "bar build struct full explore case adr --prompt \"...\"",
			example: "bar build struct full explore case adr --prompt \"Document the microservices architecture\"",
			desc:    "Use for creating ADRs or documenting architectural decisions",
		},
		{
			title:   "Explanation/Understanding (Process)",
			command: "bar build time full flow walkthrough --prompt \"...\"",
			example: "bar build time full flow walkthrough --prompt \"Explain the OAuth authentication flow\"",
			desc:    "Use when explaining how something works over time or in sequence",
		},
		{
			title:   "Explanation/Understanding (Concepts)",
			command: "bar build mean full scaffold --prompt \"...\"",
			example: "bar build mean full scaffold --prompt \"What is eventual consistency?\"",
			desc:    "Use when explaining what something means or building conceptual understanding",
		},
		{
			title:   "Structural Analysis",
			command: "bar build struct full mapping --prompt \"...\"",
			example: "bar build struct full mapping --prompt \"Analyze the database schema relationships\"",
			desc:    "Use for understanding relationships, boundaries, and structure",
		},
		{
			title:   "Problem Diagnosis",
			command: "bar build fail full diagnose checklist --prompt \"...\"",
			example: "bar build fail full diagnose checklist --prompt \"Debug production memory leak\"",
			desc:    "Use for troubleshooting and root cause analysis",
		},
		{
			title:   "Task Planning",
			command: "bar build act full prioritize actions --prompt \"...\"",
			example: "bar build act full prioritize actions --prompt \"Plan the database migration steps\"",
			desc:    "Use when breaking down work into actionable steps",
		},
		{
			title:   "Exploratory Analysis",
			command: "bar build thing full explore variants --prompt \"...\"",
			example: "bar build thing full explore variants --prompt \"What are different approaches to state management?\"",
			desc:    "Use when surveying possibilities or generating alternatives",
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
	fmt.Fprintf(w, "- **Perspectives** → `view`\n\n")

	fmt.Fprintf(w, "### Choosing Method\n\n")
	fmt.Fprintf(w, "**Decision Methods:**\n")
	fmt.Fprintf(w, "- Deciding between options → `branch`, `compare`, `prioritize`\n")
	fmt.Fprintf(w, "- Evaluating constraints → `constraints`, `tradeoff`\n\n")

	fmt.Fprintf(w, "**Understanding Methods:**\n")
	fmt.Fprintf(w, "- Architecture/structure → `mapping`, `structure`\n")
	fmt.Fprintf(w, "- Process flow → `flow`, `sequence`\n")
	fmt.Fprintf(w, "- Relationships → `dependencies`, `impacts`\n\n")

	fmt.Fprintf(w, "**Exploration Methods:**\n")
	fmt.Fprintf(w, "- Discovering possibilities → `explore`, `diverge`, `survey`\n")
	fmt.Fprintf(w, "- Generating alternatives → `variants`, `options`\n\n")

	fmt.Fprintf(w, "**Diagnostic Methods:**\n")
	fmt.Fprintf(w, "- Root cause analysis → `diagnose`, `failure`, `stress`\n")
	fmt.Fprintf(w, "- Risk assessment → `risks`, `vulnerabilities`\n\n")

	fmt.Fprintf(w, "### Choosing Form\n\n")
	fmt.Fprintf(w, "- **Actionable next steps** → `actions`, `checklist`, `tasks`\n")
	fmt.Fprintf(w, "- **Multiple alternatives** → `variants`, `options`\n")
	fmt.Fprintf(w, "- **Step-by-step guidance** → `walkthrough`, `recipe`, `flow`\n")
	fmt.Fprintf(w, "- **Structured comparison** → `table`, `matrix`\n")
	fmt.Fprintf(w, "- **Building understanding** → `scaffold`\n")
	fmt.Fprintf(w, "- **Decision documentation** → `case`, `adr`, `log`\n\n")
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
	fmt.Fprintf(w, "- **Static prompts**: %d\n", len(grammar.Static.Profiles))
	fmt.Fprintf(w, "- **Persona presets**: %d\n", len(grammar.Persona.Presets))

	fmt.Fprintf(w, "\n---\n\n")
	fmt.Fprintf(w, "*This reference is generated from the current grammar state. Use `bar help llm` to regenerate.*\n")
}
