mode: command
tag: user.cursorless
-

# Apply a prompt to any text, and output it any target
# Paste it to the cursor if no target is specified
{user.model} <user.modelSimplePrompt> <user.cursorless_target> [<user.cursorless_destination>]$:
    text = user.cursorless_get_text(cursorless_target)
    result = user.gpt_run_prompt(user.modelSimplePrompt, text)
    default_destination = user.cursorless_create_destination(cursorless_target)
    user.cursorless_insert(cursorless_destination or default_destination, result)

# Add the text from a cursorless target to your context
{user.model} pass <user.cursorless_target> [{user.modelDestination}]$:
    text = user.cursorless_get_text(cursorless_target)
    user.gpt_insert_text(text, user.modelDestination)
