## Behaviour outcome
Implement CLI command input mode for the token palette, showing live `bar build` command in the filter and updating status line to guide Tab completion workflow.

## Commands executed

### Tests
- green | 2026-01-13T17:25:00Z | scripts/tools/run-tui-expect.sh --all
  - 8 tests passed: clipboard-history, environment-allowlist, focus-cycle, launch-status, sticky-summary, token-command-history, token-palette-history, token-palette-workflow

## Implementation notes
- Modified palette status line to show CLI command syntax: `bar build=` when empty, `bar build infer=` when typing
- Updated status guidance: "type a value, press Tab to cycle completions, Enter applies an option"
- Added "copy command" instruction in status for discoverability of CLI copy action
- Ctrl+W now shows "CLI command reset" status confirming filter cleared
- Updated expect tests to match new CLI command input mode behavior:
  - token-palette-history.exp: Uses "infer" token instead of "todo", expects CLI syntax in status
  - token-palette-workflow.exp: Updated all status expectations for new CLI-focused messaging
- Filter input now displays with `bar build` prefix, making the CLI grammar visible
- Enter on a filtered token navigates to toggle state, second Enter applies
