mode: command
tag: user.gpt_beta
-

# Find all Talon commands that match the user's text
{user.model} find <user.text>: user.gpt_find_talon_commands(user.text)

# Pass the raw text of a prompt to a destination without actually calling GPT with it
{user.model} pass <user.modelPrompt> [{user.modelDestination}]:
    user.gpt_insert_response(modelPrompt, modelDestination or "")
