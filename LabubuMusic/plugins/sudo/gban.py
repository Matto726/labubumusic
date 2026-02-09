import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    add_banned_user, get_banned_count, get_banned_users,
    get_served_chats, is_banned_user, remove_banned_user
)
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.extraction import extract_user
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["gban", "globalban"]) & SUDO_USERS)
@language
async def global_ban_handler(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target = await extract_user(message)
    if not target:
        return
        
    if target.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    if target.id in SUDO_USERS:
        return await message.reply_text(_["gban_2"])
    if await is_banned_user(target.id):
        return await message.reply_text(_["gban_3"].format(target.mention))

    await add_banned_user(target.id)
    BANNED_USERS.add(target.id)
    
    status_msg = await message.reply_text(_["gban_4"].format(target.mention))

    count = 0
    chats = await get_served_chats()
    for chat_data in chats:
        cid = int(chat_data["chat_id"])
        try:
            await matto_bot.ban_chat_member(cid, target.id)
            count += 1
            await asyncio.sleep(0.1)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            continue
            
    await status_msg.edit_text(_["gban_5"].format(target.mention, count))

@matto_bot.on_message(filters.command(["ungban"]) & SUDO_USERS)
@language
async def global_unban_handler(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target = await extract_user(message)
    if not target:
        return
        
    if not await is_banned_user(target.id):
        return await message.reply_text(_["gban_7"].format(target.mention))
        
    await remove_banned_user(target.id)
    BANNED_USERS.discard(target.id)
    
    status_msg = await message.reply_text(_["gban_8"].format(target.mention))

    count = 0
    chats = await get_served_chats()
    for chat_data in chats:
        cid = int(chat_data["chat_id"])
        try:
            await matto_bot.unban_chat_member(cid, target.id)
            count += 1
            await asyncio.sleep(0.1)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            continue
            
    await status_msg.edit_text(_["gban_9"].format(target.mention, count))

@matto_bot.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDO_USERS)
@language
async def list_gbans(client, message: Message, _):
    total = await get_banned_count()
    if total == 0:
        return await message.reply_text(_["gban_10"])
        
    report = _["gban_11"]
    content = _["gban_12"]
    
    banned_ids = await get_banned_users()
    idx = 0
    
    for uid in banned_ids:
        idx += 1
        try:
            u = await matto_bot.get_users(uid)
            display = u.mention or u.first_name
            content += f"{idx}➤ {display}\n"
        except:
            content += f"{idx}➤ {uid}\n"
            
    await message.reply_text(content if idx > 0 else _["gban_10"])