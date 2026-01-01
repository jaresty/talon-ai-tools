# 050 – Migrate persona/intent-like static prompts to stance axes

## Status
Proposed

## Context
- The static prompt axis currently contains prompts whose semantics lean toward **persona/intent** stances (Who/Why) rather than content/task patterns (What/How).
- Existing Persona/Intent axes (ADR 015/040/042): voice, audience, tone, intent, persona presets, intent presets. These represent **who is speaking** and **why they are acting**.
- Persona/Intent presets and aliases are exposed through the shared `get_persona_intent_orchestrator()` façade (backed by `lib.personaConfig`), keeping guidance surfaces aligned.
- Contract axes (ADR 012/018/032/048): static prompt, completeness, scope, method, form, channel, directional. These capture **what to do and how to do it**, not who or why.
- Drift risk: keeping stance-oriented prompts inside the static prompt catalog blurs boundaries, increases validation complexity, and makes hydration/docs inconsistent.

## Definitions
- **Persona/Intent (Who/Why)**: voice/audience/tone/intent tokens and persona/intent presets that shape stance, empathy, and rhetorical posture.
- **Contract axes (What/How)**: static prompt (task archetype), completeness, scope, method, form, channel, directional. These describe the work shape, not the speaker.

## Findings (tokens better suited to stance axes)
- Static prompts that describe audience/stance rather than task:
  - `jobs` (JTBD “why” framing)
  - `value` (user value / intent)
  - `pain` (audience pain points)
  - `team` (people/roles focus)
  - `question` (conversational stance to audience)
  - `facilitate` (facilitator stance; meeting design)
  - `done` (definition of done / acceptance stance)
  - Borderline task-vs-stance: `fix` (tone/voice heavy), `LLM` (meta audience), `shuffled` (format transform rather than task).
- Form/channel tokens with stance flavour:
  - `announce` (rhetorical tone + audience); consider tone/intent + destination instead.
  - `plain`, `tight`, `headline` (tone/voice rather than pure form).

## Decision (proposed)
- **Re-home stance-like static prompts into Persona/Intent axes or presets**, removing them from `staticPrompt`:
  - `jobs`, `value`, `pain`, `team`, `question`, `facilitate`, `done` -> add as `intent`/intent tokens or persona presets where appropriate; drop from static prompt catalog.
  - Evaluate `fix`, `LLM`, `shuffled` for migration to method/form/tone; default is move to method/form if purely mechanical, otherwise drop or keep only if truly a task archetype.
- **Revisit form/channel stance tokens**:
  - Move `announce` to tone/intent + explicit channel destination; keep channel axis for pure destinations.
  - Consider moving `plain`, `tight`, `headline` into tone/persona presets; keep form axis focused on structure/layout.
- Maintain task-like static prompts in `staticPromptConfig` only when they describe *what to do*, not *who/why*.

## Rationale
- Persona/Intent axes already encode stance; putting stance inside static prompts creates duplication and validation drift.
- Keeping contract axes “what/how” pure preserves ADR 012/018 boundaries and simplifies suggest/validation (stanceValidation, axisCatalog drift checks).
- Hydration surfaces (help hub, suggest UI, response recaps) become clearer: stance comes from Persona/Intent; task shape comes from static prompt + contract axes.

## Migration Plan
1) **Add stance tokens/presets**  
   - Add new tokens to `GPT/lists/modelVoice|modelAudience|modelTone|modelIntent.talon-list` as needed.  
   - If preset-worthy, add to `lib/personaConfig.py` persona/intent presets and ensure `get_persona_intent_orchestrator()` (and its call sites) surface the new entries.
2) **Remove/migrate static prompts**  
   - Delete or deprecate the listed stance-like tokens from `lib/staticPromptConfig.py` and `GPT/lists/staticPrompt.talon-list`.  
   - For borderline items, reclassify:
     - `fix` -> method/token (proofreading) or tone preset if kept.
     - `shuffled` -> form/method (transform) or remove.
     - `LLM` -> meta destination/tone; likely remove from staticPrompt.
3) **Adjust form/channel axis entries**  
   - Remove `announce` from `form/channel` axes; express via tone/intent + destination.  
   - Move `plain`, `tight`, `headline` to tone/persona if retained.
4) **Regenerate and validate**  
   - Regenerate `lib/axisConfig.py` (`scripts/tools/generate_axis_config.py`).  
   - Update `lib/staticPromptConfig.py` profiles.  
   - Run drift checks (`scripts/tools/axis-catalog-validate.py`) and tests (`python3 -m pytest`).
5) **Update UI/help surfaces**  
   - Ensure help/suggest text reflects the new stance tokens (helpHub, modelHelpCanvas, suggest prompt text).  
   - Remove references to migrated static prompts from docs/patterns.
6) **Deprecation communication**  
   - Add short release note or migration hint in help hub for users of removed static prompts (e.g., “Use persona/intent stance X instead of static prompt Y”).

## Consequences
- Clearer axis separation: stance in Persona/Intent; task shape in static prompt + contract axes.
- Suggest validation becomes stricter but simpler; fewer ambiguous static prompts.
- Users may need to update habits/shortcuts; mitigated via help hints and presets.

## Token-by-token re-homing (with retire/decompose notes and alternate fits)
- `jobs` → Prefer intent/intent token (Why); alternate: persona preset (“jobs lens”)  
  JTBD is motivation. As intent, it can layer on any task; as persona preset, it could be a quick stance. Avoid static prompt so Why is not welded to What.
- `value` → Intent/intent token (Why); alternate: method `analysis` + intent  
  Outcome/impact framing. Intent keeps it portable; pairing with method `analysis` is fine, but the Why should live in intent.
- `pain` → Intent/intent token (Why); alternate: scope `actions` + intent  
  Pain points describe problem state. Keeping it as intent allows any task to highlight pains; scope/actions can complement, but the driver is Why.
- `team` → Persona preset (Who) + audience token; alternate: scope `system` when mapping org structure  
  People/roles context fits persona. If used for org mapping, scope `system` can combine; static prompt not needed.
- `question` → Method `socratic` (exists) + tone/persona; alternate: form `faq` when outputting Q&A  
  Interaction style. Use method; if the output must be Q&A, form `faq` covers layout. Remove from static prompt.
- `facilitate` → Persona preset (facilitator) + Method `liberating`/`plan` + Intent (session outcome); alternate: scope `activities`  
  Facilitator stance plus process. Method + persona captures it; scope `activities` can narrow to agenda. Drop static prompt.
- `done` → Intent/intent token (Definition of Done); alternate: completeness axis presets if we add “acceptance” flavour  
  Acceptance criteria is Why. Could also be a completeness-style preset, but best as intent so any task can state DoD.
- `ticket` → Form `story`/`bug`/`adr` + Channel `jira` (or destination preset); alternate: method `plan`/`steps` for structure  
  Output shape/destination. Keep task separate; use form/channel/method to shape the artifact.
- `fix` → Method `rewrite`/`proofread` + Tone `plain`/`tight`; alternate: form `plain` text output  
  Transform + style. Decompose; if a form is needed, lean on existing form tokens (bullets/table) plus tone, not a static prompt.
- `LLM` → Retire; alternate: destination preset (“produce prompts for model X”) if truly needed  
  Meta/instructional; avoid baking into axes. A dedicated destination/preset is safer than static prompt.
- `shuffled` → Method `rewrite`/`structure` + Form (table/cards); alternate: scope `relations` if the goal is regrouping  
  Layout transform. Use method+form; remove from static prompt.
- `announce` (form/channel) → Tone/intent + Channel destination; alternate: method `direct` + audience token  
  Rhetorical stance; better as tone/intent. Channel stays for transport; method `direct` can express headline-first delivery.
- `plain`, `tight`, `headline` (form) → Tone/voice tokens; alternate: keep `headline` as method `direct` if needed, but prefer tone  
  Stylistic constraints. Move to tone/persona; form should stay structural (table/checklist/adr). If headline-first is kept, model it as method `direct`.
