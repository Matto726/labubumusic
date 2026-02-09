import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from py_yt import VideosSearch

class RessoService:
    def __init__(self):
        self._regex = r"^(https:\/\/m.resso.com\/)(.*)$"
        self._endpoint = "https://m.resso.com/"

    async def valid(self, url: str):
        return bool(re.search(self._regex, url))

    async def track(self, url, playid: Union[bool, str] = None):
        target = self._endpoint + url if playid else url
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target) as resp:
                if resp.status != 200:
                    return False
                raw_html = await resp.text()

        parser = BeautifulSoup(raw_html, "html.parser")
        meta_title = None
        meta_desc = ""
        tags = parser.find_all("meta")
        for tag in tags:
            prop = tag.get("property")
            if prop == "og:title":
                meta_title = tag.get("content")
            elif prop == "og:description":
                desc_content = tag.get("content")
                meta_desc = desc_content.split("·")[0] if desc_content else ""

        if not meta_desc:
            return None

        yt_search = VideosSearch(meta_title, limit=1)
        res_data = await yt_search.next()
        top_result = res_data["result"][0]
        
        info = {
            "title": top_result["title"],
            "link": top_result["link"],
            "vidid": top_result["id"],
            "duration_min": top_result["duration"],
            "thumb": top_result["thumbnails"][0]["url"].split("?")[0],
        }
        return info, top_result["id"]