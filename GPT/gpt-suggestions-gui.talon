tag: user.model_suggestion_window_open
-

# Voice triggers for the suggestion picker while it is open.

^close suggestions$: user.model_prompt_recipe_suggestions_gui_close()
^run suggestion <number>$: user.model_prompt_recipe_suggestions_run_index(number)
