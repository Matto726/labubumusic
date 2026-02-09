from datetime import datetime
from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.utils import bot_sys_stats
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL

@matto_bot.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def system_ping(client, message, _):
    start_time = datetime.now()

    msg = await message.reply_photo(
        photo=PING_IMG_URL,
        caption=_["ping_1"].format(matto_bot.mention)
    )

    call_latency = await Matto.ping()
    uptime, cpu, ram, disk = await bot_sys_stats()
    
    end_time = datetime.now()
    api_latency = (end_time - start_time).microseconds / 1000

    final_text = _["ping_2"].format(
        api_latency, 
        matto_bot.mention, 
        uptime, 
        ram, 
        cpu, 
        disk, 
        call_latency
    )
    
    await msg.edit_text(
        final_text,
        reply_markup=supp_markup(_)
    )