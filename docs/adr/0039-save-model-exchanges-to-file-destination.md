# ADR-0039 – Save Model Exchanges via File Destination

Status: Accepted  
Date: 2025-12-10  
Owners: Talon AI tools maintainers

---

## Context / Jobs To Be Done

From a user perspective, the core jobs are:

- **Archive** – When a run is good, save the *whole thing* (prompt/context/source + response + relevant meta) as a durable artifact that can be browsed or skimmed later.
- **Reconstitute** – Given such an artifact, quickly recall what happened and, if needed, re-run or adapt it.
- **Trace / learn** – Build a personal “data bank” of examples and regressions, without having to stitch together prompt, response, and meta by hand.

We already have:

- A strong, composable mental model around `model pass <source> to <destination>` for routing model **outputs**.
- ADR-0038, which introduced a custom, source-only helper (`gpt_save_source_to_file`) and surfaces like `model source save file` and “Save source to file” buttons.

In practice, this has several mismatches:

- What people usually want to keep is the **model output / exchange**, not just the raw input `ModelSource` text.
- The custom "save source" path duplicates the destination abstraction instead of extending it.
- Having a separate `model source save file` command and bespoke helpers increases cognitive load versus reusing the familiar `model pass` grammar.

We want to:

- Treat "save to file" as a **first-class destination** within the existing destination model.
- Reuse the `model pass … to …` grammar so users say what they already know.
- Make the saved artefacts human-oriented (skim-friendly) rather than raw log dumps.

---

## Problem

- The current implementation from ADR-0038:
  - Introduces a custom `gpt_save_source_to_file` helper that writes only the **input source text** to markdown.
  - Adds separate surfaces/grammar (`model source save file`, custom buttons) instead of teaching `file` as a destination.
  - Produces artefacts that often *omit the response*, which is the main payload users want to retain.
- This design:
  - Splits the mental model between "destinations" and "save helpers".
  - Increases the number of one-off commands for similar work.
  - Does not map well to the JTBD of building a personal data bank of exchanges.

We need to:

- Introduce a **File** destination that can accept any supported model destination payload (response text, exchanges, etc.).
- Wire it through the existing `model pass` grammar.
- Retire the custom "save source" surfaces in favour of this unified approach.

---

## Decision

We will:

1. **Add a file-backed `ModelDestination`** that writes model payloads to human-readable markdown files.
2. **Teach the existing `model pass` grammar about a `file` destination**, so users can say things like:
   - `model pass last to file`
   - `model pass exchange to file`
   - `model pass response to file`
3. **Remove the bespoke `gpt_save_source_to_file` action and its direct surfaces**, migrating callers to the new destination where appropriate.

### 1. File-backed `ModelDestination`

- Introduce a destination (name TBD, but conceptually `FileDestination`) within `modelDestination.py`.
- Behaviour:
  - **Input contract**: accepts the same payloads as other destinations (e.g. the rendered response text, or an exchange string built by existing helpers such as `modelResponseCanvas` / history presenters).
  - **Directory**:
    - Uses `user.model_source_save_directory` as the base when set, expanded with `~`.
    - Falls back to `<talon user root>/talon-ai-model-sources/` when unset.
  - **Filename**:
    - Timestamp prefix `YYYY-MM-DDTHH-MM-SSZ`.
    - Slug from axes/recipe and, when available, a short source label (e.g. `response`, `exchange`, `history`, `adr`, etc.).
    - Example: `2025-12-10T18-47-03Z-response-describe-full-jog.md`.
  - **Content** (human-readable markdown, not raw JSON):
    - For **simple response passes** (e.g. `model pass last to file`):
      - Header with `saved_at`, `kind=response`, model name, and recipe/axes recap.
      - `# Response` section with the full response body.
      - Optional `# Prompt / Context` section when cheaply available from state/history.
    - For **exchange-style passes** (e.g. `model pass exchange to file`):
      - Header as above with `kind=exchange`.
      - `# Prompt / Context` section.
      - `# Response` section.
      - `# Meta` section when present.
    - We explicitly *do not* include raw HTTP request/response logs here; these artefacts are for human consumption and skimming.

### 2. Extend `model pass … to …` to support `file`

- Update the `modelDestination` list / Talon lists so `file` is a recognised destination token.
- Extend the grammar so that:
  - `model pass last to file` routes the "last response" payload into the File destination.
  - `model pass exchange to file` routes a composite prompt+response+meta string into the File destination (using existing helpers to format an exchange for humans).
  - Other sources (e.g. `history …`, `selection`, etc.) can also be passed to `file` where sensible, reusing the same destination implementation.
- This keeps all destinations (window, clipboard, browser, file, etc.) in **one mental bucket**, with one composable grammar.

### 3. Remove bespoke "save source" surfaces

- Deprecate and then remove:
  - `gpt_save_source_to_file`.
  - `model source save file` grammar.
  - Confirmation GUI / pattern GUI / prompt GUI / history surfaces that directly call the old helper.
- Replace them with `file`-destination usage where a GUI affordance makes sense:
  - For example, a confirmation GUI "Save to file" control that simply acts as a shortcut for `model pass last to file` or `model pass exchange to file`.
- Update ADR-0038’s work-log to mark the source-only helper as superseded by this destination-based approach.

---

## Migration Plan

1. **Introduce the File destination (behind existing code paths)**
   - Implement the `FileDestination` and directory/filename/content rules described above.
   - Add tests to ensure:
     - `model pass last to file` writes a markdown file with header + `# Response`.
     - `model pass exchange to file` writes prompt + response + meta when available.
2. **Wire grammar and internal calls**
   - Add `file` to the model destination list and `model pass` grammar.
   - Update internal callers where an explicit "save" surface already exists (e.g. confirmation GUI) to use the `file` destination instead of bespoke helpers.
3. **Remove `gpt_save_source_to_file` and its grammar**
   - Once the File destination is stable and covered by tests, delete:
     - The `gpt_save_source_to_file` action.
     - The `model source save file` grammar and any direct users.
   - Update tests and docs to reference `model pass … to file` patterns instead.
4. **Document the new flow**
   - README / help surfaces should teach examples such as:
     - `model pass last to file` – save the last response.
     - `model pass exchange to file` – save prompt + response + meta.
   - Make it clear that these artefacts are designed for human reading, not raw-log debugging.

---

## Consequences

- **Positive**
  - Users get a clear, composable way to save *responses and exchanges* using the familiar `model pass` pattern.
  - The destination model remains the single place to reason about "where things go"; we do not add parallel one-off helpers.
  - Saved files are human-oriented and easy to skim, supporting the "personal data bank" job.
- **Trade-offs**
  - Users who were relying specifically on the old "source-only" save behaviour will need to adapt; however, the new behaviour is more generally useful and better aligned with JTBD.
  - We avoid exposing raw logs in this path; deeper debugging continues to rely on existing log/trace mechanisms or future dedicated tooling.
- **Out of scope**
  - Round-tripping from these files back into a runnable exchange.
  - Automated pruning/rotation or indexing of saved files.
  - Any change to how `model pass` chooses *which* response/exchange to route; this ADR is strictly about adding a `file` destination and removing the bespoke "save source" pathway.
