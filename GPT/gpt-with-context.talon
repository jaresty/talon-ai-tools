# All of the following commands allow the user to store or manipulate context
# `thread` represents a conversation with the model
# `context` represents additional info that can persist across `threads`

# Passes a model source to a model destination unchanged; useful for debugging,
# passing around context, or chaining the responses of previous prompts
# If the source is omitted, default to selected text; If the destination is omitted default to paste
# Example: `model pass this to context`
# Example: `model pass context to clip`
# Example: `model pass thread to browser`
# Example: `model pass clip to this`
^{user.model} pass <user.passConfiguration>$:
    user.gpt_pass(passConfiguration)

# Clear the context stored in the model
# Note that if you are in a thread, your thread
# will still remain active.
{user.model} clear context: user.gpt_clear_context()

# Clear the query stored in the model
# Note that if you are in a thread, your thread
# will still remain active.
{user.model} clear query: user.gpt_clear_query()
{user.model} clear all: user.gpt_clear_all()

# Create a new thread which is similar to a conversation with the model
# A thread allows the model to access data from the previous queries in the same thread
{user.model} start thread: user.gpt_enable_threading()

# Clear all data stored in the current thread conversation.
# If threading is enabled, it will stay enabled
{user.model} clear thread: user.gpt_clear_thread()

# Stop threading and do not store model responses as additional contexts
{user.model} stop thread: user.gpt_disable_threading()

# Open a window for visualizing the current thread conversation
# If you are in a thread, it will be automatically updated
# as you say new requests
^{user.model} toggle window$:
    force_open = true
    user.confirmation_gui_refresh_thread(force_open)
