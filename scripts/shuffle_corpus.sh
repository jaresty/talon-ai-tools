#!/usr/bin/env bash
# Generate a reproducible corpus of shuffled prompts for catalog evaluation

set -euo pipefail

# Default values
COUNT=50
OUTPUT_DIR="docs/adr/evidence/0085/corpus"
SEED_START=1
FILL=0.5
BAR_CMD="./bar"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --count)
      COUNT="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --seed-start)
      SEED_START="$2"
      shift 2
      ;;
    --fill)
      FILL="$2"
      shift 2
      ;;
    --bar)
      BAR_CMD="$2"
      shift 2
      ;;
    --help)
      cat <<EOF
Usage: $0 [OPTIONS]

Generate a reproducible corpus of shuffled prompts for catalog evaluation.

Options:
  --count N          Number of prompts to generate (default: 50)
  --output DIR       Output directory (default: docs/adr/evidence/0085/corpus)
  --seed-start N     Starting seed value (default: 1)
  --fill PROB        Fill probability for shuffle (default: 0.5)
  --bar PATH         Path to bar binary (default: ./bar)
  --help             Show this help message

Examples:
  # Generate 50 prompts with default settings
  $0

  # Generate 10 test prompts to /tmp
  $0 --count 10 --output /tmp/test_corpus

  # Generate prompts with high fill probability
  $0 --count 20 --fill 0.9

  # Use installed bar command
  $0 --bar bar
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run with --help for usage information" >&2
      exit 1
      ;;
  esac
done

# Validate bar command exists
if ! command -v "$BAR_CMD" &> /dev/null; then
  echo "Error: bar command not found at '$BAR_CMD'" >&2
  echo "Build with 'go build ./cmd/bar' or specify path with --bar" >&2
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Generating $COUNT shuffled prompts..."
echo "Output directory: $OUTPUT_DIR"
echo "Seed range: $SEED_START to $((SEED_START + COUNT - 1))"
echo "Fill probability: $FILL"
echo ""

# Generate corpus
for ((i=0; i<COUNT; i++)); do
  seed=$((SEED_START + i))
  output_file="$OUTPUT_DIR/shuffle_$(printf "%04d" $seed).json"

  if "$BAR_CMD" shuffle --seed "$seed" --fill "$FILL" --json > "$output_file" 2>/dev/null; then
    echo "✓ Generated shuffle_$(printf "%04d" $seed).json (seed=$seed)"
  else
    echo "✗ Failed to generate shuffle_$(printf "%04d" $seed).json (seed=$seed)" >&2
    exit 1
  fi
done

echo ""
echo "Successfully generated $COUNT prompts in $OUTPUT_DIR"
echo ""
echo "Manifest:"
echo "  Seeds: $SEED_START to $((SEED_START + COUNT - 1))"
echo "  Fill: $FILL"
echo "  Files: $(ls -1 "$OUTPUT_DIR"/shuffle_*.json | wc -l | tr -d ' ')"
echo ""
echo "Next steps:"
echo "  1. Review generated prompts: cat $OUTPUT_DIR/shuffle_0001.json | jq ."
echo "  2. Begin evaluation using the template in docs/adr/0085-shuffle-driven-catalog-refinement.md"
