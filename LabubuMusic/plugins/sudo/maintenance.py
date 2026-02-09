from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    get_lang, is_maintenance, 
    maintenance_off, maintenance_on
)
from strings import get_string

@matto_bot.on_message(filters.command("maintenance") & SUDO_USERS)
async def maintenance_handler(client, message: Message):
    try:
        lang = await get_lang(message.chat.id)
        _ = get_string(lang)
    except:
        _ = get_string("en")
        
    if len(message.command) != 2:
        return await message.reply_text(_["maint_1"])
        
    state = message.text.split(None, 1)[1].strip().lower()
    
    if state == "enable":
        if await is_maintenance():
            await message.reply_text(_["maint_2"].format(matto_bot.mention))
        else:
            await maintenance_on()
            await message.reply_text(_["maint_2"].format(matto_bot.mention))
            
    elif state == "disable":
        if not await is_maintenance():
            await message.reply_text(_["maint_3"].format(matto_bot.mention))
        else:
            await maintenance_off()
            await message.reply_text(_["maint_3"].format(matto_bot.mention))
            
    else:
        await message.reply_text(_["maint_1"])