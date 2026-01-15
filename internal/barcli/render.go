package barcli

import (
	"fmt"
	"sort"
	"strings"
)

const (
	subjectPlaceholder = "(none provided)"
	sectionReference   = "=== REFERENCE KEY ==="
	sectionTask        = "=== TASK (DO THIS) ==="
	sectionConstraints = "=== CONSTRAINTS (GUARDRAILS) ==="
	sectionPersona     = "=== PERSONA (STANCE) ==="
	sectionSubject     = "=== SUBJECT (CONTEXT) ==="
	sectionPromptlets  = "Promptlets"

	referenceKeyText = `This prompt uses structured tokens. Interpret each section as follows:

TASK: The primary action to perform. Execute this goal directly.

CONSTRAINTS: Independent guardrails that shape HOW to complete the task.
  • Completeness — coverage depth: how thoroughly to fill the territory
  • Scope — boundary fence: which conceptual territory is in-bounds
  • Method — reasoning tool: which approach to use for thinking
  • Form — output shape: structural format of the response
  • Channel — delivery context: format conventions for the platform
  • Directional — thinking lens: perspective filter for reasoning

PERSONA: Communication identity that shapes delivery.
  • Voice — speaker identity: who is speaking
  • Audience — recipient identity: who the message is for
  • Tone — relational register: emotional modulation
  • Intent — interaction purpose: why this response is needed

SUBJECT: The content to work with. Apply task and constraints to this material.`
)

// RenderPlainText builds the human-readable output for the CLI.
func RenderPlainText(result *BuildResult) string {
	var b strings.Builder

	taskBody := strings.TrimSpace(result.Task)
	taskBody = strings.TrimPrefix(taskBody, "Task:\n")
	taskBody = strings.TrimPrefix(taskBody, "Task:")
	taskBody = strings.TrimSpace(taskBody)
	writeSection(&b, sectionTask, taskBody)

	b.WriteString(sectionConstraints)

	b.WriteString("\n")
	if len(result.Constraints) == 0 {
		b.WriteString("(none)\n\n")
	} else {
		for i, constraint := range result.Constraints {
			fmt.Fprintf(&b, "%d. %s\n", i+1, constraint)
		}
		b.WriteString("\n")
	}

	if writePersonaSection(&b, result.Persona, result.HydratedPersona) {
		b.WriteString("\n")
	} else {
		writeSection(&b, sectionPersona, "(none)")
	}

	// Add reference key before subject to help LLMs interpret the structure
	// (placed here so users see their task/constraints/persona first in previews)
	writeSection(&b, sectionReference, referenceKeyText)

	subject := subjectPlaceholder
	if strings.TrimSpace(result.Subject) != "" {
		subject = strings.TrimSpace(result.Subject)
	}
	writeSection(&b, sectionSubject, subject)

	return strings.TrimRight(b.String(), "\n") + "\n"
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

func writePersonaSection(b *strings.Builder, persona PersonaResult, promptlets []HydratedPromptlet) bool {
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
		entries := axisEntries[axis.key]
		tokens := make([]string, 0, len(entries))
		for _, entry := range entries {
			if t := strings.TrimSpace(entry.Token); t != "" {
				tokens = append(tokens, t)
			}
			if desc == "" && strings.TrimSpace(entry.Description) != "" {
				desc = strings.TrimSpace(entry.Description)
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

		if token == "" {
			fmt.Fprintf(b, "- %s — %s\n", axis.label, desc)
		} else if desc == "" {
			fmt.Fprintf(b, "- %s: %s\n", axis.label, token)
		} else {
			fmt.Fprintf(b, "- %s: %s — %s\n", axis.label, token, desc)
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
				formatted := strings.TrimSpace(formatPromptlet(entry))
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
