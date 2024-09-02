mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
# Paste it to the cursor if no target is specified
{user.model} <user.modelSimplePrompt> <user.cursorless_target> [{user.modelDestination}]$:
    text = user.cursorless_get_text(cursorless_target)
    result = user.gpt_run_prompt(user.modelSimplePrompt, text)
    user.gpt_insert_text(result, modelDestination or "window")

# Apply a paired prompt to any two targets, and output it any target
# Paste it to the cursor if no target is specified
{user.model} <user.modelSimplePrompt> <user.cursorless_target> with <user.cursorless_target> [{user.modelDestination}]$:
    first_source = user.cursorless_get_text(cursorless_target_1)
    second_source = user.cursorless_get_text(cursorless_target_2)
    result = user.gpt_run_prompt(user.modelSimplePairPrompt, first_source, second_source)
    user.gpt_insert_text(result, modelDestination or "window")

# Add the text from a cursorless target to your context
{user.model} pass <user.cursorless_target> [{user.modelDestination}]$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_insert_text(text, user.modelDestination)
