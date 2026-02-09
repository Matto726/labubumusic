import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message

from LabubuMusic import matto_bot
from LabubuMusic.misc import db
from LabubuMusic.utils import seconds_to_min
from LabubuMusic.utils.database import is_active_chat, is_music_playing
from LabubuMusic.utils.decorators.language import language, languageCB
from LabubuMusic.utils.inline import queue_back_markup, queue_markup
from config import BANNED_USERS, YOUTUBE_IMG_URL

@matto_bot.on_message(filters.command(["queue", "cqueue"]) & filters.group & ~BANNED_USERS)
@language
async def view_queue(client, message: Message, _):
    chat_id = message.chat.id
    
    if not await is_active_chat(chat_id):
        return await message.reply_text(_["queue_2"])
        
    queue_data = db.get(chat_id)
    if not queue_data:
        return await message.reply_text(_["queue_2"])
        
    current = queue_data[0]

    title = current["title"]
    duration = current["dur"]
    played = seconds_to_min(current["played"])
    link = current["link"]
    buttons = queue_markup(_, duration, "c" if message.command[0][0] == "c" else "g", current["vidid"], played, duration)
    
    await message.reply_photo(
        photo=YOUTUBE_IMG_URL,
        caption=_["queue_1"].format(
            title, played, duration, link
        ),
        reply_markup=buttons
    )

@matto_bot.on_callback_query(filters.regex("GetTimer") & ~BANNED_USERS)
async def queue_timer_callback(client, cb: CallbackQuery):
    try:
        await cb.answer()
    except:
        pass
