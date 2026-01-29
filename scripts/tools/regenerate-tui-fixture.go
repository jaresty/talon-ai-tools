package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

type tuiFixtureFile struct {
	Tokens          []string `json:"tokens"`
	Subject         string   `json:"subject"`
	ExpectedPreview string   `json:"expected_preview"`
	ExpectedView    string   `json:"expected_view"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <fixture-path> [grammar-path]\n", os.Args[0])
		os.Exit(1)
	}

	fixturePath := os.Args[1]
	grammarPath := "cmd/bar/testdata/grammar.json"
	if len(os.Args) > 2 {
		grammarPath = os.Args[2]
	}

	// Load existing fixture to get tokens and subject
	data, err := os.ReadFile(fixturePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "read fixture: %v\n", err)
		os.Exit(1)
	}
	var fixture tuiFixtureFile
	if err := json.Unmarshal(data, &fixture); err != nil {
		fmt.Fprintf(os.Stderr, "parse fixture: %v\n", err)
		os.Exit(1)
	}

	// Load grammar
	grammar, err := barcli.LoadGrammar(grammarPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "load grammar: %v\n", err)
		os.Exit(1)
	}

	// Build token categories
	tokenCategories := barcli.BuildTokenCategories(grammar)

	// Preview function
	preview := func(subject string, tokens []string) (string, error) {
		result, buildErr := barcli.Build(grammar, tokens)
		if buildErr != nil {
			return "", fmt.Errorf("build prompt: %s", buildErr.Message)
		}
		result.Subject = subject
		result.PlainText = barcli.RenderPlainText(result)
		return result.PlainText, nil
	}

	// Generate snapshot
	opts := bartui.Options{
		Tokens:          fixture.Tokens,
		TokenCategories: tokenCategories,
		Preview:         preview,
	}
	view, previewOutput, err := bartui.Snapshot(opts, fixture.Subject)
	if err != nil {
		fmt.Fprintf(os.Stderr, "generate snapshot: %v\n", err)
		os.Exit(1)
	}

	// Update fixture with new expected values
	fixture.ExpectedPreview = previewOutput
	fixture.ExpectedView = view

	// Write updated fixture
	output, err := json.MarshalIndent(fixture, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "marshal fixture: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(fixturePath, append(output, '\n'), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "write fixture: %v\n", err)
		os.Exit(1)
	}

	absPath, _ := filepath.Abs(fixturePath)
	fmt.Printf("✓ Regenerated fixture: %s\n", absPath)
}
