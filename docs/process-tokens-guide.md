# Process Tokens Guide

> `ground`, `gate`, `chain`, `atomic` — and the presets that compose them.

These four tokens address a shared failure mode: **optimizer drift** — the model finding
a cheap path to *appearing* done rather than *being* done. Each token closes a different
escape route.

---

## The Tokens

### `ground` 地 — Derive your own enforcement process

**Failure mode it closes**: The model acknowledges constraints and then ignores them because
nothing makes violation costly.

**What it does**: Forces the model to derive a concrete step-by-step enforcement process
*before* acting — one that makes each shortcut immediately visible and costly. The model
must specify what counts as completion (not appearance of completion) and what visible
evidence will exist at each step.

**Use when**: The task is open-ended or novel enough that you can't anticipate the specific
failure shape in advance. `ground` is the meta-token — use it when you want the model to
figure out *which* constraints this task needs, not just apply ones you've named.

**Independent uses**:
- Open-ended research or analysis where the model can appear to answer by summarizing confidently
- Planning tasks where a plausible-looking plan isn't the same as a grounded one
- Summarization where fluent prose can substitute for actual coverage
- Any task where the failure mode is novel and you can't pre-specify the process

---

### `gate` 門 — Evaluation precedes implementation

**Failure mode it closes**: Evaluation written after the fact is shaped by what it evaluates
and cannot expose gaps the implementation was designed around.

**What it does**: Forces a structurally separate evaluation artifact to exist *before* the
implementation artifact. Declare success criteria before acting. Self-certification is
impossible — the evaluation must precede and be independent of what it evaluates.

**Use when**: Any artifact (code, argument, plan, decision) must be demonstrably correct
rather than plausibly correct.

**Independent uses**:
- Write acceptance criteria for a decision before making it (hiring, vendor selection, policy)
- Define what a good answer looks like before prompting an LLM
- Specify what a research summary must contain before reading the papers
- Write a rubric before reviewing or grading something
- Draft falsification conditions for a hypothesis before running an experiment

---

### `chain` 繋 — Each step cites its predecessor

**Failure mode it closes**: Conclusions detach from premises across multi-step reasoning;
hidden jumps accumulate until the final output can't be reconstructed from the inputs.

**What it does**: Forces each artifact or conclusion to explicitly cite its predecessor's
actual content. Any reader should be able to reconstruct why each step follows from the
previous one.

**Use when**: Multi-step reasoning, multi-artifact sequences, or iterative refinement must
remain auditable — "how did you get there" is as important as "what did you get."

**Independent uses**:
- Legal or policy arguments where each step must cite the prior clause
- Medical differential diagnosis where each elimination must cite the ruling-out evidence
- Financial models where each assumption must trace to a source
- Design documents where each constraint derives from a stated requirement
- Multi-round LLM conversations where you need to catch when the model has drifted from the original problem

---

### `atomic` 粒 — One observable change per step

**Failure mode it closes**: When multiple changes are bundled in one step, the causal link
between each change and its effect becomes unobservable — you can't tell what fixed it.

**What it does**: Forces each refinement step to address exactly one observed failure and
introduce nothing beyond what closes it. Domain-agnostic: the unit is the smallest
independently observable change.

**Use when**: Iterative refinement of any kind where you need to know which change caused
which improvement.

**Independent uses**:
- Writing revision: change one argument per draft so you know what improved clarity
- Debugging: isolate one variable at a time to find the cause
- Negotiation prep: explore one concession per pass to track trade-off structure
- Decision-making: change one assumption per cycle to know what shifted the outcome
- A/B testing design: one variable changed per trial

---

## Distinguishing Adjacent Tokens

| Confusion | Resolution |
|-----------|-----------|
| `gate` vs `verify` | `gate` is temporal ordering — evaluation artifact precedes implementation artifact. `verify` is falsification pressure on claims regardless of timing — require external constraints and defined negative space. Use `gate` for TDD/planning; use `verify` for anti-hallucination and grounding factual claims. |
| `chain` vs `trace` | `trace` narrates sequential progression. `chain` enforces that each step *derives from* the previous one's actual content. Narration doesn't require derivation. |
| `atomic` vs `rigor` | `rigor` is disciplined, well-justified reasoning in general. `atomic` specifically controls step granularity — one observable change per step. Rigorous reasoning can still bundle multiple changes. |
| `ground` vs `gate chain atomic` | `ground` asks the model to *derive* what constraints this task needs. `gate chain atomic` *specifies* the constraints. Use `ground` for open-ended tasks; use the specific tokens when you already know the shape of the task. |

---

## Presets

### `craft` = `ground gate chain atomic`

**Disciplined iterative making** — TDD and similar workflows where artifacts are produced
in strict cycles with full derivation visibility.

- `ground`: derive an enforcement process before starting
- `gate`: tests/criteria exist before implementation
- `chain`: each cycle cites its predecessor
- `atomic`: one behavior per cycle

Best for: software TDD, rigorous design iteration, any task where "I think it works"
is not acceptable.

---

### `audit` = `verify chain`

**Verifiable multi-step argument** — every claim is externally anchored and every step
traces to its predecessor.

- `verify`: each claim requires external evidence, not self-certification
- `chain`: each step must cite the prior step's actual content

Best for: fact-checking, policy analysis, legal arguments, research summaries where
both claim grounding and reasoning continuity matter.

---

### `scout` = `gate verify`

**Research with defined intent** — declare what you're looking for before reading, and
require citations for everything you find.

- `gate`: define success criteria (what the research must answer) before starting
- `verify`: require external anchoring for every claim in the output

Best for: literature reviews, due diligence, any research task where the failure modes
are "I read but didn't find what was asked" and "I asserted without citing."

---

### `chisel` = `chain atomic`

**Traceable incremental revision** — one change per pass, each pass explicitly citing
what changed from the previous.

- `chain`: each draft cites what it changed from the prior draft
- `atomic`: exactly one argument, assumption, or variable changed per pass

Best for: writing revision (know what improved the draft), iterative design (know what
changed the evaluation), debugging prose or arguments (isolate the broken claim).

---

## Composition Notes

- **`ground` + specific tokens**: `ground` derives *what* to enforce; adding `gate chain atomic`
  tells it *specifically what* to enforce. The combination (`craft`) is stronger than either alone —
  `ground` makes the model internalize the tokens rather than passively acknowledge them.

- **`verify` is not in any preset**: It addresses claim grounding, not artifact ordering or
  step granularity. Add it ad hoc when factual accuracy is a separate concern from process
  discipline (e.g., `craft` + `verify` for a TDD task involving factual claims).

- **Standalone tokens**: `ground`, `gate`, `chain`, `atomic` are each independently useful.
  Reach for a preset only when the full combination applies — don't add tokens for coverage.

---

*See ADR-0224 for the decomposition rationale and Exp 15b validation results.*
