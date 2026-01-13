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
3. **Fuzzy search, not navigation**: Type to filter completions across all categories simultaneously; no category browsing required.
4. **Live preview**: The generated prompt updates immediately as tokens change, providing constant feedback.
5. **Progressive disclosure**: Advanced features (command execution, subject input, presets) are accessible but not always visible.
6. **Terminal-native**: The interface should feel like a modern CLI tool (fzf, fish, lazygit) rather than a GUI application.

## Decision

### Layout: Three-Pane Vertical Split

```
┌─────────────────────────────────────────────────────────────────┐
│ > bar build todo focus_                                         │
├─────────────────────────────────────────────────────────────────┤
│ TOKENS                            COMPLETIONS                   │
│ └─ Static: todo                   ▸ breadth      Scope          │
│ └─ Scope: focus                   ▸ full         Completeness   │
│                                   ▸ gist         Completeness   │
│                                   ▸ steps        Method         │
│                                   ▸ inform       Intent         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ PREVIEW                                                         │
│ ═══════                                                         │
│ === TASK (DO THIS) ===                                          │
│ Return a todo list                                              │
│                                                                 │
│ === CONSTRAINTS (GUARDRAILS) ===                                │
│ 1. Scope (focus): The response concentrates on a single focal   │
│    topic without drifting into tangents.                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Enter: select ▪ Backspace: remove last ▪ Ctrl+L: subject        │
│ Ctrl+Enter: run command ▪ Ctrl+B: copy CLI ▪ Esc: exit          │
└─────────────────────────────────────────────────────────────────┘
```

**Pane 1 - Command Input (fixed height, ~1 line)**:
- Single text input showing the live `bar build` command
- Cursor position determines where the next token inserts
- Typing filters the completions pane instantly

**Pane 2 - Tokens & Completions (split horizontally, flexible height)**:
- Left side: Selected tokens as a simple tree structure showing `Category: value`
- Right side: Filtered completions grouped by category, fuzzy-matched to input
- Up/Down arrows navigate completions; Enter selects; Backspace removes last token

**Pane 3 - Preview (scrollable, takes remaining space)**:
- Live-rendered prompt that updates as tokens change
- Formatted with clear section headers (Task, Constraints, Persona, Subject)
- When a command runs, this pane shows the command output instead

**Pane 4 - Hotkey Bar (fixed height, 1-2 lines)**:
- Minimal list of available actions; context-sensitive
- No verbose status messages; errors appear inline or as brief toasts

### Interaction Model

**Token Selection (primary workflow)**:
1. Type in the command input to fuzzy-filter completions
2. Arrow keys highlight a completion; Enter adds it to the command
3. Selected token appears in the tree and the command line updates
4. Backspace removes the last token (or deletes characters if mid-word)
5. Preview updates immediately after each change

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

Completions use fuzzy matching (like fzf) across all categories:

- `fo` matches: `focus` (Scope), `form` (Form), `fog` (Directional), `inform` (Intent)
- `scope:fo` narrows to Scope category only (colon syntax for power users)
- Empty input shows all available options, prioritized by: recently used, then category order

Completion entries show:
```
▸ focus          Scope — concentrates on a single focal topic
```
Value, category, and brief description (truncated to fit).

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
- **Fuzzy search eliminates navigation overhead**: No need to browse 11 categories; type what you want and it appears.
- **Tree visualization shows structure**: The selected tokens tree provides a mental model of what's been built without requiring category knowledge.
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

### Wizard-style Progressive Disclosure
Walk users through categories one at a time: "What task?" → "How thorough?" → "What scope?"

Rejected: Too slow for experts; doesn't teach the grammar because it hides the command structure.

### Chat-style Interface
Type commands as messages, see prompt as response, history scrolls above.

Rejected: Doesn't feel like a tool; weird for a command builder.

### Keep Current Layout, Simplify Controls
Reduce shortcuts and remove sidebar but keep the four-zone layout.

Rejected: The fundamental problem is the layout itself, not just the controls. Subject/Tokens/Command/Result as separate zones doesn't match the mental model of "building a command."

### Full-Screen Completion Menu (fzf clone)
Single filterable list of all options, full screen, no preview.

Rejected: Loses the live preview feedback that makes the grammar learnable. Preview is essential.
