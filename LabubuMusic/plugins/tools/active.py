from pyrogram import filters
from pyrogram.types import Message
from unidecode import unidecode

from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)

@matto_bot.on_message(filters.command(["activevc", "activevoice"]) & SUDO_USERS)
async def list_active_voice_chats(client, message: Message):
    status_msg = await message.reply_text("Scanning active voice chats...")
    active_list = await get_active_chats()
    
    report_text = ""
    count = 0
    
    for chat_id in active_list:
        try:
            chat_obj = await matto_bot.get_chat(chat_id)
            title = unidecode(chat_obj.title).upper()
            
            if chat_obj.username:
                link = f"<a href=https://t.me/{chat_obj.username}>{title}</a>"
            else:
                link = title
                
            report_text += f"<b>{count + 1}.</b> {link} [<code>{chat_id}</code>]\n"
            count += 1
        except Exception:
            await remove_active_chat(chat_id)
            continue
            
    if not report_text:
        await status_msg.edit_text(f"No active voice chats found on {matto_bot.mention}.")
    else:
        await status_msg.edit_text(
            f"<b>Active Voice Chats List:</b>\n\n{report_text}",
            disable_web_page_preview=True
        )

@matto_bot.on_message(filters.command(["activev", "activevideo"]) & SUDO_USERS)
async def list_active_video_chats(client, message: Message):
    status_msg = await message.reply_text("Scanning active video chats...")
    video_list = await get_active_video_chats()
    
    report_text = ""
    count = 0
    
    for chat_id in video_list:
        try:
            chat_obj = await matto_bot.get_chat(chat_id)
            title = unidecode(chat_obj.title).upper()
            
            if chat_obj.username:
                link = f"<a href=https://t.me/{chat_obj.username}>{title}</a>"
            else:
                link = title
                
            report_text += f"<b>{count + 1}.</b> {link} [<code>{chat_id}</code>]\n"
            count += 1
        except Exception:
            await remove_active_video_chat(chat_id)
            continue
            
    if not report_text:
        await status_msg.edit_text(f"No active video chats found on {matto_bot.mention}.")
    else:
        await status_msg.edit_text(
            f"<b>Active Video Chats List:</b>\n\n{report_text}",
            disable_web_page_preview=True
        )