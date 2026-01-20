# ADR 0084: Bar Shuffle - Random Prompt Generation

## Status

Accepted

## Context

The `bar build` command constructs prompts from explicit token selections. This works well for deliberate prompt composition but doesn't support exploration or creative variation.

Users may want to:

- Discover new token combinations they wouldn't normally try
- Generate varied prompts for testing or brainstorming
- Quickly produce a "surprise me" prompt without decision fatigue

A `bar shuffle` command would randomly select tokens to generate a prompt, using the same grammar and output mechanics as `bar build`.

---

## Decision

Add a `bar shuffle` subcommand that generates a prompt by randomly selecting tokens from available categories.

### Interface

```
bar shuffle [flags]
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--prompt`, `-p` | Subject text to include in the generated prompt |
| `--output`, `-o` | Output file path (default: stdout) |
| `--json` | Output as JSON (matches `bar build --json` format) |
| `--seed` | Random seed for reproducible shuffles |
| `--include` | Categories to always include (comma-separated) |
| `--exclude` | Categories to skip (comma-separated) |
| `--fill` | Fill probability per category (0.0-1.0, default: 0.5) |

**Stdin:** Subject text can be piped via stdin (same as `bar build`).

### Examples

```bash
# Random prompt to stdout
bar shuffle

# Random prompt with subject
bar shuffle --prompt "Refactor the auth module"

# Pipe subject from file
cat context.txt | bar shuffle

# Reproducible shuffle
bar shuffle --seed 42

# Always include a static prompt, maybe include others
bar shuffle --include static --fill 0.3

# Skip persona categories
bar shuffle --exclude voice,audience,tone

# JSON output for tooling
bar shuffle --json | jq .
```

### Token Selection Logic

1. Load grammar (same as `bar build`)
2. For each category in stage order:
   - If category is in `--include`: always select one token
   - If category is in `--exclude`: skip
   - Otherwise: select with probability `--fill` (default 50%)
3. When selecting from a category:
   - Pick uniformly at random from available tokens
   - Respect `MaxSelections` (typically 1)
4. Build prompt using selected tokens (reuse `Build()` from build.go)

### Output

Same format as `bar build`:

- Default: Plain text prompt to stdout
- `--json`: JSON object with `task`, `constraints`, `persona`, `subject`, `preview`
- `--output`: Write to file instead of stdout

### Categories

Uses the same stage order as TUI2:

1. `intent` (optional)
2. `persona_preset` (optional)
3. `voice` (optional)
4. `audience` (optional)
5. `tone` (optional)
6. `static` (the main prompt type)
7. `completeness`
8. `scope`
9. `method`
10. `form`
11. `channel`
12. `directional`

Default behavior with `--fill 0.5`:
- `static` is always included (required for a valid prompt)
- Other categories have 50% chance of inclusion

---

## Implementation

### Files to Create/Modify

| File | Change |
|------|--------|
| `internal/barcli/shuffle.go` | New file: shuffle logic and random selection |
| `internal/barcli/app.go` | Add `shuffle` subcommand to CLI parser |
| `cmd/bar/main.go` | Wire up shuffle command (if needed) |

### Shuffle Logic (shuffle.go)

```go
type ShuffleOptions struct {
    Seed     int64
    Include  []string
    Exclude  []string
    Fill     float64
    Subject  string
    Output   string
    JSON     bool
}

func Shuffle(g *Grammar, opts ShuffleOptions) (*BuildResult, error) {
    rng := rand.New(rand.NewSource(opts.Seed))

    var tokens []string
    excludeSet := toSet(opts.Exclude)
    includeSet := toSet(opts.Include)

    for _, stage := range stageOrder {
        if excludeSet[stage] {
            continue
        }

        // Always include static prompt for valid output
        mustInclude := stage == "static" || includeSet[stage]
        if !mustInclude && rng.Float64() > opts.Fill {
            continue
        }

        category := g.CategoryByKey(stage)
        if category == nil || len(category.Tokens) == 0 {
            continue
        }

        // Pick random token from category
        token := category.Tokens[rng.Intn(len(category.Tokens))]
        tokens = append(tokens, token)
    }

    return Build(g, tokens)
}
```

### CLI Integration

Add to argument parser alongside `build`:

```go
case "shuffle":
    return runShuffle(args, grammar)
```

---

## Consequences

### Positive

- Low-friction exploration of token space
- Reproducible via `--seed` for testing/debugging
- Reuses existing `Build()` and output formatting
- Minimal new code (~150 lines)

### Tradeoffs

- Random selection may produce nonsensical combinations
- No guarantee of "good" prompts (by design)
- Another subcommand to document

### Future Extensions

- `--bias`: Weight certain categories higher
- `--template`: Pre-fill some tokens, randomize others
- `--count`: Generate multiple shuffled prompts
- Integration with TUI for "shuffle and edit"

---

## Validation

```bash
# Smoke test: should produce valid prompt
bar shuffle

# Reproducibility: same seed = same output
bar shuffle --seed 123 > a.txt
bar shuffle --seed 123 > b.txt
diff a.txt b.txt  # should be empty

# JSON output matches build format
bar shuffle --json | jq -e '.task and .preview'

# Include/exclude work
bar shuffle --include static,method --exclude persona_preset
```
