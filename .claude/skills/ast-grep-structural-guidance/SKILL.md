---
name: ast-grep-structural-guidance
description: Applies when tasks involve structural or textual edits with supported grammars; documents the repository expectations for ast-grep workflows, diagnostics, and fallbacks.
---

# Ast-grep Structural Guidance

## Trigger Conditions
- This skill activates for any code-editing task where structural precision matters; `ast-grep` remains the default mechanism whenever the target language has grammar support, covering structural find-and-replace operations, Codex-driven rewrites, and other AST-aware workflows.

## Role and Scope
- This repository treats `ast-grep` as the default mechanism for structural or textual edits whenever the target language has grammar support.
- Agents perform structural discovery with `ast-grep run` before relying on manual context gathering.
- Pattern validation occurs in search-only mode (`--json` or `--debug-query`) before any rewrite is applied.
- Fallback tooling such as `sed`, `awk`, inline Python or Node scripts, or shell redirection remains disallowed unless ast-grep cannot represent the change and that exception is documented.

## Workflow Expectations
- Candidate rewrites run first without `--rewrite`, and their matches are inspected via `--json`, `--debug-query`, or `--interactive` output.
- Multi-line replacements travel through heredocs or files so quoting remains intact before ast-grep executes.
- Scope control relies on `--globs` and language selection rather than shell glob switches.
- Multi-node patterns become sequences of single-node rewrites, chaining captures when necessary.
- Markdown edits stay blocked because ast-grep currently lacks a Markdown grammar; alternate guidance precedes any `.md` modifications.

## Rewrite Examples
- The examples below illustrate common rewrites while keeping statements declarative.

```bash
ast-grep -p "runDemo($ARGS*)" --lang ts --rewrite "await runDemo($ARGS*)" scripts/__tests__/rcef
```

```bash
ast-grep -p "import { mkdtemp, readFile, rm } from 'node:fs/promises';" --lang ts \
  --rewrite "import { mkdtemp, readFile, readdir, rm } from 'node:fs/promises';" scripts/__tests__/rcef
```

```bash
ast-grep run -p "runDemo($ARGS*)" --lang ts --globs "scripts/__tests__/rcef/**/*.ts"
```

## YAML Rule Guidance
- YAML rules enable expanded transformations, including `fix`, `transform`, and `rewriters` blocks for complex edits.
- Transform helpers such as `substring`, `replace`, and `convert` shape captured meta-variables before they feed fixes.
- Fix strings remain indentation-sensitive, so the replacement text mirrors the desired layout exactly.
- Surrounding punctuation is captured via `expandStart` or `expandEnd` to avoid stray delimiters.

## Diagnostics and Recovery
- Search-only diagnostics rely on `ast-grep run --debug-query --lang <lang>` or `--json[=pretty]` outputs.
- Rule validation occurs through `ast-grep test rule.yaml`, and structural dumps come from `ast-grep dump rule.yaml`.
- The AST of a source file is inspected with `ast-grep --dump-ast <file>`, while interactive exploration uses `ast-grep --interactive`.
- Severity filtering through `--error`, `--warning`, `--info`, `--hint`, and `--off` tailors lint results.
- When pattern matches return empty results, agents log the attempt, review diagnostics, and either relax the pattern or seek human guidance before abandoning ast-grep.

## Operational Notes
- The workspace already supplies ast-grep, so no installation step is required.
- Agents record any fallbacks away from ast-grep in their final summaries, including the rationale.
- Structural edits on unsupported grammars or formats always escalate for alternate workflows.
