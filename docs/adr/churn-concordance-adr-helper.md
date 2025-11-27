# Churn × Complexity Concordance ADR Helper

This file is a reusable helper prompt for running a **churn × complexity (statement‑level) + Concordance** analysis and then drafting a new ADR **directly on disk**. It is **not** an ADR itself.

When asked to “run the churn × complexity Concordance ADR helper using `docs/adr/churn-concordance-adr-helper.md`”, the assistant should follow the steps below **and must write the resulting ADR markdown to a new file under `docs/adr/` rather than returning it only as chat text**.

---

## 0. Preconditions and Scope

- Scope: this helper is designed for churn/complexity and Concordance work over the core RCEF and testing hotspots:
  - `scripts/rcef/**`
  - `scripts/testing/**`
  - `scripts/__tests__/**`
- Tools (already in this repo):
  - **Line‑level churn × complexity heatmap (statement‑level):** `scripts/tools/line-churn-heatmap.mjs`
  - **Git log fixture for churn scope:** `npm run dev:churn:git-log` → `scripts/tools/churn-git-log-stat.mjs`
- ADR identifier and title selection should be **automatic**:
  - List existing ADR files under `docs/adr/` that match `^\d{4}-.*\.md$` (excluding `*.work-log.md`).
  - Parse their numeric prefixes, find the maximum `N`, and choose `ADR_ID = N + 1`, left‑padded to 4 digits (for example, if the highest is `0117`, pick `0118`).
  - Derive a short human‑readable working title from the analysis theme (for example, "Concordance Churn × Complexity Hidden Domain Refresh").
  - Derive `ADR_TITLE_SLUG` by lowercasing the title, replacing spaces and punctuation with hyphens, and collapsing repeats (for example, `concordance-churn-complexity-hidden-domain-refresh`).

The final ADR **must** be written to:

- `docs/adr/ADR_ID-ADR_TITLE_SLUG.md` (for example, `docs/adr/0118-concordance-churn-complexity-hidden-domain-refresh.md`).

Do **not** just print the ADR body in chat and expect a copy‑paste; use file‑editing tools in this environment (for example, `apply_patch`) to create/update the ADR file.

---

## 1. Run Statement‑Level Churn × Complexity Analysis

Use the in‑repo **line‑level churn × complexity heatmap** as the canonical “latest, statement‑level analysis” for Concordance work. This combines:

- Per‑line churn from `git log -p`.
- Per‑line branch/complexity heuristics.
- A coordination weight based on how many files change together in the same commit.

### 1.1 Capture git‑log fixture for the churn scope

Run the dev helper to capture `git log --stat` output for the same churn window and scope as the heatmap:

```bash
cd /Users/tkma6d4/dev/aem_manager

# Optional: override window/scope via env, otherwise defaults are:
#   LINE_CHURN_SINCE="90 days ago"
#   LINE_CHURN_SCOPE="scripts/rcef/,scripts/testing/"

npm run dev:churn:git-log
```

This runs `node scripts/tools/churn-git-log-stat.mjs` and writes:

- `tmp/churn-scan/git-log-stat.txt` — reproducible `git log --stat` text for the configured window/scope.

### 1.2 Run the line‑level churn × complexity heatmap

Then run the statement‑level churn × complexity tool:

```bash
cd /Users/tkma6d4/dev/aem_manager

# Environment variables (all optional):
#   LINE_CHURN_SINCE   - git --since window (default: "90 days ago")
#   LINE_CHURN_SCOPE   - comma-separated path prefixes (default: "scripts/rcef/,scripts/testing/")
#   LINE_CHURN_LIMIT   - max nodes to report (default: 200)
#   LINE_CHURN_OUTPUT  - JSON output path (default: "tmp/churn-scan/line-hotspots.json")

node scripts/tools/line-churn-heatmap.mjs
```

This script:

- Runs `git log -p` scoped to `LINE_CHURN_SCOPE` since `LINE_CHURN_SINCE`.
- Computes per‑line churn, per‑line complexity, and a coordination weight per touched line.
- Aggregates per‑line stats into **structural nodes** (file + symbol + node kind + node start line).
- Sorts by `score = churn × complexity × coordination_weight`.
- Prints a human‑readable top‑N list and writes a JSON payload to:
  - `tmp/churn-scan/line-hotspots.json`

`line-hotspots.json` has the approximate shape:

```jsonc
{
  "since": "90 days ago",
  "scope": ["scripts/rcef/", "scripts/testing/"],
  "limit": 200,
  "generatedAt": "2025-..",
  "lines": [
    { "file": "…", "line": 123, "churn": 4, "complexity": 5, "coordination": 3.2, "score": 64.0, "symbolName": "…", "role": "…" }
  ],
  "nodes": [
    {
      "file": "scripts/rcef/generate-index.ts",
      "symbolName": "generateForYaml",
      "role": "…",
      "nodeKind": "FunctionDeclaration",
      "nodeStartLine": 248,
      "totalChurn": 10,
      "totalCoordination": 6.3,
      "avgComplexity": 7.2,
      "score": 453.6,
      "sampleLines": [248, 249, 253],
      "episodes": [
        { "commit": "abc123", "text": "+ if (…" }
      ]
    }
  ]
}
```

When running this helper, the assistant should **read and parse** `tmp/churn-scan/line-hotspots.json` to drive the analysis rather than re‑implementing the heatmap logic.

---

## 2. Map Hotspots and Clusters from the Heatmap

Using `tmp/churn-scan/line-hotspots.json`:

1. Extract the top **node‑level** hotspots from `nodes` (by `score`).
2. For each node, record at least:
   - `file`, `symbolName`, `nodeKind`, `nodeStartLine`.
   - `totalChurn`, `avgComplexity`, `totalCoordination`, `score`.
   - `role` (from the heatmap) if present.
3. Group nodes into **clusters** based on shared responsibilities or concerns (for example, harness + detector config, sentinel findings, index + verification, session orchestration, etc.).

Output (in the ADR draft):

- A concise table or list of **Individual Hotspots**.
- A set of **Hotspot Clusters**, where each cluster lists member nodes and a short description of what the cluster appears to do.

Do **not** propose refactors yet in this step; focus on mapping where the coordination/churn pain is.

---

## 3. Apply the Concordance Frame to Find Hidden Domains

Apply the Concordance framing to the hotspot clusters using this description:

> Concordance measures how elements coordinate across visibility (how obvious the link is), scope (how far it reaches), and volatility (how often it changes); analyze the system to find clusters that share these coordination patterns, infer the shared intent or “tune” that defines each hidden domain, and recommend specific ways to clarify or strengthen those domains by reducing coordination cost or aligning their boundaries.

Throughout this analysis, treat **Concordance scores and health snapshot signals as first‑class outcomes of the work**: your recommendations should aim to **reduce sustained Concordance scores for the in‑scope hotspots over time** by fixing underlying structural, test, and UX issues, not by weakening guardrails, narrowing coverage, or otherwise gaming the scoring pipeline.

Concretely, look for changes that **increase visibility** (make coordination links and contracts more obvious), **narrow scope** (reduce the blast radius when hotspots change), and **reduce volatility** (stabilise or better absorb frequent changes) so that Concordance scores fall because the system is genuinely easier and safer to coordinate.

For each hotspot cluster:

1. Analyze **visibility**:
   - How obvious are the coordination links between the cluster’s files and functions?
   - Are contracts and flows clear at the orchestrator level, or hidden behind scattered conditionals and implicit data shapes?
2. Analyze **scope**:
   - When a node in this cluster changes, how broadly does that change propagate (file, module, package, cross‑service)?
3. Analyze **volatility**:
   - How often do these nodes change, individually and together, according to the heatmap (`totalChurn`, `episodes`)?
4. Identify clusters that share similar visibility/scope/volatility patterns and infer for each a **hidden domain / “tune”**: the shared intent behind their coordination.

In the ADR draft, describe:

- Each hidden domain / “tune”.
- Its member hotspots.
- Its visibility/scope/volatility pattern.
- The implied coordination cost or friction.

---

## 4. Draft Refactor and Boundary Recommendations

Using the hidden domains from step 3, propose **initial** refactor and boundary recommendations (these will be refined in step 5):

For each hidden domain:

1. Recommend **ways to clarify or strengthen the domain** by:
   - Reducing coordination cost:
     - Co‑locating heavily coupled logic.
     - Introducing or tightening clear facades/orchestrators.
     - Eliminating or consolidating implicit cross‑module dependencies.
   - Aligning boundaries:
     - Aligning modules/packages and CLI entrypoints with the inferred domain boundaries.
     - Moving orchestration logic out of large CLI entrypoints into dedicated domain homes (for example, `verify-pipeline/*`, `index-pipeline/*`, `session/*`, `session-tune/*`).
2. For each recommendation, capture:
   - The **target domain boundary** (what belongs together / apart).
   - Proposed **orchestrators/facades vs underlying domain modules**.
   - Any natural **phasing** (e.g., “Phase 1: extract façade; Phase 2: migrate callers”).

At this stage, mark these as **draft recommendations**; do not yet assume they match existing patterns.

---

## 5. Seek Similar Existing Behavior and Revise Recommendations

The assistant must now search the codebase for **similar behavior and existing patterns** and update the recommendations to prefer reuse/extension over invention.

For each draft recommendation from step 4:

1. **Search for prior art** in the repo:
   - Prefer existing domain homes and patterns, for example:
     - `scripts/rcef/verify-pipeline/**`, `scripts/rcef/index-pipeline/**`.
     - `scripts/rcef/session/**`, `scripts/rcef/session-tune/**`.
     - Existing domain facades and orchestrators (`*-facade.ts`, `*-orchestrator.ts`, `*-tune` modules).
2. Compare the draft with prior art:
   - Is there an existing module or pattern that already solves a similar coordination/boundary problem?
   - Can we **extend or reuse** that pattern rather than creating a completely new one?
3. Rewrite the recommendation to:
   - Align with or extend existing patterns and domain homes.
   - Minimize new concepts when a compatible, well‑tested pattern exists.
   - Explicitly describe how we will evolve or hook into the prior art.

Record, for each recommendation, in the ADR draft:

- `Original Draft` — short summary of the initial idea.
- `Similar Existing Behavior` — where the pattern already exists and how it works.
- `Revised Recommendation` — updated plan aligned to existing domain homes.

---

## 6. Tests‑First Refactor Principle and Characterization Coverage

The goal of this step is to ensure **adequate, branch‑focused test coverage for the behaviour you are about to change**, **not** to impose a blanket requirement to add new characterization tests when good tests already exist.

Put differently: this helper uses "characterize" in the sense of **"make sure the behaviour is well covered by tests"**, which may mean **relying entirely on existing tests** when they already exercise the relevant branches, or **adding new characterization tests only where those existing tests are insufficient**.

In other words:

- You **must** have adequate tests for the behaviour you are changing.
- You **must not** treat this step as "always write brand‑new characterization tests" when existing tests already cover the relevant behaviour and branches.

For every **revised recommendation** that changes behavior, structure, or boundaries, enforce this explicit **tests‑first refactor principle** (capturing and reaffirming the project’s existing guidance):

> At each step, we will first analyze existing tests to ensure that the behavior we intend to change is well covered. Where coverage is insufficient, we will add focused characterization tests capturing current behavior (including relevant branches and error paths), and then proceed with the refactor guarded by those tests. Where coverage is already strong and branch‑focused for the paths we are changing, we will rely on and, if needed, extend those existing tests rather than adding redundant characterization tests.

Concretely, for each proposed change:

1. Identify the **affected modules/functions** and their current tests.
2. Assess coverage qualitatively with an eye to **branches**:
   - True/false paths.
   - Error/exception paths.
   - Early returns and gating conditions.
3. Produce a **Tests‑First Refactor Plan**:
   - Where gaps exist, list **new characterization tests** that must be added **before** any refactor step.
   - Map each refactor step to:
     - The tests (existing or new) that characterize current behavior.
     - The tests that should confirm the new behavior or structure post‑refactor.
4. Make explicit that:
- Behavior‑changing refactors must not proceed without **adequate** characterization tests for the behavior being changed; when existing tests already cover the relevant branches and contracts, **no additional pre‑refactor characterization tests are required**, and the existing tests should be **reused and, if needed, extended**.
- When existing tests already provide good behavioral and branch coverage for the paths being changed, prefer **reusing and extending** those tests over adding near‑duplicate ones; do not add new tests “just because” if they do not meaningfully improve confidence.
   - Tests should favor **behavioral/contract‑level assertions** over internal implementation details, and the suite should stay reasonably fast and focused (avoid over‑testing the same behavior in many redundant places).

Include in the ADR a dedicated section titled **“Tests‑First Refactor Plan”** that captures this mapping.

---

## 7. Draft and Write the ADR File to Disk

Using the outputs from steps 1–6, the assistant must now **create a new ADR file under `docs/adr/`** with at least the following structure, and explicitly tie its refactor plan to Concordance outcomes:

1. **Title & Status**
   - `# ADR-ADR_ID – HUMAN-READABLE TITLE`
   - `Status: Proposed` (or as directed by the user).
   - Date and owners.
2. **Context**
   - Summary of the churn × complexity hotspots (from the heatmap).
   - Summary of the Concordance analysis (visibility/scope/volatility patterns).
   - Hidden domains / “tunes” identified.
3. **Problem**
   - How current coordination patterns and misaligned boundaries create high coordination cost, fragile behavior, and refactor risk.
4. **Decision**
   - Core decisions about domain boundaries, orchestrators/facades, and alignment with existing patterns.
   - A short statement making clear that, for the in‑scope hotspots, the intended long‑term effect of these decisions is to **reduce Concordance scores** by improving structure, tests, and guardrails rather than by relaxing scoring or hiding signals.
   - Where relevant, an explicit note that the chosen refactors aim to **increase visibility**, **narrow scope**, and **reduce volatility** for those hotspots so that coordination becomes easier and safer over time.
5. **Tests‑First Principle**
   - An explicit section restating the tests‑first characterization principle in bold or a blockquote, including the expectation of branch‑level coverage for new/changed logic where practical.
6. **Refactor Plan**
   - Phased plan tying domain/boundary changes to characterization tests and follow‑up tests.
7. **Consequences**
   - Positive outcomes, risks, and mitigations.
    - Where possible, expected **Concordance‑score effects** (for example, "should lower sustained scores for Sentinel tune hotspots once refactors and tests land"), with a reminder that reductions must come from genuine improvements, not from weakening Concordance checks.
8. **Salient Tasks** (optional but recommended)
   - Checklist of concrete tasks (code, tests, docs) that can be completed in small, independent slices.
   - When the new ADR will govern Concordance hotspots/tunes already covered by ADR‑0107 / 0118 / 0119 / 0120 / 0123, align its Salient Tasks and execution plan with ADR‑0126’s no‑deferral policy:
     - Treat the ADR as the long‑term home for **completing** the in‑scope Concordance refactors/guardrails in this repo (not just as a container for future rounds).
     - Phrase Salient Tasks in terms of concrete behaviour changes (code + tests + minimal docs) rather than “write another ADR” or “explicitly defer this tune”.
     - Avoid introducing tasks whose only outcome is to move work into yet another successor ADR without landing at least one material behaviour slice.

### 7.1 File creation requirements

When running under the AEM Manager Codex CLI harness:

- Use the available file‑editing tools (for example, `apply_patch`) to create the ADR file at:
  - `docs/adr/ADR_ID-ADR_TITLE_SLUG.md`.
- The assistant’s final chat response should:
  - Mention the exact file path created.
  - Summarize the key decisions and next steps.
  - **Not** require the user to copy‑paste ADR content; the source of truth is the file on disk.

If the file already exists, the assistant should:

- Read it.
- Decide whether to append a new section or evolve it according to the new churn/Concordance analysis (coordinating with the existing ADR’s status and content).

---

## 8. Final Output Back to the User

After writing or updating the ADR file on disk, the assistant should return a concise summary to the user covering:

- Where the statement‑level churn × complexity scan was run and where the JSON lives.
- The main hidden domains / “tunes” discovered.
- The top‑level refactor decisions and boundaries.
- A pointer to the new or updated ADR file path under `docs/adr/`.
- Any immediate **next slices** the user might want to run (for example, “write characterization tests for X before extracting Y façade”).

The assistant should **not** inline the entire ADR body in the chat unless the user explicitly asks to view it; the ADR document on disk is the primary artifact.
