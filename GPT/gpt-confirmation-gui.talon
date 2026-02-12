tag: user.model_window_open
-

# Confirm and paste the output of the model
^paste response$: user.confirmation_gui_paste()
^{user.model} pass response$: user.confirmation_gui_paste()

# Confirm and paste the output of the model selected
^chain response$:
    user.confirmation_gui_paste()
    user.gpt_select_last()

^copy response$: user.confirmation_gui_copy()
^pass to context$: user.confirmation_gui_pass_context()
^pass to query$: user.confirmation_gui_pass_query()
^pass to thread$: user.confirmation_gui_pass_thread()
^open browser$: user.confirmation_gui_open_browser()
^analyze prompt$: user.confirmation_gui_analyze_prompt()

# Deny the output of the model and discard it
^discard response$: user.confirmation_gui_close()

^{user.model} toggle window$: user.confirmation_gui_close()
