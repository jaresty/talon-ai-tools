---
name: bar
description: bar CLI — structured prompting tool. Use when the user wants to run bar build, apply bar tokens, build a workflow, or get help with bar commands. Covers autopilot, workflow, suggest, manual, dictionary, and all bar token usage.
allowed-tools: Bash(bar:*)
---

# bar

bar is a structured prompting CLI that shapes LLM responses via token axes (task, completeness, scope, method, form, persona).

## Start here

Before doing anything bar-related, load the available skills:

```bash
bar skills list
```

Then load the specific skill you need:

```bash
bar skills get bar-autopilot   # automatically apply bar structuring to responses
bar skills get bar-workflow    # build and execute multi-step bar command sequences
bar skills get bar-suggest     # present users with bar-based approach options
bar skills get bar-manual      # guide users on how to manually build bar commands
bar skills get bar-dictionary  # look up bar tokens by intent (used by other skills)
```

## Skill dispatch

If the user invokes `/bar suggest`, `/bar workflow`, `/bar autopilot`, etc., treat the
suffix as a skill name — run `bar skills get bar-<suffix>` rather than looking for a
matching CLI subcommand. These are skills, not native subcommands.

```bash
# /bar suggest  →
bar skills get bar-suggest

# /bar workflow  →
bar skills get bar-workflow
```

Do not reject a `/bar X` invocation because `bar X` fails as a shell command — check
the skill layer first.

## Quick reference

```bash
bar build <tokens> --subject "..."            # build a structured prompt
bar build <tokens> --subject "..." \
  --addendum "extra context or constraints"   # append additional context
bar help llm                                  # full token reference for LLM agents
bar skills list                               # list available skills
bar skills get <name>                         # load a specific skill
bar install-skills [--location PATH]          # install this stub to ~/.claude/skills
```
