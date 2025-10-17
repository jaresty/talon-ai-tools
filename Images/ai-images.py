import webbrowser

import requests
from talon import Module

from ..lib.modelHelpers import get_token, notify

mod = Module()


@mod.action_class
class Actions:
    def image_generate(prompt: str):
        """Generate an image from the provided text"""

        url = "https://api.openai.com/v1/images/generations"
        TOKEN = get_token()
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
