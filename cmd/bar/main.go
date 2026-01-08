package main

import (
	"os"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

func main() {
	os.Exit(barcli.Run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}
