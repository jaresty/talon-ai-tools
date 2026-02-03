package main

import (
	"os"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

// barVersion is set at build time via -ldflags "-X main.barVersion=x.y.z"
var barVersion = "dev"

func main() {
	// Pass version to barcli for update checks
	barcli.SetVersion(barVersion)
	os.Exit(barcli.Run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}
