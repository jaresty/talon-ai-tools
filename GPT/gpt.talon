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
^{user.model} reset writing$: user.gpt_reset_system_prompt()

^{user.model} set completeness {user.completenessModifier}$: user.gpt_set_default_completeness(completenessModifier)
^{user.model} set scope {user.scopeModifier}$: user.gpt_set_default_scope(scopeModifier)
^{user.model} set method {user.methodModifier}$: user.gpt_set_default_method(methodModifier)
^{user.model} set style {user.styleModifier}$: user.gpt_set_default_style(styleModifier)

^{user.model} reset completeness$: user.gpt_reset_default_completeness()
^{user.model} reset scope$: user.gpt_reset_default_scope()
^{user.model} reset method$: user.gpt_reset_default_method()
^{user.model} reset style$: user.gpt_reset_default_style()

{user.model} analyze prompt <user.modelDestination>$: user.gpt_analyze_prompt(modelDestination)
{user.model} analyze prompt$: user.gpt_analyze_prompt()
{user.model} replay [{user.modelDestination}]$: user.gpt_replay(modelDestination or "")

{user.model} last recipe$: user.gpt_show_last_recipe()
{user.model} last meta$: user.gpt_show_last_meta()

{user.model} debug logs$: user.gpt_copy_last_raw_exchange()
{user.model} cancel$: user.gpt_cancel_request()
{user.model} async blocking$: user.gpt_set_async_blocking(1)
{user.model} async non blocking$: user.gpt_set_async_blocking(0)

^{user.model} again$:
    user.gpt_rerun_last_recipe("", "", "", "", "", "")

^{user.model} again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe(staticPrompt or "", completenessModifier or "", scopeModifier_list or "", methodModifier_list or "", styleModifier_list or "", directionalModifier or "")

^{user.model} again [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe("", completenessModifier or "", scopeModifier_list or "", methodModifier_list or "", styleModifier_list or "", directionalModifier or "")

^{user.model} <user.modelSimpleSource> again$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, "", "", "", "", "", "")

^{user.model} <user.modelSimpleSource> again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, staticPrompt or "", completenessModifier or "", scopeModifier_list or "", methodModifier_list, styleModifier_list, directionalModifier or "")

^{user.model} <user.modelSimpleSource> again [{user.completenessModifier}] [{user.scopeModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:
    user.gpt_rerun_last_recipe_with_source(modelSimpleSource, "", completenessModifier or "", scopeModifier_list or "", methodModifier_list, styleModifier_list, directionalModifier or "")

{user.model} <user.modelSimpleSource> suggest for <user.text>$: user.gpt_suggest_prompt_recipes_with_source(modelSimpleSource, text)
{user.model} <user.modelSimpleSource> suggest$: user.gpt_suggest_prompt_recipes_with_source(modelSimpleSource, "")
{user.model} suggest for <user.text>$: user.gpt_suggest_prompt_recipes(text)
{user.model} suggest$: user.gpt_suggest_prompt_recipes("")
{user.model} suggestions$: user.model_prompt_recipe_suggestions_gui_open()

# Select the last GPT response so you can edit it further
{user.model} take response: user.gpt_select_last()

# Enable debug logging so you can more details about messages being sent
{user.model} start debug: user.gpt_start_debug()

# Disable debug logging
{user.model} stop debug: user.gpt_stop_debug()
