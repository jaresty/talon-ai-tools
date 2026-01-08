package barcli

import (
	"fmt"
	"strings"
)

const (
	subjectPlaceholder = "(none provided)"
	sectionTask        = "=== TASK (DO THIS) ==="
	sectionConstraints = "=== CONSTRAINTS (GUARDRAILS) ==="
	sectionPersona     = "=== PERSONA (STANCE) ==="
	sectionSubject     = "=== SUBJECT (CONTEXT) ==="
	sectionPromptlets  = "Promptlets"
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

	personasSectionWritten := false
	persona := result.Persona
	if persona != (PersonaResult{}) {
		writePersonaLine := func(format string, values ...any) {
			if !personasSectionWritten {
				b.WriteString(sectionPersona)
				b.WriteString("\n")
				personasSectionWritten = true
			}
			fmt.Fprintf(&b, format+"\n", values...)
		}

		if persona.Preset != "" {
			label := persona.Preset
			if persona.PresetLabel != "" && persona.PresetLabel != persona.Preset {
				label = fmt.Sprintf("%s — %s", persona.Preset, persona.PresetLabel)
			}
			writePersonaLine("- Preset: %s", label)
		}
		if persona.Voice != "" {
			writePersonaLine("- Voice: %s", persona.Voice)
		}
		if persona.Audience != "" {
			writePersonaLine("- Audience: %s", persona.Audience)
		}
		if persona.Tone != "" {
			writePersonaLine("- Tone: %s", persona.Tone)
		}
		if persona.Intent != "" {
			writePersonaLine("- Intent: %s", persona.Intent)
		}
	}

	promptletsWritten := false
	for _, entry := range result.HydratedPersona {
		if entry.Axis == "persona_preset" {
			continue
		}
		if !personasSectionWritten {
			b.WriteString(sectionPersona)
			b.WriteString("\n")
			personasSectionWritten = true
		}
		if !promptletsWritten {
			fmt.Fprintf(&b, "- %s:\n", sectionPromptlets)
			promptletsWritten = true
		}
		fmt.Fprintf(&b, "  • %s\n", formatPromptlet(entry))
	}

	if personasSectionWritten {
		b.WriteString("\n")
	} else {
		writeSection(&b, sectionPersona, "(none)")
	}

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
