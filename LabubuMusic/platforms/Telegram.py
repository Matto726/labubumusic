import asyncio
import os
import time
from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice
import config
from LabubuMusic import matto_bot
from LabubuMusic.utils.formatters import (
    check_duration,
    convert_bytes,
    get_readable_time,
    seconds_to_min,
)

class TelegramService:
    def __init__(self):
        self.limit = 4096

    async def send_split_text(self, message, text_content):
        chunks = (text_content[i : i + self.limit] for i in range(0, len(text_content), self.limit))
        
        count = 0
        for chunk in chunks:
            if count < 3:
                await message.reply_text(chunk, disable_web_page_preview=True)
                count += 1
        return True

    async def get_link(self, msg):
        return msg.link

    async def get_filename(self, file_obj, is_audio: Union[bool, str] = None):
        try:
            fname = file_obj.file_name
            if not fname:
                fname = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if is_audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        except:
            fname = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if is_audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        return fname

    async def get_duration(self, file_obj, file_path=None):
        try:
            return seconds_to_min(file_obj.duration)
        except:
            if file_path:
                try:
                    raw_dur = await asyncio.get_event_loop().run_in_executor(
                        None, check_duration, file_path
                    )
                    return seconds_to_min(raw_dur)
                except:
                    pass
            return "Unknown"

    async def get_filepath(self, audio=None, video=None):
        base_dir = os.path.realpath("downloads")
        
        if audio:
            uid = audio.file_unique_id
            try:
                ext = "ogg" if isinstance(audio, Voice) else audio.file_name.split(".")[-1]
            except:
                ext = "ogg"
            return os.path.join(base_dir, f"{uid}.{ext}")
            
        if video:
            uid = video.file_unique_id
            try:
                ext = video.file_name.split(".")[-1]
            except:
                ext = "mp4"
            return os.path.join(base_dir, f"{uid}.{ext}")
            
        return None

    async def download(self, _, message, status_msg, filename):
        checkpoints = {0, 10, 25, 50, 75, 90, 100}
        last_update = 0
        start_time = time.time()
        
        if os.path.exists(filename):
            return True

        async def _progress_hook(current, total):
            nonlocal last_update
            now = time.time()

            pct = int(current * 100 / total)
            if pct in checkpoints and (now - last_update) > 3:
                last_update = now
                diff = now - start_time
                speed = current / diff if diff > 0 else 0
                
                eta = int((total - current) / speed) if speed > 0 else 0
                eta_str = get_readable_time(eta) or "0 sᴇᴄᴏɴᴅs"
                
                stats = _["tg_1"].format(
                    matto_bot.mention,
                    convert_bytes(total),
                    convert_bytes(current),
                    f"{pct}%",
                    convert_bytes(speed),
                    eta_str,
                )
                
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="stop_downloading")]
                ])
                
                try:
                    await status_msg.edit_text(text=stats, reply_markup=buttons)
                except:
                    pass

        try:
            await matto_bot.download_media(
                message.reply_to_message,
                file_name=filename,
                progress=_progress_hook,
            )
            
            total_time = get_readable_time(int(time.time() - start_time)) or "0 sᴇᴄᴏɴᴅs"
            await status_msg.edit_text(_["tg_2"].format(total_time))
            return True
            
        except Exception:
            await status_msg.edit_text(_["tg_3"])
            return False

    