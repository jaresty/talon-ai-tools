# ADR-0222: Ground Prompt TDD Refinement Process

## Summary

Define a systematic process for refining the ground protocol using TDD-style evaluation with subagents, targeting minimal prompts that produce maximal TDD compliance through principle-based steering rather than prescriptive steps.

## Context

The ground protocol has evolved through manual refinement and ad-hoc testing. This has produced:
- Over-specified prompts with too many rules
- Rules that are prescriptive rather than principle-derived
- No systematic way to verify if prompt changes improve or degrade agent TDD behavior

The goal is a minimal prompt where agents self-direct using principles, not procedures.

## Process

### 1. Define Reference Task

Select a small, multi-step coding task that requires TDD:
- **Criteria**: 5-15 minute implementation, requires test-first behavior, multiple refinement cycles
- **Example**: FizzBuzz, word wrap, prime factors, bowling game
- **Why**: Tractable enough to evaluate, complex enough to show TDD patterns

### 2. Run Subagent with Prompt

Give the subagent:
- The task specification
- The ground protocol prompt (current version)
- Instructions to execute the task using TDD

### 3. Scorecard Evaluation

Evaluate the TDD quality using a scorecard:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Test-first assertion | 25% | Did agent write failing test before implementation? |
| Minimal skeleton | 20% | Did agent write minimal scaffolding, not complete solution? |
| Visible failure | 15% | Did agent show actual failing test output? |
| One gap at a time | 15% | Did agent address exactly one failure per cycle? |
| Evidence before claims | 15% | Did agent cite evidence (failing output) before proceeding? |
| Meta-loop | 10% | Did agent re-run challenge after each verification? |

### 4. Refine Prompt

Based on scorecard results:
- Identify weakest areas
- Add/remove/modify rules in ground prompt
- Maintain principle-based framing (not prescriptive steps)
- Target: highest total score with fewest rules

### 5. Iterate

Repeat steps 2-4 until:
- Scorecard reaches target threshold (e.g., 80%)
- Rule count stabilizes or decreases
- No further principle-based improvements found

## Principles

- **Minimal**: Fewer rules is better; each rule must earn its place
- **Principle-derived**: Agents derive behavior from principles, not copy procedures
- **Self-steering**: Prompt enables agents to guide themselves through ladder
- **Commensurate verification**: Challenge strength matches task complexity
- **Demonstrated, not described**: Agents show actual failure, not analysis

## Outcomes

- Systematic, reproducible prompt refinement
- Evidence-based improvements (scorecard data)
- Minimal ground protocol producing high TDD compliance
- Process can be applied to other protocol prompts

## Status

Adopted as process reference (see ADR-0223 for the structural experiment that uses this process)

## Notes

- Subagent can be Claude Code or external LLM
- Scorecard can be automated or manual review
- Task should change between iterations to prevent overfitting
