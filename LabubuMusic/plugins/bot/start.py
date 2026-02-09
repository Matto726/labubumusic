import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch
import config
from LabubuMusic import matto_bot
from LabubuMusic.misc import BOOT_TIMESTAMP
from LabubuMusic.plugins.sudo.sudoers import sudoers_list
from LabubuMusic.utils.database import (
    add_served_chat, add_served_user, blacklisted_chats,
    get_lang, is_banned_user, is_on_off
)
from LabubuMusic.utils import bot_sys_stats
from LabubuMusic.utils.decorators.language import LanguageStart
from LabubuMusic.utils.formatters import get_readable_time
from LabubuMusic.utils.inline import help_pannel_page1, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

@matto_bot.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_command_private(client, message: Message, _):
    await add_served_user(message.from_user.id)
    
    if len(message.text.split()) > 1:
        param = message.text.split(None, 1)[1]
        
        if param.startswith("help"):
            kb = help_pannel_page1(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                reply_markup=kb
            )

        if param.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await matto_bot.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} checked **sudo list**.\nID: `{message.from_user.id}`"
                )
            return

        if param.startswith("inf"):
            vid_id = param.replace("info_", "", 1)
            query_url = f"https://www.youtube.com/watch?v={vid_id}"
            
            search = VideosSearch(query_url, limit=1)
            res = (await search.next())["result"][0]
            
            info_text = _["start_6"].format(
                res["title"], res["duration"], res["viewCount"]["short"], 
                res["publishedTime"], res["channel"]["link"], 
                res["channel"]["name"], matto_bot.mention
            )
            
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(text=_["S_B_8"], url=res["link"]),
                InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP),
            ]])
            
            await message.reply_photo(
                photo=res["thumbnails"][0]["url"].split("?")[0],
                caption=info_text,
                reply_markup=kb
            )
            
            if await is_on_off(2):
                await matto_bot.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} checked **track info**.\nID: `{message.from_user.id}`"
                )
            return

    kb = private_panel(_)
    uptime, cpu, ram, disk = await bot_sys_stats()
    
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_2"].format(message.from_user.mention, matto_bot.mention, uptime, disk, cpu, ram),
        reply_markup=InlineKeyboardMarkup(kb)
    )
    
    if await is_on_off(2):
        await matto_bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=f"{message.from_user.mention} started the bot.\nID: `{message.from_user.id}`"
        )

@matto_bot.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_command_group(client, message: Message, _):
    kb = start_panel(_)
    uptime_sec = int(time.time() - BOOT_TIMESTAMP)
    
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(matto_bot.mention, get_readable_time(uptime_sec)),
        reply_markup=InlineKeyboardMarkup(kb)
    )
    await add_served_chat(message.chat.id)

@matto_bot.on_message(filters.new_chat_members, group=-1)
async def welcome_handler(client, message: Message):
    for member in message.new_chat_members:
        try:
            if await is_banned_user(member.id):
                try: await message.chat.ban_member(member.id)
                except: pass

            if member.id == matto_bot.id:
                lang = await get_lang(message.chat.id)
                _ = get_string(lang)
                
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await matto_bot.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(matto_bot.mention, config.SUPPORT_GROUP, config.SUPPORT_GROUP),
                        disable_web_page_preview=True
                    )
                    return await matto_bot.leave_chat(message.chat.id)

                kb = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name, matto_bot.mention, 
                        message.chat.title, matto_bot.mention
                    ),
                    reply_markup=InlineKeyboardMarkup(kb)
                )
                await add_served_chat(message.chat.id)
                
        except Exception:
            pass