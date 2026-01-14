Proposed — TUI redesign: command-centric interface for grammar learning (2026-01-13)

## Context
- **Supersedes ADR 0077** (Bubble Tea TUI interaction simplification). After 17 loops of incremental improvement, the fundamental interaction model proved difficult to learn; this ADR proposes a clean-slate redesign.
- The current TUI evolved from a palette-based token selector into a complex multi-pane layout with Subject, Tokens, Command, and Result zones, each competing for attention.
- Operators report difficulty learning the `bar build` grammar because the interface abstracts the command syntax behind modal interactions and focus management.
- The sidebar displays 11 token categories vertically, overwhelming new users and requiring mental mapping between UI elements and CLI tokens.
- Status messages, summary strips, focus breadcrumbs, and toast notifications create information overload that obscures the primary workflow.
- Tab completion was retrofitted onto the palette filter but the interaction model remains disconnected from how operators would actually type `bar build` commands in a terminal.
- The two-column layout creates navigation complexity (Ctrl+G toggle, auto-hide behavior, focus zones) that distracts from the core task of building a prompt.

## Design Principles
1. **Command as interface**: The `bar build` command line IS the primary interaction surface, not a representation of it.
2. **Grammar through structure**: Selected tokens render as a visual tree that mirrors the command structure, teaching the grammar through direct observation.
3. **Stage-based progression**: Tokens are presented in grammar order (Intent → Preset → Voice → Audience → Tone → Static → Completeness → Scope → Method → Form → Channel → Directional), with inline hints showing where each token belongs in the command. Navigation is bidirectional—Backspace removes the last token and returns to that stage.
4. **Live preview**: The generated prompt updates immediately as tokens change, providing constant feedback.
5. **Progressive disclosure**: Advanced features (command execution, subject input, presets) are accessible but not always visible.
6. **Terminal-native**: The interface should feel like a modern CLI tool (fzf, fish, lazygit) rather than a GUI application.

## Decision

### Layout: Three-Pane Vertical Split

```
┌─────────────────────────────────────────────────────────────────┐
│ > bar build todo focus [Completeness?] _                        │
│             ╰─Static ╰─Scope                                    │
├─────────────────────────────────────────────────────────────────┤
│ TOKENS (2)                  COMPLETENESS                        │
│ ├─ Static: todo             ▸ full         thorough answer      │
│ └─ Scope: focus               gist         concise summary      │
│                               essential    key points only      │
│                             ─────────────────────────────────   │
│                             Tab: skip  │  Then: Method, Form... │
├─────────────────────────────────────────────────────────────────┤
│ PREVIEW                                                         │
│ === TASK (DO THIS) ===                                          │
│ Return a todo list                                              │
│                                                                 │
│ === CONSTRAINTS (GUARDRAILS) ===                                │
│ 1. Scope (focus): The response concentrates on a single focal   │
│    topic without drifting into tangents.                        │
├─────────────────────────────────────────────────────────────────┤
│ Enter: select ▪ Tab/S-Tab: next/prev ▪ BS: remove ▪ ^K: clear   │
│ ^L: subject ▪ ^Enter: run ▪ ^B: copy ▪ Esc: exit                │
└─────────────────────────────────────────────────────────────────┘
```

The command line shows inline stage markers:
- `todo` and `focus` have small annotations (`╰─Static`, `╰─Scope`) showing their category
- `[Completeness?]` indicates the current stage being completed
- Tokens are positioned in grammar order, not append order

**Pane 1 - Command Input (fixed height, 2 lines)**:
- Line 1: The live `bar build` command with inline stage marker (e.g., `[Completeness?]`)
- Line 2: Small annotations below tokens showing their category (e.g., `╰─Static ╰─Scope`)
- Tokens are always positioned in grammar order, teaching the correct CLI syntax
- Typing filters completions within the current stage

**Pane 2 - Tokens & Completions (split horizontally, flexible height)**:
- Left side: Selected tokens as a tree structure showing `Category: value` in grammar order
- Right side: Completions for the **current stage only**, with stage name as header
- Shows "Then: Method, Form..." hint indicating remaining stages
- Up/Down arrows navigate completions; Enter selects; Tab skips stage
- Backspace (with no filter) removes last token and returns to that stage

**Pane 3 - Preview (scrollable, takes remaining space)**:
- Live-rendered prompt that updates as tokens change
- Formatted with clear section headers (Task, Constraints, Persona, Subject)
- When a command runs, this pane shows the command output instead

**Pane 4 - Hotkey Bar (fixed height, 1-2 lines)**:
- Minimal list of available actions; context-sensitive
- No verbose status messages; errors appear inline or as brief toasts

### Interaction Model

**Stage-Based Token Selection (primary workflow)**:
1. The TUI starts at the first stage (Intent) and shows only tokens for that stage
2. Type to fuzzy-filter within the current stage's completions
3. Arrow keys highlight a completion; Enter adds it to the command at the correct position
4. After selecting, the TUI advances to the next stage (or stays if the stage allows multiple selections)
5. Tab skips the current stage without selecting; Shift+Tab goes to the previous stage
6. Backspace behavior depends on context:
   - If there's filter text, Backspace deletes characters from the filter
   - If there's no filter text, Backspace removes the last token AND returns to that token's stage
7. Ctrl+K clears all tokens and restarts from the first stage
8. Preview updates immediately after each change
9. The command line shows `[StageName?]` to indicate what's being asked

**Stage Order** (matches CLI grammar):
1. **Intent** — What the user wants to accomplish (optional, can skip)
2. **Preset** — Saved persona configuration (optional, can skip)
3. **Voice** — Speaking style or persona voice (optional, can skip)
4. **Audience** — Target audience for the response (optional, can skip)
5. **Tone** — Emotional tone of the response (optional, can skip)
6. **Static** — The main prompt type (e.g., "todo", "code-comment")
7. **Completeness** — How thorough (full, gist, essential)
8. **Scope** — How focused (focus, breadth, system) — up to 2 selections
9. **Method** — How to approach (steps, compare, etc.) — up to 3 selections
10. **Form** — Output format (prose, bullets, etc.)
11. **Channel** — Communication style (direct, formal, etc.)
12. **Directional** — Emphasis direction (forward, backward, etc.)

Users can skip any stage with Tab and go back with Shift+Tab, enabling free navigation between stages. The command always shows tokens in grammar order regardless of selection sequence. Backspace on an empty filter removes the last token and returns to that token's stage. Ctrl+K clears all tokens and restarts from the first stage.

**Subject Input (Ctrl+L)**:
- Opens a modal text area for entering/pasting subject content
- Can also load from clipboard with a secondary shortcut
- Subject appears in preview's SUBJECT section when set

**Command Execution (Ctrl+Enter)**:
- Opens a modal input for the shell command (pre-filled if previously used)
- Runs the command with the generated prompt piped to stdin
- Result replaces the preview pane content
- Ctrl+Y yanks result to clipboard; Ctrl+R returns to preview

**Copy CLI (Ctrl+B)**:
- Copies the current `bar build ...` command to clipboard
- Brief toast confirmation, no modal

**Preset Selection (Ctrl+P)**:
- Opens a filterable list of saved presets
- Selecting a preset populates the command with its tokens
- Current tokens can be saved as a new preset

### Token Tree Visualization

The tree structure teaches the grammar by making category relationships visible:

```
TOKENS (3 selected)
├─ Static: todo
├─ Scope: focus
└─ Completeness: full
```

When empty:
```
TOKENS (none selected)
Type to search, Enter to select
```

The tree uses minimal indentation (single level) because tokens are flat in the grammar. Category names are dimmed; values are highlighted.

### Completion Filtering

Completions are **stage-scoped**: only tokens for the current stage appear.

- When at Scope stage, typing `fo` shows only `focus` (not `form` from Form stage)
- Empty input shows all options for the current stage
- The completion header shows the stage name (e.g., "SCOPE" or "COMPLETENESS")
- A "Then:" hint shows upcoming stages so users understand the progression

Completion entries show:
```
▸ focus          concentrates on a single focal topic
```
Value and description (category is implicit from stage header).

**Power user escape hatch**: Typing `category=value` (e.g., `scope=focus`) bypasses stage progression and allows direct override syntax, matching CLI behavior. This works at any time, including after all stages are complete.

**After all stages complete**:
- The completions pane shows "All stages complete" with available actions
- Typing `category=value` syntax allows overriding any previous selection
- Backspace removes the last token and returns to that stage for modification
- The command input becomes effectively read-only for normal typing (no stage to filter)

### Narrow Terminal Adaptation

When terminal width < 80 columns:
- Token tree and completions stack vertically instead of side-by-side
- Preview remains full-width below
- Hotkey bar abbreviates to icons/single letters

### Removed Features

The following features from the current TUI are explicitly removed or deferred:

- **Two-column layout with sidebar**: Replaced by vertical panes
- **Focus zones (Subject/Tokens/Command/Result)**: Single focus on command input
- **Category navigation**: Categories are display-only, not navigable
- **Palette modal (Ctrl+P)**: Completions are always visible; presets use Ctrl+P
- **Status bar with verbose messages**: Replaced by context-sensitive hotkey bar
- **Summary strip**: Information is in the command line and tree
- **History sidebar**: Replaced by undo (Ctrl+Z) and session history (Ctrl+H overlay)
- **Token telemetry display**: Removed (developer feature, not user-facing)

## Rationale
- **Command-centric teaches the grammar**: By typing `bar build todo focus`, operators learn the exact syntax they'll use in terminal scripts and aliases.
- **Stage progression teaches token order**: By presenting tokens in grammar order (Static → Scope → Completeness → ...), users internalize that "todo" comes before "focus" which comes before "full". The inline `[StageName?]` marker shows exactly where each token belongs.
- **Inline annotations reinforce categories**: The small `╰─Static ╰─Scope` markers below tokens provide continuous reinforcement of which category each token belongs to, without cluttering the command.
- **Constrained choices reduce overwhelm**: Showing only current-stage completions (not all 50+ tokens) makes each decision manageable while teaching the grammar's structure.
- **Tree visualization shows structure**: The selected tokens tree provides a mental model of what's been built, always in grammar order.
- **Live preview creates tight feedback loop**: Changes are visible immediately, encouraging experimentation.
- **Minimal chrome reduces cognitive load**: Fewer UI elements means attention focuses on the task.
- **Terminal-native feel**: Operators familiar with fzf, fish, or lazygit will find the interaction model intuitive.

## Consequences

### Implementation Changes
- `internal/bartui/program.go` requires significant refactoring to implement the three-pane layout
- Remove focus zone management, sidebar toggle, palette modal, summary strip, and status bar
- Implement fuzzy matching for completions (can use existing `getCompletionsForPartial` as base)
- Add tree rendering for selected tokens
- Refactor command execution to use modal workflow instead of always-visible pane
- Update all expect tests to match new output format

### Reusable Components
- Preview rendering can reuse existing prompt generation
- Token category definitions remain unchanged
- CLI builder logic transfers directly
- Clipboard integration remains the same

### New Dependencies
- May benefit from Bubble Tea's `list` component for completions
- Consider `bubbles/textinput` with custom completion handler

### Migration Path
1. Build new TUI as separate command (`bar tui2` or feature flag)
2. Validate with operators for usability
3. Replace default `bar tui` once stable
4. Archive old implementation in case rollback needed

## Validation
- `go test ./internal/bartui` with new test suite matching redesigned components
- `scripts/tools/run-tui-expect.sh --all` with updated expect scripts for new output format
- Manual usability testing: can a new user build `bar build todo focus full` within 30 seconds?
- Grammar learning validation: after 5 minutes, can the user type the command from memory?

## Follow-up
- Prototype the three-pane layout to validate screen space allocation
- Evaluate fuzzy matching libraries vs. custom implementation
- Design preset management workflow (save/load/edit)
- Consider fish-style autosuggestions (ghost text showing most likely completion)
- Investigate syntax highlighting for the command input (category colors)
- Plan migration from current TUI to new design

## Alternatives Considered

### Pure Wizard-style (Modal Questions)
Walk users through categories with modal dialogs: "What task?" → "How thorough?" → "What scope?"

Rejected: Too slow for experts; hides the command structure behind modals. Our stage-based approach differs by keeping the command visible at all times with inline stage markers, so users see exactly how their choices build the CLI command.

### Chat-style Interface
Type commands as messages, see prompt as response, history scrolls above.

Rejected: Doesn't feel like a tool; weird for a command builder.

### Keep Current Layout, Simplify Controls
Reduce shortcuts and remove sidebar but keep the four-zone layout.

Rejected: The fundamental problem is the layout itself, not just the controls. Subject/Tokens/Command/Result as separate zones doesn't match the mental model of "building a command."

### Full-Screen Completion Menu (fzf clone)
Single filterable list of all options, full screen, no preview.

Rejected: Loses the live preview feedback that makes the grammar learnable. Preview is essential.

### Flat Fuzzy Search Across All Categories
Show all 50+ tokens in a single filterable list, append selections in any order.

Rejected after initial implementation: While convenient for power users who already know the grammar, this approach fails to teach token ordering. Users select tokens in random order and the command doesn't reflect the canonical grammar structure. New users never learn that "todo" (Static) should come before "focus" (Scope) which should come before "full" (Completeness).
