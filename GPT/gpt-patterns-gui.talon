tag: user.model_pattern_window_open
-

# Voice triggers for the pattern picker while it is open.
# These run the corresponding pattern and dismiss the GUI.

^debug bug$: user.model_pattern_run_name("Debug bug")
^fix locally$: user.model_pattern_run_name("Fix locally")
^explain flow$: user.model_pattern_run_name("Explain flow")
^summarize selection$: user.model_pattern_run_name("Summarize selection")
^extract todos$: user.model_pattern_run_name("Extract todos")

^summarize gist$: user.model_pattern_run_name("Summarize gist")
^product framing$: user.model_pattern_run_name("Product framing")
^retro reflect$: user.model_pattern_run_name("Retro / reflect")
^pain points$: user.model_pattern_run_name("Pain points")

^close patterns$: user.model_pattern_gui_close()
^help hub$: user.help_hub_open()
