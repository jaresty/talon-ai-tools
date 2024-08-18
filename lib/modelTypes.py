from typing import Literal, NotRequired, TypedDict


class GPTMessageItem(TypedDict):
    type: Literal["text", "image_url"]
    text: NotRequired[str]
    image_url: NotRequired[dict[Literal["url"], str]]


class GPTMessage(TypedDict):
    role: Literal["user", "system", "assistant"]
    content: list[GPTMessageItem]


class GPTRequest(TypedDict):
    messages: list[GPTMessage]
    max_tokens: int
    temperature: float
    n: int
    model: str
