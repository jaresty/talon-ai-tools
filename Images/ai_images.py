import webbrowser

import requests
from talon import Module

from ..lib.modelHelpers import (
    UnsupportedProviderCapability,
    active_provider,
    get_token,
    notify,
)
from ..lib.providerCanvas import show_provider_canvas

mod = Module()


@mod.action_class
class Actions:
    def image_generate(prompt: str):
        """Generate an image from the provided text"""

        provider = active_provider()
        if not provider.features.get("images", False):
            show_provider_canvas(
                "Provider error",
                [f"Provider '{provider.id}' does not support image generation."],
            )
            raise UnsupportedProviderCapability(provider.id, "images")

        url = _image_endpoint_for(provider.endpoint)
        TOKEN = get_token(provider)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_dict = response.json()
            image_url = response_dict["data"][0]["url"]
            # TODO choose whether to save the image, save the url, or paste the image into the current window
            webbrowser.open(image_url)
            return

        print(response.json())
        notify("Error generating image")
        raise Exception("Error generating image")


def _image_endpoint_for(chat_endpoint: str) -> str:
    """Derive an image generation endpoint from the provider chat endpoint."""

    if chat_endpoint and "images/generations" in chat_endpoint:
        return chat_endpoint
    if chat_endpoint and "chat/completions" in chat_endpoint:
        return chat_endpoint.replace("chat/completions", "images/generations")
    if chat_endpoint and chat_endpoint.rstrip("/").endswith("/v1"):
        return chat_endpoint.rstrip("/") + "/images/generations"
    # Fallback to OpenAI default.
    return "https://api.openai.com/v1/images/generations"
