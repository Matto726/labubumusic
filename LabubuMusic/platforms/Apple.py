import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from py_yt import VideosSearch

class AppleService:
    def __init__(self):
        self._pattern = r"^(https:\/\/music.apple.com\/)(.*)$"
        self._base_url = "https://music.apple.com/in/playlist/"

    async def valid(self, link: str):
        return bool(re.search(self._pattern, link))

    async def track(self, url, playid: Union[bool, str] = None):
        target_link = self._base_url + url if playid else url
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_link) as resp:
                if resp.status != 200:
                    return False
                page_content = await resp.text()

        soup_obj = BeautifulSoup(page_content, "html.parser")
        query_title = None
        
        meta_tags = soup_obj.find_all("meta")
        for tag in meta_tags:
            if tag.get("property") == "og:title":
                query_title = tag.get("content")
                break
                
        if not query_title:
            return False
            
        search_engine = VideosSearch(query_title, limit=1)
        search_result = await search_engine.next()
        first_entry = search_result["result"][0]
        
        meta_data = {
            "title": first_entry["title"],
            "link": first_entry["link"],
            "vidid": first_entry["id"],
            "duration_min": first_entry["duration"],
            "thumb": first_entry["thumbnails"][0]["url"].split("?")[0],
        }
        return meta_data, first_entry["id"]

    async def playlist(self, url, playid: Union[bool, str] = None):
        target_link = self._base_url + url if playid else url
        pid = url.split("playlist/")[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_link) as resp:
                if resp.status != 200:
                    return False
                page_content = await resp.text()

        soup_obj = BeautifulSoup(page_content, "html.parser")
        song_tags = soup_obj.find_all("meta", attrs={"property": "music:song"})
        
        track_list = []
        for tag in song_tags:
            try:
                content_url = tag["content"]
                raw_name = content_url.split("album/")[1].split("/")[0]
                clean_name = raw_name.replace("-", " ")
                track_list.append(clean_name)
            except Exception:
                continue
                
        return track_list, pid