# 101 – Helpful error messages for unrecognized tokens in Go CLI

Status: Proposed
Date: 2026-02-05
Owners: CLI Experience Team

## Context

- The Go CLI (`internal/barcli/build.go`) returns minimal error messages when tokens aren't recognized: `"unrecognized token"` or `"unrecognized token for {axis}"`.
- The `CLIError` struct captures structured data (`Unrecognized []string`, `Recognized map[string][]string`) but the human-facing message doesn't leverage this information.
- Users encountering these errors have no guidance on:
  - What tokens are valid for the failing axis
  - How to discover available tokens (`bar help tokens`)
  - Whether their input was close to a valid token (typos, wrong casing, spaces vs dashes)
  - What tokens they successfully specified before the error
- This friction is particularly acute for new users learning the grammar, users working from memory, and voice input scenarios where token pronunciation may vary.
- ADR-0073 established concise help discoverability patterns; error messages should maintain that same philosophy of pointing users toward the right next action.
- Similar CLI tools (Cobra, Click, Clap) provide "did you mean?" suggestions and command discovery hints that reduce user frustration and support tickets.

## Problem

Users get stuck when they mistype tokens or don't know what's valid for an axis, and the current error provides no actionable guidance to unblock them. This creates unnecessary friction in the learning curve and interrupts productive workflows with dead ends that require external documentation lookups.

## Decision

Enhance the error message formatting in `internal/barcli/build.go` to provide context-aware guidance:

### Core improvements

1. **Structured error output** - When an unrecognized token is encountered:
   ```
   error: unrecognized token for method: "analyz"

   Did you mean one of these?
     • analyze
     • analysis

   To see all valid method tokens:
     bar help tokens method
   ```

2. **Axis-aware help hints** - Include the specific `bar help tokens {axis}` command for the failing axis, making discovery immediate and eliminating guesswork.

3. **Fuzzy matching suggestions** - When the unrecognized token is within edit distance 2 of known tokens for that axis, display up to 3 closest matches under "Did you mean?" This handles:
   - Typos ("analyz" → "analyze")
   - Missing dashes ("fly rog" → "fly-rog")
   - Common misspellings

4. **Recognized token context** - When multiple tokens failed or succeeded, show what was successfully parsed:
   ```
   Successfully recognized:
     static: todo
     scope: focus
     method: ??? (unrecognized: "analyz")
   ```

5. **Shorthand vs key=value clarity** - If the error occurs after a `key=value` override, remind the user that all subsequent tokens must use `key=value` format:
   ```
   error: unrecognized token "analyze" after key=value override

   After the first key=value token, all remaining tokens must use key=value format.
   Did you mean: method=analyze
   ```

### Implementation approach

**Option A: Enhance error formatting at return site** (recommended)
- Modify `unknownValue()` and `applyShorthandToken()` in `build.go` to build richer messages
- Leverage existing `CLIError.Recognized` and `CLIError.Unrecognized` fields
- Add fuzzy matching helper using Levenshtein distance
- Query grammar for valid axis tokens to generate suggestions

**Option B: Post-process errors in app layer**
- Keep `build.go` error construction minimal
- Enhance formatting in `app.go` where errors are printed
- Separates concerns but makes context reconstruction harder

**Option C: Structured JSON errors only**
- Keep human messages minimal, emit full context via `--json`
- Requires external tooling to interpret
- Doesn't help interactive CLI users

We choose **Option A** because it provides immediate value to all users, keeps error context intact at the error site, and aligns with the principle that errors should be helpful by default.

### Fuzzy matching approach

- Use Levenshtein edit distance (stdlib or lightweight implementation)
- Match against tokens valid for the specific axis (if known) or all tokens (if ambiguous shorthand)
- Show up to 3 suggestions with edit distance ≤ 2
- Prioritize exact prefix matches over pure edit distance
- For multi-word tokens, suggest both the canonical dash form and note the spoken form

### Changes required

1. **`internal/barcli/build.go`**:
   - Add `formatUnrecognizedError(axis, token string, grammar *grammar) string` helper
   - Add `fuzzyMatch(input string, candidates []string, maxDist int) []string` helper
   - Update `unknownValue()` to use `formatUnrecognizedError()` for `Message` field
   - Update `applyShorthandToken()` to detect post-override context and adjust message
   - Update `Recognized` tracking to include axis names for better context display

2. **`internal/barcli/app.go`**:
   - Ensure error printing preserves multi-line formatting
   - Consider adding color support (using `github.com/fatih/color` or similar) to highlight suggestions (respects `NO_COLOR` env var)

3. **`internal/barcli/cli/config.go`**:
   - Add methods to query valid tokens by axis from grammar
   - Support querying all static prompts, all method tokens, etc.

4. **Tests** (`internal/barcli/build_test.go`):
   - Add fuzzy match test cases (typos, dashes, edit distance boundaries)
   - Test axis-specific help hints appear correctly
   - Test shorthand vs override context detection
   - Test recognized token context display

## Rationale

- **Reduces cognitive load**: Users don't need to context-switch to docs/help to find valid tokens.
- **Faster learning**: Fuzzy suggestions teach the correct spelling/format through immediate feedback.
- **Voice input support**: Users working with voice dictation benefit from pronunciation-tolerant suggestions.
- **Consistency with ADR-0073**: Extends the "concise help with clear next steps" philosophy to error states.
- **Lower support burden**: Fewer "what tokens are valid?" questions in issues and discussions.
- **Progressive enhancement**: Errors remain parseable by `--json` consumers while becoming more helpful for humans.

## Consequences

- Error message formatting code in `build.go` becomes more complex; needs clear helper extraction to stay maintainable.
- Fuzzy matching adds minor performance overhead (negligible for small token sets, <1ms).
- Error output becomes multi-line; tests and fixtures that match on exact error strings will need updates.
- Color support adds a dependency; must remain optional and respect terminal capabilities.
- Grammar must expose token enumeration methods if not already available.

## Validation

- Extend `go test ./internal/barcli/...` with:
  - Fuzzy match accuracy tests (correct suggestions within edit distance 2)
  - Axis-specific help hint presence tests
  - Shorthand vs override context detection tests
  - Recognized token context display tests
- Update test fixtures (`internal/barcli/app_build_cli_test.go`) to expect richer error output
- Smoke test common error scenarios:
  ```bash
  bar build analyz focus steps          # Typo in method
  bar build todo foccus                 # Typo in scope
  bar build scope=focus analyze         # Shorthand after override
  bar build does-not-exist              # Completely unknown token
  ```
- Verify `--json` output remains machine-parseable and includes `unrecognized` and `recognized` fields

## Follow-up

- Consider surfacing recognized token context in `bar tui` validation messages for consistency.
- Explore adding shell completion hints that pre-emptively show valid tokens as users type (via `bar completion`).
- Monitor telemetry for error frequency after shipping to assess impact on user success rates.
- Consider extending fuzzy matching to suggest related commands (e.g., "Unknown command 'biuld'" → "Did you mean 'build'?").

## Anti-goals

- Do not add suggestion telemetry or analytics that phones home; keep the CLI fully offline-capable.
- Do not change the `CLIError` struct's JSON schema in breaking ways; keep `--json` consumers compatible.
- Do not implement complex NLP or semantic matching; Levenshtein distance is sufficient for typo correction.
- Do not gate helpful errors behind flags; make them the default experience.

## Example Output

### Before
```
$ bar build todo focus analyz steps
error: unrecognized token for method
```

### After
```
$ bar build todo focus analyz steps
error: unrecognized token for method: "analyz"

Did you mean one of these?
  • analyze
  • analysis

To see all valid method tokens:
  bar help tokens method

Successfully recognized:
  static: todo
  scope: focus
```

### After (shorthand-after-override error)
```
$ bar build method=analyze todo
error: unrecognized token "todo" after key=value override

After the first key=value token, all remaining tokens must use key=value format.
Did you mean: static=todo

To see all valid static prompt tokens:
  bar help tokens static
```
