import asyncio
import speedtest
from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.decorators.language import language

def execute_speedtest(status_msg, _):
    st_client = speedtest.Speedtest()
    
    try:
        status_msg.edit_text(_["server_12"])
        st_client.get_best_server()
        
        status_msg.edit_text(_["server_13"])
        st_client.download()
        
        status_msg.edit_text(_["server_14"])
        st_client.upload()
        
        st_client.results.share()
        return st_client.results.dict()
    except Exception as e:
        status_msg.edit_text(f"Speedtest failed: {e}")
        return None

@matto_bot.on_message(filters.command(["speedtest", "spt"]) & SUDO_USERS)
@language
async def run_speedtest(client, message, _):
    init_msg = await message.reply_text(_["server_11"])
    loop = asyncio.get_event_loop()
    
    results = await loop.run_in_executor(None, execute_speedtest, init_msg, _)
    
    if results:
        caption_text = _["server_15"].format(
            results["client"]["isp"],
            results["client"]["country"],
            results["server"]["name"],
            results["server"]["country"],
            results["server"]["cc"],
            results["server"]["sponsor"],
            results["server"]["latency"],
            results["ping"]
        )
        
        await message.reply_photo(
            photo=results["share"], 
            caption=caption_text
        )
        await init_msg.delete()