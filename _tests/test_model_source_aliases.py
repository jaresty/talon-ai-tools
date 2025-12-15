from talon_user.lib.modelSource import GPTRequest, create_model_source
from talon_user.lib.modelState import GPTState


def test_request_alias_resolves_to_gpt_request_messages():
    GPTState.request = {"messages": [{"role": "user", "content": "hello world"}]}

    source = create_model_source("request")

    assert isinstance(source, GPTRequest)
    assert getattr(source, "modelSimpleSource", "") in {"request", "gptRequest"}
    # The helper flattens role + content with blank lines; just ensure the body is present.
    assert "hello world" in source.get_text()
