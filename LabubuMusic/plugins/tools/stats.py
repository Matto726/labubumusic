import platform
import psutil
from sys import version as python_ver
from pyrogram import filters, __version__ as pyro_ver
from pytgcalls.__version__ import __version__ as pytg_ver
from pyrogram.types import InputMediaPhoto

from LabubuMusic import matto_bot
from LabubuMusic.core.mongo import mongodb
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.plugins import ALL_MODULES
from LabubuMusic.utils.database import (
    get_served_chats, get_served_users, get_sudoers
)
from LabubuMusic.utils.decorators.language import language, languageCB
from LabubuMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS, STATS_IMG_URL

@matto_bot.on_message(filters.command(["stats", "gstats"]) & filters.user(SUDO_USERS))
@language
async def show_stats(client, message, _):
    upl = stats_buttons(_, True)
    await message.reply_photo(
        photo=STATS_IMG_URL,
        caption=_["gstats_2"].format(matto_bot.mention),
        reply_markup=upl,
    )

@matto_bot.on_callback_query(filters.regex("GetStats") & ~BANNED_USERS)
@languageCB
async def callback_stats(client, cb, _):
    try:
        await cb.answer()
    except:
        pass
        
    cmd = cb.data.split(":")[1] if ":" in cb.data else "General"
    
    if cmd == "General":
        ram_info = psutil.virtual_memory()
        ram_used = str(ram_info.percent)
        cpu_freq = psutil.cpu_freq().current
        disk_info = psutil.disk_usage("/")

        db_stats = await mongodb.command("dbstats")
        data_size = db_stats.get("dataSize", 0) / 1024
        storage_size = db_stats.get("storageSize", 0) / 1024

        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        blocked_users = len(BANNED_USERS)
        sudo_count = len(await get_sudoers())
        
        stats_text = _["gstats_5"].format(
            matto_bot.mention,
            len(ALL_MODULES),
            platform.system(),
            ram_used,
            psutil.cpu_count(logical=False),
            psutil.cpu_count(logical=True),
            cpu_freq,
            python_ver.split()[0],
            pyro_ver,
            pytg_ver,
            f"{disk_info.total / (1024**3):.2f}",
            f"{disk_info.used / (1024**3):.2f}",
            f"{disk_info.free / (1024**3):.2f}",
            served_chats,
            served_users,
            blocked_users,
            sudo_count,
            f"{data_size:.2f}",
            f"{storage_size:.2f}",
            db_stats.get("collections", 0),
            db_stats.get("objects", 0),
        )
        
        media = InputMediaPhoto(media=STATS_IMG_URL, caption=stats_text)
        buttons = back_stats_buttons(_)
        
        await cb.edit_message_media(media=media, reply_markup=buttons)

    elif cmd == "Bot":
        await cb.edit_message_caption(
            caption=_["gstats_2"].format(matto_bot.mention),
            reply_markup=stats_buttons(_, True)
        )