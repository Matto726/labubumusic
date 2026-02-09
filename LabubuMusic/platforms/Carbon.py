import random
from os.path import realpath
import aiohttp
from aiohttp import client_exceptions

class CarbonFetchError(Exception):
    pass
THEME_LIST = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark", "base16-light",
    "cobalt", "duotone-dark", "dracula-pro", "hopscotch", "lucario",
    "material", "monokai", "nightowl", "nord", "oceanic-next",
    "one-light", "one-dark", "panda-syntax", "parasio-dark", "seti",
    "shades-of-purple", "solarized+dark", "solarized+light", "synthwave-84",
    "twilight", "verminal", "vscode", "yeti", "zenburn"
]

COLOR_PALETTE = [
    "#FF0000", "#FF5733", "#FFFF00", "#008000", "#0000FF", "#800080",
    "#A52A2A", "#FF00FF", "#D2B48C", "#00FFFF", "#808000", "#800000",
    "#00FFFF", "#30D5C8", "#00FF00", "#008080", "#4B0082", "#EE82EE",
    "#FFC0CB", "#000000", "#FFFFFF", "#808080"
]

class CarbonService:
    def __init__(self):
        self.config = {
            "language": "auto",
            "dropShadow": True,
            "dropShadowBlurRadius": "68px",
            "dropShadowOffsetY": "20px",
            "fontFamily": "JetBrains Mono",
            "widthAdjustment": True,
            "watermark": False
        }

    async def generate(self, code_text: str, user_id):
        async with aiohttp.ClientSession(
            headers={"Content-Type": "application/json"}
        ) as session:
            payload = self.config.copy()
            payload.update({
                "code": code_text,
                "backgroundColor": random.choice(COLOR_PALETTE),
                "theme": random.choice(THEME_LIST)
            })
            
            try:
                async with session.post(
                    "https://carbonara.solopov.dev/api/cook",
                    json=payload
                ) as resp:
                    image_data = await resp.read()
            except client_exceptions.ClientConnectorError:
                raise CarbonFetchError("Carbon API Unreachable")
            
            output_path = f"cache/carbon{user_id}.jpg"
            with open(output_path, "wb") as file:
                file.write(image_data)
                
            return realpath(file.name)