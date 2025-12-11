# ADR-0038 – Save Model Source to File Destination

Status: Accepted  
Date: 2025-12-10  
Owners: Talon AI tools maintainers

---

## Context

- Power users frequently want to preserve the exact **model source** used for a run (prompt text plus any contextual source like context, thread, or GPTExchange) as a file:
  - For later editing or reuse.
  - For attaching to bug reports or sharing with others.
  - For building their own small prompt/script libraries outside Talon.
- Today, this typically requires:
  - Manually copying from the confirmation GUI or history surfaces.
  - Pasting into an editor and choosing a filename/location each time.
- Model **destinations** already provide a single, composable way to say "where does the result go?" but there is no parallel, low-friction path for "persist the source as a file" that:
  - Works from the current run’s source without extra selection.
  - Does not prompt for a path on each use.
  - Is discoverable from the same model-facing surfaces users already rely on.

We want a first-class way to save the current **model source** to disk with one action, using a predictable directory and filename scheme, and surfaced in the standard GPT UI surfaces.

---

## Problem

- There is no built-in, **one-step** action to turn the current model source into a file:
  - Users must juggle the confirmation GUI, clipboard, and an editor.
  - Repro steps or "share this exact prompt + context" workflows are manual and error-prone.
- When saving is done manually, file location is:
  - Inconsistent (various folders/projects).
  - Easy to forget or misplace later.
- Existing destinations focus on **outputs** (paste, browser, clipboard, etc.), while:
  - The **source side** (prompt + context) is not as easily persisted.
  - The source-saving behavior is not integrated into the model’s standard surfaces (confirmation GUI, pattern GUI, history, etc.).

We need a **standardized, low-friction** way to persist a model source to a file, without prompting for a path each time, and a clear plan for where users can invoke it.

---

## Decision

We will introduce a new **destination-like action** that saves the current **model source** to a file in a configured base directory, without asking the user for a path on each invocation, and surface it in key GPT UI surfaces.

### 1. New "Save Model Source to File" action

- Define a new action (conceptually a destination for the **source side**) with a canonical key, e.g. `saveSourceFile`.
- Behavior:
  - Resolve the effective `ModelSource` for the current run (respecting `user.model_default_source` and any explicit source used by the request).
  - Call `source.get_text()` / `format_messages()` as appropriate to obtain a serializable representation of the source.
  - Write a file under a **single base directory** (see below) using:
    - A timestamp prefix (e.g. `2025-12-10T14-32-05Z`).
    - A short slug derived from static prompt, axis context, or source type (e.g. `gptExchange`, `context`, or the static prompt key).
    - An extension of `.md` by default for text sources.
  - Emit a lightweight notification containing:
    - The final file path.
    - A short hint on how to open or navigate there.

### 2. Base directory and configuration

- Introduce a dedicated directory for saved model sources, e.g.:

  - Default: `<talon user root>/talon-ai-model-sources/`
  - Exposed via a setting, e.g. `user.model_source_save_directory`.

- Requirements:
  - The save action **never prompts for a location per use**.
  - Users may override the base directory through settings, but the action always chooses a subpath/filename automatically.
  - If the directory is missing, the action creates it on first use (best effort), else reports a clear failure notification.

### 3. File format and contents

- Default format: Markdown (`.md`) for text-only sources.
- Minimum contents:
  - A small header block encoding:
    - Date/time.
    - Source type (e.g. `context`, `gptExchange`, `gptRequest`, `clipboard`, etc.).
    - Any available static prompt name and major axes tokens (e.g. completeness/scope/method/style) to make the file self-describing.
  - A separator (e.g. `---`).
  - The raw source text (`get_text()` output), optionally prefixed with a `# Source` heading when useful.
- For multi-message sources (like `GPTExchange`):
  - Preserve message boundaries as plain text (for example, `user:` / `assistant:` blocks) so the file is readable and can be round-tripped manually if needed.
- For non-text sources (e.g. clipboard images):
  - Initial scope: support text-first flows.
  - If an image is the only content, emit a short, explicit message describing that the current source is not serializable as plain text and fail with a notification (future ADR can extend this to image artifacts).

### 4. Surfaces / discoverability

We will expose the "Save model source to file" action in **appropriate GPT surfaces**:

- **Confirmation GUI / response viewer**
  - Add a "Save source to file" control in the confirmation GUI (for example, in a meta/overflow menu near browser/open/clipboard actions).
  - This uses the **source that produced the current run**, not the response.

- **Pattern / prompt GUIs**
  - Where a specific source is implied by the pattern GUI (static prompt + chosen source), expose a "Save source to file" action in:
    - Pattern GUI action menu.
    - Any existing "more…" or meta menus.

- **Request history surfaces**
  - For each request entry where the source is reconstructable (e.g. from `requestHistory`/`requestState`), add a contextual action:
    - "Save this request’s source to file."
  - This allows retroactive saving of important runs.

- **Talon voice commands**
  - Add at least one direct command, e.g. `"model source save file"` or `"model save source file"`, that triggers the same action for:
    - The most recent request.
    - Or the currently focused confirmation GUI entry (matching existing focus semantics).

Surfacing should follow existing patterns from prior ADRs (e.g. ADR-019, ADR-023, ADR-028) to keep behavior consistent and predictable.

---

## Consequences

- **Positive**
  - Makes it trivial to create durable, shareable artifacts for prompts and context, improving reproducibility and collaboration.
  - Centralizes where model sources are written on disk, simplifying cleanup and backup.
  - Reduces friction compared to ad hoc copy–paste flows and avoids per-use file dialogs.
  - Aligns with existing destination and surface patterns so users can discover the feature where they already work.

- **Risks / trade-offs**
  - Accumulation of many saved source files over time:
    - Mitigation: clearly document the directory and encourage users to manage/clean it as needed; future work can add pruning or naming improvements.
  - Potential for sensitive content to be written to disk:
    - Mitigation: treat the feature as **opt-in** via explicit commands/UI controls; consider a follow-up setting to disable/enable the action or require confirmation in sensitive contexts.
  - Slight increase in complexity around request/source tracking to ensure the correct source is used when saving from history or GUIs.

- **Out of scope for this ADR**
  - Automatic rotation/pruning policies for the save directory.
  - Round-tripping from saved files back into model sources (e.g. "run this saved file as source") — this can be addressed in a follow-up ADR once the basic persistence path is in place.
