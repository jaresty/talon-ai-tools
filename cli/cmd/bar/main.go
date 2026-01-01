package main

import (
	"context"
	"fmt"
	"os"
)

func main() {
	ctx := context.Background()
	if err := run(ctx, os.Args[1:]); err != nil {
		fmt.Fprintf(os.Stderr, "bar cli error: %v\n", err)
		os.Exit(1)
	}
}

func run(ctx context.Context, args []string) error {
	_ = ctx
	if len(args) > 0 {
		switch args[0] {
		case "--help", "-h":
			printHelp()
			return nil
		case "--version", "-v":
			fmt.Println("bar-cli dev-snapshot")
			return nil
		}
	}
	printHelp()
	return nil
}

func printHelp() {
	fmt.Println("Bar CLI (ADR-0063) — single source of truth scaffold")
	fmt.Println()
	fmt.Println("Usage:")
	fmt.Println("  bar [--help] [--version]")
}
