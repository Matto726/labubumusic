from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    blacklist_chat, blacklisted_chats, whitelist_chat
)
from LabubuMusic.utils.decorators.language import language
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["blchat", "blacklistchat"]) & SUDO_USERS)
@language
async def blacklist_chat_func(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_1"])
    
    try:
        chat_id = int(message.text.strip().split()[1])
    except ValueError:
        return await message.reply_text(_["black_1"])

    current_blacklist = await blacklisted_chats()
    if chat_id in current_blacklist:
        return await message.reply_text(_["black_2"])
    
    try:
        await blacklist_chat(chat_id)
        await message.reply_text(_["black_3"])

        try:
            await matto_bot.leave_chat(chat_id)
        except:
            pass
    except Exception:
        await message.reply_text("Error adding to blacklist.")

@matto_bot.on_message(filters.command(["whitelistchat", "unblacklistchat", "unblchat"]) & SUDO_USERS)
@language
async def whitelist_function(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_4"])
    
    try:
        chat_id = int(message.text.strip().split()[1])
    except ValueError:
        return await message.reply_text(_["black_4"])

    current_blacklist = await blacklisted_chats()
    if chat_id not in current_blacklist:
        return await message.reply_text(_["black_5"])
    
    if await whitelist_chat(chat_id):
        return await message.reply_text(_["black_6"])
    
    await message.reply_text(_["black_9"])

@matto_bot.on_message(filters.command(["blchats", "blacklistedchats"]) & ~BANNED_USERS)
@language
async def view_blacklisted_chats(client, message: Message, _):
    bl_chats = await blacklisted_chats()
    
    if not bl_chats:
        return await message.reply_text(_["black_8"].format(matto_bot.mention))
        
    response = _["black_7"]
    for idx, chat_id in enumerate(bl_chats, 1):
        try:
            chat_obj = await matto_bot.get_chat(chat_id)
            title = chat_obj.title
        except:
            title = "Private/Unknown"
            
        response += f"{idx}. {title} [<code>{chat_id}</code>]\n"
        
    await message.reply_text(response)