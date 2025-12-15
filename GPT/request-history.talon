# Model request history commands

{user.model} history latest$: user.gpt_request_history_show_latest()
{user.model} history previous$: user.gpt_request_history_prev()
{user.model} history next$: user.gpt_request_history_next()
{user.model} history list$: user.gpt_request_history_list()
{user.model} history save source$: user.gpt_request_history_save_latest_source()
{user.model} history copy last save$: user.gpt_request_history_copy_last_save_path()
{user.model} history open last save$: user.gpt_request_history_open_last_save_path()
{user.model} history show last save$: user.gpt_request_history_show_last_save_path()
{user.model} history drawer$: user.request_history_drawer_toggle()
