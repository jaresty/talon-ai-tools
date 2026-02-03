# ADR 0097: Bar Command for Installing LLM Automation Skills

## Status
Proposed

## Context

The bar CLI provides a promptlet-based system for building unambiguous prompt recipes. Users discover available tokens through `bar help tokens` and compose valid sequences to generate prompts. However, bar's real power emerges when **LLMs use bar automatically** to structure their own responses and drive conversations using higher-level concepts.

### Current State

Bar CLI skills currently exist to teach users how to manually construct bar commands. However, there's a gap: **skills that enable LLMs (like Claude) to automatically use bar** for:
- Auto-discovering appropriate token combinations for user requests
- Structuring responses using bar's framework
- Presenting structured options to users
- Chaining bar commands for complex workflows

These "LLM automation skills" need to be installed consistently across repositories and work reliably across different agent types (general-purpose, Explore, Plan, etc.).

### The Problem

When setting up bar automation skills in a repository, users must:
1. Manually identify which bar automation skills exist
2. Install them to appropriate skill locations (`.claude/skills/`)
3. Ensure skills work across different agent contexts
4. Keep skills updated across multiple repositories

This creates friction for:
- **New projects**: No streamlined bootstrap process
- **Consistency**: Different repos may have different skill versions
- **Discovery**: Users may not know bar automation skills exist
- **Cross-agent reliability**: Skills must work for all agent types

## Explored Approaches

### Approach 1: Single Monolithic Install Command

Create a `bar install-skills` command that installs all bar automation skills to `.claude/skills/`.

**Advantages:**
- Simple UX: one command, done
- Fast for common case
- No configuration needed

**Disadvantages:**
- No flexibility for partial installation
- Installs skills user may not want
- All-or-nothing approach

**Trade-offs:**
- Optimizes for speed over control
- Best for "just make it work" scenarios

### Approach 2: Phased Installation (MVP → Full)

Install skills in phases based on maturity and user sophistication:
- **MVP**: Install only `bar-autopilot` (core automation)
- **Standard**: Add `bar-workflow` (multi-step chains)
- **Full**: Add `bar-suggest` (interactive option presentation)

**Advantages:**
- Progressive enhancement
- Users can start simple, add complexity
- Clear upgrade path
- Less overwhelming for new users

**Disadvantages:**
- Multiple installation targets
- Need to manage phase definitions
- Users must understand what each phase provides

**Trade-offs:**
- Balances simplicity with flexibility
- Good for growing with user needs

### Approach 3: Declarative Configuration

Use a configuration file (`.bar-skills.yaml`) that declares which skills to install.

**Advantages:**
- Version-controllable
- Team-shareable
- Explicit and reviewable

**Disadvantages:**
- Requires creating config file
- More complexity for simple case
- Another file to manage

**Trade-offs:**
- Optimizes for team collaboration
- Overkill for individual users

## Decision

**Recommended: Approach 1 (Simple Monolithic Install) for MVP**

Implement a `bar install-skills` command with the following behavior:

1. **Default mode** (no arguments): Install all bar automation skills to `.claude/skills/`
2. **Location override**: `--location <path>` specifies installation target
3. **Dry-run mode**: `--dry-run` shows what would be installed without installing
4. **Force update**: `--force` overwrites existing skills

### Specific Skills to Install (MVP)

The command will install these specific bar CLI automation skills:

#### 1. bar-autopilot (MVP)
**Purpose:** Automatically detect when a user request benefits from bar structuring and apply it

**Capabilities:**
- Analyzes user request for implicit structure needs
- Runs `bar help tokens` to discover current available tokens (version-agnostic)
- Builds appropriate bar command based on request type
- Executes command and uses output as prompt structure
- Works proactively without user needing to know about bar

**Trigger patterns:**
- "Write an ADR for..." → auto-runs bar with channel=adr
- "Help me decide..." → auto-runs bar with method=branch, form=variants
- "Explore options for..." → auto-runs bar with method=explore
- "Explain how..." → auto-runs bar with scope=mean or flow

#### 2. bar-workflow (MVP)
**Purpose:** Build and execute multi-step bar command sequences for complex tasks

**Capabilities:**
- Identifies complex requests requiring multiple perspectives
- Chains bar commands (e.g., probe → plan → make)
- Uses output of each command to inform the next
- Progressively builds comprehensive responses

**Trigger patterns:**
- "Design a new feature" (probe → explore → plan)
- "Analyze this architecture" (probe → show → identify risks)
- "Refactor this system" (probe → explore → plan)

#### 3. bar-suggest (MVP)
**Purpose:** Present users with bar-based choices for how to approach their request

**Capabilities:**
- Discovers relevant bar tokens
- Generates 2-4 distinct bar commands representing different approaches
- Presents options to user with plain-language descriptions
- Executes user's choice

**Trigger patterns:**
- Open-ended requests
- Ambiguous user goals
- Multiple valid approaches

### MVP Scope

**Phase 1 (Now):**
- Install all three skills: `bar-autopilot`, `bar-workflow`, and `bar-suggest`
- Target `.claude/skills/` by default
- Support `--location` override
- Include `--dry-run` for safety

**Future enhancements:**
- Skill update mechanism (`bar update-skills`)
- Skill removal (`bar remove-skills`)
- Version management and conflict resolution

### Cross-Agent Compatibility

All bar automation skills must:
- Work across agent types (general-purpose, Explore, Plan, etc.)
- Use `bar help tokens` for discovery (version-agnostic)
- Never hardcode specific tokens (tokens evolve)
- Handle missing bar gracefully (check if bar is installed)
- Use Bash tool to execute bar commands
- Parse bar output reliably

### Rationale

This approach addresses key constraints:

**For new users:**
- Zero-config default provides immediate value
- Simple mental model: "just install it"
- `--dry-run` allows safe exploration

**For LLM automation:**
- Skills teach Claude to use bar as thinking tool
- Users get better-structured responses automatically
- No user-facing complexity

**For cross-agent reliability:**
- Skills discover tokens dynamically
- No version-specific assumptions
- Graceful degradation if bar unavailable

**For maintenance:**
- Single source of truth for skill installation
- Updatable via re-running command with `--force`
- Clear upgrade path to future skills

## Consequences

### Positive

- **Reduced friction**: New projects get bar automation in seconds
- **Better LLM responses**: Claude automatically structures answers better
- **Consistency**: Same skills across all repositories
- **Version-agnostic**: Skills discover tokens dynamically
- **Cross-agent reliable**: Works for all Claude agent types
- **User-invisible**: Users benefit without needing to learn bar

### Negative

- **Implementation complexity**: Skills must be robust and well-tested
- **Bar dependency**: Requires bar CLI to be installed
- **Debugging difficulty**: LLM automation failures may be opaque
- **Token discovery overhead**: Each skill run may call `bar help tokens`

### Neutral

- **Skill source**: Need to determine where skills are sourced from (git repo, URLs, embedded)
- **Update mechanism**: How users update skills when improved
- **Versioning**: May need skill version management in future

## Implementation Plan

### Phase 1: Create All Three Bar Automation Skills (MVP)

**Step 1:** Define skill specifications
- Create bar-autopilot skill prompt/instructions
  - Define trigger patterns for automatic structuring
  - Specify bar command construction logic
  - Add cross-agent compatibility requirements
- Create bar-workflow skill prompt/instructions
  - Define multi-step chaining patterns
  - Create workflow templates (probe → explore → plan, etc.)
  - Specify sequence orchestration logic
- Create bar-suggest skill prompt/instructions
  - Define option generation logic
  - Design user choice interface
  - Specify decision patterns

**Step 2:** Implement and test skills
- Create `.claude/skills/bar-autopilot/` with skill definition
- Create `.claude/skills/bar-workflow/` with skill definition
- Create `.claude/skills/bar-suggest/` with skill definition
- Test each skill individually with various user requests
- Validate skills work across agent types (general-purpose, Explore, Plan)
- Ensure token discovery works dynamically
- Test skills working together (autopilot may delegate to workflow or suggest)

**Step 3:** Create `bar install-skills` command
- Implement skill installation logic for all three skills
- Support `--location` override flag
- Support `--dry-run` flag for preview
- Support `--force` flag for overwriting
- Add error handling and validation
- Create installation tests

**Step 4:** Document and ship
- Add usage documentation for `bar install-skills` command
- Create examples showing each skill in action
- Document skill interactions (how they work together)
- Update bar help text
- Announce to users

### Phase 2: Enhancement and Maintenance (Future)

**Step 1:** Add update mechanism
- Implement `bar update-skills` command
- Check for skill version updates
- Handle conflicts and breaking changes

**Step 2:** Add removal mechanism
- Implement `bar remove-skills` command
- Support selective removal (by skill name)
- Clean up skill directories properly

**Step 3:** Add advanced features
- Skill versioning and compatibility checking
- Custom skill sources (git repos, URLs)
- Skill configuration and customization

### Cross-Cutting Concerns

**Version Management:**
- Skills must handle bar version evolution
- Use `bar help tokens` for runtime discovery
- Never assume specific tokens exist

**Error Handling:**
- Check if bar is installed before running
- Gracefully degrade if bar unavailable
- Provide clear error messages

**Performance:**
- Cache token discovery results when possible
- Minimize `bar help tokens` calls
- Optimize for common patterns

**Testing Strategy:**
- Unit tests for skill logic
- Integration tests with real bar commands
- Cross-agent compatibility tests
- Version compatibility tests (old/new bar versions)

## Success Metrics

**For MVP (Phase 1):**
- [ ] All three skills (bar-autopilot, bar-workflow, bar-suggest) created and tested
- [ ] `bar install-skills` command implemented
- [ ] Skills work across 3+ agent types (general-purpose, Explore, Plan)
- [ ] Installation takes < 5 seconds
- [ ] Skills correctly discover tokens via `bar help tokens` (version-agnostic)
- [ ] Skills work together cohesively (autopilot can delegate to workflow/suggest)
- [ ] Zero user-reported cross-agent failures in first month

**For Future Enhancements:**
- [ ] Skill update mechanism working (`bar update-skills`)
- [ ] Skill removal mechanism working (`bar remove-skills`)
- [ ] Skills handle 90%+ of common bar use cases
- [ ] User reports improved response quality
- [ ] Skills work with bar version N and N+1 (backward/forward compatible)

## References

- Existing bar CLI skill at `.claude/skills/bar-cli/`
- Bar token system documentation
- Claude agent type specifications
- Skill installation patterns in other tools
