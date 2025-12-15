# Shows the list of available prompts
{user.model} help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
{user.model} run <user.applyPromptConfiguration>:
    user.gpt_apply_prompt(applyPromptConfiguration)

^{user.model} run <user.pleasePromptConfiguration>:
    user.gpt_apply_prompt(pleasePromptConfiguration)

{user.model} run {user.search_engine} <user.modelCompoundSource>:
    result = user.gpt_search_engine(search_engine, modelCompoundSource)
    user.search_with_search_engine(search_engine, result)

^{user.model} clear stack {user.letter}:
    user.gpt_clear_stack(letter)

^{user.model} write [{user.modelVoice} | {user.modelAudience} | {user.modelIntent} | {user.modelTone}]+: user.gpt_set_system_prompt(modelVoice or "", modelAudience or "", modelIntent or "", modelTone or "")
^{user.model} reset writing$: user.gpt_reset_system_prompt()

^{user.model} set completeness {user.completenessModifier}$: user.gpt_set_default_completeness(completenessModifier)
^{user.model} set scope {user.scopeModifier}$: user.gpt_set_default_scope(scopeModifier)
^{user.model} set method {user.methodModifier}$: user.gpt_set_default_method(methodModifier)
^{user.model} set form {user.formModifier}$: user.gpt_set_default_form(formModifier)
^{user.model} set channel {user.channelModifier}$: user.gpt_set_default_channel(channelModifier)

^{user.model} reset completeness$: user.gpt_reset_default_completeness()
^{user.model} reset scope$: user.gpt_reset_default_scope()
^{user.model} reset method$: user.gpt_reset_default_method()
^{user.model} reset form$: user.gpt_reset_default_form()
^{user.model} reset channel$: user.gpt_reset_default_channel()

{user.model} analyze prompt <user.modelDestination>$: user.gpt_analyze_prompt(modelDestination)
{user.model} analyze prompt$: user.gpt_analyze_prompt()
{user.model} replay [{user.modelDestination}]$: user.gpt_replay(modelDestination or "")

{user.model} last recipe$: user.gpt_show_last_recipe()
{user.model} last meta$: user.gpt_show_last_meta()

{user.model} debug logs$: user.gpt_copy_last_raw_exchange()
{user.model} cancel$: user.gpt_cancel_request()
{user.model} async blocking$: user.gpt_set_async_blocking(1)
{user.model} async non blocking$: user.gpt_set_async_blocking(0)

^{user.model} run again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.formModifier}] [{user.channelModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe(staticPrompt or "", completenessModifier or "", scopeModifier_list or "", methodModifier_list or "", directionalModifier or "", formModifier or "", channelModifier or "")

^{user.model} run again [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.formModifier}] [{user.channelModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe("", completenessModifier or "", scopeModifier_list or "", methodModifier_list or "", directionalModifier or "", formModifier or "", channelModifier or "")

^{user.model} run <user.modelSimpleSource> again$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, "", "", "", "", "", "")

^{user.model} run <user.modelSimpleSource> again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.formModifier}] [{user.channelModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, staticPrompt or "", completenessModifier or "", scopeModifier_list or "", methodModifier_list, directionalModifier or "", formModifier or "", channelModifier or "")

^{user.model} run <user.modelSimpleSource> again [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.formModifier}] [{user.channelModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, "", completenessModifier or "", scopeModifier_list or "", methodModifier_list, directionalModifier or "", formModifier or "", channelModifier or "")

{user.model} run <user.modelSimpleSource> suggest [for <user.modelPromptSuffix>]$: user.gpt_suggest_prompt_recipes_with_source(modelSimpleSource, modelPromptSuffix or "")
{user.model} run suggest [for <user.modelPromptSuffix>]$: user.gpt_suggest_prompt_recipes(modelPromptSuffix or "")
{user.model} suggestions$: user.model_prompt_recipe_suggestions_gui_open()

# Select the last GPT response so you can edit it further
{user.model} take response: user.gpt_select_last()

# Enable debug logging so you can more details about messages being sent
{user.model} start debug: user.gpt_start_debug()

# Disable debug logging
{user.model} stop debug: user.gpt_stop_debug()

# Persona / Intent preset stance commands (ADR 042)
persona {user.personaPreset}: user.persona_set_preset(personaPreset)
intent {user.intentPreset}: user.intent_set_preset(intentPreset)

{user.model} preset save <user.text>$: user.gpt_preset_save(text)
{user.model} preset run <user.text>$: user.gpt_preset_run(text)
{user.model} preset list$: user.gpt_preset_list()

persona status: user.persona_status()
intent status: user.intent_status()

persona reset: user.persona_reset()
intent reset: user.intent_reset()

# Provider selection (ADR 047)
{user.model} provider list$: user.model_provider_list()
{user.model} provider status$: user.model_provider_status()
{user.model} provider (use|switch) <user.text>$: user.model_provider_use(text)
{user.model} provider (use|switch) <user.text> model <user.text>$: user.model_provider_use(text, text1)
{user.model} provider next$: user.model_provider_next()
{user.model} provider previous$: user.model_provider_previous()
{user.model} provider close$: user.model_provider_close()
