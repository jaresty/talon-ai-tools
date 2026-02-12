not user.gpt_busy
-
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
{user.model} run suggest again$: user.gpt_rerun_last_suggest()

{user.model} run [<user.modelSimpleSource>] [<user.modelDestination>] preset <user.text>$:
    user.gpt_run_preset_with_source(modelSimpleSource or "", modelDestination or "", text)
