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
	sectionLateralSeed      = "=== LATERAL SEED 種 ==="
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
		b.WriteString("Issue all `bar help token <slug>` calls in a single Bash tool call joined with `&&` before writing any `Loaded:` lines.\n\nFor each slug in this TOKENS section's bullet list (excluding `persona = (none)`), run `bar help token <slug>` as a Bash tool call. You may append `--skip \"<phrase>\"` where `<phrase>` is a verbatim substring of that token's Definition or Heuristics known from this session — the binary emits a one-line confirmation when the phrase matches, or full output when it does not. Either output satisfies the tool-result requirement. A `Loaded: <slug>` line is valid if and only if a tool-result block whose first line is `# Token: <slug>` or `# Token: <slug> (confirmed: \"...\")` appears in this transcript above this TOKENS section than the `Loaded:` line, and the `Loaded:` line's `when:` value is a verbatim complete semicolon-delimited phrase from the `Heuristics` line of that tool-result block (or the confirmed phrase when a confirmation line appeared), and the `not:` value is a different verbatim complete semicolon-delimited phrase from the same `Heuristics` line.\n\nThe `Loaded:` line form is: `Loaded: <slug> (when: \"<phrase>\" — not: \"<phrase>\" — because: <reason this token applies to this invocation>)`. The `because:` value must name why this token is being applied — a token present in the TOKENS list is always applied; its presence is the decision. A `because:` value that questions applicability, concludes the token is unnecessary, or declines to apply it is a validity violation — the token is mandatory if listed.\n\nDo not skip based on memory or inference — the call is always required.\n\nIn a parallel batch, the `Loaded:` lines for all slugs in the batch must appear as consecutive lines in the next assistant output block — one per slug, in the order their tool-result blocks appeared, beginning with the next line of assistant output that is not itself a tool-result block.\n\nBefore writing `Token loads complete.`, write: `Loads verified: <slug1>, ... (<N> of <N>)` where N is the count of distinct valid `Loaded: <slug>` lines appearing above this line in the transcript, each for a slug in this TOKENS section's bullet list. Then write `Token loads complete.`\n\nIn the Token derivations block, for each active token write: `[slug]: \"[verbatim Heuristics phrase from the tool-result block whose first line is # Token: <slug>, appearing above the valid Loaded: line for this slug]\" → \"[verbatim Description text up to the first ' —' or first '.'; if neither appears, use full Description]\" as applied here: [manifestation in this response]`. A derivations line whose `→` clause does not appear verbatim in that tool-result block does not satisfy this requirement.\n\n`Token loads complete.` is not a turn-end signal and no user message may appear between it and the Token derivations block.\n")
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

	// ADR-0227: inject COMPOSITION RULES section when token co-presence activates compositions with non-empty prose.
	var nonEmptyCompositions []Composition
	for _, comp := range result.ActiveCompositions {
		if strings.TrimSpace(comp.Prose) != "" {
			nonEmptyCompositions = append(nonEmptyCompositions, comp)
		}
	}
	if len(nonEmptyCompositions) > 0 {
		b.WriteString(sectionCompositionRules)
		b.WriteString("\n")
		b.WriteString("↓ [Additional rules that apply because specific token combinations are co-present. Applied on top of TOKENS.]\n")
		b.WriteString("Issue all `bar help composition <slug>` calls in a single parallel batch before writing any `Composition active:` lines.\n\nFor each composition line below, run `bar help composition <slug>` as a tool call. You may append `--skip \"<phrase>\"` where `<phrase>` is a verbatim substring of the composition prose known from this session — the binary emits a one-line confirmation when the phrase matches, or full output when it does not. Either output satisfies the tool-result requirement. The call is always required — do not skip based on memory or inference. After the tool-result block appears, write `Loaded: <slug>` — a `Loaded:` line not preceded by a tool-result block for that slug does not satisfy this requirement. After writing `Loaded: <slug>`, immediately write `Composition active: <slug> (when: \"<verbatim condition from the composition rule body that applies to this invocation>\" — because: <reason this specific invocation activates it>)` — a `Composition active:` line not appearing immediately after a `Loaded: <slug>` line does not satisfy this requirement; a `Composition active:` line whose `when:` value is not a verbatim substring of the composition rule body returned by `bar help composition <slug>` does not satisfy this requirement. All `Loaded:` and `Composition active:` pairs for every slug listed here must appear before the `Token loads complete.` line from the TOKENS section above. Each composition is a binding constraint on this response — its rules apply throughout.\n")
		for _, comp := range nonEmptyCompositions {
			name := strings.TrimSpace(comp.Name)
			fmt.Fprintf(&b, "- %s  → bar help composition %s\n", name, name)
		}
		b.WriteString("\n")
	}

	writeSection(&b, sectionFormat, result.PlanningDirective)
	writeSection(&b, sectionMeta, result.MetaInterpretationGuidance)

	// LATERAL SEED: opt-in creative seed injected via --seed-words. Emitted only
	// when words are present, so a build without the flag is byte-identical to before.
	if len(result.LateralSeed) > 0 {
		writeSection(&b, sectionLateralSeed, lateralSeedBody(result.LateralSeed))
	}

	return strings.TrimRight(b.String(), "\n") + "\n"
}

// lateralSeedBody renders the seed words and soft framing. Singular framing asks
// the model to let the one word inform its approach; plural framing points at the
// interplay between the words, since combination is where the useful jumps come from.
func lateralSeedBody(words []string) string {
	quoted := make([]string, len(words))
	for i, w := range words {
		quoted[i] = fmt.Sprintf("%q", w)
	}
	joined := strings.Join(quoted, ", ")
	if len(words) == 1 {
		return fmt.Sprintf("Lateral seed: %s. Let this word inform your approach where it productively can — as an angle, metaphor, or association. Do not force it, and do not treat it as part of the request.", joined)
	}
	return fmt.Sprintf("Lateral seed: %s. Let the interplay between these words inform your approach where it productively can — as an angle, metaphor, or association. Do not force them, and do not treat them as part of the request.", joined)
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
