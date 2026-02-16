# ADR 0128: Token Guidance and Tooling Fixes from Task-Gap Analysis

## Status

Proposed

## Context

ADR-0113 (Task-Gap-Driven Catalog Refinement) identified several gaps in skill guidance and tooling. ADR-0127 already addressed channel-form conflicts in token guidance.

This ADR addresses remaining gaps: task-level guidance for probe/pull/show/make distinctions (better in token guidance than help_llm), plus tooling bugs.

## Decision

### Token Guidance Updates (Preferred over help_llm)

Token guidance shows in TUI at selection time - more actionable than help_llm.

#### 1. G-04: Probe vs Pull for Risk Tasks

**Problem:** Users pick `probe` for risk extraction, but `pull` is correct.

**Fix:** Add to `lib/staticPromptConfig.py` `STATIC_PROMPT_GUIDANCE_OVERRIDES`:

```python
"probe": "For extraction tasks ('what are the risks?', 'list the issues'), prefer 'pull' over 'probe'. "
    "probe = analyze broadly; pull = extract subset.",
```

---

#### 2. G-05: Scaffold + Make Conflict

**Problem:** `scaffold` wrongly used with design artifact tasks.

**Fix:** Already addressed in ADR-0127 token guidance. Verify:

```python
# In axisConfig.py AXIS_KEY_TO_GUIDANCE["form"]:
"scaffold": "Learning-oriented explanation. Avoid with 'make' task producing artifacts "
    "(code, diagram, adr) - use only when user wants accompanied explanation.",
```

---

#### 3. G-06: Summarisation Routing

**Problem:** Users pick `show` for summarisation, but `pull` is correct.

**Fix:** Add to `lib/staticPromptConfig.py`:

```python
"show": "For summarisation of long documents, prefer 'pull' (extraction). "
    "show = explain a concept; pull = compress source material.",
```

---

#### 4. G-07: Test Plan vs Coverage Gap

**Problem:** `make` vs `check` not distinguished for testing tasks.

**Fix:** Enhance ADR-0127 additions in `lib/staticPromptConfig.py`:

```python
"check": "Works well with: log (validation output), gherkin (acceptance criteria). "
    "For test coverage gaps: use check, not make. 'check' = evaluate existing; 'make' = create new.",
"make": "Works well with: svg, adr, diagram, codetour. "
    "For test plans: use make, not check. 'make' = create artifact; 'check' = evaluate existing.",
```

---

#### 5. G-08: Pre-mortem / Inversion

**Problem:** Inversion not surfaced for pre-mortem tasks.

**Fix:** Already covered in existing `inversion` guidance. Verify present in `lib/axisConfig.py`:

```python
# In AXIS_KEY_TO_GUIDANCE["method"]:
"inversion": "Well-suited for pre-mortem: assume failure, work backward to find causes.",
```

---

### Documentation Updates (help_llm)

Some items still belong in help_llm for comprehensive reference:

#### 6. G-09: Multi-turn Scope Note

**Fix:** Add to `internal/barcli/help_llm.go`:

```yaml
## Scope Boundaries
Bar produces single-turn structured prompts. It does not model multi-turn interactive sessions.
- Use `cocreate` form for responses structured to invite iteration
```

---

### Tooling Fixes

#### 7. SF-01: Persona Token Slug Format

**Problem:** `audience=to-product-manager` fails in key=value syntax.

**Fix:** Fix slug normalization in parser.

#### 8. SF-02: Case Form Hang

**Problem:** `bar build probe full fail time origin case` hangs.

**Fix:** Add `case` to incompatibility rules; fail cleanly with error.

---

## Implementation

1. Update `lib/staticPromptConfig.py` — add task guidance (1, 3, 4)
2. Verify `lib/axisConfig.py` guidance present (2, 5)
3. Update `internal/barcli/help_llm.go` — scope note (6)
4. Fix parser for SF-01
5. Fix grammar for SF-02
6. Regenerate axis config

## Validation

After implementation:
1. Run ADR-0113 task sample to verify improved token selection
2. Test persona slug format with key=value syntax
3. Verify `case` form fails cleanly
