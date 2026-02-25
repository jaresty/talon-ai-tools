# ADR-0085 Cycle 8: Kanji & Group Evaluation
**Date:** 2026-02-25
**Seeds:** 141–175 (35 prompts)
**Focus:** Kanji spot-check across all axes + method category group coherence
**Bar command used:** `bar build probe full good struct analysis gap table`

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A — kanji collisions are objective (same character), group coherence uses description-based analysis

---

## Corpus Summary (Seeds 141–175)

| Seed | Task | Completeness | Scope | Method(s) | Form | Channel | Dir | Persona |
|------|------|-------------|-------|-----------|------|---------|-----|---------|
| 141 | diff | minimal(小) | struct(造) | verify(検) | — | slack(通) | — | as-prompt-engineer |
| 142 | diff | minimal(小) | good(良) | analog(類) | — | wardley(図) | dip-bog | exec_brief |
| 143 | sort | narrow(狭) | time(時) | melody(旋) | facilitate(促) | diagram(図) | rog | as-facilitator |
| 144 | diff | full(全) | agent(主) | bias(偏) | bullets(列) | sketch(描) | dip-rog | exec_brief |
| 145 | plan | deep(深) | — | induce(帰) | — | code(碼) | fly-bog | — |
| 146 | fix | deep(深) | — | cite(引) | — | — | ong | product_manager_to_team |
| 147 | show | skim(掠) | stable(安) | flow(流) | tight(簡) | — | — | stakeholder_facilitator |
| 148 | pick | deep(深) | — | compare(較) | — | — | fip-bog | — |
| 149 | sort | full(全) | — | grove(蓄) | — | code(碼) | — | scientist_to_analyst |
| 150 | fix | full(全) | good(良) | meld(融) | — | — | fly-bog | — |
| 151 | pick | full(全) | fail(敗) | systemic(系) | — | html(標) | ong | designer_to_pm |
| 152 | fix | full(全) | view(視) | objectivity(客) | — | plain(文) | fip-ong | as-PM to-CEO |
| 153 | diff | narrow(狭) | — | analysis(析) | — | presenterm(演) | rog | peer_engineer |
| 154 | pull | max(極) | view(視) | resilience(耐) | — | — | — | intent=inform |
| 155 | probe | full(全) | fail(敗) | trade(衡) | — | — | — | product_manager_to_team |
| 156 | sort | full(全) | — | actors(者) | — | jira(票) | ong | product_manager_to_team |
| 157 | sim | full(全) | cross(横) | prioritize(優) | — | wardley(図) | — | as-writer |
| 158 | sim | full(全) | assume(仮) | flow(流) | — | gherkin(シ) | — | designer_to_pm |
| 159 | plan | full(全) | good(良) | gap(隙) | socratic(導) | — | dip-ong | as-designer to-designer |
| 160 | fix | full(全) | — | compare(較) | direct(直) | slack(通) | — | designer_to_pm |
| 161 | show | minimal(小) | — | rigor(厳) | — | wardley(図) | dip-bog | as-principal-engineer |
| 162 | show | max(極) | — | spec(仕) | — | — | dip-rog | exec_brief |
| 163 | sim | minimal(小) | — | diagnose(診) | — | — | fip-ong | casual |
| 164 | check | full(全) | — | jobs(需) | — | — | — | exec_brief |
| 165 | diff | full(全) | — | spec(仕) | — | — | — | scientist_to_analyst |
| 166 | make | minimal(小) | — | abduce(因) | — | remote(遠) | — | to-analyst gently |
| 167 | pick | skim(掠) | — | risks(危) | spike(査) | — | bog | stakeholder_facilitator |
| 168 | pull | skim(掠) | motifs(紋) | verify(検) | cocreate(共) | — | — | to-principal-engineer |
| 169 | plan | full(全) | act(為) | trans(伝) | — | svg(画) | bog | scientist_to_analyst |
| 170 | sim | full(全) | cross(横) | canon(準) | socratic(導) | remote(遠) | fog | as-designer |
| 171 | sort | full(全) | — | order(順) | indirect(間) | sketch(描) | — | designer_to_pm |
| 172 | sim | full(全) | — | spec(仕) | actions(行) | — | — | as-facilitator to-CEO |
| 173 | plan | full(全) | — | probability(確) | socratic(導) | remote(遠) | — | to-kent-beck formally |
| 174 | plan | minimal(小) | — | adversarial(攻) | — | presenterm(演) | fig | exec_brief |
| 175 | check | full(全) | — | shift(転) | direct(直) | remote(遠) | dip-bog | as-scientist |

---

## Kanji Collision Audit

### Cross-Axis Kanji Duplicates (HIGH PRIORITY — can appear in same prompt)

| Kanji | Token 1 (axis) | Token 2 (axis) | Collision type | Example seeds |
|-------|----------------|----------------|----------------|---------------|
| 極 | `max` (completeness) | `boom` (method) | Can appear together in any prompt | — |
| 検 | `verify` (method) | `checklist` (form) | Can appear together | 141, 168 (verify but no checklist) |
| 論 | `argue` (method) | `case` (form) | Can appear together | — |
| 類 | `analog` (method) | `taxonomy` (form) | Can appear together | 142 (analog, no taxonomy) |
| 視 | `view` (scope) | `visual` (form) | Can appear together | 152, 154 (view, no visual) |
| 形 | `reify` (method) | `formats` (form) | Can appear together | — |

### Same-Channel Duplicates (LOWER PRIORITY — can't appear together)

| Kanji | Token 1 | Token 2 | Notes |
|-------|---------|---------|-------|
| 図 | `wardley` (channel) | `diagram` (channel) | Both channels; can't combine |

### Kanji Quality Issues

| Token | Kanji | Issue | Evidence seeds | Proposed fix |
|-------|-------|-------|----------------|--------------|
| `gherkin` | シ | Katakana only, not a kanji; purely phonetic | 158 | Use 黄 (yellow — Gherkin = cucumber = green, but closest vegetable/specification kanji) or 瓜 (cucumber), or 仕様 variant |
| `spec` | 仕 | 仕 means "to serve/to do" in isolation; 仕様 = specification requires two characters. Single 仕 reads as "serve" not "spec" | 162, 165, 172 | Use 規 (standard/norm) or 様 (manner/specification) |

### Kanji Strengths (confirmed good)

| Token | Kanji | Strength |
|-------|-------|---------|
| `adversarial` | 攻 | "attack/offensive" — exact semantic fit |
| `diagnose` | 診 | Medical diagnosis character — perfect |
| `jobs` | 需 | "need/demand" — captures jobs-to-be-done well |
| `gap` | 隙 | "crack/gap" — precise |
| `trade` | 衡 | "balance/weigh" — excellent for tradeoffs |
| `melody` | 旋 | "whirl/revolve" — captures musical quality |
| `branch` | 枝 | "tree branch" — perfect |
| `inversion` | 逆 | "reverse/invert" — exact |
| `unknowns` | 未 | 未知 = unknown — clear |
| `depends` | 依 | "depend on" — precise |
| `converge` | 収 | "gather/converge" — correct |
| `polar` | 磁 | "magnet/poles" — captures polar opposition |
| `origin` | 起 | "rise/start/origin" — exact |
| `explore` | 探 | "search/explore" — correct |

---

## Method Category Group Coherence Evaluation

### Category: Reasoning (11 tokens)
abduce(因), argue(論), bias(偏), calc(計), cite(引), deduce(演), induce(帰), objectivity(客), probability(確), rigor(厳), verify(検)

**Distinguishability:** STRONG — each token has a clearly distinct analytical role:
- abduce/deduce/induce = three logical forms (clearly differentiated by description)
- argue = logical structure; bias = cognitive error identification; calc = quantitative; cite = sourcing; objectivity = fact/opinion separation; probability = statistical; rigor = disciplined process; verify = falsification

**Kanji coherence within category:** Good. No internal collisions. The three logical forms (因/演/帰) use different characters.

**Score: 5 — Excellent differentiation**

### Category: Exploration (6 tokens)
boom(極), branch(枝), domains(領), experimental(実), explore(探), split(分)

**Distinguishability:** MODERATE
- boom vs experimental: overlap possible (both test conditions/extremes). boom = scale extremes; experimental = hypothesis testing. Descriptions are distinguishable but use cases may blur.
- explore vs domains: explore = open survey; domains = structured domain enumeration. Moderately distinct.
- branch vs split: branch = parallel reasoning paths; split = A/B fork on a decision variable. Clear.

**Concern:** boom(極) collides with max(極) — see kanji audit above.

**Score: 4 — Good, with one kanji collision and mild boom/experimental proximity**

### Category: Structural (9 tokens)
analysis(析), canon(準), cluster(集), depends(依), gap(隙), mapping(写), order(順), origin(起), spec(仕)

**Distinguishability:** MODERATE
- analysis(析) is very broad ("describe and structure the situation") — overlaps with almost every other structural method. It may absorb many of their use cases.
- mapping(写) vs analysis(析): mapping = surface all elements/relationships; analysis = describe and structure. High proximity.
- order(順) + sort(task): in seed 171 (sort+order), the sorting task and ordering method produced a redundant double-sequencing signal. The method adds little when the task already implies arranging.

**Concern:** spec(仕) kanji issue as noted.

**Score: 3 — analysis(析) is over-broad; order+sort task-level redundancy; spec kanji weak**

### Category: Diagnostic (7 tokens)
adversarial(攻), diagnose(診), inversion(逆), resilience(耐), risks(危), robust(堅), unknowns(未)

**Distinguishability:** STRONG — each targets a distinct failure mode dimension:
- adversarial = deliberate attack; diagnose = root cause; inversion = backward from failure; resilience = stress resistance; risks = probability/severity of bad outcomes; robust = resistance to variation; unknowns = unknown-unknowns

**No kanji collisions within category.**

**Score: 5 — Excellent**

### Category: Actor-centered (4 tokens)
actors(者), afford(構), field(場), jobs(需)

**Distinguishability:** STRONG — each takes a distinct human/user-centered lens:
- actors = who acts and decides; afford = what the design affords; field = ethnographic/contextual; jobs = JTBD

**Score: 5 — Small but well-differentiated**

### Category: Temporal/Dynamic (6 tokens)
effects(効), flow(流), operations(営), simulation(象), systemic(系), trans(伝)

**Distinguishability:** MODERATE
- simulation(method) vs sim(task): sim = temporal scenario walkthrough task; simulation = method enriching any task with simulation modeling. When both are selected (sim task + simulation method), the task-method distinction may be unclear to the LLM.
- trans(伝) kanji issue: 伝 means "transmit/convey". Token is described as "transformation and transmission thinking" but kanji only captures the transmission half. Transformation (転換/変換) would use different characters.
- effects vs systemic: related but distinct (point effects vs system-wide patterns). OK.

**Score: 3 — simulation(method)/sim(task) ambiguity; trans(伝) kanji covers only half the semantic**

### Category: Comparative (8 tokens)
balance(均), compare(較), converge(収), dimension(次), meld(融), polar(磁), prioritize(優), trade(衡)

**Distinguishability:** MODERATE
- converge vs prioritize: both narrow/reduce a set. converge = move toward single conclusion; prioritize = rank by importance. Close enough to blur.
- compare(method) vs diff(task): the method/task distinction exists, but compare method with a non-diff task (seed 160: fix+compare) is a valid and clear combination. The distinction is well-designed.

**Score: 4 — converge/prioritize proximity warrants attention**

### Category: Generative (9 tokens)
analog(類), grove(蓄), grow(増), melody(旋), mod(周), models(型), product(商), reify(形), shift(転)

**Distinguishability:** WEAK in subclusters
- **grow(増) vs grove(蓄)**: Both about building up. grow = expand incrementally from a seed; grove = accumulate/gather context then synthesize. Very similar sounding tokens with similar concepts. High same-category redundancy risk.
- mod(周): 周 means "circumference/all-around/weekly period". For "modular" this captures the periodic aspect but misses the discrete/modular aspect. Kanji is partially appropriate.
- analog(類) collides with taxonomy(類) — see kanji audit.
- The category is highly heterogeneous: analog, melody, mod feel quite different in character from grow/grove/models.

**Score: 3 — grow/grove same-category proximity; kanji collision (analog/taxonomy); category coherence questionable**

---

## Per-Seed Notable Findings

**Seed 142**: diff + analog(類) + wardley(図) — wardley channel is very specific (strategic mapping); analog method (analogy) is quite general. The combination would produce a Wardley map constructed by analogy, which is unusual. Score 3. Kanji: 図 for wardley is clear and appropriate.

**Seed 147**: show + stable(安) + flow(流) — Productive tension: explaining what's stable through a flow lens forces attention to the forces that maintain equilibrium. Not redundant — complementary. Score 4.

**Seed 151**: pick + fail(敗) + systemic(系) — Selecting an option by examining systemic failure modes. Excellent analytical combination. Score 5.

**Seed 153**: diff + analysis(析) + presenterm — Clean, minimal combination. Score 5.

**Seed 159**: plan + good(良) + gap(隙) + socratic(導) — Quality-focused planning that finds gaps via Socratic questioning. Excellent — high analytical value. Score 5.

**Seed 162**: show + max(極) + spec(仕) — max = exhaustive, spec = specification analysis. The kanji 極 for max is strong, but 仕 for spec is weak. Overall combination is coherent but spec kanji is a recurrent issue.

**Seed 171**: sort + order(順) — Redundant double-sequencing signal. sort task already implies ordering; order method adds no distinct analytical lens when the task is sort. Score 2 for method distinctiveness.

---

## Cycle 8 Findings Summary

### Issue 1: Kanji Collisions (6 cross-axis duplicates)
**Priority: HIGH** — visual confusion when two tokens show the same kanji in a prompt header

| ID | Collision | Affected seeds |
|----|-----------|----------------|
| K1 | max(極) ↔ boom(極) | any max+boom combo |
| K2 | verify(検) ↔ checklist(検) | any verify+checklist combo |
| K3 | argue(論) ↔ case(論) | any argue+case combo |
| K4 | analog(類) ↔ taxonomy(類) | any analog+taxonomy combo |
| K5 | view(視) ↔ visual(視) | any view+visual combo |
| K6 | reify(形) ↔ formats(形) | any reify+formats combo |

### Issue 2: Weak Kanji (2 tokens)
**Priority: MEDIUM**

| ID | Token | Current | Problem | Proposal |
|----|-------|---------|---------|---------|
| K7 | `gherkin` | シ | Katakana only, no semantic content | 瓜 (cucumber) or 仕様 abbreviation |
| K8 | `spec` | 仕 | "to do/serve" ≠ "specification" | 規 (norm/standard) or 様 (manner/spec) |

### Issue 3: Category Coherence (3 concerns)
**Priority: MEDIUM**

| ID | Category | Issue |
|----|----------|-------|
| G1 | Generative | grow(増) vs grove(蓄) — same-category semantic proximity; high redundancy risk |
| G2 | Structural | analysis(析) is over-broad; overlaps with mapping, canon, and most structural methods |
| G3 | Temporal/Dynamic | trans(伝) kanji captures only "transmission" half, not "transformation" |

### Issue 4: Task-Method Redundancy
**Priority: LOW** (by design, task and method are different axes)

| ID | Combination | Issue |
|----|-------------|-------|
| R1 | sort(task) + order(method) | Double sequencing signal; order adds no distinct analytical lens when task is sort |

---

## Recommendations (Cycle 8)

```yaml
- id: R22
  action: edit-kanji
  token: spec
  axis: method
  current_kanji: 仕
  proposed_kanji: 規
  reason: 仕 means "to do/serve" in isolation; 規 (norm/standard/specification) is semantically correct
  evidence: [seed_162, seed_165, seed_172]

- id: R23
  action: edit-kanji
  token: gherkin
  axis: channel
  current_kanji: シ
  proposed_kanji: 瓜
  reason: シ is bare katakana with no semantic content; 瓜 (cucumber) references the gherkin cucumber
  evidence: [seed_158]

- id: R24
  action: edit-kanji
  token: max
  axis: completeness
  current_kanji: 極
  proposed_kanji: 尽
  reason: 尽 (exhaust/use up completely) distinguishes max from boom(極); boom is "extreme scale" so 極 fits boom better; max is "exhaust all coverage" so 尽 fits max
  evidence: [kanji_collision_K1]

- id: R25
  action: edit-kanji
  token: verify
  axis: method
  current_kanji: 検
  proposed_kanji: 証
  reason: 証 (prove/certify/evidence) distinguishes verify from checklist(検); 検 = inspect/investigate; 証 = prove/falsify more precisely
  evidence: [kanji_collision_K2, seed_141, seed_168]

- id: R26
  action: edit-kanji
  token: case
  axis: form
  current_kanji: 論
  proposed_kanji: 策
  reason: 策 (plan/strategy) distinguishes case from argue(論); case form builds to a recommendation/strategy, not just an argument
  evidence: [kanji_collision_K3]

- id: R27
  action: edit-kanji
  token: taxonomy
  axis: form
  current_kanji: 類
  proposed_kanji: 分
  reason: 分 (divide/classify) distinguishes taxonomy from analog(類); taxonomy = classification system; 分 captures classification more precisely
  evidence: [kanji_collision_K4]

- id: R28
  action: edit-kanji
  token: visual
  axis: form
  current_kanji: 視
  proposed_kanji: 絵
  reason: 絵 (picture/drawing) distinguishes visual form from view(視) scope; visual = drawn/pictorial output; 絵 is unambiguous
  evidence: [kanji_collision_K5]

- id: R29
  action: edit-kanji
  token: formats
  axis: form
  current_kanji: 形
  proposed_kanji: 式
  reason: 式 (formula/style/form) distinguishes formats from reify(形); formats = output format enumeration; 式 captures format-as-style better
  evidence: [kanji_collision_K6]

- id: R30
  action: investigate
  token: grow
  axis: method
  category: Generative
  peer_token: grove
  reason: grow (expand incrementally) and grove (accumulate context) are semantically close within same category; need LLM execution comparison to assess redundancy
  evidence: [group_analysis_G1]

- id: R31
  action: investigate
  token: analysis
  axis: method
  category: Structural
  reason: analysis(析) description is over-broad ("describe and structure the situation") — likely absorbs use cases from mapping, canon, and most other Structural methods; may warrant description edit to narrow its scope
  evidence: [group_analysis_G2]
```
