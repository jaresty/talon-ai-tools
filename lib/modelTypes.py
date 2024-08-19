from typing import Literal, TypedDict


class GPTTextItem(TypedDict):
    type: Literal["text"]
    text: str


class GPTImageItem(TypedDict):
    type: Literal["image_url"]
    image_url: dict[Literal["url"], str]


class GPTMessage(TypedDict):
    role: Literal["user", "system", "assistant"]
    content: list[GPTTextItem | GPTImageItem]


class GPTRequest(TypedDict):
    messages: list[GPTMessage]
    max_tokens: int
    temperature: float
    n: int
    model: str
