from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    autoend_off, autoend_on, 
    autoleave_off, autoleave_on, 
    is_autoend, is_autoleave
)

@matto_bot.on_message(filters.command("autoend") & SUDO_USERS)
async def auto_end_stream_config(client, message: Message):
    current_state = "Enabled" if await is_autoend() else "Disabled"
    usage_text = f"**Usage:**\n/autoend [enable|disable]\n\n**Current Status:** {current_state}"
    
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
    
    action = message.text.split(None, 1)[1].strip().lower()
    
    if action in ["enable", "on", "yes"]:
        await autoend_on()
        await message.reply_text(
            "» **Auto End Stream Enabled.**\n\n"
            "The assistant will leave the voice chat automatically if no one is listening."
        )
    elif action in ["disable", "off", "no"]:
        await autoend_off()
        await message.reply_text("» **Auto End Stream Disabled.**")
    else:
        await message.reply_text(usage_text)

@matto_bot.on_message(filters.command("autoleave") & SUDO_USERS)
async def auto_leave_chat_config(client, message: Message):
    current_state = "Enabled" if await is_autoleave() else "Disabled"
    usage_text = f"**Usage:**\n/autoleave [enable|disable]\n\n**Current Status:** {current_state}"
    
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
    
    action = message.text.split(None, 1)[1].strip().lower()
    
    if action in ["enable", "on", "yes"]:
        await autoleave_on()
        await message.reply_text(
            "» **Auto Leave Chat Enabled.**\n\n"
            "The assistant will leave chats where the bot was removed."
        )
    elif action in ["disable", "off", "no"]:
        await autoleave_off()
        await message.reply_text("» **Auto Leave Chat Disabled.**")
    else:
        await message.reply_text(usage_text)