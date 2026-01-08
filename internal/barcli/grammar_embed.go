package barcli

import (
	"bytes"
	"fmt"
	"io"

	_ "embed"
)

//go:embed embed/prompt-grammar.json
var embeddedGrammar []byte

// EmbeddedGrammarReader returns an io.Reader for the embedded prompt grammar payload.
func EmbeddedGrammarReader() (io.Reader, error) {
	data, err := embeddedGrammarBytes()
	if err != nil {
		return nil, err
	}
	return bytes.NewReader(data), nil
}

func embeddedGrammarBytes() ([]byte, error) {
	if len(embeddedGrammar) == 0 {
		return nil, fmt.Errorf("embedded grammar payload missing; regenerate with `python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json`")
	}

	return embeddedGrammar, nil
}
