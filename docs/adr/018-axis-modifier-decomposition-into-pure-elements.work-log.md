# 018 – Axis Modifier Decomposition into Pure Elements – Work-log

## 2025-12-05 – Loop 1 – Draft ADR and align with loop helper

- Focus: Capture the problem and high-level plan for decomposing axis modifiers into pure elements, following the ADR loop helper.
- Changes:
  - Added `docs/adr/018-axis-modifier-decomposition-into-pure-elements.md` with:
    - Context describing composite axis tokens across completeness/scope/method/style.
    - Purity constraints for each axis.
    - High-level reclassification decisions for key composite tokens (`framework`, `path`, `samples`, stance/audience method tokens, and heavy style genres).
    - An implementation plan covering list refactors, recipes/patterns, and tests/docs.
  - Updated the ADR to:
    - Link to ADR 017 explicitly.  
    - Note that fine-grained token changes will be tracked in this work-log rather than in the ADR body.
- Notes / next slices:
  - Next loops should:
    - Build the token-by-token classification table for all axis modifiers.  
    - Apply the first batch of concrete list changes (for example, decomposing `path` / `framework` / `samples`) with matching tests.  
    - Update `modelTone` / `modelAudience` lists and `STATIC_PROMPT_CONFIG` where they currently depend on composite axis tokens.

## 2025-12-05 – Loop 2 – Add Current Status snapshot to ADR 018

- Focus: Capture a concise, current snapshot of axis list contents inside the ADR so future loops can see where composite vs pure tokens exist without re-scanning the lists.
- Changes:
  - Added a **Current Status (this repo)** section to `docs/adr/018-axis-modifier-decomposition-into-pure-elements.md` summarising:
    - Completeness tokens, highlighting `framework`, `path`, and `samples` as composite.  
    - Scope tokens, separating `narrow` / `focus` / `bound` from relational/dynamic/system/actions lenses.  
    - Method tokens, separating reasoning patterns from stance/audience tokens (`adversarial`, `receptive`, `resistant`, `novice`).  
    - Style tokens, separating layout/surface styles from heavy genre/container styles.
- Notes / next slices:
  - Use this snapshot as the basis for the token-by-token classification table mentioned in Loop 1.  
  - Next loops can start applying concrete list refactors for one axis (for example, completeness) plus corresponding tests and docs.

## 2025-12-05 – Loop 3 – Add Salient Tasks checklist to ADR 018

- Focus: Make ADR-018’s remaining work more discoverable by adding a Salient Tasks section that points at concrete files and behaviours, in line with the ADR loop helper and ADR-010’s pattern.
- Changes:
  - Added a **Salient Tasks** section to `docs/adr/018-axis-modifier-decomposition-into-pure-elements.md` grouping tasks into:
    - Axis list refactors (completeness/scope/method/style list cleanups and token moves).  
    - Static prompt and pattern recipes (expressing former composite behaviours via explicit axis combinations in `lib/staticPromptConfig.py` and pattern GUIs).  
    - Guardrails, tests, and docs (tests in `tests/test_axis_mapping.py`, `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, and updates to `GPT/readme.md` and help surfaces).
- Notes / next slices:
  - Future loops can now pick a specific Salient Task (for example, “retire `framework`/`path`/`samples` from completeness” or “move stance tokens to tone/audience lists”) and implement it end-to-end with matching tests.

## 2025-12-05 – Loop 4 – Add “How to Exercise ADR‑018 Checks” section

- Focus: Make it easy to run the most relevant tests for ADR-018 and to see where new guardrails should be added as the implementation proceeds.
- Changes:
  - Added a **How to Exercise ADR‑018 Checks (this repo)** section to `docs/adr/018-axis-modifier-decomposition-into-pure-elements.md` that:
    - Points at the existing axis-related and static-prompt tests:
      - `python -m unittest tests.test_axis_mapping tests.test_static_prompt_config`.  
      - `python -m unittest tests.test_static_prompt_docs`.  
      - `make test` for a full sweep.  
    - Notes that these tests should be extended, per the Implementation Plan, to assert purity of axis tokens and coverage of former composite behaviours via explicit axis combinations or patterns.
- Notes / next slices:
  - When concrete list refactors land, extend the referenced tests accordingly so this section continues to describe the primary guardrails for ADR-018.

