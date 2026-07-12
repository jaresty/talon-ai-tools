package barcli

import (
	"fmt"
	"sort"
	"strings"
)

const (
	subjectPlaceholder      = "(none provided)"
	sectionReference        = "=== REFERENCE KEY ==="
	sectionTask             = "=== TASK 任務 (DO THIS) ==="
	sectionAddendum         = "=== ADDENDUM 追加 (CLARIFICATION) ==="
	sectionAxes             = "=== AXES 軸 (token types — each governs a different dimension) ==="
	sectionTokens           = "=== TOKENS 役割 ==="
	sectionTokenDefinitions = "=== TOKEN DEFINITIONS 定義 ==="
	sectionCompositionRules = "=== COMPOSITION RULES 合成 (CO-PRESENCE) ===" // ADR-0227
	sectionPersona          = "=== PERSONA 人格 (STANCE) ==="
	sectionSubject          = "=== REQUEST 依頼 ==="
	sectionExecution        = "=== EXECUTION REMINDER ==="
	sectionMeta             = "=== META INTERPRETATION ==="
	sectionFormat           = "=== FORMAT 形式 ==="
	sectionPromptlets       = "Promptlets"
)

// RenderPlainText builds the human-readable output for the CLI.
func RenderPlainText(result *BuildResult) string {
	var b strings.Builder

	// Preamble: plain user voice constant precedes all sections.
	if p := strings.TrimSpace(result.Preamble); p != "" {
		b.WriteString(p)
		b.WriteString("\n\n")
	}

	// REQUEST: task body + addendum + subject merged into one block.
	taskBody := strings.TrimSpace(result.Task)
	taskBody = strings.TrimPrefix(taskBody, "Task:\n")
	taskBody = strings.TrimPrefix(taskBody, "Task:")
	taskBody = strings.TrimSpace(taskBody)

	var requestParts []string
	if taskBody != "" {
		requestParts = append(requestParts, taskBody)
	}
	if strings.TrimSpace(result.Addendum) != "" {
		requestParts = append(requestParts, strings.TrimSpace(result.Addendum))
	}
	subject := strings.TrimSpace(result.Subject)
	if subject != "" {
		requestParts = append(requestParts, subject)
	}
	requestBody := strings.Join(requestParts, "\n\n")
	if requestBody == "" {
		requestBody = subjectPlaceholder
	}
	writeSection(&b, sectionSubject, requestBody)

	// AXES: one bullet per active axis with its role description.
	b.WriteString(sectionAxes)
	b.WriteString("\n")
	if len(result.HydratedConstraints) == 0 {
		b.WriteString("(none)\n\n")
	} else {
		seenAxes := make(map[string]struct{})
		for _, constraint := range result.HydratedConstraints {
			axisKey := strings.ToLower(strings.TrimSpace(constraint.Axis))
			if _, seen := seenAxes[axisKey]; seen {
				continue
			}
			seenAxes[axisKey] = struct{}{}
			desc := ""
			if result.AxisDescriptions != nil {
				desc = result.AxisDescriptions[axisKey]
			}
			if desc != "" {
				fmt.Fprintf(&b, "- %s: %s\n", axisKey, desc)
			} else {
				fmt.Fprintf(&b, "- %s\n", axisKey)
			}
		}
		if ai := strings.TrimSpace(result.AxisInteraction); ai != "" {
			fmt.Fprintf(&b, "%s\n", ai)
		}
		b.WriteString("\n")
	}

	// TOKENS: one bullet per active axis including persona row.
	// Definitions are omitted; load any unfamiliar token with: bar help token <name>
	b.WriteString(sectionTokens)
	b.WriteString("\n")
	if len(result.HydratedConstraints) == 0 && result.Persona == (PersonaResult{}) {
		b.WriteString("(none)\n\n")
	} else {
		b.WriteString("For each token line below (excluding persona = (none)), run `bar help token <slug>` as a Bash tool call, where <slug> is the slug shown after →. The first assistant text after that tool-result block must begin with `Loaded: <slug> (when: \"<one verbatim heuristic trigger phrase from the Heuristics line in the tool result>\")` — a Loaded: line not preceded by a tool-result block containing \"# Token: <slug>\", or whose quoted phrase does not appear verbatim in that tool-result block, does not satisfy this requirement. Skip the tool call only if a compliant `Loaded: <slug> (when: \"...\")` already appears verbatim in the transcript above this TOKENS section; in that case, write `Loaded: <slug> (skip confirmed)` — a skip-confirmed line not preceded by a verbatim `Loaded: <slug> (when: \"...\")` for the same slug in the transcript above does not satisfy this requirement. Once a `Loaded: <slug>` line exists for every slug listed above, write the literal line `Token loads complete.` — a Token derivations block appearing before `Token loads complete.` does not satisfy this requirement; `Token loads complete.` appearing before all required `Loaded:` lines does not satisfy this requirement. Then write the Token derivations block. In the Token derivations block, for each active token write one line of the form `[slug]: \"[quoted trigger phrase from the Loaded: line]\" → [specific effect on this response]` — a derivations line whose quoted phrase does not match the phrase in the corresponding `Loaded:` line does not satisfy this requirement.\n")
		for _, constraint := range result.HydratedConstraints {
			axisKey := strings.ToLower(strings.TrimSpace(constraint.Axis))
			token := strings.TrimSpace(constraint.Token)
			kanji := strings.TrimSpace(constraint.Kanji)
			slug := strings.ReplaceAll(strings.ToLower(token), " ", "-")
			if kanji != "" {
				fmt.Fprintf(&b, "- %s = %s %s  → bar help token %s\n", axisKey, token, kanji, slug)
			} else {
				fmt.Fprintf(&b, "- %s = %s  → bar help token %s\n", axisKey, token, slug)
			}
			if constraint.ConflictNote != "" {
				fmt.Fprintf(&b, "  ↳ %s\n", constraint.ConflictNote)
			}
		}
		personaWritten := false
		for _, p := range result.HydratedPersona {
			axisKey := strings.ToLower(strings.TrimSpace(p.Axis))
			if axisKey == "persona_preset" {
				continue
			}
			tok := strings.TrimSpace(p.Token)
			pKanji := strings.TrimSpace(p.Kanji)
			pSlug := strings.ReplaceAll(strings.ToLower(tok), " ", "-")
			if tok != "" {
				if pKanji != "" {
					fmt.Fprintf(&b, "- %s = %s %s  → bar help token %s\n", axisKey, tok, pKanji, pSlug)
				} else {
					fmt.Fprintf(&b, "- %s = %s  → bar help token %s\n", axisKey, tok, pSlug)
				}
				personaWritten = true
			}
		}
		if !personaWritten {
			b.WriteString("- persona = (none)\n")
		}
		b.WriteString("\n")
	}

	// ADR-0227: inject COMPOSITION RULES section when token co-presence activates compositions.
	if len(result.ActiveCompositions) > 0 {
		b.WriteString(sectionCompositionRules)
		b.WriteString("\n")
		b.WriteString("↓ [Additional rules that apply because specific token combinations are co-present. Applied on top of TOKENS.]\n")
		b.WriteString("For each composition line below, run bar help composition <slug> as a tool call. After the tool-result block appears, write Loaded: <slug> — a Loaded: line not immediately preceded by a tool-result block for that slug does not satisfy this requirement. Skip the tool call only if Loaded: <slug> already appears verbatim in the transcript above this COMPOSITION RULES section; in that case, write Loaded: <slug> again to confirm. Once a `Loaded: <slug>` line exists for every slug listed above, write the literal line `Token loads complete.` — a Token derivations block appearing before `Token loads complete.` does not satisfy this requirement; `Token loads complete.` appearing before all required `Loaded:` lines does not satisfy this requirement. Then write the Token derivations block. Each composition is a binding constraint on this response — its rules apply throughout.\n")
		for _, comp := range result.ActiveCompositions {
			name := strings.TrimSpace(comp.Name)
			fmt.Fprintf(&b, "- %s  → bar help composition %s\n", name, name)
		}
		b.WriteString("\n")
	}

	writeSection(&b, sectionFormat, result.PlanningDirective)
	writeSection(&b, sectionMeta, result.MetaInterpretationGuidance)

	return strings.TrimRight(b.String(), "\n") + "\n"
}

// buildPersonaTokenSummary returns a short token summary string for the TOKENS row,
// or empty string when no persona axes are active.
func buildPersonaTokenSummary(p PersonaResult) string {
	var parts []string
	if p.Preset != "" {
		parts = append(parts, p.Preset)
	} else {
		if p.Voice != "" {
			parts = append(parts, p.Voice)
		}
		if p.Audience != "" {
			parts = append(parts, p.Audience)
		}
		if p.Tone != "" {
			parts = append(parts, p.Tone)
		}
		if p.Intent != "" {
			parts = append(parts, p.Intent)
		}
	}
	return strings.Join(parts, ", ")
}

// writePersonaDefinitionRow emits one "- <axis> (<token>): <desc>" line per persona axis
// into TOKEN DEFINITIONS, matching the format of constraint token lines.
func writePersonaDefinitionRow(b *strings.Builder, promptlets []HydratedPromptlet) {
	written := false
	for _, p := range promptlets {
		axisKey := strings.ToLower(strings.TrimSpace(p.Axis))
		if axisKey == "persona_preset" {
			continue
		}
		tok := strings.TrimSpace(p.Token)
		kanji := strings.TrimSpace(p.Kanji)
		desc := strings.TrimSpace(p.Description)
		if tok == "" {
			continue
		}
		tokenWithKanji := tok
		if kanji != "" {
			tokenWithKanji = fmt.Sprintf("%s %s", tok, kanji)
		}
		if desc != "" {
			fmt.Fprintf(b, "- %s (%s): %s\n", axisKey, tokenWithKanji, desc)
		} else {
			fmt.Fprintf(b, "- %s (%s)\n", axisKey, tokenWithKanji)
		}
		written = true
	}
	if !written {
		b.WriteString("- persona (none): No communication-identity styling applied.\n")
	}
}

func writeSection(b *strings.Builder, heading string, body string) {
	b.WriteString(heading)
	b.WriteString("\n")
	if strings.TrimSpace(body) == "" {
		b.WriteString("(none)\n\n")
		return
	}
	b.WriteString(body)
	b.WriteString("\n\n")
}

// writeSectionWithContract writes a section header, an optional inline contract
// line sourced from the grammar's ReferenceKeyContracts (ADR-0176), then the body.
func writeSectionWithContract(b *strings.Builder, heading string, contract string, body string) {
	b.WriteString(heading)
	b.WriteString("\n")
	if c := strings.TrimSpace(contract); c != "" {
		fmt.Fprintf(b, "↓ [%s]\n", c)
	}
	if strings.TrimSpace(body) == "" {
		b.WriteString("(none)\n\n")
		return
	}
	b.WriteString(body)
	b.WriteString("\n\n")
}

func writePersonaSection(b *strings.Builder, persona PersonaResult, promptlets []HydratedPromptlet, contract string) bool {
	axisEntries := make(map[string][]HydratedPromptlet)
	hasPromptletData := false
	for _, entry := range promptlets {
		axisKey := strings.ToLower(strings.TrimSpace(entry.Axis))
		if axisKey == "" || axisKey == "persona_preset" {
			continue
		}
		axisEntries[axisKey] = append(axisEntries[axisKey], entry)
		if strings.TrimSpace(entry.Token) != "" || strings.TrimSpace(entry.Description) != "" {
			hasPromptletData = true
		}
	}

	hasPersona := persona != (PersonaResult{})
	if !hasPersona && !hasPromptletData {
		return false
	}

	b.WriteString(sectionPersona)
	b.WriteString("\n")
	if c := strings.TrimSpace(contract); c != "" {
		fmt.Fprintf(b, "↓ [%s]\n", c)
	}

	if persona.Preset != "" {
		label := persona.Preset
		if persona.PresetLabel != "" && persona.PresetLabel != persona.Preset {
			label = fmt.Sprintf("%s — %s", persona.Preset, persona.PresetLabel)
		}
		fmt.Fprintf(b, "- Preset: %s\n", label)
	}

	type axisDisplay struct {
		key   string
		label string
		value string
	}

	axisOrder := []axisDisplay{
		{key: "voice", label: "Voice", value: persona.Voice},
		{key: "audience", label: "Audience", value: persona.Audience},
		{key: "tone", label: "Tone", value: persona.Tone},
		{key: "intent", label: "Intent", value: persona.Intent},
	}

	for _, axis := range axisOrder {
		token := strings.TrimSpace(axis.value)
		desc := ""
		kanji := ""
		entries := axisEntries[axis.key]
		tokens := make([]string, 0, len(entries))
		for _, entry := range entries {
			if t := strings.TrimSpace(entry.Token); t != "" {
				tokens = append(tokens, t)
			}
			if desc == "" && strings.TrimSpace(entry.Description) != "" {
				desc = strings.TrimSpace(entry.Description)
			}
			if kanji == "" && strings.TrimSpace(entry.Kanji) != "" {
				kanji = strings.TrimSpace(entry.Kanji)
			}
		}
		if token == "" && len(tokens) > 0 {
			deduped := dedupeInOrder(tokens)
			token = strings.Join(deduped, ", ")
		}

		if token == "" && desc == "" {
			delete(axisEntries, axis.key)
			continue
		}

		tokenWithKanji := token
		if kanji != "" {
			tokenWithKanji = fmt.Sprintf("%s %s", token, kanji)
		}

		if token == "" {
			fmt.Fprintf(b, "- %s — %s\n", axis.label, desc)
		} else if desc == "" {
			fmt.Fprintf(b, "- %s (%s)\n", axis.label, tokenWithKanji)
		} else {
			fmt.Fprintf(b, "- %s (%s): %s\n", axis.label, tokenWithKanji, desc)
		}

		delete(axisEntries, axis.key)
	}

	noteLines := make([]string, 0)
	if len(axisEntries) > 0 {
		keys := make([]string, 0, len(axisEntries))
		for key := range axisEntries {
			keys = append(keys, key)
		}
		sort.Strings(keys)
		for _, key := range keys {
			entries := axisEntries[key]
			for _, entry := range entries {
				formatted := strings.TrimSpace(renderPromptlet(entry))
				if formatted == "" {
					continue
				}
				noteLines = append(noteLines, formatted)
			}
		}
	}

	if len(noteLines) > 0 {
		fmt.Fprintf(b, "- Additional stance notes:\n")
		for _, line := range noteLines {
			fmt.Fprintf(b, "  • %s\n", line)
		}
	}

	return true
}
