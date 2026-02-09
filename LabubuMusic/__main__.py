import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall

import config
from LabubuMusic import log_factory, matto_bot, userbot
from LabubuMusic.core.call import Matto
from LabubuMusic.misc import load_sudo_users
from LabubuMusic.plugins import ALL_MODULES
from LabubuMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Organized Bot Commands
BOT_MENU = [
    BotCommand("start", "❖ Start the bot"),
    BotCommand("help", "❖ Help menu and management"),
    BotCommand("ping", "❖ Check system stats"),
    BotCommand("play", "❖ Play audio in VC"),
    BotCommand("vplay", "❖ Play video in VC"),
    BotCommand("playrtmps", "❖ Stream live video"),
    BotCommand("playforce", "❖ Force play audio"),
    BotCommand("vplayforce", "❖ Force play video"),
    BotCommand("pause", "❖ Pause stream"),
    BotCommand("resume", "❖ Resume stream"),
    BotCommand("skip", "❖ Skip track"),
    BotCommand("end", "❖ End stream"),
    BotCommand("stop", "❖ Stop stream"),
    BotCommand("queue", "❖ Show queue"),
    BotCommand("auth", "❖ Authorize user"),
    BotCommand("unauth", "❖ Unauthorize user"),
    BotCommand("authusers", "❖ List auth users"),
    BotCommand("cplay", "❖ Play audio in channel"),
    BotCommand("cvplay", "❖ Play video in channel"),
    BotCommand("cplayforce", "❖ Force play channel audio"),
    BotCommand("cvplayforce", "❖ Force play channel video"),
    BotCommand("channelplay", "❖ Connect channel"),
    BotCommand("loop", "❖ Toggle loop mode"),
    BotCommand("stats", "❖ Show stats"),
    BotCommand("shuffle", "❖ Shuffle queue"),
    BotCommand("seek", "❖ Seek forward"),
    BotCommand("seekback", "❖ Seek backward"),
    BotCommand("song", "❖ Download song"),
    BotCommand("speed", "❖ Adjust speed"),
    BotCommand("cspeed", "❖ Adjust channel speed"),
    BotCommand("tagall", "❖ Tag everyone"),
]

async def set_commands():
    try:
        await matto_bot.set_bot_commands(BOT_MENU)
        log_factory("LabubuMusic").info("Bot commands configured.")
    except Exception as ex:
        log_factory("LabubuMusic").error(f"Command setup failed: {ex}")

async def start_system():
    # Check for assistant variables
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        log_factory(__name__).error("Assistant client variables missing. Exiting.")
        exit()

    await load_sudo_users()

    # Load Banned Users
    try:
        gbanned = await get_gbanned()
        banned = await get_banned_users()
        BANNED_USERS.update(gbanned)
        BANNED_USERS.update(banned)
    except Exception:
        pass

    await matto_bot.start()
    await set_commands()

    # Import Plugins
    for module in ALL_MODULES:
        importlib.import_module("LabubuMusic.plugins" + module)

    log_factory("LabubuMusic.plugins").info("Modules Imported Successfully.")

    await userbot.start()
    await Matto.start()

    # Join Log Channel
    try:
        await Matto.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        log_factory("LabubuMusic").error(
            "Please enable videochat in your log group/channel. Stopping..."
        )
        exit()
    except Exception:
        pass

    await Matto.decorators()

    # "Labubu Music Started Successfully.\n\nDon't forget to visit @Laboobubots"
    log_factory("LabubuMusic").info(
        "Labubu Music Started Successfully.\n\nDon't forget to visit @Laboobubots"
    )

    await idle()

    await matto_bot.stop()
    await userbot.stop()
    log_factory("LabubuMusic").info("Stopping Labubu Music Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_system())