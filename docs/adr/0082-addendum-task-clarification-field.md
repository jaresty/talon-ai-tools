# 0082 – Addendum: Task clarification field distinct from Subject

## Status
Proposed

## Context
- The Talon Python code already separates these concepts in `lib/modelSource.py`:
  - **`prompt`**: Task clarification sent as "# Prompt" section
  - **`source`**: The actual content sent as "primary content" section
- The bar CLI currently conflates these, treating `--prompt` (via stdin) as subject rather than task clarification.
- Users providing custom text intend it as task clarification ("focus on error handling"), not as subject matter.
- The reference key describes Subject as "the content to work with," which doesn't fit task clarification use cases.
- Aligning the CLI with the existing Talon architecture will provide consistency.

## Decision
Introduce a distinct **Addendum** field that captures task clarification, separate from Subject:

- **Task**: What to do (static prompt like "summarize", "explain", "todo")
- **Addendum**: How to customize/clarify the task ("focus on error handling", "keep under 100 words", "use simple language")
- **Constraints**: Guardrails shaping execution (completeness, scope, method, form, channel, directional)
- **Persona**: Communication identity (voice, audience, tone, intent)
- **Subject**: The actual content/material to work with

Example prompt structure:
```
Task: summarize
Addendum: focus on architectural decisions and trade-offs
Constraints: Completeness=gist, Form=bullets
Persona: Voice=as architect, Audience=to team
Subject: [ADR document content]
```

## Rationale
- Aligns bar CLI with existing Talon architecture (`prompt` vs `source` in `lib/modelSource.py`).
- Clearer semantic distinction helps LLMs understand what is instruction vs. what is content.
- Enables more precise prompt construction: users can specify both clarification AND subject.
- Aligns with how users naturally think about prompts ("do X, but focus on Y, with this material Z").
- Reference key can accurately describe each section's purpose.

## Implementation Plan

### Phase 1: CLI `bar build`
1. Add `--addendum` flag (or `--clarify`, `--custom`) to accept task clarification text.
2. Update `RenderPlainText` to emit an `=== ADDENDUM ===` section when present.
3. Position addendum after Task but before Constraints in rendered output.
4. Keep `--prompt` as alias for backward compatibility (deprecation notice optional).

### Phase 2: TUI2 Interface
1. Add `addendum` field to TUI2 model state.
2. Add editable text input for addendum in the UI (likely near subject input or as separate pane).
3. Update preview rendering to show addendum section.
4. Consider keyboard shortcut for quick access (e.g., Ctrl+A for addendum focus).

### Phase 3: Reference Key Updates
1. Update Go `referenceKeyText` in `internal/barcli/render.go` to include Addendum explanation.
2. Update Python `PROMPT_REFERENCE_KEY` in `lib/metaPromptConfig.py` to match.
3. Addendum description: "Task clarification that modifies HOW to execute the task. Not content to work with."

### Phase 4: Python/Talon Alignment (mostly done)
The Talon code already supports this via `lib/modelSource.py`:
- `prompt` parameter = task clarification (rendered as "# Prompt" section)
- `source` parameter = subject content (rendered as "primary content" section)

Remaining work:
1. Verify terminology consistency between CLI and Python rendered output.
2. Update reference key in Python to match CLI terminology if needed.
3. Consider if voice commands need any updates for clarity.

## Naming Considerations
Options for the flag/field name:
- `--addendum`: Formal, clear meaning ("something added")
- `--clarify`: Action-oriented, intuitive
- `--custom`: Generic, might be confused with custom task
- `--note`: Too vague
- `--instruction`: Could be confused with task itself

**Recommendation**: Use `--addendum` for precision; consider `--clarify` as alias for voice ergonomics.

## Rendered Output Format
```
=== TASK (DO THIS) ===
The response formats the content as a todo list.

=== ADDENDUM (CLARIFICATION) ===
Focus on action items and deadlines; ignore background context.

=== CONSTRAINTS (GUARDRAILS) ===
1. Completeness (gist): ...
2. Form (bullets): ...

=== PERSONA (STANCE) ===
- Voice: as project manager
- Audience: to team

=== REFERENCE KEY ===
[interpretation guidance]

=== SUBJECT (CONTEXT) ===
[the actual content to work with]
```

## Definition of Done
- [ ] `bar build --addendum "text"` renders addendum section in output
- [ ] TUI2 has editable addendum field
- [ ] Reference key explains addendum in both Go and Python
- [ ] `go test ./...` passes
- [ ] `make ci-guardrails` passes (PYTHON=.venv/bin/python)
- [ ] Manual: addendum appears correctly in preview and final output

## Consequences
- More precise prompt structure with clearer semantics.
- Minor complexity increase (one more field to manage).
- Backward compatibility maintained via `--prompt` alias.
- Better LLM interpretation of user intent vs. content.

## Open Tasks
- [ ] Phase 1: CLI implementation
- [ ] Phase 2: TUI2 implementation
- [ ] Phase 3: Reference key updates
- [ ] Phase 4: Python/Talon integration

## Risks and Mitigations
- User confusion about addendum vs subject: Clear labeling and reference key explanation.
- Migration from `--prompt`: Keep as alias, optionally emit deprecation notice.
- UI clutter in TUI2: Design compact addendum input that doesn't overwhelm the interface.
