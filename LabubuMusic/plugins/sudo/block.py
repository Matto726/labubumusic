from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import add_gban_user, remove_gban_user
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.extraction import extract_user
from config import BANNED_USERS

@matto_bot.on_message(filters.command("block") & SUDO_USERS)
@language
async def block_user_func(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
    
    target_user = await extract_user(message)
    if not target_user:
        return
        
    if target_user.id in BANNED_USERS:
        return await message.reply_text(_["block_1"].format(target_user.mention))
    
    await add_gban_user(target_user.id)
    BANNED_USERS.add(target_user.id)
    
    await message.reply_text(_["block_2"].format(target_user.mention))

@matto_bot.on_message(filters.command("unblock") & SUDO_USERS)
@language
async def unblock_user_func(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
    
    target_user = await extract_user(message)
    if not target_user:
        return

    if target_user.id not in BANNED_USERS:
        return await message.reply_text(_["block_3"].format(target_user.mention))
    
    await remove_gban_user(target_user.id)
    BANNED_USERS.remove(target_user.id)
    
    await message.reply_text(_["block_4"].format(target_user.mention))

@matto_bot.on_message(filters.command(["blocked", "blockedusers", "blusers"]) & SUDO_USERS)
@language
async def list_blocked_users(client, message: Message, _):
    if not BANNED_USERS:
        return await message.reply_text(_["block_5"])
    
    temp_msg = await message.reply_text(_["block_6"])
    report_text = _["block_7"]
    
    count = 0
    for uid in BANNED_USERS:
        try:
            u_obj = await matto_bot.get_users(uid)
            name = u_obj.mention or u_obj.first_name
            count += 1
            report_text += f"{count}➤ {name}\n"
        except:
            continue
            
    if count == 0:
        await temp_msg.edit_text(_["block_5"])
    else:
        await temp_msg.edit_text(report_text)