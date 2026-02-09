from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import add_off, add_on
from LabubuMusic.utils.decorators.language import language

@matto_bot.on_message(filters.command("logger") & SUDO_USERS)
@language
async def logger_config(client, message, _):
    usage = _["log_1"]
    
    if len(message.command) != 2:
        return await message.reply_text(usage)
        
    arg = message.text.split(None, 1)[1].strip().lower()
    
    if arg == "enable":
        await add_on(2)
        await message.reply_text(_["log_2"])
    elif arg == "disable":
        await add_off(2)
        await message.reply_text(_["log_3"])
    else:
        await message.reply_text(usage)

@matto_bot.on_message(filters.command("cookies") & SUDO_USERS)
async def fetch_cookies(client, message):
    try:
        await message.reply_document(
            document="cookies/logs.csv",
            caption="Here is the latest cookie log file."
        )
    except Exception as e:
        await message.reply_text(f"Failed to fetch cookies: {e}")