mode: command
tag: user.gpt_beta
-
# Pass the raw text of a prompt to a destination without actually calling GPT with it
{user.model} pass <user.modelPrompt>:
    user.gpt_beta_paste_prompt(modelPrompt)
