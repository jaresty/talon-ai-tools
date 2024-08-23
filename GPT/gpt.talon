# Shows the list of available prompts
{user.model} help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
{user.model} <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]$:
    user.gpt_apply_prompt(modelPrompt, modelSource_1 or "", "", modelDestination or "")

# Runs a model prompt on two targets
{user.model} <user.modelSimplePairPrompt> {user.modelSource} [with {user.modelSource}] [{user.modelDestination}]$:
    user.gpt_apply_prompt(modelSimplePairPrompt, modelSource_1 or "", modelSource_2 or "", modelDestination or "")

^{user.model} [<user.modelPrompt>] <user.pleasePrompt> [{user.modelSource}] [{user.modelDestination}]$:
    user.gpt_apply_prompt(pleasePrompt, modelSource or "", "", modelDestination or "")

{user.model} analyze prompt [{user.modelDestination}]$: user.gpt_analyze_prompt(modelDestination or "")
{user.model} replay [{user.modelDestination}]$: user.gpt_replay(modelDestination or "")

# Select the last GPT response so you can edit it further
{user.model} take response: user.gpt_select_last()

# Reformat the last dictation with additional context or formatting instructions
{user.model} [nope] that was <user.text>$:
    result = user.gpt_reformat_last(text)
    user.paste(result)

# Enable debug logging so you can more details about messages being sent
{user.model} start debug: user.gpt_start_debug()

# Disable debug logging
{user.model} stop debug: user.gpt_stop_debug()
