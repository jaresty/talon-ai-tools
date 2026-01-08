## loop-001 red | helper:rerun go run ./cmd/bar completion fish
- timestamp: 2026-01-08T08:05:12Z
- exit status: 0 (baseline capture)
- helper:diff-snapshot=0 files changed
- excerpt:
  ```
  function __fish_bar_completions
      set -l tokens (commandline -opc)
      set -l partial (commandline -p)
      set -l current (commandline -ct)

      if test (count $tokens) -eq 0
          set tokens ""
      end

      if string match -q '* ' -- $partial
          set tokens $tokens ""
      else if test -n "$current"
          set tokens $tokens $current
      end

      set -l index (math (count $tokens) - 1)
      for item in (command bar __complete fish $index $tokens 2>/dev/null)
          if test -n "$item"
              printf '%s\n' $item
          end
      end
  end
  ```
