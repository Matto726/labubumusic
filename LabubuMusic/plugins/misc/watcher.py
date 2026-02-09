from pyrogram import filters
from pyrogram.types import Message

from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto

GROUP_START = 20
GROUP_END = 30

@matto_bot.on_message(filters.video_chat_started, group=GROUP_START)
@matto_bot.on_message(filters.video_chat_ended, group=GROUP_END)
async def video_chat_state_handler(client, message: Message):
    try:
        await Matto.stop_stream_force(message.chat.id)
    except Exception:
        pass