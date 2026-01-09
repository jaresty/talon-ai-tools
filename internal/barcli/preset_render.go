package barcli

import (
	"fmt"
	"io"
	"strings"
	"text/tabwriter"
	"time"
)

func writePresetTable(w io.Writer, presets []presetSummary) {
	tw := tabwriter.NewWriter(w, 0, 2, 2, ' ', 0)
	fmt.Fprintf(tw, "NAME\tSAVED AT\tSTATIC\tVOICE\tAUDIENCE\tTONE\n")
	for _, preset := range presets {
		fmt.Fprintf(
			tw,
			"%s\t%s\t%s\t%s\t%s\t%s\n",
			preset.Name,
			formatTime(preset.SavedAt),
			safePlaceholder(preset.Static),
			safePlaceholder(preset.Voice),
			safePlaceholder(preset.Audience),
			safePlaceholder(preset.Tone),
		)
	}
	tw.Flush()
}

func renderPresetDetails(w io.Writer, preset *presetFile) {
	fmt.Fprintf(w, "Preset: %s\n", preset.Name)
	fmt.Fprintf(w, "Saved: %s\n", formatTime(preset.SavedAt))
	fmt.Fprintf(w, "Tokens: %s\n", strings.Join(preset.Tokens, " "))
	fmt.Fprintf(w, "Static prompt: %s\n", safePlaceholder(preset.Result.Axes.Static))
	fmt.Fprintf(w, "Persona voice: %s\n", safePlaceholder(preset.Result.Persona.Voice))
	fmt.Fprintf(w, "Persona audience: %s\n", safePlaceholder(preset.Result.Persona.Audience))
	fmt.Fprintf(w, "Persona tone: %s\n", safePlaceholder(preset.Result.Persona.Tone))
	fmt.Fprintf(w, "Intent: %s\n", safePlaceholder(preset.Result.Persona.Intent))
	fmt.Fprintf(w, "Subject: (not stored; supply when rebuilding)\n")
	fmt.Fprintf(w, "Plain text: (re-run 'bar preset use %s' with a new prompt to render)\n", preset.Name)
}

func formatTime(t time.Time) string {
	if t.IsZero() {
		return "(unknown)"
	}
	return t.UTC().Format(time.RFC3339)
}

func safePlaceholder(value string) string {
	value = strings.TrimSpace(value)
	if value == "" {
		return "(none)"
	}
	return value
}

func indentBlock(body string, prefix string) string {
	trimmed := strings.TrimRight(body, "\n")
	if trimmed == "" {
		return prefix + "(none)"
	}
	lines := strings.Split(trimmed, "\n")
	for i, line := range lines {
		lines[i] = prefix + line
	}
	return strings.Join(lines, "\n")
}
