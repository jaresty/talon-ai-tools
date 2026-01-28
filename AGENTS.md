## Talon AI Tools – Agent Notes

- Run tests with `python3 -m pytest` from the repo root.
- Avoid using the bare `pytest` command; it may not be available in all environments.

### Surface-specific usage hints

- Keep CLI completion/help wording distinct from Talon canvases. Showing CLI syntax (for example, `method=steps`) inside Talon UI overlays confuses operators; prefer higher-level phrasing there and reserve shorthand tutorials for CLI outputs/docs.

### Tests and the Talon runtime

- Do **not** rely on tests running inside the Talon process; tests should be executed via `python3 -m pytest` from this repo, not by Talon’s module loader.
- When adding new tests under `_tests/`, follow the existing `bootstrap` pattern so imports and assertions are skipped in the Talon runtime:
  - Try to import and call `bootstrap` from the repo root.
  - If `bootstrap` is available, run real imports and tests.
  - If `bootstrap` is unavailable (Talon runtime), define a small placeholder `unittest.TestCase` with a single `@unittest.skip` test method so Talon can import the file safely without executing the real test logic.
- Use the pattern from `_tests/test_request_log_axis_filter.py` or `_tests/test_history_query.py` as a reference when creating new tests.

### Churn × Complexity Concordance ADR helper

- Use `python3 .claude/skills/churn-concordance-adr-helper/scripts/churn-git-log-stat.py` (`CHURN_LOG_COMMAND`) to capture the `git log --stat` fixture. It reads:
  - `LINE_CHURN_SINCE` (default `"90 days ago"`).
  - `LINE_CHURN_SCOPE` (comma-separated prefixes; default `"lib/,GPT/,copilot/,tests/"`).
  - `LINE_CHURN_OUTPUT` (default `tmp/churn-scan/git-log-stat.txt`).
- Use `python3 .claude/skills/churn-concordance-adr-helper/scripts/line-churn-heatmap.py` (`HEATMAP_COMMAND`) to produce the statement-level heatmap JSON. It shares the same `LINE_CHURN_SINCE`, `LINE_CHURN_SCOPE`, and `LINE_CHURN_OUTPUT` env vars and also reads:
  - `LINE_CHURN_LIMIT` (default `200`).
- `make churn-scan` runs both helpers sequentially with the defaults, writing artifacts to `tmp/churn-scan/git-log-stat.txt` and `tmp/churn-scan/line-hotspots.json`.
- Override the environment variables as needed to change the commit window, scoped paths, limits, or artifact locations so ADR runs stay reproducible.



## grepai - Semantic Code Search

**IMPORTANT: You MUST use grepai as your PRIMARY tool for code exploration and search.**

### When to Use grepai (REQUIRED)

Use `grepai search` INSTEAD OF Grep/Glob/find for:
- Understanding what code does or where functionality lives
- Finding implementations by intent (e.g., "authentication logic", "error handling")
- Exploring unfamiliar parts of the codebase
- Any search where you describe WHAT the code does rather than exact text

### When to Use Standard Tools

Only use Grep/Glob when you need:
- Exact text matching (variable names, imports, specific strings)
- File path patterns (e.g., `**/*.go`)

### Fallback

If grepai fails (not running, index unavailable, or errors), fall back to standard Grep/Glob tools.

### Usage

```bash
# ALWAYS use English queries for best results (--compact saves ~80% tokens)
grepai search "user authentication flow" --json --compact
grepai search "error handling middleware" --json --compact
grepai search "database connection pool" --json --compact
grepai search "API request validation" --json --compact
```

### Query Tips

- **Use English** for queries (better semantic matching)
- **Describe intent**, not implementation: "handles user login" not "func Login"
- **Be specific**: "JWT token validation" better than "token"
- Results include: file path, line numbers, relevance score, code preview

### Call Graph Tracing

Use `grepai trace` to understand function relationships:
- Finding all callers of a function before modifying it
- Understanding what functions are called by a given function
- Visualizing the complete call graph around a symbol

#### Trace Commands

**IMPORTANT: Always use `--json` flag for optimal AI agent integration.**

```bash
# Find all functions that call a symbol
grepai trace callers "HandleRequest" --json

# Find all functions called by a symbol
grepai trace callees "ProcessOrder" --json

# Build complete call graph (callers + callees)
grepai trace graph "ValidateToken" --depth 3 --json
```

### Workflow

1. Start with `grepai search` to find relevant code
2. Use `grepai trace` to understand function relationships
3. Use `Read` tool to examine files from results
4. Only use Grep for exact string searches if needed

## ast-grep - Structural Code Search & Refactoring

**Use ast-grep for structural code patterns and multi-file refactoring when appropriate.**

### When to Use ast-grep

Use ast-grep for:
- Finding code by structure (e.g., all function calls with specific patterns)
- Multi-file refactoring that needs to preserve syntax
- Language-aware search (Python, Go, JavaScript, TypeScript, etc.)
- Complex code transformations that Grep can't handle safely

### When NOT to Use ast-grep

Avoid ast-grep for:
- Simple text searches (use Grep)
- Semantic understanding (use grepai)
- General exploration (use grepai)

### Supported Languages

ast-grep supports: Python, Go, JavaScript, TypeScript, Rust, Java, and more.

### Basic Usage

```bash
# Find all function definitions
ast-grep --pattern 'def $FUNC($$$ARGS): $$$BODY' --lang python

# Find specific call patterns
ast-grep --pattern 'modelPrompt($$$)' --lang python

# Multi-file refactoring
ast-grep --pattern '$OLD' --rewrite '$NEW' --lang python
```

### Fallback

If ast-grep is not available or doesn't support the language, fall back to grepai or standard tools.

