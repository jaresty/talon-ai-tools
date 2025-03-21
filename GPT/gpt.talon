# Shows the list of available prompts
{user.model} help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
{user.model} <user.applyPromptConfiguration>:
    user.gpt_apply_prompt(applyPromptConfiguration)

^{user.model} <user.pleasePromptConfiguration>:
    user.gpt_apply_prompt(pleasePromptConfiguration)

{user.model} {user.search_engine} <user.modelCompoundSource>:
    result = user.gpt_search_engine(search_engine, modelCompoundSource)
    user.search_with_search_engine(search_engine, result)

^{user.model} clear stack {user.letter}:
    user.gpt_clear_stack(letter)

^{user.model} write [{user.modelVoice} | {user.modelAudience} | {user.modelPurpose} | {user.modelTone}]+: user.gpt_set_system_prompt(modelVoice or "", modelAudience or "", modelPurpose or "", modelTone or "")
^{user.model} write reset: user.gpt_reset_system_prompt()

{user.model} analyze prompt <user.modelDestination>$: user.gpt_analyze_prompt(modelDestination)
{user.model} analyze prompt$: user.gpt_analyze_prompt()
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
