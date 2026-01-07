# Experiment Loop Helper

The experiment loop operates under these declarative rules:

1. **State Capture**
   - The experiment log reflects the current set of corroborated facts and the full list of unresolved questions at every loop boundary.

2. **Focus Selection**
   - Exactly one open question is named as the focus of the loop and recorded before work proceeds.

3. **Hypothesis & Plan**
   - The focused question carries an explicit hypothesis.
   - A minimal, enumerated experiment plan declares the evidence to gather and the success/abort criteria.

4. **Execution Discipline**
   - The recorded plan is executed without deviation.
   - All resulting artifacts (commands run, logs, diffs, traces) are captured as evidence.

5. **Outcome Logging**
   - The experiment log records the outcome status (green / red / blocked), supporting evidence, newly confirmed facts, and any newly surfaced questions.
   - The open-question list is updated to reflect resolved and remaining uncertainties.

6. **Continuous Looping**
   - After logging, control returns to rule 2 with the refreshed question set; the process repeats until no open questions remain for the current slice.

### Invocation Template
Request a loop with declarative intent, e.g.

```
Implement one loop of <experiment name> via docs/experiment-loop-helper.md
```

This ensures the helper’s rules are applied to every investigative slice.
