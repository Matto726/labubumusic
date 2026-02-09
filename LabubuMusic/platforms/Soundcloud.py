from os import path
from yt_dlp import YoutubeDL
from LabubuMusic.utils.formatters import seconds_to_min

class SoundCloudService:
    def __init__(self):
        self.dl_config = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
        }

    async def valid(self, url: str):
        return "soundcloud" in url

    async def download(self, url):
        downloader = YoutubeDL(self.dl_config)
        try:
            data = downloader.extract_info(url)
        except Exception:
            return False

        file_location = path.join("downloads", f"{data['id']}.{data['ext']}")
        
        meta = {
            "title": data["title"],
            "duration_sec": data["duration"],
            "duration_min": seconds_to_min(data["duration"]),
            "uploader": data["uploader"],
            "filepath": file_location,
        }
        return meta, file_location