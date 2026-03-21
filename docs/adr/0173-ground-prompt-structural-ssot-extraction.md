# ADR-0173: Ground Prompt Structural SSOT Extraction

**Status:** Accepted
**Date:** 2026-03-21
**Relates to:** ADR-0172 (ground prompt principle-derived reformulation)

---

## Context

`lib/groundPrompt.py` contains the ground method prompt as ~400 lines of prose split across four `GROUND_PARTS` sections (~26,800 characters total). The prompt is injected into LLM context and must be followed during inference.

A question arose whether mathematical notation (logic symbols, set notation, formal grammar) would reduce token count more efficiently than prose. A `probe thing mint reify shear` analysis was run to evaluate this.

**Finding from the probe:** The prompt contains two distinct classes of content with opposite compression profiles:

1. **Structural enumeration** — sentinel format strings, the rung sequence list. These are low-ambiguity, high-density, and candidates for extraction into canonical data structures.
2. **Behavioral qualification** — the prose explaining why rules apply, what counts as a violation, and what the edge cases are. This is where LLM compliance lives and it resists compression.

Mathematical notation was rejected because the prompt's enforcement mechanism is LLM comprehension at inference time, not theorem-proving. Symbols add cognitive load and fail silently when misread; prose with redundancy provides multiple recovery hooks at different violation points.

A redundancy audit (Thread 3) confirmed that nearly all repetition in the prompt is load-bearing: each repeated phrase appears at a different violation hook or in a different section for cross-section enforcement. The cross-section repetition of "the tool must be re-run with the sentinel appearing immediately before it" (appearing in both `epistemological_protocol` and `sentinel_rules`) is representative — both occurrences are positionally necessary.

---

## Decision

Extract structural enumeration into canonical Python data structures while leaving all behavioral qualification prose intact.

**Three changes were made:**

### 1. `SENTINEL_TEMPLATES` dict
A canonical dictionary of sentinel format strings, keyed by reference name. This is the SSOT for all format literals previously scattered inline through `sentinel_rules`. The impl_gate format string (`🟢 Implementation gate cleared — gap cited: [verbatim from 🔴 Execution observed]`) appeared 4 times; it now appears once (canonical definition at the emit instruction) with a name reference at the second occurrence.

### 2. `RUNG_SEQUENCE` list
A list of 7 dicts, one per rung, each with keys: `name`, `artifact`, `gate`, `voids_if`. This is the SSOT for rung metadata previously expressed only as a numbered prose list embedded in `rung_sequence_code`. The numbered list was replaced with a compact inline arrow sequence.

### 3. Redundancy audit finding (no removals)
Thread 3 audit found no safe emphasis-only removals. The audit methodology was: for each repeated phrase, identify the violation hook at each occurrence; if hooks differ, the repetition is load-bearing. All significant repetitions passed this test.

**Mathematical notation was explicitly rejected** as the primary compression strategy. The shear is not prose → math; it is structural enumeration → data structure, with behavioral prose preserved.

---

## Consequences

**Positive:**
- `SENTINEL_TEMPLATES` and `RUNG_SEQUENCE` are now importable SSOs usable in tests, generation scripts, and future tooling.
- The impl_gate format string duplication in `sentinel_rules` is eliminated.
- The numbered rung list is replaced with a compact arrow sequence (modest char reduction).
- Three test files validate the extraction and guard against regression.

**Negative / tradeoffs:**
- Net token reduction is modest (~31 chars in `rung_sequence_code`, one format string deduplication in `sentinel_rules`). The prompt remains long because the behavioral qualification prose is the enforcement mechanism.
- Mathematical notation remains unvalidated empirically — if compliance data later shows the prompt is undertriggering on specific rules, targeted formalization of those rules could be revisited.

**Test coverage added:**
- `_tests/test_ground_prompt_sentinel_extraction.py` — validates `SENTINEL_TEMPLATES` exists, all keys present, no format string duplicated in `sentinel_rules`.
- `_tests/test_ground_prompt_rung_table.py` — validates `RUNG_SEQUENCE` exists, 7 entries, all canonical names in order, `rung_sequence_code` shorter than pre-extraction baseline.
- `_tests/test_ground_prompt_redundancy_audit.py` — validates candidate repetitions are ≤1 occurrence, output integrity, total char count does not grow.

---

## Considered Alternatives

**Full mathematical notation:** Rejected. LLMs follow natural language instructions more reliably than formal logic at inference time. Precision gain does not compensate for comprehension loss. Failure mode is silent misparse with no recovery path.

**Partial formalization of sentinel format strings as a prompt-visible table:** Considered as part of Thread 2. Decided against — the format strings are already clearly stated inline; a separate table header would add tokens, not remove them. The value of `SENTINEL_TEMPLATES` is as a Python SSOT, not as additional injected text.

**Aggressive redundancy removal:** Rejected after Thread 3 audit. Cross-section and cross-hook redundancy is the primary compliance mechanism for a probabilistic inference system. Removing it treats the prompt as a human-readable document rather than an enforcement surface.
