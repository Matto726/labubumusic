from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_playmode, get_playtype, is_nonadmin_chat
from LabubuMusic.utils.decorators import language
from LabubuMusic.utils.inline.settings import playmode_users_markup
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["playmode", "mode"]) & filters.group & ~BANNED_USERS)
@language
async def set_play_mode(client, message: Message, _):
    current_mode = await get_playmode(message.chat.id)
    current_type = await get_playtype(message.chat.id)
    is_non_admin = await is_nonadmin_chat(message.chat.id)

    direct_state = True if current_mode == "Direct" else None
    group_state = True if not is_non_admin else None
    playtype_state = True if current_type != "Everyone" else None

    mode_buttons = playmode_users_markup(_, direct_state, group_state, playtype_state)
    
    await message.reply_text(
        _["play_22"].format(message.chat.title),
        reply_markup=InlineKeyboardMarkup(mode_buttons),
    )