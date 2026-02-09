import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_authuser_names, get_cmode
from LabubuMusic.utils.decorators import ActualAdminCB, language
from config import BANNED_USERS, adminlist, lyrical

reload_cooldown = {}

@matto_bot.on_message(
    filters.command(["admincache", "reload", "refresh"]) & filters.group & ~BANNED_USERS
)
@language
async def refresh_admin_cache(client, message: Message, _):
    chat_id = message.chat.id

    if chat_id in reload_cooldown:
        return await message.reply_text(_["admin_20"])
        
    reload_cooldown[chat_id] = True

    auth_users = await get_authuser_names(chat_id)
    adminlist[chat_id] = []

    async for member in message.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
        if member.privileges.can_manage_video_chats:
            adminlist[chat_id].append(member.user.id)

    for user_token in auth_users:
        from LabubuMusic.utils.formatters import alpha_to_int
        uid = await alpha_to_int(user_token)
        adminlist[chat_id].append(uid)
        
    await message.reply_text(_["admin_20"])

    await asyncio.sleep(20)
    reload_cooldown.pop(chat_id, None)

@matto_bot.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def cancel_download_task(client, cb: CallbackQuery, _):
    msg_id = cb.message.id
    download_task = lyrical.get(msg_id)
    
    if not download_task:
        return await cb.answer(_["tg_4"], show_alert=True)
        
    if download_task.done() or download_task.cancelled():
        return await cb.answer(_["tg_5"], show_alert=True)
        
    try:
        download_task.cancel()
        lyrical.pop(msg_id, None)
        
        await cb.answer(_["tg_6"], show_alert=True)
        await cb.edit_message_text(
            _["tg_7"].format(cb.from_user.mention)
        )
    except Exception:
        await cb.answer(_["tg_8"], show_alert=True)

@matto_bot.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_button_handler(client, cb: CallbackQuery):
    try:
        await cb.message.delete()
        await cb.message.reply_text(
            f"Closed by: {cb.from_user.mention}",
            disable_notification=True
        )
    except:
        pass