import asyncio
import os
import re
from typing import Union
import yt_dlp
import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from LabubuMusic.utils.formatters import time_to_seconds
from LabubuMusic import log_factory

try:
    from py_yt import VideosSearch
except ImportError:
    from youtubesearchpython.__future__ import VideosSearch

BACKEND_URL = "https://shrutibots.site"

async def _fetch_media(link: str, media_type: str) -> str:
    """Internal helper to handle download logic for both audio and video."""
    vid = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not vid or len(vid) < 3:
        return None

    dl_folder = "downloads"
    os.makedirs(dl_folder, exist_ok=True)
    ext = "mp3" if media_type == "audio" else "mp4"
    target_path = os.path.join(dl_folder, f"{vid}.{ext}")

    if os.path.exists(target_path):
        return target_path

    try:
        async with aiohttp.ClientSession() as session:
            init_url = f"{BACKEND_URL}/download"
            async with session.get(init_url, params={"url": vid, "type": media_type}, timeout=aiohttp.ClientTimeout(total=7)) as resp:
                if resp.status != 200:
                    return None
                token_data = await resp.json()
            
            token = token_data.get("download_token")
            if not token:
                return None

            stream_url = f"{BACKEND_URL}/stream/{vid}?type={media_type}&token={token}"
            timeout_val = 300 if media_type == "audio" else 600
            
            async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=timeout_val)) as file_resp:
                final_resp = file_resp

                if file_resp.status == 302:
                    loc = file_resp.headers.get('Location')
                    if loc:
                        final_resp = await session.get(loc)
                
                if final_resp.status != 200:
                    return None

                with open(target_path, "wb") as f:
                    async for chunk in final_resp.content.iter_chunked(16384):
                        f.write(chunk)
                
                if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    return target_path
                return None

    except Exception:
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except:
                pass
        return None

async def download_song(link: str) -> str:
    return await _fetch_media(link, "audio")

async def download_video(link: str) -> str:
    return await _fetch_media(link, "video")

async def run_shell(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    
    err_msg = stderr.decode("utf-8")
    if err_msg and "unavailable videos are hidden" not in err_msg.lower():
        return err_msg
    return stdout.decode("utf-8")

class YouTubeService:
    def __init__(self):
        self._watch_url = "https://www.youtube.com/watch?v="
        self._pattern = r"(?:youtube\.com|youtu\.be)"
        self._playlist_url = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        target = self._watch_url + link if videoid else link
        return bool(re.search(self._pattern, target))

    async def url(self, msg: Message) -> Union[str, None]:
        msgs = [msg]
        if msg.reply_to_message:
            msgs.append(msg.reply_to_message)
            
        for m in msgs:
            if m.entities:
                for ent in m.entities:
                    if ent.type == MessageEntityType.URL:
                        return (m.text or m.caption)[ent.offset : ent.offset + ent.length]
            elif m.caption_entities:
                for ent in m.caption_entities:
                    if ent.type == MessageEntityType.TEXT_LINK:
                        return ent.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        clean_link = (self._watch_url + link if videoid else link).split("&")[0]
        
        search = VideosSearch(clean_link, limit=1)
        res = await search.next()
        data = res["result"][0]
        
        dur_min = data["duration"]
        dur_sec = int(time_to_seconds(dur_min)) if dur_min else 0
        
        return (
            data["title"],
            dur_min,
            dur_sec,
            data["thumbnails"][0]["url"].split("?")[0],
            data["id"]
        )

    
    async def title(self, link, videoid=None):
        return (await self.details(link, videoid))[0]

    async def duration(self, link, videoid=None):
        return (await self.details(link, videoid))[1]

    async def thumbnail(self, link, videoid=None):
        return (await self.details(link, videoid))[3]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        clean_link = (self._watch_url + link if videoid else link).split("&")[0]
        try:
            path = await download_video(clean_link)
            return (1, path) if path else (0, "Video download failed")
        except Exception as e:
            return 0, f"Error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        clean_link = (self._playlist_url + link if videoid else link).split("&")[0]
        
        cmd = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {clean_link}"
        output = await run_shell(cmd)
        
        return [x for x in output.split("\n") if x]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        clean_link = (self._watch_url + link if videoid else link).split("&")[0]
        
        search = VideosSearch(clean_link, limit=1)
        res = await search.next()
        data = res["result"][0]
        
        return {
            "title": data["title"],
            "link": data["link"],
            "vidid": data["id"],
            "duration_min": data["duration"],
            "thumb": data["thumbnails"][0]["url"].split("?")[0],
        }, data["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        clean_link = (self._watch_url + link if videoid else link).split("&")[0]
        
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(clean_link, download=False)
            
            avail_formats = []
            for fmt in info.get("formats", []):
                try:
                    if "dash" not in str(fmt.get("format")).lower():
                        avail_formats.append({
                            "format": fmt["format"],
                            "filesize": fmt.get("filesize"),
                            "format_id": fmt["format_id"],
                            "ext": fmt["ext"],
                            "format_note": fmt.get("format_note"),
                            "yturl": clean_link,
                        })
                except:
                    continue
            return avail_formats, clean_link

    async def slider(self, link: str, index: int, videoid: Union[bool, str] = None):
        clean_link = (self._watch_url + link if videoid else link).split("&")[0]
        
        search = VideosSearch(clean_link, limit=10)
        res = (await search.next()).get("result")
        
        item = res[index]
        return (
            item["title"],
            item["duration"],
            item["thumbnails"][0]["url"].split("?")[0],
            item["id"]
        )

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        clean_link = (self._watch_url + link if videoid else link)
        
        try:
            path = await download_video(clean_link) if video else await download_song(clean_link)
            return (path, True) if path else (None, False)
        except Exception:
            return None, False